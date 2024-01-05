from typing import Annotated, List, Union
from pydantic import Field
from auth.auth import auth_backend
from fastapi import APIRouter, HTTPException, Depends, Query, status
from fastapi_users import FastAPIUsers
from sqlalchemy import select, insert, delete, update
from auth.manager import get_user_manager
from auth.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from user.models import asset_ratio, instrument
from user.schemas import (
    ProfileResponse,
    RatioRequest,
    UsersTokens,
    Instruments,
    Instrument_ratio,
)
from auth.models import user

from database import get_async_session


route = APIRouter(prefix="/user", tags=["user"])

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

c_user = fastapi_users.current_user()  # c_user = current_user


@route.post("/set-token")
async def set_token(
    token: str,
    session: AsyncSession = Depends(get_async_session),
    c_user: User = Depends(c_user),
):
    stmt = update(user).where(user.c.id == c_user.id).values(tinkoff_invest_token=token)
    await session.execute(stmt)
    await session.commit()
    return {"status_code": 200, "content": "the record has been successfully changed"}


# TODO : добавить ограничение на размер строки
@route.post("/set-username")
async def set_username(
    username: Annotated[str | None, Query(max_length=50)],
    session: AsyncSession = Depends(get_async_session),
    c_user: User = Depends(c_user),
):
    stmt = update(user).where(user.c.id == c_user.id).values(username=username)
    await session.execute(stmt)
    await session.commit()
    return {"status_code": 200, "content": "the record has been successfully changed"}


@route.get("/")
async def get_profile(
    session: AsyncSession = Depends(get_async_session),
    c_user: User = Depends(c_user),
) -> ProfileResponse:
    query = select(user.c.username, user.c.email).where(user.c.id == c_user.id)
    result = await session.execute(query)
    # print(result.all())
    return result.first()._asdict()


@route.get("/instrument-list")
async def instrument_list(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(c_user),
) -> list[Instruments]:
    query = select(instrument.c.id, instrument.c.type_name)
    result = await session.execute(query)
    await session.commit()
    response = list()
    for i in result.all():
        response.append(i._asdict())
    return response


@route.post("/set-ratio", status_code=status.HTTP_201_CREATED)
async def set_instrument_ratio(
    instrument: RatioRequest,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(c_user),
):
    if instrument.ratio <= 0:
        raise HTTPException(
            status_code=422, detail="the value of 'ratio' must be greater than zero"
        )
    stmt = (
        insert(asset_ratio)
        .values(
            user_id=user.id,
            ratio=instrument.ratio,
            instrument=instrument.instrument_id,
            name=instrument.name,
            figi=instrument.figi,
        )
        .returning(asset_ratio.c.id)
    )
    try:
        result = await session.execute(stmt)
        await session.commit()
    except Exception as e:
        raise HTTPException(
            status_code=422, detail="the specified values cannot be processed"
        )
    return {
        "content": "the record was created successfully",
        "record ID": result.first()[0],
    }


@route.get("/ratio")
async def get_ratio(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(c_user),
) -> list[Instrument_ratio]:
    query = (
        select(instrument.c.type_name, asset_ratio.c.ratio, asset_ratio.c.id)
        .select_from(asset_ratio)
        .join(instrument)
        .where(asset_ratio.c.user_id == user.id)
    )
    result = await session.execute(query)
    await session.commit()
    content = list()
    for i in result.all():
        content.append(i._asdict())
    return content


@route.put("/ratio-update")
async def set_instrument_ratio(
    ratio_id: int,
    instrument: RatioRequest,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(c_user),
):
    if instrument.ratio <= 0:
        raise HTTPException(
            status_code=422, detail="the value of 'ratio' must be greater than zero"
        )
    stmt = (
        update(asset_ratio)
        .where(asset_ratio.c.user_id == user.id, asset_ratio.c.id == ratio_id)
        .values(
            user_id=user.id,
            ratio=instrument.ratio,
            instrument=instrument.instrument_id,
            name=instrument.name,
            figi=instrument.figi,
        )
    ).returning(asset_ratio.c.id)

    try:
        result = await session.execute(stmt)
        await session.commit()
    except Exception as e:
        raise HTTPException(
            status_code=422, detail="the specified values cannot be processed"
        )
    return {
        "status_code": 200,
        "content": "the record has been successfully changed",
        "record ID": result.first()[0],
    }


@route.delete("/ratio_delete")
async def set_instrument_ratio(
    asset_ratio_id: int,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(c_user),
):
    stmt = (
        delete(asset_ratio)
        .where(asset_ratio.c.id == asset_ratio_id)
        .returning(asset_ratio.c.id)
    )
    result = await session.execute(stmt)
    await session.commit()
    id = result.first()
    id = id[0] if id else None
    if id:
        return {"status_code": 200, "content": "the record was successfully deleted"}
    else:
        raise HTTPException(
            status_code=404, detail="there is no record with the specified number"
        )


@route.get("/users")
async def get_users(
    session: AsyncSession = Depends(get_async_session),
    super_user: User = Depends(c_user),
) -> list[UsersTokens]:
    if super_user.is_superuser:
        query = select(user.c.id, user.c.username, user.c.tinkoff_invest_token)
        result = await session.execute(query)
        await session.commit()
        content = list()
        for i in result.all():
            content.append(i._asdict())
        return content
    else:
        return {"status_code": 403, "content": "You are not a super user"}
