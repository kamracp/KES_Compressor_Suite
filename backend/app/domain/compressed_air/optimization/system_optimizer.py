from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum

from app.domain.compressed_air.brownfield.audit_analysis import (
    BrownfieldAuditAnalysisResult,
)
from app.domain.compressed_air.brownfield.opportunity_engine import (
    BrownfieldOpportunityResult,
)
from app.domain.compressed_air.distribution.network_optimizer import (
    NetworkOptimizationResult,
)
from app.domain.compressed_air.skid.skid_models import AirSkidAssessmentResult
from app.domain.compressed_air.station.station_models import (
    CompressorStationCapacityResult,
)


class SystemOptimizationCategory(StrEnum):
    CAPACITY = "CAPACITY"
    CONTROL = "CONTROL"
    LEAKAGE = "LEAKAGE"
    PRESSURE = "PRESSURE"
    DISTRIBUTION = "DISTRIBUTION"
    SKID = "SKID"
    TREATMENT = "TREATMENT"
    STORAGE = "STORAGE"
    ENERGY = "ENERGY"


class SystemOptimizationPriority(StrEnum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass(frozen=True, slots=True)
class SystemOptimizationAction:
    """One integrated factory compressed-air optimization action."""

    action_code: str
    category: SystemOptimizationCategory
    priority: SystemOptimizationPriority

    title: str
    rationale: str

    estimated_power_saving_kw: Decimal = Decimal("0")
    estimated_annual_energy_saving_kwh: Decimal = Decimal("0")
    estimated_annual_cost_saving: Decimal = Decimal("0")


@dataclass(frozen=True, slots=True)
class SystemOptimizationResult:
    """Integrated compressed-air system optimization result."""

    actions: tuple[SystemOptimizationAction, ...]

    total_estimated_power_saving_kw: Decimal
    total_estimated_annual_energy_saving_kwh: Decimal
    total_estimated_annual_cost_saving: Decimal

    critical_action_count: int
    high_priority_action_count: int

    system_requires_improvement: bool


def optimize_compressed_air_system(
    *,
    station_capacity: CompressorStationCapacityResult | None = None,
    skid_assessment: AirSkidAssessmentResult | None = None,
    distribution_optimization: NetworkOptimizationResult | None = None,
    brownfield_analysis: BrownfieldAuditAnalysisResult | None = None,
    brownfield_opportunities: BrownfieldOpportunityResult | None = None,
) -> SystemOptimizationResult:
    """Build integrated optimization actions for a factory air system."""

    actions: list[SystemOptimizationAction] = []

    if station_capacity is not None:
        if not station_capacity.available_capacity_is_adequate:
            actions.append(
                SystemOptimizationAction(
                    action_code="STATION-CAPACITY-SHORTFALL",
                    category=SystemOptimizationCategory.CAPACITY,
                    priority=SystemOptimizationPriority.CRITICAL,
                    title="Increase available compressor station capacity",
                    rationale=("Available compressor capacity is below the required design flow."),
                )
            )

    if skid_assessment is not None:
        if not skid_assessment.flow_capacity_is_adequate:
            actions.append(
                SystemOptimizationAction(
                    action_code="SKID-FLOW-CAPACITY",
                    category=SystemOptimizationCategory.SKID,
                    priority=SystemOptimizationPriority.HIGH,
                    title="Correct undersized skid components",
                    rationale=(
                        "One or more flow-critical skid components are "
                        "undersized for the design flow."
                    ),
                )
            )

        if not skid_assessment.pressure_rating_is_adequate:
            actions.append(
                SystemOptimizationAction(
                    action_code="SKID-PRESSURE-RATING",
                    category=SystemOptimizationCategory.SKID,
                    priority=SystemOptimizationPriority.CRITICAL,
                    title="Correct insufficient skid pressure rating",
                    rationale=(
                        "One or more skid components have pressure ratings "
                        "below the system design pressure."
                    ),
                )
            )

        if not skid_assessment.instrumentation_is_complete:
            actions.append(
                SystemOptimizationAction(
                    action_code="SKID-INSTRUMENTATION",
                    category=SystemOptimizationCategory.SKID,
                    priority=SystemOptimizationPriority.MEDIUM,
                    title="Complete skid monitoring instrumentation",
                    rationale=("Flow, pressure, and dew-point monitoring are not all available."),
                )
            )

    if distribution_optimization is not None:
        if distribution_optimization.optimization_required:
            actions.append(
                SystemOptimizationAction(
                    action_code="DISTRIBUTION-UPGRADE",
                    category=SystemOptimizationCategory.DISTRIBUTION,
                    priority=SystemOptimizationPriority.HIGH,
                    title="Reduce compressed-air distribution losses",
                    rationale=(
                        "One or more consumer paths are pressure deficient. "
                        "Header or branch resizing can reduce system losses."
                    ),
                )
            )

    if brownfield_analysis is not None:
        if brownfield_analysis.high_unloaded_running_detected:
            actions.append(
                SystemOptimizationAction(
                    action_code="CONTROL-UNLOAD-REDUCTION",
                    category=SystemOptimizationCategory.CONTROL,
                    priority=SystemOptimizationPriority.HIGH,
                    title="Reduce unloaded compressor operation",
                    rationale=("Measured compressor operation shows significant unloaded running."),
                )
            )

        if brownfield_analysis.significant_leakage_detected:
            actions.append(
                SystemOptimizationAction(
                    action_code="LEAKAGE-REDUCTION",
                    category=SystemOptimizationCategory.LEAKAGE,
                    priority=SystemOptimizationPriority.HIGH,
                    title="Reduce compressed-air leakage",
                    rationale=("Measured leakage is significant relative to average plant demand."),
                )
            )

    if brownfield_opportunities is not None:
        for opportunity in brownfield_opportunities.opportunities:
            category = _map_brownfield_category(opportunity.category.value)

            priority = _map_brownfield_priority(opportunity.priority.value)

            actions.append(
                SystemOptimizationAction(
                    action_code=f"BF-{opportunity.opportunity_code}",
                    category=category,
                    priority=priority,
                    title=opportunity.title,
                    rationale=opportunity.rationale,
                    estimated_power_saving_kw=(opportunity.estimated_power_saving_kw),
                    estimated_annual_energy_saving_kwh=(
                        opportunity.estimated_annual_energy_saving_kwh
                    ),
                    estimated_annual_cost_saving=(opportunity.estimated_annual_cost_saving),
                )
            )

    actions = _deduplicate_actions(actions)

    actions.sort(
        key=lambda item: (
            _priority_rank(item.priority),
            item.estimated_annual_cost_saving,
        ),
        reverse=True,
    )

    total_power_saving = sum(
        (action.estimated_power_saving_kw for action in actions),
        start=Decimal("0"),
    )

    total_energy_saving = sum(
        (action.estimated_annual_energy_saving_kwh for action in actions),
        start=Decimal("0"),
    )

    total_cost_saving = sum(
        (action.estimated_annual_cost_saving for action in actions),
        start=Decimal("0"),
    )

    critical_action_count = sum(
        1 for action in actions if action.priority == SystemOptimizationPriority.CRITICAL
    )

    high_priority_action_count = sum(
        1 for action in actions if action.priority == SystemOptimizationPriority.HIGH
    )

    return SystemOptimizationResult(
        actions=tuple(actions),
        total_estimated_power_saving_kw=total_power_saving,
        total_estimated_annual_energy_saving_kwh=total_energy_saving,
        total_estimated_annual_cost_saving=total_cost_saving,
        critical_action_count=critical_action_count,
        high_priority_action_count=high_priority_action_count,
        system_requires_improvement=bool(actions),
    )


def _map_brownfield_category(
    category: str,
) -> SystemOptimizationCategory:
    mapping = {
        "LEAKAGE": SystemOptimizationCategory.LEAKAGE,
        "UNLOADED_RUNNING": SystemOptimizationCategory.CONTROL,
        "PRESSURE": SystemOptimizationCategory.PRESSURE,
        "CAPACITY": SystemOptimizationCategory.CAPACITY,
        "UTILIZATION": SystemOptimizationCategory.ENERGY,
    }

    return mapping.get(
        category,
        SystemOptimizationCategory.ENERGY,
    )


def _map_brownfield_priority(
    priority: str,
) -> SystemOptimizationPriority:
    mapping = {
        "HIGH": SystemOptimizationPriority.HIGH,
        "MEDIUM": SystemOptimizationPriority.MEDIUM,
        "LOW": SystemOptimizationPriority.LOW,
    }

    return mapping.get(
        priority,
        SystemOptimizationPriority.MEDIUM,
    )


def _priority_rank(
    priority: SystemOptimizationPriority,
) -> int:
    return {
        SystemOptimizationPriority.CRITICAL: 4,
        SystemOptimizationPriority.HIGH: 3,
        SystemOptimizationPriority.MEDIUM: 2,
        SystemOptimizationPriority.LOW: 1,
    }[priority]


def _deduplicate_actions(
    actions: list[SystemOptimizationAction],
) -> list[SystemOptimizationAction]:
    unique: dict[str, SystemOptimizationAction] = {}

    for action in actions:
        unique.setdefault(
            action.action_code,
            action,
        )

    return list(unique.values())
