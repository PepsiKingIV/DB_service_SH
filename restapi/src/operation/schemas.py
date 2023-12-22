from pydantic import BaseModel
from datetime import datetime


class RequestOperation(BaseModel):
    buy: bool
    price: float
    figi: str
    count: int
    date: datetime
    justification: str | None = None
    expectations: str | None = None


class RequestOperationSuper(RequestOperation):
    user_id: int


class ResponseOperation(RequestOperation):
    id: int
