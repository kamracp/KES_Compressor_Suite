from decimal import Decimal

import pytest

from app.domain.compressed_air.station.capacity import (
    InvalidStationCapacityInputError,
    calculate_station_capacity,
)
from app.domain.compressed_air.station.station_models import (
    CompressorControlMode,
    CompressorDutyRole,
    CompressorStationConfiguration,
    CompressorTechnology,
    CompressorUnit,
    RedundancyPhilosophy,
)


def build_unit(
    *,
    unit_code: str,
    rated_fad: str,
    duty_role: CompressorDutyRole,
    control_mode: CompressorControlMode,
    available: bool = True,
) -> CompressorUnit:
    return CompressorUnit(
        unit_code=unit_code,
        technology=CompressorTechnology.ROTARY_SCREW_OIL_INJECTED,
        control_mode=control_mode,
        duty_role=duty_role,
        rated_fad_nm3_per_hr=Decimal(rated_fad),
        minimum_stable_flow_fraction=Decimal("0.25")
        if control_mode == CompressorControlMode.VSD
        else Decimal("0.60"),
        rated_discharge_pressure_bar_g=Decimal("7.0"),
        rated_motor_power_kw=Decimal("250"),
        available=available,
    )


def test_station_capacity_split() -> None:
    configuration = CompressorStationConfiguration(
        station_code="CAS-01",
        units=(
            build_unit(
                unit_code="AC-01",
                rated_fad="1800",
                duty_role=CompressorDutyRole.BASE_LOAD,
                control_mode=CompressorControlMode.FIXED_SPEED,
            ),
            build_unit(
                unit_code="AC-02",
                rated_fad="1400",
                duty_role=CompressorDutyRole.TRIM,
                control_mode=CompressorControlMode.VSD,
            ),
            build_unit(
                unit_code="AC-03",
                rated_fad="1800",
                duty_role=CompressorDutyRole.STANDBY,
                control_mode=CompressorControlMode.FIXED_SPEED,
            ),
        ),
        redundancy_philosophy=RedundancyPhilosophy.N_PLUS_1,
        minimum_required_pressure_bar_g=Decimal("6.7"),
        design_flow_nm3_per_hr=Decimal("3000"),
        master_control_enabled=True,
    )

    result = calculate_station_capacity(configuration)

    assert result.total_installed_fad_nm3_per_hr == Decimal("5000")
    assert result.available_fad_nm3_per_hr == Decimal("5000")

    assert result.duty_fad_nm3_per_hr == Decimal("1800")
    assert result.trim_fad_nm3_per_hr == Decimal("1400")
    assert result.standby_fad_nm3_per_hr == Decimal("1800")

    assert result.installed_capacity_margin_nm3_per_hr == Decimal("2000")
    assert result.available_capacity_margin_nm3_per_hr == Decimal("2000")

    assert result.design_capacity_is_adequate is True
    assert result.available_capacity_is_adequate is True

    assert result.active_unit_count == 2
    assert result.standby_unit_count == 1


def test_unavailable_unit_reduces_available_capacity() -> None:
    configuration = CompressorStationConfiguration(
        station_code="CAS-02",
        units=(
            build_unit(
                unit_code="AC-01",
                rated_fad="1800",
                duty_role=CompressorDutyRole.BASE_LOAD,
                control_mode=CompressorControlMode.FIXED_SPEED,
            ),
            build_unit(
                unit_code="AC-02",
                rated_fad="1400",
                duty_role=CompressorDutyRole.TRIM,
                control_mode=CompressorControlMode.VSD,
                available=False,
            ),
            build_unit(
                unit_code="AC-03",
                rated_fad="1800",
                duty_role=CompressorDutyRole.STANDBY,
                control_mode=CompressorControlMode.FIXED_SPEED,
            ),
        ),
        redundancy_philosophy=RedundancyPhilosophy.N_PLUS_1,
        minimum_required_pressure_bar_g=Decimal("6.7"),
        design_flow_nm3_per_hr=Decimal("3000"),
    )

    result = calculate_station_capacity(configuration)

    assert result.total_installed_fad_nm3_per_hr == Decimal("5000")
    assert result.available_fad_nm3_per_hr == Decimal("3600")

    assert result.available_capacity_margin_nm3_per_hr == Decimal("600")
    assert result.available_capacity_is_adequate is True


def test_available_capacity_can_be_inadequate() -> None:
    configuration = CompressorStationConfiguration(
        station_code="CAS-03",
        units=(
            build_unit(
                unit_code="AC-01",
                rated_fad="1800",
                duty_role=CompressorDutyRole.BASE_LOAD,
                control_mode=CompressorControlMode.FIXED_SPEED,
            ),
            build_unit(
                unit_code="AC-02",
                rated_fad="1400",
                duty_role=CompressorDutyRole.TRIM,
                control_mode=CompressorControlMode.VSD,
                available=False,
            ),
        ),
        redundancy_philosophy=RedundancyPhilosophy.NONE,
        minimum_required_pressure_bar_g=Decimal("6.7"),
        design_flow_nm3_per_hr=Decimal("2500"),
    )

    result = calculate_station_capacity(configuration)

    assert result.total_installed_fad_nm3_per_hr == Decimal("3200")
    assert result.available_fad_nm3_per_hr == Decimal("1800")

    assert result.design_capacity_is_adequate is True
    assert result.available_capacity_is_adequate is False
    assert result.available_capacity_margin_nm3_per_hr == Decimal("-700")


def test_empty_station_code_is_rejected() -> None:
    configuration = CompressorStationConfiguration(
        station_code="",
        units=(
            build_unit(
                unit_code="AC-01",
                rated_fad="1000",
                duty_role=CompressorDutyRole.DUTY,
                control_mode=CompressorControlMode.FIXED_SPEED,
            ),
        ),
        redundancy_philosophy=RedundancyPhilosophy.NONE,
        minimum_required_pressure_bar_g=Decimal("6"),
        design_flow_nm3_per_hr=Decimal("800"),
    )

    with pytest.raises(
        InvalidStationCapacityInputError,
        match="Station code cannot be empty",
    ):
        calculate_station_capacity(configuration)


def test_empty_unit_list_is_rejected() -> None:
    configuration = CompressorStationConfiguration(
        station_code="CAS-04",
        units=(),
        redundancy_philosophy=RedundancyPhilosophy.NONE,
        minimum_required_pressure_bar_g=Decimal("6"),
        design_flow_nm3_per_hr=Decimal("800"),
    )

    with pytest.raises(
        InvalidStationCapacityInputError,
        match="At least one compressor unit is required",
    ):
        calculate_station_capacity(configuration)


def test_zero_design_flow_is_rejected() -> None:
    configuration = CompressorStationConfiguration(
        station_code="CAS-05",
        units=(
            build_unit(
                unit_code="AC-01",
                rated_fad="1000",
                duty_role=CompressorDutyRole.DUTY,
                control_mode=CompressorControlMode.FIXED_SPEED,
            ),
        ),
        redundancy_philosophy=RedundancyPhilosophy.NONE,
        minimum_required_pressure_bar_g=Decimal("6"),
        design_flow_nm3_per_hr=Decimal("0"),
    )

    with pytest.raises(
        InvalidStationCapacityInputError,
        match="Design flow must be greater than zero",
    ):
        calculate_station_capacity(configuration)


def test_invalid_minimum_stable_flow_fraction_is_rejected() -> None:
    bad_unit = CompressorUnit(
        unit_code="AC-BAD",
        technology=CompressorTechnology.ROTARY_SCREW_OIL_INJECTED,
        control_mode=CompressorControlMode.VSD,
        duty_role=CompressorDutyRole.TRIM,
        rated_fad_nm3_per_hr=Decimal("1000"),
        minimum_stable_flow_fraction=Decimal("1.10"),
        rated_discharge_pressure_bar_g=Decimal("7"),
        rated_motor_power_kw=Decimal("150"),
    )

    configuration = CompressorStationConfiguration(
        station_code="CAS-06",
        units=(bad_unit,),
        redundancy_philosophy=RedundancyPhilosophy.NONE,
        minimum_required_pressure_bar_g=Decimal("6"),
        design_flow_nm3_per_hr=Decimal("800"),
    )

    with pytest.raises(
        InvalidStationCapacityInputError,
        match="Minimum stable flow fraction must be between zero and one",
    ):
        calculate_station_capacity(configuration)
