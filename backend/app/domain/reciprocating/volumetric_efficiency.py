from decimal import Decimal

from app.domain.reciprocating.recip_models import VolumetricEfficiencyResult


class InvalidVolumetricEfficiencyInputError(ValueError):
    """Raised when volumetric-efficiency inputs are invalid."""


def calculate_volumetric_efficiency(
    clearance_fraction: Decimal,
    stage_compression_ratio: Decimal,
    suction_z_factor: Decimal,
    discharge_z_factor: Decimal,
    isentropic_exponent: Decimal,
    displacement_m3_per_hr: Decimal,
) -> VolumetricEfficiencyResult:
    """Calculate volumetric efficiency and delivered compressor capacity."""

    if clearance_fraction < 0 or clearance_fraction >= 1:
        raise InvalidVolumetricEfficiencyInputError(
            "Clearance fraction must be greater than or equal to zero and less than one."
        )

    if stage_compression_ratio <= 1:
        raise InvalidVolumetricEfficiencyInputError(
            "Stage compression ratio must be greater than one."
        )

    if suction_z_factor <= 0:
        raise InvalidVolumetricEfficiencyInputError("Suction Z-factor must be greater than zero.")

    if discharge_z_factor <= 0:
        raise InvalidVolumetricEfficiencyInputError("Discharge Z-factor must be greater than zero.")

    if isentropic_exponent <= 1:
        raise InvalidVolumetricEfficiencyInputError("Isentropic exponent must be greater than one.")

    if displacement_m3_per_hr <= 0:
        raise InvalidVolumetricEfficiencyInputError(
            "Compressor displacement must be greater than zero."
        )

    expansion_term = Decimal(
        str(float(stage_compression_ratio) ** (1.0 / float(isentropic_exponent)) - 1.0)
    )

    volumetric_efficiency = (
        Decimal("1") - clearance_fraction * (suction_z_factor / discharge_z_factor) * expansion_term
    )

    if volumetric_efficiency <= 0 or volumetric_efficiency > 1:
        raise InvalidVolumetricEfficiencyInputError(
            "Calculated volumetric efficiency must be greater than zero and not exceed one."
        )

    delivered_flow_m3_per_hr = volumetric_efficiency * displacement_m3_per_hr

    return VolumetricEfficiencyResult(
        volumetric_efficiency=volumetric_efficiency,
        delivered_flow_m3_per_hr=delivered_flow_m3_per_hr,
    )
