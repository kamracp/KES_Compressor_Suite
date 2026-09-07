"""Part-load power curves for compressor capacity-control modes (C-8).

One module holds every curve so the sequencing simulator, the brownfield
energy baseline and the performance engine cannot drift apart. Every
constant is a cited guideline value from schemas/_bounds.py
(DOE-CAC-SOURCEBOOK-2003, CAGI-CENTRIFUGAL-CAPACITY-CONTROLS,
ATLASCOPCO-CAM-9ED-2019); every machine-specific figure is an input.

Time-averaged, steady-demand model per demand period:

* LOAD_UNLOAD      P = f_u + (1 - f_u) * q. Instantaneous load/unload with no
                   blowdown transient, i.e. the large-storage asymptote of the
                   DOE storage family. The storage-dependent penalty needs the
                   receiver cycle model (sequencing simulator) and the optional
                   unload_blowdown_seconds input carried on the curve.
* MODULATION       P = 0.70 + 0.30 * q down to the modulation floor (DOE
                   Fig. 2.6: 40 % then unload; Atlas Copco: 10 % possible);
                   below the floor the machine cycles between the floor point
                   and unloaded.
* VARIABLE_DISPLACEMENT  P = q over the first 50 % of capacity (turn / spiral /
                   poppet valve keeps the compression ratio stable, DOE); below
                   50 % load/unload cycling between the floor point and unloaded.
* VARIABLE_SPEED   P linear from (q_min, p_min) to (1, 1); below q_min the unit
                   cycles at minimum speed against unloaded.
* INLET_GUIDE_VANE P linear from (q_td, p_td) to (1, 1); below the turndown
                   flow either BLOW_OFF (power stays at p_td, surplus air is
                   vented - CAGI, Atlas Copco "energy consumption unchanged")
                   or UNLOAD (auto-dual: cycles between p_td and the off-loaded
                   power fraction).

All fractions are relative to rated FAD and rated (full-load) power.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from enum import StrEnum

from app.schemas._bounds import (
    DEFAULT_MODULATION_FLOOR_CAPACITY_FRACTION,
    MAX_CENTRIFUGAL_TURNDOWN_FRACTION,
    MAX_CENTRIFUGAL_UNLOAD_POWER_FRACTION,
    MAX_FIXED_SPEED_UNLOAD_POWER_FRACTION,
    MAX_MODULATION_FLOOR_CAPACITY_FRACTION,
    MIN_CENTRIFUGAL_POWER_FRACTION_AT_TURNDOWN,
    MIN_CENTRIFUGAL_TURNDOWN_FRACTION,
    MIN_CENTRIFUGAL_UNLOAD_POWER_FRACTION,
    MIN_FIXED_SPEED_UNLOAD_POWER_FRACTION,
    MIN_MODULATION_FLOOR_CAPACITY_FRACTION,
    MIN_VSD_MINIMUM_FLOW_FRACTION,
    MODULATION_ZERO_FLOW_POWER_FRACTION,
    VARIABLE_DISPLACEMENT_FLOOR_CAPACITY_FRACTION,
)

ZERO = Decimal("0")
ONE = Decimal("1")
QUANTUM = Decimal("0.0001")


class InvalidPartLoadInputError(ValueError):
    """Raised when a part-load curve or operating point is not physical."""


class PartLoadMode(StrEnum):
    """Capacity-control mode whose part-load curve is modelled."""

    LOAD_UNLOAD = "LOAD_UNLOAD"
    MODULATION = "MODULATION"
    VARIABLE_DISPLACEMENT = "VARIABLE_DISPLACEMENT"
    VARIABLE_SPEED = "VARIABLE_SPEED"
    INLET_GUIDE_VANE = "INLET_GUIDE_VANE"


class BelowTurndownMode(StrEnum):
    """What a centrifugal machine does once demand falls below its turndown."""

    BLOW_OFF = "BLOW_OFF"
    UNLOAD = "UNLOAD"


@dataclass(frozen=True, slots=True)
class PartLoadCurve:
    """Per-machine description of one capacity-control curve."""

    mode: PartLoadMode

    # LOAD_UNLOAD / MODULATION / VARIABLE_DISPLACEMENT / VARIABLE_SPEED:
    # off-loaded power as a fraction of full-load power (screw 0.15-0.35).
    # INLET_GUIDE_VANE with UNLOAD: centrifugal off-loaded power (0.05-0.35).
    unload_power_fraction: Decimal | None = None

    # MODULATION only: capacity fraction where throttling stops and the
    # machine unloads (DOE 0.40 default; Atlas Copco down to 0.10).
    modulation_floor_capacity_fraction: Decimal = DEFAULT_MODULATION_FLOOR_CAPACITY_FRACTION

    # VARIABLE_SPEED only (CAGI datasheet points).
    minimum_flow_fraction: Decimal | None = None
    minimum_flow_power_fraction: Decimal | None = None

    # INLET_GUIDE_VANE only (machine specific per CAGI).
    turndown_flow_fraction: Decimal | None = None
    power_fraction_at_turndown: Decimal | None = None
    below_turndown: BelowTurndownMode = BelowTurndownMode.BLOW_OFF

    # LOAD_UNLOAD only, optional, manufacturer supplied: sump blowdown time.
    # Not used by the steady-state curve; carried for the receiver cycle model.
    unload_blowdown_seconds: Decimal | None = None


@dataclass(frozen=True, slots=True)
class PartLoadPoint:
    """Time-averaged operating point for one demand level."""

    mode: PartLoadMode
    capacity_fraction: Decimal
    power_fraction: Decimal
    delivered_fraction: Decimal
    wasted_flow_fraction: Decimal
    regime: str


def _q(value: Decimal) -> Decimal:
    return value.quantize(QUANTUM, rounding=ROUND_HALF_UP)


def _require_range(name: str, value: Decimal | None, low: Decimal, high: Decimal) -> Decimal:
    if value is None:
        raise InvalidPartLoadInputError(f"{name} is required for this control mode.")
    if not (low <= value <= high):
        raise InvalidPartLoadInputError(f"{name} must be within {low} and {high}, got {value}.")
    return value


def _require_absent(name: str, value: object, mode: PartLoadMode) -> None:
    if value is not None:
        raise InvalidPartLoadInputError(f"{name} does not apply to {mode.value}.")


def validate_curve(curve: PartLoadCurve) -> None:
    """Reject curves whose inputs fall outside the cited bounds."""
    mode = curve.mode

    if mode is PartLoadMode.INLET_GUIDE_VANE:
        turndown = _require_range(
            "turndown_flow_fraction",
            curve.turndown_flow_fraction,
            MIN_CENTRIFUGAL_TURNDOWN_FRACTION,
            MAX_CENTRIFUGAL_TURNDOWN_FRACTION,
        )
        _require_range(
            "power_fraction_at_turndown",
            curve.power_fraction_at_turndown,
            MIN_CENTRIFUGAL_POWER_FRACTION_AT_TURNDOWN,
            ONE,
        )
        if curve.below_turndown is BelowTurndownMode.UNLOAD:
            _require_range(
                "unload_power_fraction",
                curve.unload_power_fraction,
                MIN_CENTRIFUGAL_UNLOAD_POWER_FRACTION,
                MAX_CENTRIFUGAL_UNLOAD_POWER_FRACTION,
            )
        _require_absent("minimum_flow_fraction", curve.minimum_flow_fraction, mode)
        _require_absent("minimum_flow_power_fraction", curve.minimum_flow_power_fraction, mode)
        _require_absent("unload_blowdown_seconds", curve.unload_blowdown_seconds, mode)
        del turndown
        return

    _require_range(
        "unload_power_fraction",
        curve.unload_power_fraction,
        MIN_FIXED_SPEED_UNLOAD_POWER_FRACTION,
        MAX_FIXED_SPEED_UNLOAD_POWER_FRACTION,
    )
    _require_absent("turndown_flow_fraction", curve.turndown_flow_fraction, mode)
    _require_absent("power_fraction_at_turndown", curve.power_fraction_at_turndown, mode)

    if mode is PartLoadMode.VARIABLE_SPEED:
        _require_range(
            "minimum_flow_fraction",
            curve.minimum_flow_fraction,
            MIN_VSD_MINIMUM_FLOW_FRACTION,
            ONE,
        )
        power = _require_range(
            "minimum_flow_power_fraction", curve.minimum_flow_power_fraction, ZERO, ONE
        )
        if power <= ZERO:
            raise InvalidPartLoadInputError("minimum_flow_power_fraction must be above 0.")
    else:
        _require_absent("minimum_flow_fraction", curve.minimum_flow_fraction, mode)
        _require_absent("minimum_flow_power_fraction", curve.minimum_flow_power_fraction, mode)

    if mode is PartLoadMode.MODULATION:
        _require_range(
            "modulation_floor_capacity_fraction",
            curve.modulation_floor_capacity_fraction,
            MIN_MODULATION_FLOOR_CAPACITY_FRACTION,
            MAX_MODULATION_FLOOR_CAPACITY_FRACTION,
        )

    if mode is not PartLoadMode.LOAD_UNLOAD and curve.unload_blowdown_seconds is not None:
        raise InvalidPartLoadInputError("unload_blowdown_seconds applies to LOAD_UNLOAD only.")
    if curve.unload_blowdown_seconds is not None and curve.unload_blowdown_seconds < ZERO:
        raise InvalidPartLoadInputError("unload_blowdown_seconds cannot be negative.")


def _cycling_power(
    duty: Decimal, loaded_power_fraction: Decimal, unloaded_power_fraction: Decimal
) -> Decimal:
    """Time-average of a machine alternating between two power levels."""
    return duty * loaded_power_fraction + (ONE - duty) * unloaded_power_fraction


def part_load_point(curve: PartLoadCurve, capacity_fraction: Decimal) -> PartLoadPoint:
    """Time-averaged power for a demand equal to capacity_fraction x rated FAD."""
    validate_curve(curve)
    if not (ZERO <= capacity_fraction <= ONE):
        raise InvalidPartLoadInputError("capacity_fraction must be within 0 and 1.")

    q = capacity_fraction
    mode = curve.mode
    f_unload = curve.unload_power_fraction if curve.unload_power_fraction is not None else ZERO
    wasted = ZERO

    if mode is PartLoadMode.LOAD_UNLOAD:
        power = _cycling_power(q, ONE, f_unload)
        regime = "load/unload cycling" if ZERO < q < ONE else ("loaded" if q == ONE else "unloaded")

    elif mode is PartLoadMode.MODULATION:
        floor = curve.modulation_floor_capacity_fraction
        slope = ONE - MODULATION_ZERO_FLOW_POWER_FRACTION
        if q >= floor:
            power = MODULATION_ZERO_FLOW_POWER_FRACTION + slope * q
            regime = "inlet modulation"
        else:
            floor_power = MODULATION_ZERO_FLOW_POWER_FRACTION + slope * floor
            power = _cycling_power(q / floor, floor_power, f_unload)
            regime = "modulation floor / unload cycling"

    elif mode is PartLoadMode.VARIABLE_DISPLACEMENT:
        floor = VARIABLE_DISPLACEMENT_FLOOR_CAPACITY_FRACTION
        if q >= floor:
            power = q
            regime = "variable displacement"
        else:
            power = _cycling_power(q / floor, floor, f_unload)
            regime = "displacement floor / unload cycling"

    elif mode is PartLoadMode.VARIABLE_SPEED:
        q_min = curve.minimum_flow_fraction
        p_min = curve.minimum_flow_power_fraction
        assert q_min is not None and p_min is not None  # validated above
        if q >= q_min:
            power = (
                ONE if q_min == ONE else p_min + (ONE - p_min) * (q - q_min) / (ONE - q_min)
            )
            regime = "speed regulation"
        else:
            power = _cycling_power(q / q_min, p_min, f_unload)
            regime = "minimum speed / unload cycling"

    else:  # INLET_GUIDE_VANE
        turndown = curve.turndown_flow_fraction
        p_td = curve.power_fraction_at_turndown
        assert turndown is not None and p_td is not None  # validated above
        q_td = ONE - turndown
        if q >= q_td:
            power = p_td + (ONE - p_td) * (q - q_td) / turndown
            regime = "inlet guide vane throttling"
        elif curve.below_turndown is BelowTurndownMode.BLOW_OFF:
            power = p_td
            wasted = q_td - q
            regime = "blow-off"
        else:
            power = _cycling_power(q / q_td, p_td, f_unload)
            regime = "auto-dual unload cycling"

    return PartLoadPoint(
        mode=mode,
        capacity_fraction=_q(q),
        power_fraction=_q(power),
        delivered_fraction=_q(q),
        wasted_flow_fraction=_q(wasted),
        regime=regime,
    )
