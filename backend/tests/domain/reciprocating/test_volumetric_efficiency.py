from decimal import Decimal

import pytest

from app.domain.reciprocating.volumetric_efficiency import (
    InvalidVolumetricEfficiencyInputError,
    calculate_volumetric_efficiency,
)


def test_calculate_volumetric_efficiency() -> None:
    result = calculate_volumetric_efficiency(
        clearance_fraction=Decimal("0.10"),
        stage_compression_ratio=Decimal("1.442"),
        suction_z_factor=Decimal("0.9398"),
        discharge_z_factor=Decimal("0.8700"),
        isentropic_exponent=Decimal("1.27"),
        displacement_m3_per_hr=Decimal("1980.333"),
    )

    assert result.volumetric_efficiency > Decimal("0.95")
    assert result.volumetric_efficiency < Decimal("0.98")
    assert result.delivered_flow_m3_per_hr > Decimal("1900")
    assert result.delivered_flow_m3_per_hr < Decimal("1920")


def test_zero_clearance_is_allowed() -> None:
    result = calculate_volumetric_efficiency(
        clearance_fraction=Decimal("0"),
        stage_compression_ratio=Decimal("1.5"),
        suction_z_factor=Decimal("1"),
        discharge_z_factor=Decimal("1"),
        isentropic_exponent=Decimal("1.30"),
        displacement_m3_per_hr=Decimal("1000"),
    )

    assert result.volumetric_efficiency == Decimal("1")
    assert result.delivered_flow_m3_per_hr == Decimal("1000")


def test_negative_clearance_is_rejected() -> None:
    with pytest.raises(
        InvalidVolumetricEfficiencyInputError,
        match="Clearance fraction must be greater than or equal to zero and less than one",
    ):
        calculate_volumetric_efficiency(
            clearance_fraction=Decimal("-0.01"),
            stage_compression_ratio=Decimal("1.5"),
            suction_z_factor=Decimal("1"),
            discharge_z_factor=Decimal("1"),
            isentropic_exponent=Decimal("1.30"),
            displacement_m3_per_hr=Decimal("1000"),
        )


def test_clearance_equal_to_one_is_rejected() -> None:
    with pytest.raises(
        InvalidVolumetricEfficiencyInputError,
        match="Clearance fraction must be greater than or equal to zero and less than one",
    ):
        calculate_volumetric_efficiency(
            clearance_fraction=Decimal("1"),
            stage_compression_ratio=Decimal("1.5"),
            suction_z_factor=Decimal("1"),
            discharge_z_factor=Decimal("1"),
            isentropic_exponent=Decimal("1.30"),
            displacement_m3_per_hr=Decimal("1000"),
        )


def test_invalid_stage_compression_ratio_is_rejected() -> None:
    with pytest.raises(
        InvalidVolumetricEfficiencyInputError,
        match="Stage compression ratio must be greater than one",
    ):
        calculate_volumetric_efficiency(
            clearance_fraction=Decimal("0.10"),
            stage_compression_ratio=Decimal("1"),
            suction_z_factor=Decimal("1"),
            discharge_z_factor=Decimal("1"),
            isentropic_exponent=Decimal("1.30"),
            displacement_m3_per_hr=Decimal("1000"),
        )


def test_zero_suction_z_factor_is_rejected() -> None:
    with pytest.raises(
        InvalidVolumetricEfficiencyInputError,
        match="Suction Z-factor must be greater than zero",
    ):
        calculate_volumetric_efficiency(
            clearance_fraction=Decimal("0.10"),
            stage_compression_ratio=Decimal("1.5"),
            suction_z_factor=Decimal("0"),
            discharge_z_factor=Decimal("1"),
            isentropic_exponent=Decimal("1.30"),
            displacement_m3_per_hr=Decimal("1000"),
        )


def test_zero_discharge_z_factor_is_rejected() -> None:
    with pytest.raises(
        InvalidVolumetricEfficiencyInputError,
        match="Discharge Z-factor must be greater than zero",
    ):
        calculate_volumetric_efficiency(
            clearance_fraction=Decimal("0.10"),
            stage_compression_ratio=Decimal("1.5"),
            suction_z_factor=Decimal("1"),
            discharge_z_factor=Decimal("0"),
            isentropic_exponent=Decimal("1.30"),
            displacement_m3_per_hr=Decimal("1000"),
        )


def test_invalid_isentropic_exponent_is_rejected() -> None:
    with pytest.raises(
        InvalidVolumetricEfficiencyInputError,
        match="Isentropic exponent must be greater than one",
    ):
        calculate_volumetric_efficiency(
            clearance_fraction=Decimal("0.10"),
            stage_compression_ratio=Decimal("1.5"),
            suction_z_factor=Decimal("1"),
            discharge_z_factor=Decimal("1"),
            isentropic_exponent=Decimal("1"),
            displacement_m3_per_hr=Decimal("1000"),
        )


def test_zero_displacement_is_rejected() -> None:
    with pytest.raises(
        InvalidVolumetricEfficiencyInputError,
        match="Compressor displacement must be greater than zero",
    ):
        calculate_volumetric_efficiency(
            clearance_fraction=Decimal("0.10"),
            stage_compression_ratio=Decimal("1.5"),
            suction_z_factor=Decimal("1"),
            discharge_z_factor=Decimal("1"),
            isentropic_exponent=Decimal("1.30"),
            displacement_m3_per_hr=Decimal("0"),
        )
