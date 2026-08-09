from decimal import Decimal

from app.domain.compressed_air.advanced.advanced_registry import (
    AdvancedApplicationType,
    AdvancedEngineeringModule,
)
from app.domain.compressed_air.advanced.advanced_summary import (
    build_advanced_engineering_summary,
    has_advanced_module,
    has_applicable_standard,
)
from app.domain.compressed_air.advanced.application_router import (
    AdvancedRoutingInput,
)
from app.domain.compressed_air.advanced.standards_mapping import (
    EngineeringStandard,
)
from app.domain.compressed_air.station.station_models import (
    CompressorTechnology,
)


def test_reciprocating_process_summary() -> None:
    summary = build_advanced_engineering_summary(
        AdvancedRoutingInput(
            application_type=(AdvancedApplicationType.RECIPROCATING_PROCESS_COMPRESSOR),
            compressor_technology=CompressorTechnology.RECIPROCATING,
            discharge_pressure_bar_g=Decimal("25"),
            process_gas_service=True,
            high_pressure_service=True,
            standards_review_required=True,
        )
    )

    assert summary.advanced_engineering_required is True
    assert summary.standards_review_required is True

    assert (
        AdvancedEngineeringModule.RECIPROCATING_ENGINEERING.value
        in summary.recommended_module_codes
    )

    assert AdvancedEngineeringModule.ROD_LOAD.value in summary.recommended_module_codes

    assert EngineeringStandard.API_618.value in (summary.applicable_standard_codes)

    assert EngineeringStandard.ASME_PTC_10.value in (summary.applicable_standard_codes)

    assert EngineeringStandard.GPSA_ENGINEERING_DATA_BOOK.value in (
        summary.applicable_standard_codes
    )

    assert summary.formal_compliance_claim_available is False


def test_centrifugal_summary_contains_map_and_surge() -> None:
    summary = build_advanced_engineering_summary(
        AdvancedRoutingInput(
            application_type=(AdvancedApplicationType.CENTRIFUGAL_PROCESS_COMPRESSOR),
            compressor_technology=CompressorTechnology.CENTRIFUGAL,
            process_gas_service=True,
        )
    )

    assert has_advanced_module(
        summary,
        AdvancedEngineeringModule.CENTRIFUGAL_ENGINEERING,
    )

    assert has_advanced_module(
        summary,
        AdvancedEngineeringModule.PERFORMANCE_MAP,
    )

    assert has_advanced_module(
        summary,
        AdvancedEngineeringModule.SURGE_ANALYSIS,
    )

    assert has_applicable_standard(
        summary,
        EngineeringStandard.API_617,
    )


def test_factory_air_summary_keeps_advanced_layer_available() -> None:
    summary = build_advanced_engineering_summary(
        AdvancedRoutingInput(
            application_type=AdvancedApplicationType.FACTORY_COMPRESSED_AIR,
        )
    )

    assert summary.advanced_engineering_required is True

    assert has_advanced_module(
        summary,
        AdvancedEngineeringModule.COMPRESSION_THERMODYNAMICS,
    )

    assert has_advanced_module(
        summary,
        AdvancedEngineeringModule.DRIVER_AND_POWER,
    )

    assert has_applicable_standard(
        summary,
        EngineeringStandard.ASME_PTC_10,
    )

    assert not has_applicable_standard(
        summary,
        EngineeringStandard.API_617,
    )

    assert not has_applicable_standard(
        summary,
        EngineeringStandard.API_618,
    )


def test_high_pressure_air_summary_adds_advanced_compression_modules() -> None:
    summary = build_advanced_engineering_summary(
        AdvancedRoutingInput(
            application_type=AdvancedApplicationType.HIGH_PRESSURE_AIR,
            discharge_pressure_bar_g=Decimal("30"),
            high_pressure_service=True,
        )
    )

    assert has_advanced_module(
        summary,
        AdvancedEngineeringModule.GAS_PROPERTIES,
    )

    assert has_advanced_module(
        summary,
        AdvancedEngineeringModule.COMPRESSION_THERMODYNAMICS,
    )

    assert has_advanced_module(
        summary,
        AdvancedEngineeringModule.COOLING_AND_INTERCOOLING,
    )

    assert has_advanced_module(
        summary,
        AdvancedEngineeringModule.DRIVER_AND_POWER,
    )


def test_requested_rod_load_can_trigger_api_618_review() -> None:
    summary = build_advanced_engineering_summary(
        AdvancedRoutingInput(
            application_type=AdvancedApplicationType.FACTORY_COMPRESSED_AIR,
            compressor_technology=CompressorTechnology.RECIPROCATING,
        )
    )

    assert EngineeringStandard.API_618.value in summary.review_required_standard_codes


def test_formal_compliance_claim_remains_disabled() -> None:
    summary = build_advanced_engineering_summary(
        AdvancedRoutingInput(
            application_type=(AdvancedApplicationType.CENTRIFUGAL_PROCESS_COMPRESSOR),
            compressor_technology=CompressorTechnology.CENTRIFUGAL,
            standards_review_required=True,
        )
    )

    assert summary.formal_compliance_claim_available is False

    assert all(
        item.formal_compliance_claim_allowed is False for item in summary.compliance.assessments
    )
