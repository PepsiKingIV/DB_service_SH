from fastapi import FastAPI, Request
from fastapi_users import FastAPIUsers
from auth.manager import get_user_manager
from auth.models import User
from datetime import timedelta
from auth.schemas import UserCreate, UserRead
from database import get_async_session, engine
from auth.auth import auth_backend
from operation.routes import route as operation_route
from asset.routes import route as asset_route
from user.routes import route as user_route
from fastapi.middleware.trustedhost import TrustedHostMiddleware


TOKEN = "token"

app = FastAPI(title="Sheres")

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/verify",
    tags=["verify"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)


app.include_router(router=operation_route)

app.include_router(router=asset_route)

app.include_router(router=user_route)

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["31.129.105.185"])
