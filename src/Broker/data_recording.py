import logging
from datetime import datetime, timedelta
from sqlalchemy import select, insert, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_async_session
from data_retriever import BrokerDataAdapterTinkoff
from operation.models import operation
from auth.models import User



logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler(f"data_recording.log", mode="w")
formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.info(f"Logger for data_rocorder. Start:{datetime.now()}")


def process(
    user: User,
    frequency: timedelta,
    session: AsyncSession = get_async_session(),
):
    query = select(user.tinkoff_invest_token)
    result = session.execute(query)
    # accounts = list(result.all())
    accounts = [
        "t.EcQ3vwja_ihQTb68vby2kptxblMAJRPcMxD1nJVgm55J28g0axeoSlycp1BI0pNLbYefhh-4GxTw6oGfGrvR6A"
    ]
    for i in accounts:
        for elem in BrokerDataAdapterTinkoff(i).get_operations(date_from=frequency):
            stmt = insert(operation).values(
                user_id=user.id,
                buy=elem.buy,
                price=elem.price,
                count=elem.count,
                date=elem.date,
            )
            session.execute(stmt)
            session.commit()


if __name__ == "__main__":
    process(User, frequency=timedelta(days=1))
