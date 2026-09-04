"""Closed-form pressure-band sequencing over a stepped demand profile (C-7a).

Demand is constant within each DemandProfilePoint, so the steady state of a
cascaded set of machines follows from a mass balance rather than a time-step
integration: every machine above the cycling unit runs fully loaded, the
cycling unit's load duty equals residual demand over its capacity, and its
load/unload cycle time follows from the receiver volume and the band width
(isothermal receiver, free air referred to atmospheric pressure).
"""

from decimal import Decimal

from app.domain.compressed_air.energy.pressure_energy import ATMOSPHERIC_PRESSURE_BAR
from app.domain.compressed_air.sequencing.sequencing_models import (
    ControlMode,
    DutyRole,
    InvalidSequencingInputError,
    MachinePeriodResult,
    PeriodResult,
    SequencedMachine,
    SequencingInput,
    SequencingResult,
)

_Q4 = Decimal("0.0001")
_ZERO = Decimal("0")
_ONE = Decimal("1")


def _q(value: Decimal) -> Decimal:
    return value.quantize(_Q4)


def _validate(inputs: SequencingInput) -> None:
    if not inputs.machines:
        raise InvalidSequencingInputError("At least one machine is required.")
    if not inputs.demand_profile:
        raise InvalidSequencingInputError("At least one demand period is required.")
    if inputs.receiver_volume_m3 <= _ZERO:
        raise InvalidSequencingInputError("Receiver volume must be greater than zero.")
    codes = [m.unit_code for m in inputs.machines]
    if len(set(codes)) != len(codes):
        raise InvalidSequencingInputError("Machine unit codes must be unique.")
    for m in inputs.machines:
        if m.rated_fad_nm3_per_hr <= _ZERO or m.rated_power_kw <= _ZERO:
            raise InvalidSequencingInputError(
                f"{m.unit_code}: rated FAD and power must be positive."
            )
        if m.band.width_bar <= _ZERO:
            raise InvalidSequencingInputError(
                f"{m.unit_code}: unload pressure must exceed load pressure."
            )
        if m.unload_power_fraction is None or not (_ZERO <= m.unload_power_fraction < _ONE):
            raise InvalidSequencingInputError(
                f"{m.unit_code}: unload_power_fraction is required and must be in [0, 1)."
            )
        if m.control_mode is ControlMode.VARIABLE_SPEED:
            if m.minimum_flow_fraction is None or not (_ZERO < m.minimum_flow_fraction <= _ONE):
                raise InvalidSequencingInputError(
                    f"{m.unit_code}: VSD minimum_flow_fraction must be in (0, 1]."
                )
            if m.minimum_flow_power_fraction is None or not (
                _ZERO < m.minimum_flow_power_fraction <= _ONE
            ):
                raise InvalidSequencingInputError(
                    f"{m.unit_code}: VSD minimum_flow_power_fraction must be in (0, 1]."
                )
    for point in inputs.demand_profile:
        if point.demand_nm3_per_hr < _ZERO or point.duration_hours <= _ZERO:
            raise InvalidSequencingInputError(
                f"Period {point.period_index}: demand must be >= 0 and duration > 0."
            )


def cascade_order(machines: tuple[SequencedMachine, ...]) -> tuple[SequencedMachine, ...]:
    """Highest load setpoint first: it loads first as header pressure falls."""

    if all(m.priority is not None for m in machines):
        return tuple(sorted(machines, key=lambda m: (m.priority, m.unit_code)))
    if any(m.priority is not None for m in machines):
        raise InvalidSequencingInputError("Set priority on every machine or on none.")
    return tuple(
        sorted(
            machines,
            key=lambda m: (-m.band.load_pressure_bar_g, -m.band.unload_pressure_bar_g, m.unit_code),
        )
    )


def _cycles_per_hour(
    receiver_volume_m3: Decimal,
    band_width_bar: Decimal,
    supply_nm3_per_hr: Decimal,
    demand_nm3_per_hr: Decimal,
) -> Decimal:
    """Load/unload cycles per hour for a unit cycling between its setpoints."""

    surplus = supply_nm3_per_hr - demand_nm3_per_hr
    if surplus <= _ZERO or demand_nm3_per_hr <= _ZERO:
        return _ZERO  # continuously loaded or continuously unloaded: no cycling
    stored_free_air_nm3 = receiver_volume_m3 * band_width_bar / ATMOSPHERIC_PRESSURE_BAR
    t_up = stored_free_air_nm3 / surplus
    t_down = stored_free_air_nm3 / demand_nm3_per_hr
    return _ONE / (t_up + t_down)


def _fixed_speed_cycling(
    machine: SequencedMachine,
    residual_nm3_per_hr: Decimal,
    receiver_volume_m3: Decimal,
) -> tuple[Decimal, Decimal, Decimal]:
    """Return (load_fraction, cycles_per_hour, average_power_kw)."""

    assert machine.unload_power_fraction is not None
    load_fraction = residual_nm3_per_hr / machine.rated_fad_nm3_per_hr
    cycles = _cycles_per_hour(
        receiver_volume_m3,
        machine.band.width_bar,
        machine.rated_fad_nm3_per_hr,
        residual_nm3_per_hr,
    )
    power = machine.rated_power_kw * (
        load_fraction + (_ONE - load_fraction) * machine.unload_power_fraction
    )
    return load_fraction, cycles, power


def _vsd_trim(
    machine: SequencedMachine,
    residual_nm3_per_hr: Decimal,
    receiver_volume_m3: Decimal,
) -> tuple[Decimal, Decimal | None, Decimal]:
    """Return (load_fraction, cycles_per_hour or None, average_power_kw)."""

    assert machine.minimum_flow_fraction is not None
    assert machine.minimum_flow_power_fraction is not None
    assert machine.unload_power_fraction is not None
    q_min = machine.rated_fad_nm3_per_hr * machine.minimum_flow_fraction
    p_min = machine.rated_power_kw * machine.minimum_flow_power_fraction
    if residual_nm3_per_hr >= q_min:
        span = machine.rated_fad_nm3_per_hr - q_min
        ratio = _ZERO if span == _ZERO else (residual_nm3_per_hr - q_min) / span
        return _ONE, None, p_min + (machine.rated_power_kw - p_min) * ratio
    # Below minimum flow the drive cycles at minimum speed.
    load_fraction = residual_nm3_per_hr / q_min
    cycles = _cycles_per_hour(
        receiver_volume_m3, machine.band.width_bar, q_min, residual_nm3_per_hr
    )
    power = p_min * load_fraction + machine.rated_power_kw * machine.unload_power_fraction * (
        _ONE - load_fraction
    )
    return load_fraction, cycles, power


def _designated_trim(order: tuple[SequencedMachine, ...]) -> SequencedMachine | None:
    """With explicit priorities and exactly one VSD, that VSD is the trim unit."""

    if not all(m.priority is not None for m in order):
        return None
    vsds = [m for m in order if m.control_mode is ControlMode.VARIABLE_SPEED]
    return vsds[0] if len(vsds) == 1 else None


def _stands_down_for_trim(
    machine: SequencedMachine, trim: SequencedMachine | None, residual: Decimal
) -> bool:
    """A fixed-speed unit stays off when the trim VSD can carry the residual."""

    if trim is None or machine is trim or machine.control_mode is ControlMode.VARIABLE_SPEED:
        return False
    assert trim.minimum_flow_fraction is not None
    if residual > trim.rated_fad_nm3_per_hr:
        return False  # trim cannot carry it alone; this unit must load
    q_min = trim.rated_fad_nm3_per_hr * trim.minimum_flow_fraction
    return (
        residual < machine.rated_fad_nm3_per_hr or residual - machine.rated_fad_nm3_per_hr < q_min
    )


def simulate_pressure_bands(inputs: SequencingInput) -> SequencingResult:
    _validate(inputs)
    order = cascade_order(inputs.machines)
    periods: list[PeriodResult] = []
    total_energy = _ZERO
    unload_energy = _ZERO
    standby_energy = _ZERO
    unmet_hours = _ZERO
    supplied_volume = _ZERO
    total_hours = _ZERO

    trim = _designated_trim(order)
    for point in inputs.demand_profile:
        residual = point.demand_nm3_per_hr
        machine_results: list[MachinePeriodResult] = []
        header_pressure: Decimal | None = None
        period_power = _ZERO
        period_unload_power = _ZERO
        period_standby_power = _ZERO
        supplied = _ZERO

        for machine in order:
            if residual <= _ZERO:
                standby_power = (
                    machine.rated_power_kw * machine.unload_power_fraction
                    if machine.standby_runs_unloaded and machine.unload_power_fraction is not None
                    else _ZERO
                )
                role, flow, load_fraction, cycles, power = (
                    DutyRole.STANDBY,
                    _ZERO,
                    _ZERO,
                    None,
                    standby_power,
                )
                period_standby_power += standby_power
            elif _stands_down_for_trim(machine, trim, residual):
                role, flow, load_fraction, cycles, power = (
                    DutyRole.STANDBY,
                    _ZERO,
                    _ZERO,
                    None,
                    _ZERO,
                )
            elif residual >= machine.rated_fad_nm3_per_hr:
                role, flow, load_fraction, cycles, power = (
                    DutyRole.BASE,
                    machine.rated_fad_nm3_per_hr,
                    _ONE,
                    None,
                    machine.rated_power_kw,
                )
            else:
                role, flow = DutyRole.TRIM, residual
                if machine.control_mode is ControlMode.VARIABLE_SPEED:
                    load_fraction, cycles, power = _vsd_trim(
                        machine, residual, inputs.receiver_volume_m3
                    )
                else:
                    load_fraction, cycles, power = _fixed_speed_cycling(
                        machine, residual, inputs.receiver_volume_m3
                    )
                header_pressure = (
                    machine.band.load_pressure_bar_g + machine.band.unload_pressure_bar_g
                ) / 2
                if machine.unload_power_fraction is not None and load_fraction < _ONE:
                    period_unload_power += (
                        machine.rated_power_kw
                        * machine.unload_power_fraction
                        * (_ONE - load_fraction)
                    )
            residual -= flow
            supplied += flow
            period_power += power
            machine_results.append(
                MachinePeriodResult(
                    unit_code=machine.unit_code,
                    period_index=point.period_index,
                    duty_role=role,
                    delivered_flow_nm3_per_hr=_q(flow),
                    load_fraction=_q(load_fraction),
                    cycles_per_hour=None if cycles is None else _q(cycles),
                    average_power_kw=_q(power),
                    energy_kwh=_q(power * point.duration_hours),
                )
            )

        shortfall = residual if residual > _ZERO else _ZERO
        if header_pressure is None:
            # No unit is cycling: either every loaded unit is saturated (shortfall,
            # pressure sags to the lowest load setpoint) or demand is zero.
            header_pressure = min(m.band.load_pressure_bar_g for m in order)
            if shortfall == _ZERO and point.demand_nm3_per_hr == _ZERO:
                header_pressure = max(m.band.unload_pressure_bar_g for m in order)
        if shortfall > _ZERO:
            unmet_hours += point.duration_hours

        energy = period_power * point.duration_hours
        total_energy += energy
        unload_energy += period_unload_power * point.duration_hours
        standby_energy += period_standby_power * point.duration_hours
        supplied_volume += supplied * point.duration_hours
        total_hours += point.duration_hours
        periods.append(
            PeriodResult(
                period_index=point.period_index,
                label=point.label,
                demand_nm3_per_hr=point.demand_nm3_per_hr,
                duration_hours=point.duration_hours,
                supplied_flow_nm3_per_hr=_q(supplied),
                shortfall_nm3_per_hr=_q(shortfall),
                average_header_pressure_bar_g=_q(header_pressure),
                total_power_kw=_q(period_power),
                energy_kwh=_q(energy),
                machines=tuple(machine_results),
            )
        )

    average_flow_nm3_per_min = (
        _ZERO if total_hours == _ZERO else supplied_volume / total_hours / Decimal("60")
    )
    specific_power = (
        _ZERO
        if average_flow_nm3_per_min == _ZERO
        else (total_energy / total_hours) / average_flow_nm3_per_min
    )
    return SequencingResult(
        analysis_code=inputs.analysis_code,
        periods=tuple(periods),
        total_energy_kwh=_q(total_energy),
        total_energy_cost=_q(total_energy * inputs.electricity_tariff_per_kwh),
        specific_power_kw_per_nm3_per_min=_q(specific_power),
        unload_energy_kwh=_q(unload_energy),
        standby_energy_kwh=_q(standby_energy),
        unmet_demand_hours=_q(unmet_hours),
    )
