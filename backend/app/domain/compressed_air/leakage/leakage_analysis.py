from decimal import Decimal

from app.domain.compressed_air.energy.leakage_energy import (
    LeakageEnergyInput,
    calculate_leakage_energy,
)
from app.domain.compressed_air.leakage.leakage_models import (
    LeakageManagementInput,
    LeakageManagementResult,
    LeakItemAnalysisResult,
    LeakPriority,
)


class InvalidLeakageManagementInputError(ValueError):
    """Raised when leakage-management study inputs are invalid."""


ZERO = Decimal("0")

CRITICAL_LEAK_SHARE = Decimal("0.25")
HIGH_LEAK_SHARE = Decimal("0.10")
MEDIUM_LEAK_SHARE = Decimal("0.03")


def analyze_leakage_management(
    inputs: LeakageManagementInput,
) -> LeakageManagementResult:
    """Analyze a registered compressed-air leakage survey."""

    _validate_inputs(inputs)

    total_registered_leakage_flow = sum(
        (item.baseline_leakage_flow_nm3_per_hr for item in inputs.leaks),
        ZERO,
    )

    item_results: list[LeakItemAnalysisResult] = []

    for item in inputs.leaks:
        if total_registered_leakage_flow > ZERO:
            fraction_of_total = (
                item.baseline_leakage_flow_nm3_per_hr / total_registered_leakage_flow
            )
        else:
            fraction_of_total = ZERO

        energy = calculate_leakage_energy(
            LeakageEnergyInput(
                leakage_flow_nm3_per_hr=(item.baseline_leakage_flow_nm3_per_hr),
                specific_power_kw_per_nm3_per_min=(inputs.specific_power_kw_per_nm3_per_min),
                annual_operating_hours=inputs.annual_operating_hours,
                electricity_tariff_per_kwh=(inputs.electricity_tariff_per_kwh),
                expected_repair_fraction=(item.expected_repair_fraction),
                demand_saving_control_factor=(inputs.demand_saving_control_factor),
            )
        )

        simple_payback_years = _calculate_simple_payback(
            estimated_repair_cost=item.estimated_repair_cost,
            annual_cost_saving=energy.annual_cost_saving,
        )

        (
            verified_flow_reduction,
            verified_repair_fraction,
        ) = _calculate_verified_repair(
            baseline_flow=item.baseline_leakage_flow_nm3_per_hr,
            verified_post_repair_flow=(item.verified_post_repair_flow_nm3_per_hr),
        )

        item_results.append(
            LeakItemAnalysisResult(
                leak_code=item.leak_code,
                location=item.location,
                source_category=item.source_category,
                quantification_basis=item.quantification_basis,
                repair_status=item.repair_status,
                priority=_determine_priority(fraction_of_total),
                baseline_leakage_flow_nm3_per_hr=(item.baseline_leakage_flow_nm3_per_hr),
                fraction_of_total_registered_leakage=fraction_of_total,
                energy=energy,
                estimated_repair_cost=item.estimated_repair_cost,
                simple_payback_years=simple_payback_years,
                verified_post_repair_flow_nm3_per_hr=(item.verified_post_repair_flow_nm3_per_hr),
                verified_flow_reduction_nm3_per_hr=(verified_flow_reduction),
                verified_repair_fraction=verified_repair_fraction,
                notes=item.notes,
            )
        )

    leakage_fraction_of_average_system_demand = None

    if inputs.average_system_demand_nm3_per_hr is not None:
        leakage_fraction_of_average_system_demand = (
            total_registered_leakage_flow / inputs.average_system_demand_nm3_per_hr
        )

    verified_items = [
        result for result in item_results if result.verified_post_repair_flow_nm3_per_hr is not None
    ]

    verified_flow_reduction = sum(
        (result.verified_flow_reduction_nm3_per_hr or ZERO for result in verified_items),
        ZERO,
    )

    return LeakageManagementResult(
        analysis_code=inputs.analysis_code,
        leak_count=len(item_results),
        total_registered_leakage_flow_nm3_per_hr=(total_registered_leakage_flow),
        leakage_fraction_of_average_system_demand=(leakage_fraction_of_average_system_demand),
        total_wasted_power_kw=sum(
            (result.energy.wasted_power_kw for result in item_results),
            ZERO,
        ),
        total_annual_wasted_energy_kwh=sum(
            (result.energy.annual_wasted_energy_kwh for result in item_results),
            ZERO,
        ),
        total_annual_wasted_energy_cost=sum(
            (result.energy.annual_wasted_energy_cost for result in item_results),
            ZERO,
        ),
        total_recoverable_leakage_flow_nm3_per_hr=sum(
            (result.energy.recoverable_leakage_flow_nm3_per_hr for result in item_results),
            ZERO,
        ),
        total_recoverable_power_kw=sum(
            (result.energy.recoverable_power_kw for result in item_results),
            ZERO,
        ),
        total_annual_energy_saving_kwh=sum(
            (result.energy.annual_energy_saving_kwh for result in item_results),
            ZERO,
        ),
        total_annual_cost_saving=sum(
            (result.energy.annual_cost_saving for result in item_results),
            ZERO,
        ),
        total_residual_leakage_flow_nm3_per_hr=sum(
            (result.energy.residual_leakage_flow_nm3_per_hr for result in item_results),
            ZERO,
        ),
        verified_leak_count=len(verified_items),
        verified_flow_reduction_nm3_per_hr=verified_flow_reduction,
        items=tuple(item_results),
    )


def _determine_priority(
    fraction_of_total_registered_leakage: Decimal,
) -> LeakPriority:
    if fraction_of_total_registered_leakage >= CRITICAL_LEAK_SHARE:
        return LeakPriority.CRITICAL

    if fraction_of_total_registered_leakage >= HIGH_LEAK_SHARE:
        return LeakPriority.HIGH

    if fraction_of_total_registered_leakage >= MEDIUM_LEAK_SHARE:
        return LeakPriority.MEDIUM

    return LeakPriority.LOW


def _calculate_simple_payback(
    estimated_repair_cost: Decimal | None,
    annual_cost_saving: Decimal,
) -> Decimal | None:
    if estimated_repair_cost is None:
        return None

    if annual_cost_saving <= ZERO:
        return None

    return estimated_repair_cost / annual_cost_saving


def _calculate_verified_repair(
    baseline_flow: Decimal,
    verified_post_repair_flow: Decimal | None,
) -> tuple[Decimal | None, Decimal | None]:
    if verified_post_repair_flow is None:
        return None, None

    verified_flow_reduction = baseline_flow - verified_post_repair_flow

    if baseline_flow <= ZERO:
        return verified_flow_reduction, None

    verified_repair_fraction = verified_flow_reduction / baseline_flow

    return verified_flow_reduction, verified_repair_fraction


def _validate_inputs(
    inputs: LeakageManagementInput,
) -> None:
    if not inputs.analysis_code.strip():
        raise InvalidLeakageManagementInputError("Analysis code is required.")

    if not inputs.leaks:
        raise InvalidLeakageManagementInputError("At least one leakage register item is required.")

    if inputs.specific_power_kw_per_nm3_per_min <= ZERO:
        raise InvalidLeakageManagementInputError("Specific power must be greater than zero.")

    if inputs.annual_operating_hours <= ZERO:
        raise InvalidLeakageManagementInputError(
            "Annual operating hours must be greater than zero."
        )

    if inputs.electricity_tariff_per_kwh < ZERO:
        raise InvalidLeakageManagementInputError("Electricity tariff cannot be negative.")

    if (
        inputs.average_system_demand_nm3_per_hr is not None
        and inputs.average_system_demand_nm3_per_hr <= ZERO
    ):
        raise InvalidLeakageManagementInputError("Average system demand must be greater than zero.")

    leak_codes: set[str] = set()

    for index, item in enumerate(inputs.leaks):
        prefix = f"Leak item {index + 1}"

        normalized_code = item.leak_code.strip()

        if not normalized_code:
            raise InvalidLeakageManagementInputError(f"{prefix} leak code is required.")

        if normalized_code in leak_codes:
            raise InvalidLeakageManagementInputError(f"Duplicate leak code: {normalized_code}.")

        leak_codes.add(normalized_code)

        if not item.location.strip():
            raise InvalidLeakageManagementInputError(f"{prefix} location is required.")

        if item.baseline_leakage_flow_nm3_per_hr < ZERO:
            raise InvalidLeakageManagementInputError(
                f"{prefix} baseline leakage flow cannot be negative."
            )

        if item.survey_pressure_bar_g is not None and item.survey_pressure_bar_g < ZERO:
            raise InvalidLeakageManagementInputError(
                f"{prefix} survey pressure cannot be negative."
            )

        if item.expected_repair_fraction < ZERO or item.expected_repair_fraction > Decimal("1"):
            raise InvalidLeakageManagementInputError(
                f"{prefix} expected repair fraction must be between zero and one."
            )

        if item.estimated_repair_cost is not None and item.estimated_repair_cost < ZERO:
            raise InvalidLeakageManagementInputError(
                f"{prefix} estimated repair cost cannot be negative."
            )

        if (
            item.verified_post_repair_flow_nm3_per_hr is not None
            and item.verified_post_repair_flow_nm3_per_hr < ZERO
        ):
            raise InvalidLeakageManagementInputError(
                f"{prefix} verified post-repair flow cannot be negative."
            )
