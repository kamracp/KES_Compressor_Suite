from dataclasses import dataclass
from decimal import Decimal, localcontext


class InvalidCompressionInputError(ValueError):
    """Raised when compression-ratio inputs are invalid."""


@dataclass(frozen=True, slots=True)
class CompressionRatioResult:
    """Compression-ratio calculation result."""

    suction_pressure_bar: Decimal
    discharge_pressure_bar: Decimal
    overall_compression_ratio: Decimal
    number_of_stages: int
    stage_compression_ratio: Decimal


def calculate_compression_ratio(
    suction_pressure_bar: Decimal,
    discharge_pressure_bar: Decimal,
    number_of_stages: int,
) -> CompressionRatioResult:
    """Calculate overall and equal per-stage compression ratios."""

    if suction_pressure_bar <= 0:
        raise InvalidCompressionInputError("Suction absolute pressure must be greater than zero.")

    if discharge_pressure_bar <= 0:
        raise InvalidCompressionInputError("Discharge absolute pressure must be greater than zero.")

    if discharge_pressure_bar <= suction_pressure_bar:
        raise InvalidCompressionInputError(
            "Discharge pressure must be greater than suction pressure."
        )

    if number_of_stages < 1:
        raise InvalidCompressionInputError("Number of compression stages must be at least one.")

    with localcontext() as context:
        context.prec = 28

        overall_ratio = discharge_pressure_bar / suction_pressure_bar

        stage_ratio = Decimal(str(float(overall_ratio) ** (1.0 / number_of_stages)))

    return CompressionRatioResult(
        suction_pressure_bar=suction_pressure_bar,
        discharge_pressure_bar=discharge_pressure_bar,
        overall_compression_ratio=overall_ratio,
        number_of_stages=number_of_stages,
        stage_compression_ratio=stage_ratio,
    )
