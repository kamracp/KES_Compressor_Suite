from dataclasses import dataclass
from decimal import Decimal

from app.domain.compressed_air.distribution.network_models import (
    CompressedAirNetwork,
    NetworkPath,
)
from app.domain.compressed_air.distribution.path_solver import (
    NetworkPathResult,
    solve_network_path,
)


class InvalidNetworkSolverInputError(ValueError):
    """Raised when compressed-air network solver inputs are invalid."""


@dataclass(frozen=True, slots=True)
class NetworkHydraulicResult:
    """Hydraulic assessment of a compressed-air distribution network."""

    network_code: str

    path_results: tuple[NetworkPathResult, ...]

    worst_pressure_path_code: str
    highest_pressure_drop_path_code: str

    minimum_destination_pressure_bar_g: Decimal
    maximum_path_pressure_drop_bar: Decimal

    pressure_deficient_path_codes: tuple[str, ...]

    total_paths: int
    adequate_paths: int
    deficient_paths: int

    network_pressure_is_adequate: bool


def solve_network(
    *,
    network: CompressedAirNetwork,
    paths: tuple[NetworkPath, ...],
    air_density_kg_per_m3: Decimal,
    darcy_friction_factor: Decimal,
) -> NetworkHydraulicResult:
    """Solve all defined compressed-air network paths."""

    if not paths:
        raise InvalidNetworkSolverInputError("At least one network path is required.")

    path_codes = tuple(path.path_code for path in paths)

    if len(set(path_codes)) != len(path_codes):
        raise InvalidNetworkSolverInputError("Network path codes must be unique.")

    path_results = tuple(
        solve_network_path(
            network=network,
            path=path,
            air_density_kg_per_m3=air_density_kg_per_m3,
            darcy_friction_factor=darcy_friction_factor,
        )
        for path in paths
    )

    worst_pressure_result = min(
        path_results,
        key=lambda result: result.destination_pressure_bar_g,
    )

    highest_pressure_drop_result = max(
        path_results,
        key=lambda result: result.total_pressure_drop_bar,
    )

    pressure_deficient_path_codes = tuple(
        result.path_code
        for result in path_results
        if result.destination_pressure_is_adequate is False
    )

    adequate_paths = sum(
        1 for result in path_results if result.destination_pressure_is_adequate is True
    )

    deficient_paths = len(pressure_deficient_path_codes)

    network_pressure_is_adequate = deficient_paths == 0

    return NetworkHydraulicResult(
        network_code=network.network_code,
        path_results=path_results,
        worst_pressure_path_code=worst_pressure_result.path_code,
        highest_pressure_drop_path_code=(highest_pressure_drop_result.path_code),
        minimum_destination_pressure_bar_g=(worst_pressure_result.destination_pressure_bar_g),
        maximum_path_pressure_drop_bar=(highest_pressure_drop_result.total_pressure_drop_bar),
        pressure_deficient_path_codes=pressure_deficient_path_codes,
        total_paths=len(path_results),
        adequate_paths=adequate_paths,
        deficient_paths=deficient_paths,
        network_pressure_is_adequate=network_pressure_is_adequate,
    )
