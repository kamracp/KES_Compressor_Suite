from decimal import Decimal

import pytest

from app.domain.compressed_air.equipment.correction_factors import (
    STANDARD_ATMOSPHERIC_PRESSURE_BAR_A,
    EquipmentCorrectionInput,
    InvalidCorrectionFactorInputError,
    apply_capacity_correction,
    calculate_inlet_condition_correction,
    calculate_site_pressure_bar_a,
)


def test_standard_reference_conditions_produce_unity_factor() -> None:
    result = calculate_inlet_condition_correction(
        EquipmentCorrectionInput(
            actual_inlet_pressure_bar_a=STANDARD_ATMOSPHERIC_PRESSURE_BAR_A,
            actual_inlet_temperature_c=Decimal("20"),
        )
    )

    assert result.pressure_factor == Decimal("1")
    assert result.temperature_factor == Decimal("1")
    assert result.combined_capacity_factor == Decimal("1")


def test_lower_inlet_pressure_reduces_capacity_factor() -> None:
    result = calculate_inlet_condition_correction(
        EquipmentCorrectionInput(
            actual_inlet_pressure_bar_a=Decimal("0.90"),
            actual_inlet_temperature_c=Decimal("20"),
        )
    )

    assert result.pressure_factor < Decimal("1")
    assert result.combined_capacity_factor < Decimal("1")


def test_higher_inlet_temperature_reduces_temperature_factor() -> None:
    result = calculate_inlet_condition_correction(
        EquipmentCorrectionInput(
            actual_inlet_pressure_bar_a=STANDARD_ATMOSPHERIC_PRESSURE_BAR_A,
            actual_inlet_temperature_c=Decimal("40"),
        )
    )

    assert result.temperature_factor < Decimal("1")
    assert result.combined_capacity_factor < Decimal("1")


def test_capacity_correction_is_applied() -> None:
    correction = calculate_inlet_condition_correction(
        EquipmentCorrectionInput(
            actual_inlet_pressure_bar_a=Decimal("0.95"),
            actual_inlet_temperature_c=Decimal("30"),
        )
    )

    corrected_capacity = apply_capacity_correction(
        reference_capacity_nm3_per_hr=Decimal("1000"),
        correction=correction,
    )

    assert corrected_capacity == (Decimal("1000") * correction.combined_capacity_factor)


def test_reference_capacity_must_be_positive() -> None:
    correction = calculate_inlet_condition_correction(
        EquipmentCorrectionInput(
            actual_inlet_pressure_bar_a=STANDARD_ATMOSPHERIC_PRESSURE_BAR_A,
            actual_inlet_temperature_c=Decimal("20"),
        )
    )

    with pytest.raises(
        InvalidCorrectionFactorInputError,
        match="Reference capacity must be greater than zero",
    ):
        apply_capacity_correction(
            reference_capacity_nm3_per_hr=Decimal("0"),
            correction=correction,
        )


def test_sea_level_site_pressure_is_close_to_standard_pressure() -> None:
    pressure = calculate_site_pressure_bar_a(
        altitude_m=Decimal("0"),
    )

    assert pressure == STANDARD_ATMOSPHERIC_PRESSURE_BAR_A


def test_site_pressure_decreases_with_altitude() -> None:
    sea_level = calculate_site_pressure_bar_a(
        altitude_m=Decimal("0"),
    )

    high_altitude = calculate_site_pressure_bar_a(
        altitude_m=Decimal("2000"),
    )

    assert high_altitude < sea_level


def test_altitude_below_supported_range_is_rejected() -> None:
    with pytest.raises(
        InvalidCorrectionFactorInputError,
        match="Altitude is outside the supported preliminary-engineering range",
    ):
        calculate_site_pressure_bar_a(
            altitude_m=Decimal("-501"),
        )


def test_altitude_above_supported_range_is_rejected() -> None:
    with pytest.raises(
        InvalidCorrectionFactorInputError,
        match="Altitude is outside the supported preliminary-engineering range",
    ):
        calculate_site_pressure_bar_a(
            altitude_m=Decimal("11001"),
        )


def test_actual_inlet_pressure_must_be_positive() -> None:
    with pytest.raises(
        InvalidCorrectionFactorInputError,
        match="Actual inlet absolute pressure must be greater than zero",
    ):
        calculate_inlet_condition_correction(
            EquipmentCorrectionInput(
                actual_inlet_pressure_bar_a=Decimal("0"),
                actual_inlet_temperature_c=Decimal("20"),
            )
        )


def test_reference_inlet_pressure_must_be_positive() -> None:
    with pytest.raises(
        InvalidCorrectionFactorInputError,
        match="Reference inlet absolute pressure must be greater than zero",
    ):
        calculate_inlet_condition_correction(
            EquipmentCorrectionInput(
                actual_inlet_pressure_bar_a=Decimal("1"),
                actual_inlet_temperature_c=Decimal("20"),
                reference_inlet_pressure_bar_a=Decimal("0"),
            )
        )


def test_actual_temperature_must_be_above_absolute_zero() -> None:
    with pytest.raises(
        InvalidCorrectionFactorInputError,
        match="Actual inlet temperature must be above absolute zero",
    ):
        calculate_inlet_condition_correction(
            EquipmentCorrectionInput(
                actual_inlet_pressure_bar_a=Decimal("1"),
                actual_inlet_temperature_c=Decimal("-273.15"),
            )
        )


def test_reference_temperature_must_be_above_absolute_zero() -> None:
    with pytest.raises(
        InvalidCorrectionFactorInputError,
        match="Reference inlet temperature must be above absolute zero",
    ):
        calculate_inlet_condition_correction(
            EquipmentCorrectionInput(
                actual_inlet_pressure_bar_a=Decimal("1"),
                actual_inlet_temperature_c=Decimal("20"),
                reference_inlet_temperature_c=Decimal("-273.15"),
            )
        )
