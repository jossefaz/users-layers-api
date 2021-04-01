import json

import pytest
from fastapi import status
from starlette.testclient import TestClient

from ..app.api.schemas import CustomLayer, TokenData
from ..app.utils import token
from ..app.db import customlayers as customlayers_repository

VALID_PAYLOAD = {
    "is_public": False,
    "layer": {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "coordinates": [
                        15, 15
                    ],
                    "type": "Point"
                },
                "properties": {},
                "id": "string",
                "bbox": None
            }
        ],
        "bbox": None
    }
}

INVALID_PAYLOAD_GEOJSON_COORDINATE = {
    "is_public": False,
    "layer": {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point"
                },
                "properties": {},
                "id": "string"
            }
        ]
    }
}

INVALID_PAYLOAD_GEOJSON_GEOM_TYPE = {
    "is_public": False,
    "layer": {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "coordinates": [
                        15, 15
                    ],
                    "type": "point"
                },
                "properties": {},
                "id": "string"
            }
        ]
    }
}


@pytest.mark.parametrize(
    "customlayer_payload, tokendata, expected_status_code",
    [
        [VALID_PAYLOAD, {"username": "john", "id": 1}, status.HTTP_201_CREATED],
        [VALID_PAYLOAD, False, status.HTTP_401_UNAUTHORIZED],
        [INVALID_PAYLOAD_GEOJSON_GEOM_TYPE, {"username": "john", "id": 1},
         status.HTTP_422_UNPROCESSABLE_ENTITY],
        [INVALID_PAYLOAD_GEOJSON_COORDINATE, {"username": "john", "id": 1},
         status.HTTP_422_UNPROCESSABLE_ENTITY],
    ]
)
def test_create_layer(test_app: TestClient, monkeypatch, customlayer_payload, tokendata, expected_status_code):
    async def mock_check_credentials(token: str):
        return tokendata

    async def mock_create(payload: CustomLayer, user: TokenData):
        return 1

    async def mock_get_one(id: int):
        return {"geojson": json.dumps(customlayer_payload["layer"])}

    test_app.headers["access-token"] = "some-dummy-token"
    monkeypatch.setattr(token, "check_user_credentials", mock_check_credentials)
    monkeypatch.setattr(customlayers_repository, "create", mock_create)
    monkeypatch.setattr(customlayers_repository, "get_one", mock_get_one)

    response = test_app.post("/layers/", data=json.dumps(customlayer_payload))

    assert response.status_code == expected_status_code
    if response.status_code == status.HTTP_201_CREATED:
        assert response.json() == customlayer_payload["layer"]
