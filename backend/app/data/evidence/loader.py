"""Loader for manufacturer evidence sets (JSON) shipped inside the package.

Evidence sets are vendor-published technical data used as the documented
basis for physical input bounds (mission C-7b) and for independent check
cases. They are reference material only and must never be used as
calculation constants or defaults. Every set must have a matching entry in
the standards registry with authority MANUFACTURER, so that any bound
derived from it carries a citable identifier.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import cache
from importlib import resources
from typing import Any

from app.domain.compliance.standards_registry import (
    StandardAuthority,
    get_standard,
)

_PACKAGE = "app.data.evidence.manufacturer"


@dataclass(frozen=True, slots=True)
class DerivedBound:
    """One physical bound derived from a manufacturer evidence set."""

    evidence_set_id: str
    parameter: str
    applies_to: str
    minimum: float | None
    maximum: float | None
    basis: str
    note: str | None


def list_evidence_files() -> tuple[str, ...]:
    """Return the JSON evidence file names bundled with the package."""

    names = (
        entry.name for entry in resources.files(_PACKAGE).iterdir() if entry.name.endswith(".json")
    )
    return tuple(sorted(names))


@cache
def load_evidence_file(file_name: str) -> dict[str, Any]:
    """Load one evidence JSON file and validate its registry linkage."""

    text = resources.files(_PACKAGE).joinpath(file_name).read_text(encoding="utf-8")
    data: dict[str, Any] = json.loads(text)

    evidence_id = data.get("evidence_set_id")
    if not isinstance(evidence_id, str) or not evidence_id:
        raise ValueError(f"{file_name}: missing evidence_set_id")

    entry = get_standard(evidence_id)
    if entry is None:
        raise ValueError(f"{file_name}: evidence_set_id {evidence_id!r} has no registry entry")
    if entry.authority is not StandardAuthority.MANUFACTURER:
        raise ValueError(
            f"{file_name}: registry entry {evidence_id!r} must have "
            f"authority MANUFACTURER, got {entry.authority}"
        )
    if data.get("kind") != "manufacturer_evidence":
        raise ValueError(f"{file_name}: kind must be 'manufacturer_evidence'")
    return data


@cache
def load_all_evidence() -> dict[str, dict[str, Any]]:
    """Return every bundled evidence set keyed by evidence_set_id."""

    loaded: dict[str, dict[str, Any]] = {}
    for file_name in list_evidence_files():
        data = load_evidence_file(file_name)
        evidence_id = data["evidence_set_id"]
        if evidence_id in loaded:
            raise ValueError(f"duplicate evidence_set_id {evidence_id!r}")
        loaded[evidence_id] = data
    return loaded


def get_evidence(evidence_set_id: str) -> dict[str, Any]:
    """Return one evidence set by id; raises KeyError if absent."""

    return load_all_evidence()[evidence_set_id.strip().upper()]


def derived_bounds(parameter: str | None = None) -> tuple[DerivedBound, ...]:
    """Return derived bounds across all evidence sets, optionally by parameter."""

    bounds: list[DerivedBound] = []
    for evidence_id, data in load_all_evidence().items():
        for raw in data.get("derived_bounds_for_c7b", ()):
            if parameter is not None and raw.get("parameter") != parameter:
                continue
            bounds.append(
                DerivedBound(
                    evidence_set_id=evidence_id,
                    parameter=raw["parameter"],
                    applies_to=raw.get("applies_to", ""),
                    minimum=raw.get("min"),
                    maximum=raw.get("max"),
                    basis=raw.get("basis", ""),
                    note=raw.get("note"),
                )
            )
    return tuple(bounds)


def bound_envelope(parameter: str) -> tuple[float | None, float | None]:
    """Widest (min, max) envelope for a parameter across all vendors.

    The envelope is the union of vendor ranges: lowest documented minimum
    and highest documented maximum. Returns (None, None) if no vendor
    documents the parameter.
    """

    mins = [b.minimum for b in derived_bounds(parameter) if b.minimum is not None]
    maxs = [b.maximum for b in derived_bounds(parameter) if b.maximum is not None]
    return (min(mins) if mins else None, max(maxs) if maxs else None)
