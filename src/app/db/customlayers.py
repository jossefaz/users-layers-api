from .db_models import CustomLayers as CustomLayersTable
from .db_engine import database
from ..api.schemas import TokenData, CustomLayer


async def create(payload: CustomLayer, user: TokenData):
    query = CustomLayersTable.insert().values(geojson=payload.layer.json(), user_id=user["user_id"],
                                              is_public=payload.is_public)
    return await database.execute(query=query)


async def update(layer_id: int, payload: CustomLayer):
    query = CustomLayersTable.update().where(layer_id == CustomLayersTable.c.id).values(geojson=payload.layer.json(),
                                                                                        is_public=payload.is_public)
    return await database.execute(query=query)


async def get_one(layer_id: int):
    query = CustomLayersTable.select().where(layer_id == CustomLayersTable.c.id)
    return await database.fetch_one(query=query)


async def delete(layer_id: int):
    query = CustomLayersTable.delete().where(layer_id == CustomLayersTable.c.id)
    return await database.execute(query=query)
