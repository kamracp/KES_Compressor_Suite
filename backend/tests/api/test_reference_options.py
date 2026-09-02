from decimal import Decimal

from fastapi.testclient import TestClient

from app.main import app
from app.schemas._bounds import SELECTABLE_ELECTRICITY_TARIFFS_INR_PER_KWH
from tests.helpers.api_tenant_auth import prepare_authenticated_tenant

client = TestClient(app)

URL = "/api/v1/reference/input-options"


def test_input_options_contract() -> None:
    _, _, headers = prepare_authenticated_tenant(client)
    response = client.get(URL, headers=headers)
    assert response.status_code == 200
    data = response.json()

    tariffs = data["electricity_tariff_inr_per_kwh"]
    assert len(tariffs) == 21
    assert tariffs[0] == "5" and tariffs[1] == "6" and tariffs[-1] == "25"
    assert [Decimal(t) for t in tariffs] == list(SELECTABLE_ELECTRICITY_TARIFFS_INR_PER_KWH)

    assert data["supply_phase"] == ["single", "three"]
    assert data["nominal_supply_voltage_v"] == [240, 415, 3300, 6600, 11000]
    assert data["supply_frequency_hz"] == [50, 60]


def test_input_options_requires_authentication() -> None:
    response = client.get(URL)
    assert response.status_code == 401
