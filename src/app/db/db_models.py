from sqlalchemy import MetaData, Table, Column, Integer, JSON, Boolean
from sqlalchemy.sql import expression

metadata = MetaData()

CustomLayers = Table(
    "custom_layers",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("data", JSON),
    Column("is_public", Boolean, default=expression.false()),
    Column("user_id", Integer),
)
