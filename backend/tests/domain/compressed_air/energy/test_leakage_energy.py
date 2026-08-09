from decimal import Decimal

import pytest

from app.domain.compressed_air.energy.leakage_energy import (
    InvalidLeakageEnergyInputError,
    LeakageEnergyInput,
    calculate_leakage_energy,
)


def test_calculate_leakage_energy_loss() -> None:
    result = calculate_leakage_energy(
        LeakageEnergyInput(
            leakage_flow_nm3_per_hr=Decimal("600"),
            specific_power_kw_per_nm3_per_min=Decimal("6.5"),
            annual_operating_hours=Decimal("8000"),
            electricity_tariff_per_kwh=Decimal("8"),
            expected_repair_fraction=Decimal("0.80"),
        )
    )

    assert result.leakage_flow_nm3_per_min == Decimal("10")
    assert result.wasted_power_kw == Decimal("65.0")

    assert result.annual_wasted_energy_kwh == Decimal("520000.0")
    assert result.annual_wasted_energy_cost == Decimal("4160000.0")

    assert result.recoverable_leakage_flow_nm3_per_hr == Decimal("480.00")
    assert result.recoverable_power_kw == Decimal("52.000")

    assert result.annual_energy_saving_kwh == Decimal("416000.000")
    assert result.annual_cost_saving == Decimal("3328000.000")

    assert result.residual_leakage_flow_nm3_per_hr == Decimal("120.00")


def test_zero_leakage_has_zero_energy_loss() -> None:
    result = calculate_leakage_energy(
        LeakageEnergyInput(
            leakage_flow_nm3_per_hr=Decimal("0"),
            specific_power_kw_per_nm3_per_min=Decimal("6.5"),
            annual_operating_hours=Decimal("8000"),
            electricity_tariff_per_kwh=Decimal("8"),
        )
    )

    assert result.leakage_flow_nm3_per_min == Decimal("0")
    assert result.wasted_power_kw == Decimal("0")
    assert result.annual_wasted_energy_kwh == Decimal("0")
    assert result.annual_wasted_energy_cost == Decimal("0")
    assert result.annual_cost_saving == Decimal("0")


def test_full_repair_removes_all_leakage() -> None:
    result = calculate_leakage_energy(
        LeakageEnergyInput(
            leakage_flow_nm3_per_hr=Decimal("500"),
            specific_power_kw_per_nm3_per_min=Decimal("6"),
            annual_operating_hours=Decimal("7000"),
            electricity_tariff_per_kwh=Decimal("8"),
            expected_repair_fraction=Decimal("1"),
        )
    )

    assert result.recoverable_leakage_flow_nm3_per_hr == Decimal("500")
    assert result.residual_leakage_flow_nm3_per_hr == Decimal("0")

    assert result.annual_energy_saving_kwh == (result.annual_wasted_energy_kwh)

    assert result.annual_cost_saving == result.annual_wasted_energy_cost


def test_partial_repair_leaves_residual_leakage() -> None:
    result = calculate_leakage_energy(
        LeakageEnergyInput(
            leakage_flow_nm3_per_hr=Decimal("1000"),
            specific_power_kw_per_nm3_per_min=Decimal("6.5"),
            annual_operating_hours=Decimal("8000"),
            electricity_tariff_per_kwh=Decimal("8"),
            expected_repair_fraction=Decimal("0.60"),
        )
    )

    assert result.recoverable_leakage_flow_nm3_per_hr == Decimal("600.00")
    assert result.residual_leakage_flow_nm3_per_hr == Decimal("400.00")


def test_higher_tariff_increases_cost_loss_and_saving() -> None:
    low_tariff = calculate_leakage_energy(
        LeakageEnergyInput(
            leakage_flow_nm3_per_hr=Decimal("600"),
            specific_power_kw_per_nm3_per_min=Decimal("6.5"),
            annual_operating_hours=Decimal("8000"),
            electricity_tariff_per_kwh=Decimal("6"),
            expected_repair_fraction=Decimal("0.80"),
        )
    )

    high_tariff = calculate_leakage_energy(
        LeakageEnergyInput(
            leakage_flow_nm3_per_hr=Decimal("600"),
            specific_power_kw_per_nm3_per_min=Decimal("6.5"),
            annual_operating_hours=Decimal("8000"),
            electricity_tariff_per_kwh=Decimal("10"),
            expected_repair_fraction=Decimal("0.80"),
        )
    )

    assert low_tariff.wasted_power_kw == high_tariff.wasted_power_kw
    assert low_tariff.annual_wasted_energy_kwh == high_tariff.annual_wasted_energy_kwh

    assert high_tariff.annual_wasted_energy_cost > low_tariff.annual_wasted_energy_cost

    assert high_tariff.annual_cost_saving > low_tariff.annual_cost_saving


def test_higher_specific_power_increases_leakage_energy_penalty() -> None:
    efficient = calculate_leakage_energy(
        LeakageEnergyInput(
            leakage_flow_nm3_per_hr=Decimal("600"),
            specific_power_kw_per_nm3_per_min=Decimal("5.5"),
            annual_operating_hours=Decimal("8000"),
            electricity_tariff_per_kwh=Decimal("8"),
        )
    )

    inefficient = calculate_leakage_energy(
        LeakageEnergyInput(
            leakage_flow_nm3_per_hr=Decimal("600"),
            specific_power_kw_per_nm3_per_min=Decimal("7.0"),
            annual_operating_hours=Decimal("8000"),
            electricity_tariff_per_kwh=Decimal("8"),
        )
    )

    assert inefficient.wasted_power_kw > efficient.wasted_power_kw
    assert inefficient.annual_wasted_energy_kwh > efficient.annual_wasted_energy_kwh


def test_negative_leakage_is_rejected() -> None:
    with pytest.raises(
        InvalidLeakageEnergyInputError,
        match="Leakage flow cannot be negative",
    ):
        calculate_leakage_energy(
            LeakageEnergyInput(
                leakage_flow_nm3_per_hr=Decimal("-1"),
                specific_power_kw_per_nm3_per_min=Decimal("6.5"),
                annual_operating_hours=Decimal("8000"),
                electricity_tariff_per_kwh=Decimal("8"),
            )
        )


def test_zero_specific_power_is_rejected() -> None:
    with pytest.raises(
        InvalidLeakageEnergyInputError,
        match="Specific power must be greater than zero",
    ):
        calculate_leakage_energy(
            LeakageEnergyInput(
                leakage_flow_nm3_per_hr=Decimal("600"),
                specific_power_kw_per_nm3_per_min=Decimal("0"),
                annual_operating_hours=Decimal("8000"),
                electricity_tariff_per_kwh=Decimal("8"),
            )
        )


def test_zero_operating_hours_is_rejected() -> None:
    with pytest.raises(
        InvalidLeakageEnergyInputError,
        match="Annual operating hours must be greater than zero",
    ):
        calculate_leakage_energy(
            LeakageEnergyInput(
                leakage_flow_nm3_per_hr=Decimal("600"),
                specific_power_kw_per_nm3_per_min=Decimal("6.5"),
                annual_operating_hours=Decimal("0"),
                electricity_tariff_per_kwh=Decimal("8"),
            )
        )


def test_invalid_repair_fraction_is_rejected() -> None:
    with pytest.raises(
        InvalidLeakageEnergyInputError,
        match="Expected repair fraction must be between zero and one",
    ):
        calculate_leakage_energy(
            LeakageEnergyInput(
                leakage_flow_nm3_per_hr=Decimal("600"),
                specific_power_kw_per_nm3_per_min=Decimal("6.5"),
                annual_operating_hours=Decimal("8000"),
                electricity_tariff_per_kwh=Decimal("8"),
                expected_repair_fraction=Decimal("1.10"),
            )
        )
