from decimal import Decimal

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_compressor_selection_endpoint() -> None:
    response = client.post(
        "/api/v1/compressor/selection",
        json={
            "required_flow_m3_per_hr": "14143.4",
            "suction_pressure_bar": "30",
            "discharge_pressure_bar": "90",
            "required_turndown_fraction": "0.70",
            "continuous_operation": True,
            "gas_molecular_weight": "19.075",
            "estimated_operating_hours_per_year": "8400",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["recommended_type"] in {
        "RECIPROCATING",
        "CENTRIFUGAL",
        "ROTARY_SCREW",
    }
    assert Decimal(data["reciprocating"]["overall_score"]) > Decimal("0")
    assert Decimal(data["centrifugal"]["overall_score"]) > Decimal("0")
    assert Decimal(data["rotary_screw"]["overall_score"]) > Decimal("0")


def test_common_compression_endpoint() -> None:
    response = client.post(
        "/api/v1/compressor/compression/calculate",
        json={
            "gas": {
                "suction_pressure_bar": "30",
                "discharge_pressure_bar": "90",
                "suction_temperature_k": "308.15",
                "mass_flow_kg_per_s": "93.376",
                "actual_flow_m3_per_s": "3.9287",
                "molecular_weight_kg_per_kmol": "19.075",
                "suction_z_factor": "0.9398",
                "discharge_z_factor": "0.8700",
                "isentropic_exponent": "1.27",
            },
            "number_of_stages": 3,
            "specific_heat_cp_kj_per_kg_k": "2.35",
            "isentropic_efficiency": "0.78",
            "mechanical_efficiency": "0.95",
            "intercooler_outlet_temperature_k": "313.15",
            "cooling_water_inlet_temperature_k": "303.15",
            "cooling_water_outlet_temperature_k": "313.15",
            "selected_driver_power_kw": "25000",
            "driver_service_factor": "0.10",
            "motor_efficiency": "0.96",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["staging"]["overall_compression_ratio"] == "3"
    assert Decimal(data["power"]["shaft_power_kw"]) > Decimal("0")
    assert Decimal(data["cooling"]["cooling_duty_kw"]) > Decimal("0")
    assert data["driver"]["driver_is_adequate"] is True


def test_reciprocating_endpoint() -> None:
    response = client.post(
        "/api/v1/compressor/reciprocating/calculate",
        json={
            "required_flow_m3_per_hr": "14143.4",
            "bore_mm": "300",
            "stroke_mm": "400",
            "rod_diameter_mm": "70",
            "speed_rpm": "600",
            "clearance_fraction": "0.10",
            "stage_compression_ratio": "1.442",
            "suction_z_factor": "0.9398",
            "discharge_z_factor": "0.8700",
            "isentropic_exponent": "1.27",
            "suction_pressure_bar": "30",
            "discharge_pressure_bar": "43.27",
            "allowable_rod_load_kn": "450",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["cylinder_sizing"]["required_cylinders"] == 8
    assert data["cylinder_sizing"]["capacity_is_adequate"] is True
    assert data["rod_load"]["rod_load_is_adequate"] is True


def test_centrifugal_endpoint() -> None:
    response = client.post(
        "/api/v1/compressor/centrifugal/calculate",
        json={
            "gas": {
                "suction_pressure_bar": "30",
                "discharge_pressure_bar": "90",
                "suction_temperature_k": "308.15",
                "mass_flow_kg_per_s": "93.376",
                "actual_flow_m3_per_s": "3.9287",
                "molecular_weight_kg_per_kmol": "19.075",
                "suction_z_factor": "0.9398",
                "discharge_z_factor": "0.8700",
                "isentropic_exponent": "1.27",
            },
            "polytropic_efficiency": "0.78",
            "number_of_impeller_stages": 3,
            "head_coefficient": "0.55",
            "rotational_speed_rpm": "8000",
            "mechanical_loss_fraction": "0.025",
            "driver_margin_fraction": "0.10",
            "selected_driver_power_kw": "22000",
            "motor_efficiency": "0.96",
            "surge_flow_fraction": "0.70",
            "anti_surge_margin_fraction": "0.10",
            "stonewall_flow_fraction": "1.25",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["head"]["overall_compression_ratio"] == "3"
    assert data["impeller"]["number_of_impeller_stages"] == 3
    assert Decimal(data["power"]["gas_power_kw"]) > Decimal("0")
    assert data["surge"]["surge_margin_fraction"] == "0.30"
    assert len(data["performance_map"]["points"]) == 3


def test_invalid_selection_request_returns_422() -> None:
    response = client.post(
        "/api/v1/compressor/selection",
        json={
            "required_flow_m3_per_hr": "0",
            "suction_pressure_bar": "30",
            "discharge_pressure_bar": "90",
            "required_turndown_fraction": "0.70",
            "continuous_operation": True,
            "gas_molecular_weight": "19.075",
            "estimated_operating_hours_per_year": "8400",
        },
    )

    assert response.status_code == 422


def test_rotary_screw_endpoint_minimal_payload() -> None:
    response = client.post(
        "/api/v1/compressor/rotary-screw/calculate",
        json={
            "inlet_pressure_bar_a": "1",
            "inlet_temperature_k": "300",
            "discharge_pressure_bar_g": "7",
            "rotational_speed_rpm": "3000",
            "oil_type": "OIL_INJECTED",
            "control_type": "FIXED_SPEED_LOAD_UNLOAD",
            "rated_fad_m3_per_min": "10",
            "package_input_power_kw": "60",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["displacement"] is None
    assert data["standard_air_correction"] is None
    assert Decimal(data["performance"]["specific_power_kw_per_m3_min"]) == Decimal("6.000")


def test_rotary_screw_endpoint_full_payload() -> None:
    response = client.post(
        "/api/v1/compressor/rotary-screw/calculate",
        json={
            "inlet_pressure_bar_a": "1",
            "inlet_temperature_k": "300",
            "discharge_pressure_bar_g": "7",
            "rotational_speed_rpm": "3000",
            "oil_type": "OIL_FREE",
            "control_type": "VARIABLE_SPEED_DRIVE",
            "stage_count": "TWO_STAGE",
            "rated_fad_m3_per_min": "10",
            "package_input_power_kw": "60",
            "rotor_geometry": {
                "male_rotor_diameter_mm": "200",
                "rotor_length_mm": "300",
                "area_utilisation_coefficient": "0.5",
            },
            "standard_reference_pressure_bar_a": "1",
            "standard_reference_temperature_k": "300",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert Decimal(data["displacement"]["theoretical_displacement_m3_per_min"]) == Decimal(
        "18.000"
    )
    assert Decimal(
        data["standard_air_correction"]["corrected_fad_m3_per_min"]
    ) == Decimal("10.0")


def test_invalid_rotary_screw_request_returns_422() -> None:
    response = client.post(
        "/api/v1/compressor/rotary-screw/calculate",
        json={
            "inlet_pressure_bar_a": "0",
            "inlet_temperature_k": "300",
            "discharge_pressure_bar_g": "7",
            "rotational_speed_rpm": "3000",
            "oil_type": "OIL_INJECTED",
            "control_type": "FIXED_SPEED_LOAD_UNLOAD",
            "rated_fad_m3_per_min": "10",
            "package_input_power_kw": "60",
        },
    )

    assert response.status_code == 422
