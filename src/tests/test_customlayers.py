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

VALID_PUBLIC_LAYER = {
    "user_id": 1,
    "is_public": True,
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

VALID_PRIVATE_LAYER = {
    "user_id": 1,
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
    "customlayer_payload, token_data, expected_status_code",
    [
        [VALID_PAYLOAD, {"username": "john", "user_id": 1}, status.HTTP_201_CREATED],
        [VALID_PAYLOAD, False, status.HTTP_401_UNAUTHORIZED],
        [INVALID_PAYLOAD_GEOJSON_GEOM_TYPE, {"username": "john", "user_id": 1},
         status.HTTP_422_UNPROCESSABLE_ENTITY],
        [INVALID_PAYLOAD_GEOJSON_COORDINATE, {"username": "john", "user_id": 1},
         status.HTTP_422_UNPROCESSABLE_ENTITY],
    ]
)
def test_create_layer(test_app: TestClient, monkeypatch, customlayer_payload, token_data, expected_status_code):
    async def mock_check_credentials(token: str):
        return token_data

    async def mock_create(payload: CustomLayer, user: token_data):
        return 1

    async def mock_get_one(id: int):
        return {"id": 1, "geojson": json.dumps(customlayer_payload["layer"])}

    test_app.headers["access-token"] = "some-dummy-token"
    monkeypatch.setattr(token, "check_user_credentials", mock_check_credentials)
    monkeypatch.setattr(customlayers_repository, "create", mock_create)
    monkeypatch.setattr(customlayers_repository, "get_one", mock_get_one)

    response = test_app.post("/layers/", data=json.dumps(customlayer_payload))

    assert response.status_code == expected_status_code
    if response.status_code == status.HTTP_200_OK:
        assert response.json() == {"id": 1, "status": "created"}


@pytest.mark.parametrize(
    "retrieved_layer, token_data, expected_status_code",
    [
        [VALID_PUBLIC_LAYER, None, status.HTTP_200_OK],
        [VALID_PRIVATE_LAYER, {"username": "john", "user_id": 1}, status.HTTP_200_OK],
        [VALID_PRIVATE_LAYER, {"username": "notjohn", "user_id": 2}, status.HTTP_401_UNAUTHORIZED],
        [None, None, status.HTTP_401_UNAUTHORIZED],
        [None, {"username": "john", "user_id": 1}, status.HTTP_404_NOT_FOUND],
    ]
)
def test_retrieve_layer(test_app: TestClient, monkeypatch, retrieved_layer, token_data, expected_status_code):
    async def mock_check_credentials(token: str):
        return token_data

    async def mock_get_one(id: int):
        if retrieved_layer:
            return {"is_public": retrieved_layer["is_public"], "user_id": retrieved_layer["user_id"],
                    "geojson": json.dumps(retrieved_layer["layer"])}
        return None

    test_app.headers["access-token"] = "some-dummy-token"
    monkeypatch.setattr(token, "check_user_credentials", mock_check_credentials)
    monkeypatch.setattr(customlayers_repository, "get_one", mock_get_one)

    response = test_app.get("/layers/1")

    assert response.status_code == expected_status_code


@pytest.mark.parametrize(
    "customlayer_payload, token_data, expected_status_code",
    [
        [VALID_PAYLOAD, {"username": "john", "id": 1}, status.HTTP_204_NO_CONTENT],
        [VALID_PAYLOAD, False, status.HTTP_401_UNAUTHORIZED],
        [INVALID_PAYLOAD_GEOJSON_GEOM_TYPE, {"username": "john", "user_id": 1},
         status.HTTP_422_UNPROCESSABLE_ENTITY],
        [INVALID_PAYLOAD_GEOJSON_COORDINATE, {"username": "john", "user_id": 1},
         status.HTTP_422_UNPROCESSABLE_ENTITY],
    ]
)
def test_update_layer(test_app: TestClient, monkeypatch, customlayer_payload, token_data, expected_status_code):
    async def mock_check_credentials(token: str):
        return token_data

    async def mock_get_one(id: int):
        return {"id": 1, "user_id": 1, "geojson": json.dumps(customlayer_payload["layer"])}

    async def mock_update(payload, layer_id):
        return 1

    test_app.headers["access-token"] = "some-dummy-token"
    monkeypatch.setattr(token, "check_user_credentials", mock_check_credentials)
    monkeypatch.setattr(customlayers_repository, "update", mock_update)
    monkeypatch.setattr(customlayers_repository, "get_one", mock_get_one)

    response = test_app.put("/layers/1", data=json.dumps(customlayer_payload))

    assert response.status_code == expected_status_code
    
@pytest.mark.parametrize(
    "retrieved_custom_layer, token_data, expected_status_code",
    [
        [VALID_PUBLIC_LAYER, {"username": "john", "user_id": 1}, status.HTTP_204_NO_CONTENT],
        [None, {"username": "john", "user_id": 1}, status.HTTP_404_NOT_FOUND],
        [None, None, status.HTTP_401_UNAUTHORIZED]
    ]
)
def test_delete_layer(test_app:TestClient, monkeypatch, retrieved_custom_layer, token_data, expected_status_code):
    async def mock_check_credentials(token: str):
        return token_data

    async def mock_get_one(id: int):
        return retrieved_custom_layer

    async def mock_delete(payload, layer_id):
        return 1

    test_app.headers["access-token"] = "some-dummy-token"
    monkeypatch.setattr(token, "check_user_credentials", mock_check_credentials)
    monkeypatch.setattr(customlayers_repository, "update", mock_delete)
    monkeypatch.setattr(customlayers_repository, "get_one", mock_get_one)
    response = test_app.delete("/layers/1")
    assert response.status_code == expected_status_code


