from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def build_request() -> dict:
    return {
        "consumers": [
            {
                "consumer_code": "CNC-001",
                "name": "CNC Machine Group",
                "category": "PRODUCTION_MACHINE",
                "quantity": 10,
                "required_pressure_bar_g": "6.0",
                "air_quality_class": "GENERAL_PLANT_AIR",
                "consumption_basis": "FLOW_WHEN_OPERATING",
                "flow_per_unit_nm3_per_hr": "25",
                "duty_factor": "0.70",
                "simultaneity_factor": "0.80",
                "operating_hours_per_day": "16",
                "operating_days_per_year": "300",
                "criticality": "NORMAL",
                "area": "Machine Shop",
            },
            {
                "consumer_code": "IA-001",
                "name": "Instrument Air",
                "category": "INSTRUMENT_AIR",
                "quantity": 1,
                "required_pressure_bar_g": "6.5",
                "air_quality_class": "INSTRUMENT_AIR",
                "consumption_basis": "CONTINUOUS_FLOW",
                "flow_per_unit_nm3_per_hr": "120",
                "criticality": "CRITICAL",
            },
        ],
        "demand_profile_points": [
            {
                "period_index": 1,
                "label": "Low Demand",
                "demand_nm3_per_hr": "180",
                "required_pressure_bar_g": "6.5",
                "duration_hours": "8",
            },
            {
                "period_index": 2,
                "label": "Normal Demand",
                "demand_nm3_per_hr": "260",
                "required_pressure_bar_g": "6.5",
                "duration_hours": "8",
            },
            {
                "period_index": 3,
                "label": "Peak Demand",
                "demand_nm3_per_hr": "320",
                "required_pressure_bar_g": "6.5",
                "duration_hours": "8",
            },
        ],
        "leakage_fraction": "0.10",
        "future_expansion_fraction": "0.15",
        "other_allowance_fraction": "0",
        "minimum_point_of_use_pressure_bar_g": "6.0",
        "pressure_loss_components": [
            {
                "component_code": "DRYER",
                "name": "Dryer",
                "pressure_drop_bar": "0.15",
                "category": "TREATMENT",
            },
            {
                "component_code": "FILTER",
                "name": "Filters",
                "pressure_drop_bar": "0.10",
                "category": "TREATMENT",
            },
            {
                "component_code": "HEADER",
                "name": "Distribution Header",
                "pressure_drop_bar": "0.20",
                "category": "DISTRIBUTION",
            },
        ],
        "control_margin_bar": "0.20",
        "treatment": {
            "required_delivered_flow_nm3_per_hr": "350",
            "required_air_quality": "GENERAL_PLANT_AIR",
            "dryer_type": "REFRIGERATED",
            "dryer_correction_factor": "0.95",
            "dryer_purge_fraction": "0",
            "prefilter_pressure_drop_bar": "0",
            "afterfilter_pressure_drop_bar": "0",
            "dryer_pressure_drop_bar": "0",
            "treatment_capacity_margin_fraction": "0.10",
        },
        "station": {
            "station_code": "CAS-GF-001",
            "units": [
                {
                    "unit_code": "AC-01",
                    "technology": "ROTARY_SCREW_OIL_INJECTED",
                    "control_mode": "FIXED_SPEED",
                    "duty_role": "BASE_LOAD",
                    "rated_fad_nm3_per_hr": "250",
                    "minimum_stable_flow_fraction": "0.60",
                    "rated_discharge_pressure_bar_g": "7.0",
                    "rated_motor_power_kw": "45",
                    "available": True,
                },
                {
                    "unit_code": "AC-02",
                    "technology": "ROTARY_SCREW_OIL_INJECTED",
                    "control_mode": "VSD",
                    "duty_role": "TRIM",
                    "rated_fad_nm3_per_hr": "180",
                    "minimum_stable_flow_fraction": "0.20",
                    "rated_discharge_pressure_bar_g": "7.0",
                    "rated_motor_power_kw": "30",
                    "available": True,
                },
                {
                    "unit_code": "AC-03",
                    "technology": "ROTARY_SCREW_OIL_INJECTED",
                    "control_mode": "FIXED_SPEED",
                    "duty_role": "STANDBY",
                    "rated_fad_nm3_per_hr": "250",
                    "minimum_stable_flow_fraction": "0.60",
                    "rated_discharge_pressure_bar_g": "7.0",
                    "rated_motor_power_kw": "45",
                    "available": True,
                },
            ],
            "redundancy_philosophy": "N_PLUS_1",
            "minimum_required_pressure_bar_g": "6.9",
            "design_flow_nm3_per_hr": "350",
            "master_control_enabled": True,
        },
        "receiver": {
            "peak_demand_nm3_per_hr": "400",
            "available_compressor_flow_nm3_per_hr": "350",
            "event_duration_seconds": "30",
            "receiver_high_pressure_bar_g": "7.0",
            "receiver_low_pressure_bar_g": "6.5",
            "reserve_fraction": "0.20",
        },
        "specific_power_kw_per_nm3_per_min": "6.5",
        "annual_operating_days": "330",
        "electricity_tariff_per_kwh": "8",
    }


def test_greenfield_design_endpoint() -> None:
    response = client.post(
        "/api/v1/compressed-air/greenfield/design",
        json=build_request(),
    )

    assert response.status_code == 200

    data = response.json()

    assert float(data["required_design_flow_nm3_per_hr"]) > 0

    assert data["required_compressor_discharge_pressure_bar_g"] == "6.65"

    assert data["peak_profile_demand_nm3_per_hr"] == "320"

    assert float(data["treatment_capacity_nm3_per_hr"]) > 350

    assert data["station_available_capacity_nm3_per_hr"] == "680"
    assert data["station_capacity_is_adequate"] is True

    assert float(data["receiver_volume_m3"]) > 0
    assert data["receiver_storage_required"] is True

    assert float(data["annual_energy_kwh"]) > 0
    assert float(data["annual_energy_cost"]) > 0

    assert data["system_design_is_feasible"] is True
    assert data["engineering_messages"]


def test_greenfield_design_supports_minimum_workflow() -> None:
    request = build_request()

    request["treatment"] = None
    request["station"] = None
    request["receiver"] = None
    request["specific_power_kw_per_nm3_per_min"] = None
    request["annual_operating_days"] = None

    response = client.post(
        "/api/v1/compressed-air/greenfield/design",
        json=request,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["treatment_capacity_nm3_per_hr"] is None
    assert data["station_available_capacity_nm3_per_hr"] is None
    assert data["station_capacity_is_adequate"] is None
    assert data["receiver_volume_m3"] is None
    assert data["annual_energy_kwh"] is None


def test_invalid_consumer_quantity_returns_422() -> None:
    request = build_request()

    request["consumers"][0]["quantity"] = 0

    response = client.post(
        "/api/v1/compressed-air/greenfield/design",
        json=request,
    )

    assert response.status_code == 422


def test_invalid_receiver_pressure_band_returns_422() -> None:
    request = build_request()

    request["receiver"]["receiver_high_pressure_bar_g"] = "6.5"
    request["receiver"]["receiver_low_pressure_bar_g"] = "6.5"

    response = client.post(
        "/api/v1/compressed-air/greenfield/design",
        json=request,
    )

    assert response.status_code == 422

    assert (
        "Receiver high pressure must be greater than receiver low pressure"
        in response.json()["detail"]
    )


def test_energy_without_operating_days_returns_422() -> None:
    request = build_request()

    request["annual_operating_days"] = None

    response = client.post(
        "/api/v1/compressed-air/greenfield/design",
        json=request,
    )

    assert response.status_code == 422

    assert "Annual operating days are required" in response.json()["detail"]
