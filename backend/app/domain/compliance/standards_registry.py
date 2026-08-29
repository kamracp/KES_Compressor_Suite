from dataclasses import dataclass
from enum import StrEnum


class StandardAuthority(StrEnum):
    API = "API"
    ASME = "ASME"
    GPSA = "GPSA"
    ISO = "ISO"


class StandardApplicability(StrEnum):
    CENTRIFUGAL = "CENTRIFUGAL"
    RECIPROCATING = "RECIPROCATING"
    ROTARY_SCREW = "ROTARY_SCREW"
    PERFORMANCE_TESTING = "PERFORMANCE_TESTING"
    GAS_PROCESSING_DATA = "GAS_PROCESSING_DATA"


class StandardVerificationStatus(StrEnum):
    OFFICIAL_SOURCE_VERIFIED = "OFFICIAL_SOURCE_VERIFIED"
    CLAUSE_MAPPING_PENDING = "CLAUSE_MAPPING_PENDING"


@dataclass(frozen=True, slots=True)
class EngineeringStandard:
    """Reference metadata for a compressor engineering standard."""

    standard_id: str
    authority: StandardAuthority
    title: str
    edition: str
    publication_date: str | None
    applicability: tuple[StandardApplicability, ...]
    verification_status: StandardVerificationStatus
    notes: str


API_617 = EngineeringStandard(
    standard_id="API-617",
    authority=StandardAuthority.API,
    title=(
        "Axial and Centrifugal Compressors and Expander-compressors "
        "for Petroleum, Chemical and Gas Industry Services"
    ),
    edition="9th Edition",
    publication_date="2022-04",
    applicability=(StandardApplicability.CENTRIFUGAL,),
    verification_status=(StandardVerificationStatus.CLAUSE_MAPPING_PENDING),
    notes=(
        "Standard identity and edition verified from an official API source. "
        "Clause-level requirements must be mapped from an authorized copy."
    ),
)


API_618 = EngineeringStandard(
    standard_id="API-618",
    authority=StandardAuthority.API,
    title=("Reciprocating Compressors for Petroleum, Chemical, and Gas Industry Services"),
    edition="6th Edition",
    publication_date="2024-05",
    applicability=(StandardApplicability.RECIPROCATING,),
    verification_status=(StandardVerificationStatus.CLAUSE_MAPPING_PENDING),
    notes=(
        "Standard identity and edition verified from an official API source. "
        "Clause-level requirements must be mapped from an authorized copy."
    ),
)


ASME_PTC_10 = EngineeringStandard(
    standard_id="ASME-PTC-10",
    authority=StandardAuthority.ASME,
    title="Axial and Centrifugal Compressors",
    edition="2022",
    publication_date="2022",
    applicability=(
        StandardApplicability.CENTRIFUGAL,
        StandardApplicability.PERFORMANCE_TESTING,
    ),
    verification_status=(StandardVerificationStatus.CLAUSE_MAPPING_PENDING),
    notes=(
        "Official ASME source verifies the 2022 edition and compressor "
        "performance-testing scope. Clause-level mapping remains pending."
    ),
)


GPSA_ENGINEERING_DATA_BOOK = EngineeringStandard(
    standard_id="GPSA-EDB",
    authority=StandardAuthority.GPSA,
    title="GPSA Engineering Data Book",
    edition="Current Digital Edition",
    publication_date=None,
    applicability=(
        StandardApplicability.GAS_PROCESSING_DATA,
        StandardApplicability.CENTRIFUGAL,
        StandardApplicability.RECIPROCATING,
    ),
    verification_status=(StandardVerificationStatus.CLAUSE_MAPPING_PENDING),
    notes=(
        "GPSA/GPA Midstream maintains the Engineering Data Book as a "
        "continuously revised digital engineering resource. Specific section "
        "and equation references require access to the authorized Data Book."
    ),
)


ISO_1217 = EngineeringStandard(
    standard_id="ISO-1217",
    authority=StandardAuthority.ISO,
    title="Displacement compressors -- Acceptance tests",
    edition="Fourth edition, with Amendment 1",
    publication_date="2009 (Amd 1: 2016)",
    applicability=(
        StandardApplicability.ROTARY_SCREW,
        StandardApplicability.RECIPROCATING,
        StandardApplicability.PERFORMANCE_TESTING,
    ),
    verification_status=(StandardVerificationStatus.CLAUSE_MAPPING_PENDING),
    notes=(
        "Standard identity and edition verified from an official ISO source. "
        "ISO 1217 is an acceptance-test standard for volume flow rate and "
        "power of displacement compressors (Annex C: simplified acceptance "
        "test for packaged displacement air compressors), not a design or "
        "performance-prediction formula. Clause-level requirements must be "
        "mapped from an authorized copy."
    ),
)


ENGINEERING_STANDARDS: tuple[EngineeringStandard, ...] = (
    API_617,
    API_618,
    ASME_PTC_10,
    GPSA_ENGINEERING_DATA_BOOK,
    ISO_1217,
)


def get_standard(
    standard_id: str,
) -> EngineeringStandard | None:
    """Return an engineering standard by its identifier."""

    normalized_id = standard_id.strip().upper()

    for standard in ENGINEERING_STANDARDS:
        if standard.standard_id.upper() == normalized_id:
            return standard

    return None
