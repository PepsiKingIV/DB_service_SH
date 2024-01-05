from pydantic import BaseModel
from datetime import datetime


class ProfileResponse(BaseModel):
    username: str
    email: str


class RatioRequest(BaseModel):
    instrument_id: int
    ratio: float 
    name: str | None = None
    figi: str | None = None


class UsersTokens(BaseModel):
    id: int
    username: str
    tinkoff_invest_token: str | None = None


class Instruments(BaseModel):
    id: int
    type_name: str


class Instrument_ratio(Instruments):
    ratio: float
