from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.core.database import SessionLocal
from app.main import app
from app.models.calculation_case import CalculationCase
from app.models.project import Project
from tests.helpers.api_tenant_auth import prepare_authenticated_tenant

client = TestClient(app)


def reset_data() -> None:
    with SessionLocal() as db:
        db.execute(delete(CalculationCase))
        db.execute(delete(Project))
        db.commit()


def prepare_context() -> dict[str, str]:
    _, _, headers = prepare_authenticated_tenant(client)
    return headers


def create_project(
    *,
    headers: dict[str, str],
) -> int:
    response = client.post(
        "/api/v1/projects",
        headers=headers,
        json={
            "project_code": "KESC-EXEC-API-001",
            "project_name": "Compressor Execution API Test",
        },
    )

    assert response.status_code == 201
    return response.json()["id"]


def build_selection_payload(
    *,
    persist_result: bool,
    project_id: int | None = None,
    calculation_code: str | None = None,
) -> dict:
    execution = {
        "persist_result": persist_result,
    }

    if project_id is not None:
        execution["project_id"] = project_id

    if calculation_code is not None:
        execution["calculation_code"] = calculation_code
        execution["title"] = "Compressor Selection Execution"

    return {
        "calculation": {
            "required_flow_m3_per_hr": "14143.4",
            "suction_pressure_bar": "30",
            "discharge_pressure_bar": "90",
            "required_turndown_fraction": "0.70",
            "continuous_operation": True,
            "gas_molecular_weight": "19.075",
            "estimated_operating_hours_per_year": "8400",
        },
        "execution": execution,
    }


def build_rotary_screw_payload(
    *,
    persist_result: bool,
    project_id: int | None = None,
    calculation_code: str | None = None,
) -> dict:
    execution = {
        "persist_result": persist_result,
    }

    if project_id is not None:
        execution["project_id"] = project_id

    if calculation_code is not None:
        execution["calculation_code"] = calculation_code
        execution["title"] = "Rotary Screw Execution"

    return {
        "calculation": {
            "inlet_pressure_bar_a": "1",
            "inlet_temperature_k": "300",
            "discharge_pressure_bar_g": "7",
            "rotational_speed_rpm": "3000",
            "oil_type": "OIL_INJECTED",
            "control_type": "FIXED_SPEED_LOAD_UNLOAD",
            "rated_fad_m3_per_min": "10",
            "package_input_power_kw": "60",
        },
        "execution": execution,
    }


def test_execute_selection_without_persistence() -> None:
    reset_data()
    headers = prepare_context()

    response = client.post(
        "/api/v1/compressor-execution/selection",
        headers=headers,
        json=build_selection_payload(
            persist_result=False,
        ),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["calculation_case_id"] is None
    assert data["result"]["recommended_type"] in {
        "RECIPROCATING",
        "CENTRIFUGAL",
        "ROTARY_SCREW",
    }


def test_execute_selection_with_persistence() -> None:
    reset_data()
    headers = prepare_context()

    project_id = create_project(
        headers=headers,
    )

    response = client.post(
        "/api/v1/compressor-execution/selection",
        headers=headers,
        json=build_selection_payload(
            persist_result=True,
            project_id=project_id,
            calculation_code="SEL-API-001",
        ),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["calculation_case_id"] is not None

    case_response = client.get(
        f"/api/v1/calculation-cases/{data['calculation_case_id']}",
        headers=headers,
    )

    assert case_response.status_code == 200

    stored = case_response.json()

    assert stored["project_id"] == project_id
    assert stored["calculation_code"] == "SEL-API-001"
    assert stored["calculation_type"] == "SELECTION"
    assert stored["status"] == "COMPLETED"


def test_duplicate_calculation_code_returns_conflict() -> None:
    reset_data()
    headers = prepare_context()

    project_id = create_project(
        headers=headers,
    )

    payload = build_selection_payload(
        persist_result=True,
        project_id=project_id,
        calculation_code="SEL-API-002",
    )

    first_response = client.post(
        "/api/v1/compressor-execution/selection",
        headers=headers,
        json=payload,
    )

    second_response = client.post(
        "/api/v1/compressor-execution/selection",
        headers=headers,
        json=payload,
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 409


def test_missing_project_returns_not_found() -> None:
    reset_data()
    headers = prepare_context()

    response = client.post(
        "/api/v1/compressor-execution/selection",
        headers=headers,
        json=build_selection_payload(
            persist_result=True,
            project_id=999999,
            calculation_code="SEL-API-003",
        ),
    )

    assert response.status_code == 404


def test_missing_persistence_metadata_returns_422() -> None:
    reset_data()
    headers = prepare_context()

    response = client.post(
        "/api/v1/compressor-execution/selection",
        headers=headers,
        json={
            "calculation": {
                "required_flow_m3_per_hr": "14143.4",
                "suction_pressure_bar": "30",
                "discharge_pressure_bar": "90",
                "required_turndown_fraction": "0.70",
                "continuous_operation": True,
                "gas_molecular_weight": "19.075",
                "estimated_operating_hours_per_year": "8400",
            },
            "execution": {
                "persist_result": True,
            },
        },
    )

    assert response.status_code == 422


def test_execute_rotary_screw_without_persistence() -> None:
    reset_data()
    headers = prepare_context()

    response = client.post(
        "/api/v1/compressor-execution/rotary-screw",
        headers=headers,
        json=build_rotary_screw_payload(
            persist_result=False,
        ),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["calculation_case_id"] is None
    assert Decimal(
        data["result"]["performance"]["specific_power_kw_per_m3_min"]
    ) == Decimal("6.000")


def test_execute_rotary_screw_with_persistence() -> None:
    reset_data()
    headers = prepare_context()

    project_id = create_project(
        headers=headers,
    )

    response = client.post(
        "/api/v1/compressor-execution/rotary-screw",
        headers=headers,
        json=build_rotary_screw_payload(
            persist_result=True,
            project_id=project_id,
            calculation_code="RS-API-001",
        ),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["calculation_case_id"] is not None

    case_response = client.get(
        f"/api/v1/calculation-cases/{data['calculation_case_id']}",
        headers=headers,
    )

    assert case_response.status_code == 200

    stored = case_response.json()

    assert stored["project_id"] == project_id
    assert stored["calculation_code"] == "RS-API-001"
    assert stored["calculation_type"] == "ROTARY_SCREW"
    assert stored["status"] == "COMPLETED"
