import unittest

from unit.backend.chalice.api_server import BaseAPITest


class TestAPP(BaseAPITest, unittest.TestCase):
    def test_smoke(self):
        """ If this fails then the server does not work """
        response = self.app.get("/")
        response.raise_for_status()
