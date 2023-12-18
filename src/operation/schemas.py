from pydantic import BaseModel
from datetime import datetime


class RequestOperation(BaseModel):
    amount: float
    date: datetime
    priority: int | None


class OperationResponse(BaseModel):
    id: int
    user_id: int
    debit: bool
    amount: float
    date: datetime
    type_name: str
    priority: int | None


class DeletedOperation(BaseModel):
    id: int
    user_type_id: int
    debit: bool
    amount: float
    date: datetime
    type_id: int
    priority: int
