from dataclasses import dataclass
from enum import StrEnum

from app.domain.compressed_air.advanced.advanced_registry import (
    AdvancedApplicationType,
    AdvancedEngineeringModule,
)


class EngineeringStandard(StrEnum):
    """Engineering standards and references used by advanced compressor modules."""

    API_617 = "API_617"
    API_618 = "API_618"
    ASME_PTC_10 = "ASME_PTC_10"
    GPSA_ENGINEERING_DATA_BOOK = "GPSA_ENGINEERING_DATA_BOOK"


class StandardReferenceType(StrEnum):
    """Nature of a mapped engineering reference."""

    DESIGN_STANDARD = "DESIGN_STANDARD"
    PERFORMANCE_TEST_CODE = "PERFORMANCE_TEST_CODE"
    ENGINEERING_REFERENCE = "ENGINEERING_REFERENCE"


@dataclass(frozen=True, slots=True)
class StandardMapping:
    """Applicability mapping between a reference and platform capability."""

    standard: EngineeringStandard
    title: str
    reference_type: StandardReferenceType

    applicable_applications: tuple[AdvancedApplicationType, ...]
    related_modules: tuple[AdvancedEngineeringModule, ...]

    purpose: str

    clause_rules_implemented: bool = False


def get_standards_mapping() -> tuple[StandardMapping, ...]:
    """Return the advanced compressor standards applicability registry."""

    return (
        StandardMapping(
            standard=EngineeringStandard.API_617,
            title=("API 617 - Axial and Centrifugal Compressors and Expander-compressors"),
            reference_type=StandardReferenceType.DESIGN_STANDARD,
            applicable_applications=(
                AdvancedApplicationType.CENTRIFUGAL_PROCESS_COMPRESSOR,
                AdvancedApplicationType.PROCESS_GAS,
            ),
            related_modules=(
                AdvancedEngineeringModule.CENTRIFUGAL_ENGINEERING,
                AdvancedEngineeringModule.PERFORMANCE_MAP,
                AdvancedEngineeringModule.SURGE_ANALYSIS,
                AdvancedEngineeringModule.DRIVER_AND_POWER,
                AdvancedEngineeringModule.STANDARDS_COMPLIANCE,
            ),
            purpose=(
                "Map centrifugal and axial process-compressor engineering "
                "checks to the applicable API machinery standard."
            ),
        ),
        StandardMapping(
            standard=EngineeringStandard.API_618,
            title=(
                "API 618 - Reciprocating Compressors for Petroleum, "
                "Chemical, and Gas Industry Services"
            ),
            reference_type=StandardReferenceType.DESIGN_STANDARD,
            applicable_applications=(
                AdvancedApplicationType.RECIPROCATING_PROCESS_COMPRESSOR,
                AdvancedApplicationType.PROCESS_GAS,
                AdvancedApplicationType.HIGH_PRESSURE_AIR,
            ),
            related_modules=(
                AdvancedEngineeringModule.RECIPROCATING_ENGINEERING,
                AdvancedEngineeringModule.ROD_LOAD,
                AdvancedEngineeringModule.COMPRESSION_THERMODYNAMICS,
                AdvancedEngineeringModule.COOLING_AND_INTERCOOLING,
                AdvancedEngineeringModule.DRIVER_AND_POWER,
                AdvancedEngineeringModule.STANDARDS_COMPLIANCE,
            ),
            purpose=(
                "Map reciprocating compressor engineering and mechanical "
                "checks to the applicable API machinery standard."
            ),
        ),
        StandardMapping(
            standard=EngineeringStandard.ASME_PTC_10,
            title="ASME PTC 10 - Performance Test Code on Compressors and Exhausters",
            reference_type=StandardReferenceType.PERFORMANCE_TEST_CODE,
            applicable_applications=(
                AdvancedApplicationType.FACTORY_COMPRESSED_AIR,
                AdvancedApplicationType.HIGH_PRESSURE_AIR,
                AdvancedApplicationType.PROCESS_GAS,
                AdvancedApplicationType.RECIPROCATING_PROCESS_COMPRESSOR,
                AdvancedApplicationType.CENTRIFUGAL_PROCESS_COMPRESSOR,
            ),
            related_modules=(
                AdvancedEngineeringModule.COMPRESSION_THERMODYNAMICS,
                AdvancedEngineeringModule.DRIVER_AND_POWER,
                AdvancedEngineeringModule.CENTRIFUGAL_ENGINEERING,
                AdvancedEngineeringModule.RECIPROCATING_ENGINEERING,
                AdvancedEngineeringModule.STANDARDS_COMPLIANCE,
            ),
            purpose=(
                "Provide the standards mapping point for compressor "
                "performance-test and acceptance calculations."
            ),
        ),
        StandardMapping(
            standard=EngineeringStandard.GPSA_ENGINEERING_DATA_BOOK,
            title="GPSA Engineering Data Book",
            reference_type=StandardReferenceType.ENGINEERING_REFERENCE,
            applicable_applications=(
                AdvancedApplicationType.PROCESS_GAS,
                AdvancedApplicationType.HIGH_PRESSURE_AIR,
                AdvancedApplicationType.RECIPROCATING_PROCESS_COMPRESSOR,
                AdvancedApplicationType.CENTRIFUGAL_PROCESS_COMPRESSOR,
            ),
            related_modules=(
                AdvancedEngineeringModule.GAS_PROPERTIES,
                AdvancedEngineeringModule.COMPRESSION_THERMODYNAMICS,
                AdvancedEngineeringModule.COOLING_AND_INTERCOOLING,
                AdvancedEngineeringModule.DRIVER_AND_POWER,
            ),
            purpose=(
                "Provide engineering-reference mapping for gas properties, "
                "compression calculations, and process-gas design inputs."
            ),
        ),
    )


def get_standards_for_application(
    application_type: AdvancedApplicationType,
) -> tuple[StandardMapping, ...]:
    """Return standards mapped to one advanced application type."""

    return tuple(
        mapping
        for mapping in get_standards_mapping()
        if application_type in mapping.applicable_applications
    )


def get_standards_for_module(
    module: AdvancedEngineeringModule,
) -> tuple[StandardMapping, ...]:
    """Return standards mapped to one advanced engineering module."""

    return tuple(
        mapping for mapping in get_standards_mapping() if module in mapping.related_modules
    )
