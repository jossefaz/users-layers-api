from typing import Optional
from geojson_pydantic.features import FeatureCollection

from pydantic import BaseModel


class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int]


class CustomLayer(BaseModel):
    is_public: Optional[bool] = False
    layer: FeatureCollection

