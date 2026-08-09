from app.models.calculation_case import (
    CalculationCase,
    CalculationStatus,
    CalculationType,
)


def test_calculation_case_table_name() -> None:
    assert CalculationCase.__tablename__ == "calculation_cases"


def test_calculation_case_expected_columns() -> None:
    columns = set(CalculationCase.__table__.columns.keys())

    assert columns == {
        "id",
        "project_id",
        "calculation_code",
        "calculation_type",
        "status",
        "revision",
        "title",
        "description",
        "input_data",
        "result_data",
        "engineering_notes",
        "created_at",
        "updated_at",
        "completed_at",
    }


def test_calculation_type_values() -> None:
    assert {item.value for item in CalculationType} == {
        "COMPRESSION",
        "RECIPROCATING",
        "CENTRIFUGAL",
        "SELECTION",
    }


def test_calculation_status_values() -> None:
    assert {item.value for item in CalculationStatus} == {
        "DRAFT",
        "COMPLETED",
        "SUPERSEDED",
    }


def test_calculation_code_is_unique() -> None:
    column = CalculationCase.__table__.columns["calculation_code"]

    assert column.unique is True


def test_project_id_has_foreign_key() -> None:
    column = CalculationCase.__table__.columns["project_id"]

    foreign_keys = list(column.foreign_keys)

    assert len(foreign_keys) == 1
    assert foreign_keys[0].target_fullname == "projects.id"


def test_jsonb_columns_exist() -> None:
    input_column = CalculationCase.__table__.columns["input_data"]
    result_column = CalculationCase.__table__.columns["result_data"]

    assert input_column.type.__class__.__name__ == "JSONB"
    assert result_column.type.__class__.__name__ == "JSONB"


def test_composite_indexes_exist() -> None:
    indexes = {index.name for index in CalculationCase.__table__.indexes}

    assert "ix_calculation_cases_project_type" in indexes
    assert "ix_calculation_cases_project_status" in indexes
