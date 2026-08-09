from dataclasses import dataclass
from decimal import Decimal, localcontext


class InvalidStagingInputError(ValueError):
    """Raised when staging inputs are invalid."""


@dataclass(frozen=True, slots=True)
class CompressionStage:
    """Represents one compression stage."""

    stage_number: int
    inlet_pressure_bar: Decimal
    outlet_pressure_bar: Decimal
    compression_ratio: Decimal


@dataclass(frozen=True, slots=True)
class StagingResult:
    """Compression staging calculation result."""

    number_of_stages: int
    overall_compression_ratio: Decimal
    stage_compression_ratio: Decimal
    stages: tuple[CompressionStage, ...]


def recommend_number_of_stages(
    suction_pressure_bar: Decimal,
    discharge_pressure_bar: Decimal,
    maximum_stage_ratio: Decimal = Decimal("3.5"),
) -> int:
    """Recommend the minimum number of stages within a stage-ratio limit."""

    if suction_pressure_bar <= 0:
        raise InvalidStagingInputError("Suction absolute pressure must be greater than zero.")

    if discharge_pressure_bar <= suction_pressure_bar:
        raise InvalidStagingInputError("Discharge pressure must be greater than suction pressure.")

    if maximum_stage_ratio <= 1:
        raise InvalidStagingInputError("Maximum stage compression ratio must be greater than one.")

    overall_ratio = discharge_pressure_bar / suction_pressure_bar

    stages = 1

    while True:
        stage_ratio = Decimal(str(float(overall_ratio) ** (1.0 / stages)))

        if stage_ratio <= maximum_stage_ratio:
            return stages

        stages += 1


def calculate_equal_staging(
    suction_pressure_bar: Decimal,
    discharge_pressure_bar: Decimal,
    number_of_stages: int,
) -> StagingResult:
    """Calculate equal compression-ratio staging and interstage pressures."""

    if suction_pressure_bar <= 0:
        raise InvalidStagingInputError("Suction absolute pressure must be greater than zero.")

    if discharge_pressure_bar <= suction_pressure_bar:
        raise InvalidStagingInputError("Discharge pressure must be greater than suction pressure.")

    if number_of_stages < 1:
        raise InvalidStagingInputError("Number of compression stages must be at least one.")

    with localcontext() as context:
        context.prec = 28

        overall_ratio = discharge_pressure_bar / suction_pressure_bar

        stage_ratio = Decimal(str(float(overall_ratio) ** (1.0 / number_of_stages)))

        stages: list[CompressionStage] = []

        inlet_pressure = suction_pressure_bar

        for stage_number in range(1, number_of_stages + 1):
            if stage_number == number_of_stages:
                outlet_pressure = discharge_pressure_bar
            else:
                outlet_pressure = inlet_pressure * stage_ratio

            stage_ratio_actual = outlet_pressure / inlet_pressure

            stages.append(
                CompressionStage(
                    stage_number=stage_number,
                    inlet_pressure_bar=inlet_pressure,
                    outlet_pressure_bar=outlet_pressure,
                    compression_ratio=stage_ratio_actual,
                )
            )

            inlet_pressure = outlet_pressure

    return StagingResult(
        number_of_stages=number_of_stages,
        overall_compression_ratio=overall_ratio,
        stage_compression_ratio=stage_ratio,
        stages=tuple(stages),
    )
