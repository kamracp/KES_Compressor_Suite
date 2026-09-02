// Submit-time mirrors of backend input bounds (backend app/schemas/_bounds.py
// and the per-field ceilings landed in C-7b; evidence set
// MFR-ATLASCOPCO-AIR-RANGE-2026-09 unless noted). They exist so the user sees
// a message before a 422 - the backend remains the source of truth.
export const MAX_PLANT_AIR_PRESSURE_BAR_G = 25;
export const MAX_ASSET_FAD_NM3_PER_HR = 36000; // largest centrifugal plant-air package
export const MAX_ASSET_MOTOR_KW = 3150; // ZH+ centrifugal, largest single motor
export const MAX_MEASURED_POWER_KW = 3400; // 3150 kW x 1.08 measured/nameplate ratio
export const MIN_ELECTRICITY_TARIFF_INR_PER_KWH = 5;
export const MAX_ELECTRICITY_TARIFF_INR_PER_KWH = 25;

export function pushIfAbove(
  raw: string,
  bound: number,
  message: string,
  errors: string[],
): void {
  const value = Number(raw);
  if (Number.isFinite(value) && value > bound) {
    errors.push(message);
  }
}

export function pushIfTariffOutOfRange(raw: string, errors: string[]): void {
  const tariff = Number(raw);
  if (
    Number.isFinite(tariff) &&
    (tariff < MIN_ELECTRICITY_TARIFF_INR_PER_KWH ||
      tariff > MAX_ELECTRICITY_TARIFF_INR_PER_KWH)
  ) {
    errors.push(
      `Electricity tariff must be between ${MIN_ELECTRICITY_TARIFF_INR_PER_KWH} and ${MAX_ELECTRICITY_TARIFF_INR_PER_KWH} INR/kWh.`,
    );
  }
}
