from auth.auth import auth_backend
from fastapi import APIRouter, Depends
from fastapi import APIRouter
from fastapi_users import FastAPIUsers
from sqlalchemy import select, insert, delete, update
from auth.manager import get_user_manager
from auth.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from operation.models import operation
from operation.schemas import RequestOperation, ResponseOperation, RequestOperationSuper

from database import get_async_session


route = APIRouter(prefix="/operation", tags=["operation"])

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

c_user = fastapi_users.current_user()  # c_user = current_user


@route.post("post/")
async def set_operations(
    new_operation: RequestOperation,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(c_user),
):
    stmt = insert(operation).values(
        user_id=user.id,
        buy=new_operation.buy,
        figi=new_operation.figi,
        price=new_operation.price,
        count=new_operation.count,
        date=new_operation.date.replace(tzinfo=None),
    )
    await session.execute(stmt)
    await session.commit()
    return {"status_code": 201, "content": "the record was created successfully"}


@route.get("get/")
async def get_operations(
    session: AsyncSession = Depends(get_async_session), user: User = Depends(c_user)
) -> list[ResponseOperation]:
    query = select(operation).where(operation.c.user_id == user.id)
    result = await session.execute(query)
    await session.commit()
    return result.all()


@route.delete("delete/")
async def delete_operation(
    operation: int,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(c_user),
):
    stmt = delete(operation).where(operation.c.id == operation.id)
    await session.execute(stmt)
    await session.commit()
    return {"status_code": 200, "content": "the record was successfully deleted"}


@route.put("put/")
async def change_operation(
    operation: int,
    new_operation: RequestOperation,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(c_user),
):
    stmt = (
        update(operation)
        .where(operation.c.id == operation.id, operation.c.user_id == user.id)
        .values(
            user_id=user.id,
            buy=new_operation.buy,
            price=new_operation.price,
            count=new_operation.count,
            date=new_operation.date.replace(tzinfo=None),
        )
    )
    await session.execute(stmt)
    await session.commit()
    return {"status_code": 200, "content": "the record has been successfully changed"}


@route.post("post_super/")
async def set_operations(
    new_operation: RequestOperationSuper,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(c_user),
):
    if user.is_superuser:
        stmt = insert(operation).values(
            user_id=new_operation.user_id,
            buy=new_operation.buy,
            figi=new_operation.figi,
            price=new_operation.price,
            count=new_operation.count,
            date=new_operation.date.replace(tzinfo=None),
        )
        await session.execute(stmt)
        await session.commit()
        return {"status_code": 201, "content": "the record was created successfully"}
    else:
        return {"status_code": 403, "content": "You are not a super user"}


@route.put("put_super/")
async def change_operation(
    operation: int,
    new_operation: RequestOperationSuper,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(c_user),
):
    if user.is_superuser:
        stmt = (
            update(operation)
            .where(
                operation.c.id == operation.id,
                operation.c.user_id == new_operation.user_id,
            )
            .values(
                user_id=new_operation.user_id,
                buy=new_operation.buy,
                price=new_operation.price,
                count=new_operation.count,
                date=new_operation.date.replace(tzinfo=None),
            )
        )
        await session.execute(stmt)
        await session.commit()
        return {
            "status_code": 200,
            "content": "the record has been successfully changed",
        }
    else:
        return {"status_code": 403, "content": "You are not a super user"}


@route.delete("delete_super/")
async def delete_operation(
    operation: int,
    user_id: int,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(c_user),
):
    if user.is_superuser:
        stmt = delete(operation).where(
            operation.c.id == operation.id, operation.c.user_id == user_id
        )
        await session.execute(stmt)
        await session.commit()
        return {"status_code": 200, "content": "the record was successfully deleted"}
    else:
        return {"status_code": 403, "content": "You are not a super user"}
