from datetime import date
from typing import Annotated

import pytest
from annotated_types import Le
from pydantic import TypeAdapter, ValidationError

from app.schemas import compressed_air_brownfield, compressor_calculation
from app.schemas._bounds import (
    MAX_CENTRIFUGAL_IMPELLER_STAGES,
    MAX_INSTALLATION_YEAR,
    MAX_RECIP_STAGES,
    MIN_INSTALLATION_YEAR,
)

CASES = [
    (compressor_calculation.CompressionCalculationRequest, "number_of_stages", MAX_RECIP_STAGES),
    (
        compressor_calculation.CentrifugalCalculationRequest,
        "number_of_impeller_stages",
        MAX_CENTRIFUGAL_IMPELLER_STAGES,
    ),
    (
        compressed_air_brownfield.ExistingCompressorInputSchema,
        "installation_year",
        MAX_INSTALLATION_YEAR,
    ),
]


def _adapter(model, field):
    info = model.model_fields[field]
    return TypeAdapter(Annotated[info.annotation, *info.metadata])


@pytest.mark.parametrize(
    ("model", "field", "cap"), CASES, ids=[f"{m.__name__}.{f}" for m, f, _ in CASES]
)
def test_cap_is_declared_and_enforced(model, field, cap):
    assert [c.le for c in model.model_fields[field].metadata if isinstance(c, Le)] == [cap]
    adapter = _adapter(model, field)
    assert adapter.validate_python(cap) == cap
    with pytest.raises(ValidationError):
        adapter.validate_python(cap + 1)


def test_installation_year_window():
    adapter = _adapter(compressed_air_brownfield.ExistingCompressorInputSchema, "installation_year")
    assert date.today().year + 1 == MAX_INSTALLATION_YEAR
    assert adapter.validate_python(None) is None
    assert adapter.validate_python(MIN_INSTALLATION_YEAR) == MIN_INSTALLATION_YEAR
    with pytest.raises(ValidationError):
        adapter.validate_python(MIN_INSTALLATION_YEAR - 1)
