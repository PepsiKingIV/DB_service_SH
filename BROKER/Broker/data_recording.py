from ast import literal_eval
import asyncio
import logging
import aiohttp
from datetime import datetime, timedelta
import json

from schemas import (
    SuperUser,
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
                date_from=datetime.now() - timedelta(hours=1), date_to=datetime.now()
            )
            print(operations_in_last_hour)
        except Exception as e:
            # raise PostOperation(e)
            pass
        async with aiohttp.ClientSession() as session:
            for i in operations_in_last_hour:
                data = {
                    "user_id": user.id,
                    "buy": i.buy,
                    "price": i.price,
                    "figi": i.figi,
                    "count": i.count,
                    "date": i.date.isoformat(),
                }
                print(data)
                async with session.post(
                    url=self._post_operation_url,
                    cookies=self._cookies,
                    json=json.loads(json.dumps(data)),
                ) as result:
                    if result.status != 202:
                        raise PostOperation("status code", result.status)

    async def set_assets(self, user: UsersToken):
        try:
            open_positions = BrokerDataAdapterTinkoff(
                user.tinkoff_invest_token
            ).get_assets()
        except Exception as e:
            # raise PostAsset(e)
            pass
        async with aiohttp.ClientSession() as session:
            for i in open_positions:
                data = {
                    "date": datetime.now().isoformat(),
                    "figi": i.figi,
                    "instrument_id": self._instrument_dict[i.asset_type],
                    "name": i.name,
                    "price": i.price,
                    "count": i.count,
                    "user_id": user.id,
                }
                print(self._instrument_dict)
                if data["name"] == "Российский рубль":
                    data["price"] = 1.0
                async with session.post(
                    url=self._post_asset_url,
                    json=json.loads(json.dumps(data)),
                    cookies=self._cookies,
                ) as result:
                    print(await result.content.read())
                    print(
                        {
                            "date": datetime.now().isoformat(),
                            "figi": i.figi,
                            "instrument_id": self._instrument_dict[i.asset_type],
                            "name": i.name,
                            "price": i.price,
                            "count": i.count,
                            "user_id": user.id,
                        }
                    )
                    if result.status != 201:
                        raise PostAsset("status code", result.status)


async def main():
    urls = Urls(
        authorization_url="http://31.129.105.185/auth/jwt/login",
        get_tokens_url="http://31.129.105.185/user/users",
        post_asset_url="http://31.129.105.185/asset/post-super",
        post_operation_url="http://31.129.105.185/operation/post-super",
        get_instrument_list="http://31.129.105.185/user/instrument-list",
    )
    super_user = SuperUser(email="test@test.com", password="test51445")
    bip = AsyncRecorder(urls=urls, super_user=super_user)
    while True:
        if datetime.now().minute == 0 and datetime.now().second == 1:
            print(datetime.now())
            await asyncio.create_task(bip.authorization())
            users = await asyncio.create_task(bip.get_tokens())
            asset_reqs = [bip.set_assets(i) for i in users]
            position_reqs = [bip.set_operation(i) for i in users]
            results1 = await asyncio.gather(*asset_reqs, return_exceptions=True)
            results2 = await asyncio.gather(*position_reqs, return_exceptions=True)
            exceptions1 = [res for res in results1 if isinstance(res, Exception)]
            exceptions2 = [res for res in results2 if isinstance(res, Exception)]
            successful_result1 = [
                res for res in results1 if not isinstance(res, Exception)
            ]
            successful_result2 = [
                res for res in results2 if not isinstance(res, Exception)
            ]
            print("exceptions1: \n", exceptions1)
            print("successful_result1: \n", successful_result1)
            print("exceptions2: \n", exceptions2)
            print("successful_result2: \n", successful_result2)


if __name__ == "__main__":
    try:
        asyncio.run(main=main())
    except Exception as e:
        print(e)
