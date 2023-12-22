from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import create_engine
from sqlalchemy import (
    MetaData,
    Table,
    String,
    Integer,
    Column,
    DateTime,
    Boolean,
    Float,
    CheckConstraint,
    ForeignKey,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from database import metadata

Base = declarative_base()


class User(SQLAlchemyBaseUserTable[int], Base):
    id = Column(Integer(), primary_key=True)
    tinkoff_invest_token = Column(String(200), nullable=True)
    username = Column(String(50), nullable=True)
    email = Column(String(length=320), unique=True, index=True, nullable=False)
    hashed_password = Column(String(length=1024), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)


user = Table(
    "user",
    metadata,
    Column("id", Integer(), primary_key=True),
    Column("tinkoff_invest_token", String(length=200), nullable=True),
    Column("username", String(length=50), nullable=True),
    Column("email", String(length=320), unique=True, index=True, nullable=False),
    Column("hashed_password", String(length=1024), nullable=False),
    Column("is_active", Boolean(), default=True, nullable=False),
    Column("is_superuser", Boolean(), default=False, nullable=False),
    Column("is_verified", Boolean(), default=False, nullable=False),
)


