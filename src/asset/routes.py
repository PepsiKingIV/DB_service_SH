from auth.auth import auth_backend
from fastapi import APIRouter, Depends
from fastapi import APIRouter
from fastapi_users import FastAPIUsers
from sqlalchemy import select, insert, delete, update
from auth.manager import get_user_manager
from auth.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from asset.models import asset
from asset.schemas import RequestAsset, ResponseAsset

from database import get_async_session


route = APIRouter(prefix="/asset", tags=["asset"])

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

c_user = fastapi_users.current_user()  # c_user = current_user


@route.get("get/")
async def get_asset(
    session: AsyncSession = Depends(get_async_session), user: User = Depends(c_user)
) -> list[ResponseAsset]:
    query = select(asset).where(asset.c.user_id == user.id)
    result = await session.execute(query)
    await session.commit()
    return result.all()


@route.post("post/")
async def set_asset(
    new_asset: RequestAsset,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(c_user),
):
    stmt = insert(asset).values(
        user_id=user.id,
        figi=new_asset.figi,
        name=new_asset.name,
        asset_type=new_asset.instrument_type_id,
        price=new_asset.price,
        count=new_asset.count,
        date=new_asset.date,
    )
    await session.execute(stmt)
    await session.commit()
    return {"status_code": "201", "content": "the record was created successfully"}


@route.delete("delete/")
async def delete_asset(
    asset_id: int,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(c_user),
):
    stmt = delete(asset).where(asset.c.id == asset_id.id)
    await session.execute(stmt)
    await session.commit()
    return {"status_code": "200", "content": "the record was successfully deleted"}


@route.put("put/")
async def change_asset(
    asset_id: int,
    new_asset: RequestAsset,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(c_user),
):
    stmt = (
        update(asset)
        .where(asset.c.id == asset_id, asset_id.c.user_id == user.id)
        .values(
            figi=new_asset.figi,
            name=new_asset.name,
            asset_type=new_asset.instrument_type_id,
            price=new_asset.price,
            count=new_asset.count,
            date=new_asset.date,
        )
    )
    await session.execute(stmt)
    await session.commit()
    
