"""C-7b: schema bounds must agree with the manufacturer evidence registry.

Pydantic bounds are import-time literals, so they cannot read the evidence
JSON directly. This test pins each literal to bound_envelope() so that a
change in either place is caught.
"""

import inspect
from decimal import Decimal

import annotated_types
from pydantic import BaseModel

from app.data.evidence.loader import bound_envelope
from app.schemas import compressor_calculation as module


def _limits(field_name: str) -> list[tuple[str, Decimal | None, Decimal | None]]:
    """Return (model, ge, le) for every model in the module owning the field."""

    found = []
    for name, cls in inspect.getmembers(module, inspect.isclass):
        if not issubclass(cls, BaseModel) or cls is BaseModel:
            continue
        info = cls.model_fields.get(field_name)
        if info is None:
            continue
        ge = le = None
        for meta in info.metadata:
            if isinstance(meta, annotated_types.Ge):
                ge = Decimal(str(meta.ge))
            if isinstance(meta, annotated_types.Le):
                le = Decimal(str(meta.le))
        found.append((name, ge, le))
    return found


def test_screw_discharge_pressure_bound_matches_registry_envelope() -> None:
    limits = _limits("discharge_pressure_bar_g")
    assert limits, "field not found"
    _, envelope_max = bound_envelope("working_pressure_bar_g")
    for _, _, le in limits:
        assert le == Decimal(str(envelope_max))


def test_screw_fad_bound_covers_registry_envelope() -> None:
    _, envelope_max = bound_envelope("fad_m3_min")
    for _, _, le in _limits("rated_fad_m3_per_min"):
        assert le is not None
        assert Decimal(str(envelope_max)) <= le <= Decimal(str(envelope_max)) * Decimal("1.2")


def test_screw_package_power_bound_covers_registry_envelope() -> None:
    _, motor_max = bound_envelope("rated_motor_power_kw")
    _, ratio_max = bound_envelope("package_power_to_nameplate_ratio")
    for _, _, le in _limits("package_input_power_kw"):
        assert le is not None
        assert le >= Decimal(str(motor_max)) * Decimal(str(ratio_max))


def test_reference_conditions_include_iso_1217_point() -> None:
    for _, ge, le in _limits("standard_reference_pressure_bar_a"):
        assert ge <= Decimal("1.0") <= le
    for _, ge, le in _limits("standard_reference_temperature_k"):
        assert ge <= Decimal("293.15") <= le


def test_operating_hours_cannot_exceed_a_leap_year() -> None:
    for _, _, le in _limits("estimated_operating_hours_per_year"):
        assert le == Decimal("8784")


def test_cooling_water_is_liquid_range() -> None:
    for field in ("cooling_water_inlet_temperature_k", "cooling_water_outlet_temperature_k"):
        for _, ge, le in _limits(field):
            assert (ge, le) == (Decimal("273"), Decimal("373"))
