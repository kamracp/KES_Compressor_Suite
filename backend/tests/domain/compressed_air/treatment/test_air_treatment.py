from decimal import Decimal

import pytest

from app.domain.compressed_air.consumers.consumer_models import AirQualityClass
from app.domain.compressed_air.treatment.air_treatment import (
    AirTreatmentInput,
    DryerType,
    InvalidAirTreatmentInputError,
    calculate_air_treatment,
)


def test_refrigerated_dryer_without_purge() -> None:
    result = calculate_air_treatment(
        AirTreatmentInput(
            required_delivered_flow_nm3_per_hr=Decimal("3000"),
            required_air_quality=AirQualityClass.GENERAL_PLANT_AIR,
            dryer_type=DryerType.REFRIGERATED,
            dryer_correction_factor=Decimal("0.95"),
            dryer_purge_fraction=Decimal("0"),
            prefilter_pressure_drop_bar=Decimal("0.05"),
            afterfilter_pressure_drop_bar=Decimal("0.05"),
            dryer_pressure_drop_bar=Decimal("0.10"),
            treatment_capacity_margin_fraction=Decimal("0.10"),
        )
    )

    assert result.required_delivered_flow_nm3_per_hr == Decimal("3000")
    assert result.dryer_purge_loss_nm3_per_hr == Decimal("0")
    assert result.gross_flow_before_purge_nm3_per_hr == Decimal("3000")

    assert result.corrected_required_treatment_capacity_nm3_per_hr == (
        Decimal("3000") / Decimal("0.95")
    )

    assert result.recommended_treatment_capacity_nm3_per_hr == (
        result.corrected_required_treatment_capacity_nm3_per_hr * Decimal("1.10")
    )

    assert result.total_treatment_pressure_drop_bar == Decimal("0.20")


def test_heatless_desiccant_dryer_accounts_for_purge_loss() -> None:
    result = calculate_air_treatment(
        AirTreatmentInput(
            required_delivered_flow_nm3_per_hr=Decimal("3000"),
            required_air_quality=AirQualityClass.INSTRUMENT_AIR,
            dryer_type=DryerType.HEATLESS_DESICCANT,
            dryer_correction_factor=Decimal("0.90"),
            dryer_purge_fraction=Decimal("0.15"),
        )
    )

    expected_gross_flow = Decimal("3000") / Decimal("0.85")

    assert result.gross_flow_before_purge_nm3_per_hr == expected_gross_flow

    assert result.dryer_purge_loss_nm3_per_hr == (expected_gross_flow - Decimal("3000"))

    assert result.corrected_required_treatment_capacity_nm3_per_hr == (
        expected_gross_flow / Decimal("0.90")
    )


def test_lower_correction_factor_increases_required_capacity() -> None:
    favorable = calculate_air_treatment(
        AirTreatmentInput(
            required_delivered_flow_nm3_per_hr=Decimal("3000"),
            required_air_quality=AirQualityClass.GENERAL_PLANT_AIR,
            dryer_type=DryerType.REFRIGERATED,
            dryer_correction_factor=Decimal("1.00"),
        )
    )

    derated = calculate_air_treatment(
        AirTreatmentInput(
            required_delivered_flow_nm3_per_hr=Decimal("3000"),
            required_air_quality=AirQualityClass.GENERAL_PLANT_AIR,
            dryer_type=DryerType.REFRIGERATED,
            dryer_correction_factor=Decimal("0.80"),
        )
    )

    assert (
        derated.corrected_required_treatment_capacity_nm3_per_hr
        > favorable.corrected_required_treatment_capacity_nm3_per_hr
    )


def test_pressure_drops_are_aggregated() -> None:
    result = calculate_air_treatment(
        AirTreatmentInput(
            required_delivered_flow_nm3_per_hr=Decimal("1000"),
            required_air_quality=AirQualityClass.GENERAL_PLANT_AIR,
            dryer_type=DryerType.REFRIGERATED,
            prefilter_pressure_drop_bar=Decimal("0.08"),
            afterfilter_pressure_drop_bar=Decimal("0.07"),
            dryer_pressure_drop_bar=Decimal("0.12"),
        )
    )

    assert result.total_treatment_pressure_drop_bar == Decimal("0.27")


def test_capacity_margin_increases_recommended_size() -> None:
    result = calculate_air_treatment(
        AirTreatmentInput(
            required_delivered_flow_nm3_per_hr=Decimal("2000"),
            required_air_quality=AirQualityClass.GENERAL_PLANT_AIR,
            dryer_type=DryerType.REFRIGERATED,
            dryer_correction_factor=Decimal("1"),
            treatment_capacity_margin_fraction=Decimal("0.20"),
        )
    )

    assert result.corrected_required_treatment_capacity_nm3_per_hr == Decimal("2000")

    assert result.recommended_treatment_capacity_nm3_per_hr == Decimal("2400.00")


def test_zero_delivered_flow_is_rejected() -> None:
    with pytest.raises(
        InvalidAirTreatmentInputError,
        match="Required delivered flow must be greater than zero",
    ):
        calculate_air_treatment(
            AirTreatmentInput(
                required_delivered_flow_nm3_per_hr=Decimal("0"),
                required_air_quality=AirQualityClass.GENERAL_PLANT_AIR,
                dryer_type=DryerType.REFRIGERATED,
            )
        )


def test_zero_correction_factor_is_rejected() -> None:
    with pytest.raises(
        InvalidAirTreatmentInputError,
        match="Dryer correction factor must be greater than zero",
    ):
        calculate_air_treatment(
            AirTreatmentInput(
                required_delivered_flow_nm3_per_hr=Decimal("1000"),
                required_air_quality=AirQualityClass.GENERAL_PLANT_AIR,
                dryer_type=DryerType.REFRIGERATED,
                dryer_correction_factor=Decimal("0"),
            )
        )


def test_purge_fraction_equal_to_one_is_rejected() -> None:
    with pytest.raises(
        InvalidAirTreatmentInputError,
        match="Dryer purge fraction must be less than one",
    ):
        calculate_air_treatment(
            AirTreatmentInput(
                required_delivered_flow_nm3_per_hr=Decimal("1000"),
                required_air_quality=AirQualityClass.INSTRUMENT_AIR,
                dryer_type=DryerType.HEATLESS_DESICCANT,
                dryer_purge_fraction=Decimal("1"),
            )
        )


def test_negative_filter_pressure_drop_is_rejected() -> None:
    with pytest.raises(
        InvalidAirTreatmentInputError,
        match="Prefilter pressure drop cannot be negative",
    ):
        calculate_air_treatment(
            AirTreatmentInput(
                required_delivered_flow_nm3_per_hr=Decimal("1000"),
                required_air_quality=AirQualityClass.GENERAL_PLANT_AIR,
                dryer_type=DryerType.REFRIGERATED,
                prefilter_pressure_drop_bar=Decimal("-0.01"),
            )
        )


def test_invalid_capacity_margin_is_rejected() -> None:
    with pytest.raises(
        InvalidAirTreatmentInputError,
        match=("Treatment capacity margin fraction must be between zero and one"),
    ):
        calculate_air_treatment(
            AirTreatmentInput(
                required_delivered_flow_nm3_per_hr=Decimal("1000"),
                required_air_quality=AirQualityClass.GENERAL_PLANT_AIR,
                dryer_type=DryerType.REFRIGERATED,
                treatment_capacity_margin_fraction=Decimal("1.10"),
            )
        )
