from dataclasses import dataclass
from decimal import Decimal

from app.domain.centrifugal.centrifugal_models import (
    CentrifugalDriverType,
    CentrifugalOperatingPoint,
)
from app.domain.centrifugal.impeller import (
    ImpellerSizingResult,
    calculate_impeller_sizing,
)
from app.domain.centrifugal.performance_map import (
    PerformanceMapResult,
    calculate_performance_map,
)
from app.domain.centrifugal.polytropic_head import (
    PolytropicHeadResult,
    calculate_polytropic_head,
)
from app.domain.centrifugal.power import (
    CentrifugalPowerCalculationResult,
    calculate_centrifugal_power,
)
from app.domain.centrifugal.surge import (
    SurgeControlResult,
    calculate_surge_control,
)


@dataclass(frozen=True, slots=True)
class CentrifugalEngineInput:
    """Input data for integrated centrifugal compressor sizing."""

    operating_point: CentrifugalOperatingPoint

    number_of_impeller_stages: int
    head_coefficient: Decimal
    rotational_speed_rpm: Decimal

    mechanical_loss_fraction: Decimal
    driver_margin_fraction: Decimal
    selected_driver_power_kw: Decimal
    driver_type: CentrifugalDriverType
    motor_efficiency: Decimal | None = None

    surge_flow_fraction: Decimal = Decimal("0.70")
    anti_surge_margin_fraction: Decimal = Decimal("0.10")
    stonewall_flow_fraction: Decimal = Decimal("1.25")


@dataclass(frozen=True, slots=True)
class CentrifugalEngineResult:
    """Integrated centrifugal compressor sizing result."""

    head: PolytropicHeadResult
    impeller: ImpellerSizingResult
    power: CentrifugalPowerCalculationResult
    surge: SurgeControlResult
    performance_map: PerformanceMapResult


def calculate_centrifugal_case(
    inputs: CentrifugalEngineInput,
) -> CentrifugalEngineResult:
    """Run an integrated centrifugal compressor sizing calculation."""

    head = calculate_polytropic_head(
        inputs.operating_point,
    )

    impeller = calculate_impeller_sizing(
        total_polytropic_head_kj_per_kg=head.polytropic_head_kj_per_kg,
        number_of_impeller_stages=inputs.number_of_impeller_stages,
        head_coefficient=inputs.head_coefficient,
        rotational_speed_rpm=inputs.rotational_speed_rpm,
    )

    power = calculate_centrifugal_power(
        mass_flow_kg_per_s=inputs.operating_point.mass_flow_kg_per_s,
        polytropic_head_kj_per_kg=head.polytropic_head_kj_per_kg,
        polytropic_efficiency=inputs.operating_point.polytropic_efficiency,
        mechanical_loss_fraction=inputs.mechanical_loss_fraction,
        driver_margin_fraction=inputs.driver_margin_fraction,
        selected_driver_power_kw=inputs.selected_driver_power_kw,
        driver_type=inputs.driver_type,
        motor_efficiency=inputs.motor_efficiency,
    )

    design_flow_m3_per_hr = inputs.operating_point.actual_flow_m3_per_s * Decimal("3600")

    surge = calculate_surge_control(
        design_flow_m3_per_hr=design_flow_m3_per_hr,
        surge_flow_fraction=inputs.surge_flow_fraction,
        anti_surge_margin_fraction=inputs.anti_surge_margin_fraction,
        stonewall_flow_fraction=inputs.stonewall_flow_fraction,
    )

    performance_map = calculate_performance_map(
        design_speed_rpm=inputs.rotational_speed_rpm,
        design_flow_m3_per_hr=design_flow_m3_per_hr,
        design_head_kj_per_kg=head.polytropic_head_kj_per_kg,
    )

    return CentrifugalEngineResult(
        head=head,
        impeller=impeller,
        power=power,
        surge=surge,
        performance_map=performance_map,
    )
