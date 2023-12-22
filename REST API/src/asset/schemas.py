from pydantic import BaseModel
from datetime import datetime


class RequestAsset(BaseModel):
    date: datetime
    figi: str
    instrument_type_id: int
    name: str
    price: float
    count: int


class ResponseAsset(RequestAsset):
    id: int


class RequestAssetSuper(RequestAsset):
    user_id: int
