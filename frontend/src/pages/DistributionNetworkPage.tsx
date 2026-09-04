import {
  useState,
  type ComponentProps,
  type Dispatch,
  type FormEvent,
  type SetStateAction,
} from "react";

import { useMutation } from "@tanstack/react-query";
import {
  AlertTriangle,
  CheckCircle2,
  GitBranch,
  Network,
  Play,
  Plus,
  RotateCcw,
  Route,
  Save,
  Trash2,
  Waves,
  Wind,
} from "lucide-react";
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
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

import { useAuth } from "../features/auth/AuthProvider";
import { executeDistributionCalculation } from "../features/projects/distributionService";
import type {
  DistributionExecutionResponse,
  EngineeringNumber,
  NetworkNodeType,
  NetworkPathResult,
  NetworkTopology,
  PipeSegmentRole,
  VelocityScreeningStatus,
} from "../features/projects/distributionTypes";
import { useProjectContext } from "../features/projects/useProjectContext";
import { validateDistributionPressures } from "../features/projects/distributionValidation";
import { ApiError } from "../services/apiClient";

// Velocity screening bands mirrored from the backend calibration.
// CAGI Pressure Drop technical brief: keep piping velocity <= 20 ft/s
// (~6 m/s). BCAS: design mains at 6-7 m/s, never exceed 9 m/s.
// Standards registry: CAGI-CAGH, BCAS-BPG-101.
const VELOCITY_RECOMMENDED_LIMIT_M_PER_S = 6;
const VELOCITY_ABSOLUTE_LIMIT_M_PER_S = 9;

const VELOCITY_BAND_TOOLTIP =
  "CAGI recommends <= 6 m/s; BCAS design band 6-7 m/s, never above 9 m/s " +
  "(standards registry: CAGI-CAGH, BCAS-BPG-101)";

const TOPOLOGY_OPTIONS: { value: NetworkTopology; label: string }[] = [
  { value: "DEAD_END", label: "Dead End" },
  { value: "BRANCHED", label: "Branched" },
  { value: "RING_MAIN", label: "Ring Main" },
  { value: "MULTIPLE_RING", label: "Multiple Ring" },
  { value: "HYBRID", label: "Hybrid" },
];

const NODE_TYPE_OPTIONS: { value: NetworkNodeType; label: string }[] = [
  { value: "COMPRESSOR_STATION", label: "Compressor Station" },
  { value: "RECEIVER", label: "Receiver" },
  { value: "HEADER_JUNCTION", label: "Header Junction" },
  { value: "BRANCH_JUNCTION", label: "Branch Junction" },
  { value: "CONSUMER", label: "Consumer" },
  { value: "RING_CONNECTION", label: "Ring Connection" },
];

const SEGMENT_ROLE_OPTIONS: { value: PipeSegmentRole; label: string }[] = [
  { value: "MAIN_HEADER", label: "Main Header" },
  { value: "RING_MAIN", label: "Ring Main" },
  { value: "SUB_HEADER", label: "Sub Header" },
  { value: "BRANCH", label: "Branch" },
  { value: "DROP_LEG", label: "Drop Leg" },
  { value: "EQUIPMENT_CONNECTION", label: "Equipment Connection" },
];

const SELECT_CLASS_NAME =
  "h-9 w-full rounded-md border border-slate-200 bg-white px-3 text-sm " +
  "shadow-sm outline-none transition focus-visible:border-slate-400 " +
  "focus-visible:ring-2 focus-visible:ring-slate-200";

type NodeFormState = {
  rowId: string;
  nodeCode: string;
  name: string;
  nodeType: NetworkNodeType;
  elevation: string;
  demand: string;
  minimumPressure: string;
};

type SegmentFormState = {
  rowId: string;
  segmentCode: string;
  name: string;
  role: PipeSegmentRole;
  startNodeCode: string;
  endNodeCode: string;
  length: string;
  fittingLength: string;
  internalDiameter: string;
  roughness: string;
  designFlow: string;
  operatingPressure: string;
  operatingTemperature: string;
};

type PathFormState = {
  rowId: string;
  pathCode: string;
  nodeCodesCsv: string;
  segmentCodesCsv: string;
};

function makeRowId(): string {
  return crypto.randomUUID();
}

function makeDefaultNodes(): NodeFormState[] {
  return [
    {
      rowId: makeRowId(),
      nodeCode: "N1",
      name: "Compressor Station",
      nodeType: "COMPRESSOR_STATION",
      elevation: "0",
      demand: "0",
      minimumPressure: "",
    },
    {
      rowId: makeRowId(),
      nodeCode: "N2",
      name: "Production Consumer",
      nodeType: "CONSUMER",
      elevation: "0",
      demand: "600",
      minimumPressure: "6.0",
    },
  ];
}

function makeDefaultSegments(): SegmentFormState[] {
  return [
    {
      rowId: makeRowId(),
      segmentCode: "S1",
      name: "Main Header",
      role: "MAIN_HEADER",
      startNodeCode: "N1",
      endNodeCode: "N2",
      length: "80",
      fittingLength: "20",
      internalDiameter: "80",
      roughness: "0.045",
      designFlow: "600",
      operatingPressure: "7.0",
      operatingTemperature: "303.15",
    },
  ];
}

function makeDefaultPaths(): PathFormState[] {
  return [
    {
      rowId: makeRowId(),
      pathCode: "P1",
      nodeCodesCsv: "N1, N2",
      segmentCodesCsv: "S1",
    },
  ];
}

type EngineeringInputProps = Omit<ComponentProps<typeof Input>, "id"> & {
  id: string;
  label: string;
  unit?: string;
};

function EngineeringInput({
  id,
  label,
  unit,
  ...inputProps
}: EngineeringInputProps) {
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between gap-3">
        <Label htmlFor={id}>{label}</Label>

        {unit && (
          <span className="text-xs font-medium text-slate-500">{unit}</span>
        )}
      </div>

      <Input
        id={id}
        {...inputProps}
      />
    </div>
  );
}

type ResultMetricProps = {
  label: string;
  value: string;
  description?: string;
};

function ResultMetric({ label, value, description }: ResultMetricProps) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4">
      <dt className="text-xs font-medium uppercase tracking-wide text-slate-500">
        {label}
      </dt>

      <dd className="mt-2 break-words text-xl font-semibold text-slate-950">
        {value}
      </dd>

      {description && (
        <p className="mt-2 text-xs leading-5 text-slate-600">{description}</p>
      )}
    </div>
  );
}

function formatEngineeringNumber(
  value: EngineeringNumber,
  maximumFractionDigits = 3,
): string {
  const numericValue = Number(value);

  if (!Number.isFinite(numericValue)) {
    return String(value);
  }

  return numericValue.toLocaleString("en-IN", {
    maximumFractionDigits,
  });
}

function classifyVelocity(value: EngineeringNumber): VelocityScreeningStatus {
  const numericValue = Number(value);

  if (numericValue <= VELOCITY_RECOMMENDED_LIMIT_M_PER_S) {
    return "RECOMMENDED";
  }

  if (numericValue <= VELOCITY_ABSOLUTE_LIMIT_M_PER_S) {
    return "CAUTION";
  }

  return "EXCESSIVE";
}

const VELOCITY_BAND_CLASS_NAMES: Record<VelocityScreeningStatus, string> = {
  RECOMMENDED: "border-emerald-200 bg-emerald-50 text-emerald-700",
  CAUTION: "border-amber-200 bg-amber-50 text-amber-700",
  EXCESSIVE: "border-red-200 bg-red-50 text-red-700",
};

function VelocityBandBadge({ value }: { value: EngineeringNumber }) {
  const status = classifyVelocity(value);

  return (
    <span
      title={VELOCITY_BAND_TOOLTIP}
      className={
        "inline-flex items-center rounded-full border px-2 py-0.5 " +
        "text-xs font-semibold " +
        VELOCITY_BAND_CLASS_NAMES[status]
      }
    >
      {status}
    </span>
  );
}

function parseCsvCodes(value: string): string[] {
  return value
    .split(",")
    .map((code) => code.trim())
    .filter((code) => code.length > 0);
}

function parseCsvNumbers(value: string): number[] {
  return parseCsvCodes(value).map((entry) => Number(entry));
}

function isPositiveNumber(value: string): boolean {
  const numericValue = Number(value);

  return Number.isFinite(numericValue) && numericValue > 0;
}

function isNonNegativeNumber(value: string): boolean {
  const numericValue = Number(value);

  return Number.isFinite(numericValue) && numericValue >= 0;
}

function isFiniteNumber(value: string): boolean {
  return Number.isFinite(Number(value));
}

function getCalculationErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    if (
      typeof error.details === "object" &&
      error.details !== null &&
      "detail" in error.details &&
      typeof error.details.detail === "string"
    ) {
      return error.details.detail;
    }

    return `The distribution network service returned HTTP ${error.status}.`;
  }

  if (error instanceof Error) {
    return error.message;
  }

  return "The distribution network analysis could not be completed.";
}

export function DistributionNetworkPage() {
  const { accessToken } = useAuth();
  const { projectId, hasValidProjectId, project, projectQuery } =
    useProjectContext();

  const [networkCode, setNetworkCode] = useState("NET-1");
  const [topology, setTopology] = useState<NetworkTopology>("DEAD_END");
  const [designSourcePressure, setDesignSourcePressure] = useState("7.0");
  const [airDensity, setAirDensity] = useState("9.2");
  const [darcyFrictionFactor, setDarcyFrictionFactor] = useState("0.02");
  const [description, setDescription] = useState("");

  const [nodes, setNodes] = useState<NodeFormState[]>(makeDefaultNodes);
  const [segments, setSegments] = useState<SegmentFormState[]>(
    makeDefaultSegments,
  );
  const [paths, setPaths] = useState<PathFormState[]>(makeDefaultPaths);

  const [includeOptimization, setIncludeOptimization] = useState(false);
  const [candidateDiametersCsv, setCandidateDiametersCsv] = useState(
    "50, 65, 80, 100, 125, 150",
  );
  const [maximumPreferredVelocity, setMaximumPreferredVelocity] = useState(
    String(VELOCITY_RECOMMENDED_LIMIT_M_PER_S),
  );
  const [minimumReductionFraction, setMinimumReductionFraction] =
    useState("0.20");

  const [persistResult, setPersistResult] = useState(false);
  const [calculationCode, setCalculationCode] = useState("");
  const [title, setTitle] = useState("Distribution Network Analysis");
  const [engineeringNotes, setEngineeringNotes] = useState("");

  const [result, setResult] =
    useState<DistributionExecutionResponse | null>(null);

  const networkBasisIsValid =
    networkCode.trim().length > 0 &&
    isNonNegativeNumber(designSourcePressure) &&
    isPositiveNumber(airDensity) &&
    isPositiveNumber(darcyFrictionFactor) &&
    Number(darcyFrictionFactor) < 1;

  const nodesAreValid =
    nodes.length > 0 &&
    nodes.every(
      (node) =>
        node.nodeCode.trim().length > 0 &&
        node.name.trim().length > 0 &&
        isFiniteNumber(node.elevation) &&
        isNonNegativeNumber(node.demand) &&
        (node.minimumPressure.trim().length === 0 ||
          isNonNegativeNumber(node.minimumPressure)),
    );

  const segmentsAreValid =
    segments.length > 0 &&
    segments.every(
      (segment) =>
        segment.segmentCode.trim().length > 0 &&
        segment.name.trim().length > 0 &&
        segment.startNodeCode.trim().length > 0 &&
        segment.endNodeCode.trim().length > 0 &&
        isPositiveNumber(segment.length) &&
        isNonNegativeNumber(segment.fittingLength) &&
        isPositiveNumber(segment.internalDiameter) &&
        isNonNegativeNumber(segment.roughness) &&
        isPositiveNumber(segment.designFlow) &&
        isNonNegativeNumber(segment.operatingPressure) &&
        isPositiveNumber(segment.operatingTemperature),
    );

  const pathsAreValid =
    paths.length > 0 &&
    paths.every(
      (path) =>
        path.pathCode.trim().length > 0 &&
        parseCsvCodes(path.nodeCodesCsv).length >= 2 &&
        parseCsvCodes(path.segmentCodesCsv).length >= 1,
    );

  const candidateDiameters = parseCsvNumbers(candidateDiametersCsv);

  const optimizationIsValid =
    !includeOptimization ||
    (candidateDiameters.length > 0 &&
      candidateDiameters.every(
        (diameter) => Number.isFinite(diameter) && diameter > 0,
      ) &&
      isPositiveNumber(maximumPreferredVelocity) &&
      isPositiveNumber(minimumReductionFraction) &&
      Number(minimumReductionFraction) < 1);

  const persistenceIsValid =
    !persistResult ||
    (calculationCode.trim().length > 0 && title.trim().length > 0);

  const pressureErrors = validateDistributionPressures({
    designSourcePressure,
    nodes,
    segments,
  });
  const canSubmit =
    networkBasisIsValid &&
    nodesAreValid &&
    segmentsAreValid &&
    pathsAreValid &&
    optimizationIsValid &&
    persistenceIsValid &&
    pressureErrors.length === 0;

  const calculationMutation = useMutation({
    mutationFn: () => {
      if (!accessToken) {
        throw new Error("Authenticated access token is required.");
      }

      return executeDistributionCalculation(accessToken, {
        calculation: {
          network_code: networkCode.trim(),
          topology,
          nodes: nodes.map((node) => ({
            node_code: node.nodeCode.trim(),
            name: node.name.trim(),
            node_type: node.nodeType,
            elevation_m: Number(node.elevation),
            demand_nm3_per_hr: Number(node.demand),
            minimum_pressure_bar_g:
              node.minimumPressure.trim().length > 0
                ? Number(node.minimumPressure)
                : null,
          })),
          segments: segments.map((segment) => ({
            segment_code: segment.segmentCode.trim(),
            name: segment.name.trim(),
            role: segment.role,
            start_node_code: segment.startNodeCode.trim(),
            end_node_code: segment.endNodeCode.trim(),
            length_m: Number(segment.length),
            equivalent_fitting_length_m: Number(segment.fittingLength),
            internal_diameter_mm: Number(segment.internalDiameter),
            roughness_mm: Number(segment.roughness),
            design_flow_nm3_per_hr: Number(segment.designFlow),
            operating_pressure_bar_g: Number(segment.operatingPressure),
            operating_temperature_k: Number(segment.operatingTemperature),
          })),
          paths: paths.map((path) => ({
            path_code: path.pathCode.trim(),
            node_codes: parseCsvCodes(path.nodeCodesCsv),
            segment_codes: parseCsvCodes(path.segmentCodesCsv),
          })),
          design_source_pressure_bar_g: Number(designSourcePressure),
          air_density_kg_per_m3: Number(airDensity),
          darcy_friction_factor: Number(darcyFrictionFactor),
          candidate_internal_diameters_mm: includeOptimization
            ? candidateDiameters
            : null,
          maximum_preferred_velocity_m_per_s: includeOptimization
            ? Number(maximumPreferredVelocity)
            : undefined,
          minimum_pressure_drop_reduction_fraction: includeOptimization
            ? Number(minimumReductionFraction)
            : undefined,
          description:
            description.trim().length > 0 ? description.trim() : null,
        },
        execution: {
          persist_result: persistResult,
          project_id: persistResult ? projectId : null,
          calculation_code: persistResult ? calculationCode.trim() : null,
          title: persistResult ? title.trim() : null,
          engineering_notes:
            persistResult && engineeringNotes.trim()
              ? engineeringNotes.trim()
              : null,
        },
      });
    },
    onSuccess: (response) => {
      setResult(response);
    },
  });

  if (!accessToken) {
    throw new Error("Authenticated access token is required.");
  }

  if (!hasValidProjectId) {
    throw new Error("Valid project ID is required.");
  }

  function clearPreviousResult(): void {
    setResult(null);
    calculationMutation.reset();
  }

  function updateInput(
    setter: Dispatch<SetStateAction<string>>,
    value: string,
  ): void {
    setter(value);
    clearPreviousResult();
  }

  function updateBoolean(
    setter: Dispatch<SetStateAction<boolean>>,
    value: boolean,
  ): void {
    setter(value);
    clearPreviousResult();
  }

  function updateNode(
    rowId: string,
    field: keyof Omit<NodeFormState, "rowId">,
    value: string,
  ): void {
    setNodes((previous) =>
      previous.map((node) =>
        node.rowId === rowId ? { ...node, [field]: value } : node,
      ),
    );
    clearPreviousResult();
  }

  function addNode(): void {
    setNodes((previous) => [
      ...previous,
      {
        rowId: makeRowId(),
        nodeCode: `N${previous.length + 1}`,
        name: "",
        nodeType: "CONSUMER",
        elevation: "0",
        demand: "0",
        minimumPressure: "",
      },
    ]);
    clearPreviousResult();
  }

  function removeNode(rowId: string): void {
    setNodes((previous) => previous.filter((node) => node.rowId !== rowId));
    clearPreviousResult();
  }

  function updateSegment(
    rowId: string,
    field: keyof Omit<SegmentFormState, "rowId">,
    value: string,
  ): void {
    setSegments((previous) =>
      previous.map((segment) =>
        segment.rowId === rowId ? { ...segment, [field]: value } : segment,
      ),
    );
    clearPreviousResult();
  }

  function addSegment(): void {
    setSegments((previous) => [
      ...previous,
      {
        rowId: makeRowId(),
        segmentCode: `S${previous.length + 1}`,
        name: "",
        role: "BRANCH",
        startNodeCode: "",
        endNodeCode: "",
        length: "20",
        fittingLength: "5",
        internalDiameter: "50",
        roughness: "0.045",
        designFlow: "100",
        operatingPressure: "7.0",
        operatingTemperature: "303.15",
      },
    ]);
    clearPreviousResult();
  }

  function removeSegment(rowId: string): void {
    setSegments((previous) =>
      previous.filter((segment) => segment.rowId !== rowId),
    );
    clearPreviousResult();
  }

  function updatePath(
    rowId: string,
    field: keyof Omit<PathFormState, "rowId">,
    value: string,
  ): void {
    setPaths((previous) =>
      previous.map((path) =>
        path.rowId === rowId ? { ...path, [field]: value } : path,
      ),
    );
    clearPreviousResult();
  }

  function addPath(): void {
    setPaths((previous) => [
      ...previous,
      {
        rowId: makeRowId(),
        pathCode: `P${previous.length + 1}`,
        nodeCodesCsv: "",
        segmentCodesCsv: "",
      },
    ]);
    clearPreviousResult();
  }

  function removePath(rowId: string): void {
    setPaths((previous) => previous.filter((path) => path.rowId !== rowId));
    clearPreviousResult();
  }

  function handleReset(): void {
    setNetworkCode("NET-1");
    setTopology("DEAD_END");
    setDesignSourcePressure("7.0");
    setAirDensity("9.2");
    setDarcyFrictionFactor("0.02");
    setDescription("");
    setNodes(makeDefaultNodes());
    setSegments(makeDefaultSegments());
    setPaths(makeDefaultPaths());
    setIncludeOptimization(false);
    setCandidateDiametersCsv("50, 65, 80, 100, 125, 150");
    setMaximumPreferredVelocity(String(VELOCITY_RECOMMENDED_LIMIT_M_PER_S));
    setMinimumReductionFraction("0.20");
    setPersistResult(false);
    setCalculationCode("");
    setTitle("Distribution Network Analysis");
    setEngineeringNotes("");
    clearPreviousResult();
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>): void {
    event.preventDefault();

    if (!canSubmit) {
      return;
    }

    setResult(null);
    calculationMutation.mutate();
  }

  const analysis = result?.result ?? null;

  return (
    <main className="mx-auto w-full max-w-7xl space-y-6 pb-12">
      <Card className="bg-white">
        <CardHeader>
          <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
            <div className="space-y-3">
              <Badge variant="outline">Distribution Network Engineering</Badge>

              <div>
                <h1 className="text-3xl font-bold tracking-tight text-slate-950">
                  Distribution Network Engineering
                </h1>

                <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
                  Model the compressed-air pipe network as nodes, segments and
                  flow paths; validate the structure, solve Darcy-Weisbach
                  path hydraulics against minimum consumer pressures, and
                  optionally optimize deficient paths against your actual pipe
                  schedule.
                </p>
              </div>

              <div className="flex flex-wrap items-center gap-2 text-xs">
                <span className="font-semibold text-slate-900">
                  {project
                    ? `${project.project_code} · ${project.project_name}`
                    : projectQuery.isPending
                      ? "Loading project..."
                      : `Project ${projectId}`}
                </span>

                {project && <Badge variant="outline">{project.status}</Badge>}

                <Badge variant="outline">Vendor Neutral</Badge>
                <Badge variant="outline">CAGI / BCAS Calibrated</Badge>
                <Badge variant="outline">Darcy-Weisbach</Badge>
              </div>
            </div>

            <div className="flex flex-wrap gap-2">
              <Button
                asChild
                variant="outline"
              >
                <Link to={`/projects/${projectId}/compressor`}>
                  <Wind className="size-4" />
                  Advanced Engineering
                </Link>
              </Button>

              <Button
                type="button"
                variant="outline"
                onClick={handleReset}
                disabled={calculationMutation.isPending}
              >
                <RotateCcw className="size-4" />
                Reset
              </Button>

              <Button
                type="submit"
                form="distribution-network-form"
                disabled={!canSubmit}
              >
                <Play className="size-4" />
                {calculationMutation.isPending
                  ? "Analyzing..."
                  : "Run Analysis"}
              </Button>
            </div>
          </div>
        </CardHeader>
      </Card>

      <form
        id="distribution-network-form"
        className="space-y-6"
        onSubmit={handleSubmit}
      >
        <Card>
          <CardHeader>
            <div className="flex items-start gap-3">
              <Network className="mt-0.5 size-5 shrink-0 text-slate-500" />

              <div>
                <CardTitle>Network Basis</CardTitle>

                <CardDescription className="mt-1 leading-6">
                  Identify the network, its topology, the design pressure at
                  the source, and the hydraulic constants used by the
                  Darcy-Weisbach solver.
                </CardDescription>
              </div>
            </div>
          </CardHeader>

          <CardContent className="space-y-5">
            <fieldset className="grid gap-5 md:grid-cols-2 lg:grid-cols-4">
              <legend className="sr-only">Network basis</legend>

              <EngineeringInput
                id="network-code"
                label="Network Code"
                value={networkCode}
                onChange={(event) =>
                  updateInput(setNetworkCode, event.target.value)
                }
              />

              <div className="space-y-2">
                <Label htmlFor="network-topology">Topology</Label>

                <select
                  id="network-topology"
                  className={SELECT_CLASS_NAME}
                  value={topology}
                  onChange={(event) => {
                    setTopology(event.target.value as NetworkTopology);
                    clearPreviousResult();
                  }}
                >
                  {TOPOLOGY_OPTIONS.map((option) => (
                    <option
                      key={option.value}
                      value={option.value}
                    >
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>

              <EngineeringInput
                id="design-source-pressure"
                label="Design Source Pressure"
                unit="bar g"
                inputMode="decimal"
                value={designSourcePressure}
                onChange={(event) =>
                  updateInput(setDesignSourcePressure, event.target.value)
                }
              />

              <EngineeringInput
                id="air-density"
                label="Air Density at Line Conditions"
                unit="kg/m³"
                inputMode="decimal"
                value={airDensity}
                onChange={(event) =>
                  updateInput(setAirDensity, event.target.value)
                }
              />

              <EngineeringInput
                id="darcy-friction-factor"
                label="Darcy Friction Factor"
                unit="-"
                inputMode="decimal"
                value={darcyFrictionFactor}
                onChange={(event) =>
                  updateInput(setDarcyFrictionFactor, event.target.value)
                }
              />

              <div className="space-y-2 md:col-span-2 lg:col-span-3">
                <Label htmlFor="network-description">
                  Description (optional)
                </Label>
                <Input
                  id="network-description"
                  value={description}
                  onChange={(event) =>
                    updateInput(setDescription, event.target.value)
                  }
                />
              </div>
            </fieldset>

            <p className="text-xs leading-5 text-slate-500">
              Air density defaults to ~9.2 kg/m³ (ideal-gas air at 7 bar g,
              30 °C); adjust for your line pressure and temperature. The
              friction factor default of 0.02 is a commercial-steel
              turbulent-flow estimate -- confirm from a Moody chart or
              Colebrook solution for the actual Reynolds number and relative
              roughness.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-start justify-between gap-3">
              <div className="flex items-start gap-3">
                <GitBranch className="mt-0.5 size-5 shrink-0 text-slate-500" />

                <div>
                  <CardTitle>Network Nodes</CardTitle>

                  <CardDescription className="mt-1 leading-6">
                    Every point where air is produced, stored, branched or
                    consumed. Consumer nodes can declare a minimum required
                    pressure that the solver will verify.
                  </CardDescription>
                </div>
              </div>

              <Button
                type="button"
                variant="outline"
                onClick={addNode}
              >
                <Plus className="size-4" />
                Add Node
              </Button>
            </div>
          </CardHeader>

          <CardContent className="space-y-4">
            {nodes.map((node, index) => (
              <fieldset
                key={node.rowId}
                className="rounded-xl border border-slate-200 bg-slate-50 p-4"
              >
                <legend className="sr-only">{`Node ${index + 1}`}</legend>

                <div className="grid gap-4 md:grid-cols-3 lg:grid-cols-7">
                  <EngineeringInput
                    id={`node-code-${node.rowId}`}
                    label="Code"
                    value={node.nodeCode}
                    onChange={(event) =>
                      updateNode(node.rowId, "nodeCode", event.target.value)
                    }
                  />

                  <EngineeringInput
                    id={`node-name-${node.rowId}`}
                    label="Name"
                    value={node.name}
                    onChange={(event) =>
                      updateNode(node.rowId, "name", event.target.value)
                    }
                  />

                  <div className="space-y-2">
                    <Label htmlFor={`node-type-${node.rowId}`}>Type</Label>

                    <select
                      id={`node-type-${node.rowId}`}
                      className={SELECT_CLASS_NAME}
                      value={node.nodeType}
                      onChange={(event) =>
                        updateNode(node.rowId, "nodeType", event.target.value)
                      }
                    >
                      {NODE_TYPE_OPTIONS.map((option) => (
                        <option
                          key={option.value}
                          value={option.value}
                        >
                          {option.label}
                        </option>
                      ))}
                    </select>
                  </div>

                  <EngineeringInput
                    id={`node-elevation-${node.rowId}`}
                    label="Elevation"
                    unit="m"
                    inputMode="decimal"
                    value={node.elevation}
                    onChange={(event) =>
                      updateNode(node.rowId, "elevation", event.target.value)
                    }
                  />

                  <EngineeringInput
                    id={`node-demand-${node.rowId}`}
                    label="Demand"
                    unit="Nm³/hr"
                    inputMode="decimal"
                    value={node.demand}
                    onChange={(event) =>
                      updateNode(node.rowId, "demand", event.target.value)
                    }
                  />

                  <EngineeringInput
                    id={`node-minimum-pressure-${node.rowId}`}
                    label="Min. Pressure"
                    unit="bar g"
                    inputMode="decimal"
                    placeholder="optional"
                    value={node.minimumPressure}
                    onChange={(event) =>
                      updateNode(
                        node.rowId,
                        "minimumPressure",
                        event.target.value,
                      )
                    }
                  />

                  <div className="flex items-end">
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => removeNode(node.rowId)}
                      disabled={nodes.length <= 1}
                    >
                      <Trash2 className="size-4" />
                      Remove
                    </Button>
                  </div>
                </div>
              </fieldset>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-start justify-between gap-3">
              <div className="flex items-start gap-3">
                <Waves className="mt-0.5 size-5 shrink-0 text-slate-500" />

                <div>
                  <CardTitle>Pipe Segments</CardTitle>

                  <CardDescription className="mt-1 leading-6">
                    Physical pipe runs connecting two nodes. Equivalent
                    fitting length accounts for elbows, valves and tees;
                    roughness defaults to 0.045 mm (commercial steel, Moody
                    chart data).
                  </CardDescription>
                </div>
              </div>

              <Button
                type="button"
                variant="outline"
                onClick={addSegment}
              >
                <Plus className="size-4" />
                Add Segment
              </Button>
            </div>
          </CardHeader>

          <CardContent className="space-y-4">
            {segments.map((segment, index) => (
              <fieldset
                key={segment.rowId}
                className="rounded-xl border border-slate-200 bg-slate-50 p-4"
              >
                <legend className="sr-only">{`Segment ${index + 1}`}</legend>

                <div className="grid gap-4 md:grid-cols-3 lg:grid-cols-6">
                  <EngineeringInput
                    id={`segment-code-${segment.rowId}`}
                    label="Code"
                    value={segment.segmentCode}
                    onChange={(event) =>
                      updateSegment(
                        segment.rowId,
                        "segmentCode",
                        event.target.value,
                      )
                    }
                  />

                  <EngineeringInput
                    id={`segment-name-${segment.rowId}`}
                    label="Name"
                    value={segment.name}
                    onChange={(event) =>
                      updateSegment(segment.rowId, "name", event.target.value)
                    }
                  />

                  <div className="space-y-2">
                    <Label htmlFor={`segment-role-${segment.rowId}`}>
                      Role
                    </Label>

                    <select
                      id={`segment-role-${segment.rowId}`}
                      className={SELECT_CLASS_NAME}
                      value={segment.role}
                      onChange={(event) =>
                        updateSegment(
                          segment.rowId,
                          "role",
                          event.target.value,
                        )
                      }
                    >
                      {SEGMENT_ROLE_OPTIONS.map((option) => (
                        <option
                          key={option.value}
                          value={option.value}
                        >
                          {option.label}
                        </option>
                      ))}
                    </select>
                  </div>

                  <EngineeringInput
                    id={`segment-start-${segment.rowId}`}
                    label="Start Node"
                    value={segment.startNodeCode}
                    onChange={(event) =>
                      updateSegment(
                        segment.rowId,
                        "startNodeCode",
                        event.target.value,
                      )
                    }
                  />

                  <EngineeringInput
                    id={`segment-end-${segment.rowId}`}
                    label="End Node"
                    value={segment.endNodeCode}
                    onChange={(event) =>
                      updateSegment(
                        segment.rowId,
                        "endNodeCode",
                        event.target.value,
                      )
                    }
                  />

                  <EngineeringInput
                    id={`segment-length-${segment.rowId}`}
                    label="Straight Length"
                    unit="m"
                    inputMode="decimal"
                    value={segment.length}
                    onChange={(event) =>
                      updateSegment(
                        segment.rowId,
                        "length",
                        event.target.value,
                      )
                    }
                  />

                  <EngineeringInput
                    id={`segment-fitting-length-${segment.rowId}`}
                    label="Equivalent Fitting Length"
                    unit="m"
                    inputMode="decimal"
                    value={segment.fittingLength}
                    onChange={(event) =>
                      updateSegment(
                        segment.rowId,
                        "fittingLength",
                        event.target.value,
                      )
                    }
                  />

                  <EngineeringInput
                    id={`segment-diameter-${segment.rowId}`}
                    label="Internal Diameter"
                    unit="mm"
                    inputMode="decimal"
                    value={segment.internalDiameter}
                    onChange={(event) =>
                      updateSegment(
                        segment.rowId,
                        "internalDiameter",
                        event.target.value,
                      )
                    }
                  />

                  <EngineeringInput
                    id={`segment-roughness-${segment.rowId}`}
                    label="Roughness"
                    unit="mm"
                    inputMode="decimal"
                    value={segment.roughness}
                    onChange={(event) =>
                      updateSegment(
                        segment.rowId,
                        "roughness",
                        event.target.value,
                      )
                    }
                  />

                  <EngineeringInput
                    id={`segment-design-flow-${segment.rowId}`}
                    label="Design Flow"
                    unit="Nm³/hr"
                    inputMode="decimal"
                    value={segment.designFlow}
                    onChange={(event) =>
                      updateSegment(
                        segment.rowId,
                        "designFlow",
                        event.target.value,
                      )
                    }
                  />

                  <EngineeringInput
                    id={`segment-pressure-${segment.rowId}`}
                    label="Operating Pressure"
                    unit="bar g"
                    inputMode="decimal"
                    value={segment.operatingPressure}
                    onChange={(event) =>
                      updateSegment(
                        segment.rowId,
                        "operatingPressure",
                        event.target.value,
                      )
                    }
                  />

                  <EngineeringInput
                    id={`segment-temperature-${segment.rowId}`}
                    label="Operating Temperature"
                    unit="K"
                    inputMode="decimal"
                    value={segment.operatingTemperature}
                    onChange={(event) =>
                      updateSegment(
                        segment.rowId,
                        "operatingTemperature",
                        event.target.value,
                      )
                    }
                  />

                  <div className="flex items-end">
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => removeSegment(segment.rowId)}
                      disabled={segments.length <= 1}
                    >
                      <Trash2 className="size-4" />
                      Remove
                    </Button>
                  </div>
                </div>
              </fieldset>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-start justify-between gap-3">
              <div className="flex items-start gap-3">
                <Route className="mt-0.5 size-5 shrink-0 text-slate-500" />

                <div>
                  <CardTitle>Flow Paths</CardTitle>

                  <CardDescription className="mt-1 leading-6">
                    Ordered source-to-destination routes through the network.
                    List node codes and segment codes separated by commas, in
                    flow order (a path needs at least two nodes and one
                    segment).
                  </CardDescription>
                </div>
              </div>

              <Button
                type="button"
                variant="outline"
                onClick={addPath}
              >
                <Plus className="size-4" />
                Add Path
              </Button>
            </div>
          </CardHeader>

          <CardContent className="space-y-4">
            {paths.map((path, index) => (
              <fieldset
                key={path.rowId}
                className="rounded-xl border border-slate-200 bg-slate-50 p-4"
              >
                <legend className="sr-only">{`Path ${index + 1}`}</legend>

                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                  <EngineeringInput
                    id={`path-code-${path.rowId}`}
                    label="Path Code"
                    value={path.pathCode}
                    onChange={(event) =>
                      updatePath(path.rowId, "pathCode", event.target.value)
                    }
                  />

                  <EngineeringInput
                    id={`path-nodes-${path.rowId}`}
                    label="Node Codes (in order)"
                    placeholder="N1, N2"
                    value={path.nodeCodesCsv}
                    onChange={(event) =>
                      updatePath(
                        path.rowId,
                        "nodeCodesCsv",
                        event.target.value,
                      )
                    }
                  />

                  <EngineeringInput
                    id={`path-segments-${path.rowId}`}
                    label="Segment Codes (in order)"
                    placeholder="S1"
                    value={path.segmentCodesCsv}
                    onChange={(event) =>
                      updatePath(
                        path.rowId,
                        "segmentCodesCsv",
                        event.target.value,
                      )
                    }
                  />

                  <div className="flex items-end">
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => removePath(path.rowId)}
                      disabled={paths.length <= 1}
                    >
                      <Trash2 className="size-4" />
                      Remove
                    </Button>
                  </div>
                </div>
              </fieldset>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-start gap-3">
              <Wind className="mt-0.5 size-5 shrink-0 text-slate-500" />

              <div>
                <CardTitle>Pipe Diameter Optimization</CardTitle>

                <CardDescription className="mt-1 leading-6">
                  When enabled, pressure-deficient paths are re-evaluated
                  against your actual available pipe schedule and upgrade
                  recommendations are produced per segment.
                </CardDescription>
              </div>
            </div>
          </CardHeader>

          <CardContent className="space-y-5">
            <label className="flex cursor-pointer items-start gap-3 rounded-xl border border-slate-200 bg-slate-50 p-4">
              <input
                type="checkbox"
                className="mt-1 size-4 rounded border-slate-300"
                checked={includeOptimization}
                onChange={(event) =>
                  updateBoolean(setIncludeOptimization, event.target.checked)
                }
              />

              <span>
                <span className="block text-sm font-semibold text-slate-950">
                  Optimize Deficient Paths Against a Pipe Schedule
                </span>
                <span className="mt-1 block text-sm leading-6 text-slate-600">
                  Provide the internal diameters actually available to you;
                  the optimizer will only recommend sizes from this list.
                </span>
              </span>
            </label>

            {includeOptimization && (
              <fieldset className="grid gap-5 md:grid-cols-3">
                <legend className="sr-only">Optimization options</legend>

                <EngineeringInput
                  id="candidate-diameters"
                  label="Candidate Internal Diameters"
                  unit="mm, comma separated"
                  value={candidateDiametersCsv}
                  onChange={(event) =>
                    updateInput(setCandidateDiametersCsv, event.target.value)
                  }
                />

                <EngineeringInput
                  id="maximum-preferred-velocity"
                  label="Maximum Preferred Velocity"
                  unit="m/s"
                  inputMode="decimal"
                  value={maximumPreferredVelocity}
                  onChange={(event) =>
                    updateInput(
                      setMaximumPreferredVelocity,
                      event.target.value,
                    )
                  }
                />

                <EngineeringInput
                  id="minimum-reduction-fraction"
                  label="Minimum Pressure-Drop Reduction"
                  unit="fraction"
                  inputMode="decimal"
                  value={minimumReductionFraction}
                  onChange={(event) =>
                    updateInput(
                      setMinimumReductionFraction,
                      event.target.value,
                    )
                  }
                />
              </fieldset>
            )}

            {includeOptimization && (
              <p className="text-xs leading-5 text-slate-500">
                The 6 m/s default preferred velocity follows CAGI (&le; 20
                ft/s) and sits inside the BCAS 6-7 m/s design band with its
                9 m/s never-exceed ceiling (standards registry: CAGI-CAGH,
                BCAS-BPG-101).
              </p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-start gap-3">
              <Save className="mt-0.5 size-5 shrink-0 text-slate-500" />

              <div>
                <CardTitle>Result Persistence</CardTitle>

                <CardDescription className="mt-1 leading-6">
                  Optionally store this analysis as a calculation case in the
                  project history for revision tracking and reporting.
                </CardDescription>
              </div>
            </div>
          </CardHeader>

          <CardContent className="space-y-5">
            <label className="flex cursor-pointer items-start gap-3 rounded-xl border border-slate-200 bg-slate-50 p-4">
              <input
                type="checkbox"
                className="mt-1 size-4 rounded border-slate-300"
                checked={persistResult}
                onChange={(event) =>
                  updateBoolean(setPersistResult, event.target.checked)
                }
              />

              <span>
                <span className="block text-sm font-semibold text-slate-950">
                  Persist This Analysis
                </span>
                <span className="mt-1 block text-sm leading-6 text-slate-600">
                  Save the network definition and full result set to the
                  project calculation history.
                </span>
              </span>
            </label>

            {persistResult ? (
              <fieldset className="grid gap-5 md:grid-cols-2">
                <legend className="sr-only">Persistence metadata</legend>

                <EngineeringInput
                  id="calculation-code"
                  label="Calculation Code"
                  value={calculationCode}
                  onChange={(event) =>
                    updateInput(setCalculationCode, event.target.value)
                  }
                />

                <EngineeringInput
                  id="calculation-title"
                  label="Title"
                  value={title}
                  onChange={(event) =>
                    updateInput(setTitle, event.target.value)
                  }
                />

                <div className="space-y-2 md:col-span-2">
                  <Label htmlFor="engineering-notes">Engineering Notes</Label>
                  <textarea
                    id="engineering-notes"
                    className="min-h-28 w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm shadow-sm outline-none transition focus-visible:border-slate-400 focus-visible:ring-2 focus-visible:ring-slate-200"
                    value={engineeringNotes}
                    onChange={(event) =>
                      updateInput(setEngineeringNotes, event.target.value)
                    }
                  />
                </div>
              </fieldset>
            ) : (
              <div className="rounded-xl border border-slate-200 bg-white p-4 text-sm leading-6 text-slate-600">
                The analysis result will be returned for review without
                creating a persistent calculation case.
              </div>
            )}
          </CardContent>
        </Card>
      </form>

      {pressureErrors.length > 0 && (
        <Card className="border-red-200 bg-red-50">
          <CardHeader>
            <div className="flex items-start gap-3">
              <AlertTriangle className="mt-0.5 size-5 shrink-0 text-red-600" />
              <div>
                <CardTitle className="text-red-900">
                  Check Pressure Inputs
                </CardTitle>
                <CardDescription className="mt-1 leading-6 text-red-800">
                  Fix these before running the analysis.
                </CardDescription>
                <ul className="mt-2 list-disc pl-5 text-sm leading-6 text-red-800">
                  {pressureErrors.map((error) => (
                    <li key={error}>{error}</li>
                  ))}
                </ul>
              </div>
            </div>
          </CardHeader>
        </Card>
      )}
      {calculationMutation.isError && (
        <Card className="border-red-200 bg-red-50">
          <CardHeader>
            <div className="flex items-start gap-3">
              <AlertTriangle className="mt-0.5 size-5 shrink-0 text-red-600" />

              <div>
                <CardTitle className="text-red-900">
                  Analysis Failed
                </CardTitle>

                <CardDescription className="mt-1 leading-6 text-red-800">
                  {getCalculationErrorMessage(calculationMutation.error)}
                </CardDescription>
              </div>
            </div>
          </CardHeader>
        </Card>
      )}

      {analysis && (
        <section className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-start gap-3">
                  <CheckCircle2 className="mt-0.5 size-5 shrink-0 text-slate-500" />

                  <div>
                    <CardTitle>Structural Validation</CardTitle>

                    <CardDescription className="mt-1 leading-6">
                      Network integrity checks before any hydraulic solving.
                    </CardDescription>
                  </div>
                </div>

                <Badge
                  variant="outline"
                  className={
                    analysis.validation.is_structurally_valid
                      ? "border-emerald-200 bg-emerald-50 text-emerald-700"
                      : "border-red-200 bg-red-50 text-red-700"
                  }
                >
                  {analysis.validation.is_structurally_valid
                    ? "Structurally Valid"
                    : "Structural Issues"}
                </Badge>
              </div>
            </CardHeader>

            <CardContent>
              <dl className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <ResultMetric
                  label="Nodes"
                  value={String(analysis.validation.node_count)}
                />
                <ResultMetric
                  label="Segments"
                  value={String(analysis.validation.segment_count)}
                />
                <ResultMetric
                  label="Source Nodes"
                  value={String(analysis.validation.source_node_count)}
                />
                <ResultMetric
                  label="Consumer Nodes"
                  value={String(analysis.validation.consumer_node_count)}
                />
              </dl>

              {(analysis.validation.duplicate_node_codes.length > 0 ||
                analysis.validation.duplicate_segment_codes.length > 0 ||
                analysis.validation.orphan_segment_codes.length > 0) && (
                <div className="mt-4 space-y-1 rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm leading-6 text-amber-800">
                  {analysis.validation.duplicate_node_codes.length > 0 && (
                    <p>
                      Duplicate node codes:{" "}
                      {analysis.validation.duplicate_node_codes.join(", ")}
                    </p>
                  )}
                  {analysis.validation.duplicate_segment_codes.length > 0 && (
                    <p>
                      Duplicate segment codes:{" "}
                      {analysis.validation.duplicate_segment_codes.join(", ")}
                    </p>
                  )}
                  {analysis.validation.orphan_segment_codes.length > 0 && (
                    <p>
                      Orphan segments (endpoint not defined):{" "}
                      {analysis.validation.orphan_segment_codes.join(", ")}
                    </p>
                  )}
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-start gap-3">
                  <Waves className="mt-0.5 size-5 shrink-0 text-slate-500" />

                  <div>
                    <CardTitle>Path Hydraulics</CardTitle>

                    <CardDescription className="mt-1 leading-6">
                      Darcy-Weisbach pressure drop per path; velocity bands
                      follow the calibrated CAGI/BCAS screening thresholds.
                    </CardDescription>
                  </div>
                </div>

                <Badge
                  variant="outline"
                  className={
                    analysis.hydraulics.network_pressure_is_adequate
                      ? "border-emerald-200 bg-emerald-50 text-emerald-700"
                      : "border-red-200 bg-red-50 text-red-700"
                  }
                >
                  {analysis.hydraulics.network_pressure_is_adequate
                    ? "Pressure Adequate"
                    : "Pressure Deficient"}
                </Badge>
              </div>
            </CardHeader>

            <CardContent className="space-y-6">
              <dl className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <ResultMetric
                  label="Paths (Adequate / Deficient)"
                  value={`${analysis.hydraulics.total_paths} (${analysis.hydraulics.adequate_paths} / ${analysis.hydraulics.deficient_paths})`}
                />
                <ResultMetric
                  label="Minimum Destination Pressure"
                  value={`${formatEngineeringNumber(
                    analysis.hydraulics.minimum_destination_pressure_bar_g,
                  )} bar g`}
                  description={`Worst path: ${analysis.hydraulics.worst_pressure_path_code}`}
                />
                <ResultMetric
                  label="Maximum Path Pressure Drop"
                  value={`${formatEngineeringNumber(
                    analysis.hydraulics.maximum_path_pressure_drop_bar,
                  )} bar`}
                  description={`Highest-drop path: ${analysis.hydraulics.highest_pressure_drop_path_code}`}
                />
                <ResultMetric
                  label="Deficient Paths"
                  value={
                    analysis.hydraulics.pressure_deficient_path_codes.length >
                    0
                      ? analysis.hydraulics.pressure_deficient_path_codes.join(
                          ", ",
                        )
                      : "None"
                  }
                />
              </dl>

              {analysis.hydraulics.path_results.map(
                (pathResult: NetworkPathResult) => (
                  <div
                    key={pathResult.path_code}
                    className="rounded-xl border border-slate-200 bg-white p-4"
                  >
                    <div className="flex flex-wrap items-center justify-between gap-3">
                      <div className="text-sm font-semibold text-slate-950">
                        {pathResult.path_code}{" "}
                        <span className="font-normal text-slate-500">
                          {pathResult.source_node_code} →{" "}
                          {pathResult.destination_node_code}
                        </span>
                      </div>

                      <div className="flex flex-wrap items-center gap-2 text-xs">
                        <span className="text-slate-600">
                          ΔP{" "}
                          {formatEngineeringNumber(
                            pathResult.total_pressure_drop_bar,
                          )}{" "}
                          bar
                        </span>

                        <span className="text-slate-600">
                          Destination{" "}
                          {formatEngineeringNumber(
                            pathResult.destination_pressure_bar_g,
                          )}{" "}
                          bar g
                        </span>

                        {pathResult.destination_pressure_is_adequate !==
                          null && (
                          <Badge
                            variant="outline"
                            className={
                              pathResult.destination_pressure_is_adequate
                                ? "border-emerald-200 bg-emerald-50 text-emerald-700"
                                : "border-red-200 bg-red-50 text-red-700"
                            }
                          >
                            {pathResult.destination_pressure_is_adequate
                              ? "Adequate"
                              : "Deficient"}
                          </Badge>
                        )}
                      </div>
                    </div>

                    <div className="mt-3 overflow-x-auto">
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead>Segment</TableHead>
                            <TableHead>From → To</TableHead>
                            <TableHead className="text-right">
                              Flow (Nm³/hr)
                            </TableHead>
                            <TableHead className="text-right">
                              Equivalent Length (m)
                            </TableHead>
                            <TableHead className="text-right">
                              Velocity (m/s)
                            </TableHead>
                            <TableHead>Band</TableHead>
                            <TableHead className="text-right">
                              ΔP (bar)
                            </TableHead>
                          </TableRow>
                        </TableHeader>

                        <TableBody>
                          {pathResult.segment_results.map((segmentResult) => (
                            <TableRow key={segmentResult.segment_code}>
                              <TableCell className="font-medium">
                                {segmentResult.segment_code}
                              </TableCell>
                              <TableCell>
                                {segmentResult.start_node_code} →{" "}
                                {segmentResult.end_node_code}
                              </TableCell>
                              <TableCell className="text-right">
                                {formatEngineeringNumber(
                                  segmentResult.design_flow_nm3_per_hr,
                                )}
                              </TableCell>
                              <TableCell className="text-right">
                                {formatEngineeringNumber(
                                  segmentResult.total_equivalent_length_m,
                                )}
                              </TableCell>
                              <TableCell className="text-right">
                                {formatEngineeringNumber(
                                  segmentResult.velocity_m_per_s,
                                )}
                              </TableCell>
                              <TableCell>
                                <VelocityBandBadge
                                  value={segmentResult.velocity_m_per_s}
                                />
                              </TableCell>
                              <TableCell className="text-right">
                                {formatEngineeringNumber(
                                  segmentResult.pressure_drop_bar,
                                  4,
                                )}
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </div>
                  </div>
                ),
              )}
            </CardContent>
          </Card>

          {analysis.optimization && (
            <Card>
              <CardHeader>
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-start gap-3">
                    <Wind className="mt-0.5 size-5 shrink-0 text-slate-500" />

                    <div>
                      <CardTitle>Optimization Recommendations</CardTitle>

                      <CardDescription className="mt-1 leading-6">
                        Segment upgrades selected from your candidate pipe
                        schedule for pressure-deficient paths.
                      </CardDescription>
                    </div>
                  </div>

                  <Badge
                    variant="outline"
                    className={
                      analysis.optimization.optimization_required
                        ? "border-amber-200 bg-amber-50 text-amber-700"
                        : "border-emerald-200 bg-emerald-50 text-emerald-700"
                    }
                  >
                    {analysis.optimization.optimization_required
                      ? "Upgrades Recommended"
                      : "No Upgrade Required"}
                  </Badge>
                </div>
              </CardHeader>

              <CardContent className="space-y-4">
                <dl className="grid gap-4 md:grid-cols-3">
                  <ResultMetric
                    label="Deficient Paths"
                    value={
                      analysis.optimization.deficient_path_codes.length > 0
                        ? analysis.optimization.deficient_path_codes.join(
                            ", ",
                          )
                        : "None"
                    }
                  />
                  <ResultMetric
                    label="Target Segment Drop (Current)"
                    value={`${formatEngineeringNumber(
                      analysis.optimization
                        .total_current_target_segment_drop_bar,
                      4,
                    )} bar`}
                  />
                  <ResultMetric
                    label="Estimated Drop Reduction"
                    value={`${formatEngineeringNumber(
                      analysis.optimization
                        .estimated_total_pressure_drop_reduction_bar,
                      4,
                    )} bar`}
                  />
                </dl>

                {analysis.optimization.recommendations.length > 0 && (
                  <div className="overflow-x-auto">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Segment</TableHead>
                          <TableHead className="text-right">
                            Diameter (mm)
                          </TableHead>
                          <TableHead className="text-right">
                            Velocity (m/s)
                          </TableHead>
                          <TableHead>Band</TableHead>
                          <TableHead className="text-right">
                            ΔP Reduction (bar)
                          </TableHead>
                          <TableHead>Status</TableHead>
                          <TableHead>Rationale</TableHead>
                        </TableRow>
                      </TableHeader>

                      <TableBody>
                        {analysis.optimization.recommendations.map(
                          (recommendation) => (
                            <TableRow key={recommendation.segment_code}>
                              <TableCell className="font-medium">
                                {recommendation.segment_code}
                                <span className="block text-xs font-normal text-slate-500">
                                  {recommendation.segment_name}
                                </span>
                              </TableCell>
                              <TableCell className="text-right">
                                {formatEngineeringNumber(
                                  recommendation.current_internal_diameter_mm,
                                )}{" "}
                                →{" "}
                                {formatEngineeringNumber(
                                  recommendation.recommended_internal_diameter_mm,
                                )}
                              </TableCell>
                              <TableCell className="text-right">
                                {formatEngineeringNumber(
                                  recommendation.current_velocity_m_per_s,
                                )}{" "}
                                →{" "}
                                {formatEngineeringNumber(
                                  recommendation.recommended_velocity_m_per_s,
                                )}
                              </TableCell>
                              <TableCell>
                                <VelocityBandBadge
                                  value={
                                    recommendation.recommended_velocity_m_per_s
                                  }
                                />
                              </TableCell>
                              <TableCell className="text-right">
                                {formatEngineeringNumber(
                                  recommendation.pressure_drop_reduction_bar,
                                  4,
                                )}
                              </TableCell>
                              <TableCell>
                                {recommendation.recommendation_status}
                              </TableCell>
                              <TableCell className="max-w-xs text-xs leading-5 text-slate-600">
                                {recommendation.rationale.join(" ")}
                              </TableCell>
                            </TableRow>
                          ),
                        )}
                      </TableBody>
                    </Table>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {result && result.calculation_case_id !== null && (
            <Card className="border-emerald-200 bg-emerald-50">
              <CardHeader>
                <div className="flex items-start gap-3">
                  <CheckCircle2 className="mt-0.5 size-5 shrink-0 text-emerald-600" />

                  <div>
                    <CardTitle className="text-emerald-900">
                      Calculation Case Saved
                    </CardTitle>

                    <CardDescription className="mt-1 leading-6 text-emerald-800">
                      This analysis was persisted as calculation case #
                      {result.calculation_case_id} in the project history.
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
            </Card>
          )}
        </section>
      )}
    </main>
  );
}
