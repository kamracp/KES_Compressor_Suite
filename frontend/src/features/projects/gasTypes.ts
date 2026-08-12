export type GasCompositionItem = {
  component: string;
  mole_fraction: number;
};

export type GasPropertiesRequest = {
  components: GasCompositionItem[];
  pressure_bar: number;
  temperature_k: number;
};

export type GasPropertiesResponse = {
  molecular_weight_kg_per_kmol: string;
  specific_gravity_air_1: string;

  pseudocritical_temperature_k: string;
  pseudocritical_pressure_bar: string;

  reduced_temperature: string;
  reduced_pressure: string;

  z_factor: string;
  z_factor_correlation: string;

  density_kg_per_m3: string;
};
