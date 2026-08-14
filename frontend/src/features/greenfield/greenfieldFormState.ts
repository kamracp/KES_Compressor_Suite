import type {
  AirConsumerInput,
  AirTreatmentInput,
  CompressorStationInput,
  DemandProfilePointInput,
  GreenfieldSystemDesignRequest,
  PressureLossComponentInput,
  ReceiverSizingInput,
} from "./greenfieldTypes";

export type GreenfieldDesignBasisState = {
  minimumPointOfUsePressureBarG: string;
  leakageFraction: string;
  futureExpansionFraction: string;
  otherAllowanceFraction: string;
  controlMarginBar: string;
  annualOperatingDays: string;
  electricityTariffPerKwh: string;
};

export type GreenfieldFormState = {
  designBasis: GreenfieldDesignBasisState;
  consumers: AirConsumerInput[];
  demandProfilePoints: DemandProfilePointInput[];
  pressureLossComponents: PressureLossComponentInput[];
  station: CompressorStationInput | null;
  treatment: AirTreatmentInput | null;
  receiver: ReceiverSizingInput | null;
  specificPowerKwPerNm3PerMin: string;
};

function createInitialConsumer(): AirConsumerInput {
  return {
    consumer_code: "AC-001",
    name: "",
    category: "PRODUCTION_MACHINE",
    quantity: 1,
    required_pressure_bar_g: "6",
    air_quality_class: "GENERAL_PLANT_AIR",
    consumption_basis: "FLOW_WHEN_OPERATING",
    flow_per_unit_nm3_per_hr: "",
    air_per_cycle_nl: null,
    cycles_per_minute: null,
    duty_factor: "1",
    simultaneity_factor: "1",
    operating_hours_per_day: "24",
    operating_days_per_year: "365",
    criticality: "NORMAL",
    area: null,
    production_line: null,
    notes: null,
  };
}

function createInitialDemandPoint(): DemandProfilePointInput {
  return {
    period_index: 1,
    label: "Normal Demand",
    demand_nm3_per_hr: "",
    required_pressure_bar_g: "6",
    duration_hours: "8",
  };
}

export function createInitialGreenfieldFormState(): GreenfieldFormState {
  return {
    designBasis: {
      minimumPointOfUsePressureBarG: "6",
      leakageFraction: "0",
      futureExpansionFraction: "0",
      otherAllowanceFraction: "0",
      controlMarginBar: "0",
      annualOperatingDays: "",
      electricityTariffPerKwh: "0",
    },
    consumers: [createInitialConsumer()],
    demandProfilePoints: [createInitialDemandPoint()],
    pressureLossComponents: [],
    station: null,
    treatment: null,
    receiver: null,
    specificPowerKwPerNm3PerMin: "",
  };
}

function asNumber(value: string): number {
  return Number(value);
}

function requireNonNegative(
  value: string,
  label: string,
  errors: string[],
): void {
  const number = asNumber(value);

  if (value.trim() === "" || !Number.isFinite(number) || number < 0) {
    errors.push(`${label} must be zero or greater.`);
  }
}

function requirePositive(
  value: string,
  label: string,
  errors: string[],
): void {
  const number = asNumber(value);

  if (value.trim() === "" || !Number.isFinite(number) || number <= 0) {
    errors.push(`${label} must be greater than zero.`);
  }
}

function requireFraction(
  value: string,
  label: string,
  errors: string[],
  upperInclusive = true,
): void {
  const number = asNumber(value);

  const invalidUpperBound = upperInclusive
    ? number > 1
    : number >= 1;

  if (
    value.trim() === "" ||
    !Number.isFinite(number) ||
    number < 0 ||
    invalidUpperBound
  ) {
    errors.push(
      `${label} must be between zero and ${
        upperInclusive ? "one" : "less than one"
      }.`,
    );
  }
}

export function validateGreenfieldFormState(
  state: GreenfieldFormState,
): string[] {
  const errors: string[] = [];

  requireNonNegative(
    state.designBasis.minimumPointOfUsePressureBarG,
    "Minimum point-of-use pressure",
    errors,
  );
  requireFraction(
    state.designBasis.leakageFraction,
    "Leakage allowance",
    errors,
  );
  requireFraction(
    state.designBasis.futureExpansionFraction,
    "Future expansion allowance",
    errors,
  );
  requireFraction(
    state.designBasis.otherAllowanceFraction,
    "Other design allowance",
    errors,
  );
  requireNonNegative(
    state.designBasis.controlMarginBar,
    "Control margin",
    errors,
  );

  if (state.consumers.length === 0) {
    errors.push("At least one air consumer is required.");
  }

  state.consumers.forEach((consumer, index) => {
    const prefix = `Consumer ${index + 1}`;

    if (!consumer.consumer_code.trim()) {
      errors.push(`${prefix} code is required.`);
    }

    if (!consumer.name.trim()) {
      errors.push(`${prefix} name is required.`);
    }

    if (!Number.isInteger(consumer.quantity) || consumer.quantity <= 0) {
      errors.push(`${prefix} quantity must be greater than zero.`);
    }

    requireNonNegative(
      consumer.required_pressure_bar_g,
      `${prefix} required pressure`,
      errors,
    );

    requireFraction(
      consumer.duty_factor ?? "1",
      `${prefix} duty factor`,
      errors,
    );

    requireFraction(
      consumer.simultaneity_factor ?? "1",
      `${prefix} simultaneity factor`,
      errors,
    );

    if (consumer.consumption_basis === "PER_CYCLE") {
      requireNonNegative(
        consumer.air_per_cycle_nl ?? "",
        `${prefix} air per cycle`,
        errors,
      );

      requireNonNegative(
        consumer.cycles_per_minute ?? "",
        `${prefix} cycles per minute`,
        errors,
      );
    } else {
      requireNonNegative(
        consumer.flow_per_unit_nm3_per_hr ?? "",
        `${prefix} flow per unit`,
        errors,
      );
    }
  });

  if (state.demandProfilePoints.length === 0) {
    errors.push("At least one demand-profile period is required.");
  }

  state.demandProfilePoints.forEach((point, index) => {
    const prefix = `Demand period ${index + 1}`;

    if (!point.label.trim()) {
      errors.push(`${prefix} label is required.`);
    }

    requireNonNegative(
      point.demand_nm3_per_hr,
      `${prefix} demand`,
      errors,
    );

    requireNonNegative(
      point.required_pressure_bar_g,
      `${prefix} required pressure`,
      errors,
    );

    requirePositive(
      point.duration_hours,
      `${prefix} duration`,
      errors,
    );
  });

  state.pressureLossComponents.forEach((component, index) => {
    const prefix = `Pressure-loss component ${index + 1}`;

    if (!component.component_code.trim()) {
      errors.push(`${prefix} code is required.`);
    }

    if (!component.name.trim()) {
      errors.push(`${prefix} name is required.`);
    }

    if (!component.category.trim()) {
      errors.push(`${prefix} category is required.`);
    }

    requireNonNegative(
      component.pressure_drop_bar,
      `${prefix} pressure drop`,
      errors,
    );
  });

  if (state.treatment) {
    requirePositive(
      state.treatment.required_delivered_flow_nm3_per_hr,
      "Treatment delivered flow",
      errors,
    );

    requirePositive(
      state.treatment.dryer_correction_factor ?? "1",
      "Dryer correction factor",
      errors,
    );

    requireFraction(
      state.treatment.dryer_purge_fraction ?? "0",
      "Dryer purge fraction",
      errors,
      false,
    );

    requireFraction(
      state.treatment.treatment_capacity_margin_fraction ?? "0",
      "Treatment capacity margin",
      errors,
    );
  }

  if (state.station) {
    if (!state.station.station_code.trim()) {
      errors.push("Compressor station code is required.");
    }

    requirePositive(
      state.station.design_flow_nm3_per_hr,
      "Station design flow",
      errors,
    );

    requireNonNegative(
      state.station.minimum_required_pressure_bar_g,
      "Station minimum required pressure",
      errors,
    );

    state.station.units.forEach((unit, index) => {
      const prefix = `Compressor ${index + 1}`;

      if (!unit.unit_code.trim()) {
        errors.push(`${prefix} unit code is required.`);
      }

      requirePositive(
        unit.rated_fad_nm3_per_hr,
        `${prefix} rated FAD`,
        errors,
      );

      requireFraction(
        unit.minimum_stable_flow_fraction,
        `${prefix} minimum stable flow fraction`,
        errors,
      );

      requireNonNegative(
        unit.rated_discharge_pressure_bar_g,
        `${prefix} rated discharge pressure`,
        errors,
      );
    });
  }

  if (state.receiver) {
    requireNonNegative(
      state.receiver.peak_demand_nm3_per_hr,
      "Receiver peak demand",
      errors,
    );

    requireNonNegative(
      state.receiver.available_compressor_flow_nm3_per_hr,
      "Receiver available compressor flow",
      errors,
    );

    requirePositive(
      state.receiver.event_duration_seconds,
      "Receiver event duration",
      errors,
    );

    requireNonNegative(
      state.receiver.receiver_high_pressure_bar_g,
      "Receiver high pressure",
      errors,
    );

    requireNonNegative(
      state.receiver.receiver_low_pressure_bar_g,
      "Receiver low pressure",
      errors,
    );

    if (
      Number(state.receiver.receiver_high_pressure_bar_g) <=
      Number(state.receiver.receiver_low_pressure_bar_g)
    ) {
      errors.push(
        "Receiver high pressure must be greater than receiver low pressure.",
      );
    }

    requireFraction(
      state.receiver.reserve_fraction ?? "0",
      "Receiver reserve fraction",
      errors,
    );
  }

  if (state.specificPowerKwPerNm3PerMin.trim()) {
    requirePositive(
      state.specificPowerKwPerNm3PerMin,
      "Specific power",
      errors,
    );

    requirePositive(
      state.designBasis.annualOperatingDays,
      "Annual operating days",
      errors,
    );
  }

  return errors;
}

export function buildGreenfieldDesignRequest(
  state: GreenfieldFormState,
): GreenfieldSystemDesignRequest {
  const energyEnabled =
    state.specificPowerKwPerNm3PerMin.trim() !== "";

  return {
    consumers: state.consumers,
    demand_profile_points: state.demandProfilePoints,
    leakage_fraction: state.designBasis.leakageFraction,
    future_expansion_fraction:
      state.designBasis.futureExpansionFraction,
    other_allowance_fraction:
      state.designBasis.otherAllowanceFraction,
    minimum_point_of_use_pressure_bar_g:
      state.designBasis.minimumPointOfUsePressureBarG,
    pressure_loss_components: state.pressureLossComponents,
    control_margin_bar: state.designBasis.controlMarginBar,
    treatment: state.treatment,
    station: state.station,
    receiver: state.receiver,
    specific_power_kw_per_nm3_per_min: energyEnabled
      ? state.specificPowerKwPerNm3PerMin
      : null,
    annual_operating_days: energyEnabled
      ? state.designBasis.annualOperatingDays
      : null,
    electricity_tariff_per_kwh:
      state.designBasis.electricityTariffPerKwh || "0",
  };
}
