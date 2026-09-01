from decimal import Decimal

# Physical input bounds for factory compressed-air systems (India scope).
# Each bound is a gross-error catcher, not design guidance.
#
# MAX_PLANT_AIR_PRESSURE_BAR_G = 25
#   Basis: CAGI Compressed Air & Gas Handbook, 7th Ed. Ch.2 (2018) -
#   single-stage oil-injected rotary screw packages are catalogued at
#   50-250 psig (= 17.2 bar g). KAESER Compressed Air Engineering
#   (P-2010ED, 2023), Tip 4 - systems above 16 bar require a separate
#   high-pressure relief chamber. 25 bar g sits above the highest
#   catalogued plant-air package with margin.
MAX_PLANT_AIR_PRESSURE_BAR_G = Decimal("25")

# Electricity tariff, INR per kWh (India scope).
#   Range set by the operator for Indian industrial supply. The UI offers
#   a dropdown stepped in 0.50 increments (5.00 to 25.00, 41 entries).
#   The list is a UI convenience only - the schema itself accepts any
#   decimal in range so a real
#   fractional tariff is never rejected. There is deliberately no default:
#   the domain layer multiplies cost by this value, so a silent zero would
#   report zero cost rather than a missing input.
MIN_ELECTRICITY_TARIFF_INR_PER_KWH = Decimal("5")
MAX_ELECTRICITY_TARIFF_INR_PER_KWH = Decimal("25")
ELECTRICITY_TARIFF_STEP_INR_PER_KWH = Decimal("0.50")
SELECTABLE_ELECTRICITY_TARIFFS_INR_PER_KWH = tuple(
    (MIN_ELECTRICITY_TARIFF_INR_PER_KWH + step * ELECTRICITY_TARIFF_STEP_INR_PER_KWH).quantize(
        Decimal("0.01")
    )
    for step in range(
        int(
            (MAX_ELECTRICITY_TARIFF_INR_PER_KWH - MIN_ELECTRICITY_TARIFF_INR_PER_KWH)
            / ELECTRICITY_TARIFF_STEP_INR_PER_KWH
        )
        + 1
    )
)
