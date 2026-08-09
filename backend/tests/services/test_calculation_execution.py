from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy import delete

from app.core.database import SessionLocal
from app.models.calculation_case import CalculationCase, CalculationStatus, CalculationType
from app.models.project import Project
from app.schemas.project import ProjectCreate
from app.repositories.project import project_repository
from app.services.calculation_execution import calculation_execution_service


@dataclass(frozen=True, slots=True)
class DummyCalculationResult:
    """Simple calculation result used for persistence testing."""

    shaft_power_kw: Decimal
    driver_power_kw: Decimal
    status: str


def reset_data() -> None:
    with SessionLocal() as db:
        db.execute(delete(CalculationCase))
        db.execute(delete(Project))
        db.commit()


def create_test_project() -> int:
    with SessionLocal() as db:
        project = project_repository.create(
            db,
            ProjectCreate(
                project_code="KESC-EXEC-001",
                project_name="Calculation Execution Test Project",
            ),
        )

        return project.id


def test_persist_completed_calculation_execution() -> None:
    reset_data()

    project_id = create_test_project()

    result = DummyCalculationResult(
        shaft_power_kw=Decimal("19101.2"),
        driver_power_kw=Decimal("21011.32"),
        status="PASS",
    )

    with SessionLocal() as db:
        calculation_case = calculation_execution_service.persist_execution(
            db,
            project_id=project_id,
            calculation_code="EXEC-CALC-001",
            calculation_type=CalculationType.CENTRIFUGAL,
            title="Centrifugal Compressor Calculation",
            input_data={
                "suction_pressure_bar": "30",
                "discharge_pressure_bar": "90",
            },
            result=result,
            engineering_notes="Automated calculation execution test.",
        )

        assert calculation_case.id > 0
        assert calculation_case.project_id == project_id
        assert calculation_case.calculation_code == "EXEC-CALC-001"
        assert calculation_case.calculation_type == CalculationType.CENTRIFUGAL.value
        assert calculation_case.status == CalculationStatus.COMPLETED.value

        assert calculation_case.input_data == {
            "suction_pressure_bar": "30",
            "discharge_pressure_bar": "90",
        }

        assert calculation_case.result_data is not None
        assert calculation_case.result_data["shaft_power_kw"] == "19101.2"
        assert calculation_case.result_data["driver_power_kw"] == "21011.32"
        assert calculation_case.result_data["status"] == "PASS"


def test_persisted_execution_can_be_reloaded() -> None:
    reset_data()

    project_id = create_test_project()

    result = DummyCalculationResult(
        shaft_power_kw=Decimal("1000"),
        driver_power_kw=Decimal("1100"),
        status="PASS",
    )

    with SessionLocal() as db:
        created = calculation_execution_service.persist_execution(
            db,
            project_id=project_id,
            calculation_code="EXEC-CALC-002",
            calculation_type=CalculationType.COMPRESSION,
            title="Compression Calculation",
            input_data={
                "number_of_stages": 3,
            },
            result=result,
        )

        calculation_case_id = created.id

    with SessionLocal() as db:
        stored = db.get(CalculationCase, calculation_case_id)

        assert stored is not None
        assert stored.calculation_code == "EXEC-CALC-002"
        assert stored.result_data is not None
        assert stored.result_data["driver_power_kw"] == "1100"
