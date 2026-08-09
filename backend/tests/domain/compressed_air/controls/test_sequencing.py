from decimal import Decimal

import pytest

from app.domain.compressed_air.controls.sequencing import (
    InvalidSequencingInputError,
    UnitOperatingCommand,
    sequence_compressors,
)
from app.domain.compressed_air.station.station_models import (
    CompressorControlMode,
    CompressorDutyRole,
    CompressorTechnology,
    CompressorUnit,
)


def build_unit(
    *,
    unit_code: str,
    fad: str,
    role: CompressorDutyRole,
    control: CompressorControlMode,
    minimum_fraction: str,
    available: bool = True,
) -> CompressorUnit:
    return CompressorUnit(
        unit_code=unit_code,
        technology=CompressorTechnology.ROTARY_SCREW_OIL_INJECTED,
        control_mode=control,
        duty_role=role,
        rated_fad_nm3_per_hr=Decimal(fad),
        minimum_stable_flow_fraction=Decimal(minimum_fraction),
        rated_discharge_pressure_bar_g=Decimal("7.0"),
        rated_motor_power_kw=Decimal("250"),
        available=available,
    )


def build_station_units() -> tuple[CompressorUnit, ...]:
    return (
        build_unit(
            unit_code="AC-01",
            fad="1800",
            role=CompressorDutyRole.BASE_LOAD,
            control=CompressorControlMode.FIXED_SPEED,
            minimum_fraction="0.60",
        ),
        build_unit(
            unit_code="AC-02",
            fad="1400",
            role=CompressorDutyRole.TRIM,
            control=CompressorControlMode.VSD,
            minimum_fraction="0.20",
        ),
        build_unit(
            unit_code="AC-03",
            fad="1800",
            role=CompressorDutyRole.STANDBY,
            control=CompressorControlMode.FIXED_SPEED,
            minimum_fraction="0.60",
        ),
    )


def test_low_demand_is_handled_by_vsd_trim() -> None:
    result = sequence_compressors(
        units=build_station_units(),
        required_flow_nm3_per_hr=Decimal("700"),
    )

    assert result.demand_is_fully_covered is True
    assert result.unmet_flow_nm3_per_hr == Decimal("0")
    assert result.vsd_trim_active is True

    trim = next(item for item in result.unit_results if item.unit_code == "AC-02")

    assert trim.command == UnitOperatingCommand.TRIM
    assert trim.assigned_flow_nm3_per_hr == Decimal("700")


def test_normal_demand_uses_base_and_trim() -> None:
    result = sequence_compressors(
        units=build_station_units(),
        required_flow_nm3_per_hr=Decimal("2500"),
    )

    base = next(item for item in result.unit_results if item.unit_code == "AC-01")

    trim = next(item for item in result.unit_results if item.unit_code == "AC-02")

    standby = next(item for item in result.unit_results if item.unit_code == "AC-03")

    assert base.is_running is True
    assert trim.is_running is True
    assert standby.is_running is False

    assert base.assigned_flow_nm3_per_hr == Decimal("1800")
    assert trim.assigned_flow_nm3_per_hr == Decimal("700")

    assert result.assigned_flow_nm3_per_hr == Decimal("2500")
    assert result.demand_is_fully_covered is True


def test_peak_demand_uses_standby_capacity() -> None:
    result = sequence_compressors(
        units=build_station_units(),
        required_flow_nm3_per_hr=Decimal("4200"),
    )

    standby = next(item for item in result.unit_results if item.unit_code == "AC-03")

    assert standby.is_running is True
    assert standby.command == UnitOperatingCommand.FULL_LOAD

    assert result.assigned_flow_nm3_per_hr == Decimal("4200")
    assert result.unmet_flow_nm3_per_hr == Decimal("0")
    assert result.demand_is_fully_covered is True


def test_insufficient_capacity_reports_unmet_flow() -> None:
    units = (
        build_unit(
            unit_code="AC-01",
            fad="1800",
            role=CompressorDutyRole.BASE_LOAD,
            control=CompressorControlMode.FIXED_SPEED,
            minimum_fraction="0.60",
        ),
        build_unit(
            unit_code="AC-02",
            fad="1400",
            role=CompressorDutyRole.TRIM,
            control=CompressorControlMode.VSD,
            minimum_fraction="0.20",
        ),
    )

    result = sequence_compressors(
        units=units,
        required_flow_nm3_per_hr=Decimal("4000"),
    )

    assert result.assigned_flow_nm3_per_hr == Decimal("3200")
    assert result.unmet_flow_nm3_per_hr == Decimal("800")
    assert result.demand_is_fully_covered is False


def test_unavailable_standby_is_not_used() -> None:
    units = (
        build_station_units()[0],
        build_station_units()[1],
        build_unit(
            unit_code="AC-03",
            fad="1800",
            role=CompressorDutyRole.STANDBY,
            control=CompressorControlMode.FIXED_SPEED,
            minimum_fraction="0.60",
            available=False,
        ),
    )

    result = sequence_compressors(
        units=units,
        required_flow_nm3_per_hr=Decimal("4200"),
    )

    standby = next(item for item in result.unit_results if item.unit_code == "AC-03")

    assert standby.is_running is False
    assert result.unmet_flow_nm3_per_hr == Decimal("1000")
    assert result.demand_is_fully_covered is False


def test_zero_demand_stops_active_units() -> None:
    result = sequence_compressors(
        units=build_station_units(),
        required_flow_nm3_per_hr=Decimal("0"),
    )

    assert result.assigned_flow_nm3_per_hr == Decimal("0")
    assert result.unmet_flow_nm3_per_hr == Decimal("0")
    assert result.running_unit_count == 0
    assert result.demand_is_fully_covered is True

    assert all(not item.is_running for item in result.unit_results)


def test_negative_required_flow_is_rejected() -> None:
    with pytest.raises(
        InvalidSequencingInputError,
        match="Required flow cannot be negative",
    ):
        sequence_compressors(
            units=build_station_units(),
            required_flow_nm3_per_hr=Decimal("-1"),
        )


def test_empty_unit_list_is_rejected() -> None:
    with pytest.raises(
        InvalidSequencingInputError,
        match="At least one compressor unit is required",
    ):
        sequence_compressors(
            units=(),
            required_flow_nm3_per_hr=Decimal("1000"),
        )


def test_invalid_minimum_stable_fraction_is_rejected() -> None:
    bad_unit = build_unit(
        unit_code="AC-BAD",
        fad="1000",
        role=CompressorDutyRole.TRIM,
        control=CompressorControlMode.VSD,
        minimum_fraction="1.10",
    )

    with pytest.raises(
        InvalidSequencingInputError,
        match="Minimum stable flow fraction must be between zero and one",
    ):
        sequence_compressors(
            units=(bad_unit,),
            required_flow_nm3_per_hr=Decimal("500"),
        )
