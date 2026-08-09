from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum

from app.domain.compressed_air.consumers.consumer_models import AirQualityClass


class InvalidAirTreatmentInputError(ValueError):
    """Raised when compressed-air treatment sizing inputs are invalid."""


class DryerType(StrEnum):
    """Compressed-air dryer technology."""

    REFRIGERATED = "REFRIGERATED"
    HEATLESS_DESICCANT = "HEATLESS_DESICCANT"
    HEATED_DESICCANT = "HEATED_DESICCANT"
    BLOWER_PURGE_DESICCANT = "BLOWER_PURGE_DESICCANT"
    MEMBRANE = "MEMBRANE"
    NONE = "NONE"


@dataclass(frozen=True, slots=True)
class AirTreatmentInput:
    """Input data for compressed-air treatment sizing."""

    required_delivered_flow_nm3_per_hr: Decimal

    required_air_quality: AirQualityClass
    dryer_type: DryerType

    dryer_correction_factor: Decimal = Decimal("1")
    dryer_purge_fraction: Decimal = Decimal("0")

    prefilter_pressure_drop_bar: Decimal = Decimal("0")
    afterfilter_pressure_drop_bar: Decimal = Decimal("0")
    dryer_pressure_drop_bar: Decimal = Decimal("0")

    treatment_capacity_margin_fraction: Decimal = Decimal("0")


@dataclass(frozen=True, slots=True)
class AirTreatmentResult:
    """Calculated compressed-air treatment sizing result."""

    required_delivered_flow_nm3_per_hr: Decimal

    dryer_purge_loss_nm3_per_hr: Decimal
    gross_flow_before_purge_nm3_per_hr: Decimal

    corrected_required_treatment_capacity_nm3_per_hr: Decimal
    recommended_treatment_capacity_nm3_per_hr: Decimal

    total_treatment_pressure_drop_bar: Decimal

    dryer_type: DryerType
    required_air_quality: AirQualityClass

    purge_loss_fraction: Decimal
    correction_factor: Decimal
    treatment_capacity_margin_fraction: Decimal


def calculate_air_treatment(
    inputs: AirTreatmentInput,
) -> AirTreatmentResult:
    """Calculate compressed-air treatment capacity and losses."""

    _validate_inputs(inputs)

    if inputs.dryer_purge_fraction >= Decimal("1"):
        raise InvalidAirTreatmentInputError("Dryer purge fraction must be less than one.")

    if inputs.dryer_purge_fraction == Decimal("0"):
        gross_flow_before_purge = inputs.required_delivered_flow_nm3_per_hr
        dryer_purge_loss = Decimal("0")
    else:
        gross_flow_before_purge = inputs.required_delivered_flow_nm3_per_hr / (
            Decimal("1") - inputs.dryer_purge_fraction
        )

        dryer_purge_loss = gross_flow_before_purge - inputs.required_delivered_flow_nm3_per_hr

    corrected_required_treatment_capacity = gross_flow_before_purge / inputs.dryer_correction_factor

    recommended_treatment_capacity = corrected_required_treatment_capacity * (
        Decimal("1") + inputs.treatment_capacity_margin_fraction
    )

    total_treatment_pressure_drop = (
        inputs.prefilter_pressure_drop_bar
        + inputs.afterfilter_pressure_drop_bar
        + inputs.dryer_pressure_drop_bar
    )

    return AirTreatmentResult(
        required_delivered_flow_nm3_per_hr=(inputs.required_delivered_flow_nm3_per_hr),
        dryer_purge_loss_nm3_per_hr=dryer_purge_loss,
        gross_flow_before_purge_nm3_per_hr=gross_flow_before_purge,
        corrected_required_treatment_capacity_nm3_per_hr=(corrected_required_treatment_capacity),
        recommended_treatment_capacity_nm3_per_hr=(recommended_treatment_capacity),
        total_treatment_pressure_drop_bar=(total_treatment_pressure_drop),
        dryer_type=inputs.dryer_type,
        required_air_quality=inputs.required_air_quality,
        purge_loss_fraction=inputs.dryer_purge_fraction,
        correction_factor=inputs.dryer_correction_factor,
        treatment_capacity_margin_fraction=(inputs.treatment_capacity_margin_fraction),
    )


def _validate_inputs(
    inputs: AirTreatmentInput,
) -> None:
    if inputs.required_delivered_flow_nm3_per_hr <= 0:
        raise InvalidAirTreatmentInputError("Required delivered flow must be greater than zero.")

    if inputs.dryer_correction_factor <= 0:
        raise InvalidAirTreatmentInputError("Dryer correction factor must be greater than zero.")

    if inputs.dryer_purge_fraction < 0:
        raise InvalidAirTreatmentInputError("Dryer purge fraction cannot be negative.")

    if inputs.prefilter_pressure_drop_bar < 0:
        raise InvalidAirTreatmentInputError("Prefilter pressure drop cannot be negative.")

    if inputs.afterfilter_pressure_drop_bar < 0:
        raise InvalidAirTreatmentInputError("Afterfilter pressure drop cannot be negative.")

    if inputs.dryer_pressure_drop_bar < 0:
        raise InvalidAirTreatmentInputError("Dryer pressure drop cannot be negative.")

    if (
        inputs.treatment_capacity_margin_fraction < 0
        or inputs.treatment_capacity_margin_fraction > 1
    ):
        raise InvalidAirTreatmentInputError(
            "Treatment capacity margin fraction must be between zero and one."
        )
