from decimal import Decimal

from app.domain.centrifugal.centrifugal_models import (
    CentrifugalOperatingPoint,
    PolytropicHeadResult,
)

UNIVERSAL_GAS_CONSTANT_KJ_PER_KMOL_K = Decimal("8.314462618")


class InvalidPolytropicHeadInputError(ValueError):
    """Raised when centrifugal polytropic-head inputs are invalid."""


def calculate_polytropic_head(
    operating_point: CentrifugalOperatingPoint,
) -> PolytropicHeadResult:
    """Calculate centrifugal compressor polytropic head."""

    if operating_point.suction_pressure_bar <= 0:
        raise InvalidPolytropicHeadInputError(
            "Suction absolute pressure must be greater than zero."
        )

    if operating_point.discharge_pressure_bar <= operating_point.suction_pressure_bar:
        raise InvalidPolytropicHeadInputError(
            "Discharge pressure must be greater than suction pressure."
        )

    if operating_point.suction_temperature_k <= 0:
        raise InvalidPolytropicHeadInputError(
            "Suction absolute temperature must be greater than zero."
        )

    if operating_point.molecular_weight_kg_per_kmol <= 0:
        raise InvalidPolytropicHeadInputError("Molecular weight must be greater than zero.")

    if operating_point.suction_z_factor <= 0:
        raise InvalidPolytropicHeadInputError("Suction Z-factor must be greater than zero.")

    if operating_point.discharge_z_factor <= 0:
        raise InvalidPolytropicHeadInputError("Discharge Z-factor must be greater than zero.")

    if operating_point.isentropic_exponent <= 1:
        raise InvalidPolytropicHeadInputError("Isentropic exponent must be greater than one.")

    if operating_point.polytropic_efficiency <= 0 or operating_point.polytropic_efficiency > 1:
        raise InvalidPolytropicHeadInputError(
            "Polytropic efficiency must be greater than zero and not exceed one."
        )

    overall_compression_ratio = (
        operating_point.discharge_pressure_bar / operating_point.suction_pressure_bar
    )

    average_z_factor = (
        operating_point.suction_z_factor + operating_point.discharge_z_factor
    ) / Decimal("2")

    k = operating_point.isentropic_exponent
    efficiency = operating_point.polytropic_efficiency

    polytropic_exponent = Decimal("1") / (Decimal("1") - ((k - Decimal("1")) / (k * efficiency)))

    exponent = (polytropic_exponent - Decimal("1")) / polytropic_exponent

    specific_gas_constant = (
        UNIVERSAL_GAS_CONSTANT_KJ_PER_KMOL_K / operating_point.molecular_weight_kg_per_kmol
    )

    ratio_term = Decimal(str(float(overall_compression_ratio) ** float(exponent)))

    polytropic_head_kj_per_kg = (
        average_z_factor
        * specific_gas_constant
        * operating_point.suction_temperature_k
        * (polytropic_exponent / (polytropic_exponent - Decimal("1")))
        * (ratio_term - Decimal("1"))
    )

    return PolytropicHeadResult(
        average_z_factor=average_z_factor,
        polytropic_exponent=polytropic_exponent,
        overall_compression_ratio=overall_compression_ratio,
        polytropic_head_kj_per_kg=polytropic_head_kj_per_kg,
    )
