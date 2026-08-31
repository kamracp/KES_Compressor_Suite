"""
Tests for motor_pfc.py — motor power measurement and PFC sizing.

Manual cross-check (three-phase, IEEE 141):
  V=415V, I=60A, PF=0.78, target PF=0.95
  P = √3 × 415 × 60 × 0.78 / 1000
    = 1.7320508 × 415 × 60 × 0.78 / 1000
    = 33.6329 kW (rounded to 4dp)
  φ1 = arccos(0.78) = 38.739°  tan φ1 = 0.80241
  φ2 = arccos(0.95) = 18.195°  tan φ2 = 0.32868
  Q_c = 33.6329 × (0.80241 − 0.32868) = 15.935 kVAr (approx)

Citation: IEEE Std 141-1993 (Red Book); IS 15167 Part 1.
"""
from decimal import Decimal

import pytest

from app.domain.compressed_air.energy.motor_pfc import (
    InvalidMotorPfcInputError,
    MotorMeasurementInput,
    calculate_motor_pfc,
)


# ---------------------------------------------------------------------------
# Happy-path: 415 V / 60 A / PF 0.78 → target 0.95
# ---------------------------------------------------------------------------

@pytest.fixture
def standard_input() -> MotorMeasurementInput:
    return MotorMeasurementInput(
        measured_voltage_v=Decimal("415"),
        measured_current_a=Decimal("60"),
        measured_power_factor=Decimal("0.78"),
        target_power_factor=Decimal("0.95"),
        rated_motor_power_kw=Decimal("37"),
    )


def test_active_power_formula(standard_input):
    """P = sqrt(3) x V x I x PF / 1000 — matches manual cross-check."""
    result = calculate_motor_pfc(standard_input)
    # Expected: 1.7320508075688 x 415 x 60 x 0.78 / 1000 = 33.6329 kW
    # Tolerance: ±0.01 kW (rounding at 4dp)
    assert abs(result.measured_active_power_kw - Decimal("33.6329")) < Decimal("0.01")


def test_pfc_correction_beneficial(standard_input):
    """PF 0.78 < target 0.95 → correction is beneficial."""
    result = calculate_motor_pfc(standard_input)
    assert result.pfc_correction_beneficial is True


def test_required_capacitor_kvar_positive(standard_input):
    """Capacitor kVAr must be positive when PF is below target."""
    result = calculate_motor_pfc(standard_input)
    assert result.required_capacitor_kvar > 0


def test_required_capacitor_kvar_formula(standard_input):
    """Q_c = P x (tan phi1 - tan phi2) — approx 15.9 kVAr."""
    result = calculate_motor_pfc(standard_input)
    # Rough bounds from manual calc
    assert Decimal("14") < result.required_capacitor_kvar < Decimal("18")


def test_target_reactive_less_than_measured(standard_input):
    """After correction, reactive power demand must fall."""
    result = calculate_motor_pfc(standard_input)
    assert result.target_reactive_power_kvar < result.measured_reactive_power_kvar


def test_nameplate_deviation_computed(standard_input):
    """Deviation from 37 kW nameplate is returned."""
    result = calculate_motor_pfc(standard_input)
    assert result.power_deviation_from_nameplate is not None


def test_nameplate_deviation_sign(standard_input):
    """Measured 33.6 kW < 37 kW nameplate → deviation is negative."""
    result = calculate_motor_pfc(standard_input)
    assert result.power_deviation_from_nameplate < 0


# ---------------------------------------------------------------------------
# PF at or above target — no correction needed
# ---------------------------------------------------------------------------

def test_no_correction_when_pf_meets_target():
    """When measured PF equals target, no correction is needed."""
    inputs = MotorMeasurementInput(
        measured_voltage_v=Decimal("415"),
        measured_current_a=Decimal("60"),
        measured_power_factor=Decimal("0.95"),
        target_power_factor=Decimal("0.95"),
    )
    result = calculate_motor_pfc(inputs)
    assert result.pfc_correction_beneficial is False
    assert result.required_capacitor_kvar == Decimal("0")


def test_no_correction_when_pf_exceeds_target():
    """When measured PF exceeds target, capacitor kVAr is clamped to zero."""
    inputs = MotorMeasurementInput(
        measured_voltage_v=Decimal("415"),
        measured_current_a=Decimal("60"),
        measured_power_factor=Decimal("0.98"),
        target_power_factor=Decimal("0.95"),
    )
    result = calculate_motor_pfc(inputs)
    assert result.required_capacitor_kvar == Decimal("0")
    assert result.pfc_correction_beneficial is False


# ---------------------------------------------------------------------------
# No nameplate — deviation is None
# ---------------------------------------------------------------------------

def test_no_nameplate_deviation_is_none():
    inputs = MotorMeasurementInput(
        measured_voltage_v=Decimal("415"),
        measured_current_a=Decimal("60"),
        measured_power_factor=Decimal("0.85"),
    )
    result = calculate_motor_pfc(inputs)
    assert result.power_deviation_from_nameplate is None


# ---------------------------------------------------------------------------
# Unity PF motor (pure resistive load)
# ---------------------------------------------------------------------------

def test_unity_pf_no_reactive_power():
    """At PF = 1, reactive power is zero and no correction is needed."""
    inputs = MotorMeasurementInput(
        measured_voltage_v=Decimal("415"),
        measured_current_a=Decimal("50"),
        measured_power_factor=Decimal("1"),
        target_power_factor=Decimal("1"),
    )
    result = calculate_motor_pfc(inputs)
    assert result.measured_reactive_power_kvar == pytest.approx(0, abs=1e-4)
    assert result.required_capacitor_kvar == Decimal("0")


# ---------------------------------------------------------------------------
# Validation errors
# ---------------------------------------------------------------------------

def test_zero_voltage_rejected():
    with pytest.raises(InvalidMotorPfcInputError, match="voltage"):
        calculate_motor_pfc(MotorMeasurementInput(
            measured_voltage_v=Decimal("0"),
            measured_current_a=Decimal("50"),
            measured_power_factor=Decimal("0.85"),
        ))


def test_negative_current_rejected():
    with pytest.raises(InvalidMotorPfcInputError, match="current"):
        calculate_motor_pfc(MotorMeasurementInput(
            measured_voltage_v=Decimal("415"),
            measured_current_a=Decimal("-1"),
            measured_power_factor=Decimal("0.85"),
        ))


def test_zero_power_factor_rejected():
    with pytest.raises(InvalidMotorPfcInputError, match="power factor"):
        calculate_motor_pfc(MotorMeasurementInput(
            measured_voltage_v=Decimal("415"),
            measured_current_a=Decimal("50"),
            measured_power_factor=Decimal("0"),
        ))


def test_power_factor_above_one_rejected():
    with pytest.raises(InvalidMotorPfcInputError, match="power factor"):
        calculate_motor_pfc(MotorMeasurementInput(
            measured_voltage_v=Decimal("415"),
            measured_current_a=Decimal("50"),
            measured_power_factor=Decimal("1.01"),
        ))


def test_negative_rated_power_rejected():
    with pytest.raises(InvalidMotorPfcInputError, match="Rated motor power"):
        calculate_motor_pfc(MotorMeasurementInput(
            measured_voltage_v=Decimal("415"),
            measured_current_a=Decimal("50"),
            measured_power_factor=Decimal("0.85"),
            rated_motor_power_kw=Decimal("-5"),
        ))
