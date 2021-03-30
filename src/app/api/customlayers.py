import os
from typing import List, Optional

from ..db import customlayers as customlayers_repository
from geojson_pydantic.features import FeatureCollection
from fastapi import APIRouter, HTTPException, status, Security, Depends, Header
from .schemas import CustomLayer
from ..utils.Exceptions import raise_401_exception, raise_404_exception
from ..utils.token import check_user_credentials

router = APIRouter()


@router.post("/", response_model=FeatureCollection, status_code=status.HTTP_201_CREATED)
async def create_item(payload: CustomLayer, access_token: Optional[str] = Header(None)):
    if not access_token:
        raise_401_exception()
    user = await check_user_credentials(access_token)
    if not user:
        raise_401_exception()
    layer_id = await customlayers_repository.create(payload, user)
    layer = await customlayers_repository.get_one(layer_id)
    if not layer:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Problem occured during item creation")
    return layer.geojson


@router.get("/{user_id}/{layer_id}", response_model=FeatureCollection, status_code=status.HTTP_200_OK)
async def get_item(user_id: int, layer_id, access_token: Optional[str] = Header(None)):
    layer = customlayers_repository.get_one(layer_id)
    if not layer:
        raise_404_exception()
    if layer.is_public:
        return layer.geojson
    if not access_token:
        raise_401_exception()
    user = check_user_credentials(access_token)
    if not user:
        raise_401_exception()
    if user.id != user_id:
        raise_401_exception()
    return layer.geojson
