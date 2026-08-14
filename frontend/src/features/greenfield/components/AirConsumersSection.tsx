import {
  Factory,
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

import {
  airConsumptionBasisOptions,
  airConsumerCategoryOptions,
  airQualityClassOptions,
  consumerCriticalityOptions,
} from "../greenfieldOptions";
import type {
  AirConsumerInput,
  AirConsumptionBasis,
  AirConsumerCategory,
  AirQualityClass,
  ConsumerCriticality,
} from "../greenfieldTypes";

type AirConsumersSectionProps = {
  consumers: AirConsumerInput[];
  onChange: (consumers: AirConsumerInput[]) => void;
};

function createConsumer(index: number): AirConsumerInput {
  return {
    consumer_code: `AC-${String(index + 1).padStart(3, "0")}`,
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

export function AirConsumersSection({
  consumers,
  onChange,
}: AirConsumersSectionProps) {
  function updateConsumer(
    index: number,
    changes: Partial<AirConsumerInput>,
  ): void {
    onChange(
      consumers.map((consumer, consumerIndex) =>
        consumerIndex === index
          ? {
              ...consumer,
              ...changes,
            }
          : consumer,
      ),
    );
  }

  function addConsumer(): void {
    onChange([
      ...consumers,
      createConsumer(consumers.length),
    ]);
  }

  function removeConsumer(index: number): void {
    if (consumers.length <= 1) {
      return;
    }

    onChange(
      consumers.filter(
        (_, consumerIndex) => consumerIndex !== index,
      ),
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div className="flex items-start gap-3">
            <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-700">
              <Factory className="size-5" />
            </div>

            <div>
              <CardTitle>
                Air Consumers
              </CardTitle>

              <CardDescription className="mt-1 max-w-3xl leading-6">
                Define production machines, instruments, pneumatic equipment,
                process users, and other compressed-air consumers that form the
                Greenfield demand basis.
              </CardDescription>
            </div>
          </div>

          <Button
            type="button"
            variant="outline"
            onClick={addConsumer}
          >
            <Plus className="size-4" />
            Add Consumer
          </Button>
        </div>
      </CardHeader>

      <CardContent className="space-y-5">
        {consumers.map((consumer, index) => (
          <section
            key={`${consumer.consumer_code}-${index}`}
            className="rounded-xl border border-slate-200 bg-slate-50/40 p-4 sm:p-5"
          >
            <div className="mb-5 flex items-center justify-between gap-4">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
                  Consumer {index + 1}
                </p>

                <h3 className="mt-1 text-base font-semibold text-slate-900">
                  {consumer.name || "New Air Consumer"}
                </h3>
              </div>

              <Button
                type="button"
                size="icon-sm"
                variant="ghost"
                disabled={consumers.length <= 1}
                onClick={() => removeConsumer(index)}
                aria-label={`Remove consumer ${index + 1}`}
              >
                <Trash2 className="size-4" />
              </Button>
            </div>

            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
              <div className="space-y-2">
                <Label htmlFor={`consumer-code-${index}`}>
                  Consumer Code
                </Label>

                <Input
                  id={`consumer-code-${index}`}
                  value={consumer.consumer_code}
                  onChange={(event) =>
                    updateConsumer(index, {
                      consumer_code: event.target.value,
                    })
                  }
                />
              </div>

              <div className="space-y-2 md:col-span-1 xl:col-span-2">
                <Label htmlFor={`consumer-name-${index}`}>
                  Consumer / Equipment Name
                </Label>

                <Input
                  id={`consumer-name-${index}`}
                  value={consumer.name}
                  placeholder="Example: CNC Machine Group"
                  onChange={(event) =>
                    updateConsumer(index, {
                      name: event.target.value,
                    })
                  }
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor={`consumer-quantity-${index}`}>
                  Quantity
                </Label>

                <Input
                  id={`consumer-quantity-${index}`}
                  type="number"
                  min="1"
                  step="1"
                  value={consumer.quantity}
                  onChange={(event) =>
                    updateConsumer(index, {
                      quantity: Math.max(
                        1,
                        Number(event.target.value) || 1,
                      ),
                    })
                  }
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor={`consumer-category-${index}`}>
                  Category
                </Label>

                <select
                  id={`consumer-category-${index}`}
                  value={consumer.category}
                  onChange={(event) =>
                    updateConsumer(index, {
                      category:
                        event.target.value as AirConsumerCategory,
                    })
                  }
                  className="h-9 w-full rounded-md border border-input bg-transparent px-3 text-sm shadow-xs outline-none focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50"
                >
                  {airConsumerCategoryOptions.map((option) => (
                    <option
                      key={option.value}
                      value={option.value}
                    >
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>

              <div className="space-y-2">
                <Label htmlFor={`consumer-quality-${index}`}>
                  Air Quality
                </Label>

                <select
                  id={`consumer-quality-${index}`}
                  value={consumer.air_quality_class}
                  onChange={(event) =>
                    updateConsumer(index, {
                      air_quality_class:
                        event.target.value as AirQualityClass,
                    })
                  }
                  className="h-9 w-full rounded-md border border-input bg-transparent px-3 text-sm shadow-xs outline-none focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50"
                >
                  {airQualityClassOptions.map((option) => (
                    <option
                      key={option.value}
                      value={option.value}
                    >
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>

              <div className="space-y-2">
                <Label htmlFor={`consumer-pressure-${index}`}>
                  Required Pressure
                </Label>

                <div className="relative">
                  <Input
                    id={`consumer-pressure-${index}`}
                    type="number"
                    min="0"
                    step="any"
                    value={consumer.required_pressure_bar_g}
                    onChange={(event) =>
                      updateConsumer(index, {
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
                <Label htmlFor={`consumer-criticality-${index}`}>
                  Criticality
                </Label>

                <select
                  id={`consumer-criticality-${index}`}
                  value={consumer.criticality ?? "NORMAL"}
                  onChange={(event) =>
                    updateConsumer(index, {
                      criticality:
                        event.target.value as ConsumerCriticality,
                    })
                  }
                  className="h-9 w-full rounded-md border border-input bg-transparent px-3 text-sm shadow-xs outline-none focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50"
                >
                  {consumerCriticalityOptions.map((option) => (
                    <option
                      key={option.value}
                      value={option.value}
                    >
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="my-5 border-t border-slate-200" />

            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
              <div className="space-y-2">
                <Label htmlFor={`consumption-basis-${index}`}>
                  Consumption Basis
                </Label>

                <select
                  id={`consumption-basis-${index}`}
                  value={consumer.consumption_basis}
                  onChange={(event) => {
                    const basis =
                      event.target.value as AirConsumptionBasis;

                    updateConsumer(index, {
                      consumption_basis: basis,
                      flow_per_unit_nm3_per_hr:
                        basis === "PER_CYCLE"
                          ? null
                          : consumer.flow_per_unit_nm3_per_hr ?? "",
                      air_per_cycle_nl:
                        basis === "PER_CYCLE"
                          ? consumer.air_per_cycle_nl ?? ""
                          : null,
                      cycles_per_minute:
                        basis === "PER_CYCLE"
                          ? consumer.cycles_per_minute ?? ""
                          : null,
                    });
                  }}
                  className="h-9 w-full rounded-md border border-input bg-transparent px-3 text-sm shadow-xs outline-none focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50"
                >
                  {airConsumptionBasisOptions.map((option) => (
                    <option
                      key={option.value}
                      value={option.value}
                    >
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>

              {consumer.consumption_basis === "PER_CYCLE" ? (
                <>
                  <div className="space-y-2">
                    <Label htmlFor={`air-per-cycle-${index}`}>
                      Air per Cycle
                    </Label>

                    <Input
                      id={`air-per-cycle-${index}`}
                      type="number"
                      min="0"
                      step="any"
                      value={consumer.air_per_cycle_nl ?? ""}
                      onChange={(event) =>
                        updateConsumer(index, {
                          air_per_cycle_nl: event.target.value,
                        })
                      }
                    />

                    <p className="text-xs text-slate-500">
                      Normal litres per cycle
                    </p>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor={`cycles-per-minute-${index}`}>
                      Cycles per Minute
                    </Label>

                    <Input
                      id={`cycles-per-minute-${index}`}
                      type="number"
                      min="0"
                      step="any"
                      value={consumer.cycles_per_minute ?? ""}
                      onChange={(event) =>
                        updateConsumer(index, {
                          cycles_per_minute: event.target.value,
                        })
                      }
                    />
                  </div>
                </>
              ) : (
                <div className="space-y-2">
                  <Label htmlFor={`flow-per-unit-${index}`}>
                    Flow per Unit
                  </Label>

                  <Input
                    id={`flow-per-unit-${index}`}
                    type="number"
                    min="0"
                    step="any"
                    value={
                      consumer.flow_per_unit_nm3_per_hr ?? ""
                    }
                    onChange={(event) =>
                      updateConsumer(index, {
                        flow_per_unit_nm3_per_hr:
                          event.target.value,
                      })
                    }
                  />

                  <p className="text-xs text-slate-500">
                    Nm³/h per operating unit
                  </p>
                </div>
              )}

              <div className="space-y-2">
                <Label htmlFor={`duty-factor-${index}`}>
                  Duty Factor
                </Label>

                <Input
                  id={`duty-factor-${index}`}
                  type="number"
                  min="0"
                  max="1"
                  step="0.01"
                  value={consumer.duty_factor ?? "1"}
                  onChange={(event) =>
                    updateConsumer(index, {
                      duty_factor: event.target.value,
                    })
                  }
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor={`simultaneity-${index}`}>
                  Simultaneity Factor
                </Label>

                <Input
                  id={`simultaneity-${index}`}
                  type="number"
                  min="0"
                  max="1"
                  step="0.01"
                  value={consumer.simultaneity_factor ?? "1"}
                  onChange={(event) =>
                    updateConsumer(index, {
                      simultaneity_factor:
                        event.target.value,
                    })
                  }
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor={`hours-day-${index}`}>
                  Operating Hours / Day
                </Label>

                <Input
                  id={`hours-day-${index}`}
                  type="number"
                  min="0"
                  max="24"
                  step="any"
                  value={
                    consumer.operating_hours_per_day ?? "24"
                  }
                  onChange={(event) =>
                    updateConsumer(index, {
                      operating_hours_per_day:
                        event.target.value,
                    })
                  }
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor={`days-year-${index}`}>
                  Operating Days / Year
                </Label>

                <Input
                  id={`days-year-${index}`}
                  type="number"
                  min="0"
                  max="366"
                  step="1"
                  value={
                    consumer.operating_days_per_year ?? "365"
                  }
                  onChange={(event) =>
                    updateConsumer(index, {
                      operating_days_per_year:
                        event.target.value,
                    })
                  }
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor={`consumer-area-${index}`}>
                  Area / Department
                </Label>

                <Input
                  id={`consumer-area-${index}`}
                  value={consumer.area ?? ""}
                  placeholder="Example: Machine Shop"
                  onChange={(event) =>
                    updateConsumer(index, {
                      area: event.target.value || null,
                    })
                  }
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor={`production-line-${index}`}>
                  Production Line
                </Label>

                <Input
                  id={`production-line-${index}`}
                  value={consumer.production_line ?? ""}
                  placeholder="Optional"
                  onChange={(event) =>
                    updateConsumer(index, {
                      production_line:
                        event.target.value || null,
                    })
                  }
                />
              </div>
            </div>
          </section>
        ))}
      </CardContent>
    </Card>
  );
}
