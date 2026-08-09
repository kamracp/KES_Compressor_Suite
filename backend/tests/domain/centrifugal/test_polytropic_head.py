from decimal import Decimal

import pytest

from app.domain.centrifugal.centrifugal_models import CentrifugalOperatingPoint
from app.domain.centrifugal.polytropic_head import (
    InvalidPolytropicHeadInputError,
    calculate_polytropic_head,
)


def build_operating_point() -> CentrifugalOperatingPoint:
    return CentrifugalOperatingPoint(
        suction_pressure_bar=Decimal("30"),
        discharge_pressure_bar=Decimal("90"),
        suction_temperature_k=Decimal("308.15"),
        mass_flow_kg_per_s=Decimal("93.376"),
        actual_flow_m3_per_s=Decimal("3.9287"),
        molecular_weight_kg_per_kmol=Decimal("19.075"),
        suction_z_factor=Decimal("0.9398"),
        discharge_z_factor=Decimal("0.8700"),
        isentropic_exponent=Decimal("1.27"),
        polytropic_efficiency=Decimal("0.78"),
    )


def test_calculate_polytropic_head() -> None:
    result = calculate_polytropic_head(build_operating_point())

    assert result.overall_compression_ratio == Decimal("3")
    assert result.average_z_factor == Decimal("0.9049")
    assert result.polytropic_exponent > Decimal("1")
    assert result.polytropic_head_kj_per_kg > Decimal("100")
    assert result.polytropic_head_kj_per_kg < Decimal("250")


def test_zero_suction_pressure_is_rejected() -> None:
    point = build_operating_point()

    point = CentrifugalOperatingPoint(
        suction_pressure_bar=Decimal("0"),
        discharge_pressure_bar=point.discharge_pressure_bar,
        suction_temperature_k=point.suction_temperature_k,
        mass_flow_kg_per_s=point.mass_flow_kg_per_s,
        actual_flow_m3_per_s=point.actual_flow_m3_per_s,
        molecular_weight_kg_per_kmol=point.molecular_weight_kg_per_kmol,
        suction_z_factor=point.suction_z_factor,
        discharge_z_factor=point.discharge_z_factor,
        isentropic_exponent=point.isentropic_exponent,
        polytropic_efficiency=point.polytropic_efficiency,
    )

    with pytest.raises(
        InvalidPolytropicHeadInputError,
        match="Suction absolute pressure must be greater than zero",
    ):
        calculate_polytropic_head(point)


def test_discharge_pressure_must_exceed_suction_pressure() -> None:
    point = build_operating_point()

    point = CentrifugalOperatingPoint(
        suction_pressure_bar=Decimal("30"),
        discharge_pressure_bar=Decimal("30"),
        suction_temperature_k=point.suction_temperature_k,
        mass_flow_kg_per_s=point.mass_flow_kg_per_s,
        actual_flow_m3_per_s=point.actual_flow_m3_per_s,
        molecular_weight_kg_per_kmol=point.molecular_weight_kg_per_kmol,
        suction_z_factor=point.suction_z_factor,
        discharge_z_factor=point.discharge_z_factor,
        isentropic_exponent=point.isentropic_exponent,
        polytropic_efficiency=point.polytropic_efficiency,
    )

    with pytest.raises(
        InvalidPolytropicHeadInputError,
        match="Discharge pressure must be greater than suction pressure",
    ):
        calculate_polytropic_head(point)


def test_zero_suction_temperature_is_rejected() -> None:
    point = build_operating_point()

    point = CentrifugalOperatingPoint(
        suction_pressure_bar=point.suction_pressure_bar,
        discharge_pressure_bar=point.discharge_pressure_bar,
        suction_temperature_k=Decimal("0"),
        mass_flow_kg_per_s=point.mass_flow_kg_per_s,
        actual_flow_m3_per_s=point.actual_flow_m3_per_s,
        molecular_weight_kg_per_kmol=point.molecular_weight_kg_per_kmol,
        suction_z_factor=point.suction_z_factor,
        discharge_z_factor=point.discharge_z_factor,
        isentropic_exponent=point.isentropic_exponent,
        polytropic_efficiency=point.polytropic_efficiency,
    )

    with pytest.raises(
        InvalidPolytropicHeadInputError,
        match="Suction absolute temperature must be greater than zero",
    ):
        calculate_polytropic_head(point)


def test_zero_molecular_weight_is_rejected() -> None:
    point = build_operating_point()

    point = CentrifugalOperatingPoint(
        suction_pressure_bar=point.suction_pressure_bar,
        discharge_pressure_bar=point.discharge_pressure_bar,
        suction_temperature_k=point.suction_temperature_k,
        mass_flow_kg_per_s=point.mass_flow_kg_per_s,
        actual_flow_m3_per_s=point.actual_flow_m3_per_s,
        molecular_weight_kg_per_kmol=Decimal("0"),
        suction_z_factor=point.suction_z_factor,
        discharge_z_factor=point.discharge_z_factor,
        isentropic_exponent=point.isentropic_exponent,
        polytropic_efficiency=point.polytropic_efficiency,
    )

    with pytest.raises(
        InvalidPolytropicHeadInputError,
        match="Molecular weight must be greater than zero",
    ):
        calculate_polytropic_head(point)


def test_zero_suction_z_factor_is_rejected() -> None:
    point = build_operating_point()

    point = CentrifugalOperatingPoint(
        suction_pressure_bar=point.suction_pressure_bar,
        discharge_pressure_bar=point.discharge_pressure_bar,
        suction_temperature_k=point.suction_temperature_k,
        mass_flow_kg_per_s=point.mass_flow_kg_per_s,
        actual_flow_m3_per_s=point.actual_flow_m3_per_s,
        molecular_weight_kg_per_kmol=point.molecular_weight_kg_per_kmol,
        suction_z_factor=Decimal("0"),
        discharge_z_factor=point.discharge_z_factor,
        isentropic_exponent=point.isentropic_exponent,
        polytropic_efficiency=point.polytropic_efficiency,
    )

    with pytest.raises(
        InvalidPolytropicHeadInputError,
        match="Suction Z-factor must be greater than zero",
    ):
        calculate_polytropic_head(point)


def test_zero_discharge_z_factor_is_rejected() -> None:
    point = build_operating_point()

    point = CentrifugalOperatingPoint(
        suction_pressure_bar=point.suction_pressure_bar,
        discharge_pressure_bar=point.discharge_pressure_bar,
        suction_temperature_k=point.suction_temperature_k,
        mass_flow_kg_per_s=point.mass_flow_kg_per_s,
        actual_flow_m3_per_s=point.actual_flow_m3_per_s,
        molecular_weight_kg_per_kmol=point.molecular_weight_kg_per_kmol,
        suction_z_factor=point.suction_z_factor,
        discharge_z_factor=Decimal("0"),
        isentropic_exponent=point.isentropic_exponent,
        polytropic_efficiency=point.polytropic_efficiency,
    )

    with pytest.raises(
        InvalidPolytropicHeadInputError,
        match="Discharge Z-factor must be greater than zero",
    ):
        calculate_polytropic_head(point)


def test_invalid_isentropic_exponent_is_rejected() -> None:
    point = build_operating_point()

    point = CentrifugalOperatingPoint(
        suction_pressure_bar=point.suction_pressure_bar,
        discharge_pressure_bar=point.discharge_pressure_bar,
        suction_temperature_k=point.suction_temperature_k,
        mass_flow_kg_per_s=point.mass_flow_kg_per_s,
        actual_flow_m3_per_s=point.actual_flow_m3_per_s,
        molecular_weight_kg_per_kmol=point.molecular_weight_kg_per_kmol,
        suction_z_factor=point.suction_z_factor,
        discharge_z_factor=point.discharge_z_factor,
        isentropic_exponent=Decimal("1"),
        polytropic_efficiency=point.polytropic_efficiency,
    )

    with pytest.raises(
        InvalidPolytropicHeadInputError,
        match="Isentropic exponent must be greater than one",
    ):
        calculate_polytropic_head(point)


def test_invalid_polytropic_efficiency_is_rejected() -> None:
    point = build_operating_point()

    point = CentrifugalOperatingPoint(
        suction_pressure_bar=point.suction_pressure_bar,
        discharge_pressure_bar=point.discharge_pressure_bar,
        suction_temperature_k=point.suction_temperature_k,
        mass_flow_kg_per_s=point.mass_flow_kg_per_s,
        actual_flow_m3_per_s=point.actual_flow_m3_per_s,
        molecular_weight_kg_per_kmol=point.molecular_weight_kg_per_kmol,
        suction_z_factor=point.suction_z_factor,
        discharge_z_factor=point.discharge_z_factor,
        isentropic_exponent=point.isentropic_exponent,
        polytropic_efficiency=Decimal("0"),
    )

    with pytest.raises(
        InvalidPolytropicHeadInputError,
        match="Polytropic efficiency must be greater than zero and not exceed one",
    ):
        calculate_polytropic_head(point)
