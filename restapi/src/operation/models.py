from datetime import datetime
from database import metadata
from sqlalchemy import (
    MetaData,
    Table,
    String,
    Integer,
    Column,
    DateTime,
    Boolean,
    Float,
    ForeignKey,
)


operation = Table(
    "operation",
    metadata,
    Column("id", Integer(), primary_key=True),
    Column("user_id", Integer(), ForeignKey("user.id")),
    Column("figi", String(50), nullable=False),
    Column("buy", Boolean(), nullable=False),
    Column("price", Float(), nullable=False),
    Column("date", DateTime(), default=datetime.utcnow),
    Column("count", Integer(), nullable=False),
    Column("justification", String(), nullable=True),
    Column("expectations", String(), nullable=True),
)
