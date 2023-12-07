import abc
from enum import Enum
from pydantic import BaseModel
from datetime import datetime
from tinkoff.invest import Client, InstrumentIdType, OperationState


class Assets_type(Enum):
    SHARE = 1
    BOND = 2
    FUTURE = 3
    CURRENCY = 4
    ETF = 5
    OPTION = 6


class Asset(BaseModel):
    figi: str
    name: str
    asset_type: Assets_type
    price: float
    count: int


class Operation(BaseModel):
    date: datetime
    count: int
    price: float
    buy: bool


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


# TODO написать реализацию класса


class BrokerDataAdapterTinkoff(IBrokerDataAdapter):
    def __init__(self, broker_token: str) -> None:
        self.broker_token = broker_token
        self.__enter__()
        self.id_list = [
            item.id
            for item in self.client.users.get_accounts().accounts
            if item.name != "Инвесткопилка"
        ]

    def __enter__(self):
        self.client = Client(self.broker_token).__enter__()

    def get_total_assets_cost(self) -> float:
        total_amount = 0
        for item in self.id_list:
            try:
                for elem in self.client.operations.get_portfolio(
                    account_id=item
                ).positions:
                    total_amount = (
                        total_amount
                        + (
                            elem.current_price.units
                            + elem.current_price.nano / (10**9)
                        )
                        * elem.quantity.units
                    )
            except:
                raise
        return total_amount

    def get_asset_cost(self, figi: str) -> float:
        try:
            asset = self.client.market_data.get_last_prices(figi=[figi]).last_prices[-1]
        except:
            raise
        return asset.price.units + asset.price.nano / (10**9)

    def get_assets(self) -> list[Asset]:
        assets = []
        assets_dict = {
            "share": self.client.instruments.share_by,
            "bond": self.client.instruments.bond_by,
            "currency": self.client.instruments.currency_by,
            "etf": self.client.instruments.etf_by,
            "future": self.client.instruments.future_by,
            "option": self.client.instruments.option_by,
        }
        for item in self.id_list:
            try:
                for elem in self.client.operations.get_portfolio(
                    account_id=item
                ).positions:
                    asset = assets_dict[elem.instrument_type](
                        id_type=InstrumentIdType(1), id=elem.figi
                    ).instrument
                    asset_price = self.get_asset_cost(elem.figi)
                    assets.append(
                        {
                            "figi": asset.figi,
                            "name": asset.name,
                            "asset_type": elem.instrument_type,
                            "price": asset_price,
                            "count": elem.quantity_lots.units,
                        }
                    )
            except:
                raise
        return assets

    def get_operations(
        self, date_from: datetime | None = None, date_to: datetime | None = None
    ) -> list[Operation]:
        operations = []
        for item in self.id_list:
            try:
                for elem in self.client.operations.get_operations(
                    account_id=item,
                    from_=date_from,
                    to=date_to,
                    state=OperationState(2),
                ).operations:
                    operations.append(
                        {
                            "date": elem.date,
                            "count": elem.quantity,
                            "price": elem.price.units + elem.price.nano / (10**9),
                            "buy": True if elem.operation_type == 15 else False,
                        }
                    )
            except:
                raise
        return operations

    def __exit__(self):
        Client(self.broker_token).__exit__()


if __name__ == "__main__":
    broker = BrokerDataAdapterTinkoff(
        broker_token="test_token"
    )
    # print(broker.get_total_assets_cost())
    # print(broker.get_asset_cost("BBG004731032"))
    # print(broker.get_assets())

    print(
        broker.get_operations(
            date_from=datetime.fromisoformat("2023-04-12"), date_to=datetime.now()
        )
    )
