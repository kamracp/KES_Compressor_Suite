"""
Motor power measurement and power-factor correction (PFC) sizing.

Physics
-------
Three-phase active power (IEEE 141 / IS 1180):
    P = √3 × V_L × I_L × PF      [W]  →  kW = P / 1000

Reactive power required to improve PF from PF1 to PF2 (IS 15167):
    Q_c = P × (tan φ1 − tan φ2)   [kVAr]

Where φ1 = arccos(PF1), φ2 = arccos(PF2).

Citations
---------
- IEEE Std 141-1993 (Red Book): Recommended Practice for Electric Power
  Distribution for Industrial Plants. §3 motor power formula.
- IS 1180: Indian Standard — Outdoor-type oil-immersed distribution
  transformers and PF correction guidelines.
- IS 15167 (Part 1): Shunt power capacitors for AC power systems — used
  for kVAr sizing methodology.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from decimal import Decimal


class InvalidMotorPfcInputError(ValueError):
    """Raised when motor or PFC inputs are invalid."""


SQRT3 = Decimal("1.7320508075688772935")  # √3, 19 significant figures


@dataclass(frozen=True, slots=True)
class MotorMeasurementInput:
    """
    Field-measured electrical parameters of a compressor motor.

    All values are line quantities (line voltage, line current) for a
    three-phase motor.  Single-phase motors are not in scope for this
    module.
    """

    # Measured line-to-line voltage (V)
    measured_voltage_v: Decimal

    # Measured line current (A)
    measured_current_a: Decimal

    # Measured power factor (0 < PF ≤ 1)
    measured_power_factor: Decimal

    # Target power factor after correction (0 < PF ≤ 1, must be ≥ measured)
    target_power_factor: Decimal = Decimal("0.95")

    # Motor nameplate rated power (kW) — used for deviation check only
    rated_motor_power_kw: Decimal | None = None


@dataclass(frozen=True, slots=True)
class MotorMeasurementResult:
    """Calculated motor power and PFC sizing from field measurements."""

    measured_voltage_v: Decimal
    measured_current_a: Decimal
    measured_power_factor: Decimal
    target_power_factor: Decimal

    # Three-phase active power: √3 × V × I × PF / 1000  (kW)
    measured_active_power_kw: Decimal

    # Reactive power drawn at current PF (kVAr)
    measured_reactive_power_kvar: Decimal

    # Reactive power that would be drawn at target PF (kVAr)
    target_reactive_power_kvar: Decimal

    # Capacitor bank required: Q_c = P × (tan φ1 − tan φ2)  (kVAr)
    required_capacitor_kvar: Decimal

    # True when measured PF is below target (correction is beneficial)
    pfc_correction_beneficial: bool

    # Deviation of measured power from nameplate (fraction); None if no
    # nameplate power was provided.
    power_deviation_from_nameplate: Decimal | None


def calculate_motor_pfc(
    inputs: MotorMeasurementInput,
) -> MotorMeasurementResult:
    """
    Calculate motor active power from field measurements and size the
    PFC capacitor bank required to reach the target power factor.

    Formula (three-phase, IEEE 141):
        P_kW = √3 × V_L × I_L × PF / 1000

    PFC sizing (IS 15167):
        Q_c = P_kW × (tan(arccos(PF1)) − tan(arccos(PF2)))
    """
    _validate_inputs(inputs)

    # ── Active power ──────────────────────────────────────────────────────
    active_power_kw = (
        SQRT3
        * inputs.measured_voltage_v
        * inputs.measured_current_a
        * inputs.measured_power_factor
        / Decimal("1000")
    )

    # ── Reactive power at measured PF ─────────────────────────────────────
    phi1 = Decimal(str(math.acos(float(inputs.measured_power_factor))))
    tan_phi1 = Decimal(str(math.tan(float(phi1))))
    reactive_power_kvar = active_power_kw * tan_phi1

    # ── Reactive power at target PF ───────────────────────────────────────
    phi2 = Decimal(str(math.acos(float(inputs.target_power_factor))))
    tan_phi2 = Decimal(str(math.tan(float(phi2))))
    target_reactive_kvar = active_power_kw * tan_phi2

    # ── Capacitor bank required ───────────────────────────────────────────
    required_capacitor_kvar = active_power_kw * (tan_phi1 - tan_phi2)

    # Clamp to zero: if measured PF ≥ target, no correction needed
    if required_capacitor_kvar < 0:
        required_capacitor_kvar = Decimal("0")

    pfc_beneficial = (
        inputs.measured_power_factor < inputs.target_power_factor
        and required_capacitor_kvar > 0
    )

    # ── Nameplate deviation ───────────────────────────────────────────────
    if inputs.rated_motor_power_kw is not None and inputs.rated_motor_power_kw > 0:
        power_deviation = (
            (active_power_kw - inputs.rated_motor_power_kw)
            / inputs.rated_motor_power_kw
        )
    else:
        power_deviation = None

    return MotorMeasurementResult(
        measured_voltage_v=inputs.measured_voltage_v,
        measured_current_a=inputs.measured_current_a,
        measured_power_factor=inputs.measured_power_factor,
        target_power_factor=inputs.target_power_factor,
        measured_active_power_kw=_round4(active_power_kw),
        measured_reactive_power_kvar=_round4(reactive_power_kvar),
        target_reactive_power_kvar=_round4(target_reactive_kvar),
        required_capacitor_kvar=_round4(required_capacitor_kvar),
        pfc_correction_beneficial=pfc_beneficial,
        power_deviation_from_nameplate=(
            _round4(power_deviation) if power_deviation is not None else None
        ),
    )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _round4(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.0001"))


def _validate_inputs(inputs: MotorMeasurementInput) -> None:
    if inputs.measured_voltage_v <= 0:
        raise InvalidMotorPfcInputError("Measured voltage must be greater than zero.")

    if inputs.measured_current_a < 0:
        raise InvalidMotorPfcInputError("Measured current cannot be negative.")

    if not (Decimal("0") < inputs.measured_power_factor <= Decimal("1")):
        raise InvalidMotorPfcInputError(
            "Measured power factor must be between 0 (exclusive) and 1 (inclusive)."
        )

    if not (Decimal("0") < inputs.target_power_factor <= Decimal("1")):
        raise InvalidMotorPfcInputError(
            "Target power factor must be between 0 (exclusive) and 1 (inclusive)."
        )

    if inputs.rated_motor_power_kw is not None and inputs.rated_motor_power_kw <= 0:
        raise InvalidMotorPfcInputError(
            "Rated motor power, when provided, must be greater than zero."
        )
