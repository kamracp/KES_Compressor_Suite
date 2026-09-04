from decimal import Decimal

from pydantic import BaseModel, Field

from app.domain.rotary_screw.models import (
    RotaryScrewControlType,
    RotaryScrewOilType,
    RotaryScrewStageCount,
)
from app.schemas._bounds import (
    MAX_CENTRIFUGAL_IMPELLER_STAGES,
    MAX_ELECTRICITY_TARIFF_INR_PER_KWH,
    MAX_RECIP_STAGES,
    MIN_ELECTRICITY_TARIFF_INR_PER_KWH,
)


class GasConditionInput(BaseModel):
    """Gas operating-condition input for compressor calculations."""

    suction_pressure_bar: Decimal = Field(
        gt=0,
        le=Decimal("800"),
        description=(
            "Reciprocating / process compressor frames are published to 800 bar "
            "(MFR-RECIP-FRAME-LIMITS-2026-09)."
        ),
    )
    discharge_pressure_bar: Decimal = Field(
        gt=0,
        le=Decimal("800"),
        description=(
            "Reciprocating / process compressor frames are published to 800 bar "
            "(MFR-RECIP-FRAME-LIMITS-2026-09)."
        ),
    )
    suction_temperature_k: Decimal = Field(
        ge=Decimal("173"),
        le=Decimal("423"),
        description=(
            "-100 to +150 degC; API 618 practice limits lubricated discharge to about 150 degC."
        ),
    )
    mass_flow_kg_per_s: Decimal = Field(gt=0)
    actual_flow_m3_per_s: Decimal = Field(gt=0)

    molecular_weight_kg_per_kmol: Decimal = Field(
        ge=Decimal("2"),
        le=Decimal("150"),
        description="GPSA Section 23 physical constants: hydrogen 2.016 to n-decane 142.3 kg/kmol.",
    )
    suction_z_factor: Decimal = Field(
        ge=Decimal("0.2"),
        le=Decimal("2.0"),
        description="GPSA Section 23 generalized (Standing-Katz) compressibility chart range.",
    )
    discharge_z_factor: Decimal = Field(
        ge=Decimal("0.2"),
        le=Decimal("2.0"),
        description="GPSA Section 23 generalized (Standing-Katz) compressibility chart range.",
    )
    isentropic_exponent: Decimal = Field(gt=1)


class CompressionCalculationRequest(BaseModel):
    """Request payload for common compressor thermodynamic calculations."""

    gas: GasConditionInput

    number_of_stages: int = Field(
        ge=1,
        le=MAX_RECIP_STAGES,
        description=(
            "Largest published API 618 frame carries 10 cylinders and a stage "
            "needs at least one cylinder (MFR-RECIP-FRAME-LIMITS-2026-09 SRC-BH-API618)."
        ),
    )

    specific_heat_cp_kj_per_kg_k: Decimal = Field(
        ge=Decimal("0.5"),
        le=Decimal("15"),
        description="GPSA Section 23: hydrogen 14.3 kJ/kg.K is the upper physical case.",
    )
    isentropic_efficiency: Decimal = Field(gt=0, le=1)
    mechanical_efficiency: Decimal = Field(gt=0, le=1)

    intercooler_outlet_temperature_k: Decimal = Field(
        ge=Decimal("273"),
        le=Decimal("423"),
        description="0 to +150 degC; API 618 practice discharge ceiling.",
    )
    cooling_water_inlet_temperature_k: Decimal = Field(
        ge=Decimal("273"),
        le=Decimal("373"),
        description="Liquid water at near-atmospheric pressure: 0-100 degC.",
    )
    cooling_water_outlet_temperature_k: Decimal = Field(
        ge=Decimal("273"),
        le=Decimal("373"),
        description="Liquid water at near-atmospheric pressure: 0-100 degC.",
    )

    selected_driver_power_kw: Decimal = Field(gt=0)
    driver_service_factor: Decimal = Field(ge=0)
    motor_efficiency: Decimal | None = Field(default=None, gt=0, le=1)


class ReciprocatingCalculationRequest(BaseModel):
    """Request payload for reciprocating compressor sizing."""

    required_flow_m3_per_hr: Decimal = Field(gt=0)

    bore_mm: Decimal = Field(
        gt=0,
        le=Decimal("1250"),
        description=(
            "Largest published API 618 cylinder bore 1250 mm (MFR-RECIP-FRAME-LIMITS-2026-09)."
        ),
    )
    stroke_mm: Decimal = Field(gt=0)
    rod_diameter_mm: Decimal = Field(ge=0)
    speed_rpm: Decimal = Field(
        gt=0,
        le=Decimal("1800"),
        description=(
            "High-speed API 11P frames run to 1800 rpm "
            "(MFR-RECIP-FRAME-LIMITS-2026-09); API 618 sets no numeric limit."
        ),
    )
    clearance_fraction: Decimal = Field(ge=0, lt=1)

    stage_compression_ratio: Decimal = Field(gt=1)
    suction_z_factor: Decimal = Field(
        ge=Decimal("0.2"),
        le=Decimal("2.0"),
        description="GPSA Section 23 generalized (Standing-Katz) compressibility chart range.",
    )
    discharge_z_factor: Decimal = Field(
        ge=Decimal("0.2"),
        le=Decimal("2.0"),
        description="GPSA Section 23 generalized (Standing-Katz) compressibility chart range.",
    )
    isentropic_exponent: Decimal = Field(gt=1)

    suction_pressure_bar: Decimal = Field(
        gt=0,
        le=Decimal("800"),
        description=(
            "Reciprocating / process compressor frames are published to 800 bar "
            "(MFR-RECIP-FRAME-LIMITS-2026-09)."
        ),
    )
    discharge_pressure_bar: Decimal = Field(
        gt=0,
        le=Decimal("800"),
        description=(
            "Reciprocating / process compressor frames are published to 800 bar "
            "(MFR-RECIP-FRAME-LIMITS-2026-09)."
        ),
    )
    allowable_rod_load_kn: Decimal = Field(
        gt=0,
        le=Decimal("2000"),
        description="Largest published frame rod load 1980 kN (MFR-RECIP-FRAME-LIMITS-2026-09).",
    )


class CentrifugalCalculationRequest(BaseModel):
    """Request payload for centrifugal compressor sizing."""

    gas: GasConditionInput

    polytropic_efficiency: Decimal = Field(gt=0, le=1)

    number_of_impeller_stages: int = Field(
        ge=1,
        le=MAX_CENTRIFUGAL_IMPELLER_STAGES,
        description=(
            "Integrally geared machines reach 8 impellers and beam-style single "
            "casings are limited to 10 stages (MFR-CENTRIFUGAL-STAGE-LIMITS-2026-09)."
        ),
    )
    head_coefficient: Decimal = Field(
        gt=0,
        le=Decimal("1.0"),
        description=(
            "Euler work limit: psi = H/U_tip^2 reaches 1.0 only for radial blades with zero slip."
        ),
    )
    rotational_speed_rpm: Decimal = Field(gt=0)

    mechanical_loss_fraction: Decimal = Field(
        ge=0,
        le=Decimal("0.2"),
        description="API 617 driver-to-shaft losses (gear + coupling) are typically 5-8 %.",
    )
    driver_margin_fraction: Decimal = Field(
        ge=0,
        le=Decimal("0.5"),
        description="API 617 para 2.2.2 requires at least 10 % margin over maximum absorbed power.",
    )
    selected_driver_power_kw: Decimal = Field(gt=0)
    motor_efficiency: Decimal | None = Field(default=None, gt=0, le=1)

    surge_flow_fraction: Decimal = Field(default=Decimal("0.70"), gt=0, lt=1)
    anti_surge_margin_fraction: Decimal = Field(
        default=Decimal("0.10"),
        ge=Decimal("0.10"),
        le=Decimal("0.5"),
        description="API 617: continuous operation at least 10 % above predicted surge capacity.",
    )
    stonewall_flow_fraction: Decimal = Field(default=Decimal("1.25"), gt=1)


class CompressorSelectionRequest(BaseModel):
    """Request payload for reciprocating/centrifugal/rotary-screw selection."""

    required_flow_m3_per_hr: Decimal = Field(gt=0)
    suction_pressure_bar: Decimal = Field(
        gt=0,
        le=Decimal("800"),
        description=(
            "Reciprocating / process compressor frames are published to 800 bar "
            "(MFR-RECIP-FRAME-LIMITS-2026-09)."
        ),
    )
    discharge_pressure_bar: Decimal = Field(
        gt=0,
        le=Decimal("800"),
        description=(
            "Reciprocating / process compressor frames are published to 800 bar "
            "(MFR-RECIP-FRAME-LIMITS-2026-09)."
        ),
    )
    required_turndown_fraction: Decimal = Field(gt=0, le=1)

    continuous_operation: bool

    gas_molecular_weight: Decimal = Field(
        ge=Decimal("2"),
        le=Decimal("150"),
        description="GPSA Section 23 physical constants: hydrogen 2.016 to n-decane 142.3 kg/kmol.",
    )
    estimated_operating_hours_per_year: Decimal = Field(
        ge=0, le=Decimal("8784"), description="Calendar limit: 366 days x 24 h."
    )

    oil_free_air_required: bool = False


class RotaryScrewGeometryInput(BaseModel):
    """Optional male-rotor geometry input for a theoretical displacement estimate."""

    male_rotor_diameter_mm: Decimal = Field(gt=0)
    rotor_length_mm: Decimal = Field(gt=0)
    area_utilisation_coefficient: Decimal = Field(gt=0)


class RotaryScrewCalculationRequest(BaseModel):
    """Request payload for rotary screw compressor evaluation.

    ``rotor_geometry`` is optional -- supply it only when a theoretical
    displacement estimate is wanted. ``standard_reference_pressure_bar_a``
    and ``standard_reference_temperature_k`` are optional together -- supply
    both only when an ISO 1217 standard-air correction is wanted.
    ``annual_operating_hours`` and ``electricity_tariff_per_kwh`` are
    optional together -- supply both only when an annual energy cost is
    wanted.
    """

    inlet_pressure_bar_a: Decimal = Field(
        ge=Decimal("0.5"),
        le=Decimal("1.1"),
        description=(
            "Ambient intake, ISO 1217 reference 1 bar a; 0.5 bar a covers ~5000 m altitude."
        ),
    )
    inlet_temperature_k: Decimal = Field(
        ge=Decimal("233"),
        le=Decimal("333"),
        description=(
            "-40 to +60 degC intake; MFR-COMPAIR-OILFREE-SCREW-2026-09 rates -10 degC "
            "heater option and 46 degC ambient."
        ),
    )
    discharge_pressure_bar_g: Decimal = Field(
        gt=0,
        le=Decimal("15"),
        description=(
            "Rotary screw package maximum working pressure 15 bar g "
            "(MFR-KAESER-OILINJ-SCREW-2026-09); oil-free two-stage 10.7 bar g "
            "(MFR-COMPAIR-OILFREE-SCREW-2026-09)."
        ),
    )
    rotational_speed_rpm: Decimal = Field(
        gt=0,
        le=Decimal("25000"),
        description=(
            "Two-stage dry screw airends run 6000-25000 rpm "
            "(MFR-COMPAIR-OILFREE-SCREW-2026-09, DH comparison table)."
        ),
    )
    oil_type: RotaryScrewOilType
    control_type: RotaryScrewControlType
    stage_count: RotaryScrewStageCount = RotaryScrewStageCount.SINGLE_STAGE

    rated_fad_m3_per_min: Decimal = Field(
        gt=0,
        le=Decimal("160"),
        description=(
            "Largest single oil-free screw package 150 m3/min "
            "(MFR-ATLASCOPCO-AIR-RANGE-2026-09 ZR/ZT; CompAir DX355e 53.4, "
            "KAESER FSG 520-2 50.7) plus headroom."
        ),
    )
    package_input_power_kw: Decimal = Field(
        gt=0,
        le=Decimal("1050"),
        description=(
            "900 kW largest screw motor (MFR-ATLASCOPCO-AIR-RANGE-2026-09) x 1.15 "
            "nameplate ratio (MFR-KAESER-OILFREE-SCREW-2026-09 CSG 130-2 "
            "measured 1.08)."
        ),
    )

    rotor_geometry: RotaryScrewGeometryInput | None = None
    standard_reference_pressure_bar_a: Decimal | None = Field(
        default=None,
        ge=Decimal("0.9"),
        le=Decimal("1.05"),
        description="ISO 1217 reference 1.0 bar a; CAGI 14.5 psia = 0.9997 bar a.",
    )
    standard_reference_temperature_k: Decimal | None = Field(
        default=None,
        ge=Decimal("273"),
        le=Decimal("303"),
        description="ISO 1217 reference 20 degC (293.15 K); CAGI 68 degF (293.15 K).",
    )
    annual_operating_hours: Decimal | None = Field(default=None, ge=0, le=8760)
    electricity_tariff_per_kwh: Decimal | None = Field(
        default=None,
        ge=MIN_ELECTRICITY_TARIFF_INR_PER_KWH,
        le=MAX_ELECTRICITY_TARIFF_INR_PER_KWH,
    )
