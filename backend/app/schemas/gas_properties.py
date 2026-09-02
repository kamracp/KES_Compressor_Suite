from decimal import Decimal

from pydantic import BaseModel, Field, model_validator


class GasCompositionItem(BaseModel):
    """One gas component in a compressor gas mixture."""

    component: str = Field(
        min_length=1,
        max_length=50,
    )
    mole_fraction: Decimal = Field(
        ge=0,
        le=1,
    )


class GasPropertiesRequest(BaseModel):
    """Gas composition and absolute operating conditions."""

    components: list[GasCompositionItem] = Field(
        min_length=1,
        max_length=20,
    )

    pressure_bar: Decimal = Field(
        gt=0,
        le=Decimal("800"),
        description=(
            "Process compressor frames are published to 800 bar (MFR-RECIP-FRAME-LIMITS-2026-09)."
        ),
    )
    temperature_k: Decimal = Field(
        ge=Decimal("173"),
        le=Decimal("423"),
        description="-100 to +150 degC; API 618 practice discharge ceiling.",
    )

    @model_validator(mode="after")
    def validate_unique_components(
        self,
    ) -> "GasPropertiesRequest":
        normalized = [item.component.strip().lower() for item in self.components]

        if len(normalized) != len(set(normalized)):
            raise ValueError("Gas components must be unique.")

        return self


class GasPropertiesResponse(BaseModel):
    """Calculated compressor gas properties."""

    molecular_weight_kg_per_kmol: Decimal
    specific_gravity_air_1: Decimal

    pseudocritical_temperature_k: Decimal
    pseudocritical_pressure_bar: Decimal

    reduced_temperature: Decimal
    reduced_pressure: Decimal

    z_factor: Decimal
    z_factor_correlation: str

    density_kg_per_m3: Decimal
