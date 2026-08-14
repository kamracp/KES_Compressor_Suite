from decimal import Decimal

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

ENDPOINT = "/api/v1/compressed-air/performance/analyze"


def as_decimal(value: object) -> Decimal:
    return Decimal(str(value))


def performance_payload() -> dict[str, object]:
    return {
        "analysis_code": "PERF-001",
        "measurements": [
            {
                "timestamp_label": "T1",
                "flow_nm3_per_hr": "600",
                "pressure_bar_g": "7.0",
                "power_kw": "90",
                "operating_state": "LOADED",
                "load_fraction": "1.0",
            },
            {
                "timestamp_label": "T2",
                "flow_nm3_per_hr": "300",
                "pressure_bar_g": "6.5",
                "power_kw": "60",
                "operating_state": "PART_LOAD",
                "load_fraction": "0.5",
            },
            {
                "timestamp_label": "T3",
                "flow_nm3_per_hr": "0",
                "pressure_bar_g": "6.0",
                "power_kw": "30",
                "operating_state": "UNLOADED",
                "load_fraction": "0",
            },
        ],
        "annual_operating_hours": "8000",
        "electricity_tariff_per_kwh": "8",
        "rated_capacity_nm3_per_hr": "600",
        "rated_power_kw": "100",
        "reference_specific_power_kw_per_nm3_per_min": "10",
    }


def test_performance_analysis_returns_engineering_kpis() -> None:
    response = client.post(
        ENDPOINT,
        json=performance_payload(),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["analysis_code"] == "PERF-001"
    assert data["measurement_count"] == 3

    assert as_decimal(data["average_flow_nm3_per_hr"]) == Decimal("300")
    assert as_decimal(data["peak_flow_nm3_per_hr"]) == Decimal("600")
    assert as_decimal(data["minimum_flow_nm3_per_hr"]) == Decimal("0")

    assert as_decimal(data["average_pressure_bar_g"]) == Decimal("6.5")
    assert as_decimal(data["average_power_kw"]) == Decimal("60")
    assert as_decimal(data["peak_power_kw"]) == Decimal("90")

    assert as_decimal(data["measured_specific_power_kw_per_nm3_per_min"]) == Decimal("12")

    assert as_decimal(data["measured_specific_energy_kwh_per_1000_nm3"]) == Decimal("200")

    assert as_decimal(data["average_capacity_utilization_fraction"]) == Decimal("0.5")

    assert as_decimal(data["peak_capacity_utilization_fraction"]) == Decimal("1")

    assert as_decimal(data["average_power_utilization_fraction"]) == Decimal("0.6")

    assert as_decimal(data["specific_power_deviation_fraction"]) == Decimal("0.2")

    assert as_decimal(data["annual_energy_kwh"]) == Decimal("480000")
    assert as_decimal(data["annual_energy_cost"]) == Decimal("3840000")


def test_performance_analysis_returns_pressure_energy_scenario() -> None:
    payload = performance_payload()
    payload["optimized_discharge_pressure_bar_g"] = "6.0"

    response = client.post(
        ENDPOINT,
        json=payload,
    )

    assert response.status_code == 200

    pressure = response.json()["pressure_energy"]

    assert pressure is not None

    assert as_decimal(pressure["current_discharge_pressure_bar_g"]) == Decimal("6.5")

    assert as_decimal(pressure["optimized_discharge_pressure_bar_g"]) == Decimal("6.0")

    assert as_decimal(pressure["pressure_reduction_bar"]) == Decimal("0.5")

    assert as_decimal(pressure["estimated_power_saving_kw"]) == Decimal("2.1")

    assert as_decimal(pressure["estimated_optimized_power_kw"]) == Decimal("57.9")

    assert as_decimal(pressure["annual_energy_saving_kwh"]) == Decimal("16800")

    assert as_decimal(pressure["annual_cost_saving"]) == Decimal("134400")

    assert pressure["pressure_reduction_is_beneficial"] is True


def test_performance_analysis_rejects_blank_analysis_code() -> None:
    payload = performance_payload()
    payload["analysis_code"] = "   "

    response = client.post(
        ENDPOINT,
        json=payload,
    )

    assert response.status_code == 422


def test_performance_analysis_rejects_negative_measurement() -> None:
    payload = performance_payload()
    measurements = payload["measurements"]

    assert isinstance(measurements, list)

    measurements[0]["flow_nm3_per_hr"] = "-1"

    response = client.post(
        ENDPOINT,
        json=payload,
    )

    assert response.status_code == 422


def test_performance_route_is_registered_in_openapi() -> None:
    openapi_schema = app.openapi()

    assert ENDPOINT in openapi_schema["paths"]
    assert "post" in openapi_schema["paths"][ENDPOINT]
