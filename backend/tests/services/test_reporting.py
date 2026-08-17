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
from app.services.reporting import (
    ReportingCalculationCaseNotFoundError,
    reporting_service,
)
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
                project_code="KESC-RPT-001",
                project_name="Reporting Service Test Project",
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
                calculation_code="RPT-CALC-001",
                calculation_type=CalculationType.CENTRIFUGAL,
                status=CalculationStatus.COMPLETED,
                revision=1,
                title="Centrifugal Reporting Case",
                description="Reporting service test.",
                input_data={
                    "suction_pressure_bar": "30",
                    "discharge_pressure_bar": "90",
                },
                result_data={
                    "required_driver_power_kw": "21011.32",
                },
                engineering_notes="Reviewed calculation.",
            ),
        )

        return case.id


def test_get_calculation_report() -> None:
    reset_data()

    project_id = create_test_project()
    calculation_case_id = create_completed_case(project_id)

    with SessionLocal() as db:
        organization_id = ensure_test_organization_id(db)

        report = reporting_service.get_calculation_report(
            db,
            organization_id=organization_id,
            calculation_case_id=calculation_case_id,
        )

    assert report.calculation_case_id == calculation_case_id
    assert report.project_id == project_id
    assert report.calculation_code == "RPT-CALC-001"
    assert report.calculation_type == "CENTRIFUGAL"
    assert report.status == "COMPLETED"

    assert report.input_data["suction_pressure_bar"] == "30"

    assert report.result_data is not None
    assert report.result_data["required_driver_power_kw"] == "21011.32"

    assert report.engineering_notes == "Reviewed calculation."
    assert report.completed_at is not None


def test_get_audit_summary() -> None:
    reset_data()

    project_id = create_test_project()
    calculation_case_id = create_completed_case(project_id)

    with SessionLocal() as db:
        organization_id = ensure_test_organization_id(db)

        summary = reporting_service.get_audit_summary(
            db,
            organization_id=organization_id,
            calculation_case_id=calculation_case_id,
        )

    assert summary.calculation_case_id == calculation_case_id
    assert summary.project_id == project_id
    assert summary.status == "COMPLETED"
    assert summary.is_completed is True
    assert summary.has_result_data is True
    assert summary.has_engineering_notes is True


def test_missing_calculation_case_raises_error() -> None:
    reset_data()

    with SessionLocal() as db:
        organization_id = ensure_test_organization_id(db)

        try:
            reporting_service.get_calculation_report(
                db,
                organization_id=organization_id,
                calculation_case_id=999999,
            )
        except ReportingCalculationCaseNotFoundError as exc:
            assert "999999" in str(exc)
        else:
            raise AssertionError("Expected ReportingCalculationCaseNotFoundError.")


def test_calculation_case_is_hidden_from_other_organization() -> None:
    reset_data()

    project_id = create_test_project()
    calculation_case_id = create_completed_case(project_id)

    with SessionLocal() as db:
        try:
            reporting_service.get_calculation_report(
                db,
                organization_id=999999,
                calculation_case_id=calculation_case_id,
            )
        except ReportingCalculationCaseNotFoundError as exc:
            assert str(calculation_case_id) in str(exc)
        else:
            raise AssertionError("Expected ReportingCalculationCaseNotFoundError.")
