from datetime import datetime
from database import metadata
from sqlalchemy import (
    Table,
    String,
    Integer,
    Column,
    DateTime,
    Float,
    ForeignKey,
)


asset = Table(
    "asset",
    metadata,
    Column("id", Integer(), primary_key=True),
    Column("user_id", Integer(), ForeignKey("user.id")),
    Column(
        "instrument_id",
        Integer(),
        ForeignKey("instrument.id"),
        nullable=False,
    ),
    Column("name", String(length=50), nullable=False),
    Column("figi", String(length=50), nullable=False),
    Column("price", Float(), nullable=False),
    Column("date", DateTime(), default=datetime.utcnow),
    Column("count", Integer(), nullable=False),
)
