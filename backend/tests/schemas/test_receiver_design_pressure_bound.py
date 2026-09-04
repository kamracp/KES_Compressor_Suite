from decimal import Decimal

import pytest
from annotated_types import Le
from pydantic import TypeAdapter, ValidationError

from app.schemas._bounds import MAX_PLANT_AIR_PRESSURE_BAR_G
from app.schemas.compressed_air_allied import ReceiverConfigurationRequest


def _design_pressure_field():
    return ReceiverConfigurationRequest.model_fields["design_pressure_bar_g"]


def test_receiver_design_pressure_shares_the_plant_air_ceiling():
    caps = [c.le for c in _design_pressure_field().metadata if isinstance(c, Le)]
    assert caps == [MAX_PLANT_AIR_PRESSURE_BAR_G]


def test_receiver_design_pressure_ceiling_is_enforced():
    field = _design_pressure_field()
    adapter = TypeAdapter(__import__("typing").Annotated[field.annotation, *field.metadata])
    assert adapter.validate_python(Decimal("25")) == Decimal("25")
    assert adapter.validate_python(None) is None
    with pytest.raises(ValidationError):
        adapter.validate_python(Decimal("25.01"))
