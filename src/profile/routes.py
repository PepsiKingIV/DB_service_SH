from auth.auth import auth_backend
from fastapi import APIRouter, Depends
from fastapi import APIRouter
from fastapi_users import FastAPIUsers
from sqlalchemy import select, insert, delete, update
from auth.manager import get_user_manager
from auth.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from auth.models import asset_ratio
from asset.models import instrument_types
from profile.schemas import ProfileResponse

from database import get_async_session


route = APIRouter(prefix="/profile", tags=["profile"])

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

c_user = fastapi_users.current_user()  # c_user = current_user


@route.post("set-token/")
async def set_token(
    token: str,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(c_user),
):
    stmt = update(user).where(user.c.id == user.id).values(tinkoff_invest_token=token)
    await session.execute(stmt)
    await session.commit()
    return {"status_code": 200, "content": "the record has been successfully changed"}


@route.post("set-username/")
async def set_username(
    username: str,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(c_user),
):
    stmt = update(user).where(user.c.id == user.id).values(username=username)
    await session.execute(stmt)
    await session.commit()
    return {"status_code": 200, "content": "the record has been successfully changed"}


@route.get("")
async def get_profile(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(c_user),
) -> ProfileResponse:
    query = select(user.c.username, user.c.email).where(user.c.id == user.id)
    result = await session.execute(query)
    await session.commit()
    return result.first()


@route.get("instrument-list/")
async def instrument_list(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(c_user),
) -> list[str]:
    query = select(instrument_types.name)
    result = await session.execute(query)
    await session.commit()
    return result.all()
