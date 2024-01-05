import json
import pytest
from sqlalchemy import select, insert, delete, update
from conftest import async_session_maker, client
from user.models import instrument, asset_ratio
from auth.models import user
from datetime import datetime
from httpx import AsyncClient

LOGIN_COOKIES = ""

# TODO : переделать коды ответов во всех роутах
# TODO : переписать название путей(сделать везде либо дифис либо нижнее подчеркивание)


@pytest.fixture(autouse=True, scope="session")
async def add_user(ac: AsyncClient):
    json = {
        "email": "alex@gmail.com",
        "password": "alex",
        "is_active": True,
        "is_superuser": False,
        "is_verified": False,
        "username": "alex",
        "tinkoff_invest_token": "alex",
    }
    response1 = await ac.post(
        "/auth/register",
        json=json,
    )
    async with async_session_maker() as session:
        stmt = (
            update(user)
            .values(is_superuser=True)
            .where(user.c.email == "alex@gmail.com")
        )
        await session.execute(stmt)
        await session.commit()
    response2 = await ac.post(
        "/auth/jwt/login",
        data={
            "password": "alex",
            "username": "alex@gmail.com",
        },
    )
    global LOGIN_COOKIES
    LOGIN_COOKIES = response2.cookies["operations"]
    yield


class TestUsersAction:
    async def test_set_username(self, ac: AsyncClient):
        response = await ac.post(
            "/user/set-username",
            params={"username": "new_username"},
            cookies={"operations": LOGIN_COOKIES},
        )
        assert response.status_code == 200

    async def test_set_username_int(self, ac: AsyncClient):
        response = await ac.post(
            "/user/set-username",
            params={"username": 223523},
            cookies={"operations": LOGIN_COOKIES},
        )
        assert response.status_code == 200

    async def test_set_username_more_50_characters(self, ac: AsyncClient):
        response = await ac.post(
            "/user/set-username",
            params={
                "username": "123456789123456789123456789123456789123456789123456789"
            },
            cookies={"operations": LOGIN_COOKIES},
        )
        assert response.status_code == 422

    async def test_set_token(self, ac: AsyncClient):
        response = await ac.post(
            "/user/set-token",
            params={"token": "t32x2"},
            cookies={"operations": LOGIN_COOKIES},
        )
        assert response.status_code == 200

    async def test_set_token_more_200_characters(self, ac: AsyncClient):
        response = await ac.post(
            "/user/set-token",
            params={
                "token": """1234567890123456789012345678901234567890
    1234567890123456789012345678901234567890
    1234567890123456789012345678901234567890
    1234567890123456789012345678901234567890
    12345678901234567890123456789012345678901"""
            },
            cookies={"operations": LOGIN_COOKIES},
        )
        assert response.status_code == 200

    async def test_get_user(self, ac: AsyncClient):
        response = await ac.get(
            "/user/",
            cookies={"operations": LOGIN_COOKIES},
        )
        assert response.status_code == 200
        assert json.loads(response.content.decode()) == {
            "email": "alex@gmail.com",
            "username": "223523",
        }

    async def test_get_instrument_list(self, ac: AsyncClient):
        response = await ac.get(
            "/user/instrument-list",
            cookies={"operations": LOGIN_COOKIES},
        )
        assert response.status_code == 200
        assert json.loads(response.content.decode()) == [
            {"id": 1, "type_name": "share"},
            {"id": 2, "type_name": "bond"},
        ]

    async def test_get_all_users(self, ac: AsyncClient):
        response = await ac.get(
            "/user/users",
            cookies={"operations": LOGIN_COOKIES},
        )
        assert response.status_code == 200


class TestSetGetRatio:
    async def test_set_ratio_basic_case(self, ac: AsyncClient):
        response = await ac.post(
            "/user/set-ratio",
            json={
                "instrument_id": 1,
                "ratio": 0.25,
                "name": "string",
                "figi": "string",
            },
            cookies={"operations": LOGIN_COOKIES},
        )
        assert response.status_code == 201

    async def test_set_ratio_non_existent_index(self, ac: AsyncClient):
        response = await ac.post(
            "/user/set-ratio",
            json={
                "instrument_id": 5,
                "ratio": 0.25,
                "name": "string",
                "figi": "string",
            },
            cookies={"operations": LOGIN_COOKIES},
        )
        assert response.status_code == 422

    async def test_set_ratio_str(self, ac: AsyncClient):
        response = await ac.post(
            "/user/set-ratio",
            json={
                "instrument_id": 2,
                "ratio": "0.25",
                "name": "string",
                "figi": "string",
            },
            cookies={"operations": LOGIN_COOKIES},
        )
        print(response.content)
        assert response.status_code == 201

    async def test_set_ratio_letters(self, ac: AsyncClient):
        response = await ac.post(
            "/user/set-ratio",
            json={
                "instrument_id": 2,
                "ratio": "vere2",
                "name": "string",
                "figi": "string",
            },
            cookies={"operations": LOGIN_COOKIES},
        )
        assert response.status_code == 422

    async def test_get_ratio(self, ac: AsyncClient):
        response = await ac.get(
            "/user/ratio",
            cookies={"operations": LOGIN_COOKIES},
        )
        assert response.status_code == 200
        print()
        assert json.loads(response.content.decode()) == [
            {"type_name": "share", "ratio": 0.25, "id": 1},
            {"type_name": "bond", "ratio": 0.25, "id": 3},
        ]


class TestUpdateDeleteRatio:
    async def test_update_ratio(self, ac: AsyncClient):
        response = await ac.put(
            "/user/ratio-update",
            params={"ratio_id": 1},
            json={"instrument_id": 2, "ratio": 0.5, "name": "string", "figi": "string"},
            cookies={"operations": LOGIN_COOKIES},
        )
        assert response.status_code == 200

    async def test_update_ratio_str(self, ac: AsyncClient):
        response = await ac.put(
            "/user/ratio-update",
            params={"ratio_id": 1},
            json={
                "instrument_id": 2,
                "ratio": "0.5",
                "name": "string",
                "figi": "string",
            },
            cookies={"operations": LOGIN_COOKIES},
        )
        assert response.status_code == 200

    async def test_update_ratio_letters(self, ac: AsyncClient):
        response = await ac.put(
            "/user/ratio-update",
            params={"ratio_id": 1},
            json={
                "instrument_id": 2,
                "ratio": "gwerber",
                "name": "string",
                "figi": "string",
            },
            cookies={"operations": LOGIN_COOKIES},
        )
        assert response.status_code == 422

    async def test_update_ratio_withuot_instrument_id(self, ac: AsyncClient):
        response = await ac.put(
            "/user/ratio-update",
            params={"ratio_id": 1},
            json={
                "ratio": 0.21,
                "name": "string",
                "figi": "string",
            },
            cookies={"operations": LOGIN_COOKIES},
        )
        assert response.status_code == 422

    async def test_update_ratio_withuot_ratio(self, ac: AsyncClient):
        response = await ac.put(
            "/user/ratio-update",
            params={"ratio_id": 1},
            json={
                "instrument_id": 2,
                "name": "string",
                "figi": "string",
            },
            cookies={"operations": LOGIN_COOKIES},
        )
        assert response.status_code == 422

    async def test_delete_ratio(self, ac: AsyncClient):
        response = await ac.delete(
            "/user/ratio_delete",
            params={"asset_ratio_id": 1},
            cookies={"operations": LOGIN_COOKIES},
        )
        print(response.content)
        assert response.status_code == 200

    async def test_delete_ratio_str(self, ac: AsyncClient):
        response = await ac.delete(
            "/user/ratio_delete",
            params={"asset_ratio_id": "3"},
            cookies={"operations": LOGIN_COOKIES},
        )
        print(response.content)
        assert response.status_code == 200

    async def test_delete_ratio_str(self, ac: AsyncClient):
        response = await ac.delete(
            "/user/ratio_delete",
            params={"asset_ratio_id": "dvgw"},
            cookies={"operations": LOGIN_COOKIES},
        )
        print(response.content)
        assert response.status_code == 422
