"""Read-only reference options served to the frontend for dropdowns.

Single source of truth: the lists are built from schemas/_bounds.py and the
domain enums, never typed into the frontend. Adding an option here is a
backend change reviewed against its evidence, not a UI edit.
"""

from decimal import Decimal

from pydantic import BaseModel, Field


class InputOptionsResponse(BaseModel):
    electricity_tariff_inr_per_kwh: list[Decimal] = Field(
        description="Whole-rupee dropdown steps; the schema accepts any decimal in range."
    )
    supply_phase: list[str] = Field(description="IS 12360 phase arrangements.")
    nominal_supply_voltage_v: list[int] = Field(
        description="IS 12360 preferred nominal voltages, volts."
    )
    supply_frequency_hz: list[int] = Field(description="System frequency options, Hz.")
