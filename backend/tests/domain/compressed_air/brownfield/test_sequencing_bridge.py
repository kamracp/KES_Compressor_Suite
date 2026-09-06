"""C-7d: brownfield audit -> sequencing assessment bridge and engine wiring."""

from decimal import Decimal

import pytest

from app.domain.compressed_air.brownfield.audit_models import (
    AuditOperatingState,
    BrownfieldAuditCase,
    CompressorMeasurementPoint,
    ExistingCompressor,
    SystemMeasurementPoint,
)
from app.domain.compressed_air.brownfield.sequencing_bridge import (
    MEASUREMENT_PERIOD_DURATION_HOURS,
    BrownfieldSequencingProposal,
    BrownfieldSequencingSettings,
    InvalidBrownfieldSequencingInputError,
    build_sequencing_assessment_input,
)
from app.domain.compressed_air.brownfield.system_engine import (
    BrownfieldSystemEngineInput,
    analyze_brownfield_system,
)
from app.domain.compressed_air.sequencing.sequencing_models import (
    ControlMode,
    PressureBand,
)
from app.domain.compressed_air.station.station_models import (
    CompressorControlMode,
    CompressorTechnology,
)


def compressor(
    code: str,
    control_mode: CompressorControlMode,
    fad: str,
    kw: str,
    *,
    available: bool = True,
) -> ExistingCompressor:
    return ExistingCompressor(
        unit_code=code,
        equipment_source=None,
        model=None,
        technology=CompressorTechnology.ROTARY_SCREW_OIL_INJECTED,
        control_mode=control_mode,
        rated_fad_nm3_per_hr=Decimal(fad),
        rated_discharge_pressure_bar_g=Decimal("7.5"),
        rated_motor_power_kw=Decimal(kw),
        available=available,
    )


def system_point(label: str, flow: str, pressure: str, power: str) -> SystemMeasurementPoint:
    return SystemMeasurementPoint(
        timestamp_label=label,
        total_flow_nm3_per_hr=Decimal(flow),
        header_pressure_bar_g=Decimal(pressure),
        total_power_kw=Decimal(power),
    )


def audit(
    compressors: tuple[ExistingCompressor, ...],
    system_points: tuple[SystemMeasurementPoint, ...],
) -> BrownfieldAuditCase:
    measurements = tuple(
        CompressorMeasurementPoint(
            unit_code=c.unit_code,
            timestamp_label="T1",
            operating_state=AuditOperatingState.LOADED,
            measured_flow_nm3_per_hr=c.rated_fad_nm3_per_hr,
            measured_discharge_pressure_bar_g=Decimal("7.0"),
            measured_power_kw=c.rated_motor_power_kw,
        )
        for c in compressors
        if c.available
    )
    return BrownfieldAuditCase(
        audit_code="AUD-01",
        project_id=1,
        compressors=compressors,
        compressor_measurements=measurements,
        system_measurements=system_points,
        electricity_tariff_per_kwh=Decimal("5"),
        annual_operating_hours=Decimal("8000"),
    )


def settings(
    code: str,
    load: str = "6.5",
    unload: str = "7.5",
    *,
    priority: int | None = None,
    minimum_flow_fraction: str | None = None,
    minimum_flow_power_fraction: str | None = None,
) -> BrownfieldSequencingSettings:
    return BrownfieldSequencingSettings(
        unit_code=code,
        band=PressureBand(
            load_pressure_bar_g=Decimal(load),
            unload_pressure_bar_g=Decimal(unload),
        ),
        unload_power_fraction=Decimal("0.25"),
        priority=priority,
        minimum_flow_fraction=(
            Decimal(minimum_flow_fraction) if minimum_flow_fraction is not None else None
        ),
        minimum_flow_power_fraction=(
            Decimal(minimum_flow_power_fraction)
            if minimum_flow_power_fraction is not None
            else None
        ),
    )


def proposal(*machine_settings: BrownfieldSequencingSettings) -> BrownfieldSequencingProposal:
    return BrownfieldSequencingProposal(
        proposed_band=PressureBand(
            load_pressure_bar_g=Decimal("6.5"),
            unload_pressure_bar_g=Decimal("7.0"),
        ),
        receiver_volume_m3=Decimal("5"),
        machine_settings=machine_settings,
    )


TWO_FIXED = (
    compressor("A", CompressorControlMode.LOAD_UNLOAD, "1000", "100"),
    compressor("B", CompressorControlMode.FIXED_SPEED, "600", "60"),
)
TWO_POINTS = (
    system_point("T1", "1200", "7.0", "150"),
    system_point("T2", "800", "6.8", "110"),
)


def test_builds_assessment_input_from_audit() -> None:
    case = build_sequencing_assessment_input(
        audit(TWO_FIXED, TWO_POINTS),
        proposal(settings("A", "6.6", "7.4"), settings("B", "6.4", "7.2")),
    )

    assert case.analysis_code == "AUD-01-SEQ"
    assert [m.unit_code for m in case.baseline_machines] == ["A", "B"]
    assert all(
        m.control_mode is ControlMode.FIXED_SPEED_LOAD_UNLOAD for m in case.baseline_machines
    )
    assert case.baseline_machines[0].rated_power_kw == Decimal("100")
    assert case.baseline_machines[0].band.unload_pressure_bar_g == Decimal("7.4")
    assert case.baseline_machines[1].rated_fad_nm3_per_hr == Decimal("600")

    assert len(case.demand_profile) == 2
    first = case.demand_profile[0]
    assert first.period_index == 0
    assert first.label == "T1"
    assert first.demand_nm3_per_hr == Decimal("1200")
    assert first.required_pressure_bar_g == Decimal("7.0")
    assert first.duration_hours == MEASUREMENT_PERIOD_DURATION_HOURS

    assert case.receiver_volume_m3 == Decimal("5")
    assert case.electricity_tariff_per_kwh == Decimal("5")
    assert case.annual_operating_hours == Decimal("8000")
    assert case.proposed_band.unload_pressure_bar_g == Decimal("7.0")


def test_vsd_maps_to_variable_speed_with_minimum_flow_fields() -> None:
    machines = (
        compressor("A", CompressorControlMode.LOAD_UNLOAD, "1000", "100"),
        compressor("V", CompressorControlMode.VSD, "800", "80"),
    )
    case = build_sequencing_assessment_input(
        audit(machines, TWO_POINTS),
        proposal(
            settings("A"),
            settings("V", minimum_flow_fraction="0.25", minimum_flow_power_fraction="0.30"),
        ),
    )

    vsd = case.baseline_machines[1]
    assert vsd.control_mode is ControlMode.VARIABLE_SPEED
    assert vsd.minimum_flow_fraction == Decimal("0.25")
    assert vsd.minimum_flow_power_fraction == Decimal("0.30")


def test_unavailable_compressor_is_excluded_and_needs_no_settings() -> None:
    machines = (
        *TWO_FIXED,
        compressor("C", CompressorControlMode.LOAD_UNLOAD, "500", "50", available=False),
    )
    case = build_sequencing_assessment_input(
        audit(machines, TWO_POINTS),
        proposal(settings("A"), settings("B")),
    )

    assert [m.unit_code for m in case.baseline_machines] == ["A", "B"]


def test_modulation_control_is_rejected_as_c8_scope() -> None:
    machines = (compressor("M", CompressorControlMode.MODULATION, "1000", "100"),)

    with pytest.raises(InvalidBrownfieldSequencingInputError, match="C-8"):
        build_sequencing_assessment_input(audit(machines, TWO_POINTS), proposal(settings("M")))


def test_missing_settings_for_available_unit_is_rejected() -> None:
    with pytest.raises(InvalidBrownfieldSequencingInputError, match="missing.*B"):
        build_sequencing_assessment_input(audit(TWO_FIXED, TWO_POINTS), proposal(settings("A")))


def test_settings_for_unknown_unit_is_rejected() -> None:
    with pytest.raises(InvalidBrownfieldSequencingInputError, match="not in the available.*Z"):
        build_sequencing_assessment_input(
            audit(TWO_FIXED, TWO_POINTS),
            proposal(settings("A"), settings("B"), settings("Z")),
        )


def test_duplicate_settings_are_rejected() -> None:
    with pytest.raises(InvalidBrownfieldSequencingInputError, match="repeat"):
        build_sequencing_assessment_input(
            audit(TWO_FIXED, TWO_POINTS),
            proposal(settings("A"), settings("A"), settings("B")),
        )


def test_mixed_priority_is_rejected() -> None:
    with pytest.raises(InvalidBrownfieldSequencingInputError, match="Priority"):
        build_sequencing_assessment_input(
            audit(TWO_FIXED, TWO_POINTS),
            proposal(settings("A", priority=1), settings("B")),
        )


def test_audit_without_system_measurements_is_rejected() -> None:
    with pytest.raises(InvalidBrownfieldSequencingInputError, match="system measurement"):
        build_sequencing_assessment_input(
            audit(TWO_FIXED, ()),
            proposal(settings("A"), settings("B")),
        )


def test_engine_runs_assessment_and_emits_central_sequencer_opportunity() -> None:
    case = audit(TWO_FIXED, TWO_POINTS)
    seq_proposal = proposal(settings("A", "6.6", "7.4"), settings("B", "6.4", "7.2"))

    with_proposal = analyze_brownfield_system(
        BrownfieldSystemEngineInput(audit=case, sequencing_proposal=seq_proposal)
    )
    without_proposal = analyze_brownfield_system(BrownfieldSystemEngineInput(audit=case))

    assert with_proposal.sequencing_assessment is not None
    assert with_proposal.sequencing_assessment.analysis_code == "AUD-01-SEQ"
    codes_with = [o.opportunity_code for o in with_proposal.opportunities.opportunities]
    assert "CENTRAL-SEQUENCER" in codes_with

    assert without_proposal.sequencing_assessment is None
    codes_without = [o.opportunity_code for o in without_proposal.opportunities.opportunities]
    assert "CENTRAL-SEQUENCER" not in codes_without
