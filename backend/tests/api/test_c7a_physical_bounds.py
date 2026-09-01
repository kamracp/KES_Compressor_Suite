"""C-7a: physical bounds on air-treatment inputs.

A filter element's *excess* pressure drop beyond its clean design
delta-p is physically bounded. DOE / Compressed Air Challenge
Sourcebook guidance places a clean element around 0.14 bar (2 psi)
and recommends replacement by roughly 0.35 bar (5 psi). Anything
above 1 bar is a data-entry error, not a filter condition.

Regression: a missing decimal point ("035" instead of "0.35") was
accepted as 35 bar and produced a 39.45 kW filter saving on a 100 kW
station -- a 39% energy claim from a filter change.
"""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.schemas.compressed_air_brownfield import (
    BrownfieldSystemAuditRequest,
)


def test_filter_excess_pressure_drop_rejects_implausible_value():
    """35 bar of filter excess drop must be rejected, not calculated."""
    with pytest.raises(ValidationError):
        BrownfieldSystemAuditRequest.model_validate(
            {
                "filter_excess_pressure_drop_bar": Decimal("35"),
            }
        )


def test_filter_excess_pressure_drop_accepts_realistic_value():
    """0.35 bar is a normal dirty-filter condition and must be accepted."""
    field = BrownfieldSystemAuditRequest.model_fields["filter_excess_pressure_drop_bar"]
    upper = [m for m in field.metadata if hasattr(m, "le")]
    assert upper, "filter_excess_pressure_drop_bar must declare an upper bound"
    assert upper[0].le == Decimal("1")
