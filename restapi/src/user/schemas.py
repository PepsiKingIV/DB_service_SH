from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime


class ProfileResponse(BaseModel):
    username: str = Field(max_length=50)
    email: EmailStr

    @validator("email")
    def email_validation(cls, email):
        if len(email) > 50:
            raise ValueError("the email is too long")
        return email


class RatioRequest(BaseModel):
    instrument_id: int = Field(gt=0, lt=1000000)
    ratio: float = Field(gt=0, lt=1)
    name: str = Field(default=None, max_length=50)
    figi: str = Field(default=None, max_length=50)


class UsersTokens(BaseModel):
    id: int = Field(gt=0, lt=1000000)
    username: str = Field(max_length=50)
    tinkoff_invest_token: str = Field(default=None, max_length=200)


class Instruments(BaseModel):
    id: int = Field(lt=1000, gt=0)
    type_name: str = Field(max_length=50)


class Instrument_ratio(Instruments):
    ratio: float = Field(gt=0, lt=1)
