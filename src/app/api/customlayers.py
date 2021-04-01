import os
from typing import List, Optional



from ..db import customlayers as customlayers_repository
from geojson_pydantic.features import FeatureCollection
from fastapi import APIRouter, HTTPException, status, Header, Response
from .schemas import CustomLayer
from ..utils.Exceptions import raise_401_exception, raise_404_exception
from ..utils import token

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_item(payload: CustomLayer, access_token: Optional[str] = Header(None)):
    if not access_token:
        raise_401_exception()
    user = await token.check_user_credentials(access_token)
    if not user:
        raise_401_exception()
    layer_id = await customlayers_repository.create(payload, user)
    layer_record = await customlayers_repository.get_one(layer_id)
    if not layer_record:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Problem occured during item creation")
    return {"id": layer_record.get("id"), "status": "created"}


@router.get("/{layer_id}", response_model=FeatureCollection, status_code=status.HTTP_200_OK)
async def get_item(layer_id:int, access_token: Optional[str] = Header(None)):
    layer_record = await customlayers_repository.get_one(layer_id)
    if not layer_record:
        raise_404_exception()
    if layer_record.get("is_public"):
        return FeatureCollection.parse_raw(layer_record.get("geojson"))
    if not access_token:
        raise_401_exception()
    user = await token.check_user_credentials(access_token)
    if not user:
        raise_401_exception()
    if user["user_id"] != layer_record.get("user_id"):
        raise_401_exception()
    return FeatureCollection.parse_raw(layer_record.get("geojson"))

@router.put("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def create_item(id:int, payload: CustomLayer, access_token: Optional[str] = Header(None)):
    if not access_token:
        raise_401_exception()
    user = await token.check_user_credentials(access_token)
    if not user:
        raise_401_exception()
    layer_id = await customlayers_repository.update(id, payload)
    print("layer id is: " , layer_id)
    layer_record = await customlayers_repository.get_one(id)
    if not layer_record:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Problem occured during item creation")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

