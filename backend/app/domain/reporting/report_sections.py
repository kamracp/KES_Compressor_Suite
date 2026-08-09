from dataclasses import dataclass
from typing import Any

from app.domain.reporting.export_payload import CalculationExportPayload


@dataclass(frozen=True, slots=True)
class ReportSection:
    """One structured section of an engineering report."""

    title: str
    data: dict[str, Any]
    description: str | None = None


@dataclass(frozen=True, slots=True)
class EngineeringReportSections:
    """Structured sections for a compressor engineering report."""

    metadata: ReportSection
    design_basis: ReportSection
    inputs: ReportSection
    results: ReportSection
    validation: ReportSection
    engineering_notes: ReportSection
    revision_audit: ReportSection


def build_report_sections(
    payload: CalculationExportPayload,
) -> EngineeringReportSections:
    """Build professional engineering report sections from an export payload."""

    metadata = ReportSection(
        title="Document Information",
        data={
            "calculation_code": payload.calculation_code,
            "calculation_type": payload.calculation_type,
            "status": payload.status,
            "revision": payload.revision,
            "project_id": payload.project_id,
            "calculation_case_id": payload.calculation_case_id,
            "title": payload.title,
        },
    )

    design_basis_data: dict[str, Any] = {
        "calculation_type": payload.calculation_type,
    }

    if payload.description is not None:
        design_basis_data["description"] = payload.description

    design_basis = ReportSection(
        title="Design Basis",
        data=design_basis_data,
        description=("Engineering basis and scope associated with this calculation case."),
    )

    inputs = ReportSection(
        title="Calculation Inputs",
        data=payload.input_data,
        description="Input parameters used by the engineering calculation engine.",
    )

    result_data = payload.result_data or {}

    validation_data: dict[str, Any] = {}

    for key in (
        "overall_status",
        "status",
        "validation_checks",
        "driver_is_adequate",
        "capacity_is_adequate",
        "rod_load_is_adequate",
        "design_point_is_within_envelope",
    ):
        if key in result_data:
            validation_data[key] = result_data[key]

    results = ReportSection(
        title="Calculation Results",
        data=result_data,
        description="Calculated engineering performance and sizing results.",
    )

    validation = ReportSection(
        title="Engineering Validation",
        data=validation_data,
        description=(
            "Engineering checks and validation indicators available in the calculation result."
        ),
    )

    engineering_notes = ReportSection(
        title="Engineering Notes",
        data={"notes": payload.engineering_notes or "No engineering notes recorded."},
    )

    revision_audit = ReportSection(
        title="Revision and Audit",
        data={
            "revision": payload.revision,
            "status": payload.status,
            "created_at": payload.created_at.isoformat(),
            "updated_at": payload.updated_at.isoformat(),
            "completed_at": (
                payload.completed_at.isoformat() if payload.completed_at is not None else None
            ),
        },
    )

    return EngineeringReportSections(
        metadata=metadata,
        design_basis=design_basis,
        inputs=inputs,
        results=results,
        validation=validation,
        engineering_notes=engineering_notes,
        revision_audit=revision_audit,
    )
