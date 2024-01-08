from pydantic import BaseModel, Field
from datetime import datetime


class RequestOperation(BaseModel):
    buy: bool
    price: float = Field(gt=0, lt=1000000)
    figi: str = Field(max_length=50)
    count: int = Field(gt=0, le=10000000)
    date: datetime
    justification: str | None = ""
    expectations: str | None = ""


class RequestOperationSuper(RequestOperation):
    user_id: int = Field(gt=0, lt=10000000)


class ResponseOperation(RequestOperation):
    id: int = Field(gt=0, lt=100000000)
