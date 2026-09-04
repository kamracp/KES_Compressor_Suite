import {
  MAX_PLANT_AIR_PRESSURE_BAR_G,
  pushIfAbove,
} from "../reference/inputBounds";

// Structural shapes so the page's local form-state types fit without import.
type NodePressureInput = { nodeCode: string; minimumPressure: string };
type SegmentPressureInput = { segmentCode: string; operatingPressure: string };

export type DistributionPressureInputs = {
  designSourcePressure: string;
  nodes: readonly NodePressureInput[];
  segments: readonly SegmentPressureInput[];
};

// C-7 item 1: submit-time mirrors of the backend distribution bounds
// (design_source_pressure_bar_g, minimum_pressure_bar_g, operating_pressure_bar_g
// all <= MAX_PLANT_AIR_PRESSURE_BAR_G). Blank optional node minimums are skipped.
export function validateDistributionPressures(
  inputs: DistributionPressureInputs,
): string[] {
  const errors: string[] = [];
  const plantAir = `cannot exceed ${MAX_PLANT_AIR_PRESSURE_BAR_G} bar g (plant-air ceiling).`;

  pushIfAbove(
    inputs.designSourcePressure,
    MAX_PLANT_AIR_PRESSURE_BAR_G,
    `Design source pressure ${plantAir}`,
    errors,
  );
  inputs.nodes.forEach((node, index) => {
    if (node.minimumPressure.trim().length === 0) {
      return;
    }
    const label = node.nodeCode.trim() || `Node ${index + 1}`;
    pushIfAbove(
      node.minimumPressure,
      MAX_PLANT_AIR_PRESSURE_BAR_G,
      `${label}: minimum pressure ${plantAir}`,
      errors,
    );
  });
  inputs.segments.forEach((segment, index) => {
    const label = segment.segmentCode.trim() || `Segment ${index + 1}`;
    pushIfAbove(
      segment.operatingPressure,
      MAX_PLANT_AIR_PRESSURE_BAR_G,
      `${label}: operating pressure ${plantAir}`,
      errors,
    );
  });
  return errors;
}
