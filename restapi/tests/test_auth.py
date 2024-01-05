import pytest
from sqlalchemy import select, insert, delete, update
from conftest import async_session_maker, client
from user.models import instrument
from datetime import datetime
from httpx import AsyncClient


@pytest.fixture(autouse=True, scope="session")
async def add_user(ac: AsyncClient):
    json = {
        "email": "test_auth@gmail.com",
        "password": "test_auth",
        "is_active": True,
        "is_superuser": False,
        "is_verified": False,
        "username": "test_auth",
        "tinkoff_invest_token": "test_auth",
    }
    response1 = await ac.post(
        "/auth/register",
        json=json,
    )
    yield


class TestBasicCase:
    async def test_register_basic_case(self, ac: AsyncClient):
        json = {
            "email": "test1@gmail.com",
            "password": "test1",
            "is_active": True,
            "is_superuser": False,
            "is_verified": False,
            "username": "test1",
            "tinkoff_invest_token": "test1",
        }
        response = await ac.post(
            "/auth/register",
            json=json,
        )
        assert response.status_code == 201

    async def test_register_existing_user(self, ac: AsyncClient):
        json = {
            "email": "test_auth@gmail.com",
            "password": "test_auth",
            "is_active": True,
            "is_superuser": False,
            "is_verified": False,
            "username": "test_auth",
            "tinkoff_invest_token": "test_auth",
        }
        response = await ac.post(
            "/auth/register",
            json=json,
        )
        my_json = response.content.decode()
        assert response.status_code == 400
        assert "REGISTER_USER_ALREADY_EXISTS" in my_json

    async def test_register_wrong_email(self, ac: AsyncClient):
        json = {
            "email": "test10",
            "password": "test10",
            "is_active": True,
            "is_superuser": False,
            "is_verified": False,
            "username": "test10",
            "tinkoff_invest_token": "test10",
        }
        response = await ac.post(
            "/auth/register",
            json=json,
        )
        assert response.status_code == 422

    async def test_register_SQLi(self, ac: AsyncClient):
        json = {
            "email": "test7@gmail.com",
            "password": ";DROPDB public.user;",
            "is_active": True,
            "is_superuser": False,
            "is_verified": False,
            "username": "test7",
            "tinkoff_invest_token": ";TRUNCATE public.user;",
        }
        response = await ac.post(
            "/auth/register",
            json=json,
        )
        assert response.status_code == 201


class TestWithoutParameters:
    async def test_register_without_email(self, ac: AsyncClient):
        json = {
            "password": "test2",
            "is_active": True,
            "is_superuser": False,
            "is_verified": False,
            "username": "test2",
            "tinkoff_invest_token": "test2",
        }
        response = await ac.post(
            "/auth/register",
            json=json,
        )
        assert response.status_code == 422

    async def test_register_without_username(self, ac: AsyncClient):
        json = {
            "email": "test3@gmail.com",
            "password": "test3",
            "is_active": True,
            "is_superuser": False,
            "is_verified": False,
            "tinkoff_invest_token": "test3",
        }
        response = await ac.post(
            "/auth/register",
            json=json,
        )
        assert response.status_code == 422

    async def test_register_without_password(self, ac: AsyncClient):
        json = {
            "email": "test4@gmail.com",
            "is_active": True,
            "is_superuser": False,
            "is_verified": False,
            "username": "test4",
            "tinkoff_invest_token": "test4",
        }
        response = await ac.post(
            "/auth/register",
            json=json,
        )
        assert response.status_code == 422

    async def test_register_without_isparameters(self, ac: AsyncClient):
        json = {
            "email": "test5@gmail.com",
            "password": "test5",
            "username": "test5",
            "tinkoff_invest_token": "test5",
        }
        response = await ac.post(
            "/auth/register",
            json=json,
        )
        assert response.status_code == 201

    async def test_register_without_all_parameters(self, ac: AsyncClient):
        json = {}
        response = await ac.post(
            "/auth/register",
            json=json,
        )
        assert response.status_code == 422


class TestTooLargeValue:
    async def test_register_username_more_50_characters(self, ac: AsyncClient):
        json = {
            "email": "test6@gmail.com",
            "password": 1432,
            "is_active": True,
            "is_superuser": False,
            "is_verified": False,
            "username": "123456789012345678901234567890123456789012345678901",
            "tinkoff_invest_token": "test6",
        }
        response = await ac.post(
            "/auth/register",
            json=json,
        )
        assert response.status_code == 422

    async def test_register_emain_more_50_characters(self, ac: AsyncClient):
        json = {
            "email": "123456789012345678901234567890123456789012345678901@gmail.com",
            "password": 1432,
            "is_active": True,
            "is_superuser": False,
            "is_verified": False,
            "username": "test2122",
            "tinkoff_invest_token": "test2122",
        }
        response = await ac.post(
            "/auth/register",
            json=json,
        )
        assert response.status_code == 422

    async def test_register_token_more_200_characters(self, ac: AsyncClient):
        json = {
            "email": "test21412@gmail.com",
            "password": 1432,
            "is_active": True,
            "is_superuser": False,
            "is_verified": False,
            "username": "test21412",
            "tinkoff_invest_token": """1234567890123456789012345678901234567890
1234567890123456789012345678901234567890
1234567890123456789012345678901234567890
1234567890123456789012345678901234567890
12345678901234567890123456789012345678901""",
        }
        response = await ac.post(
            "/auth/register",
            json=json,
        )
        assert response.status_code == 422


class TestTypeParameters:
    async def test_register_int_password(self, ac: AsyncClient):
        json = {
            "email": "test6@gmail.com",
            "password": 1432,
            "is_active": True,
            "is_superuser": False,
            "is_verified": False,
            "username": "test6",
            "tinkoff_invest_token": "test6",
        }
        response = await ac.post(
            "/auth/register",
            json=json,
        )
        assert response.status_code == 201

    async def test_register_int_username(self, ac: AsyncClient):
        json = {
            "email": "test8@gmail.com",
            "password": "test8",
            "is_active": True,
            "is_superuser": False,
            "is_verified": False,
            "username": 32141,
            "tinkoff_invest_token": "test8",
        }
        response = await ac.post(
            "/auth/register",
            json=json,
        )
        assert response.status_code == 201

    async def test_register_int_token(self, ac: AsyncClient):
        json = {
            "email": "test9@gmail.com",
            "password": "test9",
            "is_active": True,
            "is_superuser": False,
            "is_verified": False,
            "username": "test9",
            "tinkoff_invest_token": 41208012,
        }
        response = await ac.post(
            "/auth/register",
            json=json,
        )
        assert response.status_code == 201


class TestLogin:
    async def test_login_basic_case(self, ac: AsyncClient):
        response = await ac.post(
            "/auth/jwt/login",
            data={
                "password": "test1",
                "username": "test1@gmail.com",
            },
        )
        assert response.status_code == 204

    async def test_login_wrong_password(self, ac: AsyncClient):
        response = await ac.post(
            "/auth/jwt/login",
            data={
                "password": "tes",
                "username": "test1@gmail.com",
            },
        )
        assert response.status_code == 400
        assert "LOGIN_BAD_CREDENTIALS" in response.content.decode()

    async def test_login_wrong_email(self, ac: AsyncClient):
        response = await ac.post(
            "/auth/jwt/login",
            data={
                "password": "test1",
                "username": "tes@gmail.com",
            },
        )
        assert response.status_code == 400
        assert "LOGIN_BAD_CREDENTIALS" in response.content.decode()
