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
