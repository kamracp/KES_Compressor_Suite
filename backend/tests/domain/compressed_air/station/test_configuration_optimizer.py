from decimal import Decimal

from app.domain.compressed_air.profiles.demand_profile import (
    DemandProfilePoint,
    calculate_demand_profile,
)
from app.domain.compressed_air.station.configuration_optimizer import (
    optimize_station_configurations,
)
from app.domain.compressed_air.station.station_models import (
    CompressorControlMode,
    CompressorDutyRole,
    CompressorStationConfiguration,
    CompressorTechnology,
    CompressorUnit,
    RedundancyPhilosophy,
)


def build_profile():
    return calculate_demand_profile(
        (
            DemandProfilePoint(
                period_index=1,
                label="Low Demand",
                demand_nm3_per_hr=Decimal("900"),
                required_pressure_bar_g=Decimal("6.5"),
                duration_hours=Decimal("8"),
            ),
            DemandProfilePoint(
                period_index=2,
                label="Normal Demand",
                demand_nm3_per_hr=Decimal("2200"),
                required_pressure_bar_g=Decimal("6.5"),
                duration_hours=Decimal("8"),
            ),
            DemandProfilePoint(
                period_index=3,
                label="Peak Demand",
                demand_nm3_per_hr=Decimal("3000"),
                required_pressure_bar_g=Decimal("6.5"),
                duration_hours=Decimal("8"),
            ),
        )
    )


def build_unit(
    *,
    unit_code: str,
    fad: str,
    control_mode: CompressorControlMode,
    duty_role: CompressorDutyRole,
    minimum_fraction: str,
) -> CompressorUnit:
    return CompressorUnit(
        unit_code=unit_code,
        technology=CompressorTechnology.ROTARY_SCREW_OIL_INJECTED,
        control_mode=control_mode,
        duty_role=duty_role,
        rated_fad_nm3_per_hr=Decimal(fad),
        minimum_stable_flow_fraction=Decimal(minimum_fraction),
        rated_discharge_pressure_bar_g=Decimal("7.0"),
        rated_motor_power_kw=Decimal("250"),
    )


def test_vsd_trim_configuration_scores_better_than_single_oversized_unit() -> None:
    profile = build_profile()

    single_large = CompressorStationConfiguration(
        station_code="SINGLE-LARGE",
        units=(
            build_unit(
                unit_code="AC-01",
                fad="4000",
                control_mode=CompressorControlMode.FIXED_SPEED,
                duty_role=CompressorDutyRole.DUTY,
                minimum_fraction="0.70",
            ),
        ),
        redundancy_philosophy=RedundancyPhilosophy.NONE,
        minimum_required_pressure_bar_g=Decimal("6.7"),
        design_flow_nm3_per_hr=Decimal("3000"),
        master_control_enabled=False,
    )

    optimized_station = CompressorStationConfiguration(
        station_code="BASE-VSD-STANDBY",
        units=(
            build_unit(
                unit_code="AC-11",
                fad="1800",
                control_mode=CompressorControlMode.FIXED_SPEED,
                duty_role=CompressorDutyRole.BASE_LOAD,
                minimum_fraction="0.60",
            ),
            build_unit(
                unit_code="AC-12",
                fad="1400",
                control_mode=CompressorControlMode.VSD,
                duty_role=CompressorDutyRole.TRIM,
                minimum_fraction="0.20",
            ),
            build_unit(
                unit_code="AC-13",
                fad="1800",
                control_mode=CompressorControlMode.FIXED_SPEED,
                duty_role=CompressorDutyRole.STANDBY,
                minimum_fraction="0.60",
            ),
        ),
        redundancy_philosophy=RedundancyPhilosophy.N_PLUS_1,
        minimum_required_pressure_bar_g=Decimal("6.7"),
        design_flow_nm3_per_hr=Decimal("3000"),
        master_control_enabled=True,
    )

    result = optimize_station_configurations(
        configurations=(
            single_large,
            optimized_station,
        ),
        demand_profile=profile,
    )

    assessments = {item.station_code: item for item in result.assessments}

    assert result.recommended_station_code == "BASE-VSD-STANDBY"

    assert assessments["BASE-VSD-STANDBY"].overall_score > assessments["SINGLE-LARGE"].overall_score

    assert assessments["BASE-VSD-STANDBY"].has_vsd_trim is True
    assert assessments["BASE-VSD-STANDBY"].has_standby_unit is True


def test_peak_demand_not_covered_scores_zero_capacity() -> None:
    profile = build_profile()

    undersized = CompressorStationConfiguration(
        station_code="UNDERSIZED",
        units=(
            build_unit(
                unit_code="AC-21",
                fad="2000",
                control_mode=CompressorControlMode.FIXED_SPEED,
                duty_role=CompressorDutyRole.DUTY,
                minimum_fraction="0.60",
            ),
        ),
        redundancy_philosophy=RedundancyPhilosophy.NONE,
        minimum_required_pressure_bar_g=Decimal("6.7"),
        design_flow_nm3_per_hr=Decimal("3000"),
    )

    result = optimize_station_configurations(
        configurations=(undersized,),
        demand_profile=profile,
    )

    assessment = result.assessments[0]

    assert assessment.peak_demand_is_covered is False
    assert assessment.capacity_score == Decimal("0")


def test_low_demand_control_is_detected() -> None:
    profile = build_profile()

    configuration = CompressorStationConfiguration(
        station_code="LOW-DEMAND-CONTROL",
        units=(
            build_unit(
                unit_code="AC-31",
                fad="3000",
                control_mode=CompressorControlMode.VSD,
                duty_role=CompressorDutyRole.TRIM,
                minimum_fraction="0.20",
            ),
        ),
        redundancy_philosophy=RedundancyPhilosophy.NONE,
        minimum_required_pressure_bar_g=Decimal("6.7"),
        design_flow_nm3_per_hr=Decimal("3000"),
        master_control_enabled=True,
    )

    result = optimize_station_configurations(
        configurations=(configuration,),
        demand_profile=profile,
    )

    assessment = result.assessments[0]

    assert assessment.minimum_controllable_flow_nm3_per_hr == Decimal("600.00")
    assert assessment.low_demand_is_controllable is True
    assert assessment.has_vsd_trim is True


def test_configuration_with_standby_gets_redundancy_credit() -> None:
    profile = build_profile()

    configuration = CompressorStationConfiguration(
        station_code="WITH-STANDBY",
        units=(
            build_unit(
                unit_code="AC-41",
                fad="3000",
                control_mode=CompressorControlMode.VSD,
                duty_role=CompressorDutyRole.TRIM,
                minimum_fraction="0.20",
            ),
            build_unit(
                unit_code="AC-42",
                fad="3000",
                control_mode=CompressorControlMode.FIXED_SPEED,
                duty_role=CompressorDutyRole.STANDBY,
                minimum_fraction="0.60",
            ),
        ),
        redundancy_philosophy=RedundancyPhilosophy.N_PLUS_1,
        minimum_required_pressure_bar_g=Decimal("6.7"),
        design_flow_nm3_per_hr=Decimal("3000"),
        master_control_enabled=True,
    )

    result = optimize_station_configurations(
        configurations=(configuration,),
        demand_profile=profile,
    )

    assessment = result.assessments[0]

    assert assessment.has_standby_unit is True
    assert assessment.redundancy_score == Decimal("100")


def test_master_control_and_vsd_receive_full_control_score() -> None:
    profile = build_profile()

    configuration = CompressorStationConfiguration(
        station_code="MASTER-VSD",
        units=(
            build_unit(
                unit_code="AC-51",
                fad="3200",
                control_mode=CompressorControlMode.VSD,
                duty_role=CompressorDutyRole.TRIM,
                minimum_fraction="0.20",
            ),
        ),
        redundancy_philosophy=RedundancyPhilosophy.NONE,
        minimum_required_pressure_bar_g=Decimal("6.7"),
        design_flow_nm3_per_hr=Decimal("3000"),
        master_control_enabled=True,
    )

    result = optimize_station_configurations(
        configurations=(configuration,),
        demand_profile=profile,
    )

    assessment = result.assessments[0]

    assert assessment.control_score == Decimal("100")
