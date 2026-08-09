from decimal import Decimal

import pytest

from app.domain.compressed_air.equipment.equipment_models import (
    CompressorCatalogModel,
    CompressorPerformancePoint,
    EquipmentDataSourceType,
    EquipmentDataVerificationStatus,
    EquipmentReference,
)
from app.domain.compressed_air.equipment.performance_catalog import (
    InvalidEquipmentCatalogError,
    build_equipment_catalog,
    get_model,
    get_models_by_source,
    get_verified_models,
    validate_equipment_catalog,
)
from app.domain.compressed_air.station.station_models import (
    CompressorControlMode,
    CompressorTechnology,
)


def build_reference(
    *,
    source_name: str = "SOURCE-A",
    verification_status: EquipmentDataVerificationStatus = (
        EquipmentDataVerificationStatus.SOURCE_VERIFIED
    ),
) -> EquipmentReference:
    return EquipmentReference(
        source_name=source_name,
        source_type=EquipmentDataSourceType.DATASHEET,
        document_title="Technical Data Sheet",
        document_reference="DOC-001",
        verification_status=verification_status,
    )


def build_model(
    *,
    source_name: str,
    model_code: str,
    fad: str = "3000",
    pressure: str = "7.5",
    power: str = "400",
    reference: EquipmentReference | None = None,
) -> CompressorCatalogModel:
    return CompressorCatalogModel(
        source_name=source_name,
        model_code=model_code,
        technology=CompressorTechnology.ROTARY_SCREW_OIL_INJECTED,
        control_mode=CompressorControlMode.VSD,
        rated_fad_nm3_per_hr=Decimal(fad),
        rated_discharge_pressure_bar_g=Decimal(pressure),
        rated_motor_power_kw=Decimal(power),
        minimum_fad_nm3_per_hr=Decimal("900"),
        maximum_fad_nm3_per_hr=Decimal("3200"),
        minimum_operating_pressure_bar_g=Decimal("5"),
        maximum_operating_pressure_bar_g=Decimal("8"),
        reference=reference,
    )


def test_build_equipment_catalog() -> None:
    models = (
        build_model(
            source_name="SOURCE-A",
            model_code="EQ-100",
            reference=build_reference(source_name="SOURCE-A"),
        ),
        build_model(
            source_name="SOURCE-B",
            model_code="EQ-200",
            reference=build_reference(source_name="SOURCE-B"),
        ),
    )

    catalog = build_equipment_catalog(models)

    assert catalog.total_models == 2
    assert catalog.sources == ("SOURCE-A", "SOURCE-B")


def test_duplicate_model_key_is_detected() -> None:
    models = (
        build_model(
            source_name="SOURCE-A",
            model_code="EQ-100",
        ),
        build_model(
            source_name="source-a",
            model_code="eq-100",
        ),
    )

    result = validate_equipment_catalog(
        models=models,
    )

    assert result.duplicate_model_keys == ("source-a::eq-100",)
    assert result.catalog_is_valid is False


def test_model_without_reference_is_reported() -> None:
    models = (
        build_model(
            source_name="SOURCE-A",
            model_code="EQ-100",
            reference=None,
        ),
    )

    result = validate_equipment_catalog(
        models=models,
    )

    assert result.models_without_reference == ("source-a::eq-100",)
    assert result.unverified_model_keys == ("source-a::eq-100",)


def test_unverified_reference_is_reported() -> None:
    models = (
        build_model(
            source_name="SOURCE-A",
            model_code="EQ-100",
            reference=build_reference(
                source_name="SOURCE-A",
                verification_status=(EquipmentDataVerificationStatus.UNVERIFIED),
            ),
        ),
    )

    result = validate_equipment_catalog(
        models=models,
    )

    assert result.unverified_model_keys == ("source-a::eq-100",)


def test_verified_models_are_filtered() -> None:
    verified = build_model(
        source_name="SOURCE-A",
        model_code="EQ-100",
        reference=build_reference(
            source_name="SOURCE-A",
            verification_status=(EquipmentDataVerificationStatus.SOURCE_VERIFIED),
        ),
    )

    unverified = build_model(
        source_name="SOURCE-B",
        model_code="EQ-200",
        reference=build_reference(
            source_name="SOURCE-B",
            verification_status=(EquipmentDataVerificationStatus.UNVERIFIED),
        ),
    )

    catalog = build_equipment_catalog(
        (
            verified,
            unverified,
        )
    )

    results = get_verified_models(catalog)

    assert len(results) == 1
    assert results[0].model_code == "EQ-100"


def test_get_models_by_source_is_case_insensitive() -> None:
    catalog = build_equipment_catalog(
        (
            build_model(
                source_name="SOURCE-A",
                model_code="EQ-100",
            ),
            build_model(
                source_name="SOURCE-B",
                model_code="EQ-200",
            ),
        )
    )

    results = get_models_by_source(
        catalog,
        "source-a",
    )

    assert len(results) == 1
    assert results[0].model_code == "EQ-100"


def test_get_model_returns_exact_source_and_model() -> None:
    catalog = build_equipment_catalog(
        (
            build_model(
                source_name="SOURCE-A",
                model_code="EQ-100",
            ),
        )
    )

    result = get_model(
        catalog,
        source_name="source-a",
        model_code="eq-100",
    )

    assert result is not None
    assert result.model_code == "EQ-100"


def test_orphan_performance_point_is_detected() -> None:
    models = (
        build_model(
            source_name="SOURCE-A",
            model_code="EQ-100",
        ),
    )

    points = (
        CompressorPerformancePoint(
            source_name="SOURCE-X",
            model_code="EQ-X",
            discharge_pressure_bar_g=Decimal("7"),
            fad_nm3_per_hr=Decimal("2000"),
            shaft_or_input_power_kw=Decimal("300"),
            specific_power_kw_per_nm3_per_min=Decimal("9"),
        ),
    )

    result = validate_equipment_catalog(
        models=models,
        performance_points=points,
    )

    assert result.orphan_performance_points == ("source-x::eq-x",)
    assert result.catalog_is_valid is False


def test_invalid_rated_fad_is_rejected() -> None:
    model = build_model(
        source_name="SOURCE-A",
        model_code="EQ-100",
        fad="0",
    )

    with pytest.raises(
        InvalidEquipmentCatalogError,
        match="Rated FAD must be greater than zero",
    ):
        build_equipment_catalog((model,))


def test_minimum_fad_cannot_exceed_maximum_fad() -> None:
    model = CompressorCatalogModel(
        source_name="SOURCE-A",
        model_code="EQ-100",
        technology=CompressorTechnology.ROTARY_SCREW_OIL_INJECTED,
        control_mode=CompressorControlMode.VSD,
        rated_fad_nm3_per_hr=Decimal("3000"),
        rated_discharge_pressure_bar_g=Decimal("7"),
        rated_motor_power_kw=Decimal("400"),
        minimum_fad_nm3_per_hr=Decimal("3500"),
        maximum_fad_nm3_per_hr=Decimal("3200"),
    )

    with pytest.raises(
        InvalidEquipmentCatalogError,
        match="Minimum FAD cannot exceed maximum FAD",
    ):
        build_equipment_catalog((model,))
