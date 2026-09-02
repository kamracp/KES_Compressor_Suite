import pytest
from annotated_types import Le
from pydantic import ValidationError

from app.schemas import (
    auth,
    calculation_case,
    compressed_air_allied,
    compressed_air_assessment,
    compressed_air_brownfield,
    compressed_air_greenfield,
    compressed_air_skid,
    rbac,
    user,
)
from app.schemas._bounds import (
    MAX_CASE_REVISION,
    MAX_DB_INTEGER_ID,
    MAX_LINE_ITEM_QUANTITY,
    MAX_TREATMENT_UNIT_COUNT,
)

CAPPED_FIELDS = [
    (auth.LoginRequest, "organization_id", MAX_DB_INTEGER_ID),
    (rbac.RoleCreate, "organization_id", MAX_DB_INTEGER_ID),
    (rbac.RolePermissionAssignment, "role_id", MAX_DB_INTEGER_ID),
    (rbac.RolePermissionAssignment, "permission_id", MAX_DB_INTEGER_ID),
    (rbac.UserRoleAssignment, "user_id", MAX_DB_INTEGER_ID),
    (rbac.UserRoleAssignment, "role_id", MAX_DB_INTEGER_ID),
    (user.UserCreate, "organization_id", MAX_DB_INTEGER_ID),
    (calculation_case.CalculationCaseBase, "project_id", MAX_DB_INTEGER_ID),
    (calculation_case.CalculationCaseBase, "revision", MAX_CASE_REVISION),
    (calculation_case.CalculationCaseUpdate, "revision", MAX_CASE_REVISION),
    (
        compressed_air_assessment.CompressedAirAssessmentCreateRequest,
        "project_id",
        MAX_DB_INTEGER_ID,
    ),
    (compressed_air_brownfield.BrownfieldSystemAuditRequest, "project_id", MAX_DB_INTEGER_ID),
    (compressed_air_greenfield.AirConsumerInputSchema, "quantity", MAX_LINE_ITEM_QUANTITY),
    (compressed_air_skid.SkidComponentRequest, "quantity", MAX_LINE_ITEM_QUANTITY),
    (
        compressed_air_allied.ReceiverConfigurationRequest,
        "receiver_quantity",
        MAX_LINE_ITEM_QUANTITY,
    ),
    (
        compressed_air_allied.TreatmentConfigurationRequest,
        "installed_unit_count",
        MAX_TREATMENT_UNIT_COUNT,
    ),
    (
        compressed_air_allied.TreatmentConfigurationRequest,
        "duty_unit_count",
        MAX_TREATMENT_UNIT_COUNT,
    ),
]


@pytest.mark.parametrize(
    ("model", "field", "cap"),
    CAPPED_FIELDS,
    ids=[f"{m.__name__}.{f}" for m, f, _ in CAPPED_FIELDS],
)
def test_input_integer_field_carries_its_cap(model, field, cap):
    caps = [c.le for c in model.model_fields[field].metadata if isinstance(c, Le)]
    assert caps == [cap]


def test_db_integer_id_cap_is_enforced_on_login():
    ok = auth.LoginRequest(organization_id=MAX_DB_INTEGER_ID, email="a@b.com", password="x")
    assert ok.organization_id == MAX_DB_INTEGER_ID
    with pytest.raises(ValidationError):
        auth.LoginRequest(organization_id=MAX_DB_INTEGER_ID + 1, email="a@b.com", password="x")
