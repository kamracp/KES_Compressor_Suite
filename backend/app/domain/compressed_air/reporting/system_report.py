from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class EngineeringReportSection(StrEnum):
    DESIGN_BASIS = "DESIGN_BASIS"
    DEMAND_AND_CAPACITY = "DEMAND_AND_CAPACITY"
    EQUIPMENT_SELECTION = "EQUIPMENT_SELECTION"
    AIR_TREATMENT = "AIR_TREATMENT"
    STORAGE = "STORAGE"
    DISTRIBUTION = "DISTRIBUTION"
    ENERGY = "ENERGY"
    BROWNFIELD_AUDIT = "BROWNFIELD_AUDIT"
    ADVANCED_ENGINEERING = "ADVANCED_ENGINEERING"
    STANDARDS_AND_COMPLIANCE = "STANDARDS_AND_COMPLIANCE"
    RECOMMENDATIONS = "RECOMMENDATIONS"
    AUDIT_TRAIL = "AUDIT_TRAIL"


@dataclass(frozen=True, slots=True)
class EngineeringReportSectionData:
    section: EngineeringReportSection
    title: str

    included: bool

    data: dict[str, Any]

    notes: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class IntegratedEngineeringReport:
    project_id: int

    report_code: str
    title: str

    assessment_type: str

    sections: tuple[EngineeringReportSectionData, ...]

    section_count: int

    formal_compliance_claim_available: bool

    warnings: tuple[str, ...]

    generated_from_assessment_code: str | None = None
    calculation_version: str | None = None


def build_integrated_engineering_report(
    *,
    project_id: int,
    report_code: str,
    title: str,
    assessment_type: str,
    design_basis: dict[str, Any] | None = None,
    demand_and_capacity: dict[str, Any] | None = None,
    equipment_selection: dict[str, Any] | None = None,
    air_treatment: dict[str, Any] | None = None,
    storage: dict[str, Any] | None = None,
    distribution: dict[str, Any] | None = None,
    energy: dict[str, Any] | None = None,
    brownfield_audit: dict[str, Any] | None = None,
    advanced_engineering: dict[str, Any] | None = None,
    standards_and_compliance: dict[str, Any] | None = None,
    recommendations: dict[str, Any] | None = None,
    audit_trail: dict[str, Any] | None = None,
    generated_from_assessment_code: str | None = None,
    calculation_version: str | None = None,
) -> IntegratedEngineeringReport:
    """Build a consolidated vendor-neutral compressed-air engineering report."""

    if project_id <= 0:
        raise ValueError("Project ID must be greater than zero.")

    if not report_code.strip():
        raise ValueError("Report code cannot be empty.")

    if not title.strip():
        raise ValueError("Report title cannot be empty.")

    section_definitions = (
        (
            EngineeringReportSection.DESIGN_BASIS,
            "Design Basis",
            design_basis,
        ),
        (
            EngineeringReportSection.DEMAND_AND_CAPACITY,
            "Demand and Capacity",
            demand_and_capacity,
        ),
        (
            EngineeringReportSection.EQUIPMENT_SELECTION,
            "Equipment Selection",
            equipment_selection,
        ),
        (
            EngineeringReportSection.AIR_TREATMENT,
            "Air Treatment",
            air_treatment,
        ),
        (
            EngineeringReportSection.STORAGE,
            "Storage and Receivers",
            storage,
        ),
        (
            EngineeringReportSection.DISTRIBUTION,
            "Distribution and Pressure",
            distribution,
        ),
        (
            EngineeringReportSection.ENERGY,
            "Energy Performance",
            energy,
        ),
        (
            EngineeringReportSection.BROWNFIELD_AUDIT,
            "Brownfield Audit",
            brownfield_audit,
        ),
        (
            EngineeringReportSection.ADVANCED_ENGINEERING,
            "Advanced Engineering",
            advanced_engineering,
        ),
        (
            EngineeringReportSection.STANDARDS_AND_COMPLIANCE,
            "Standards and Compliance",
            standards_and_compliance,
        ),
        (
            EngineeringReportSection.RECOMMENDATIONS,
            "Engineering Recommendations",
            recommendations,
        ),
        (
            EngineeringReportSection.AUDIT_TRAIL,
            "Calculation and Audit Trail",
            audit_trail,
        ),
    )

    sections = tuple(
        EngineeringReportSectionData(
            section=section,
            title=section_title,
            included=payload is not None,
            data=payload or {},
        )
        for section, section_title, payload in section_definitions
    )

    formal_compliance_claim_available = _extract_compliance_claim_status(standards_and_compliance)

    warnings: list[str] = []

    if standards_and_compliance is None:
        warnings.append("No standards applicability snapshot is included in this report.")

    elif not formal_compliance_claim_available:
        warnings.append(
            "Standards information is provided for engineering reference and "
            "applicability review; no formal compliance claim is available."
        )

    if equipment_selection is None:
        warnings.append("No vendor-neutral equipment selection section is included.")

    return IntegratedEngineeringReport(
        project_id=project_id,
        report_code=report_code.strip(),
        title=title.strip(),
        assessment_type=assessment_type,
        sections=sections,
        section_count=sum(1 for section in sections if section.included),
        formal_compliance_claim_available=(formal_compliance_claim_available),
        warnings=tuple(warnings),
        generated_from_assessment_code=generated_from_assessment_code,
        calculation_version=calculation_version,
    )


def get_report_section(
    report: IntegratedEngineeringReport,
    section: EngineeringReportSection,
) -> EngineeringReportSectionData:
    """Return one report section."""

    for item in report.sections:
        if item.section == section:
            return item

    raise LookupError(f"Report section {section.value} was not found.")


def _extract_compliance_claim_status(
    standards_and_compliance: dict[str, Any] | None,
) -> bool:
    if standards_and_compliance is None:
        return False

    return bool(
        standards_and_compliance.get(
            "formal_compliance_claim_available",
            False,
        )
    )
