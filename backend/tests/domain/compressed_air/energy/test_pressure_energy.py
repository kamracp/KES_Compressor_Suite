from decimal import Decimal

import pytest

from app.domain.compressed_air.energy.pressure_energy import (
    InvalidPressureEnergyInputError,
    PressureEnergyInput,
    calculate_pressure_energy_saving,
)


def test_pressure_reduction_saves_power_and_energy() -> None:
    result = calculate_pressure_energy_saving(
        PressureEnergyInput(
            current_discharge_pressure_bar_g=Decimal("7.5"),
            optimized_discharge_pressure_bar_g=Decimal("6.8"),
            current_average_power_kw=Decimal("500"),
            annual_operating_hours=Decimal("8000"),
            electricity_tariff_per_kwh=Decimal("8"),
            power_penalty_fraction_per_bar=Decimal("0.07"),
        )
    )

    assert result.pressure_reduction_bar == Decimal("0.7")
    assert result.power_saving_fraction == Decimal("0.049")
    assert result.estimated_power_saving_kw == Decimal("24.500")
    assert result.estimated_optimized_power_kw == Decimal("475.500")

    assert result.annual_energy_saving_kwh == Decimal("196000.000")
    assert result.annual_cost_saving == Decimal("1568000.000")

    assert result.pressure_reduction_is_beneficial is True


def test_no_pressure_reduction_gives_zero_saving() -> None:
    result = calculate_pressure_energy_saving(
        PressureEnergyInput(
            current_discharge_pressure_bar_g=Decimal("7"),
            optimized_discharge_pressure_bar_g=Decimal("7"),
            current_average_power_kw=Decimal("500"),
            annual_operating_hours=Decimal("8000"),
            electricity_tariff_per_kwh=Decimal("8"),
        )
    )

    assert result.pressure_reduction_bar == Decimal("0")
    assert result.power_saving_fraction == Decimal("0")
    assert result.estimated_power_saving_kw == Decimal("0")
    assert result.annual_energy_saving_kwh == Decimal("0")
    assert result.annual_cost_saving == Decimal("0")
    assert result.pressure_reduction_is_beneficial is False


def test_higher_tariff_increases_cost_saving_only() -> None:
    low_tariff = calculate_pressure_energy_saving(
        PressureEnergyInput(
            current_discharge_pressure_bar_g=Decimal("7.5"),
            optimized_discharge_pressure_bar_g=Decimal("6.8"),
            current_average_power_kw=Decimal("500"),
            annual_operating_hours=Decimal("8000"),
            electricity_tariff_per_kwh=Decimal("6"),
        )
    )

    high_tariff = calculate_pressure_energy_saving(
        PressureEnergyInput(
            current_discharge_pressure_bar_g=Decimal("7.5"),
            optimized_discharge_pressure_bar_g=Decimal("6.8"),
            current_average_power_kw=Decimal("500"),
            annual_operating_hours=Decimal("8000"),
            electricity_tariff_per_kwh=Decimal("10"),
        )
    )

    assert low_tariff.estimated_power_saving_kw == high_tariff.estimated_power_saving_kw

    assert low_tariff.annual_energy_saving_kwh == high_tariff.annual_energy_saving_kwh

    assert high_tariff.annual_cost_saving > low_tariff.annual_cost_saving


def test_higher_penalty_factor_increases_saving_estimate() -> None:
    conservative = calculate_pressure_energy_saving(
        PressureEnergyInput(
            current_discharge_pressure_bar_g=Decimal("7.5"),
            optimized_discharge_pressure_bar_g=Decimal("6.5"),
            current_average_power_kw=Decimal("500"),
            annual_operating_hours=Decimal("8000"),
            electricity_tariff_per_kwh=Decimal("8"),
            power_penalty_fraction_per_bar=Decimal("0.05"),
        )
    )

    aggressive = calculate_pressure_energy_saving(
        PressureEnergyInput(
            current_discharge_pressure_bar_g=Decimal("7.5"),
            optimized_discharge_pressure_bar_g=Decimal("6.5"),
            current_average_power_kw=Decimal("500"),
            annual_operating_hours=Decimal("8000"),
            electricity_tariff_per_kwh=Decimal("8"),
            power_penalty_fraction_per_bar=Decimal("0.08"),
        )
    )

    assert aggressive.estimated_power_saving_kw > conservative.estimated_power_saving_kw

    assert aggressive.annual_energy_saving_kwh > conservative.annual_energy_saving_kwh


def test_optimized_pressure_higher_than_current_gives_zero_saving() -> None:
    result = calculate_pressure_energy_saving(
        PressureEnergyInput(
            current_discharge_pressure_bar_g=Decimal("6.5"),
            optimized_discharge_pressure_bar_g=Decimal("7.0"),
            current_average_power_kw=Decimal("500"),
            annual_operating_hours=Decimal("8000"),
            electricity_tariff_per_kwh=Decimal("8"),
        )
    )

    assert result.pressure_reduction_bar == Decimal("-0.5")
    assert result.power_saving_fraction == Decimal("0")
    assert result.estimated_power_saving_kw == Decimal("0")
    assert result.pressure_reduction_is_beneficial is False


def test_zero_average_power_is_rejected() -> None:
    with pytest.raises(
        InvalidPressureEnergyInputError,
        match="Current average power must be greater than zero",
    ):
        calculate_pressure_energy_saving(
            PressureEnergyInput(
                current_discharge_pressure_bar_g=Decimal("7"),
                optimized_discharge_pressure_bar_g=Decimal("6.5"),
                current_average_power_kw=Decimal("0"),
                annual_operating_hours=Decimal("8000"),
                electricity_tariff_per_kwh=Decimal("8"),
            )
        )


def test_zero_operating_hours_is_rejected() -> None:
    with pytest.raises(
        InvalidPressureEnergyInputError,
        match="Annual operating hours must be greater than zero",
    ):
        calculate_pressure_energy_saving(
            PressureEnergyInput(
                current_discharge_pressure_bar_g=Decimal("7"),
                optimized_discharge_pressure_bar_g=Decimal("6.5"),
                current_average_power_kw=Decimal("500"),
                annual_operating_hours=Decimal("0"),
                electricity_tariff_per_kwh=Decimal("8"),
            )
        )


def test_negative_tariff_is_rejected() -> None:
    with pytest.raises(
        InvalidPressureEnergyInputError,
        match="Electricity tariff cannot be negative",
    ):
        calculate_pressure_energy_saving(
            PressureEnergyInput(
                current_discharge_pressure_bar_g=Decimal("7"),
                optimized_discharge_pressure_bar_g=Decimal("6.5"),
                current_average_power_kw=Decimal("500"),
                annual_operating_hours=Decimal("8000"),
                electricity_tariff_per_kwh=Decimal("-1"),
            )
        )


def test_invalid_penalty_fraction_is_rejected() -> None:
    with pytest.raises(
        InvalidPressureEnergyInputError,
        match=("Power penalty fraction per bar must be between zero and one"),
    ):
        calculate_pressure_energy_saving(
            PressureEnergyInput(
                current_discharge_pressure_bar_g=Decimal("7"),
                optimized_discharge_pressure_bar_g=Decimal("6.5"),
                current_average_power_kw=Decimal("500"),
                annual_operating_hours=Decimal("8000"),
                electricity_tariff_per_kwh=Decimal("8"),
                power_penalty_fraction_per_bar=Decimal("1.10"),
            )
        )


def test_default_method_is_adiabatic_isentropic() -> None:
    result = calculate_pressure_energy_saving(
        PressureEnergyInput(
            current_discharge_pressure_bar_g=Decimal("7.0"),
            optimized_discharge_pressure_bar_g=Decimal("6.0"),
            current_average_power_kw=Decimal("100"),
            annual_operating_hours=Decimal("6000"),
            electricity_tariff_per_kwh=Decimal("5"),
        )
    )

    assert result.power_saving_method == "ADIABATIC_ISENTROPIC"
    assert result.power_penalty_fraction_per_bar is None

    # Ideal isentropic work ratio for air (k = 1.4) gives ~8.37% for a
    # 7.0 -> 6.0 bar(g) reduction -- slightly above the 7%/bar rule of
    # thumb, exactly as the physics predicts at this pressure level.
    assert Decimal("0.083") < result.power_saving_fraction < Decimal("0.085")

    assert result.estimated_power_saving_kw == (
        result.power_saving_fraction * Decimal("100")
    )


def test_explicit_penalty_selects_linear_override() -> None:
    result = calculate_pressure_energy_saving(
        PressureEnergyInput(
            current_discharge_pressure_bar_g=Decimal("7.0"),
            optimized_discharge_pressure_bar_g=Decimal("6.0"),
            current_average_power_kw=Decimal("100"),
            annual_operating_hours=Decimal("6000"),
            electricity_tariff_per_kwh=Decimal("5"),
            power_penalty_fraction_per_bar=Decimal("0.07"),
        )
    )

    assert result.power_saving_method == "LINEAR_PER_BAR"
    assert result.power_saving_fraction == Decimal("0.07")


def test_adiabatic_saving_grows_with_deeper_reduction() -> None:
    def fraction_for(target: str) -> Decimal:
        return calculate_pressure_energy_saving(
            PressureEnergyInput(
                current_discharge_pressure_bar_g=Decimal("7.0"),
                optimized_discharge_pressure_bar_g=Decimal(target),
                current_average_power_kw=Decimal("100"),
                annual_operating_hours=Decimal("6000"),
                electricity_tariff_per_kwh=Decimal("5"),
            )
        ).power_saving_fraction

    assert fraction_for("5.0") > fraction_for("6.0") > Decimal("0")


def test_adiabatic_no_saving_when_pressure_not_reduced() -> None:
    result = calculate_pressure_energy_saving(
        PressureEnergyInput(
            current_discharge_pressure_bar_g=Decimal("6.5"),
            optimized_discharge_pressure_bar_g=Decimal("6.5"),
            current_average_power_kw=Decimal("100"),
            annual_operating_hours=Decimal("6000"),
            electricity_tariff_per_kwh=Decimal("5"),
        )
    )

    assert result.power_saving_fraction == Decimal("0")
    assert result.pressure_reduction_is_beneficial is False
