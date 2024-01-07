import json
import pytest
from sqlalchemy import select, insert, delete, update
from conftest import async_session_maker, client
from user.models import instrument
from datetime import datetime
from auth.models import user
from httpx import AsyncClient


LOGIN_COOKIES = ""


@pytest.fixture(autouse=True, scope="session")
async def add_user(ac: AsyncClient):
    json = {
        "email": "asset_test@gmail.com",
        "password": "asset_test",
        "is_active": True,
        "is_superuser": False,
        "is_verified": False,
        "username": "asset_test",
        "tinkoff_invest_token": "asset_test",
    }
    response1 = await ac.post(
        "/auth/register",
        json=json,
    )
    async with async_session_maker() as session:
        stmt = (
            update(user)
            .values(is_superuser=True)
            .where(user.c.email == "asset_test@gmail.com")
        )
        await session.execute(stmt)
        await session.commit()
    response2 = await ac.post(
        "/auth/jwt/login",
        data={
            "password": "asset_test",
            "username": "asset_test@gmail.com",
        },
    )
    global LOGIN_COOKIES
    LOGIN_COOKIES = response2.cookies["operations"]
    response = await ac.post(
        "/asset/post",
        json={
            "date": "2024-01-07T09:40:36.447Z",
            "figi": "string",
            "instrument_id": 1,
            "name": "YNDX",
            "price": 2400,
            "count": 3,
        },
        cookies={"operations": LOGIN_COOKIES},
    )
    yield


class TestGet:
    async def test_basic_case(self, ac: AsyncClient):
        response = await ac.get(
            "/asset/get",
            cookies={"operations": LOGIN_COOKIES},
        )
        assert response.status_code == 200


class TestPost:
    async def test_basic_case(self, ac: AsyncClient):
        response = await ac.post(
            "/asset/post",
            json={
                "date": "2024-01-07T10:01:26.471Z",
                "figi": "string",
                "instrument_id": 1,
                "name": "YNDX",
                "price": 2431,
                "count": 3,
            },
            cookies={"operations": LOGIN_COOKIES},
        )
        assert response.status_code == 201

    async def test_without_parametr(self, ac: AsyncClient):
        without_date = await ac.post(
            "/asset/post",
            json={
                "figi": "string",
                "instrument_id": 1,
                "name": "YNDX",
                "price": 2431,
                "count": 3,
            },
            cookies={"operations": LOGIN_COOKIES},
        )
        without_figi = await ac.post(
            "/asset/post",
            json={
                "date": "2024-01-07T10:01:26.471Z",
                "instrument_id": 1,
                "name": "YNDX",
                "price": 2431,
                "count": 3,
            },
            cookies={"operations": LOGIN_COOKIES},
        )
        without_instrument_id = await ac.post(
            "/asset/post",
            json={
                "date": "2024-01-07T10:01:26.471Z",
                "figi": "string",
                "name": "YNDX",
                "price": 2431,
                "count": 3,
            },
            cookies={"operations": LOGIN_COOKIES},
        )
        without_name = await ac.post(
            "/asset/post",
            json={
                "date": "2024-01-07T10:01:26.471Z",
                "figi": "string",
                "instrument_id": 1,
                "price": 2431,
                "count": 3,
            },
            cookies={"operations": LOGIN_COOKIES},
        )
        without_price = await ac.post(
            "/asset/post",
            json={
                "date": "2024-01-07T10:01:26.471Z",
                "figi": "string",
                "instrument_id": 1,
                "name": "YNDX",
                "count": 3,
            },
            cookies={"operations": LOGIN_COOKIES},
        )
        without_count = await ac.post(
            "/asset/post",
            json={
                "date": "2024-01-07T10:01:26.471Z",
                "figi": "string",
                "instrument_id": 1,
                "name": "YNDX",
                "price": 2431,
            },
            cookies={"operations": LOGIN_COOKIES},
        )
        assert without_date.status_code == 422
        assert without_price.status_code == 422
        assert without_count.status_code == 422
        assert without_figi.status_code == 422
        assert without_instrument_id.status_code == 422
        assert without_name.status_code == 422

    async def test_int_figi(self, ac: AsyncClient):
        response = await ac.post(
            "/asset/post",
            json={
                "date": "2024-01-07T10:01:26.471Z",
                "figi": 512512521,
                "instrument_id": 1,
                "name": "YNDX",
                "price": 2431,
                "count": 3,
            },
            cookies={"operations": LOGIN_COOKIES},
        )
        assert response.status_code == 201

    async def test_str_price(self, ac: AsyncClient):
        response = await ac.post(
            "/asset/post",
            json={
                "date": "2024-01-07T10:01:26.471Z",
                "figi": "512512521",
                "instrument_id": 1,
                "name": "YNDX",
                "price": "2421",
                "count": 3,
            },
            cookies={"operations": LOGIN_COOKIES},
        )
        assert response.status_code == 201

    async def test_str_count(self, ac: AsyncClient):
        response = await ac.post(
            "/asset/post",
            json={
                "date": "2024-01-07T10:01:26.471Z",
                "figi": "512512521",
                "instrument_id": 1,
                "name": "YNDX",
                "price": 2421,
                "count": "3",
            },
            cookies={"operations": LOGIN_COOKIES},
        )
        assert response.status_code == 201

    async def test_str_instrument_id(self, ac: AsyncClient):
        response = await ac.post(
            "/asset/post",
            json={
                "date": "2024-01-07T10:01:26.471Z",
                "figi": "512512521",
                "instrument_id": "1",
                "name": "YNDX",
                "price": 2421,
                "count": 3,
            },
            cookies={"operations": LOGIN_COOKIES},
        )
        assert response.status_code == 201


class TestPut:
    async def test_basic_case(self, ac: AsyncClient):
        response = await ac.put(
            "/asset/put",
            params={"asset_id": 1},
            json={
                "date": "2024-01-07T10:01:26.471",
                "figi": "st2r3i3n5g",
                "instrument_id": 1,
                "name": "VKCO",
                "price": 3431,
                "count": 4,
            },
            cookies={"operations": LOGIN_COOKIES},
        )
        assert response.status_code == 200

    async def test_without_parameter(self, ac: AsyncClient):
        without_date = await ac.put(
            "/asset/put",
            params={"asset_id": 1},
            json={
                "figi": "st2r3i3n5g",
                "instrument_id": 1,
                "name": "VKCO",
                "price": 3431,
                "count": 4,
            },
            cookies={"operations": LOGIN_COOKIES},
        )
        without_figi = await ac.put(
            "/asset/put",
            params={"asset_id": 1},
            json={
                "date": "2024-01-07T10:01:26.471",
                "instrument_id": 1,
                "name": "VKCO",
                "price": 3431,
                "count": 4,
            },
            cookies={"operations": LOGIN_COOKIES},
        )
        without_instrument_id = await ac.put(
            "/asset/put",
            params={"asset_id": 1},
            json={
                "date": "2024-01-07T10:01:26.471",
                "figi": "st2r3i3n5g",
                "name": "VKCO",
                "price": 3431,
                "count": 4,
            },
            cookies={"operations": LOGIN_COOKIES},
        )
        without_name = await ac.put(
            "/asset/put",
            params={"asset_id": 1},
            json={
                "date": "2024-01-07T10:01:26.471",
                "figi": "st2r3i3n5g",
                "instrument_id": 1,
                "price": 3431,
                "count": 4,
            },
            cookies={"operations": LOGIN_COOKIES},
        )
        without_price = await ac.put(
            "/asset/put",
            params={"asset_id": 1},
            json={
                "date": "2024-01-07T10:01:26.471",
                "figi": "st2r3i3n5g",
                "instrument_id": 1,
                "name": "VKCO",
                "count": 4,
            },
            cookies={"operations": LOGIN_COOKIES},
        )
        without_count = await ac.put(
            "/asset/put",
            params={"asset_id": 1},
            json={
                "date": "2024-01-07T10:01:26.471",
                "figi": "st2r3i3n5g",
                "instrument_id": 1,
                "name": "VKCO",
                "price": 3431,
            },
            cookies={"operations": LOGIN_COOKIES},
        )
        assert without_date.status_code == 422
        assert without_figi.status_code == 422
        assert without_instrument_id.status_code == 422
        assert without_name.status_code == 422
        assert without_price.status_code == 422
        assert without_count.status_code == 422

    async def test_types(self, ac: AsyncClient):
        int_figi = await ac.put(
            "/asset/put",
            params={"asset_id": 1},
            json={
                "date": "2024-01-07T10:01:26.471",
                "figi": 1231231,
                "instrument_id": 1,
                "name": "VKCO",
                "price": 3431,
                "count": 4,
            },
            cookies={"operations": LOGIN_COOKIES},
        )
        str_instrument_id = await ac.put(
            "/asset/put",
            params={"asset_id": 1},
            json={
                "date": "2024-01-07T10:01:26.471",
                "figi": "1231231",
                "instrument_id": "1",
                "name": "VKCO",
                "price": 3431,
                "count": 4,
            },
            cookies={"operations": LOGIN_COOKIES},
        )
        str_price = await ac.put(
            "/asset/put",
            params={"asset_id": 1},
            json={
                "date": "2024-01-07T10:01:26.471",
                "figi": "1231231",
                "instrument_id": 1,
                "name": "VKCO",
                "price": "3431",
                "count": 4,
            },
            cookies={"operations": LOGIN_COOKIES},
        )
        str_count = await ac.put(
            "/asset/put",
            params={"asset_id": 1},
            json={
                "date": "2024-01-07T10:01:26.471",
                "figi": "1231231",
                "instrument_id": 1,
                "name": "VKCO",
                "price": 3431,
                "count": "4",
            },
            cookies={"operations": LOGIN_COOKIES},
        )
        assert str_count.status_code == 200
        assert str_instrument_id.status_code == 200
        assert str_price.status_code == 200
        assert int_figi.status_code == 200


class TestDelete:
    async def test_basic_case(self, ac: AsyncClient):
        response = await ac.delete(
            "/asset/delete",
            params={"asset_id": 1},
            cookies={"operations": LOGIN_COOKIES},
        )
        assert response.status_code == 200

    async def test_basic_case(self, ac: AsyncClient):
        response = await ac.delete(
            "/asset/delete",
            params={"asset_id": "2"},
            cookies={"operations": LOGIN_COOKIES},
        )
        assert response.status_code == 200

    async def test_basic_case(self, ac: AsyncClient):
        response = await ac.delete(
            "/asset/delete",
            params={"asset_id": 1000},
            cookies={"operations": LOGIN_COOKIES},
        )
        assert response.status_code == 422
