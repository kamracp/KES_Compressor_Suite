from dataclasses import dataclass
from decimal import Decimal

from app.domain.compressed_air.consumers.consumer_demand import (
    calculate_consumer_demand,
)
from app.domain.compressed_air.consumers.consumer_models import AirConsumer
from app.domain.compressed_air.demand.plant_demand import (
    PlantDemandResult,
    calculate_plant_demand,
)
from app.domain.compressed_air.energy.system_energy import (
    SystemEnergyInput,
    SystemEnergyResult,
    calculate_system_energy,
)
from app.domain.compressed_air.pressure.pressure_budget import (
    PressureBudgetResult,
    PressureLossComponent,
    calculate_pressure_budget,
)
from app.domain.compressed_air.profiles.demand_profile import (
    DemandProfilePoint,
    DemandProfileResult,
    calculate_demand_profile,
)
from app.domain.compressed_air.station.capacity import calculate_station_capacity
from app.domain.compressed_air.station.station_models import (
    CompressorStationCapacityResult,
    CompressorStationConfiguration,
)
from app.domain.compressed_air.storage.receiver_sizing import (
    ReceiverSizingInput,
    ReceiverSizingResult,
    calculate_receiver_size,
)
from app.domain.compressed_air.treatment.air_treatment import (
    AirTreatmentInput,
    AirTreatmentResult,
    calculate_air_treatment,
)


class InvalidGreenfieldSystemDesignInputError(ValueError):
    """Raised when greenfield compressed-air system inputs are invalid."""


@dataclass(frozen=True, slots=True)
class GreenfieldSystemDesignInput:
    """Input bundle for complete greenfield compressed-air design."""

    consumers: tuple[AirConsumer, ...]

    demand_profile_points: tuple[DemandProfilePoint, ...]

    leakage_fraction: Decimal = Decimal("0")
    future_expansion_fraction: Decimal = Decimal("0")
    other_allowance_fraction: Decimal = Decimal("0")

    minimum_point_of_use_pressure_bar_g: Decimal = Decimal("6")

    pressure_loss_components: tuple[PressureLossComponent, ...] = ()
    control_margin_bar: Decimal = Decimal("0")

    treatment_input: AirTreatmentInput | None = None

    station_configuration: CompressorStationConfiguration | None = None

    receiver_input: ReceiverSizingInput | None = None

    specific_power_kw_per_nm3_per_min: Decimal | None = None
    annual_operating_days: Decimal | None = None
    electricity_tariff_per_kwh: Decimal = Decimal("0")


@dataclass(frozen=True, slots=True)
class GreenfieldSystemDesignResult:
    """Integrated greenfield compressed-air system engineering result."""

    plant_demand: PlantDemandResult
    demand_profile: DemandProfileResult
    pressure_budget: PressureBudgetResult

    treatment: AirTreatmentResult | None
    station_capacity: CompressorStationCapacityResult | None
    receiver: ReceiverSizingResult | None
    energy: SystemEnergyResult | None

    required_design_flow_nm3_per_hr: Decimal
    required_compressor_discharge_pressure_bar_g: Decimal

    station_capacity_is_adequate: bool | None
    system_design_is_feasible: bool

    engineering_messages: tuple[str, ...]


def design_greenfield_system(
    inputs: GreenfieldSystemDesignInput,
) -> GreenfieldSystemDesignResult:
    """Run an integrated greenfield factory compressed-air system design."""

    if not inputs.consumers:
        raise InvalidGreenfieldSystemDesignInputError(
            "At least one compressed-air consumer is required."
        )

    if not inputs.demand_profile_points:
        raise InvalidGreenfieldSystemDesignInputError(
            "At least one demand profile point is required."
        )

    consumer_results = tuple(calculate_consumer_demand(consumer) for consumer in inputs.consumers)

    plant_demand = calculate_plant_demand(
        consumer_results,
        leakage_fraction=inputs.leakage_fraction,
        future_expansion_fraction=inputs.future_expansion_fraction,
        other_allowance_fraction=inputs.other_allowance_fraction,
    )

    demand_profile = calculate_demand_profile(inputs.demand_profile_points)

    pressure_budget = calculate_pressure_budget(
        minimum_point_of_use_pressure_bar_g=(inputs.minimum_point_of_use_pressure_bar_g),
        components=inputs.pressure_loss_components,
        control_margin_bar=inputs.control_margin_bar,
    )

    treatment_result = None

    if inputs.treatment_input is not None:
        treatment_result = calculate_air_treatment(inputs.treatment_input)

    station_capacity_result = None

    if inputs.station_configuration is not None:
        station_capacity_result = calculate_station_capacity(inputs.station_configuration)

    receiver_result = None

    if inputs.receiver_input is not None:
        receiver_result = calculate_receiver_size(inputs.receiver_input)

    energy_result = None

    if inputs.specific_power_kw_per_nm3_per_min is not None:
        if inputs.annual_operating_days is None:
            raise InvalidGreenfieldSystemDesignInputError(
                "Annual operating days are required for energy calculation."
            )

        energy_result = calculate_system_energy(
            SystemEnergyInput(
                demand_profile=demand_profile,
                specific_power_kw_per_nm3_per_min=(inputs.specific_power_kw_per_nm3_per_min),
                annual_operating_days=inputs.annual_operating_days,
                electricity_tariff_per_kwh=(inputs.electricity_tariff_per_kwh),
            )
        )

    messages: list[str] = []

    required_design_flow = plant_demand.design_flow_nm3_per_hr

    required_pressure = pressure_budget.required_compressor_discharge_pressure_bar_g

    if (
        treatment_result is not None
        and treatment_result.recommended_treatment_capacity_nm3_per_hr < required_design_flow
    ):
        messages.append("Treatment system capacity is below plant design flow.")

    station_capacity_is_adequate: bool | None

    if station_capacity_result is None:
        station_capacity_is_adequate = None
        messages.append("Compressor station configuration has not yet been evaluated.")
    else:
        station_capacity_is_adequate = station_capacity_result.available_capacity_is_adequate

        if not station_capacity_is_adequate:
            messages.append("Available compressor station capacity is below design flow.")

    if (
        inputs.station_configuration is not None
        and inputs.station_configuration.minimum_required_pressure_bar_g < required_pressure
    ):
        messages.append(
            "Selected compressor station pressure is below the calculated "
            "system pressure requirement."
        )

    if receiver_result is not None and receiver_result.storage_required:
        messages.append("Air storage is required to support the defined short-duration peak.")

    system_design_is_feasible = True

    if station_capacity_is_adequate is False:
        system_design_is_feasible = False

    if (
        inputs.station_configuration is not None
        and inputs.station_configuration.minimum_required_pressure_bar_g < required_pressure
    ):
        system_design_is_feasible = False

    if (
        treatment_result is not None
        and treatment_result.recommended_treatment_capacity_nm3_per_hr < required_design_flow
    ):
        system_design_is_feasible = False

    if system_design_is_feasible:
        messages.append(
            "Greenfield compressed-air system design is feasible at the "
            "current engineering screening level."
        )

    return GreenfieldSystemDesignResult(
        plant_demand=plant_demand,
        demand_profile=demand_profile,
        pressure_budget=pressure_budget,
        treatment=treatment_result,
        station_capacity=station_capacity_result,
        receiver=receiver_result,
        energy=energy_result,
        required_design_flow_nm3_per_hr=required_design_flow,
        required_compressor_discharge_pressure_bar_g=required_pressure,
        station_capacity_is_adequate=station_capacity_is_adequate,
        system_design_is_feasible=system_design_is_feasible,
        engineering_messages=tuple(messages),
    )
