from decimal import Decimal

from app.domain.gas.density import calculate_real_gas_density
from app.domain.gas.gas_catalog import get_gas_component
from app.domain.gas.gas_models import GasComponent, GasMixture
from app.domain.gas.gas_properties import calculate_mixture_properties
from app.domain.gas.pseudocritical import (
    calculate_pseudocritical_properties,
)
from app.domain.gas.reduced_properties import (
    calculate_reduced_properties,
)
from app.domain.gas.z_factor import calculate_papay_z_factor
from app.schemas.gas_properties import (
    GasPropertiesRequest,
    GasPropertiesResponse,
)


class GasPropertiesService:
    """Application service for compressor gas-property calculations."""

    def calculate(
        self,
        request: GasPropertiesRequest,
    ) -> GasPropertiesResponse:
        components: list[GasComponent] = []

        for item in request.components:
            reference = get_gas_component(item.component)

            components.append(
                GasComponent(
                    name=item.component.strip().lower(),
                    formula=reference.formula,
                    molecular_weight=reference.molecular_weight,
                    mole_fraction=Decimal(item.mole_fraction),
                )
            )

        mixture = GasMixture(
            components=tuple(components),
        )

        mixture_properties = calculate_mixture_properties(
            mixture,
        )

        pseudocritical = calculate_pseudocritical_properties(
            mixture,
        )

        reduced = calculate_reduced_properties(
            pressure_bar=request.pressure_bar,
            temperature_k=request.temperature_k,
            pseudocritical=pseudocritical,
        )

        z_factor_result = calculate_papay_z_factor(
            reduced,
        )

        density_result = calculate_real_gas_density(
            pressure_bar=request.pressure_bar,
            temperature_k=request.temperature_k,
            molecular_weight_kg_per_kmol=(mixture_properties.molecular_weight),
            z_factor=z_factor_result.z_factor,
        )

        return GasPropertiesResponse(
            molecular_weight_kg_per_kmol=(mixture_properties.molecular_weight),
            specific_gravity_air_1=(mixture_properties.specific_gravity),
            pseudocritical_temperature_k=(pseudocritical.temperature_k),
            pseudocritical_pressure_bar=(pseudocritical.pressure_bar),
            reduced_temperature=reduced.reduced_temperature,
            reduced_pressure=reduced.reduced_pressure,
            z_factor=z_factor_result.z_factor,
            z_factor_correlation=z_factor_result.correlation,
            density_kg_per_m3=density_result.density_kg_per_m3,
        )


gas_properties_service = GasPropertiesService()
