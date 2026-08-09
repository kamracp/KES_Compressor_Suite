from app.domain.compressed_air.consumers.consumer_models import AirConsumer
from app.domain.compressed_air.greenfield.system_design import (
    GreenfieldSystemDesignInput,
    design_greenfield_system,
)
from app.domain.compressed_air.pressure.pressure_budget import (
    PressureLossComponent,
)
from app.domain.compressed_air.profiles.demand_profile import DemandProfilePoint
from app.domain.compressed_air.station.station_models import (
    CompressorStationConfiguration,
    CompressorUnit,
)
from app.domain.compressed_air.storage.receiver_sizing import ReceiverSizingInput
from app.domain.compressed_air.treatment.air_treatment import AirTreatmentInput
from app.schemas.compressed_air_greenfield import (
    GreenfieldSystemDesignRequest,
    GreenfieldSystemDesignResponse,
)


class CompressedAirGreenfieldService:
    """Application service for greenfield compressed-air system design."""

    def design(
        self,
        request: GreenfieldSystemDesignRequest,
    ) -> GreenfieldSystemDesignResponse:
        domain_input = GreenfieldSystemDesignInput(
            consumers=tuple(
                AirConsumer(
                    consumer_code=item.consumer_code,
                    name=item.name,
                    category=item.category,
                    quantity=item.quantity,
                    required_pressure_bar_g=item.required_pressure_bar_g,
                    air_quality_class=item.air_quality_class,
                    consumption_basis=item.consumption_basis,
                    flow_per_unit_nm3_per_hr=item.flow_per_unit_nm3_per_hr,
                    air_per_cycle_nl=item.air_per_cycle_nl,
                    cycles_per_minute=item.cycles_per_minute,
                    duty_factor=item.duty_factor,
                    simultaneity_factor=item.simultaneity_factor,
                    operating_hours_per_day=item.operating_hours_per_day,
                    operating_days_per_year=item.operating_days_per_year,
                    criticality=item.criticality,
                    area=item.area,
                    production_line=item.production_line,
                    notes=item.notes,
                )
                for item in request.consumers
            ),
            demand_profile_points=tuple(
                DemandProfilePoint(
                    period_index=item.period_index,
                    label=item.label,
                    demand_nm3_per_hr=item.demand_nm3_per_hr,
                    required_pressure_bar_g=item.required_pressure_bar_g,
                    duration_hours=item.duration_hours,
                )
                for item in request.demand_profile_points
            ),
            leakage_fraction=request.leakage_fraction,
            future_expansion_fraction=request.future_expansion_fraction,
            other_allowance_fraction=request.other_allowance_fraction,
            minimum_point_of_use_pressure_bar_g=(request.minimum_point_of_use_pressure_bar_g),
            pressure_loss_components=tuple(
                PressureLossComponent(
                    component_code=item.component_code,
                    name=item.name,
                    pressure_drop_bar=item.pressure_drop_bar,
                    category=item.category,
                    notes=item.notes,
                )
                for item in request.pressure_loss_components
            ),
            control_margin_bar=request.control_margin_bar,
            treatment_input=self._build_treatment(request),
            station_configuration=self._build_station(request),
            receiver_input=self._build_receiver(request),
            specific_power_kw_per_nm3_per_min=(request.specific_power_kw_per_nm3_per_min),
            annual_operating_days=request.annual_operating_days,
            electricity_tariff_per_kwh=request.electricity_tariff_per_kwh,
        )

        result = design_greenfield_system(domain_input)

        treatment_capacity = None

        if result.treatment is not None:
            treatment_capacity = result.treatment.recommended_treatment_capacity_nm3_per_hr

        station_available_capacity = None

        if result.station_capacity is not None:
            station_available_capacity = result.station_capacity.available_fad_nm3_per_hr

        receiver_volume = None
        receiver_storage_required = None

        if result.receiver is not None:
            receiver_volume = result.receiver.recommended_receiver_volume_m3
            receiver_storage_required = result.receiver.storage_required

        annual_energy_kwh = None
        annual_energy_cost = None

        if result.energy is not None:
            annual_energy_kwh = result.energy.annual_energy_kwh
            annual_energy_cost = result.energy.annual_energy_cost

        return GreenfieldSystemDesignResponse(
            required_design_flow_nm3_per_hr=(result.required_design_flow_nm3_per_hr),
            required_compressor_discharge_pressure_bar_g=(
                result.required_compressor_discharge_pressure_bar_g
            ),
            simultaneous_demand_nm3_per_hr=(result.plant_demand.total_simultaneous_flow_nm3_per_hr),
            peak_profile_demand_nm3_per_hr=(result.demand_profile.maximum_demand_nm3_per_hr),
            leakage_allowance_nm3_per_hr=(result.plant_demand.leakage_allowance_nm3_per_hr),
            future_expansion_allowance_nm3_per_hr=(
                result.plant_demand.future_expansion_allowance_nm3_per_hr
            ),
            treatment_capacity_nm3_per_hr=treatment_capacity,
            station_available_capacity_nm3_per_hr=station_available_capacity,
            station_capacity_is_adequate=result.station_capacity_is_adequate,
            receiver_volume_m3=receiver_volume,
            receiver_storage_required=receiver_storage_required,
            annual_energy_kwh=annual_energy_kwh,
            annual_energy_cost=annual_energy_cost,
            system_design_is_feasible=result.system_design_is_feasible,
            engineering_messages=list(result.engineering_messages),
        )

    def _build_treatment(
        self,
        request: GreenfieldSystemDesignRequest,
    ) -> AirTreatmentInput | None:
        item = request.treatment

        if item is None:
            return None

        return AirTreatmentInput(
            required_delivered_flow_nm3_per_hr=(item.required_delivered_flow_nm3_per_hr),
            required_air_quality=item.required_air_quality,
            dryer_type=item.dryer_type,
            dryer_correction_factor=item.dryer_correction_factor,
            dryer_purge_fraction=item.dryer_purge_fraction,
            prefilter_pressure_drop_bar=item.prefilter_pressure_drop_bar,
            afterfilter_pressure_drop_bar=item.afterfilter_pressure_drop_bar,
            dryer_pressure_drop_bar=item.dryer_pressure_drop_bar,
            treatment_capacity_margin_fraction=(item.treatment_capacity_margin_fraction),
        )

    def _build_station(
        self,
        request: GreenfieldSystemDesignRequest,
    ) -> CompressorStationConfiguration | None:
        item = request.station

        if item is None:
            return None

        units = tuple(
            CompressorUnit(
                unit_code=unit.unit_code,
                technology=unit.technology,
                control_mode=unit.control_mode,
                duty_role=unit.duty_role,
                rated_fad_nm3_per_hr=unit.rated_fad_nm3_per_hr,
                minimum_stable_flow_fraction=(unit.minimum_stable_flow_fraction),
                rated_discharge_pressure_bar_g=(unit.rated_discharge_pressure_bar_g),
                rated_motor_power_kw=unit.rated_motor_power_kw,
                specific_power_kw_per_nm3_per_min=(unit.specific_power_kw_per_nm3_per_min),
                available=unit.available,
                notes=unit.notes,
            )
            for unit in item.units
        )

        return CompressorStationConfiguration(
            station_code=item.station_code,
            units=units,
            redundancy_philosophy=item.redundancy_philosophy,
            minimum_required_pressure_bar_g=(item.minimum_required_pressure_bar_g),
            design_flow_nm3_per_hr=item.design_flow_nm3_per_hr,
            master_control_enabled=item.master_control_enabled,
        )

    def _build_receiver(
        self,
        request: GreenfieldSystemDesignRequest,
    ) -> ReceiverSizingInput | None:
        item = request.receiver

        if item is None:
            return None

        return ReceiverSizingInput(
            peak_demand_nm3_per_hr=item.peak_demand_nm3_per_hr,
            available_compressor_flow_nm3_per_hr=(item.available_compressor_flow_nm3_per_hr),
            event_duration_seconds=item.event_duration_seconds,
            receiver_high_pressure_bar_g=item.receiver_high_pressure_bar_g,
            receiver_low_pressure_bar_g=item.receiver_low_pressure_bar_g,
            reserve_fraction=item.reserve_fraction,
        )


compressed_air_greenfield_service = CompressedAirGreenfieldService()
