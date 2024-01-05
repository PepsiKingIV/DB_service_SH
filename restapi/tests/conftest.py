import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient
from fastapi.testclient import TestClient
import pytest_asyncio
from sqlalchemy.pool import NullPool
from sqlalchemy import select, insert, delete, update

import pytest
from src.config import (
    DB_HOST_TEST,
    DB_NAME_TEST,
    DB_PASS_TEST,
    DB_USER_TEST,
)
from sqlalchemy.orm import sessionmaker
from user.models import instrument
from src.auth.utils import get_user_db
from src import metadata, get_async_session, app
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

DATABASE_URL_TEST = (
    f"postgresql+asyncpg://{DB_USER_TEST}:{DB_PASS_TEST}@{DB_HOST_TEST}/{DB_NAME_TEST}"
)

engine_test = create_async_engine(DATABASE_URL_TEST, poolclass=NullPool)
async_session_maker = sessionmaker(
    engine_test, class_=AsyncSession, expire_on_commit=False
)
metadata.bind = engine_test


async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


@pytest.fixture(scope="session")
async def prepare_database(request):
    async with engine_test.begin() as conn:
        await conn.run_sync(metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(metadata.drop_all)


@pytest_asyncio.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True, scope="session")
async def add_instrument_type(prepare_database):
    async with async_session_maker() as session:
        stmt = insert(instrument).values(id=1, type_name="share")
        await session.execute(stmt)
        stmt2 = insert(instrument).values(id=2, type_name="bond")
        await session.execute(stmt2)
        await session.commit()
    yield


app.dependency_overrides[get_async_session] = override_get_async_session


@pytest_asyncio.fixture(scope="session", autouse=False)
async def async_client(request):
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    await client.close()


client = TestClient(app=app, base_url="http://test")


@pytest.fixture(scope="session")
async def ac(request, follow_redirects=True) -> AsyncGenerator[AsyncSession, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
