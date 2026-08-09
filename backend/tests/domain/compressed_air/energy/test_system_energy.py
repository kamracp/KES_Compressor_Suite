from decimal import Decimal

import pytest

from app.domain.compressed_air.energy.system_energy import (
    InvalidSystemEnergyInputError,
    SystemEnergyInput,
    calculate_system_energy,
)
from app.domain.compressed_air.profiles.demand_profile import (
    DemandProfilePoint,
    calculate_demand_profile,
)


def build_profile():
    return calculate_demand_profile(
        (
            DemandProfilePoint(
                period_index=1,
                label="Low Demand",
                demand_nm3_per_hr=Decimal("1200"),
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


def test_calculate_annual_system_energy() -> None:
    result = calculate_system_energy(
        SystemEnergyInput(
            demand_profile=build_profile(),
            specific_power_kw_per_nm3_per_min=Decimal("6.5"),
            annual_operating_days=Decimal("330"),
            electricity_tariff_per_kwh=Decimal("8"),
        )
    )

    assert result.average_demand_nm3_per_hr > Decimal("0")
    assert result.average_demand_nm3_per_min > Decimal("0")
    assert result.loaded_power_kw > Decimal("0")

    assert result.annual_operating_hours == Decimal("7920")
    assert result.annual_energy_kwh > Decimal("0")

    assert result.annual_energy_cost == (result.annual_energy_kwh * Decimal("8"))

    assert result.effective_specific_energy_kwh_per_1000_nm3 > Decimal("0")


def test_unloaded_operation_changes_effective_power() -> None:
    loaded_only = calculate_system_energy(
        SystemEnergyInput(
            demand_profile=build_profile(),
            specific_power_kw_per_nm3_per_min=Decimal("6.5"),
            annual_operating_days=Decimal("330"),
            unload_power_fraction=Decimal("0"),
            average_unloaded_fraction=Decimal("0"),
        )
    )

    partially_unloaded = calculate_system_energy(
        SystemEnergyInput(
            demand_profile=build_profile(),
            specific_power_kw_per_nm3_per_min=Decimal("6.5"),
            annual_operating_days=Decimal("330"),
            unload_power_fraction=Decimal("0.30"),
            average_unloaded_fraction=Decimal("0.10"),
        )
    )

    assert partially_unloaded.unload_power_kw > Decimal("0")

    assert partially_unloaded.effective_average_power_kw < loaded_only.effective_average_power_kw


def test_higher_specific_power_increases_energy_consumption() -> None:
    efficient = calculate_system_energy(
        SystemEnergyInput(
            demand_profile=build_profile(),
            specific_power_kw_per_nm3_per_min=Decimal("6.0"),
            annual_operating_days=Decimal("330"),
        )
    )

    inefficient = calculate_system_energy(
        SystemEnergyInput(
            demand_profile=build_profile(),
            specific_power_kw_per_nm3_per_min=Decimal("7.5"),
            annual_operating_days=Decimal("330"),
        )
    )

    assert inefficient.loaded_power_kw > efficient.loaded_power_kw
    assert inefficient.annual_energy_kwh > efficient.annual_energy_kwh


def test_higher_tariff_increases_annual_cost_only() -> None:
    low_tariff = calculate_system_energy(
        SystemEnergyInput(
            demand_profile=build_profile(),
            specific_power_kw_per_nm3_per_min=Decimal("6.5"),
            annual_operating_days=Decimal("330"),
            electricity_tariff_per_kwh=Decimal("6"),
        )
    )

    high_tariff = calculate_system_energy(
        SystemEnergyInput(
            demand_profile=build_profile(),
            specific_power_kw_per_nm3_per_min=Decimal("6.5"),
            annual_operating_days=Decimal("330"),
            electricity_tariff_per_kwh=Decimal("10"),
        )
    )

    assert low_tariff.annual_energy_kwh == high_tariff.annual_energy_kwh

    assert high_tariff.annual_energy_cost > low_tariff.annual_energy_cost


def test_profile_repetitions_increase_annual_hours_and_energy() -> None:
    one_cycle = calculate_system_energy(
        SystemEnergyInput(
            demand_profile=build_profile(),
            specific_power_kw_per_nm3_per_min=Decimal("6.5"),
            annual_operating_days=Decimal("100"),
            profile_repetitions_per_day=Decimal("1"),
        )
    )

    two_cycles = calculate_system_energy(
        SystemEnergyInput(
            demand_profile=build_profile(),
            specific_power_kw_per_nm3_per_min=Decimal("6.5"),
            annual_operating_days=Decimal("100"),
            profile_repetitions_per_day=Decimal("2"),
        )
    )

    assert two_cycles.annual_operating_hours == one_cycle.annual_operating_hours * Decimal("2")

    assert two_cycles.annual_energy_kwh == one_cycle.annual_energy_kwh * Decimal("2")


def test_zero_specific_power_is_rejected() -> None:
    with pytest.raises(
        InvalidSystemEnergyInputError,
        match="Specific power must be greater than zero",
    ):
        calculate_system_energy(
            SystemEnergyInput(
                demand_profile=build_profile(),
                specific_power_kw_per_nm3_per_min=Decimal("0"),
                annual_operating_days=Decimal("330"),
            )
        )


def test_zero_operating_days_is_rejected() -> None:
    with pytest.raises(
        InvalidSystemEnergyInputError,
        match="Annual operating days must be greater than zero",
    ):
        calculate_system_energy(
            SystemEnergyInput(
                demand_profile=build_profile(),
                specific_power_kw_per_nm3_per_min=Decimal("6.5"),
                annual_operating_days=Decimal("0"),
            )
        )


def test_negative_tariff_is_rejected() -> None:
    with pytest.raises(
        InvalidSystemEnergyInputError,
        match="Electricity tariff cannot be negative",
    ):
        calculate_system_energy(
            SystemEnergyInput(
                demand_profile=build_profile(),
                specific_power_kw_per_nm3_per_min=Decimal("6.5"),
                annual_operating_days=Decimal("330"),
                electricity_tariff_per_kwh=Decimal("-1"),
            )
        )


def test_invalid_unload_power_fraction_is_rejected() -> None:
    with pytest.raises(
        InvalidSystemEnergyInputError,
        match="Unload power fraction must be between zero and one",
    ):
        calculate_system_energy(
            SystemEnergyInput(
                demand_profile=build_profile(),
                specific_power_kw_per_nm3_per_min=Decimal("6.5"),
                annual_operating_days=Decimal("330"),
                unload_power_fraction=Decimal("1.10"),
            )
        )


def test_invalid_average_unloaded_fraction_is_rejected() -> None:
    with pytest.raises(
        InvalidSystemEnergyInputError,
        match="Average unloaded fraction must be between zero and one",
    ):
        calculate_system_energy(
            SystemEnergyInput(
                demand_profile=build_profile(),
                specific_power_kw_per_nm3_per_min=Decimal("6.5"),
                annual_operating_days=Decimal("330"),
                average_unloaded_fraction=Decimal("-0.1"),
            )
        )
