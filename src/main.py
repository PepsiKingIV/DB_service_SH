from tinkoff.invest import Client, Operation, InstrumentIdType
from Broker.data_recording import process
from auth.models import User
from datetime import timedelta
from database import get_async_session, engine
import asyncio

TOKEN = "token"

# with Client(TOKEN) as client:
#     for i in client.users.get_accounts().accounts:
#         print(i.id)
#     data = client.operations.get_portfolio(account_id="2173418068")
#     # print(client.instruments.share_by(id_type=InstrumentIdType(1), id="BBG004731032").instrument.name)
#     # for i in data.positions:
#     #     print(
#     #         f"figi: {i.figi}\n\
#     #             quantity: {i.quantity_lots.units}\n\
#     #             current_price: {i.current_price.units+i.current_price.nano / (10**9)}"
#     #     )

asyncio.run(process(user=User, frequency=timedelta(minutes=60), engine=engine))