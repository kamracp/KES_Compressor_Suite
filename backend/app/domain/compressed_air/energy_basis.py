"""Electrical supply basis for compressed-air energy accounting.

Selectable options follow IS 12360 (Voltage bands for electrical
installations including preferred voltages and frequency): LV utilisation
240 V single-phase and 415 V three-phase; HV distribution 3.3 kV, 6.6 kV and
11 kV three-phase; system frequency 50 Hz in India, 60 Hz retained for export
scope. The options are a UI convenience and a consistency check only - no
engine consumes them yet (C-7b, 2 Sep 2026).
"""

from enum import IntEnum, StrEnum


class SupplyPhase(StrEnum):
    SINGLE = "single"
    THREE = "three"


class NominalSupplyVoltageV(IntEnum):
    V_240 = 240
    V_415 = 415
    V_3300 = 3300
    V_6600 = 6600
    V_11000 = 11000


class SupplyFrequencyHz(IntEnum):
    HZ_50 = 50
    HZ_60 = 60


# IS 12360 pairs each preferred voltage with one phase arrangement.
_PHASE_FOR_VOLTAGE: dict[NominalSupplyVoltageV, SupplyPhase] = {
    NominalSupplyVoltageV.V_240: SupplyPhase.SINGLE,
    NominalSupplyVoltageV.V_415: SupplyPhase.THREE,
    NominalSupplyVoltageV.V_3300: SupplyPhase.THREE,
    NominalSupplyVoltageV.V_6600: SupplyPhase.THREE,
    NominalSupplyVoltageV.V_11000: SupplyPhase.THREE,
}


def validate_supply_basis(phase: SupplyPhase, voltage: NominalSupplyVoltageV) -> None:
    """Raise ValueError when the phase/voltage pair is not an IS 12360 pairing."""
    expected = _PHASE_FOR_VOLTAGE[voltage]
    if phase is not expected:
        raise ValueError(
            f"{voltage.value} V is a {expected.value}-phase nominal voltage under "
            f"IS 12360; {phase.value}-phase was given."
        )


def supply_basis_options() -> dict[str, list[str] | list[int]]:
    """Serialisable option lists for the frontend reference endpoint."""
    return {
        "supply_phase": [p.value for p in SupplyPhase],
        "nominal_supply_voltage_v": [v.value for v in NominalSupplyVoltageV],
        "supply_frequency_hz": [f.value for f in SupplyFrequencyHz],
    }
