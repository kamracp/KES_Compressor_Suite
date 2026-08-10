from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class SystemAssessmentMode(StrEnum):
    GREENFIELD = "GREENFIELD"
    BROWNFIELD = "BROWNFIELD"
    ADVANCED = "ADVANCED"
    COMBINED = "COMBINED"


class SystemReadinessStatus(StrEnum):
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


@dataclass(frozen=True, slots=True)
class SystemCapabilitySummary:
    name: str
    available: bool
    data: dict[str, Any]


@dataclass(frozen=True, slots=True)
class CompressedAirSystemSummary:
    project_id: int
    assessment_mode: SystemAssessmentMode
    readiness_status: SystemReadinessStatus

    capabilities: tuple[SystemCapabilitySummary, ...]

    available_capability_count: int
    total_capability_count: int

    formal_compliance_claim_available: bool
    integrated_report_available: bool

    recommendations: tuple[str, ...]
    warnings: tuple[str, ...]

    assessment_code: str | None = None
    calculation_version: str | None = None


def build_compressed_air_system_summary(
    *,
    project_id: int,
    assessment_mode: SystemAssessmentMode,
    greenfield: dict[str, Any] | None = None,
    brownfield: dict[str, Any] | None = None,
    advanced_engineering: dict[str, Any] | None = None,
    demand_and_capacity: dict[str, Any] | None = None,
    pressure: dict[str, Any] | None = None,
    air_treatment: dict[str, Any] | None = None,
    storage: dict[str, Any] | None = None,
    distribution: dict[str, Any] | None = None,
    energy: dict[str, Any] | None = None,
    equipment: dict[str, Any] | None = None,
    standards: dict[str, Any] | None = None,
    persistence: dict[str, Any] | None = None,
    integrated_report: dict[str, Any] | None = None,
    recommendations: tuple[str, ...] = (),
    assessment_code: str | None = None,
    calculation_version: str | None = None,
) -> CompressedAirSystemSummary:
    """Build a top-level vendor-neutral compressed-air system summary."""

    if project_id <= 0:
        raise ValueError("Project ID must be greater than zero.")

    capability_definitions = (
        ("greenfield", greenfield),
        ("brownfield", brownfield),
        ("advanced_engineering", advanced_engineering),
        ("demand_and_capacity", demand_and_capacity),
        ("pressure", pressure),
        ("air_treatment", air_treatment),
        ("storage", storage),
        ("distribution", distribution),
        ("energy", energy),
        ("equipment", equipment),
        ("standards", standards),
        ("persistence", persistence),
        ("integrated_report", integrated_report),
    )

    capabilities = tuple(
        SystemCapabilitySummary(
            name=name,
            available=data is not None,
            data=dict(data) if data is not None else {},
        )
        for name, data in capability_definitions
    )

    available_capability_count = sum(capability.available for capability in capabilities)

    total_capability_count = len(capabilities)

    readiness_status = _determine_readiness_status(
        available_capability_count=available_capability_count,
        total_capability_count=total_capability_count,
    )

    formal_compliance_claim_available = _extract_compliance_status(standards)

    warnings = _build_warnings(
        assessment_mode=assessment_mode,
        standards=standards,
        equipment=equipment,
        persistence=persistence,
        integrated_report=integrated_report,
    )

    return CompressedAirSystemSummary(
        project_id=project_id,
        assessment_mode=assessment_mode,
        readiness_status=readiness_status,
        capabilities=capabilities,
        available_capability_count=available_capability_count,
        total_capability_count=total_capability_count,
        formal_compliance_claim_available=(formal_compliance_claim_available),
        integrated_report_available=integrated_report is not None,
        recommendations=tuple(recommendations),
        warnings=warnings,
        assessment_code=assessment_code,
        calculation_version=calculation_version,
    )


def get_system_capability(
    summary: CompressedAirSystemSummary,
    capability_name: str,
) -> SystemCapabilitySummary:
    """Return one capability from a compressed-air system summary."""

    normalized_name = capability_name.strip().lower()

    for capability in summary.capabilities:
        if capability.name.lower() == normalized_name:
            return capability

    raise LookupError(f"System capability '{capability_name}' was not found.")


def _determine_readiness_status(
    *,
    available_capability_count: int,
    total_capability_count: int,
) -> SystemReadinessStatus:
    if available_capability_count == 0:
        return SystemReadinessStatus.INSUFFICIENT_DATA

    if available_capability_count == total_capability_count:
        return SystemReadinessStatus.COMPLETE

    return SystemReadinessStatus.PARTIAL


def _extract_compliance_status(
    standards: dict[str, Any] | None,
) -> bool:
    if standards is None:
        return False

    return bool(
        standards.get(
            "formal_compliance_claim_available",
            False,
        )
    )


def _build_warnings(
    *,
    assessment_mode: SystemAssessmentMode,
    standards: dict[str, Any] | None,
    equipment: dict[str, Any] | None,
    persistence: dict[str, Any] | None,
    integrated_report: dict[str, Any] | None,
) -> tuple[str, ...]:
    warnings: list[str] = []

    if standards is None:
        warnings.append("Standards applicability information is not available.")
    elif not _extract_compliance_status(standards):
        warnings.append("No formal standards compliance claim is available.")

    if equipment is None:
        warnings.append("Vendor-neutral equipment performance information is not available.")

    if persistence is None:
        warnings.append("Assessment persistence and audit information is not available.")

    if integrated_report is None:
        warnings.append("Integrated engineering report information is not available.")

    if assessment_mode is SystemAssessmentMode.COMBINED:
        warnings.append(
            "Combined assessment mode must preserve the individual "
            "greenfield and brownfield engineering bases."
        )

    return tuple(warnings)
