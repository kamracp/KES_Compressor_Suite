export type DecimalString = string;

export type PartLoadMode =
  | "LOAD_UNLOAD"
  | "MODULATION"
  | "VARIABLE_DISPLACEMENT"
  | "VARIABLE_SPEED"
  | "INLET_GUIDE_VANE";

export type BelowTurndownMode = "BLOW_OFF" | "UNLOAD";

export type PartLoadCandidateInput = {
  label: string;
  mode: PartLoadMode;
  unload_power_fraction?: DecimalString | null;
  modulation_floor_capacity_fraction?: DecimalString | null;
  minimum_flow_fraction?: DecimalString | null;
  minimum_flow_power_fraction?: DecimalString | null;
  turndown_flow_fraction?: DecimalString | null;
  power_fraction_at_turndown?: DecimalString | null;
  below_turndown?: BelowTurndownMode | null;
};

export type LoadDurationBinInput = {
  capacity_fraction: DecimalString;
  hours: DecimalString;
};

export type PartLoadComparisonRequest = {
  analysis_code: string;
  rated_fad_nm3_per_hr: DecimalString;
  rated_power_kw: DecimalString;
  candidates: PartLoadCandidateInput[];
  capacity_fractions: DecimalString[];
  load_duration: LoadDurationBinInput[];
  electricity_tariff_per_kwh: DecimalString | null;
};

export type CandidatePointResult = {
  capacity_fraction: DecimalString;
  power_fraction: DecimalString;
  power_kw: DecimalString;
  specific_power_kw_per_nm3_per_min: DecimalString | null;
  wasted_flow_nm3_per_hr: DecimalString;
  regime: string;
};

export type CandidateResult = {
  label: string;
  mode: PartLoadMode;
  points: CandidatePointResult[];
  annual_energy_kwh: DecimalString | null;
  annual_energy_cost: DecimalString | null;
  annual_blow_off_volume_nm3: DecimalString | null;
};

export type PointWinnerResult = {
  capacity_fraction: DecimalString;
  label: string;
  power_kw: DecimalString;
};

export type PartLoadComparisonResponse = {
  analysis_code: string;
  rated_fad_nm3_per_hr: DecimalString;
  rated_power_kw: DecimalString;
  candidates: CandidateResult[];
  lowest_power_per_point: PointWinnerResult[];
  lowest_annual_energy_label: string | null;
  profile_hours: DecimalString;
};
