import { useState } from "react";

import { AlertTriangle, Play, Plus, RotateCcw, SlidersHorizontal, Trash2 } from "lucide-react";
import { useMutation } from "@tanstack/react-query";
import { Link } from "react-router";

import { Badge } from "@/components/ui/badge";
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

import { useAuth } from "../features/auth/AuthProvider";
import {
  PART_LOAD_MODE_OPTIONS,
  buildPartLoadComparisonRequest,
  createCandidate,
  createInitialPartLoadFormState,
  createLoadDurationRow,
  validatePartLoadFormState,
  type CandidateFormState,
  type LoadDurationRowState,
  type PartLoadFormState,
} from "../features/partload/partLoadFormState";
import { comparePartLoadModes } from "../features/partload/partLoadService";
import type { PartLoadComparisonResponse } from "../features/partload/partLoadTypes";
import { useProjectContext } from "../features/projects/useProjectContext";
import { ApiError } from "../services/apiClient";

function extractErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    const details = error.details;
    if (typeof details === "object" && details !== null && "detail" in details) {
      const detail = (details as { detail?: unknown }).detail;
      if (typeof detail === "string") {
        return detail;
      }
    }
    return `Part-load API request failed with status ${error.status}.`;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return "Part-load comparison could not be completed.";
}

function formatNumber(value: string | null, digits = 1): string {
  if (value === null) {
    return "—";
  }
  const parsed = Number(value);
  return Number.isFinite(parsed)
    ? parsed.toLocaleString("en-IN", { maximumFractionDigits: digits })
    : value;
}

const CHART_COLORS = ["#0f172a", "#b45309", "#0369a1", "#15803d", "#7c3aed", "#be123c", "#0891b2", "#4d7c0f"];

function PartLoadChart({ result }: { result: PartLoadComparisonResponse }) {
  const width = 640;
  const height = 320;
  const pad = { left: 56, right: 24, top: 16, bottom: 44 };
  const x = (fraction: number) => pad.left + fraction * (width - pad.left - pad.right);
  const y = (fraction: number) => height - pad.bottom - fraction * (height - pad.top - pad.bottom);
  const ticks = [0, 0.25, 0.5, 0.75, 1];

  return (
    <svg viewBox={`0 0 ${width} ${height}`} className="w-full max-w-3xl" role="img" aria-label="Part-load power curves">
      {ticks.map((tick) => (
        <g key={`grid-${tick}`}>
          <line x1={x(tick)} x2={x(tick)} y1={y(0)} y2={y(1)} stroke="#e2e8f0" />
          <line x1={x(0)} x2={x(1)} y1={y(tick)} y2={y(tick)} stroke="#e2e8f0" />
          <text x={x(tick)} y={height - pad.bottom + 18} textAnchor="middle" fontSize="11" fill="#64748b">
            {Math.round(tick * 100)}%
          </text>
          <text x={pad.left - 8} y={y(tick) + 4} textAnchor="end" fontSize="11" fill="#64748b">
            {Math.round(tick * 100)}%
          </text>
        </g>
      ))}
      <text x={(x(0) + x(1)) / 2} y={height - 6} textAnchor="middle" fontSize="12" fill="#334155">
        Capacity (% of rated FAD)
      </text>
      <text x={14} y={(y(0) + y(1)) / 2} textAnchor="middle" fontSize="12" fill="#334155" transform={`rotate(-90 14 ${(y(0) + y(1)) / 2})`}>
        Power (% of rated)
      </text>
      {result.candidates.map((candidate, index) => {
        const color = CHART_COLORS[index % CHART_COLORS.length];
        const points = candidate.points
          .map((p) => `${x(Number(p.capacity_fraction))},${y(Number(p.power_fraction))}`)
          .join(" ");
        return (
          <g key={candidate.label}>
            <polyline points={points} fill="none" stroke={color} strokeWidth="2" />
            {candidate.points.map((p) => (
              <circle key={p.capacity_fraction} cx={x(Number(p.capacity_fraction))} cy={y(Number(p.power_fraction))} r="3" fill={color} />
            ))}
            <text x={x(1) + 4} y={y(Number(candidate.points[candidate.points.length - 1].power_fraction)) - 6 - index * 12} fontSize="11" fill={color}>
              {candidate.label}
            </text>
          </g>
        );
      })}
    </svg>
  );
}

export function PartLoadComparisonPage() {
  const { accessToken } = useAuth();
  const { projectId, hasValidProjectId, project } = useProjectContext();

  const [formState, setFormState] = useState<PartLoadFormState>(createInitialPartLoadFormState);
  const [validationErrors, setValidationErrors] = useState<string[]>([]);

  if (!hasValidProjectId) {
    throw new Error("Valid project ID is required.");
  }

  const mutation = useMutation({
    mutationFn: () => {
      if (!accessToken) {
        throw new Error("Authenticated access token is required.");
      }
      return comparePartLoadModes(accessToken, buildPartLoadComparisonRequest(formState));
    },
  });

  function changeState(updater: (current: PartLoadFormState) => PartLoadFormState): void {
    mutation.reset();
    setValidationErrors([]);
    setFormState(updater);
  }

  function setField<K extends keyof PartLoadFormState>(field: K, value: PartLoadFormState[K]): void {
    changeState((current) => ({ ...current, [field]: value }));
  }

  function patchCandidate(id: string, patch: Partial<CandidateFormState>): void {
    changeState((current) => ({
      ...current,
      candidates: current.candidates.map((c) => (c.id === id ? { ...c, ...patch } : c)),
    }));
  }

  function patchRow(id: string, patch: Partial<LoadDurationRowState>): void {
    changeState((current) => ({
      ...current,
      loadDuration: current.loadDuration.map((r) => (r.id === id ? { ...r, ...patch } : r)),
    }));
  }

  function run(): void {
    const errors = validatePartLoadFormState(formState);
    if (errors.length > 0) {
      setValidationErrors(errors);
      mutation.reset();
      return;
    }
    setValidationErrors([]);
    mutation.mutate();
  }

  const result = mutation.data;

  return (
    <main className="space-y-6">
      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="max-w-3xl space-y-3">
            <Badge variant="outline">Performance Engineering</Badge>
            <h1 className="text-3xl font-semibold tracking-tight text-slate-900">
              Part-Load Control Mode Comparison
            </h1>
            <p className="leading-7 text-slate-600">
              One machine, several capacity-control modes: power, specific power and blow-off at
              each load, and annual energy over a load-duration profile. Curves follow DOE / CAC
              Sourcebook, CAGI and Atlas Copco evidence; machine-specific points are yours.
            </p>
            <div className="flex flex-wrap gap-2 text-xs text-slate-600">
              <Badge variant="outline">
                {project ? project.project_code : `Project ${projectId}`}
              </Badge>
              <Badge variant="outline">Load/unload · Modulation · Variable displacement · VSD · IGV</Badge>
            </div>
          </div>
          <div className="flex gap-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => {
                mutation.reset();
                setValidationErrors([]);
                setFormState(createInitialPartLoadFormState());
              }}
            >
              <RotateCcw className="size-4" />
              Reset
            </Button>
            <Button type="button" onClick={run} disabled={mutation.isPending}>
              <Play className="size-4" />
              Compare Modes
            </Button>
          </div>
        </div>
      </section>

      <Card>
        <CardHeader>
          <div className="flex items-start gap-3">
            <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-700">
              <SlidersHorizontal className="size-5" />
            </div>
            <div>
              <CardTitle>Machine & Comparison Basis</CardTitle>
              <CardDescription className="mt-1 leading-6">
                Rated FAD and rated (full-load) power of the machine being compared. Capacity
                fractions are the load points evaluated; the tariff is optional and only prices
                the load-duration profile.
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <div className="space-y-2">
              <Label htmlFor="pl-code">Analysis Code</Label>
              <Input id="pl-code" value={formState.analysisCode} placeholder="Example: PL-2026-001" onChange={(e) => setField("analysisCode", e.target.value)} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="pl-fad">Rated FAD (Nm³/h)</Label>
              <Input id="pl-fad" type="number" min="0" step="any" value={formState.ratedFadNm3PerHr} placeholder="Example: 1800" onChange={(e) => setField("ratedFadNm3PerHr", e.target.value)} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="pl-kw">Rated Power (kW)</Label>
              <Input id="pl-kw" type="number" min="0" step="any" value={formState.ratedPowerKw} placeholder="Example: 250" onChange={(e) => setField("ratedPowerKw", e.target.value)} />
            </div>
            <div className="space-y-2 md:col-span-2">
              <Label htmlFor="pl-fractions">Capacity Fractions</Label>
              <Input id="pl-fractions" value={formState.capacityFractionsText} onChange={(e) => setField("capacityFractionsText", e.target.value)} />
              <p className="text-xs leading-5 text-slate-500">Comma separated, 0–1. Example: 0.25, 0.5, 0.75, 1</p>
            </div>
            <div className="space-y-2">
              <Label htmlFor="pl-tariff">Electricity Tariff (per kWh)</Label>
              <Input id="pl-tariff" type="number" min="0" step="any" value={formState.electricityTariffPerKwh} placeholder="Optional" onChange={(e) => setField("electricityTariffPerKwh", e.target.value)} />
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Control-Mode Candidates</CardTitle>
          <CardDescription className="mt-1 leading-6">
            Screw unload power 0.15–0.35 (DOE), modulation floor 0.10–0.40 (DOE default 0.40),
            VSD minimum flow ≥ 0.14, centrifugal turndown 0.10–0.45 with machine power at
            turndown (CAGI), auto-dual off-loaded power 0.05–0.35 (Atlas Copco CAM ~0.20).
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {formState.candidates.map((candidate, index) => {
            const isIgv = candidate.mode === "INLET_GUIDE_VANE";
            const isVsd = candidate.mode === "VARIABLE_SPEED";
            const isModulation = candidate.mode === "MODULATION";
            const base = `pl-c-${candidate.id}`;
            return (
              <div key={candidate.id} className="rounded-lg border border-slate-200 p-4">
                <div className="mb-3 flex items-center justify-between">
                  <p className="text-sm font-medium text-slate-900">Candidate {index + 1}</p>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() =>
                      changeState((current) => ({
                        ...current,
                        candidates: current.candidates.filter((c) => c.id !== candidate.id),
                      }))
                    }
                  >
                    <Trash2 className="size-4" />
                    Remove
                  </Button>
                </div>
                <div className="grid gap-3 md:grid-cols-4">
                  <div className="space-y-1">
                    <Label htmlFor={`${base}-label`}>Label</Label>
                    <Input id={`${base}-label`} value={candidate.label} onChange={(e) => patchCandidate(candidate.id, { label: e.target.value })} />
                  </div>
                  <div className="space-y-1">
                    <Label htmlFor={`${base}-mode`}>Control mode</Label>
                    <select
                      id={`${base}-mode`}
                      className="h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm"
                      value={candidate.mode}
                      onChange={(e) => {
                        const fresh = createCandidate(e.target.value as CandidateFormState["mode"]);
                        patchCandidate(candidate.id, { ...fresh, id: candidate.id, label: candidate.label });
                      }}
                    >
                      {PART_LOAD_MODE_OPTIONS.map((option) => (
                        <option key={option.value} value={option.value}>{option.label}</option>
                      ))}
                    </select>
                  </div>
                  <div className="space-y-1">
                    <Label htmlFor={`${base}-unload`}>{isIgv ? "Off-loaded power fraction" : "Unload power fraction"}</Label>
                    <Input id={`${base}-unload`} type="number" min={isIgv ? "0.05" : "0.15"} max="0.35" step="0.01" placeholder={isIgv ? "Auto-dual only" : undefined} value={candidate.unloadPowerFraction} onChange={(e) => patchCandidate(candidate.id, { unloadPowerFraction: e.target.value })} />
                  </div>
                  {isModulation && (
                    <div className="space-y-1">
                      <Label htmlFor={`${base}-floor`}>Modulation floor</Label>
                      <Input id={`${base}-floor`} type="number" min="0.1" max="0.4" step="0.01" placeholder="Default 0.40 (DOE)" value={candidate.modulationFloorCapacityFraction} onChange={(e) => patchCandidate(candidate.id, { modulationFloorCapacityFraction: e.target.value })} />
                    </div>
                  )}
                  {isVsd && (
                    <>
                      <div className="space-y-1">
                        <Label htmlFor={`${base}-qmin`}>Minimum flow fraction</Label>
                        <Input id={`${base}-qmin`} type="number" min="0.14" max="1" step="0.01" placeholder="Example: 0.3" value={candidate.minimumFlowFraction} onChange={(e) => patchCandidate(candidate.id, { minimumFlowFraction: e.target.value })} />
                      </div>
                      <div className="space-y-1">
                        <Label htmlFor={`${base}-pmin`}>Power at minimum flow</Label>
                        <Input id={`${base}-pmin`} type="number" min="0" max="1" step="0.01" placeholder="fraction of rated" value={candidate.minimumFlowPowerFraction} onChange={(e) => patchCandidate(candidate.id, { minimumFlowPowerFraction: e.target.value })} />
                      </div>
                    </>
                  )}
                  {isIgv && (
                    <>
                      <div className="space-y-1">
                        <Label htmlFor={`${base}-td`}>Turndown fraction</Label>
                        <Input id={`${base}-td`} type="number" min="0.1" max="0.45" step="0.01" placeholder="Example: 0.30" value={candidate.turndownFlowFraction} onChange={(e) => patchCandidate(candidate.id, { turndownFlowFraction: e.target.value })} />
                      </div>
                      <div className="space-y-1">
                        <Label htmlFor={`${base}-ptd`}>Power at turndown</Label>
                        <Input id={`${base}-ptd`} type="number" min="0.6" max="1" step="0.01" placeholder="fraction of rated" value={candidate.powerFractionAtTurndown} onChange={(e) => patchCandidate(candidate.id, { powerFractionAtTurndown: e.target.value })} />
                      </div>
                      <div className="space-y-1">
                        <Label htmlFor={`${base}-below`}>Below turndown</Label>
                        <select
                          id={`${base}-below`}
                          className="h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm"
                          value={candidate.belowTurndown}
                          onChange={(e) => patchCandidate(candidate.id, { belowTurndown: e.target.value === "UNLOAD" ? "UNLOAD" : "BLOW_OFF" })}
                        >
                          <option value="BLOW_OFF">Blow-off (power unchanged)</option>
                          <option value="UNLOAD">Auto-dual unload</option>
                        </select>
                      </div>
                    </>
                  )}
                </div>
              </div>
            );
          })}
          <Button
            type="button"
            variant="outline"
            disabled={formState.candidates.length >= 8}
            onClick={() =>
              changeState((current) => ({
                ...current,
                candidates: [...current.candidates, createCandidate("VARIABLE_SPEED")],
              }))
            }
          >
            <Plus className="size-4" />
            Add candidate
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Load-Duration Profile (optional)</CardTitle>
          <CardDescription className="mt-1 leading-6">
            Hours per year at each capacity fraction. Enables annual energy, cost and blow-off
            volume per candidate. Total must not exceed 8,784 h.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {formState.loadDuration.map((row, index) => (
            <div key={row.id} className="grid gap-3 md:grid-cols-4">
              <div className="space-y-1">
                <Label htmlFor={`pl-ld-${row.id}-q`}>Capacity fraction {index + 1}</Label>
                <Input id={`pl-ld-${row.id}-q`} type="number" min="0" max="1" step="0.01" value={row.capacityFraction} onChange={(e) => patchRow(row.id, { capacityFraction: e.target.value })} />
              </div>
              <div className="space-y-1">
                <Label htmlFor={`pl-ld-${row.id}-h`}>Hours per year</Label>
                <Input id={`pl-ld-${row.id}-h`} type="number" min="0" step="1" value={row.hours} onChange={(e) => patchRow(row.id, { hours: e.target.value })} />
              </div>
              <div className="flex items-end">
                <Button type="button" variant="ghost" size="sm" onClick={() => changeState((current) => ({ ...current, loadDuration: current.loadDuration.filter((r) => r.id !== row.id) }))}>
                  <Trash2 className="size-4" />
                  Remove
                </Button>
              </div>
            </div>
          ))}
          <Button type="button" variant="outline" disabled={formState.loadDuration.length >= 24} onClick={() => changeState((current) => ({ ...current, loadDuration: [...current.loadDuration, createLoadDurationRow()] }))}>
            <Plus className="size-4" />
            Add row
          </Button>
        </CardContent>
      </Card>

      {validationErrors.length > 0 && (
        <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-800">
          <div className="mb-2 flex items-center gap-2 font-medium">
            <AlertTriangle className="size-4" />
            Inputs require review
          </div>
          <ul className="list-disc space-y-1 pl-5">
            {validationErrors.map((error) => (
              <li key={error}>{error}</li>
            ))}
          </ul>
        </div>
      )}

      {mutation.isError && (
        <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-800">
          {extractErrorMessage(mutation.error)}
        </div>
      )}

      {result && (
        <Card>
          <CardHeader>
            <CardTitle>Comparison Results · {result.analysis_code}</CardTitle>
            <CardDescription className="mt-1 leading-6">
              {formatNumber(result.rated_fad_nm3_per_hr, 0)} Nm³/h · {formatNumber(result.rated_power_kw, 0)} kW rated.
              Lowest-power mode at each load is marked; annual figures need a load-duration profile.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <PartLoadChart result={result} />

            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-200 text-left text-xs uppercase tracking-wide text-slate-500">
                    <th className="py-2 pr-4">Candidate</th>
                    {result.candidates[0].points.map((p) => (
                      <th key={p.capacity_fraction} className="py-2 pr-4">
                        {Math.round(Number(p.capacity_fraction) * 100)}% load
                      </th>
                    ))}
                    <th className="py-2 pr-4">Annual kWh</th>
                    <th className="py-2 pr-4">Annual cost</th>
                    <th className="py-2 pr-4">Blow-off Nm³</th>
                  </tr>
                </thead>
                <tbody>
                  {result.candidates.map((candidate) => (
                    <tr key={candidate.label} className="border-b border-slate-100 align-top">
                      <td className="py-2 pr-4 font-medium text-slate-900">
                        {candidate.label}
                        <span className="block text-xs font-normal text-slate-500">{candidate.mode}</span>
                        {result.lowest_annual_energy_label === candidate.label && (
                          <Badge variant="outline" className="mt-1">Lowest annual energy</Badge>
                        )}
                      </td>
                      {candidate.points.map((p) => {
                        const winner = result.lowest_power_per_point.find(
                          (w) => w.capacity_fraction === p.capacity_fraction && w.label === candidate.label,
                        );
                        return (
                          <td key={p.capacity_fraction} className={`py-2 pr-4 ${winner ? "font-semibold text-emerald-700" : "text-slate-700"}`}>
                            {formatNumber(p.power_kw)} kW
                            <span className="block text-xs text-slate-500">
                              {p.specific_power_kw_per_nm3_per_min === null ? "—" : `${formatNumber(p.specific_power_kw_per_nm3_per_min, 2)} kW/(Nm³/min)`}
                            </span>
                            <span className="block text-xs text-slate-500">{p.regime}</span>
                            {Number(p.wasted_flow_nm3_per_hr) > 0 && (
                              <span className="block text-xs text-amber-700">vents {formatNumber(p.wasted_flow_nm3_per_hr, 0)} Nm³/h</span>
                            )}
                          </td>
                        );
                      })}
                      <td className="py-2 pr-4 text-slate-700">{formatNumber(candidate.annual_energy_kwh, 0)}</td>
                      <td className="py-2 pr-4 text-slate-700">{formatNumber(candidate.annual_energy_cost, 0)}</td>
                      <td className="py-2 pr-4 text-slate-700">{formatNumber(candidate.annual_blow_off_volume_nm3, 0)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <p className="text-xs leading-5 text-slate-500">
              Load/unload is the large-storage asymptote (no blowdown transient here — use the
              sequencing simulator with a receiver volume for storage effects). Profile basis:{" "}
              {formatNumber(result.profile_hours, 0)} h.
            </p>
          </CardContent>
        </Card>
      )}

      <div>
        <Link to={`/projects/${projectId}`} className="text-sm text-slate-600 underline-offset-4 hover:underline">
          Return to Project Workspace
        </Link>
      </div>
    </main>
  );
}
