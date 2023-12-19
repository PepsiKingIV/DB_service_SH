import logging
from datetime import datetime, timedelta
from sqlalchemy import select, insert, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_async_session
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from .data_retriever import BrokerDataAdapterTinkoff
from operation.models import operation
from asset.models import asset
from auth.models import User
import asyncio

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler(f"data_recording.log", mode="w")
formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.info(f"Logger for data_rocorder. Start:{datetime.now()}")


async def process(
    user: User,
    frequency: timedelta,
    engine: AsyncEngine,
):
    async with engine.begin() as session:
        query = select(user.tinkoff_invest_token, user.id)
        result = await session.execute(query)
        accounts = list(result.all())
        await session.close()

        while True:
            if datetime.now().minute % 60 == 0:
                await operation_record(
                    engine=engine, accounts=accounts, frequency=frequency
                )
                if datetime.now().hour % 12 == 0:
                    await asset_record(engine=engine, accounts=accounts)
                await asyncio.sleep(61)

            if datetime.now().second % 5 == 0:
                print(f"processing... {datetime.now()}")
                await asyncio.sleep(1)


async def operation_record(
    engine: AsyncEngine,
    accounts: list,
    frequency: timedelta,
):
    async with engine.begin() as session:
        for i in accounts:
            try:
                operations = BrokerDataAdapterTinkoff(i[0]).get_operations(
                    date_from=datetime.now() - frequency, date_to=datetime.now()
                )
            except Exception as e:
                operations = []
                await logger.error("Recording operations", "\n", e)
            for elem in operations:
                stmt = insert(operation).values(
                    user_id=i[1],
                    buy=elem.buy,
                    price=elem.price,
                    count=elem.count,
                    date=elem.date.replace(tzinfo=None),
                )
                await session.execute(stmt)
        await session.commit()
        await session.close()
        await logger.info("The operations were recorded successfully")


async def asset_record(engine: AsyncEngine, accounts: list):
    async with engine.begin() as session:
        # TODO: написать нормальную реализацию, а не словарь
        types = {
            "share": 1,
            "bond": 2,
            "currency": 3,
            "etf": 4,
            "future": 5,
            "option": 6,
        }
        for i in accounts:
            try:
                assets = BrokerDataAdapterTinkoff(i[0]).get_assets()
            except Exception as e:
                assets = []
                await logger.error("Recording operations", "\n", e)
            for elem in assets:
                stmt = insert(asset).values(
                    user_id=i[1],
                    price=elem.price,
                    figi=elem.figi,
                    instrument_type=types[elem.asset_type],
                    count=elem.count,
                    date=datetime.now().replace(tzinfo=None),
                )
                await session.execute(stmt)
        await session.commit()
        await session.close()
        await logger.info("Data on open positions has been recorded successfully")


if __name__ == "__main__":
    process(User, frequency=timedelta(days=1))
