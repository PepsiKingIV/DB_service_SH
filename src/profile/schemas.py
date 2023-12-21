from pydantic import BaseModel
from datetime import datetime


class ProfileResponse(BaseModel):
    username: str
    email: str


class RatioRequest(BaseModel):
    instrument: str
    ratio: float
    