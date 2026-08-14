from decimal import Decimal

import pytest

from app.domain.compressed_air.leakage.leakage_analysis import (
    InvalidLeakageManagementInputError,
    analyze_leakage_management,
)
from app.domain.compressed_air.leakage.leakage_models import (
    LeakageManagementInput,
    LeakPriority,
    LeakQuantificationBasis,
    LeakRegisterItem,
    LeakRepairStatus,
    LeakSourceCategory,
)


def leak(
    code: str,
    flow: str,
    *,
    repair_fraction: str = "1",
    repair_cost: str | None = None,
    verified_flow: str | None = None,
) -> LeakRegisterItem:
    return LeakRegisterItem(
        leak_code=code,
        location=f"Location {code}",
        baseline_leakage_flow_nm3_per_hr=Decimal(flow),
        quantification_basis=LeakQuantificationBasis.ULTRASONIC_ESTIMATE,
        source_category=LeakSourceCategory.FITTING,
        expected_repair_fraction=Decimal(repair_fraction),
        repair_status=LeakRepairStatus.OPEN,
        estimated_repair_cost=(Decimal(repair_cost) if repair_cost is not None else None),
        verified_post_repair_flow_nm3_per_hr=(
            Decimal(verified_flow) if verified_flow is not None else None
        ),
    )


def base_input(
    leaks: tuple[LeakRegisterItem, ...],
) -> LeakageManagementInput:
    return LeakageManagementInput(
        analysis_code="LEAK-001",
        leaks=leaks,
        specific_power_kw_per_nm3_per_min=Decimal("6"),
        annual_operating_hours=Decimal("8000"),
        electricity_tariff_per_kwh=Decimal("8"),
        average_system_demand_nm3_per_hr=Decimal("5000"),
    )


def test_aggregates_registered_leakage_energy_and_savings() -> None:
    result = analyze_leakage_management(
        base_input(
            (
                leak(
                    "L-001",
                    "600",
                    repair_fraction="0.80",
                ),
                leak(
                    "L-002",
                    "400",
                    repair_fraction="0.50",
                ),
            )
        )
    )

    assert result.leak_count == 2

    assert result.total_registered_leakage_flow_nm3_per_hr == Decimal("1000")

    assert result.leakage_fraction_of_average_system_demand == Decimal("0.2")

    assert result.total_wasted_power_kw == Decimal("100")
    assert result.total_annual_wasted_energy_kwh == Decimal("800000")
    assert result.total_annual_wasted_energy_cost == Decimal("6400000")

    assert result.total_recoverable_leakage_flow_nm3_per_hr == Decimal("680")
    assert result.total_recoverable_power_kw == Decimal("68")
    assert result.total_annual_energy_saving_kwh == Decimal("544000")
    assert result.total_annual_cost_saving == Decimal("4352000")

    assert result.total_residual_leakage_flow_nm3_per_hr == Decimal("320")


def test_priority_is_rule_based_on_registered_leak_share() -> None:
    result = analyze_leakage_management(
        base_input(
            (
                leak("CRITICAL", "700"),
                leak("HIGH", "150"),
                leak("MEDIUM", "40"),
                leak("LOW", "10"),
            )
        )
    )

    priorities = {item.leak_code: item.priority for item in result.items}

    assert priorities["CRITICAL"] == LeakPriority.CRITICAL
    assert priorities["HIGH"] == LeakPriority.HIGH
    assert priorities["MEDIUM"] == LeakPriority.MEDIUM
    assert priorities["LOW"] == LeakPriority.LOW


def test_repair_cost_generates_simple_payback() -> None:
    result = analyze_leakage_management(
        base_input(
            (
                leak(
                    "L-001",
                    "600",
                    repair_fraction="0.80",
                    repair_cost="100000",
                ),
            )
        )
    )

    item = result.items[0]

    assert item.estimated_repair_cost == Decimal("100000")
    assert item.simple_payback_years == (Decimal("100000") / Decimal("3072000"))


def test_post_repair_verification_is_calculated() -> None:
    result = analyze_leakage_management(
        base_input(
            (
                leak(
                    "L-001",
                    "600",
                    verified_flow="100",
                ),
            )
        )
    )

    item = result.items[0]

    assert result.verified_leak_count == 1
    assert result.verified_flow_reduction_nm3_per_hr == Decimal("500")

    assert item.verified_flow_reduction_nm3_per_hr == Decimal("500")

    assert item.verified_repair_fraction == (Decimal("500") / Decimal("600"))


def test_no_verified_leaks_returns_zero_verified_reduction() -> None:
    result = analyze_leakage_management(
        base_input(
            (
                leak("L-001", "300"),
                leak("L-002", "200"),
            )
        )
    )

    assert result.verified_leak_count == 0
    assert result.verified_flow_reduction_nm3_per_hr == Decimal("0")

    assert result.items[0].verified_repair_fraction is None


def test_duplicate_leak_codes_are_rejected() -> None:
    with pytest.raises(
        InvalidLeakageManagementInputError,
        match="Duplicate leak code",
    ):
        analyze_leakage_management(
            base_input(
                (
                    leak("L-001", "300"),
                    leak("L-001", "200"),
                )
            )
        )


def test_empty_leak_register_is_rejected() -> None:
    with pytest.raises(
        InvalidLeakageManagementInputError,
        match="At least one leakage register item is required",
    ):
        analyze_leakage_management(base_input(()))


def test_negative_baseline_leakage_is_rejected() -> None:
    with pytest.raises(
        InvalidLeakageManagementInputError,
        match="baseline leakage flow cannot be negative",
    ):
        analyze_leakage_management(base_input((leak("L-001", "-1"),)))


def test_invalid_expected_repair_fraction_is_rejected() -> None:
    with pytest.raises(
        InvalidLeakageManagementInputError,
        match="expected repair fraction must be between zero and one",
    ):
        analyze_leakage_management(
            base_input(
                (
                    leak(
                        "L-001",
                        "100",
                        repair_fraction="1.10",
                    ),
                )
            )
        )


def test_invalid_average_system_demand_is_rejected() -> None:
    inputs = LeakageManagementInput(
        analysis_code="LEAK-001",
        leaks=(leak("L-001", "100"),),
        specific_power_kw_per_nm3_per_min=Decimal("6"),
        annual_operating_hours=Decimal("8000"),
        electricity_tariff_per_kwh=Decimal("8"),
        average_system_demand_nm3_per_hr=Decimal("0"),
    )

    with pytest.raises(
        InvalidLeakageManagementInputError,
        match="Average system demand must be greater than zero",
    ):
        analyze_leakage_management(inputs)
