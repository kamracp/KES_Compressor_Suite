from dataclasses import dataclass
from decimal import Decimal

from app.domain.compressed_air.advanced.advanced_registry import (
    AdvancedApplicationType,
    AdvancedEngineeringModule,
    AdvancedModuleDefinition,
    get_advanced_engineering_registry,
)
from app.domain.compressed_air.station.station_models import CompressorTechnology


@dataclass(frozen=True, slots=True)
class AdvancedRoutingInput:
    """Input used to determine relevant advanced engineering modules."""

    application_type: AdvancedApplicationType

    compressor_technology: CompressorTechnology | None = None

    discharge_pressure_bar_g: Decimal | None = None

    process_gas_service: bool = False
    high_pressure_service: bool = False

    standards_review_required: bool = False


@dataclass(frozen=True, slots=True)
class AdvancedRoutingResult:
    """Recommended advanced engineering modules for one application."""

    application_type: AdvancedApplicationType

    recommended_modules: tuple[AdvancedModuleDefinition, ...]

    advanced_engineering_required: bool

    reasons: tuple[str, ...]


def route_advanced_engineering(
    inputs: AdvancedRoutingInput,
) -> AdvancedRoutingResult:
    """Recommend advanced engineering capabilities for an application."""

    registry = get_advanced_engineering_registry()

    requested_modules: set[AdvancedEngineeringModule] = set()
    reasons: list[str] = []

    if inputs.application_type == AdvancedApplicationType.FACTORY_COMPRESSED_AIR:
        requested_modules.add(AdvancedEngineeringModule.COMPRESSION_THERMODYNAMICS)
        requested_modules.add(AdvancedEngineeringModule.DRIVER_AND_POWER)

        reasons.append(
            "Factory compressed-air systems may use advanced thermodynamic "
            "and driver analysis when detailed compressor verification is required."
        )

    if inputs.process_gas_service:
        requested_modules.update(
            {
                AdvancedEngineeringModule.GAS_PROPERTIES,
                AdvancedEngineeringModule.COMPRESSION_THERMODYNAMICS,
                AdvancedEngineeringModule.DRIVER_AND_POWER,
                AdvancedEngineeringModule.COOLING_AND_INTERCOOLING,
            }
        )

        reasons.append("Process-gas service requires gas-property and compression analysis.")

    if inputs.high_pressure_service:
        requested_modules.update(
            {
                AdvancedEngineeringModule.GAS_PROPERTIES,
                AdvancedEngineeringModule.COMPRESSION_THERMODYNAMICS,
                AdvancedEngineeringModule.COOLING_AND_INTERCOOLING,
                AdvancedEngineeringModule.DRIVER_AND_POWER,
            }
        )

        reasons.append("High-pressure service requires advanced compression and cooling review.")

    if inputs.compressor_technology == CompressorTechnology.RECIPROCATING:
        requested_modules.update(
            {
                AdvancedEngineeringModule.RECIPROCATING_ENGINEERING,
                AdvancedEngineeringModule.ROD_LOAD,
                AdvancedEngineeringModule.COMPRESSION_THERMODYNAMICS,
            }
        )

        reasons.append(
            "Reciprocating compressor technology requires displacement, "
            "volumetric-efficiency, and rod-load analysis."
        )

    if inputs.compressor_technology == CompressorTechnology.CENTRIFUGAL:
        requested_modules.update(
            {
                AdvancedEngineeringModule.CENTRIFUGAL_ENGINEERING,
                AdvancedEngineeringModule.PERFORMANCE_MAP,
                AdvancedEngineeringModule.SURGE_ANALYSIS,
                AdvancedEngineeringModule.COMPRESSION_THERMODYNAMICS,
            }
        )

        reasons.append(
            "Centrifugal compressor technology requires performance-map and surge-margin analysis."
        )

    if inputs.standards_review_required:
        requested_modules.add(AdvancedEngineeringModule.STANDARDS_COMPLIANCE)

        reasons.append("Formal engineering standards review has been requested.")

    if inputs.discharge_pressure_bar_g is not None and inputs.discharge_pressure_bar_g >= Decimal(
        "10"
    ):
        requested_modules.update(
            {
                AdvancedEngineeringModule.COMPRESSION_THERMODYNAMICS,
                AdvancedEngineeringModule.COOLING_AND_INTERCOOLING,
            }
        )

        reasons.append("Discharge pressure is high enough to justify advanced compression review.")

    recommended_modules = tuple(
        item for item in registry if item.module in requested_modules and item.enabled
    )

    return AdvancedRoutingResult(
        application_type=inputs.application_type,
        recommended_modules=recommended_modules,
        advanced_engineering_required=bool(recommended_modules),
        reasons=tuple(reasons),
    )
