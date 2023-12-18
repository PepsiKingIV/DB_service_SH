from datetime import datetime
from src.database import metadata
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
    Column("price", Float(), nullable=False),
    Column("date", DateTime(), default=datetime.utcnow),
    Column("count", Integer(), nullable=False),
)
