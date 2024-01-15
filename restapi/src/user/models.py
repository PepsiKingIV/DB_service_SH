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

instrument = Table(
    "instrument",
    metadata,
    Column("id", Integer(), primary_key=True),
    Column("type_name", String(), nullable=False),
    extend_existing=True,
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
        "instrument",
        Integer(),
        ForeignKey("instrument.id"),
        nullable=False,
    ),
    extend_existing=True,
)
