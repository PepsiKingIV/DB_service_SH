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
        "email": "felix@gmail.com",
        "password": "felix",
        "is_active": True,
        "is_superuser": False,
        "is_verified": False,
        "username": "felix",
        "tinkoff_invest_token": "felix",
    }
    response1 = await ac.post(
        "/auth/register",
        json=json,
    )
    async with async_session_maker() as session:
        stmt = (
            update(user)
            .values(is_superuser=True)
            .where(user.c.email == "felix@gmail.com")
        )
        await session.execute(stmt)
        await session.commit()
    response2 = await ac.post(
        "/auth/jwt/login",
        data={
            "password": "felix",
            "username": "felix@gmail.com",
        },
    )
    global LOGIN_COOKIES
    LOGIN_COOKIES = response2.cookies["operations"]
    await ac.post(
        "/operation/post",
        json={
            "buy": True,
            "price": 241.32,
            "figi": "figi111",
            "count": 2,
            "date": "2024-01-05T19:00:15.299Z",
            "justification": "string",
            "expectations": "string",
        },
        cookies={"operations": LOGIN_COOKIES},
    )
    await ac.post(
        "/operation/post",
        json={
            "buy": True,
            "price": 241.32,
            "figi": "figi111",
            "count": 2,
            "date": "2024-01-05T19:00:15.299Z",
            "justification": "string",
            "expectations": "string",
        },
        cookies={"operations": LOGIN_COOKIES},
    )
    await ac.post(
        "/operation/post",
        json={
            "buy": True,
            "price": 241.32,
            "figi": "figi111",
            "count": 2,
            "date": "2024-01-05T19:00:15.299Z",
            "justification": "string",
            "expectations": "string",
        },
        cookies={"operations": LOGIN_COOKIES},
    )
    yield


# TODO : добавить проверку на размер входных данных


class TestGet:
    async def test_basic_case(self, ac: AsyncClient):
        response = await ac.get(
            "/operation/get",
            cookies={"operations": LOGIN_COOKIES},
        )
        assert response.status_code == 200


class TestPost:
    async def test_basic_case(self, ac: AsyncClient):
        response = await ac.post(
            "/operation/post",
            json={
                "buy": True,
                "price": 241.32,
                "figi": "figi111",
                "count": 2,
                "date": "2024-01-05T19:00:15.299Z",
                "justification": "string",
                "expectations": "string",
            },
            cookies={"operations": LOGIN_COOKIES},
        )
        assert response.status_code == 201

    async def test_str_price(self, ac: AsyncClient):
        response = await ac.post(
            "/operation/post",
            json={
                "buy": True,
                "price": "241.32",
                "figi": "figi111",
                "count": 2,
                "date": "2024-01-05T19:00:15.299Z",
                "justification": "string",
                "expectations": "string",
            },
            cookies={"operations": LOGIN_COOKIES},
        )
        assert response.status_code == 201

    async def test_letter_price(self, ac: AsyncClient):
        response = await ac.post(
            "/operation/post",
            json={
                "buy": True,
                "price": "dsglegwe",
                "figi": "figi111",
                "count": 2,
                "date": "2024-01-05T19:00:15.299Z",
                "justification": "string",
                "expectations": "string",
            },
            cookies={"operations": LOGIN_COOKIES},
        )
        assert response.status_code == 422

    async def test_negative_price(self, ac: AsyncClient):
        response = await ac.post(
            "/operation/post",
            json={
                "buy": True,
                "price": -1241.42,
                "figi": "figi111",
                "count": 2,
                "date": "2024-01-05T19:00:15.299Z",
                "justification": "string",
                "expectations": "string",
            },
            cookies={"operations": LOGIN_COOKIES},
        )
        print(response.content)
        assert response.status_code == 422

    async def test_not_bool_buy(self, ac: AsyncClient):
        response = await ac.post(
            "/operation/post",
            json={
                "buy": 1241,
                "price": 123.12,
                "figi": "figi111",
                "count": 2,
                "date": "2024-01-05T19:00:15.299Z",
                "justification": "string",
                "expectations": "string",
            },
            cookies={"operations": LOGIN_COOKIES},
        )
        assert response.status_code == 422

    async def test_zero_count(self, ac: AsyncClient):
        response = await ac.post(
            "/operation/post",
            json={
                "buy": True,
                "price": 1241.42,
                "figi": "figi111",
                "count": 0,
                "date": "2024-01-05T19:00:15.299Z",
                "justification": "string",
                "expectations": "string",
            },
            cookies={"operations": LOGIN_COOKIES},
        )
        assert response.status_code == 422

    async def test_negative_count(self, ac: AsyncClient):
        response = await ac.post(
            "/operation/post",
            json={
                "buy": True,
                "price": 1241.42,
                "figi": "figi111",
                "count": -4,
                "date": "2024-01-05T19:00:15.299Z",
                "justification": "string",
                "expectations": "string",
            },
            cookies={"operations": LOGIN_COOKIES},
        )
        assert response.status_code == 422

    async def test_date_without_timezone(self, ac: AsyncClient):
        response = await ac.post(
            "/operation/post",
            json={
                "buy": True,
                "price": 1241.42,
                "figi": "figi111",
                "count": 4,
                "date": "2024-01-05T19:00:15.299",
                "justification": "string",
                "expectations": "string",
            },
            cookies={"operations": LOGIN_COOKIES},
        )
        assert response.status_code == 201

    async def test_without_justification(self, ac: AsyncClient):
        response = await ac.post(
            "/operation/post",
            json={
                "buy": True,
                "price": 1241.42,
                "figi": "figi111",
                "count": 4,
                "date": "2024-01-05T19:00:15.299",
                "expectations": "string",
            },
            cookies={"operations": LOGIN_COOKIES},
        )
        assert response.status_code == 201

    async def test_without_expectations(self, ac: AsyncClient):
        response = await ac.post(
            "/operation/post",
            json={
                "buy": True,
                "price": 1241.42,
                "figi": "figi111",
                "count": 4,
                "date": "2024-01-05T19:00:15.299",
                "justification": "string",
            },
            cookies={"operations": LOGIN_COOKIES},
        )
        assert response.status_code == 201

    async def test_great_price(self, ac: AsyncClient):
        response = await ac.post(
            "/operation/post",
            json={
                "buy": True,
                "price": 12345678901234567890123456789012345678901234567890123456789012345678901234567890.12345678901234567890123456789012345678901234567890123456789012345678901234567890,
                "figi": "figi111",
                "count": 4,
                "date": "2024-01-05T19:00:15.299",
                "justification": "string",
                "expectations": "string",
            },
            cookies={"operations": LOGIN_COOKIES},
        )
        assert response.status_code == 422

    async def test_great_count(self, ac: AsyncClient):
        response = await ac.post(
            "/operation/post",
            json={
                "buy": True,
                "price": 1241.42,
                "figi": "figi111",
                "count": 12345678901234567890123456789012345678901234567890123456789012345678901234567890,
                "date": "2024-01-05T19:00:15.299",
                "justification": "string",
                "expectations": "string",
            },
            cookies={"operations": LOGIN_COOKIES},
        )
        assert response.status_code == 422

    async def test_large_figi(self, ac: AsyncClient):
        response = await ac.post(
            "/operation/post",
            json={
                "buy": True,
                "price": 1241.42,
                "figi": "figi1111234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890",
                "count": 12,
                "date": "2024-01-05T19:00:15.299",
                "justification": "string",
                "expectations": "string",
            },
            cookies={"operations": LOGIN_COOKIES},
        )
        assert response.status_code == 422


class TestDelete:
    async def test_basic_case(self, ac: AsyncClient):
        response = await ac.delete(
            "/operation/delete",
            params={"operation_id": 2},
            cookies={"operations": LOGIN_COOKIES},
        )
        print(response.content)
        assert response.status_code == 204

    async def test_non_existent_record(self, ac: AsyncClient):
        response = await ac.delete(
            "/operation/delete",
            params={"operation_id": 120},
            cookies={"operations": LOGIN_COOKIES},
        )
        assert response.status_code == 404

    async def test_id_str(self, ac: AsyncClient):
        response = await ac.delete(
            "/operation/delete",
            params={"operation_id": "3"},
            cookies={"operations": LOGIN_COOKIES},
        )
        assert response.status_code == 204


class TestPut:
    async def test_basic_case(self, ac: AsyncClient):
        response = await ac.put(
            "/operation/put",
            json={
                "new_operation": {
                    "buy": True,
                    "price": 111,
                    "figi": "string",
                    "count": 111,
                    "date": "2024-01-05T19:35:25.496Z",
                    "justification": "string",
                    "expectations": "string",
                },
                "operation_id": 1,
            },
            cookies={"operations": LOGIN_COOKIES},
        )
        assert response.status_code == 202

    async def test_str_price(self, ac: AsyncClient):
        response = await ac.put(
            "/operation/put",
            json={
                "new_operation": {
                    "buy": True,
                    "price": "111",
                    "figi": "string",
                    "count": 111,
                    "date": "2024-01-05T19:35:25.496Z",
                    "justification": "string",
                    "expectations": "string",
                },
                "operation_id": 1,
            },
            cookies={"operations": LOGIN_COOKIES},
        )
        print(response.content)
        assert response.status_code == 202

    async def test_str_count(self, ac: AsyncClient):
        response = await ac.put(
            "/operation/put",
            json={
                "new_operation": {
                    "buy": True,
                    "price": 111,
                    "figi": "string",
                    "count": "111",
                    "date": "2024-01-05T19:35:25.496Z",
                    "justification": "string",
                    "expectations": "string",
                },
                "operation_id": 1,
            },
            cookies={"operations": LOGIN_COOKIES},
        )
        print(response.content)
        assert response.status_code == 202

    async def test_int_figi(self, ac: AsyncClient):
        response = await ac.put(
            "/operation/put",
            json={
                "new_operation": {
                    "buy": True,
                    "price": 111,
                    "figi": 47128802,
                    "count": 111,
                    "date": "2024-01-05T19:35:25.496Z",
                    "justification": "string",
                    "expectations": "string",
                },
                "operation_id": 1,
            },
            cookies={"operations": LOGIN_COOKIES},
        )
        assert response.status_code == 202

    async def test_without_date(self, ac: AsyncClient):
        response = await ac.put(
            "/operation/put",
            json={
                "new_operation": {
                    "buy": True,
                    "price": 111,
                    "figi": "47128802",
                    "count": 111,
                    "justification": "string",
                    "expectations": "string",
                },
                "operation_id": 1,
            },
            cookies={"operations": LOGIN_COOKIES},
        )
        assert response.status_code == 422

    async def test_without_timezone_date(self, ac: AsyncClient):
        response = await ac.put(
            "/operation/put",
            json={
                "new_operation": {
                    "buy": True,
                    "price": 111,
                    "figi": "47128802",
                    "count": 111,
                    "date": "2024-01-05T19:35:25.496",
                    "justification": "string",
                    "expectations": "string",
                },
                "operation_id": 1,
            },
            cookies={"operations": LOGIN_COOKIES},
        )
        assert response.status_code == 202

    async def test_without_timezone_date(self, ac: AsyncClient):
        response = await ac.put(
            "/operation/put",
            json={
                "new_operation": {
                    "buy": True,
                    "price": 111,
                    "figi": "47128802",
                    "count": 111,
                    "date": "2024-01-05T19:35:25.496",
                    "justification": "string",
                    "expectations": "string",
                },
                "operation_id": 1,
            },
            cookies={"operations": LOGIN_COOKIES},
        )
        assert response.status_code == 202

    async def test_without_justification(self, ac: AsyncClient):
        response = await ac.put(
            "/operation/put",
            json={
                "new_operation": {
                    "buy": True,
                    "price": 111,
                    "figi": "47128802",
                    "count": 111,
                    "date": "2024-01-05T19:35:25.496Z",
                    "expectations": "string",
                },
                "operation_id": 1,
            },
            cookies={"operations": LOGIN_COOKIES},
        )
        assert response.status_code == 202

    async def test_without_expectations(self, ac: AsyncClient):
        response = await ac.put(
            "/operation/put",
            json={
                "new_operation": {
                    "buy": True,
                    "price": 111,
                    "figi": "47128802",
                    "count": 111,
                    "date": "2024-01-05T19:35:25.496Z",
                    "justification": "string",
                },
                "operation_id": 1,
            },
            cookies={"operations": LOGIN_COOKIES},
        )
        print(response.content)
        assert response.status_code == 202

    async def test_large_price(self, ac: AsyncClient):
        response = await ac.put(
            "/operation/put",
            json={
                "new_operation": {
                    "buy": True,
                    "price": 1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890,
                    "figi": "47128802",
                    "count": 111,
                    "date": "2024-01-05T19:35:25.496Z",
                    "justification": "string",
                    "expectations": "string",
                },
                "operation_id": 1,
            },
            cookies={"operations": LOGIN_COOKIES},
        )
        assert response.status_code == 422

    async def test_large_count(self, ac: AsyncClient):
        response = await ac.put(
            "/operation/put",
            json={
                "new_operation": {
                    "buy": True,
                    "price": 123456,
                    "figi": "47128802",
                    "count": 1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890,
                    "date": "2024-01-05T19:35:25.496Z",
                    "justification": "string",
                    "expectations": "string",
                },
                "operation_id": 1,
            },
            cookies={"operations": LOGIN_COOKIES},
        )
        assert response.status_code == 422

    async def test_large_figi(self, ac: AsyncClient):
        response = await ac.put(
            "/operation/put",
            json={
                "new_operation": {
                    "buy": True,
                    "price": 123456,
                    "figi": "1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890",
                    "count": 3,
                    "date": "2024-01-05T19:35:25.496Z",
                    "justification": "string",
                    "expectations": "string",
                },
                "operation_id": 1,
            },
            cookies={"operations": LOGIN_COOKIES},
        )
        assert response.status_code == 422
