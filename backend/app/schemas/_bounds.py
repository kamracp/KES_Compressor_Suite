from datetime import date
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
# MAX_HIGH_PRESSURE_CIRCUIT_BAR_G = 45
#   Evidence MFR-ATLASCOPCO-AIR-RANGE-2026-09: packaged high-pressure air
#   (DX/DN, PET blowing and boosters) reaches 45 bar g. RESERVED - not yet
#   applied to any field. Plant-air fields stay at MAX_PLANT_AIR_PRESSURE_BAR_G;
#   this ceiling becomes reachable only behind a future high-pressure-circuit
#   flag (CTO decision, 2 Sep 2026).
MAX_HIGH_PRESSURE_CIRCUIT_BAR_G = Decimal("45")

# Electricity tariff, INR per kWh (India scope).
#   Range set by the operator for Indian industrial supply. The UI offers
#   a dropdown stepped in whole-rupee increments (5 to 25, 21 entries).
#   The list is a UI convenience only - the schema itself accepts any
#   decimal in range so a real
#   fractional tariff is never rejected. There is deliberately no default:
#   the domain layer multiplies cost by this value, so a silent zero would
#   report zero cost rather than a missing input.
MIN_ELECTRICITY_TARIFF_INR_PER_KWH = Decimal("5")
MAX_ELECTRICITY_TARIFF_INR_PER_KWH = Decimal("25")
ELECTRICITY_TARIFF_STEP_INR_PER_KWH = Decimal("1")
SELECTABLE_ELECTRICITY_TARIFFS_INR_PER_KWH = tuple(
    (MIN_ELECTRICITY_TARIFF_INR_PER_KWH + step * ELECTRICITY_TARIFF_STEP_INR_PER_KWH).quantize(
        Decimal("1")
    )
    for step in range(
        int(
            (MAX_ELECTRICITY_TARIFF_INR_PER_KWH - MIN_ELECTRICITY_TARIFF_INR_PER_KWH)
            / ELECTRICITY_TARIFF_STEP_INR_PER_KWH
        )
        + 1
    )
)

# Structural integer caps (C-7b item 4). Not engineering bounds - no
# evidence set applies. They turn impossible inputs into a 422 instead of a
# database error or an absurd calculation.
MAX_DB_INTEGER_ID = 2_147_483_647  # PostgreSQL integer primary keys
MAX_CASE_REVISION = 10_000
MAX_LINE_ITEM_QUANTITY = 1_000  # identical machines on one consumer/component line
MAX_TREATMENT_UNIT_COUNT = 100  # units in one treatment train

# Stage counts (C-7b residue, 4 Sep 2026).
#   MFR-RECIP-FRAME-LIMITS-2026-09 SRC-BH-API618: up to 10 cylinders per
#   frame, and a stage needs at least one cylinder.
#   MFR-CENTRIFUGAL-STAGE-LIMITS-2026-09: integrally geared up to 8
#   impellers (Siemens Energy); beam-style single casing <= 10 stages.
MAX_RECIP_STAGES = 10
MAX_CENTRIFUGAL_IMPELLER_STAGES = 10

# Installation year: structural date window, not an engineering bound.
#   Industrial rotary-screw plant air post-dates 1950; one year of headroom
#   above the import-time year covers commissioning entries made ahead of
#   handover and processes that span a New Year without restart.
MIN_INSTALLATION_YEAR = 1950
MAX_INSTALLATION_YEAR = date.today().year + 1

# Part-load power fractions (C-7 sequencing; DOE-CAC-SOURCEBOOK-2003).
#   Load/unload rotary screw: unloaded draw is 15-35 % of full-load power,
#   so the per-machine unload_power_fraction input is bounded to that band
#   rather than assumed. A fully modulated screw at zero flow draws ~70 %
#   (reserved for C-8 part-load modes; not applied to any field yet).
MIN_FIXED_SPEED_UNLOAD_POWER_FRACTION = Decimal("0.15")
MAX_FIXED_SPEED_UNLOAD_POWER_FRACTION = Decimal("0.35")
MODULATION_ZERO_FLOW_POWER_FRACTION = Decimal("0.70")

# VSD turndown (C-7 sequencing). Widest published turndown is 86 %
# (MFR-COMPAIR-OILFREE-SCREW-2026-09, dual-VSD two-stage), so the minimum
# stable flow fraction input cannot be below 0.14.
MIN_VSD_MINIMUM_FLOW_FRACTION = Decimal("0.14")

# Part-load modes (C-8). Guideline ranges are cited constants; machine
# curves stay per-machine inputs bounded here, never assumed.
#   Inlet modulation floor: DOE-CAC-SOURCEBOOK-2003 Fig. 2.6 throttles to
#   40 % capacity then unloads (cited default); ATLASCOPCO-CAM-9ED-2019 says
#   liquid-injected screws can throttle down to 10 %.
MIN_MODULATION_FLOOR_CAPACITY_FRACTION = Decimal("0.10")
MAX_MODULATION_FLOOR_CAPACITY_FRACTION = Decimal("0.40")
DEFAULT_MODULATION_FLOOR_CAPACITY_FRACTION = Decimal("0.40")
#   Variable displacement (turn / spiral / poppet valve): power near
#   proportional over the first 50 % of capacity (DOE-CAC-SOURCEBOOK-2003).
VARIABLE_DISPLACEMENT_FLOOR_CAPACITY_FRACTION = Decimal("0.50")
#   Centrifugal turndown before blow-off / unload: CAGI 30-40 % typical,
#   "35 % or more"; Atlas Copco ZH "over 25 %" (CAGI-CENTRIFUGAL-CAPACITY-
#   CONTROLS, MFR-ATLASCOPCO-AIR-RANGE-2026-09). Power at turndown is machine
#   specific (CAGI); a published example sits at 80 % power for 75 % flow.
MIN_CENTRIFUGAL_TURNDOWN_FRACTION = Decimal("0.10")
MAX_CENTRIFUGAL_TURNDOWN_FRACTION = Decimal("0.45")
MIN_CENTRIFUGAL_POWER_FRACTION_AT_TURNDOWN = Decimal("0.60")
#   Centrifugal auto-dual off-loaded power about 20 % of full load
#   (ATLASCOPCO-CAM-9ED-2019); bounded as a per-machine input.
MIN_CENTRIFUGAL_UNLOAD_POWER_FRACTION = Decimal("0.05")
MAX_CENTRIFUGAL_UNLOAD_POWER_FRACTION = Decimal("0.35")
