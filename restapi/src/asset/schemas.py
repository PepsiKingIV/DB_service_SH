from pydantic import BaseModel, Field
from datetime import datetime


class RequestAsset(BaseModel):
    date: datetime
    figi: str = Field(max_length=50)
    instrument_id: int = Field(gt=0, lt=2147483647)
    name: str = Field(max_length=50)
    price: float = Field(gt=0, lt=1000000)
    count: int = Field(gt=0, lt=100000000)


class ResponseAsset(RequestAsset):
    id: int = Field(gt=0)


class RequestAssetSuper(RequestAsset):
    user_id: int = Field(gt=0)
