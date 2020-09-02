import os

from .utils.secret_config import SecretConfig


class CorporaConfig(SecretConfig):
    def __init__(self, *args, **kwargs):
        super().__init__("corpora/corpora", **kwargs)


class CorporaDbConfig(SecretConfig):
    def __init__(self, *args, **kwargs):
        super().__init__(
            component_name="backend",
            secret_name=f"database{'_local' if 'CORPORA_LOCAL_DEV' in os.environ else ''}",
            **kwargs,
        )


class CorporaAuthConfig(SecretConfig):

    """
    secret keys:

    - api_base_url
        the location to the auth0 tenant base url
    - client_id
        the id of the auth0 tenant
    - client_secret
        the secret key, known to the auth0 tenant and the data portal backend
    - audience
        same as the client_id, which is required for id_tokens.
    - flask_secret_key
        the secret used to encrypt the flask session cookies
    - callback_base_url
        the data portal api base url
    - cookie_name
        the name of the cookie that stores the tokens
    - redirect_to_frontend
        the location of the front end, this is where the user is redirected after login/logout.
    """

    def __init__(self, *args, **kwargs):
        deployment = os.environ["DEPLOYMENT_STAGE"]
        if deployment == "test":
            super().__init__(component_name="backend", deployment="dev", secret_name="auth0-secret", **kwargs)
            if not self.config_is_loaded():
                self.load()
            self.config["callback_base_url"] = "http://localhost:5000"
        else:
            super().__init__(
                component_name="backend",
                secret_name="auth0-secret",
                **kwargs,
            )
            if not self.config_is_loaded():
                self.load()
            self.config["callback_base_url"] = "http://localhost:5000"
