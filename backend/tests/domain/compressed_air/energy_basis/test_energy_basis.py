import pytest

from app.domain.compressed_air.energy_basis import (
    NominalSupplyVoltageV,
    SupplyFrequencyHz,
    SupplyPhase,
    supply_basis_options,
    validate_supply_basis,
)


def test_options_follow_is_12360_in_display_order():
    options = supply_basis_options()
    assert options["supply_phase"] == ["single", "three"]
    assert options["nominal_supply_voltage_v"] == [240, 415, 3300, 6600, 11000]
    assert options["supply_frequency_hz"] == [50, 60]


def test_enums_round_trip_from_plain_values():
    assert SupplyPhase("three") is SupplyPhase.THREE
    assert NominalSupplyVoltageV(11000) is NominalSupplyVoltageV.V_11000
    assert SupplyFrequencyHz(50) is SupplyFrequencyHz.HZ_50


@pytest.mark.parametrize(
    ("phase", "voltage"),
    [
        (SupplyPhase.SINGLE, NominalSupplyVoltageV.V_240),
        (SupplyPhase.THREE, NominalSupplyVoltageV.V_415),
        (SupplyPhase.THREE, NominalSupplyVoltageV.V_3300),
        (SupplyPhase.THREE, NominalSupplyVoltageV.V_6600),
        (SupplyPhase.THREE, NominalSupplyVoltageV.V_11000),
    ],
)
def test_is_12360_pairings_are_accepted(phase, voltage):
    validate_supply_basis(phase, voltage)


@pytest.mark.parametrize(
    ("phase", "voltage"),
    [
        (SupplyPhase.THREE, NominalSupplyVoltageV.V_240),
        (SupplyPhase.SINGLE, NominalSupplyVoltageV.V_415),
        (SupplyPhase.SINGLE, NominalSupplyVoltageV.V_11000),
    ],
)
def test_mismatched_pairings_are_rejected(phase, voltage):
    with pytest.raises(ValueError, match="IS 12360"):
        validate_supply_basis(phase, voltage)
