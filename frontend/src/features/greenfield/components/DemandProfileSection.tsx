import {
  BarChart3,
  Plus,
  Trash2,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

import type { DemandProfilePointInput } from "../greenfieldTypes";

type DemandProfileSectionProps = {
  points: DemandProfilePointInput[];
  onChange: (points: DemandProfilePointInput[]) => void;
};

function createProfilePoint(
  index: number,
): DemandProfilePointInput {
  return {
    period_index: index + 1,
    label: `Operating Period ${index + 1}`,
    demand_nm3_per_hr: "",
    required_pressure_bar_g: "6",
    duration_hours: "8",
  };
}

export function DemandProfileSection({
  points,
  onChange,
}: DemandProfileSectionProps) {
  function updatePoint(
    index: number,
    changes: Partial<DemandProfilePointInput>,
  ): void {
    onChange(
      points.map((point, pointIndex) =>
        pointIndex === index
          ? {
              ...point,
              ...changes,
            }
          : point,
      ),
    );
  }

  function addPoint(): void {
    onChange([
      ...points,
      createProfilePoint(points.length),
    ]);
  }

  function removePoint(index: number): void {
    if (points.length <= 1) {
      return;
    }

    const nextPoints = points
      .filter((_, pointIndex) => pointIndex !== index)
      .map((point, pointIndex) => ({
        ...point,
        period_index: pointIndex + 1,
      }));

    onChange(nextPoints);
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div className="flex items-start gap-3">
            <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-700">
              <BarChart3 className="size-5" />
            </div>

            <div>
              <CardTitle>
                Demand Profile
              </CardTitle>

              <CardDescription className="mt-1 max-w-3xl leading-6">
                Define representative operating periods so the design engine
                can evaluate low, normal, peak, shift-based, or other
                production demand conditions.
              </CardDescription>
            </div>
          </div>

          <Button
            type="button"
            variant="outline"
            onClick={addPoint}
          >
            <Plus className="size-4" />
            Add Period
          </Button>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {points.map((point, index) => (
          <section
            key={`${point.period_index}-${index}`}
            className="rounded-xl border border-slate-200 bg-slate-50/40 p-4"
          >
            <div className="mb-4 flex items-center justify-between gap-4">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
                  Period {index + 1}
                </p>

                <p className="mt-1 text-sm font-medium text-slate-900">
                  {point.label || "Operating Period"}
                </p>
              </div>

              <Button
                type="button"
                size="icon-sm"
                variant="ghost"
                disabled={points.length <= 1}
                onClick={() => removePoint(index)}
                aria-label={`Remove demand period ${index + 1}`}
              >
                <Trash2 className="size-4" />
              </Button>
            </div>

            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
              <div className="space-y-2">
                <Label htmlFor={`profile-label-${index}`}>
                  Period Label
                </Label>

                <Input
                  id={`profile-label-${index}`}
                  value={point.label}
                  placeholder="Example: Peak Shift"
                  onChange={(event) =>
                    updatePoint(index, {
                      label: event.target.value,
                    })
                  }
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor={`profile-demand-${index}`}>
                  Demand
                </Label>

                <div className="relative">
                  <Input
                    id={`profile-demand-${index}`}
                    type="number"
                    min="0"
                    step="any"
                    value={point.demand_nm3_per_hr}
                    onChange={(event) =>
                      updatePoint(index, {
                        demand_nm3_per_hr:
                          event.target.value,
                      })
                    }
                    className="pr-16"
                  />

                  <span className="pointer-events-none absolute inset-y-0 right-3 flex items-center text-xs text-slate-500">
                    Nm³/h
                  </span>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor={`profile-pressure-${index}`}>
                  Required Pressure
                </Label>

                <div className="relative">
                  <Input
                    id={`profile-pressure-${index}`}
                    type="number"
                    min="0"
                    step="any"
                    value={point.required_pressure_bar_g}
                    onChange={(event) =>
                      updatePoint(index, {
                        required_pressure_bar_g:
                          event.target.value,
                      })
                    }
                    className="pr-16"
                  />

                  <span className="pointer-events-none absolute inset-y-0 right-3 flex items-center text-xs text-slate-500">
                    bar(g)
                  </span>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor={`profile-duration-${index}`}>
                  Duration
                </Label>

                <div className="relative">
                  <Input
                    id={`profile-duration-${index}`}
                    type="number"
                    min="0.01"
                    max="24"
                    step="any"
                    value={point.duration_hours}
                    onChange={(event) =>
                      updatePoint(index, {
                        duration_hours:
                          event.target.value,
                      })
                    }
                    className="pr-14"
                  />

                  <span className="pointer-events-none absolute inset-y-0 right-3 flex items-center text-xs text-slate-500">
                    h
                  </span>
                </div>
              </div>
            </div>
          </section>
        ))}

        <div className="rounded-lg border border-dashed border-slate-300 p-4">
          <p className="text-sm font-medium text-slate-800">
            Engineering purpose
          </p>

          <p className="mt-1 text-xs leading-5 text-slate-500">
            The highest profile demand contributes to peak-duty evaluation,
            while period duration provides the operating basis required for
            realistic system and energy analysis.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
