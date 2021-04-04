from sqlalchemy import MetaData, Table, Column, Integer, JSON, Boolean, String, DateTime
from sqlalchemy.sql import expression, func

metadata = MetaData()

CustomLayers = Table(
    "custom_layers",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("data", JSON),
    Column("is_public", Boolean, default=expression.false()),
    Column("user_id", Integer),
    Column("layer_name", String(255)),
    Column("create_date", DateTime, default=func.now()),
    Column("update_date", DateTime, onupdate=func.now())
)

