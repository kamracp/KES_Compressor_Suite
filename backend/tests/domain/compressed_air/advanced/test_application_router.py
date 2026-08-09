from decimal import Decimal

from app.domain.compressed_air.advanced.advanced_registry import (
    AdvancedApplicationType,
    AdvancedEngineeringModule,
)
from app.domain.compressed_air.advanced.application_router import (
    AdvancedRoutingInput,
    route_advanced_engineering,
)
from app.domain.compressed_air.station.station_models import (
    CompressorTechnology,
)


def module_set(result) -> set[AdvancedEngineeringModule]:
    return {item.module for item in result.recommended_modules}


def test_factory_compressed_air_routes_core_advanced_modules() -> None:
    result = route_advanced_engineering(
        AdvancedRoutingInput(
            application_type=AdvancedApplicationType.FACTORY_COMPRESSED_AIR,
        )
    )

    modules = module_set(result)

    assert AdvancedEngineeringModule.COMPRESSION_THERMODYNAMICS in modules
    assert AdvancedEngineeringModule.DRIVER_AND_POWER in modules
    assert result.advanced_engineering_required is True


def test_high_pressure_reciprocating_routes_deep_engineering() -> None:
    result = route_advanced_engineering(
        AdvancedRoutingInput(
            application_type=AdvancedApplicationType.HIGH_PRESSURE_AIR,
            compressor_technology=CompressorTechnology.RECIPROCATING,
            discharge_pressure_bar_g=Decimal("30"),
            high_pressure_service=True,
            standards_review_required=True,
        )
    )

    modules = module_set(result)

    assert AdvancedEngineeringModule.GAS_PROPERTIES in modules
    assert AdvancedEngineeringModule.COMPRESSION_THERMODYNAMICS in modules
    assert AdvancedEngineeringModule.RECIPROCATING_ENGINEERING in modules
    assert AdvancedEngineeringModule.ROD_LOAD in modules
    assert AdvancedEngineeringModule.COOLING_AND_INTERCOOLING in modules
    assert AdvancedEngineeringModule.DRIVER_AND_POWER in modules
    assert AdvancedEngineeringModule.STANDARDS_COMPLIANCE in modules

    assert result.advanced_engineering_required is True
    assert len(result.reasons) >= 3


def test_process_gas_routes_gas_and_thermodynamic_modules() -> None:
    result = route_advanced_engineering(
        AdvancedRoutingInput(
            application_type=AdvancedApplicationType.PROCESS_GAS,
            process_gas_service=True,
        )
    )

    modules = module_set(result)

    assert AdvancedEngineeringModule.GAS_PROPERTIES in modules
    assert AdvancedEngineeringModule.COMPRESSION_THERMODYNAMICS in modules
    assert AdvancedEngineeringModule.DRIVER_AND_POWER in modules
    assert AdvancedEngineeringModule.COOLING_AND_INTERCOOLING in modules


def test_centrifugal_routes_performance_and_surge_modules() -> None:
    result = route_advanced_engineering(
        AdvancedRoutingInput(
            application_type=(AdvancedApplicationType.CENTRIFUGAL_PROCESS_COMPRESSOR),
            compressor_technology=CompressorTechnology.CENTRIFUGAL,
            process_gas_service=True,
        )
    )

    modules = module_set(result)

    assert AdvancedEngineeringModule.CENTRIFUGAL_ENGINEERING in modules
    assert AdvancedEngineeringModule.PERFORMANCE_MAP in modules
    assert AdvancedEngineeringModule.SURGE_ANALYSIS in modules
    assert AdvancedEngineeringModule.COMPRESSION_THERMODYNAMICS in modules
    assert AdvancedEngineeringModule.GAS_PROPERTIES in modules


def test_standards_review_adds_compliance_module() -> None:
    result = route_advanced_engineering(
        AdvancedRoutingInput(
            application_type=AdvancedApplicationType.FACTORY_COMPRESSED_AIR,
            standards_review_required=True,
        )
    )

    modules = module_set(result)

    assert AdvancedEngineeringModule.STANDARDS_COMPLIANCE in modules


def test_pressure_above_threshold_adds_advanced_compression_review() -> None:
    result = route_advanced_engineering(
        AdvancedRoutingInput(
            application_type=AdvancedApplicationType.HIGH_PRESSURE_AIR,
            discharge_pressure_bar_g=Decimal("12"),
        )
    )

    modules = module_set(result)

    assert AdvancedEngineeringModule.COMPRESSION_THERMODYNAMICS in modules
    assert AdvancedEngineeringModule.COOLING_AND_INTERCOOLING in modules


def test_disabled_or_irrelevant_modules_are_not_added() -> None:
    result = route_advanced_engineering(
        AdvancedRoutingInput(
            application_type=AdvancedApplicationType.FACTORY_COMPRESSED_AIR,
        )
    )

    modules = module_set(result)

    assert AdvancedEngineeringModule.ROD_LOAD not in modules
    assert AdvancedEngineeringModule.SURGE_ANALYSIS not in modules
    assert AdvancedEngineeringModule.PERFORMANCE_MAP not in modules
