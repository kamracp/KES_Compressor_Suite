from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_query_all_standards_rules() -> None:
    response = client.post(
        "/api/v1/compressed-air/standards/query",
        json={},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["summary"]["total_rules"] == 4
    assert data["summary"]["verified_rules"] == 0
    assert data["summary"]["implemented_rules"] == 0
    assert data["summary"]["validated_rules"] == 0
    assert data["summary"]["compliance_claimable_rules"] == 0

    assert data["rules"]
    assert data["bindings"]

    assert data["formal_compliance_claim_available"] is False


def test_filter_rules_by_standard() -> None:
    response = client.post(
        "/api/v1/compressed-air/standards/query",
        json={
            "standard": "API_618",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["rules"]) == 1

    rule = data["rules"][0]

    assert rule["standard_code"] == "API_618"
    assert rule["rule_code"] == "API618-RECIPROCATING-DESIGN-REVIEW"


def test_filter_rules_by_application_type() -> None:
    response = client.post(
        "/api/v1/compressed-air/standards/query",
        json={
            "application_type": "FACTORY_COMPRESSED_AIR",
        },
    )

    assert response.status_code == 200

    data = response.json()

    standards = {item["standard_code"] for item in data["rules"]}

    assert "ASME_PTC_10" in standards
    assert "API_617" not in standards
    assert "API_618" not in standards


def test_filter_rules_by_module() -> None:
    response = client.post(
        "/api/v1/compressed-air/standards/query",
        json={
            "module": "ROD_LOAD",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["rules"]) == 1
    assert data["rules"][0]["standard_code"] == "API_618"

    assert all(
        item["module_code"] == "ROD_LOAD"
        or item["rule_code"] == "API618-RECIPROCATING-DESIGN-REVIEW"
        for item in data["bindings"]
    )


def test_combined_filters_are_applied() -> None:
    response = client.post(
        "/api/v1/compressed-air/standards/query",
        json={
            "application_type": "CENTRIFUGAL_PROCESS_COMPRESSOR",
            "standard": "API_617",
            "module": "SURGE_ANALYSIS",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["rules"]) == 1
    assert data["rules"][0]["standard_code"] == "API_617"


def test_unmatched_filter_returns_empty_rule_list() -> None:
    response = client.post(
        "/api/v1/compressed-air/standards/query",
        json={
            "application_type": "FACTORY_COMPRESSED_AIR",
            "standard": "API_618",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["rules"] == []
    assert data["bindings"] == []


def test_rule_metadata_preserves_unverified_status() -> None:
    response = client.post(
        "/api/v1/compressed-air/standards/query",
        json={
            "standard": "API_617",
        },
    )

    assert response.status_code == 200

    rule = response.json()["rules"][0]

    assert rule["clause_reference"] is None
    assert rule["verification_status"] == "UNVERIFIED"
    assert rule["implementation_status"] == "NOT_IMPLEMENTED"
    assert rule["calculation_binding"] is None
    assert rule["compliance_claim_allowed"] is False


def test_bindings_are_not_executable_yet() -> None:
    response = client.post(
        "/api/v1/compressed-air/standards/query",
        json={},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["summary"]["executable_bindings"] == 0

    assert all(item["executable"] is False for item in data["bindings"])


def test_formal_compliance_claim_is_never_inferred() -> None:
    response = client.post(
        "/api/v1/compressed-air/standards/query",
        json={
            "application_type": "RECIPROCATING_PROCESS_COMPRESSOR",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["formal_compliance_claim_available"] is False

    assert all(item["compliance_claim_allowed"] is False for item in data["rules"])


def test_invalid_standard_returns_422() -> None:
    response = client.post(
        "/api/v1/compressed-air/standards/query",
        json={
            "standard": "UNKNOWN_STANDARD",
        },
    )

    assert response.status_code == 422


def test_invalid_module_returns_422() -> None:
    response = client.post(
        "/api/v1/compressed-air/standards/query",
        json={
            "module": "UNKNOWN_MODULE",
        },
    )

    assert response.status_code == 422
