import json

import jsonpickle

from .db_models import CustomLayers as CustomLayersTable
from .db_engine import database
from ..api.schemas import TokenData, CustomLayer

async def create(payload: CustomLayer, user:TokenData):

    query = CustomLayersTable.insert().values(geojson=payload.layer.json(), user_id=user["user_id"], is_public=payload.is_public)
    return await database.execute(query=query)


async def get_one(id: int):
    query = CustomLayersTable.select().where(id == CustomLayersTable.c.id)
    return await database.fetch_one(query=query)