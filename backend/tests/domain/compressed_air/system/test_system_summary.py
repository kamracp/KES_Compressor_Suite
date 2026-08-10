import pytest

from app.domain.compressed_air.system.system_summary import (
    SystemAssessmentMode,
    SystemReadinessStatus,
    build_compressed_air_system_summary,
    get_system_capability,
)


def test_empty_summary_is_insufficient_data() -> None:
    summary = build_compressed_air_system_summary(
        project_id=1,
        assessment_mode=SystemAssessmentMode.GREENFIELD,
    )

    assert summary.readiness_status == SystemReadinessStatus.INSUFFICIENT_DATA

    assert summary.available_capability_count == 0
    assert summary.total_capability_count == 13

    assert summary.integrated_report_available is False
    assert summary.formal_compliance_claim_available is False


def test_partial_summary_is_identified() -> None:
    summary = build_compressed_air_system_summary(
        project_id=1,
        assessment_mode=SystemAssessmentMode.GREENFIELD,
        greenfield={
            "system_feasible": True,
        },
        energy={
            "annual_energy_kwh": "1000000",
        },
        equipment={
            "selection_basis": "vendor-neutral",
        },
    )

    assert summary.readiness_status == SystemReadinessStatus.PARTIAL
    assert summary.available_capability_count == 3


def test_complete_summary_is_identified() -> None:
    payload = {
        "available": True,
    }

    summary = build_compressed_air_system_summary(
        project_id=1,
        assessment_mode=SystemAssessmentMode.COMBINED,
        greenfield=payload,
        brownfield=payload,
        advanced_engineering=payload,
        demand_and_capacity=payload,
        pressure=payload,
        air_treatment=payload,
        storage=payload,
        distribution=payload,
        energy=payload,
        equipment=payload,
        standards={
            "formal_compliance_claim_available": False,
        },
        persistence=payload,
        integrated_report=payload,
    )

    assert summary.readiness_status == SystemReadinessStatus.COMPLETE
    assert summary.available_capability_count == 13
    assert summary.total_capability_count == 13


def test_system_capability_lookup() -> None:
    summary = build_compressed_air_system_summary(
        project_id=1,
        assessment_mode=SystemAssessmentMode.GREENFIELD,
        energy={
            "annual_energy_kwh": "1000000",
        },
    )

    capability = get_system_capability(
        summary,
        "energy",
    )

    assert capability.available is True
    assert capability.data["annual_energy_kwh"] == "1000000"


def test_missing_capability_lookup_raises_error() -> None:
    summary = build_compressed_air_system_summary(
        project_id=1,
        assessment_mode=SystemAssessmentMode.GREENFIELD,
    )

    with pytest.raises(
        LookupError,
        match="System capability",
    ):
        get_system_capability(
            summary,
            "unknown-capability",
        )


def test_formal_compliance_claim_defaults_to_false() -> None:
    summary = build_compressed_air_system_summary(
        project_id=1,
        assessment_mode=SystemAssessmentMode.GREENFIELD,
        standards={
            "formal_compliance_claim_available": False,
        },
    )

    assert summary.formal_compliance_claim_available is False


def test_formal_compliance_claim_can_be_preserved() -> None:
    summary = build_compressed_air_system_summary(
        project_id=1,
        assessment_mode=SystemAssessmentMode.GREENFIELD,
        standards={
            "formal_compliance_claim_available": True,
        },
    )

    assert summary.formal_compliance_claim_available is True


def test_integrated_report_availability_is_detected() -> None:
    summary = build_compressed_air_system_summary(
        project_id=1,
        assessment_mode=SystemAssessmentMode.GREENFIELD,
        integrated_report={
            "report_code": "RPT-001",
        },
    )

    assert summary.integrated_report_available is True


def test_vendor_neutral_equipment_warning_when_missing() -> None:
    summary = build_compressed_air_system_summary(
        project_id=1,
        assessment_mode=SystemAssessmentMode.GREENFIELD,
    )

    assert any("vendor-neutral equipment" in warning.lower() for warning in summary.warnings)


def test_combined_mode_preserves_engineering_basis_warning() -> None:
    summary = build_compressed_air_system_summary(
        project_id=1,
        assessment_mode=SystemAssessmentMode.COMBINED,
        greenfield={
            "available": True,
        },
        brownfield={
            "available": True,
        },
    )

    assert any(
        "individual greenfield and brownfield engineering bases" in warning.lower()
        for warning in summary.warnings
    )


def test_recommendations_are_preserved() -> None:
    recommendations = (
        "Monitor system specific power.",
        "Maintain the lowest practical operating pressure.",
    )

    summary = build_compressed_air_system_summary(
        project_id=1,
        assessment_mode=SystemAssessmentMode.GREENFIELD,
        recommendations=recommendations,
    )

    assert summary.recommendations == recommendations


def test_invalid_project_id_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="Project ID must be greater than zero",
    ):
        build_compressed_air_system_summary(
            project_id=0,
            assessment_mode=SystemAssessmentMode.GREENFIELD,
        )
