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

asset_ratio = Table(
    "asset_ratio",
    metadata,
    Column("id", Integer(), primary_key=True),
    Column("user_id", Integer(), ForeignKey("user.id"), nullable=False),
    Column("ratio", Float(), nullable=False),
    Column("name", String(50), nullable=True),
    Column("figi", String(50), nullable=True),
    Column(
        "instrument_type_id",
        Integer(),
        ForeignKey("instrument_types.id"),
        nullable=False,
    ),
)
