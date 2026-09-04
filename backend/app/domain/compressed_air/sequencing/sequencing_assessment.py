"""Baseline-versus-proposed sequencing assessment (C-7b).

The as-found plant (local setpoints, idle units left running unloaded) and a
proposed central-sequencer scheme (one target band, priority by specific
power with the VSD as trim, auto-standby) are both run through the closed-form
simulator. Savings are reported by component so nothing is claimed that the
simulation did not produce:

* standby saving  - idle units no longer running unloaded (auto-standby rule)
* trim saving     - less unloaded running / better turndown on the trim unit
* pressure saving - lower average header pressure, via the thermodynamic
                    method in energy/pressure_energy.py

Honesty contract: if the proposal simulates worse than the baseline the
saving is reported as zero and the reason is stated.
"""

from dataclasses import dataclass, replace
from decimal import Decimal

from app.domain.compressed_air.energy.pressure_energy import (
    PressureEnergyInput,
    calculate_pressure_energy_saving,
)
from app.domain.compressed_air.profiles.demand_profile import DemandProfilePoint
from app.domain.compressed_air.sequencing.pressure_band_simulator import (
    simulate_pressure_bands,
)
from app.domain.compressed_air.sequencing.sequencing_models import (
    ControlMode,
    InvalidSequencingInputError,
    PressureBand,
    SequencedMachine,
    SequencingInput,
    SequencingResult,
)

_Q4 = Decimal("0.0001")
_ZERO = Decimal("0")
_SIXTY = Decimal("60")


def _q(value: Decimal) -> Decimal:
    return value.quantize(_Q4)


@dataclass(frozen=True, slots=True)
class SequencingAssessmentInput:
    analysis_code: str
    baseline_machines: tuple[SequencedMachine, ...]
    demand_profile: tuple[DemandProfilePoint, ...]
    receiver_volume_m3: Decimal
    electricity_tariff_per_kwh: Decimal
    proposed_band: PressureBand
    annual_operating_hours: Decimal


@dataclass(frozen=True, slots=True)
class SequencingAssessmentResult:
    analysis_code: str
    baseline: SequencingResult
    proposed: SequencingResult
    proposed_machines: tuple[SequencedMachine, ...]
    profile_hours: Decimal
    annualisation_factor: Decimal
    baseline_average_header_pressure_bar_g: Decimal
    proposed_average_header_pressure_bar_g: Decimal
    standby_saving_kwh: Decimal
    trim_saving_kwh: Decimal
    pressure_saving_kwh: Decimal
    total_annual_saving_kwh: Decimal
    total_annual_cost_saving: Decimal
    saving_claimed: bool
    note: str


def specific_power_kw_per_nm3_per_min(machine: SequencedMachine) -> Decimal:
    return machine.rated_power_kw / (machine.rated_fad_nm3_per_hr / _SIXTY)


def propose_central_cascade(
    machines: tuple[SequencedMachine, ...], band: PressureBand
) -> tuple[SequencedMachine, ...]:
    """Fixed-speed units by ascending specific power, VSD units last (trim)."""

    if band.width_bar <= _ZERO:
        raise InvalidSequencingInputError("Proposed band must have positive width.")
    fixed = sorted(
        (m for m in machines if m.control_mode is not ControlMode.VARIABLE_SPEED),
        key=lambda m: (specific_power_kw_per_nm3_per_min(m), m.unit_code),
    )
    variable = sorted(
        (m for m in machines if m.control_mode is ControlMode.VARIABLE_SPEED),
        key=lambda m: (specific_power_kw_per_nm3_per_min(m), m.unit_code),
    )
    return tuple(
        replace(m, band=band, priority=index, standby_runs_unloaded=False)
        for index, m in enumerate(fixed + variable, start=1)
    )


def _duration_weighted_header(result: SequencingResult) -> Decimal:
    hours = sum((p.duration_hours for p in result.periods), _ZERO)
    weighted = sum(
        (p.average_header_pressure_bar_g * p.duration_hours for p in result.periods), _ZERO
    )
    return weighted / hours


def assess_sequencing(inputs: SequencingAssessmentInput) -> SequencingAssessmentResult:
    if inputs.annual_operating_hours <= _ZERO:
        raise InvalidSequencingInputError("Annual operating hours must be positive.")
    proposed_machines = propose_central_cascade(inputs.baseline_machines, inputs.proposed_band)

    def run(machines: tuple[SequencedMachine, ...]) -> SequencingResult:
        return simulate_pressure_bands(
            SequencingInput(
                analysis_code=inputs.analysis_code,
                machines=machines,
                demand_profile=inputs.demand_profile,
                receiver_volume_m3=inputs.receiver_volume_m3,
                electricity_tariff_per_kwh=inputs.electricity_tariff_per_kwh,
            )
        )

    baseline = run(inputs.baseline_machines)
    proposed = run(proposed_machines)

    profile_hours = sum((p.duration_hours for p in inputs.demand_profile), _ZERO)
    factor = inputs.annual_operating_hours / profile_hours

    simulated_saving = baseline.total_energy_kwh - proposed.total_energy_kwh
    standby_saving = baseline.standby_energy_kwh - proposed.standby_energy_kwh
    trim_saving = simulated_saving - standby_saving

    baseline_header = _duration_weighted_header(baseline)
    proposed_header = _duration_weighted_header(proposed)
    # The pressure method only returns savings for a reduction, so a proposal
    # that raises the header is charged the mirror-image penalty.
    higher, lower = max(baseline_header, proposed_header), min(baseline_header, proposed_header)
    reference_power = (
        proposed.total_energy_kwh
        if proposed_header <= baseline_header
        else baseline.total_energy_kwh
    ) / profile_hours
    pressure = calculate_pressure_energy_saving(
        PressureEnergyInput(
            current_discharge_pressure_bar_g=higher,
            optimized_discharge_pressure_bar_g=lower,
            current_average_power_kw=reference_power,
            annual_operating_hours=profile_hours,
            electricity_tariff_per_kwh=inputs.electricity_tariff_per_kwh,
        )
    )
    pressure_saving = pressure.annual_energy_saving_kwh  # over the profile hours
    if proposed_header > baseline_header:
        pressure_saving = -pressure_saving

    total_profile_saving = simulated_saving + pressure_saving
    if proposed.unmet_demand_hours > baseline.unmet_demand_hours:
        claimed, note = False, "Proposed scheme leaves more demand unmet than the baseline."
    elif total_profile_saving <= _ZERO:
        claimed, note = (
            False,
            "Proposed scheme does not reduce energy once the header-pressure effect is included.",
        )
    else:
        claimed, note = (
            True,
            "Savings are the simulated difference plus the header-pressure effect.",
        )
    standby_annual = _q(standby_saving * factor)
    trim_annual = _q(trim_saving * factor)
    pressure_annual = _q(pressure_saving * factor)
    # Report totals from the rounded components so the figures add up on paper.
    annual_saving = standby_annual + trim_annual + pressure_annual if claimed else _ZERO

    return SequencingAssessmentResult(
        analysis_code=inputs.analysis_code,
        baseline=baseline,
        proposed=proposed,
        proposed_machines=proposed_machines,
        profile_hours=_q(profile_hours),
        annualisation_factor=_q(factor),
        baseline_average_header_pressure_bar_g=_q(baseline_header),
        proposed_average_header_pressure_bar_g=_q(proposed_header),
        standby_saving_kwh=standby_annual,
        trim_saving_kwh=trim_annual,
        pressure_saving_kwh=pressure_annual,
        total_annual_saving_kwh=_q(annual_saving),
        total_annual_cost_saving=_q(annual_saving * inputs.electricity_tariff_per_kwh),
        saving_claimed=claimed,
        note=note,
    )
