from sqlalchemy import delete

from app.core.database import SessionLocal
from app.models.calculation_case import (
    CalculationCase,
    CalculationStatus,
    CalculationType,
)
from app.models.project import Project
from app.repositories.project import project_repository
from app.schemas.calculation_case import CalculationCaseCreate
from app.schemas.project import ProjectCreate
from app.services.calculation_case import calculation_case_service
from app.services.report_export import report_export_service
from app.services.reporting import ReportingCalculationCaseNotFoundError
from tests.helpers.tenant_context import ensure_test_organization_id


def reset_data() -> None:
    with SessionLocal() as db:
        db.execute(delete(CalculationCase))
        db.execute(delete(Project))
        db.commit()


def create_test_project() -> int:
    with SessionLocal() as db:
        project = project_repository.create(
            db,
            organization_id=ensure_test_organization_id(db),
            payload=ProjectCreate(
                project_code="KESC-EXPORT-001",
                project_name="Report Export Test Project",
            ),
        )

        return project.id


def create_completed_case(project_id: int) -> int:
    with SessionLocal() as db:
        case = calculation_case_service.create_case(
            db,
            organization_id=ensure_test_organization_id(db),
            payload=CalculationCaseCreate(
                project_id=project_id,
                calculation_code="EXPORT-SVC-001",
                calculation_type=CalculationType.CENTRIFUGAL,
                status=CalculationStatus.COMPLETED,
                revision=1,
                title="Centrifugal Export Service Case",
                description="Report export service test.",
                input_data={
                    "suction_pressure_bar": "30",
                    "discharge_pressure_bar": "90",
                },
                result_data={
                    "required_driver_power_kw": "21011.32",
                    "status": "PASS",
                },
                engineering_notes="Reviewed before export.",
            ),
        )

        return case.id


def test_get_export_payload() -> None:
    reset_data()

    project_id = create_test_project()
    calculation_case_id = create_completed_case(project_id)

    with SessionLocal() as db:
        organization_id = ensure_test_organization_id(db)

        payload = report_export_service.get_export_payload(
            db,
            organization_id=organization_id,
            calculation_case_id=calculation_case_id,
        )

    assert payload.calculation_case_id == calculation_case_id
    assert payload.project_id == project_id

    assert payload.calculation_code == "EXPORT-SVC-001"
    assert payload.calculation_type == "CENTRIFUGAL"
    assert payload.status == "COMPLETED"
    assert payload.revision == 1

    assert payload.input_data["suction_pressure_bar"] == "30"

    assert payload.result_data is not None
    assert payload.result_data["required_driver_power_kw"] == "21011.32"
    assert payload.result_data["status"] == "PASS"

    assert payload.engineering_notes == "Reviewed before export."
    assert payload.completed_at is not None


def test_missing_case_raises_reporting_error() -> None:
    reset_data()

    with SessionLocal() as db:
        organization_id = ensure_test_organization_id(db)

        try:
            report_export_service.get_export_payload(
                db,
                organization_id=organization_id,
                calculation_case_id=999999,
            )
        except ReportingCalculationCaseNotFoundError as exc:
            assert "999999" in str(exc)
        else:
            raise AssertionError("Expected ReportingCalculationCaseNotFoundError.")


def test_export_payload_is_hidden_from_other_organization() -> None:
    reset_data()

    project_id = create_test_project()
    calculation_case_id = create_completed_case(project_id)

    with SessionLocal() as db:
        try:
            report_export_service.get_export_payload(
                db,
                organization_id=999999,
                calculation_case_id=calculation_case_id,
            )
        except ReportingCalculationCaseNotFoundError as exc:
            assert str(calculation_case_id) in str(exc)
        else:
            raise AssertionError("Expected ReportingCalculationCaseNotFoundError.")
