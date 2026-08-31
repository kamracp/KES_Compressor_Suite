import { Droplet } from "lucide-react";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export type AirTreatmentField =
  | "condensateDrainAirLossNm3PerHr"
  | "filterExcessPressureDropBar";

type AirTreatmentSectionProps = {
  condensateDrainAirLossNm3PerHr: string;
  filterExcessPressureDropBar: string;

  onChange: (field: AirTreatmentField, value: string) => void;
};

export function AirTreatmentSection({
  condensateDrainAirLossNm3PerHr,
  filterExcessPressureDropBar,
  onChange,
}: AirTreatmentSectionProps) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-start gap-3">
          <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-700">
            <Droplet className="size-5" />
          </div>

          <div>
            <CardTitle>
              Condensate Drains & Filters
            </CardTitle>

            <CardDescription className="mt-1 max-w-3xl leading-6">
              Optional. Measured air-treatment losses. Both feed the
              opportunity register through the same engines used elsewhere in
              this audit: drain air loss through the leakage-energy engine,
              filter pressure drop through the adiabatic pressure-saving
              method.
            </CardDescription>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        <div className="grid gap-4 md:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="brownfield-drain-loss">
              Condensate Drain Air Loss
            </Label>

            <Input
              id="brownfield-drain-loss"
              type="number"
              min="0"
              step="any"
              value={condensateDrainAirLossNm3PerHr}
              placeholder="Optional"
              onChange={(event) =>
                onChange(
                  "condensateDrainAirLossNm3PerHr",
                  event.target.value,
                )
              }
            />

            <p className="text-xs leading-5 text-slate-500">
              Nm³/hr. Combined air vented by all timed solenoid drains,
              which fire on a clock regardless of condensate level.
              Zero-loss float or electronic drains remove this waste
              entirely (DOE / Compressed Air Challenge).
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="brownfield-filter-drop">
              Filter Excess Pressure Drop
            </Label>

            <Input
              id="brownfield-filter-drop"
              type="number"
              min="0"
              step="any"
              value={filterExcessPressureDropBar}
              placeholder="Optional"
              onChange={(event) =>
                onChange(
                  "filterExcessPressureDropBar",
                  event.target.value,
                )
              }
            />

            <p className="text-xs leading-5 text-slate-500">
              bar. Drop across dirty or undersized elements over and above
              their clean design value — measured, not assumed. The
              compressor must generate this extra pressure continuously.
            </p>
          </div>
        </div>

        <div className="rounded-lg border border-dashed border-slate-300 p-4">
          <p className="text-sm font-medium text-slate-800">
            Measure, do not estimate
          </p>

          <p className="mt-1 text-xs leading-5 text-slate-500">
            Drain air loss is best taken from a timed-discharge test or drain
            manufacturer flow data; filter excess drop from the differential
            gauge against the element's clean-condition specification. Left
            blank, neither opportunity is raised at all — this platform does
            not fill in a typical value on your behalf.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
