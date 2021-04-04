from typing import List, Optional

from ..db import customlayers as layers_repository
from geojson_pydantic.features import FeatureCollection
from fastapi import APIRouter, HTTPException, status, Header, Response, Path
from .schemas import CustomLayer, CustomLayerResponse
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
    layer_id = await layers_repository.create(payload, user)
    layer_record = await layers_repository.retrieve_by_id(layer_id)
    if not layer_record:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Problem occurred during item creation")
    return {"id": layer_record.get("id"), "status": "created"}


@router.get("/", response_model=List[CustomLayerResponse], status_code=status.HTTP_200_OK)
async def retrieve_by_user(user_id: Optional[int] = None, access_token: Optional[str] = Header(None)):
    if user_id is None:
        public_layer_records = await layers_repository.retrieve_all_public_layers()
        return public_layer_records
    if access_token is None:
        raise_401_exception()
    user = await token.check_user_credentials(access_token)
    if not user:
        raise_401_exception()
    layer_records = await layers_repository.retrieve_by_user_id(user_id)
    if not layer_records:
        raise_404_exception()
    return layer_records


@router.get("/{layer_id}", response_model=FeatureCollection, status_code=status.HTTP_200_OK)
async def retrieve_by_id(layer_id: int, access_token: Optional[str] = Header(None)):
    layer_record = await layers_repository.retrieve_by_id(layer_id)
    if layer_record and layer_record.get("is_public"):
        return FeatureCollection.parse_raw(layer_record.get("data"))
    if not access_token:
        raise_401_exception()
    user = await token.check_user_credentials(access_token)
    if not user:
        raise_401_exception()
    if not layer_record:
        raise_404_exception()
    if user["user_id"] != layer_record.get("user_id"):
        raise_401_exception()
    return FeatureCollection.parse_raw(layer_record.get("data"))


@router.put("/{layer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_layer(layer_id: int, payload: CustomLayer, access_token: Optional[str] = Header(None)):
    if not access_token:
        raise_401_exception()
    user = await token.check_user_credentials(access_token)
    if not user:
        raise_401_exception()
    layer_record = await layers_repository.retrieve_by_id(layer_id)
    if not layer_record:
        raise_404_exception()
    layer_id = await layers_repository.update(layer_id, payload)
    print("layer id is: ", layer_id)
    layer_record = await layers_repository.retrieve_by_id(layer_id)
    if not layer_record:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Problem occurred during item creation")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/{layer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_layer(layer_id: int, access_token: Optional[str] = Header(None)):
    if not access_token:
        raise_401_exception()
    user = await token.check_user_credentials(access_token)
    if not user:
        raise_401_exception()
    layer_record = await layers_repository.retrieve_by_id(layer_id)
    if not layer_record:
        raise_404_exception()
    if user["user_id"] != layer_record.get("user_id"):
        raise_401_exception()
    await layers_repository.delete(layer_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_layers_by_user(user_id: int, access_token: Optional[str] = Header(None)):
    if not access_token:
        raise_401_exception()
    user = await token.check_user_credentials(access_token)
    if not user or user["user_id"] != user_id:
        raise_401_exception()
    await layers_repository.delete_by_user_id(user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
