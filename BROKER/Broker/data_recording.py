import logging
from datetime import datetime, timedelta
from Broker.data_retriever import BrokerDataAdapterTinkoff
import asyncio
from Broker.schemas import RequestOperationSuper, UsersAsset
import requests

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler(f"data_recording.log", mode="w")
formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.info(f"Logger for data_rocorder. Start:{datetime.now()}")


class Recorder:
    def __init__(self, url, email, password) -> None:
        self.url = url
        self.email = email
        self.password = password

    async def login(self) -> int:
        data = {"username": self.email, "password": self.password}
        request = await requests.post(f"{self.url}/auth/jwt/login", data=data)
        if request.status_code == 200:
            cookies = request.cookies.get_dict()["operations"]
            self.cookies = {"operations": cookies}
            await logger.info("OperationRecorder has been successfully logged in")
            return 0
        else:
            await logger.error(
                request.status_code,
                "|\t",
                request.content,
                "|\t",
                "OperationRecorder couldn't log in",
            )
            return 1

    async def receiving_and_recording_operation_data(
        self,
        token: str,
        user_id: int,
        date_from: datetime | None = datetime.now() - timedelta(days=120),
        date_to: datetime | None = datetime.now(),
    ):
        operations = await BrokerDataAdapterTinkoff(token).get_operations(
            date_from=date_from, date_to=date_to
        )
        for i in operations:
            request = await requests.post(
                f"{self.url}/operation/post_super",
                data=RequestOperationSuper(
                    user_id=user_id,
                    buy=i.buy,
                    price=i.price,
                    figi=i.figi,
                    count=i.count,
                    date=i.date,
                ),
                cookies=self.cookies,
            )
            if request.status_code != 201:
                await logger.error(user_id, i, "the operation was not recorded")
                # TODO: придумать, куда класть незаписанные данные, чтобы позже их обработать

    async def receiving_and_recording_asset_data(
        self,
        token: str,
        user_id: int,
    ):
        assets = await BrokerDataAdapterTinkoff(token).get_assets()
        for i in assets:
            request = await requests.post(
                url=f"{self.url}/asset/post",
                cookies=self.cookies,
                data=UsersAsset(
                    user_id=user_id,
                    figi=i.figi,
                    name=i.name,
                    asset_type=i.asset_type,
                    price=i.price,
                    count=i.count,
                ),
            )
            if request.status_code != 201:
                await logger.error(user_id, i, "the asset was not recorded")
                # TODO: придумать, куда класть незаписанные данные, чтобы позже их обработать
