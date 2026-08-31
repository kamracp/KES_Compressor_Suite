from dataclasses import dataclass
from enum import StrEnum


class StandardAuthority(StrEnum):
    API = "API"
    ASME = "ASME"
    BCAS = "BCAS"
    CAGI = "CAGI"
    GPSA = "GPSA"
    ISO = "ISO"
    EVO = "EVO"
    ACADEMIC = "ACADEMIC"


class StandardApplicability(StrEnum):
    CENTRIFUGAL = "CENTRIFUGAL"
    RECIPROCATING = "RECIPROCATING"
    ROTARY_SCREW = "ROTARY_SCREW"
    PERFORMANCE_TESTING = "PERFORMANCE_TESTING"
    GAS_PROCESSING_DATA = "GAS_PROCESSING_DATA"
    DISTRIBUTION_PIPEWORK = "DISTRIBUTION_PIPEWORK"
    ENERGY_AUDIT = "ENERGY_AUDIT"
    LEAKAGE_MANAGEMENT = "LEAKAGE_MANAGEMENT"
    MEASUREMENT_VERIFICATION = "MEASUREMENT_VERIFICATION"


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


CAGI_HANDBOOK = EngineeringStandard(
    standard_id="CAGI-CAGH",
    authority=StandardAuthority.CAGI,
    title="Compressed Air and Gas Handbook",
    edition="7th Edition",
    publication_date="2016",
    applicability=(StandardApplicability.DISTRIBUTION_PIPEWORK,),
    verification_status=(StandardVerificationStatus.OFFICIAL_SOURCE_VERIFIED),
    notes=(
        "CAGI's official Pressure Drop technical brief (cagi.org) recommends "
        "keeping air velocity through piping at 20 ft/s (~6.1 m/s) or lower "
        "to minimize turbulence and pressure drop, and refers to the "
        "Handbook's 'Loss of Air Pressure Due to Friction' tables for piping "
        "pressure-loss data. Basis for the RECOMMENDED velocity screening "
        "threshold (<= 6 m/s) in distribution pipe sizing."
    ),
)


BCAS_BPG_101 = EngineeringStandard(
    standard_id="BCAS-BPG-101",
    authority=StandardAuthority.BCAS,
    title="Best Practice Guide 101 -- Installation of Compressed Air Systems",
    edition="BPG 101-6",
    publication_date="2023",
    applicability=(StandardApplicability.DISTRIBUTION_PIPEWORK,),
    verification_status=(StandardVerificationStatus.CLAUSE_MAPPING_PENDING),
    notes=(
        "BCAS guidance, as published by manufacturer engineering references "
        "(e.g. Atlas Copco pipe-sizing guidance citing BCAS): a velocity of "
        "6 m/s or less prevents moisture and debris being carried past drain "
        "legs into controls; above 9 m/s water and debris are transported in "
        "the air stream. Recommended design velocity for interconnecting "
        "piping and main headers is 6-7 m/s, never exceeding 9 m/s. Basis "
        "for the CAUTION band (6-9 m/s) and the EXCESSIVE threshold "
        "(> 9 m/s) in distribution pipe sizing. Clause-level mapping from "
        "the authorized BCAS guide remains pending."
    ),
)


ISO_6358 = EngineeringStandard(
    standard_id="ISO-6358",
    authority=StandardAuthority.ISO,
    title=(
        "Pneumatic fluid power — Determination of flow-rate characteristics "
        "of components using compressible fluids — Parts 1–3"
    ),
    edition="Parts 1 and 2: 2013; Part 3: 2014",
    publication_date="2013–2014",
    applicability=(StandardApplicability.LEAKAGE_MANAGEMENT,),
    verification_status=(StandardVerificationStatus.CLAUSE_MAPPING_PENDING),
    notes=(
        "ISO 6358 defines the choked-flow and subsonic-flow orifice model "
        "(conductance C and critical pressure ratio b) for pneumatic "
        "components. This is the citable basis for the leakage-orifice "
        "flow-rate formula used in the leakage energy engine when "
        "converting orifice diameter to equivalent flow. Cited in UK "
        "compressed-air audit practice as the reference for leakage "
        "quantification from crack/orifice diameter and system pressure. "
        "Clause-level mapping requires an authorized ISO copy."
    ),
)


ISO_11011 = EngineeringStandard(
    standard_id="ISO-11011",
    authority=StandardAuthority.ISO,
    title="Compressed air — Energy efficiency — Evaluation",
    edition="First edition",
    publication_date="2013-06",
    applicability=(StandardApplicability.ENERGY_AUDIT,),
    verification_status=(StandardVerificationStatus.CLAUSE_MAPPING_PENDING),
    notes=(
        "ISO 11011:2013 specifies a systematic procedure for evaluating "
        "the energy efficiency of a compressed-air system encompassing "
        "supply (generation), transmission (distribution), and demand "
        "(end use). It defines system boundaries, measurement points, "
        "specific energy ratio (SER), and the structure of an energy "
        "efficiency audit report. This is the governing framework for "
        "the Brownfield audit engine: baseline SER, optimized SER, and "
        "the opportunity report follow ISO 11011 system boundaries. "
        "Clause-level mapping requires an authorized ISO copy."
    ),
)


IPMVP_CORE = EngineeringStandard(
    standard_id="IPMVP-CORE",
    authority=StandardAuthority.EVO,
    title=("International Performance Measurement and Verification Protocol — Core Concepts"),
    edition="Current edition",
    publication_date=None,
    applicability=(StandardApplicability.MEASUREMENT_VERIFICATION,),
    verification_status=(StandardVerificationStatus.CLAUSE_MAPPING_PENDING),
    notes=(
        "IPMVP (published by the Efficiency Valuation Organization, EVO) "
        "is the international framework for measuring and verifying energy "
        "and water savings from efficiency projects. It defines four "
        "M&V Options (A–D) ranging from stipulation with spot measurement "
        "to whole-facility metering. In the Kamra Compressor OS context "
        "IPMVP Option A (stipulated baseline, measured parameter) or "
        "Option B (all parameters measured) is the recommended basis for "
        "reporting verified leak-repair and pressure-reduction savings to "
        "clients. Clause-level mapping requires the current EVO publication."
    ),
)


ZAIM_2025 = EngineeringStandard(
    standard_id="ZAIM-2025",
    authority=StandardAuthority.ACADEMIC,
    title=(
        "Energy Efficiency Evaluation of an Industrial Compressed Air "
        "System: A Case Study Applying ISO 11011"
    ),
    edition="Peer-reviewed article",
    publication_date="2025",
    applicability=(StandardApplicability.ENERGY_AUDIT,),
    verification_status=(StandardVerificationStatus.OFFICIAL_SOURCE_VERIFIED),
    notes=(
        "Zaim et al. (2025), MDPI Processes, Vol. 13. A full ISO 11011 "
        "audit of an industrial compressed-air installation with published "
        "baseline and optimized measured data (flow, pressure, specific "
        "power, SER). Serves as the external validation anchor for the "
        "Brownfield engine golden case GC-BF-ZAIM-2025: if the engine "
        "reproduces the paper's SER, recoverable power, and annual savings "
        "figures from the published inputs, the audit model is validated "
        "against a citable peer-reviewed source. DOI to be confirmed from "
        "the authorized MDPI article page."
    ),
)

ENGINEERING_STANDARDS: tuple[EngineeringStandard, ...] = (
    API_617,
    API_618,
    ASME_PTC_10,
    GPSA_ENGINEERING_DATA_BOOK,
    ISO_1217,
    ISO_6358,
    ISO_11011,
    CAGI_HANDBOOK,
    BCAS_BPG_101,
    IPMVP_CORE,
    ZAIM_2025,
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
