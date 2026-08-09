from app.domain.compressed_air.advanced.advanced_registry import (
    AdvancedApplicationType,
    AdvancedEngineeringModule,
)
from app.domain.compressed_air.advanced.standards_mapping import (
    EngineeringStandard,
    StandardReferenceType,
    get_standards_for_application,
    get_standards_for_module,
    get_standards_mapping,
)


def test_registry_contains_four_core_references() -> None:
    registry = get_standards_mapping()

    assert len(registry) == 4

    standards = {item.standard for item in registry}

    assert EngineeringStandard.API_617 in standards
    assert EngineeringStandard.API_618 in standards
    assert EngineeringStandard.ASME_PTC_10 in standards
    assert EngineeringStandard.GPSA_ENGINEERING_DATA_BOOK in standards


def test_api_617_maps_to_centrifugal_engineering() -> None:
    mappings = get_standards_for_application(AdvancedApplicationType.CENTRIFUGAL_PROCESS_COMPRESSOR)

    api_617 = next(item for item in mappings if item.standard == EngineeringStandard.API_617)

    assert api_617.reference_type == StandardReferenceType.DESIGN_STANDARD

    assert AdvancedEngineeringModule.CENTRIFUGAL_ENGINEERING in api_617.related_modules

    assert AdvancedEngineeringModule.PERFORMANCE_MAP in api_617.related_modules
    assert AdvancedEngineeringModule.SURGE_ANALYSIS in api_617.related_modules


def test_api_618_maps_to_reciprocating_engineering() -> None:
    mappings = get_standards_for_application(
        AdvancedApplicationType.RECIPROCATING_PROCESS_COMPRESSOR
    )

    api_618 = next(item for item in mappings if item.standard == EngineeringStandard.API_618)

    assert api_618.reference_type == StandardReferenceType.DESIGN_STANDARD

    assert AdvancedEngineeringModule.RECIPROCATING_ENGINEERING in api_618.related_modules

    assert AdvancedEngineeringModule.ROD_LOAD in api_618.related_modules
    assert AdvancedEngineeringModule.COMPRESSION_THERMODYNAMICS in api_618.related_modules


def test_asme_ptc_10_maps_to_performance_testing() -> None:
    registry = get_standards_mapping()

    ptc_10 = next(item for item in registry if item.standard == EngineeringStandard.ASME_PTC_10)

    assert ptc_10.reference_type == StandardReferenceType.PERFORMANCE_TEST_CODE

    assert AdvancedEngineeringModule.DRIVER_AND_POWER in ptc_10.related_modules
    assert AdvancedEngineeringModule.STANDARDS_COMPLIANCE in ptc_10.related_modules


def test_gpsa_maps_to_gas_properties_and_compression() -> None:
    registry = get_standards_mapping()

    gpsa = next(
        item for item in registry if item.standard == EngineeringStandard.GPSA_ENGINEERING_DATA_BOOK
    )

    assert gpsa.reference_type == StandardReferenceType.ENGINEERING_REFERENCE

    assert AdvancedEngineeringModule.GAS_PROPERTIES in gpsa.related_modules
    assert AdvancedEngineeringModule.COMPRESSION_THERMODYNAMICS in gpsa.related_modules

    assert AdvancedEngineeringModule.COOLING_AND_INTERCOOLING in gpsa.related_modules


def test_factory_air_maps_to_ptc_10_but_not_api_617_or_api_618() -> None:
    mappings = get_standards_for_application(AdvancedApplicationType.FACTORY_COMPRESSED_AIR)

    standards = {item.standard for item in mappings}

    assert EngineeringStandard.ASME_PTC_10 in standards
    assert EngineeringStandard.API_617 not in standards
    assert EngineeringStandard.API_618 not in standards


def test_rod_load_module_maps_to_api_618() -> None:
    mappings = get_standards_for_module(AdvancedEngineeringModule.ROD_LOAD)

    standards = {item.standard for item in mappings}

    assert EngineeringStandard.API_618 in standards
    assert EngineeringStandard.API_617 not in standards


def test_surge_module_maps_to_api_617() -> None:
    mappings = get_standards_for_module(AdvancedEngineeringModule.SURGE_ANALYSIS)

    standards = {item.standard for item in mappings}

    assert EngineeringStandard.API_617 in standards
    assert EngineeringStandard.API_618 not in standards


def test_clause_rules_are_not_claimed_as_implemented() -> None:
    registry = get_standards_mapping()

    assert all(item.clause_rules_implemented is False for item in registry)
