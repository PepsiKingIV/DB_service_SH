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
from Exceptions import LoginException, RequestException, PostOperation, PostAsset
from data_extractor import BrokerDataAdapterTinkoff

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
    _instrument_dict: dict = dict()

    def __init__(
        self,
        urls: Urls,
        super_user: SuperUser,
    ):
        self._authorization_url: str = urls.authorization_url
        self._post_operation_url: str = urls.post_operation_url
        self._post_asset_url: str = urls.post_asset_url
        self._get_tokens_url: str = urls.get_tokens_url
        self._get_instrument_list: str = urls.get_instrument_list
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
            async with session.get(
                url=self._get_instrument_list, cookies=self._cookies
            ) as result2:
                if result2.status == 200:
                    response_data = await result2.content.read()
                    for i in literal_eval(response_data.decode()):
                        self._instrument_dict[i["type_name"]] = i["id"]

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
                        self._users.append(
                            UsersToken(
                                id=i["id"],
                                tinkoff_invest_token=i["tinkoff_invest_token"],
                                username=i["username"],
                            )
                        )
                    return self._users

    async def set_operation(self, user: UsersToken) -> None:
        try:
            operations_in_last_hour = BrokerDataAdapterTinkoff(
                user.tinkoff_invest_token
            ).get_operations(
                date_from=datetime.now() - timedelta.min(60), date_to=datetime.now()
            )
        except Exception as e:
            raise PostOperation(e)
        async with aiohttp.ClientSession() as session:
            for i in operations_in_last_hour:
                async with session.post(
                    url=self._post_operation_url,
                    cookies=self._cookies,
                    data={
                        "user_id": user.id,
                        "buy": i.buy,
                        "price": i.price,
                        "figi": i.figi,
                        "count": i.count,
                        "date": i.date,
                    },
                ) as result:
                    if result.status != 202:
                        raise PostOperation("status code : ", result.status)

    async def set_assets(self, user: UsersToken):
        try:
            open_positions = BrokerDataAdapterTinkoff(
                user.tinkoff_invest_token
            ).get_assets()
        except Exception as e:
            raise PostAsset(e)

        async with aiohttp.ClientSession() as session:

            for i in open_positions:
                async with session.post(
                    url=self._post_asset_url,
                    cookies=self._cookies,
                    data={
                        "user_id": user.id,
                        "figi": i.figi,
                        "name": i.name,
                        "instrument_type_id": self._instrument_dict[i.asset_type],
                        "price": i.price,
                        "count": i.count,
                        "date": datetime.now(),
                    },
                ) as result:
                    if result.status != 201:
                        raise PostAsset("status code : ", result.status)


async def main():
    urls = Urls(
        authorization_url="http://31.129.105.185/auth/jwt/login",
        get_tokens_url="http://31.129.105.185/user/users",
        post_asset_url="http://31.129.105.185",
        post_operation_url="http://31.129.105.185",
        get_instrument_list="http://31.129.105.185/user/instrument-list",
    )
    super_user = SuperUser(email="test@test.com", password="test51445")
    bip = AsyncRecorder(urls=urls, super_user=super_user)
    await asyncio.create_task(bip.authorization())
    await asyncio.create_task(bip.get_tokens())
    await 


if __name__ == "__main__":
    asyncio.run(main=main())
