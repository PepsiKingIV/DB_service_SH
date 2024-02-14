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
    UsersTokens,
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


# class Recorder:
#     def __init__(self, url, email, password) -> None:
#         self.url = url
#         self.email = email
#         self.password = password

#     async def login(self) -> int:
#         data = {"username": self.email, "password": self.password}
#         request = await requests.post(f"{self.url}/auth/jwt/login", data=data)
#         if request.status_code == 200:
#             cookies = request.cookies.get_dict()
#             self.cookies = {"operations": cookies}
#             await logger.info("OperationRecorder has been successfully logged in")
#             return 0
#         else:
#             await logger.error(
#                 request.status_code,
#                 "|\t",
#                 request.content,
#                 "|\t",
#                 "OperationRecorder couldn't log in",
#             )
#             return 1

#     async def receiving_and_recording_operation_data(
#         self,
#         token: str,
#         user_id: int,
#         date_from: datetime | None = datetime.now() - timedelta(days=120),
#         date_to: datetime | None = datetime.now(),
#     ):
#         operations = await BrokerDataAdapterTinkoff(token).get_operations(
#             date_from=date_from, date_to=date_to
#         )
#         for i in operations:
#             request = await requests.post(
#                 f"{self.url}/operation/post_super",
#                 data=RequestOperationSuper(
#                     user_id=user_id,
#                     buy=i.buy,
#                     price=i.price,
#                     figi=i.figi,
#                     count=i.count,
#                     date=i.date,
#                 ),
#                 cookies=self.cookies,
#             )
#             if request.status_code != 201:
#                 await logger.error(user_id, i, "the operation was not recorded")
#                 # TODO: придумать, куда класть незаписанные данные, чтобы позже их обработать

#     async def receiving_and_recording_asset_data(
#         self,
#         token: str,
#         user_id: int,
#     ):
#         assets = await BrokerDataAdapterTinkoff(token).get_assets()
#         for i in assets:
#             request = await requests.post(
#                 url=f"{self.url}/asset/post",
#                 cookies=self.cookies,
#                 data=UsersAsset(
#                     user_id=user_id,
#                     figi=i.figi,
#                     name=i.name,
#                     asset_type=i.asset_type,
#                     price=i.price,
#                     count=i.count,
#                 ),
#             )
#             if request.status_code != 201:
#                 await logger.error(user_id, i, "the asset was not recorded")
#                 # TODO: придумать, куда класть незаписанные данные, чтобы позже их обработать


class AsyncRecorder(IRecorder):
    _users: list[UsersTokens] = list()
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
                            UsersTokens(
                                id=i["id"],
                                tinkoff_invest_token=i["tinkoff_invest_token"],
                                username=i["username"],
                            )
                        )


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
