from decimal import Decimal

import pytest

from app.domain.selection.selection_engine import (
    InvalidSelectionInputError,
    select_compressor_type,
)
from app.domain.selection.selection_models import (
    CompressorSelectionCriteria,
    CompressorType,
    SelectionRating,
)


def build_reference_criteria() -> CompressorSelectionCriteria:
    return CompressorSelectionCriteria(
        required_flow_m3_per_hr=Decimal("14143.4"),
        suction_pressure_bar=Decimal("30"),
        discharge_pressure_bar=Decimal("90"),
        required_turndown_fraction=Decimal("0.70"),
        continuous_operation=True,
        gas_molecular_weight=Decimal("19.075"),
        estimated_operating_hours_per_year=Decimal("8400"),
    )


def test_select_compressor_type_returns_assessments() -> None:
    result = select_compressor_type(build_reference_criteria())

    assert result.reciprocating.compressor_type == CompressorType.RECIPROCATING
    assert result.centrifugal.compressor_type == CompressorType.CENTRIFUGAL

    assert result.reciprocating.overall_score > Decimal("0")
    assert result.centrifugal.overall_score > Decimal("0")

    assert result.recommended_type in {
        CompressorType.RECIPROCATING,
        CompressorType.CENTRIFUGAL,
    }

    assert result.score_difference >= Decimal("0")


def test_high_flow_continuous_duty_favors_centrifugal() -> None:
    criteria = CompressorSelectionCriteria(
        required_flow_m3_per_hr=Decimal("50000"),
        suction_pressure_bar=Decimal("10"),
        discharge_pressure_bar=Decimal("25"),
        required_turndown_fraction=Decimal("0.80"),
        continuous_operation=True,
        gas_molecular_weight=Decimal("20"),
        estimated_operating_hours_per_year=Decimal("8400"),
    )

    result = select_compressor_type(criteria)

    assert result.recommended_type == CompressorType.CENTRIFUGAL
    assert result.centrifugal.capacity_rating == SelectionRating.EXCELLENT
    assert result.centrifugal.maintenance_rating == SelectionRating.EXCELLENT


def test_high_pressure_ratio_and_wide_turndown_favor_reciprocating() -> None:
    criteria = CompressorSelectionCriteria(
        required_flow_m3_per_hr=Decimal("5000"),
        suction_pressure_bar=Decimal("5"),
        discharge_pressure_bar=Decimal("30"),
        required_turndown_fraction=Decimal("0.40"),
        continuous_operation=False,
        gas_molecular_weight=Decimal("18"),
        estimated_operating_hours_per_year=Decimal("4000"),
    )

    result = select_compressor_type(criteria)

    assert result.recommended_type == CompressorType.RECIPROCATING
    assert result.reciprocating.pressure_ratio_rating == SelectionRating.EXCELLENT
    assert result.reciprocating.turndown_rating == SelectionRating.EXCELLENT


def test_zero_required_flow_is_rejected() -> None:
    criteria = CompressorSelectionCriteria(
        required_flow_m3_per_hr=Decimal("0"),
        suction_pressure_bar=Decimal("10"),
        discharge_pressure_bar=Decimal("20"),
        required_turndown_fraction=Decimal("0.70"),
        continuous_operation=True,
        gas_molecular_weight=Decimal("20"),
        estimated_operating_hours_per_year=Decimal("8000"),
    )

    with pytest.raises(
        InvalidSelectionInputError,
        match="Required flow must be greater than zero",
    ):
        select_compressor_type(criteria)


def test_zero_suction_pressure_is_rejected() -> None:
    criteria = CompressorSelectionCriteria(
        required_flow_m3_per_hr=Decimal("1000"),
        suction_pressure_bar=Decimal("0"),
        discharge_pressure_bar=Decimal("20"),
        required_turndown_fraction=Decimal("0.70"),
        continuous_operation=True,
        gas_molecular_weight=Decimal("20"),
        estimated_operating_hours_per_year=Decimal("8000"),
    )

    with pytest.raises(
        InvalidSelectionInputError,
        match="Suction absolute pressure must be greater than zero",
    ):
        select_compressor_type(criteria)


def test_discharge_pressure_must_exceed_suction_pressure() -> None:
    criteria = CompressorSelectionCriteria(
        required_flow_m3_per_hr=Decimal("1000"),
        suction_pressure_bar=Decimal("10"),
        discharge_pressure_bar=Decimal("10"),
        required_turndown_fraction=Decimal("0.70"),
        continuous_operation=True,
        gas_molecular_weight=Decimal("20"),
        estimated_operating_hours_per_year=Decimal("8000"),
    )

    with pytest.raises(
        InvalidSelectionInputError,
        match="Discharge pressure must be greater than suction pressure",
    ):
        select_compressor_type(criteria)


def test_invalid_turndown_fraction_is_rejected() -> None:
    criteria = CompressorSelectionCriteria(
        required_flow_m3_per_hr=Decimal("1000"),
        suction_pressure_bar=Decimal("10"),
        discharge_pressure_bar=Decimal("20"),
        required_turndown_fraction=Decimal("0"),
        continuous_operation=True,
        gas_molecular_weight=Decimal("20"),
        estimated_operating_hours_per_year=Decimal("8000"),
    )

    with pytest.raises(
        InvalidSelectionInputError,
        match="Required turndown fraction must be greater than zero and not exceed one",
    ):
        select_compressor_type(criteria)


def test_zero_gas_molecular_weight_is_rejected() -> None:
    criteria = CompressorSelectionCriteria(
        required_flow_m3_per_hr=Decimal("1000"),
        suction_pressure_bar=Decimal("10"),
        discharge_pressure_bar=Decimal("20"),
        required_turndown_fraction=Decimal("0.70"),
        continuous_operation=True,
        gas_molecular_weight=Decimal("0"),
        estimated_operating_hours_per_year=Decimal("8000"),
    )

    with pytest.raises(
        InvalidSelectionInputError,
        match="Gas molecular weight must be greater than zero",
    ):
        select_compressor_type(criteria)


def test_negative_operating_hours_are_rejected() -> None:
    criteria = CompressorSelectionCriteria(
        required_flow_m3_per_hr=Decimal("1000"),
        suction_pressure_bar=Decimal("10"),
        discharge_pressure_bar=Decimal("20"),
        required_turndown_fraction=Decimal("0.70"),
        continuous_operation=True,
        gas_molecular_weight=Decimal("20"),
        estimated_operating_hours_per_year=Decimal("-1"),
    )

    with pytest.raises(
        InvalidSelectionInputError,
        match="Annual operating hours cannot be negative",
    ):
        select_compressor_type(criteria)
