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
