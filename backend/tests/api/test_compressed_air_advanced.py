from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_factory_air_advanced_assessment() -> None:
    response = client.post(
        "/api/v1/compressed-air/advanced/assess",
        json={
            "application_type": "FACTORY_COMPRESSED_AIR",
            "standards_review_required": False,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["application_type"] == "FACTORY_COMPRESSED_AIR"
    assert data["advanced_engineering_required"] is True

    module_codes = {item["module_code"] for item in data["recommended_modules"]}

    assert "COMPRESSION_THERMODYNAMICS" in module_codes
    assert "DRIVER_AND_POWER" in module_codes

    assert "ASME_PTC_10" in data["applicable_standard_codes"]
    assert "API_617" not in data["applicable_standard_codes"]
    assert "API_618" not in data["applicable_standard_codes"]

    assert data["formal_compliance_claim_available"] is False


def test_high_pressure_reciprocating_assessment() -> None:
    response = client.post(
        "/api/v1/compressed-air/advanced/assess",
        json={
            "application_type": "RECIPROCATING_PROCESS_COMPRESSOR",
            "compressor_technology": "RECIPROCATING",
            "discharge_pressure_bar_g": "30",
            "process_gas_service": True,
            "high_pressure_service": True,
            "standards_review_required": True,
        },
    )

    assert response.status_code == 200

    data = response.json()

    module_codes = {item["module_code"] for item in data["recommended_modules"]}

    assert "GAS_PROPERTIES" in module_codes
    assert "COMPRESSION_THERMODYNAMICS" in module_codes
    assert "RECIPROCATING_ENGINEERING" in module_codes
    assert "ROD_LOAD" in module_codes
    assert "COOLING_AND_INTERCOOLING" in module_codes
    assert "DRIVER_AND_POWER" in module_codes
    assert "STANDARDS_COMPLIANCE" in module_codes

    assert "API_618" in data["applicable_standard_codes"]
    assert "ASME_PTC_10" in data["applicable_standard_codes"]
    assert "GPSA_ENGINEERING_DATA_BOOK" in data["applicable_standard_codes"]

    assert data["standards_review_required"] is True
    assert data["formal_compliance_claim_available"] is False


def test_centrifugal_assessment_routes_map_and_surge() -> None:
    response = client.post(
        "/api/v1/compressed-air/advanced/assess",
        json={
            "application_type": "CENTRIFUGAL_PROCESS_COMPRESSOR",
            "compressor_technology": "CENTRIFUGAL",
            "process_gas_service": True,
        },
    )

    assert response.status_code == 200

    data = response.json()

    module_codes = {item["module_code"] for item in data["recommended_modules"]}

    assert "CENTRIFUGAL_ENGINEERING" in module_codes
    assert "PERFORMANCE_MAP" in module_codes
    assert "SURGE_ANALYSIS" in module_codes

    assert "API_617" in data["applicable_standard_codes"]
    assert "ASME_PTC_10" in data["applicable_standard_codes"]
    assert "GPSA_ENGINEERING_DATA_BOOK" in data["applicable_standard_codes"]

    assert "API_618" not in data["applicable_standard_codes"]


def test_factory_air_reciprocating_can_trigger_api_618_review() -> None:
    response = client.post(
        "/api/v1/compressed-air/advanced/assess",
        json={
            "application_type": "FACTORY_COMPRESSED_AIR",
            "compressor_technology": "RECIPROCATING",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "API_618" in data["review_required_standard_codes"]


def test_standard_assessments_do_not_claim_clause_compliance() -> None:
    response = client.post(
        "/api/v1/compressed-air/advanced/assess",
        json={
            "application_type": "CENTRIFUGAL_PROCESS_COMPRESSOR",
            "compressor_technology": "CENTRIFUGAL",
            "standards_review_required": True,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["standard_assessments"]

    assert all(item["clause_rules_implemented"] is False for item in data["standard_assessments"])

    assert all(
        item["formal_compliance_claim_allowed"] is False for item in data["standard_assessments"]
    )


def test_negative_discharge_pressure_returns_422() -> None:
    response = client.post(
        "/api/v1/compressed-air/advanced/assess",
        json={
            "application_type": "HIGH_PRESSURE_AIR",
            "discharge_pressure_bar_g": "-1",
        },
    )

    assert response.status_code == 422


def test_invalid_application_type_returns_422() -> None:
    response = client.post(
        "/api/v1/compressed-air/advanced/assess",
        json={
            "application_type": "UNKNOWN_APPLICATION",
        },
    )

    assert response.status_code == 422
