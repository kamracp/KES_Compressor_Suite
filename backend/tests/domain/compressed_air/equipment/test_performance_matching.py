from decimal import Decimal

import pytest

from app.domain.compressed_air.equipment.equipment_models import (
    CompressorCatalogModel,
    EquipmentCatalog,
)
from app.domain.compressed_air.equipment.performance_matching import (
    EquipmentMatchingInput,
    EquipmentMatchStatus,
    get_suitable_equipment,
    match_equipment,
)
from app.domain.compressed_air.station.station_models import (
    CompressorControlMode,
    CompressorTechnology,
)


def build_model(
    *,
    model_code: str,
    fad: str,
    pressure: str,
    power: str,
    technology: CompressorTechnology = (CompressorTechnology.ROTARY_SCREW_OIL_INJECTED),
    control_mode: CompressorControlMode = CompressorControlMode.VSD,
) -> CompressorCatalogModel:
    return CompressorCatalogModel(
        source_name="GENERIC-SOURCE",
        model_code=model_code,
        technology=technology,
        control_mode=control_mode,
        rated_fad_nm3_per_hr=Decimal(fad),
        rated_discharge_pressure_bar_g=Decimal(pressure),
        rated_motor_power_kw=Decimal(power),
    )


def build_catalog() -> EquipmentCatalog:
    models = (
        build_model(
            model_code="EQ-A",
            fad="3300",
            pressure="7.5",
            power="420",
        ),
        build_model(
            model_code="EQ-B",
            fad="3600",
            pressure="8.0",
            power="450",
        ),
        build_model(
            model_code="EQ-C",
            fad="2800",
            pressure="7.5",
            power="400",
        ),
        build_model(
            model_code="EQ-D",
            fad="3500",
            pressure="6.5",
            power="430",
        ),
    )

    return EquipmentCatalog(
        models=models,
        total_models=len(models),
        sources=("GENERIC-SOURCE",),
    )


def test_suitable_equipment_is_identified() -> None:
    results = match_equipment(
        catalog=build_catalog(),
        requirements=EquipmentMatchingInput(
            required_fad_nm3_per_hr=Decimal("3000"),
            required_discharge_pressure_bar_g=Decimal("7"),
            minimum_capacity_margin_fraction=Decimal("0.10"),
        ),
    )

    result = next(item for item in results if item.model_code == "EQ-A")

    assert result.status == EquipmentMatchStatus.SUITABLE
    assert result.capacity_margin_nm3_per_hr == Decimal("300")
    assert result.capacity_margin_fraction == Decimal("0.10")
    assert result.pressure_margin_bar == Decimal("0.5")


def test_insufficient_capacity_is_detected() -> None:
    results = match_equipment(
        catalog=build_catalog(),
        requirements=EquipmentMatchingInput(
            required_fad_nm3_per_hr=Decimal("3000"),
            required_discharge_pressure_bar_g=Decimal("7"),
        ),
    )

    result = next(item for item in results if item.model_code == "EQ-C")

    assert result.status == EquipmentMatchStatus.CAPACITY_INSUFFICIENT
    assert result.capacity_margin_nm3_per_hr == Decimal("-200")


def test_insufficient_pressure_is_detected() -> None:
    results = match_equipment(
        catalog=build_catalog(),
        requirements=EquipmentMatchingInput(
            required_fad_nm3_per_hr=Decimal("3000"),
            required_discharge_pressure_bar_g=Decimal("7"),
        ),
    )

    result = next(item for item in results if item.model_code == "EQ-D")

    assert result.status == EquipmentMatchStatus.PRESSURE_INSUFFICIENT
    assert result.pressure_margin_bar == Decimal("-0.5")


def test_low_capacity_margin_is_detected() -> None:
    catalog = EquipmentCatalog(
        models=(
            build_model(
                model_code="EQ-LOW-MARGIN",
                fad="3150",
                pressure="7.5",
                power="410",
            ),
        ),
        total_models=1,
        sources=("GENERIC-SOURCE",),
    )

    result = match_equipment(
        catalog=catalog,
        requirements=EquipmentMatchingInput(
            required_fad_nm3_per_hr=Decimal("3000"),
            required_discharge_pressure_bar_g=Decimal("7"),
            minimum_capacity_margin_fraction=Decimal("0.10"),
        ),
    )[0]

    assert result.status == EquipmentMatchStatus.MARGIN_LOW
    assert result.capacity_margin_fraction == Decimal("0.05")


def test_technology_mismatch_is_detected() -> None:
    catalog = EquipmentCatalog(
        models=(
            build_model(
                model_code="EQ-RECIP",
                fad="3500",
                pressure="8",
                power="450",
                technology=CompressorTechnology.RECIPROCATING,
            ),
        ),
        total_models=1,
        sources=("GENERIC-SOURCE",),
    )

    result = match_equipment(
        catalog=catalog,
        requirements=EquipmentMatchingInput(
            required_fad_nm3_per_hr=Decimal("3000"),
            required_discharge_pressure_bar_g=Decimal("7"),
            preferred_technology=(CompressorTechnology.ROTARY_SCREW_OIL_INJECTED),
        ),
    )[0]

    assert result.status == EquipmentMatchStatus.TECHNOLOGY_MISMATCH
    assert result.technology_preference_met is False


def test_control_preference_affects_score_but_not_primary_suitability() -> None:
    catalog = EquipmentCatalog(
        models=(
            build_model(
                model_code="EQ-FIXED",
                fad="3500",
                pressure="8",
                power="440",
                control_mode=CompressorControlMode.FIXED_SPEED,
            ),
        ),
        total_models=1,
        sources=("GENERIC-SOURCE",),
    )

    result = match_equipment(
        catalog=catalog,
        requirements=EquipmentMatchingInput(
            required_fad_nm3_per_hr=Decimal("3000"),
            required_discharge_pressure_bar_g=Decimal("7"),
            preferred_control_mode=CompressorControlMode.VSD,
        ),
    )[0]

    assert result.status == EquipmentMatchStatus.SUITABLE
    assert result.control_preference_met is False
    assert "Preferred control mode is not satisfied." in result.reasons


def test_results_are_ranked_by_engineering_score() -> None:
    results = match_equipment(
        catalog=build_catalog(),
        requirements=EquipmentMatchingInput(
            required_fad_nm3_per_hr=Decimal("3000"),
            required_discharge_pressure_bar_g=Decimal("7"),
            minimum_capacity_margin_fraction=Decimal("0.10"),
        ),
    )

    scores = [item.engineering_score for item in results]

    assert scores == sorted(
        scores,
        reverse=True,
    )


def test_suitable_equipment_filter_returns_only_suitable_options() -> None:
    results = get_suitable_equipment(
        catalog=build_catalog(),
        requirements=EquipmentMatchingInput(
            required_fad_nm3_per_hr=Decimal("3000"),
            required_discharge_pressure_bar_g=Decimal("7"),
            minimum_capacity_margin_fraction=Decimal("0.10"),
        ),
    )

    assert results

    assert all(item.status == EquipmentMatchStatus.SUITABLE for item in results)


def test_zero_required_fad_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="Required FAD must be greater than zero",
    ):
        match_equipment(
            catalog=build_catalog(),
            requirements=EquipmentMatchingInput(
                required_fad_nm3_per_hr=Decimal("0"),
                required_discharge_pressure_bar_g=Decimal("7"),
            ),
        )


def test_negative_required_pressure_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="Required discharge pressure cannot be negative",
    ):
        match_equipment(
            catalog=build_catalog(),
            requirements=EquipmentMatchingInput(
                required_fad_nm3_per_hr=Decimal("3000"),
                required_discharge_pressure_bar_g=Decimal("-1"),
            ),
        )


def test_invalid_capacity_margin_fraction_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="Minimum capacity margin fraction must be between zero and one",
    ):
        match_equipment(
            catalog=build_catalog(),
            requirements=EquipmentMatchingInput(
                required_fad_nm3_per_hr=Decimal("3000"),
                required_discharge_pressure_bar_g=Decimal("7"),
                minimum_capacity_margin_fraction=Decimal("1"),
            ),
        )
