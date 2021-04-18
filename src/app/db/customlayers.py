from .db_models import CustomLayers as CustomLayersTable
from .db_engine import database
from ..api.schemas import TokenData, CustomLayer
from ..utils.logs import log_sql_query


async def create(payload: CustomLayer, user: TokenData):
    query = CustomLayersTable.insert().values(data=payload.layer.json(), user_id=user["user_id"],
                                              is_public=payload.is_public,
                                              layer_name=payload.layer_name)
    return await database.execute(query=query)


async def update(layer_id: int, payload: CustomLayer):
    query = CustomLayersTable.update().where(layer_id == CustomLayersTable.c.id).values(data=payload.layer.json(),
                                                                                        is_public=payload.is_public,
                                                                                        layer_name=payload.layer_name)
    return await database.execute(query=query)


async def retrieve_by_user_id(user_id: int):
    query = CustomLayersTable.select().where(user_id == CustomLayersTable.c.user_id)
    layers_found = await database.fetch_all(query=query)
    log_sql_query(sql_query=query, record_num=len(layers_found))
    return layers_found


async def retrieve_all_public_layers():
    query = CustomLayersTable.select().where(CustomLayersTable.c.is_public == True)
    layers_found = await database.fetch_all(query=query)
    log_sql_query(sql_query=query, record_num=len(layers_found))
    return await layers_found


async def retrieve_by_id(layer_id: int):
    query = CustomLayersTable.select().where(layer_id == CustomLayersTable.c.id)
    layers_found = await database.fetch_all(query=query)
    log_sql_query(sql_query=query, record_num=len(layers_found))
    return layers_found[0] if len(layers_found) > 0 else None


async def delete(layer_id: int):
    query = CustomLayersTable.delete().where(layer_id == CustomLayersTable.c.id)
    log_sql_query(sql_query=query)
    return await database.execute(query=query)


async def delete_by_user_id(user_id: int):
    query = CustomLayersTable.delete().where(user_id == CustomLayersTable.c.user_id)

    return await database.execute(query=query)
