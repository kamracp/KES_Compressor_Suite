from dataclasses import dataclass
from decimal import Decimal

from app.domain.compressed_air.equipment.equipment_models import (
    CompressorCatalogModel,
    CompressorPerformancePoint,
    EquipmentCatalog,
    EquipmentDataVerificationStatus,
)


class InvalidEquipmentCatalogError(ValueError):
    """Raised when source_name catalog data is invalid."""


@dataclass(frozen=True, slots=True)
class EquipmentCatalogValidationResult:
    """Validation summary for vendor-neutral compressor equipment catalog data."""

    total_models: int
    total_performance_points: int

    duplicate_model_keys: tuple[str, ...]

    models_without_reference: tuple[str, ...]
    unverified_model_keys: tuple[str, ...]

    orphan_performance_points: tuple[str, ...]

    catalog_is_valid: bool


def build_equipment_catalog(
    models: tuple[CompressorCatalogModel, ...],
) -> EquipmentCatalog:
    """Build a vendor-neutral source_name catalog."""

    _validate_models(models)

    sources = tuple(sorted({model.source_name.strip() for model in models}))

    return EquipmentCatalog(
        models=models,
        total_models=len(models),
        sources=sources,
    )


def validate_equipment_catalog(
    *,
    models: tuple[CompressorCatalogModel, ...],
    performance_points: tuple[CompressorPerformancePoint, ...] = (),
) -> EquipmentCatalogValidationResult:
    """Validate compressor catalog models and performance points."""

    _validate_models(models)

    model_keys = tuple(
        _model_key(
            source_name=model.source_name,
            model_code=model.model_code,
        )
        for model in models
    )

    duplicate_model_keys = tuple(sorted({key for key in model_keys if model_keys.count(key) > 1}))

    models_without_reference = tuple(
        sorted(
            _model_key(
                source_name=model.source_name,
                model_code=model.model_code,
            )
            for model in models
            if model.reference is None
        )
    )

    unverified_model_keys = tuple(
        sorted(
            _model_key(
                source_name=model.source_name,
                model_code=model.model_code,
            )
            for model in models
            if (
                model.reference is None
                or model.reference.verification_status == EquipmentDataVerificationStatus.UNVERIFIED
            )
        )
    )

    model_key_set = set(model_keys)

    orphan_performance_points = tuple(
        sorted(
            {
                _model_key(
                    source_name=point.source_name,
                    model_code=point.model_code,
                )
                for point in performance_points
                if _model_key(
                    source_name=point.source_name,
                    model_code=point.model_code,
                )
                not in model_key_set
            }
        )
    )

    for point in performance_points:
        _validate_performance_point(point)

    catalog_is_valid = not duplicate_model_keys and not orphan_performance_points

    return EquipmentCatalogValidationResult(
        total_models=len(models),
        total_performance_points=len(performance_points),
        duplicate_model_keys=duplicate_model_keys,
        models_without_reference=models_without_reference,
        unverified_model_keys=unverified_model_keys,
        orphan_performance_points=orphan_performance_points,
        catalog_is_valid=catalog_is_valid,
    )


def get_models_by_source(
    catalog: EquipmentCatalog,
    source_name: str,
) -> tuple[CompressorCatalogModel, ...]:
    """Return catalog models for one source_name."""

    normalized = source_name.strip().casefold()

    return tuple(
        model for model in catalog.models if model.source_name.strip().casefold() == normalized
    )


def get_model(
    catalog: EquipmentCatalog,
    *,
    source_name: str,
    model_code: str,
) -> CompressorCatalogModel | None:
    """Return one exact source_name/model combination."""

    target_key = _model_key(
        source_name=source_name,
        model_code=model_code,
    )

    for model in catalog.models:
        if (
            _model_key(
                source_name=model.source_name,
                model_code=model.model_code,
            )
            == target_key
        ):
            return model

    return None


def get_verified_models(
    catalog: EquipmentCatalog,
) -> tuple[CompressorCatalogModel, ...]:
    """Return models backed by verified source_name references."""

    return tuple(
        model
        for model in catalog.models
        if (
            model.reference is not None
            and model.reference.verification_status
            in {
                EquipmentDataVerificationStatus.SOURCE_VERIFIED,
                EquipmentDataVerificationStatus.ENGINEERING_VERIFIED,
                EquipmentDataVerificationStatus.APPROVED,
            }
        )
    )


def _validate_models(
    models: tuple[CompressorCatalogModel, ...],
) -> None:
    for model in models:
        if not model.source_name.strip():
            raise InvalidEquipmentCatalogError("Equipment name cannot be empty.")

        if not model.model_code.strip():
            raise InvalidEquipmentCatalogError("Model code cannot be empty.")

        if model.rated_fad_nm3_per_hr <= 0:
            raise InvalidEquipmentCatalogError("Rated FAD must be greater than zero.")

        if model.rated_discharge_pressure_bar_g < 0:
            raise InvalidEquipmentCatalogError("Rated discharge pressure cannot be negative.")

        if model.rated_motor_power_kw <= 0:
            raise InvalidEquipmentCatalogError("Rated motor power must be greater than zero.")

        if model.minimum_fad_nm3_per_hr is not None and model.minimum_fad_nm3_per_hr < 0:
            raise InvalidEquipmentCatalogError("Minimum FAD cannot be negative.")

        if model.maximum_fad_nm3_per_hr is not None and model.maximum_fad_nm3_per_hr <= 0:
            raise InvalidEquipmentCatalogError("Maximum FAD must be greater than zero.")

        if (
            model.minimum_fad_nm3_per_hr is not None
            and model.maximum_fad_nm3_per_hr is not None
            and model.minimum_fad_nm3_per_hr > model.maximum_fad_nm3_per_hr
        ):
            raise InvalidEquipmentCatalogError("Minimum FAD cannot exceed maximum FAD.")

        if (
            model.minimum_operating_pressure_bar_g is not None
            and model.minimum_operating_pressure_bar_g < 0
        ):
            raise InvalidEquipmentCatalogError("Minimum operating pressure cannot be negative.")

        if (
            model.maximum_operating_pressure_bar_g is not None
            and model.maximum_operating_pressure_bar_g < 0
        ):
            raise InvalidEquipmentCatalogError("Maximum operating pressure cannot be negative.")

        if (
            model.minimum_operating_pressure_bar_g is not None
            and model.maximum_operating_pressure_bar_g is not None
            and model.minimum_operating_pressure_bar_g > model.maximum_operating_pressure_bar_g
        ):
            raise InvalidEquipmentCatalogError(
                "Minimum operating pressure cannot exceed maximum operating pressure."
            )


def _validate_performance_point(
    point: CompressorPerformancePoint,
) -> None:
    if not point.source_name.strip():
        raise InvalidEquipmentCatalogError("Performance-point source_name cannot be empty.")

    if not point.model_code.strip():
        raise InvalidEquipmentCatalogError("Performance-point model code cannot be empty.")

    if point.discharge_pressure_bar_g < 0:
        raise InvalidEquipmentCatalogError(
            "Performance-point discharge pressure cannot be negative."
        )

    if point.fad_nm3_per_hr <= 0:
        raise InvalidEquipmentCatalogError("Performance-point FAD must be greater than zero.")

    if point.shaft_or_input_power_kw <= 0:
        raise InvalidEquipmentCatalogError("Performance-point power must be greater than zero.")

    if point.specific_power_kw_per_nm3_per_min <= 0:
        raise InvalidEquipmentCatalogError(
            "Performance-point specific power must be greater than zero."
        )

    if point.relative_humidity_fraction is not None and (
        point.relative_humidity_fraction < 0 or point.relative_humidity_fraction > 1
    ):
        raise InvalidEquipmentCatalogError(
            "Relative humidity fraction must be between zero and one."
        )

    if point.speed_fraction is not None and (point.speed_fraction < 0 or point.speed_fraction > 1):
        raise InvalidEquipmentCatalogError("Speed fraction must be between zero and one.")

    if point.load_fraction is not None and (point.load_fraction < 0 or point.load_fraction > 1):
        raise InvalidEquipmentCatalogError("Load fraction must be between zero and one.")


def _model_key(
    *,
    source_name: str,
    model_code: str,
) -> str:
    return source_name.strip().casefold() + "::" + model_code.strip().casefold()
