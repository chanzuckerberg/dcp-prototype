import json
import unittest

import requests
from dcplib.aws_secret import AwsSecret
from chalice import UnauthorizedError
import os

if not os.getenv("DEPLOYMENT_STAGE"):  # noqa
    os.environ["DEPLOYMENT_STAGE"] = "test"  # noqa

from dcp_prototype.backend.browser.code.common.authorizer import assert_authorized


@unittest.skipIf(os.getenv("DEPLOYMENT_STAGE") != "test", "DEPLOYMENT_STAGE not 'test'")
class TestAuthorizer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.auth0_secret = json.loads(AwsSecret(f"dcp/backend/browser/test/auth0-secret").value)
        cls.auth0_secret["audience"] = f"https://browser-api.{os.getenv('DEPLOYMENT_STAGE')}.single-cell.czi.technology"

    def test_postive(self):
        token = self.get_auth_token()
        assert_authorized({"Authorization": f"bearer {token['access_token']}"})

    def test_not_bearer(self):
        token = self.get_auth_token()
        with self.assertRaises(UnauthorizedError):
            assert_authorized({"Authorization": f"earer {token['access_token']}"})

    def test_invalid_token(self):
        token = self.get_auth_token()
        header, msg, hash = token['access_token'].split('.')
        with self.subTest("short hash"):
            with self.assertRaises(UnauthorizedError):
                assert_authorized({"Authorization": f"bearer {token['access_token'][:-1]}"})

        with self.subTest("wrong hash"):
            with self.assertRaises(UnauthorizedError):
                _token = '.'.join([header, msg, "0" * len(hash)])
                assert_authorized({"Authorization": f"bearer {_token}"})

        with self.subTest("wrong header"):
            with self.assertRaises(UnauthorizedError):
                _token = '.'.join(["0" * len(header), msg, hash])
                assert_authorized({"Authorization": f"bearer {_token}"})

        with self.subTest("short header"):
            with self.assertRaises(UnauthorizedError):
                _token = token["access_token"][1:]
                assert_authorized({"Authorization": f"bearer {_token}"})

        with self.subTest("wrong message"):
            with self.assertRaises(UnauthorizedError):
                _token = '.'.join([header, "0" * len(msg), hash])
                assert_authorized({"Authorization": f"bearer {_token}"})

    def get_auth_token(self) -> dict:
        return requests.post(
            "https://czi-single-cell.auth0.com/oauth/token",
            json=self.auth0_secret,
            headers={"content-type": "application/json"},
        ).json()
