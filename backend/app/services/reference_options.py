from app.domain.compressed_air.energy_basis import supply_basis_options
from app.schemas._bounds import SELECTABLE_ELECTRICITY_TARIFFS_INR_PER_KWH
from app.schemas.reference_options import InputOptionsResponse


def input_options() -> InputOptionsResponse:
    """Assemble every frontend dropdown list from its backend source of truth."""
    supply = supply_basis_options()
    return InputOptionsResponse(
        electricity_tariff_inr_per_kwh=list(SELECTABLE_ELECTRICITY_TARIFFS_INR_PER_KWH),
        supply_phase=supply["supply_phase"],
        nominal_supply_voltage_v=supply["nominal_supply_voltage_v"],
        supply_frequency_hz=supply["supply_frequency_hz"],
    )
