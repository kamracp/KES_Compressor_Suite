from dataclasses import dataclass
from enum import StrEnum


class AdvancedEngineeringModule(StrEnum):
    """Advanced compressor engineering modules available in the platform."""

    GAS_PROPERTIES = "GAS_PROPERTIES"
    COMPRESSION_THERMODYNAMICS = "COMPRESSION_THERMODYNAMICS"
    RECIPROCATING_ENGINEERING = "RECIPROCATING_ENGINEERING"
    CENTRIFUGAL_ENGINEERING = "CENTRIFUGAL_ENGINEERING"
    PERFORMANCE_MAP = "PERFORMANCE_MAP"
    SURGE_ANALYSIS = "SURGE_ANALYSIS"
    ROD_LOAD = "ROD_LOAD"
    DRIVER_AND_POWER = "DRIVER_AND_POWER"
    COOLING_AND_INTERCOOLING = "COOLING_AND_INTERCOOLING"
    STANDARDS_COMPLIANCE = "STANDARDS_COMPLIANCE"


class AdvancedApplicationType(StrEnum):
    """Application classes that may require advanced engineering."""

    FACTORY_COMPRESSED_AIR = "FACTORY_COMPRESSED_AIR"
    HIGH_PRESSURE_AIR = "HIGH_PRESSURE_AIR"
    PROCESS_GAS = "PROCESS_GAS"
    RECIPROCATING_PROCESS_COMPRESSOR = "RECIPROCATING_PROCESS_COMPRESSOR"
    CENTRIFUGAL_PROCESS_COMPRESSOR = "CENTRIFUGAL_PROCESS_COMPRESSOR"


@dataclass(frozen=True, slots=True)
class AdvancedModuleDefinition:
    """Definition of one advanced engineering capability."""

    module: AdvancedEngineeringModule
    title: str
    description: str

    source_package: str

    applicable_to: tuple[AdvancedApplicationType, ...]

    enabled: bool = True


def get_advanced_engineering_registry() -> tuple[AdvancedModuleDefinition, ...]:
    """Return the platform advanced-engineering capability registry."""

    return (
        AdvancedModuleDefinition(
            module=AdvancedEngineeringModule.GAS_PROPERTIES,
            title="Gas Properties",
            description=(
                "Gas composition, density, pseudocritical properties, "
                "reduced properties, compressibility factor, and flow basis."
            ),
            source_package="app.domain.gas",
            applicable_to=(
                AdvancedApplicationType.PROCESS_GAS,
                AdvancedApplicationType.HIGH_PRESSURE_AIR,
                AdvancedApplicationType.RECIPROCATING_PROCESS_COMPRESSOR,
                AdvancedApplicationType.CENTRIFUGAL_PROCESS_COMPRESSOR,
            ),
        ),
        AdvancedModuleDefinition(
            module=AdvancedEngineeringModule.COMPRESSION_THERMODYNAMICS,
            title="Compression Thermodynamics",
            description=(
                "Compression ratio, discharge temperature, power, staging, "
                "cooling, driver, and engineering validation."
            ),
            source_package="app.domain.compression",
            applicable_to=(
                AdvancedApplicationType.FACTORY_COMPRESSED_AIR,
                AdvancedApplicationType.HIGH_PRESSURE_AIR,
                AdvancedApplicationType.PROCESS_GAS,
                AdvancedApplicationType.RECIPROCATING_PROCESS_COMPRESSOR,
                AdvancedApplicationType.CENTRIFUGAL_PROCESS_COMPRESSOR,
            ),
        ),
        AdvancedModuleDefinition(
            module=AdvancedEngineeringModule.RECIPROCATING_ENGINEERING,
            title="Reciprocating Compressor Engineering",
            description=(
                "Displacement, capacity, volumetric efficiency, rod load, "
                "and reciprocating compressor performance."
            ),
            source_package="app.domain.reciprocating",
            applicable_to=(
                AdvancedApplicationType.HIGH_PRESSURE_AIR,
                AdvancedApplicationType.PROCESS_GAS,
                AdvancedApplicationType.RECIPROCATING_PROCESS_COMPRESSOR,
            ),
        ),
        AdvancedModuleDefinition(
            module=AdvancedEngineeringModule.CENTRIFUGAL_ENGINEERING,
            title="Centrifugal Compressor Engineering",
            description=(
                "Polytropic head, impeller performance, power, performance "
                "maps, and centrifugal compressor operating analysis."
            ),
            source_package="app.domain.centrifugal",
            applicable_to=(
                AdvancedApplicationType.PROCESS_GAS,
                AdvancedApplicationType.CENTRIFUGAL_PROCESS_COMPRESSOR,
            ),
        ),
        AdvancedModuleDefinition(
            module=AdvancedEngineeringModule.PERFORMANCE_MAP,
            title="Performance Map",
            description=(
                "Advanced compressor operating-map analysis and operating envelope evaluation."
            ),
            source_package="app.domain.centrifugal.performance_map",
            applicable_to=(AdvancedApplicationType.CENTRIFUGAL_PROCESS_COMPRESSOR,),
        ),
        AdvancedModuleDefinition(
            module=AdvancedEngineeringModule.SURGE_ANALYSIS,
            title="Surge Analysis",
            description=("Centrifugal compressor surge margin and operating stability assessment."),
            source_package="app.domain.centrifugal.surge",
            applicable_to=(AdvancedApplicationType.CENTRIFUGAL_PROCESS_COMPRESSOR,),
        ),
        AdvancedModuleDefinition(
            module=AdvancedEngineeringModule.ROD_LOAD,
            title="Rod Load Analysis",
            description=(
                "Reciprocating compressor rod-load assessment for mechanical operating limits."
            ),
            source_package="app.domain.reciprocating.rod_load",
            applicable_to=(AdvancedApplicationType.RECIPROCATING_PROCESS_COMPRESSOR,),
        ),
        AdvancedModuleDefinition(
            module=AdvancedEngineeringModule.DRIVER_AND_POWER,
            title="Driver and Power Engineering",
            description=(
                "Compressor power requirement, driver sizing, and operating power assessment."
            ),
            source_package="app.domain.compression.driver",
            applicable_to=(
                AdvancedApplicationType.FACTORY_COMPRESSED_AIR,
                AdvancedApplicationType.HIGH_PRESSURE_AIR,
                AdvancedApplicationType.PROCESS_GAS,
                AdvancedApplicationType.RECIPROCATING_PROCESS_COMPRESSOR,
                AdvancedApplicationType.CENTRIFUGAL_PROCESS_COMPRESSOR,
            ),
        ),
        AdvancedModuleDefinition(
            module=AdvancedEngineeringModule.COOLING_AND_INTERCOOLING,
            title="Cooling and Intercooling",
            description=("Interstage cooling and compression heat-management engineering."),
            source_package="app.domain.compression.cooling",
            applicable_to=(
                AdvancedApplicationType.HIGH_PRESSURE_AIR,
                AdvancedApplicationType.PROCESS_GAS,
                AdvancedApplicationType.RECIPROCATING_PROCESS_COMPRESSOR,
                AdvancedApplicationType.CENTRIFUGAL_PROCESS_COMPRESSOR,
            ),
        ),
        AdvancedModuleDefinition(
            module=AdvancedEngineeringModule.STANDARDS_COMPLIANCE,
            title="Standards and Compliance",
            description=("Engineering standards registry and validation framework."),
            source_package="app.domain.compliance",
            applicable_to=(
                AdvancedApplicationType.FACTORY_COMPRESSED_AIR,
                AdvancedApplicationType.HIGH_PRESSURE_AIR,
                AdvancedApplicationType.PROCESS_GAS,
                AdvancedApplicationType.RECIPROCATING_PROCESS_COMPRESSOR,
                AdvancedApplicationType.CENTRIFUGAL_PROCESS_COMPRESSOR,
            ),
        ),
    )
