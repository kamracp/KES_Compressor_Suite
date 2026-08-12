from fastapi.testclient import TestClient

from app.main import app
from tests.helpers.api_tenant_auth import prepare_authenticated_tenant

client = TestClient(app)


def test_calculate_gas_properties() -> None:
    _, _, headers = prepare_authenticated_tenant(client)

    response = client.post(
        "/api/v1/compressor/gas-properties/calculate",
        headers=headers,
        json={
            "components": [
                {
                    "component": "methane",
                    "mole_fraction": "0.90",
                },
                {
                    "component": "ethane",
                    "mole_fraction": "0.05",
                },
                {
                    "component": "nitrogen",
                    "mole_fraction": "0.03",
                },
                {
                    "component": "carbon_dioxide",
                    "mole_fraction": "0.02",
                },
            ],
            "pressure_bar": "10",
            "temperature_k": "300",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert float(data["molecular_weight_kg_per_kmol"]) > 0
    assert float(data["specific_gravity_air_1"]) > 0
    assert float(data["pseudocritical_temperature_k"]) > 0
    assert float(data["pseudocritical_pressure_bar"]) > 0
    assert float(data["reduced_temperature"]) > 0
    assert float(data["reduced_pressure"]) > 0
    assert float(data["z_factor"]) > 0
    assert data["z_factor_correlation"] == "Papay"
    assert float(data["density_kg_per_m3"]) > 0


def test_gas_properties_requires_authentication() -> None:
    response = client.post(
        "/api/v1/compressor/gas-properties/calculate",
        json={
            "components": [
                {
                    "component": "methane",
                    "mole_fraction": "1.0",
                }
            ],
            "pressure_bar": "10",
            "temperature_k": "300",
        },
    )

    assert response.status_code == 401


def test_invalid_mole_fraction_total_returns_422() -> None:
    _, _, headers = prepare_authenticated_tenant(client)

    response = client.post(
        "/api/v1/compressor/gas-properties/calculate",
        headers=headers,
        json={
            "components": [
                {
                    "component": "methane",
                    "mole_fraction": "0.8",
                },
                {
                    "component": "ethane",
                    "mole_fraction": "0.1",
                },
            ],
            "pressure_bar": "10",
            "temperature_k": "300",
        },
    )

    assert response.status_code == 422
