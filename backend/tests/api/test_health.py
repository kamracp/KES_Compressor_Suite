from collections import Counter

from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "KES Compressor Engineering Suite",
    }


def test_root_endpoint() -> None:
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "KES Compressor Engineering Suite"
    assert data["version"] == "0.1.0"
    assert data["status"] == "running"


def test_version_endpoint() -> None:
    response = client.get("/api/v1/version")

    assert response.status_code == 200

    data = response.json()

    assert data["version"] == "0.1.0"
    assert data["environment"] == "development"


def test_api_route_signatures_are_unique() -> None:
    signatures = [
        (route.path, method)
        for route in app.routes
        if isinstance(route, APIRoute)
        for method in route.methods
    ]
    duplicate_signatures = {
        signature: count for signature, count in Counter(signatures).items() if count > 1
    }

    assert duplicate_signatures == {}


def test_openapi_operation_ids_are_unique() -> None:
    operation_ids = [
        operation["operationId"]
        for path_item in app.openapi()["paths"].values()
        for operation in path_item.values()
        if "operationId" in operation
    ]
    duplicate_operation_ids = {
        operation_id: count for operation_id, count in Counter(operation_ids).items() if count > 1
    }

    assert duplicate_operation_ids == {}
