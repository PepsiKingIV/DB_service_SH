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


asset = Table(
    "asset",
    metadata,
    Column("id", Integer(), primary_key=True),
    Column("user_id", Integer(), ForeignKey("user.id")),
    Column(
        "instrument_type", Integer(), ForeignKey("instrument_types.id"), nullable=False
    ),
    Column("figi", String(length=50), nullable=False),
    Column("price", Float(), nullable=False),
    Column("date", DateTime(), default=datetime.utcnow),
    Column("count", Integer(), nullable=False),
)

instrument_types = Table(
    "instrument_types",
    metadata,
    Column("id", Integer(), primary_key=True),
    Column("type_name", String(), nullable=False),
)
