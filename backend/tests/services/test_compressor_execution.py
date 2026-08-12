from decimal import Decimal

from sqlalchemy import delete

from app.core.database import SessionLocal
from app.models.calculation_case import CalculationCase
from app.models.project import Project
from app.repositories.project import project_repository
from app.schemas.calculation_execution import CalculationExecutionMetadata
from app.schemas.compressor_calculation import (
    CompressorSelectionRequest,
)
from app.schemas.project import ProjectCreate
from app.services.compressor_execution import compressor_execution_service
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
                project_code="KESC-EXEC-SVC-001",
                project_name="Compressor Execution Service Test",
            ),
        )

        return project.id


def build_selection_request() -> CompressorSelectionRequest:
    return CompressorSelectionRequest(
        required_flow_m3_per_hr=Decimal("14143.4"),
        suction_pressure_bar=Decimal("30"),
        discharge_pressure_bar=Decimal("90"),
        required_turndown_fraction=Decimal("0.70"),
        continuous_operation=True,
        gas_molecular_weight=Decimal("19.075"),
        estimated_operating_hours_per_year=Decimal("8400"),
    )


def test_selection_calculate_only() -> None:
    reset_data()

    with SessionLocal() as db:
        response = compressor_execution_service.execute_selection(
            db,
            organization_id=ensure_test_organization_id(db),
            calculation=build_selection_request(),
            execution=CalculationExecutionMetadata(
                persist_result=False,
            ),
        )

    assert response["calculation_case_id"] is None

    result = response["result"]

    assert result["recommended_type"] in {
        "RECIPROCATING",
        "CENTRIFUGAL",
    }


def test_selection_calculate_and_persist() -> None:
    reset_data()

    project_id = create_test_project()

    with SessionLocal() as db:
        response = compressor_execution_service.execute_selection(
            db,
            organization_id=ensure_test_organization_id(db),
            calculation=build_selection_request(),
            execution=CalculationExecutionMetadata(
                persist_result=True,
                project_id=project_id,
                calculation_code="SEL-EXEC-001",
                title="Persisted Compressor Selection",
                engineering_notes="Service-level persistence test.",
            ),
        )

        calculation_case_id = response["calculation_case_id"]

        assert calculation_case_id is not None

    with SessionLocal() as db:
        stored = db.get(
            CalculationCase,
            calculation_case_id,
        )

        assert stored is not None
        assert stored.project_id == project_id
        assert stored.calculation_code == "SEL-EXEC-001"
        assert stored.calculation_type == "SELECTION"
        assert stored.status == "COMPLETED"

        assert stored.input_data["required_flow_m3_per_hr"] == "14143.4"

        assert stored.result_data is not None
        assert stored.result_data["recommended_type"] in {
            "RECIPROCATING",
            "CENTRIFUGAL",
        }


def test_calculate_only_does_not_create_database_record() -> None:
    reset_data()

    with SessionLocal() as db:
        compressor_execution_service.execute_selection(
            db,
            organization_id=ensure_test_organization_id(db),
            calculation=build_selection_request(),
            execution=CalculationExecutionMetadata(
                persist_result=False,
            ),
        )

    with SessionLocal() as db:
        stored_cases = db.query(CalculationCase).all()

        assert stored_cases == []
