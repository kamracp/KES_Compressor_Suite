from decimal import Decimal

from app.domain.compressed_air.consumers.consumer_models import (
    AirConsumer,
    AirConsumerCategory,
    AirConsumptionBasis,
    AirQualityClass,
    ConsumerCriticality,
)
from app.domain.compressed_air.greenfield.system_design import (
    GreenfieldSystemDesignInput,
    design_greenfield_system,
)
from app.domain.compressed_air.pressure.pressure_budget import (
    PressureLossComponent,
)
from app.domain.compressed_air.profiles.demand_profile import DemandProfilePoint
from app.domain.compressed_air.station.station_models import (
    CompressorControlMode,
    CompressorDutyRole,
    CompressorStationConfiguration,
    CompressorTechnology,
    CompressorUnit,
    RedundancyPhilosophy,
)
from app.domain.compressed_air.storage.receiver_sizing import ReceiverSizingInput
from app.domain.compressed_air.treatment.air_treatment import (
    AirTreatmentInput,
    DryerType,
)


def build_consumers() -> tuple[AirConsumer, ...]:
    return (
        AirConsumer(
            consumer_code="CNC-001",
            name="CNC Machine Group",
            category=AirConsumerCategory.PRODUCTION_MACHINE,
            quantity=10,
            required_pressure_bar_g=Decimal("6.0"),
            air_quality_class=AirQualityClass.GENERAL_PLANT_AIR,
            consumption_basis=AirConsumptionBasis.FLOW_WHEN_OPERATING,
            flow_per_unit_nm3_per_hr=Decimal("25"),
            duty_factor=Decimal("0.70"),
            simultaneity_factor=Decimal("0.80"),
            operating_hours_per_day=Decimal("16"),
            operating_days_per_year=Decimal("300"),
            criticality=ConsumerCriticality.NORMAL,
        ),
        AirConsumer(
            consumer_code="IA-001",
            name="Instrument Air",
            category=AirConsumerCategory.INSTRUMENT_AIR,
            quantity=1,
            required_pressure_bar_g=Decimal("6.5"),
            air_quality_class=AirQualityClass.INSTRUMENT_AIR,
            consumption_basis=AirConsumptionBasis.CONTINUOUS_FLOW,
            flow_per_unit_nm3_per_hr=Decimal("120"),
            operating_hours_per_day=Decimal("24"),
            operating_days_per_year=Decimal("365"),
            criticality=ConsumerCriticality.CRITICAL,
        ),
    )


def build_profile() -> tuple[DemandProfilePoint, ...]:
    return (
        DemandProfilePoint(
            period_index=1,
            label="Low Demand",
            demand_nm3_per_hr=Decimal("180"),
            required_pressure_bar_g=Decimal("6.5"),
            duration_hours=Decimal("8"),
        ),
        DemandProfilePoint(
            period_index=2,
            label="Normal Demand",
            demand_nm3_per_hr=Decimal("260"),
            required_pressure_bar_g=Decimal("6.5"),
            duration_hours=Decimal("8"),
        ),
        DemandProfilePoint(
            period_index=3,
            label="Peak Demand",
            demand_nm3_per_hr=Decimal("320"),
            required_pressure_bar_g=Decimal("6.5"),
            duration_hours=Decimal("8"),
        ),
    )


def build_station() -> CompressorStationConfiguration:
    return CompressorStationConfiguration(
        station_code="CAS-GF-001",
        units=(
            CompressorUnit(
                unit_code="AC-01",
                technology=CompressorTechnology.ROTARY_SCREW_OIL_INJECTED,
                control_mode=CompressorControlMode.FIXED_SPEED,
                duty_role=CompressorDutyRole.BASE_LOAD,
                rated_fad_nm3_per_hr=Decimal("250"),
                minimum_stable_flow_fraction=Decimal("0.60"),
                rated_discharge_pressure_bar_g=Decimal("7.0"),
                rated_motor_power_kw=Decimal("45"),
            ),
            CompressorUnit(
                unit_code="AC-02",
                technology=CompressorTechnology.ROTARY_SCREW_OIL_INJECTED,
                control_mode=CompressorControlMode.VSD,
                duty_role=CompressorDutyRole.TRIM,
                rated_fad_nm3_per_hr=Decimal("180"),
                minimum_stable_flow_fraction=Decimal("0.20"),
                rated_discharge_pressure_bar_g=Decimal("7.0"),
                rated_motor_power_kw=Decimal("30"),
            ),
            CompressorUnit(
                unit_code="AC-03",
                technology=CompressorTechnology.ROTARY_SCREW_OIL_INJECTED,
                control_mode=CompressorControlMode.FIXED_SPEED,
                duty_role=CompressorDutyRole.STANDBY,
                rated_fad_nm3_per_hr=Decimal("250"),
                minimum_stable_flow_fraction=Decimal("0.60"),
                rated_discharge_pressure_bar_g=Decimal("7.0"),
                rated_motor_power_kw=Decimal("45"),
            ),
        ),
        redundancy_philosophy=RedundancyPhilosophy.N_PLUS_1,
        minimum_required_pressure_bar_g=Decimal("6.9"),
        design_flow_nm3_per_hr=Decimal("350"),
        master_control_enabled=True,
    )


def test_complete_greenfield_design_chain() -> None:
    result = design_greenfield_system(
        GreenfieldSystemDesignInput(
            consumers=build_consumers(),
            demand_profile_points=build_profile(),
            leakage_fraction=Decimal("0.10"),
            future_expansion_fraction=Decimal("0.15"),
            minimum_point_of_use_pressure_bar_g=Decimal("6.0"),
            pressure_loss_components=(
                PressureLossComponent(
                    component_code="DRYER",
                    name="Dryer",
                    pressure_drop_bar=Decimal("0.15"),
                    category="TREATMENT",
                ),
                PressureLossComponent(
                    component_code="FILTER",
                    name="Filters",
                    pressure_drop_bar=Decimal("0.10"),
                    category="TREATMENT",
                ),
                PressureLossComponent(
                    component_code="HEADER",
                    name="Distribution Header",
                    pressure_drop_bar=Decimal("0.20"),
                    category="DISTRIBUTION",
                ),
            ),
            control_margin_bar=Decimal("0.20"),
            treatment_input=AirTreatmentInput(
                required_delivered_flow_nm3_per_hr=Decimal("350"),
                required_air_quality=AirQualityClass.GENERAL_PLANT_AIR,
                dryer_type=DryerType.REFRIGERATED,
                dryer_correction_factor=Decimal("0.95"),
                treatment_capacity_margin_fraction=Decimal("0.10"),
            ),
            station_configuration=build_station(),
            receiver_input=ReceiverSizingInput(
                peak_demand_nm3_per_hr=Decimal("400"),
                available_compressor_flow_nm3_per_hr=Decimal("350"),
                event_duration_seconds=Decimal("30"),
                receiver_high_pressure_bar_g=Decimal("7.0"),
                receiver_low_pressure_bar_g=Decimal("6.5"),
                reserve_fraction=Decimal("0.20"),
            ),
            specific_power_kw_per_nm3_per_min=Decimal("6.5"),
            annual_operating_days=Decimal("330"),
            electricity_tariff_per_kwh=Decimal("8"),
        )
    )

    assert result.plant_demand.design_flow_nm3_per_hr > Decimal("0")
    assert result.demand_profile.maximum_demand_nm3_per_hr == Decimal("320")

    assert result.required_compressor_discharge_pressure_bar_g == Decimal("6.65")

    assert result.treatment is not None
    assert result.station_capacity is not None
    assert result.receiver is not None
    assert result.energy is not None

    assert result.station_capacity_is_adequate is True
    assert result.receiver.storage_required is True
    assert result.energy.annual_energy_kwh > Decimal("0")

    assert result.system_design_is_feasible is True


def test_station_capacity_shortfall_makes_design_infeasible() -> None:
    station = build_station()

    undersized_station = CompressorStationConfiguration(
        station_code="CAS-GF-BAD",
        units=station.units[:1],
        redundancy_philosophy=RedundancyPhilosophy.NONE,
        minimum_required_pressure_bar_g=Decimal("6.9"),
        design_flow_nm3_per_hr=Decimal("350"),
    )

    result = design_greenfield_system(
        GreenfieldSystemDesignInput(
            consumers=build_consumers(),
            demand_profile_points=build_profile(),
            minimum_point_of_use_pressure_bar_g=Decimal("6.0"),
            station_configuration=undersized_station,
        )
    )

    assert result.station_capacity_is_adequate is False
    assert result.system_design_is_feasible is False

    assert any(
        "capacity is below design flow" in message for message in result.engineering_messages
    )


def test_insufficient_station_pressure_makes_design_infeasible() -> None:
    station = build_station()

    low_pressure_station = CompressorStationConfiguration(
        station_code="CAS-GF-LOW-P",
        units=station.units,
        redundancy_philosophy=station.redundancy_philosophy,
        minimum_required_pressure_bar_g=Decimal("6.2"),
        design_flow_nm3_per_hr=Decimal("350"),
        master_control_enabled=True,
    )

    result = design_greenfield_system(
        GreenfieldSystemDesignInput(
            consumers=build_consumers(),
            demand_profile_points=build_profile(),
            minimum_point_of_use_pressure_bar_g=Decimal("6.0"),
            pressure_loss_components=(
                PressureLossComponent(
                    component_code="LOSS",
                    name="System Loss",
                    pressure_drop_bar=Decimal("0.40"),
                    category="DISTRIBUTION",
                ),
            ),
            control_margin_bar=Decimal("0.20"),
            station_configuration=low_pressure_station,
        )
    )

    assert result.required_compressor_discharge_pressure_bar_g == Decimal("6.60")

    assert result.system_design_is_feasible is False


def test_energy_requires_annual_operating_days() -> None:
    try:
        design_greenfield_system(
            GreenfieldSystemDesignInput(
                consumers=build_consumers(),
                demand_profile_points=build_profile(),
                specific_power_kw_per_nm3_per_min=Decimal("6.5"),
            )
        )
    except ValueError as exc:
        assert "Annual operating days are required" in str(exc)
    else:
        raise AssertionError("Expected annual operating days validation error.")


def test_optional_modules_can_be_omitted() -> None:
    result = design_greenfield_system(
        GreenfieldSystemDesignInput(
            consumers=build_consumers(),
            demand_profile_points=build_profile(),
        )
    )

    assert result.treatment is None
    assert result.station_capacity is None
    assert result.receiver is None
    assert result.energy is None

    assert result.station_capacity_is_adequate is None
