from typing import Annotated, Optional
from pydantic import BaseModel, Field, validator

from fastapi_users import schemas
from pydantic import EmailStr


class UserRead(schemas.BaseUser[int]):
    id: int
    email: EmailStr
    username: str
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False

    class Config:
        orm_mode = True


class UserCreate(schemas.BaseUserCreate):
    username: str = Field(max_length=50)
    tinkoff_invest_token: str = Field(max_length=200)
    email: EmailStr
    password: str
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False

    @validator("email")
    def email_validation(cls, email):
        if len(email) > 50:
            raise ValueError("the email is too long")
        return email


class UserUpdate(schemas.BaseUserUpdate):
    pass
