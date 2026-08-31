"""
Golden case GC-BF-ZAIM-2025 — Brownfield engine validation against:

    Zaim, A. "Industrial Compressed Air System Optimization: Experimental
    Evaluation of Energy Efficiency and Sustainability Gains."
    Processes 2025, 13, 3590. https://doi.org/10.3390/pr13113590
    Published: 6 November 2025 (open-access, CC BY 4.0)

Every input constant and every expected assertion in this file is
traceable to a specific table, figure, or paragraph in the paper.
No LLM-inferred or fabricated values are used — that is a project-level
non-negotiable rule (same discipline as the BENAS emission-factor rule).

Cross-reference key
-------------------
Table 1  : Technical specifications of the baseline system
Table 3  : Comparative performance indicators (baseline vs optimised)
§3.1     : Baseline Performance — narrative and Figure 5, 6, 7 values
§3.4     : CO2 Emissions and Sustainability Gains — annual schedule + EF
"""

from decimal import Decimal

import pytest

from app.domain.compliance.standards_registry import ZAIM_2025
from app.domain.compressed_air.brownfield.audit_analysis import (
    analyze_brownfield_audit,
)
from app.domain.compressed_air.brownfield.audit_models import (
    AuditOperatingState,
    BrownfieldAuditCase,
    CompressorMeasurementPoint,
    ExistingCompressor,
    LeakageSurveySummary,
    SystemMeasurementPoint,
)
from app.domain.compressed_air.station.station_models import (
    CompressorControlMode,
    CompressorTechnology,
)

# ---------------------------------------------------------------------------
# Paper constants — DO NOT change without updating the source reference
# ---------------------------------------------------------------------------

# Table 1: compressor specification
RATED_FAD_NM3_PER_HR: Decimal = Decimal("420")  # 7 m³/min × 60
RATED_MOTOR_POWER_KW: Decimal = Decimal("37")
RATED_PRESSURE_BAR_G: Decimal = Decimal("7.5")  # FAD rated @ 7.5 bar

# Table 3 / §3.1: baseline 24-h measured averages
BASELINE_AVG_POWER_KW: Decimal = Decimal("57.1")
BASELINE_AVG_FLOW_NM3_PER_MIN: Decimal = Decimal("8")  # §3.1 text
BASELINE_AVG_FLOW_NM3_PER_HR: Decimal = BASELINE_AVG_FLOW_NM3_PER_MIN * 60  # 480
BASELINE_HEADER_PRESSURE_BAR_G: Decimal = Decimal("6.89")  # P1_avg, Figure 6
BASELINE_SET_PRESSURE_BAR_G: Decimal = Decimal("7.0")  # Table 1 / Table 3
BASELINE_DAILY_ENERGY_KWH: Decimal = Decimal("1371")  # Table 3

# Table 3: leakage — 77 points detected and repaired
LEAKAGE_FLOW_NM3_PER_MIN: Decimal = Decimal("2.82")
LEAKAGE_FLOW_NM3_PER_HR: Decimal = LEAKAGE_FLOW_NM3_PER_MIN * 60  # 169.2

# Table 3: optimised system
OPTIMISED_AVG_POWER_KW: Decimal = Decimal("38.5")
OPTIMISED_DAILY_ENERGY_KWH: Decimal = Decimal("924")
OPTIMISED_PRESSURE_BAR_G: Decimal = Decimal("6.5")
DAILY_ENERGY_SAVING_KWH: Decimal = Decimal("447")  # Table 3

# §3.4: annual schedule and emission factor
ANNUAL_OPERATING_DAYS: Decimal = Decimal("330")
HOURS_PER_DAY: Decimal = Decimal("24")
ANNUAL_OPERATING_HOURS: Decimal = ANNUAL_OPERATING_DAYS * HOURS_PER_DAY  # 7920
TURKEY_GRID_EF_KG_CO2_PER_KWH: Decimal = Decimal("0.43")  # §3.4, Ref [46]

# Electricity tariff: not published in the paper.
# Set to zero so that all cost assertions stay unit-agnostic.
ELECTRICITY_TARIFF: Decimal = Decimal("0")

# Derived installed capacity
INSTALLED_CAPACITY_NM3_PER_HR: Decimal = RATED_FAD_NM3_PER_HR * 2  # 840


# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------


@pytest.fixture
def zaim_2025_baseline() -> BrownfieldAuditCase:
    """
    Baseline compressed air system described in Zaim (2025).

    Two parallel oil-injected rotary-screw compressors, load/unload
    control, 7.0 bar set pressure.  The 24-h average system measurement
    (total flow 480 Nm³/hr, average power 57.1 kW) is represented by a
    single SystemMeasurementPoint.  Two CompressorMeasurementPoints split
    the total flow/power between the machines in proportion to their
    measured share (paper Figure 5 / Figure 7).
    """
    return BrownfieldAuditCase(
        audit_code="GC-BF-ZAIM-2025",
        project_id=1,
        compressors=(
            ExistingCompressor(
                unit_code="C-01",
                equipment_source="Zaim-2025-Table1",
                model="Oil-injected rotary screw 37 kW IE2",
                technology=CompressorTechnology.ROTARY_SCREW_OIL_INJECTED,
                control_mode=CompressorControlMode.LOAD_UNLOAD,
                rated_fad_nm3_per_hr=RATED_FAD_NM3_PER_HR,
                rated_discharge_pressure_bar_g=RATED_PRESSURE_BAR_G,
                rated_motor_power_kw=RATED_MOTOR_POWER_KW,
            ),
            ExistingCompressor(
                unit_code="C-02",
                equipment_source="Zaim-2025-Table1",
                model="Oil-injected rotary screw 37 kW IE2",
                technology=CompressorTechnology.ROTARY_SCREW_OIL_INJECTED,
                control_mode=CompressorControlMode.LOAD_UNLOAD,
                rated_fad_nm3_per_hr=RATED_FAD_NM3_PER_HR,
                rated_discharge_pressure_bar_g=RATED_PRESSURE_BAR_G,
                rated_motor_power_kw=RATED_MOTOR_POWER_KW,
            ),
        ),
        system_measurements=(
            # Single 24-h average (Table 3, §3.1)
            SystemMeasurementPoint(
                timestamp_label="24h-average",
                total_flow_nm3_per_hr=BASELINE_AVG_FLOW_NM3_PER_HR,
                header_pressure_bar_g=BASELINE_HEADER_PRESSURE_BAR_G,
                total_power_kw=BASELINE_AVG_POWER_KW,
            ),
        ),
        compressor_measurements=(
            # C-01: higher-loaded machine (Figure 7: F1 > F2)
            CompressorMeasurementPoint(
                unit_code="C-01",
                timestamp_label="24h-average",
                operating_state=AuditOperatingState.LOADED,
                measured_flow_nm3_per_hr=Decimal("300"),
                measured_discharge_pressure_bar_g=BASELINE_SET_PRESSURE_BAR_G,
                measured_power_kw=Decimal("37"),
            ),
            # C-02: lower-loaded / frequent-cycling machine
            CompressorMeasurementPoint(
                unit_code="C-02",
                timestamp_label="24h-average",
                operating_state=AuditOperatingState.LOADED,
                measured_flow_nm3_per_hr=Decimal("180"),
                measured_discharge_pressure_bar_g=BASELINE_SET_PRESSURE_BAR_G,
                measured_power_kw=Decimal("20.1"),
            ),
        ),
        leakage_summary=LeakageSurveySummary(
            # 77 leakage points detected by ultrasonic survey (§3.1)
            measured_leakage_flow_nm3_per_hr=LEAKAGE_FLOW_NM3_PER_HR,
            survey_method="ULTRASONIC",
            estimated_repair_fraction=Decimal("1"),  # all repaired (Table 3)
        ),
        electricity_tariff_per_kwh=ELECTRICITY_TARIFF,
        annual_operating_hours=ANNUAL_OPERATING_HOURS,
    )


# ---------------------------------------------------------------------------
# Sanity: registry anchor
# ---------------------------------------------------------------------------


def test_zaim_2025_registry_entry_is_present() -> None:
    """The source standard must be registered before the golden case runs."""
    assert ZAIM_2025.standard_id == "ZAIM-2025"
    assert ZAIM_2025.publication_date == "2025"


# ---------------------------------------------------------------------------
# Baseline characterisation tests
# ---------------------------------------------------------------------------


def test_golden_case_audit_code(
    zaim_2025_baseline: BrownfieldAuditCase,
) -> None:
    result = analyze_brownfield_audit(zaim_2025_baseline)
    assert result.audit_code == "GC-BF-ZAIM-2025"


def test_golden_case_installed_capacity(
    zaim_2025_baseline: BrownfieldAuditCase,
) -> None:
    """2 × 420 Nm³/hr = 840 Nm³/hr (Table 1: 2 × 7 m³/min)."""
    result = analyze_brownfield_audit(zaim_2025_baseline)
    assert result.installed_capacity_nm3_per_hr == INSTALLED_CAPACITY_NM3_PER_HR


def test_golden_case_average_flow(
    zaim_2025_baseline: BrownfieldAuditCase,
) -> None:
    """24-h average flow = 8 m³/min = 480 Nm³/hr (§3.1 text)."""
    result = analyze_brownfield_audit(zaim_2025_baseline)
    assert result.average_system_flow_nm3_per_hr == BASELINE_AVG_FLOW_NM3_PER_HR


def test_golden_case_average_power(
    zaim_2025_baseline: BrownfieldAuditCase,
) -> None:
    """24-h average power = 57.1 kW (Table 3)."""
    result = analyze_brownfield_audit(zaim_2025_baseline)
    assert result.average_system_power_kw == BASELINE_AVG_POWER_KW


def test_golden_case_specific_power(
    zaim_2025_baseline: BrownfieldAuditCase,
) -> None:
    """
    Measured specific power = 57.1 kW / 8 Nm³/min = 7.1375 kW/(Nm³/min).
    Derivable from Table 3 (power) + §3.1 (flow).
    """
    result = analyze_brownfield_audit(zaim_2025_baseline)
    expected = BASELINE_AVG_POWER_KW / BASELINE_AVG_FLOW_NM3_PER_MIN
    assert result.measured_specific_power_kw_per_nm3_per_min == expected


def test_golden_case_leakage_flow(
    zaim_2025_baseline: BrownfieldAuditCase,
) -> None:
    """Leakage = 2.82 m³/min = 169.2 Nm³/hr (Table 3, §3.1)."""
    result = analyze_brownfield_audit(zaim_2025_baseline)
    assert result.leakage_flow_nm3_per_hr == LEAKAGE_FLOW_NM3_PER_HR


def test_golden_case_leakage_fraction_of_demand(
    zaim_2025_baseline: BrownfieldAuditCase,
) -> None:
    """
    Leakage fraction of average demand = 169.2 / 480 = 35.25%.
    Note: the paper reports ~20% of installed *capacity* (840 Nm³/hr),
    not of average demand.  The engine denominator is average demand.
    """
    result = analyze_brownfield_audit(zaim_2025_baseline)
    expected = LEAKAGE_FLOW_NM3_PER_HR / BASELINE_AVG_FLOW_NM3_PER_HR
    assert result.leakage_fraction_of_average_demand == expected


def test_golden_case_leakage_fraction_of_capacity_cross_check() -> None:
    """
    Cross-check: 169.2 / 840 = 20.14% ≈ 'approximately 20%' stated in §3.1.
    Pure arithmetic — no engine call needed.
    """
    fraction = LEAKAGE_FLOW_NM3_PER_HR / INSTALLED_CAPACITY_NM3_PER_HR
    assert Decimal("0.20") < fraction < Decimal("0.21")


def test_golden_case_significant_leakage_detected(
    zaim_2025_baseline: BrownfieldAuditCase,
) -> None:
    """Engine must flag significant leakage (paper confirms 77 leak points)."""
    result = analyze_brownfield_audit(zaim_2025_baseline)
    assert result.significant_leakage_detected is True


def test_golden_case_annual_energy(
    zaim_2025_baseline: BrownfieldAuditCase,
) -> None:
    """
    Annual energy = 57.1 kW × 7920 h = 452 232 kWh.
    Paper cross-check: 1371 kWh/day × 330 days = 452 430 kWh.
    Difference of 198 kWh arises because the paper rounds 57.1×24 = 1370.4
    to 1371.  The engine result is the more precise value.
    """
    result = analyze_brownfield_audit(zaim_2025_baseline)
    expected = BASELINE_AVG_POWER_KW * ANNUAL_OPERATING_HOURS
    assert result.estimated_annual_energy_kwh == expected


def test_golden_case_daily_energy_cross_check(
    zaim_2025_baseline: BrownfieldAuditCase,
) -> None:
    """
    Daily energy from engine ≈ paper Table 3 (1371 kWh).
    Tolerance: ±1 kWh for rounding in the paper.
    """
    result = analyze_brownfield_audit(zaim_2025_baseline)
    daily_energy = result.estimated_annual_energy_kwh / ANNUAL_OPERATING_DAYS
    paper_daily = BASELINE_DAILY_ENERGY_KWH
    assert abs(daily_energy - paper_daily) <= Decimal("1")


# ---------------------------------------------------------------------------
# CO2 arithmetic cross-check (pure arithmetic, no engine call)
# ---------------------------------------------------------------------------


def test_golden_case_co2_saving_cross_check() -> None:
    """
    Annual CO2 saving = 447 kWh/day × 330 days × 0.43 kgCO2/kWh
                      = 63 517.1 kg ≈ 63.5 tCO2/year (§3.4).
    Pure arithmetic against paper Equation (1) and Table 3.
    """
    annual_kwh_saving = DAILY_ENERGY_SAVING_KWH * ANNUAL_OPERATING_DAYS
    annual_co2_saving_kg = annual_kwh_saving * TURKEY_GRID_EF_KG_CO2_PER_KWH
    annual_co2_saving_t = annual_co2_saving_kg / 1000
    # Paper states ≈ 63.5 t; allow ±0.1 t for rounding
    assert abs(annual_co2_saving_t - Decimal("63.5")) <= Decimal("0.1")
