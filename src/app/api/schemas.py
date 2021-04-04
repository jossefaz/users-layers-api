from typing import Optional
from geojson_pydantic.features import FeatureCollection

from pydantic import BaseModel, Field


class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int]


class CustomLayer(BaseModel):
    is_public: Optional[bool] = False
    layer_name: str
    layer: FeatureCollection


class CustomLayerResponse(BaseModel):
    is_public: bool
    layer_name: str
    user_id: int
    id: int
