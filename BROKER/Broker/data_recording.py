from ast import literal_eval
import asyncio
import logging
import aiohttp
import requests
import io
from datetime import datetime, timedelta

from schemas import (
    RequestOperationSuper,
    SuperUser,
    UsersAsset,
    Urls,
    UsersToken,
)
from Interfaces import IRecorder
from Exceptions import LoginException, RequestException

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler(f"data_recording.log", mode="w")
formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.info(f"Logger for data_rocorder. Start:{datetime.now()}")


class AsyncRecorder(IRecorder):
    _users: list[UsersToken] = list()
    _cookies: dict = None

    def __init__(
        self,
        urls: Urls,
        super_user: SuperUser,
    ):
        self._authorization_url: str = urls.authorization_url
        self._post_operation_url: str = urls.post_operation_url
        self._post_asset_url: str = urls.post_asset_url
        self._get_tokens_url: str = urls.get_tokens_url
        self._super_user: SuperUser = super_user

    async def authorization(self) -> None:
        async with aiohttp.ClientSession() as session:
            data = {
                "password": self._super_user.password,
                "username": self._super_user.email,
            }
            async with session.post(
                url=self._authorization_url,
                data=data,
                timeout=aiohttp.ClientTimeout(total=1),
            ) as result:
                if result.status == 204:
                    self._cookies = {"operations": result.headers["Set-Cookie"][11:168]}
                else:
                    raise LoginException(
                        f"Не удалось войти в аккаунт. status_code:{result.status}",
                    )

    async def get_tokens(self) -> None:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=self._get_tokens_url, cookies=self._cookies
            ) as result:
                if result.status != 200:
                    raise RequestException(
                        f"Не удалось получить пользователей. status_code:{result.status}"
                    )
                else:
                    bytes_result = await result.read()
                    for i in literal_eval(bytes_result.decode()):
                        print(i)
                        self._users.append(
                            UsersToken(
                                id=i["id"],
                                tinkoff_invest_token=i["tinkoff_invest_token"],
                                username=i["username"],
                            )
                        )
                    return self._users

    async def set_operation(self, user: UsersToken) -> None:

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=self._get_tokens_url, cookies=self._cookies
            ) as result:
                pass


async def main():
    urls = Urls(
        authorization_url="http://31.129.105.185/auth/jwt/login",
        get_tokens_url="http://31.129.105.185/user/users",
        post_asset_url="http://31.129.105.185",
        post_operation_url="http://31.129.105.185",
    )
    super_user = SuperUser(email="test@test.com", password="test51445")
    bip = AsyncRecorder(urls=urls, super_user=super_user)
    await asyncio.create_task(bip.authorization())
    await asyncio.create_task(bip.get_tokens())


if __name__ == "__main__":
    asyncio.run(main=main())
