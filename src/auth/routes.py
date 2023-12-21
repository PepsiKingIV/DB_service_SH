from auth.auth import auth_backend
from fastapi import APIRouter, Depends
from fastapi import APIRouter
from fastapi_users import FastAPIUsers
from sqlalchemy import select, insert, delete, update
from auth.manager import get_user_manager
from auth.models import User
from auth.models import user
from sqlalchemy.ext.asyncio import AsyncSession
from auth.schemas import UsersTokens

from database import get_async_session


route = APIRouter(prefix="/accounts", tags=["accounts"])

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

c_user = fastapi_users.current_user()  # c_user = current_user


@route.get("users/")
async def get_users(
    session: AsyncSession = Depends(get_async_session),
    super_user: User = Depends(c_user),
) -> UsersTokens:
    if super_user.is_superuser:
        query = select(user.c.id, user.c.username, user.c.tinkoff_invest_token)
        result = await session.execute(query)
        await session.commit()
        return result.all()
    else:
        return {"status_code": 403, "content": "You are not a super user"}
