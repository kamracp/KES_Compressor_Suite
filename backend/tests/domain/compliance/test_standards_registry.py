from app.domain.compliance.standards_registry import (
    API_617,
    API_618,
    ASME_PTC_10,
    BCAS_BPG_101,
    CAGI_HANDBOOK,
    ENGINEERING_STANDARDS,
    GPSA_ENGINEERING_DATA_BOOK,
    ISO_1217,
    ISO_6358,
    ISO_11011,
    IPMVP_CORE,
    ZAIM_2025,
    EngineeringStandard,
    StandardApplicability,
    StandardAuthority,
    StandardVerificationStatus,
    get_standard,
)


def test_registry_contains_expected_standards() -> None:
    assert ENGINEERING_STANDARDS == (
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


def test_standard_ids_are_unique() -> None:
    standard_ids = tuple(standard.standard_id for standard in ENGINEERING_STANDARDS)

    assert len(standard_ids) == len(set(standard_ids))


def test_api_617_metadata() -> None:
    standard = API_617

    assert isinstance(standard, EngineeringStandard)
    assert standard.standard_id == "API-617"
    assert standard.authority == StandardAuthority.API
    assert standard.edition == "9th Edition"

    assert standard.applicability == (StandardApplicability.CENTRIFUGAL,)

    assert standard.verification_status == StandardVerificationStatus.CLAUSE_MAPPING_PENDING


def test_api_618_metadata() -> None:
    standard = API_618

    assert standard.standard_id == "API-618"
    assert standard.authority == StandardAuthority.API

    assert standard.applicability == (StandardApplicability.RECIPROCATING,)


def test_asme_ptc_10_applicability() -> None:
    standard = ASME_PTC_10

    assert standard.authority == StandardAuthority.ASME

    assert StandardApplicability.CENTRIFUGAL in standard.applicability

    assert StandardApplicability.PERFORMANCE_TESTING in standard.applicability


def test_gpsa_data_book_applicability() -> None:
    standard = GPSA_ENGINEERING_DATA_BOOK

    assert standard.authority == StandardAuthority.GPSA

    assert StandardApplicability.GAS_PROCESSING_DATA in standard.applicability

    assert StandardApplicability.CENTRIFUGAL in standard.applicability

    assert StandardApplicability.RECIPROCATING in standard.applicability


def test_iso_1217_metadata() -> None:
    standard = ISO_1217

    assert standard.standard_id == "ISO-1217"
    assert standard.authority == StandardAuthority.ISO

    assert StandardApplicability.ROTARY_SCREW in standard.applicability
    assert StandardApplicability.PERFORMANCE_TESTING in standard.applicability

    assert standard.verification_status == StandardVerificationStatus.CLAUSE_MAPPING_PENDING


def test_get_standard_returns_exact_match() -> None:
    assert get_standard("API-617") is API_617


def test_get_standard_is_case_insensitive() -> None:
    assert get_standard("api-618") is API_618


def test_get_standard_ignores_surrounding_whitespace() -> None:
    assert get_standard("  asme-ptc-10  ") is ASME_PTC_10


def test_get_standard_returns_none_for_unknown_standard() -> None:
    assert get_standard("UNKNOWN-STANDARD") is None


def test_all_registered_standards_have_reference_notes() -> None:
    assert all(standard.notes.strip() for standard in ENGINEERING_STANDARDS)


def test_all_registered_standards_have_verification_status() -> None:
    assert all(
        standard.verification_status in StandardVerificationStatus
        for standard in ENGINEERING_STANDARDS
    )


def test_cagi_handbook_metadata() -> None:
    standard = CAGI_HANDBOOK

    assert standard.standard_id == "CAGI-CAGH"
    assert standard.authority == StandardAuthority.CAGI
    assert standard.edition == "7th Edition"

    assert standard.applicability == (StandardApplicability.DISTRIBUTION_PIPEWORK,)

    assert standard.verification_status == StandardVerificationStatus.OFFICIAL_SOURCE_VERIFIED


def test_bcas_bpg_101_metadata() -> None:
    standard = BCAS_BPG_101

    assert standard.standard_id == "BCAS-BPG-101"
    assert standard.authority == StandardAuthority.BCAS

    assert standard.applicability == (StandardApplicability.DISTRIBUTION_PIPEWORK,)

    assert standard.verification_status == StandardVerificationStatus.CLAUSE_MAPPING_PENDING


def test_distribution_standards_resolvable_by_id() -> None:
    assert get_standard("cagi-cagh") == CAGI_HANDBOOK
    assert get_standard(" bcas-bpg-101 ") == BCAS_BPG_101


def test_iso_6358_metadata() -> None:
    standard = ISO_6358

    assert standard.standard_id == "ISO-6358"
    assert standard.authority == StandardAuthority.ISO
    assert standard.applicability == (StandardApplicability.LEAKAGE_MANAGEMENT,)
    assert standard.verification_status == StandardVerificationStatus.CLAUSE_MAPPING_PENDING


def test_iso_11011_metadata() -> None:
    standard = ISO_11011

    assert standard.standard_id == "ISO-11011"
    assert standard.authority == StandardAuthority.ISO
    assert standard.applicability == (StandardApplicability.ENERGY_AUDIT,)
    assert standard.verification_status == StandardVerificationStatus.CLAUSE_MAPPING_PENDING


def test_ipmvp_core_metadata() -> None:
    standard = IPMVP_CORE

    assert standard.standard_id == "IPMVP-CORE"
    assert standard.authority == StandardAuthority.EVO
    assert standard.applicability == (StandardApplicability.MEASUREMENT_VERIFICATION,)
    assert standard.verification_status == StandardVerificationStatus.CLAUSE_MAPPING_PENDING


def test_zaim_2025_metadata() -> None:
    standard = ZAIM_2025

    assert standard.standard_id == "ZAIM-2025"
    assert standard.authority == StandardAuthority.ACADEMIC
    assert standard.applicability == (StandardApplicability.ENERGY_AUDIT,)
    assert standard.verification_status == StandardVerificationStatus.OFFICIAL_SOURCE_VERIFIED
