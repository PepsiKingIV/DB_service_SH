import abc
from datetime import datetime

from schemas import Operation, Assets_type, Asset, Payment_date


class IBrokerDataAdapter:
    broker_token: str

    @abc.abstractmethod
    def get_total_assets_cost(self) -> float:
        ...

    @abc.abstractmethod
    def get_asset_cost(self, figi: str, asset_type: Assets_type) -> float:
        ...

    @abc.abstractmethod
    def get_assets(self) -> list[Asset]:
        ...

    @abc.abstractmethod
    def get_operations(self, date_from: datetime, date_to: datetime) -> list[Operation]:
        ...

    @abc.abstractmethod
    def get_payment_date(
        self, date_from: datetime, date_to: datetime, figi: str
    ) -> Payment_date:
        ...
