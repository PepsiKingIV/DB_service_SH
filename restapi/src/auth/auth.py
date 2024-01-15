from fastapi_users.authentication import (
    AuthenticationBackend,
    JWTStrategy,
    CookieTransport,
)
from config import SECRET_AUTH

cookie_transport = CookieTransport(cookie_name="operations", cookie_max_age=3600)


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET_AUTH, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)
