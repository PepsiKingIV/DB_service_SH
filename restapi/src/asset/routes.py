from auth.auth import auth_backend
from fastapi import APIRouter, Depends
from fastapi import APIRouter, HTTPException
from fastapi_users import FastAPIUsers
from sqlalchemy import select, insert, delete, update
from auth.manager import get_user_manager
from auth.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from asset.models import asset
from asset.schemas import RequestAsset, ResponseAsset, RequestAssetSuper

from database import get_async_session


route = APIRouter(prefix="/asset", tags=["asset"])

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

c_user = fastapi_users.current_user()  # c_user = current_user


@route.get("/get")
async def get_asset(
    session: AsyncSession = Depends(get_async_session), user: User = Depends(c_user)
) -> list[ResponseAsset]:
    query = select(asset).where(asset.c.user_id == user.id)
    result = await session.execute(query)
    await session.commit()
    content = list()
    for i in result.all():
        content.append(i._asdict())
    return content


@route.post("/post")
async def set_asset(
    new_asset: RequestAsset,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(c_user),
):
    if new_asset.count < 1:
        raise HTTPException(
            status_code=422, detail="the value of 'count' must be greater than zero"
        )
    if new_asset.price <= 0:
        raise HTTPException(
            status_code=422, detail="the value of 'price' must be greater than zero"
        )
    stmt = (
        insert(asset)
        .values(
            user_id=user.id,
            figi=new_asset.figi,
            name=new_asset.name,
            instrument_id=new_asset.instrument_id,
            price=new_asset.price,
            count=new_asset.count,
            date=new_asset.date.replace(tzinfo=None),
        )
        .returning(asset.c.id)
    )
    result = await session.execute(stmt)
    await session.commit()
    return {
        "status_code": 201,
        "content": "the record was created successfully",
        "record ID": result.first()[0],
    }


@route.delete("/delete")
async def delete_asset(
    asset_id: int,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(c_user),
):
    stmt = delete(asset).where(asset.c.id == asset_id).returning(asset.c.id)
    try:
        result = await session.execute(stmt)
        await session.commit()
        id = result.first()[0]
        if id:
            return {
                "status_code": 200,
                "content": "the record has been successfully deleted",
                "record ID": id,
            }
        else:
            raise HTTPException(
                status_code=404, detail="there is no record with the specified number"
            )
    except Exception as e:
        raise HTTPException(
            status_code=422, detail="the specified values cannot be processed"
        )


@route.put("/put")
async def change_asset(
    asset_id: int,
    new_asset: RequestAsset,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(c_user),
):
    if new_asset.count < 1:
        raise HTTPException(
            status_code=422, detail="the value of 'count' must be greater than zero"
        )
    if new_asset.price <= 0:
        raise HTTPException(
            status_code=422, detail="the value of 'price' must be greater than zero"
        )
    stmt = (
        update(asset)
        .where(asset.c.id == asset_id, asset.c.user_id == user.id)
        .values(
            figi=new_asset.figi,
            name=new_asset.name,
            instrument_id=new_asset.instrument_id,
            price=new_asset.price,
            count=new_asset.count,
            date=new_asset.date.replace(tzinfo=None),
        )
    ).returning(asset.c.id)
    try:
        result = await session.execute(stmt)
        await session.commit()
        id = result.first()[0]
        if id:
            return {
                "status_code": 200,
                "content": "the record has been successfully changed",
                "record ID": id,
            }
        else:
            raise HTTPException(
                status_code=404, detail="there is no record with the specified number"
            )
    except Exception as e:
        raise HTTPException(
            status_code=422, detail="the specified values cannot be processed"
        )


@route.post("/post_super")
async def set_asset(
    new_asset: RequestAssetSuper,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(c_user),
):
    if user.is_superuser:
        if new_asset.count < 1:
            raise HTTPException(
                status_code=422, detail="the value of 'count' must be greater than zero"
            )
        if new_asset.price <= 0:
            raise HTTPException(
                status_code=422, detail="the value of 'price' must be greater than zero"
            )
        stmt = (
            insert(asset)
            .values(
                user_id=new_asset.user_id,
                figi=new_asset.figi,
                name=new_asset.name,
                instrument_type_id=new_asset.instrument_type_id,
                price=new_asset.price,
                count=new_asset.count,
                date=new_asset.date.replace(tzinfo=None),
            )
            .returning(asset.c.id)
        )
        try:
            await session.execute(stmt)
            await session.commit()
            return {
                "status_code": 201,
                "content": "the record was created successfully",
            }
        except Exception as e:
            raise HTTPException(
                status_code=422, detail="the specified values cannot be processed"
            )
    else:
        return {"status_code": 403, "content": "You are not a super user"}


@route.delete("/delete_super")
async def delete_asset(
    asset_id: int,
    user_id: int,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(c_user),
):
    if user.is_superuser:
        stmt = (
            delete(asset)
            .where(asset.c.id == asset_id, asset.c.user_id == user_id)
            .returning(asset.c.id)
        )
        result = await session.execute(stmt)
        await session.commit()
        id = result.first()[0]
        if id:
            return {
                "status_code": 200,
                "content": "the record has been successfully deleted",
                "record ID": id,
            }
        else:
            raise HTTPException(
                status_code=404, detail="there is no record with the specified number"
            )
    else:
        return {"status_code": 403, "content": "You are not a super user"}


@route.put("/put_super")
async def change_asset(
    asset_id: int,
    new_asset: RequestAssetSuper,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(c_user),
):
    if user.is_superuser:
        if new_asset.count < 1:
            raise HTTPException(
                status_code=422, detail="the value of 'count' must be greater than zero"
            )
        if new_asset.price <= 0:
            raise HTTPException(
                status_code=422, detail="the value of 'price' must be greater than zero"
            )
        stmt = (
            update(asset)
            .where(asset.c.id == asset_id, asset.c.user_id == new_asset.user_id)
            .values(
                figi=new_asset.figi,
                name=new_asset.name,
                instrument_type_id=new_asset.instrument_type_id,
                price=new_asset.price,
                count=new_asset.count,
                date=new_asset.date.replace(tzinfo=None),
            )
        ).returning(asset.c.id)
        try:
            result = await session.execute(stmt)
            await session.commit()
            id = result.first()[0]
            if id:
                return {
                    "status_code": 200,
                    "content": "the record was successfully updated",
                    "redord ID": id,
                }
            else:
                raise HTTPException(
                    status_code=404,
                    detail="there is no record with the specified number",
                )
        except Exception as e:
            raise HTTPException(
                status_code=404, detail="the specified values cannot be processed"
            )
    else:
        return {"status_code": 403, "content": "You are not a super user"}
