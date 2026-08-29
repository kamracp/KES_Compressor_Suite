import {
  AlertTriangle,
  ArrowRight,
  Calculator,
  CheckCircle2,
  ClipboardCheck,
  Factory,
  FileText,
  Gauge,
  History,
  Package,
  Search,
  ShieldCheck,
  Wind,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
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

import { useProjectContext } from "../features/projects/useProjectContext";

type EngineeringWorkflow = {
  title: string;
  phase: string;
  description: string;
  icon: LucideIcon;
  path: string;
  actionLabel: string;
  secondaryPath?: string;
  secondaryLabel?: string;
};

type GovernanceWorkspace = {
  title: string;
  description: string;
  icon: LucideIcon;
  path: string;
  actionLabel: string;
};

function getStatusClassName(status: string): string {
  switch (status.trim().toUpperCase()) {
    case "ACTIVE":
      return "border-emerald-300/40 bg-emerald-400/10 text-emerald-100";
    case "COMPLETED":
      return "border-sky-300/40 bg-sky-400/10 text-sky-100";
    case "DRAFT":
      return "border-amber-300/40 bg-amber-400/10 text-amber-100";
    default:
      return "border-white/15 bg-white/10 text-slate-200";
  }
}

export function ProjectWorkspacePage() {
  const { projectId, hasValidProjectId, project } = useProjectContext();

  if (!hasValidProjectId) {
    throw new Error("Valid project ID is required.");
  }

  if (!project) {
    throw new Error("Authenticated project context is required.");
  }

  const workflows: EngineeringWorkflow[] = [
    {
      title: "New System Design",
      phase: "System Planning",
      description:
        "Design a new factory compressed-air system from consumer demand through pressure, station capacity, treatment, storage, energy, and engineering review.",
      icon: Factory,
      path: `/projects/${projectId}/greenfield`,
      actionLabel: "Open New System Design",
    },
    {
      title: "Existing Plant Assessment",
      phase: "Plant Assessment",
      description:
        "Assess an existing compressor station, operating profile, system condition, capacity utilization, losses, controls, and improvement opportunities.",
      icon: Search,
      path: `/projects/${projectId}/brownfield`,
      actionLabel: "Open Plant Assessment",
    },
    {
      title: "Performance & Energy Analysis",
      phase: "Energy Performance",
      description:
        "Evaluate compressor and system specific power, operating efficiency, energy consumption, cost, deviation, and improvement potential.",
      icon: Gauge,
      path: `/projects/${projectId}/performance`,
      actionLabel: "Open Performance Analysis",
    },
    {
      title: "Leakage Management",
      phase: "Loss Management",
      description:
        "Quantify compressed-air leakage, energy loss, annual cost, repair priority, and verified post-repair savings.",
      icon: AlertTriangle,
      path: `/projects/${projectId}/leakage`,
      actionLabel: "Open Leakage Management",
    },
    {
      title: "Allied Equipment Engineering",
      phase: "Air Treatment & Storage",
      description:
        "Engineer receivers, storage, dryers, treatment, aftercoolers, moisture separators, filters, condensate drains, and allied-equipment pressure losses.",
      icon: Package,
      path: `/projects/${projectId}/allied-equipment`,
      actionLabel: "Open Allied Equipment",
      secondaryPath: `/projects/${projectId}/skid`,
      secondaryLabel: "Open Skid Engineering",
    },
    {
      title: "Advanced Compressor Engineering",
      phase: "Specialist Calculations",
      description:
        "Open gas-property, technology-selection, compression, reciprocating, centrifugal, and saved-calculation workflows.",
      icon: Calculator,
      path: `/projects/${projectId}/compressor`,
      actionLabel: "Open Compressor Engineering",
    },
  ];

  const governanceWorkspaces: GovernanceWorkspace[] = [
    {
      title: "Calculation Records",
      description:
        "Review saved engineering calculations, revisions, results, and engineering notes for this project.",
      icon: History,
      path: `/projects/${projectId}/calculations`,
      actionLabel: "Open Calculation Records",
    },
    {
      title: "Assessments",
      description:
        "Review structured assessment records and organization-authorized engineering observations.",
      icon: ClipboardCheck,
      path: "/assessments",
      actionLabel: "Open Assessments",
    },
    {
      title: "Reports",
      description:
        "Open the controlled report workspace for engineering presentation and authorized outputs.",
      icon: FileText,
      path: "/reports",
      actionLabel: "Open Reports",
    },
  ];

  return (
    <main className="space-y-8">
      <section
        aria-labelledby="project-workspace-title"
        className="overflow-hidden rounded-2xl bg-slate-950 text-white shadow-sm"
      >
        <div className="grid gap-8 p-6 sm:p-8 lg:grid-cols-[minmax(0,1fr)_auto] lg:items-end">
          <div className="max-w-3xl">
            <div className="flex flex-wrap items-center gap-2">
              <Badge className="border-sky-400/30 bg-sky-400/10 text-sky-100 hover:bg-sky-400/10">
                Project Engineering Workspace
              </Badge>

              <Badge
                variant="outline"
                className={getStatusClassName(project.status)}
              >
                {project.status}
              </Badge>
            </div>

            <p className="mt-5 font-mono text-xs font-semibold uppercase tracking-[0.18em] text-sky-300">
              {project.project_code}
            </p>

            <h1
              id="project-workspace-title"
              className="mt-2 text-3xl font-bold tracking-tight sm:text-4xl"
            >
              {project.project_name}
            </h1>

            <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-300 sm:text-base">
              {project.service_description ??
                "Select the engineering workflow required for this project. Calculations, assessments, revisions, and reports remain linked to the authenticated project context."}
            </p>
          </div>

          <Button asChild variant="secondary" className="w-full sm:w-auto">
            <Link to="/projects">
              Return to Projects
              <ArrowRight aria-hidden="true" className="ml-2 size-4" />
            </Link>
          </Button>
        </div>

        <div className="grid border-t border-white/10 bg-slate-900/70 sm:grid-cols-2 lg:grid-cols-4">
          <div className="border-b border-white/10 px-6 py-4 sm:border-r lg:border-b-0">
            <p className="text-xs uppercase tracking-wide text-slate-400">
              Client
            </p>
            <p className="mt-1 truncate text-sm font-medium text-slate-100">
              {project.client_name ?? "Not specified"}
            </p>
          </div>

          <div className="border-b border-white/10 px-6 py-4 lg:border-b-0 lg:border-r">
            <p className="text-xs uppercase tracking-wide text-slate-400">
              Plant
            </p>
            <p className="mt-1 truncate text-sm font-medium text-slate-100">
              {project.plant_name ?? "Not specified"}
            </p>
          </div>

          <div className="border-b border-white/10 px-6 py-4 sm:border-b-0 sm:border-r">
            <p className="text-xs uppercase tracking-wide text-slate-400">
              Location
            </p>
            <p className="mt-1 truncate text-sm font-medium text-slate-100">
              {project.location ?? "Not specified"}
            </p>
          </div>

          <div className="px-6 py-4">
            <p className="text-xs uppercase tracking-wide text-slate-400">
              Project Control
            </p>
            <p className="mt-1 inline-flex items-center gap-2 text-sm font-medium text-slate-100">
              <ShieldCheck
                aria-hidden="true"
                className="size-4 text-emerald-300"
              />
              Tenant secured
            </p>
          </div>
        </div>
      </section>

      <section aria-labelledby="engineering-workflows-title">
        <div className="max-w-3xl">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-sky-700">
            Engineering workflows
          </p>

          <h2
            id="engineering-workflows-title"
            className="mt-1 text-2xl font-semibold tracking-tight text-slate-950"
          >
            Select the engineering workstream
          </h2>

          <p className="mt-2 text-sm leading-6 text-slate-600">
            Each workspace operates within this project and retains
            tenant-scoped engineering context.
          </p>
        </div>

        <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {workflows.map((workflow) => {
            const Icon = workflow.icon;

            return (
              <Card
                key={workflow.title}
                className="group flex h-full flex-col border-slate-200/80 shadow-sm transition duration-200 hover:-translate-y-0.5 hover:border-sky-200 hover:shadow-md"
              >
                <CardHeader className="flex-1 pb-4">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex size-11 items-center justify-center rounded-xl bg-sky-50 text-sky-700">
                      <Icon aria-hidden="true" className="size-5" />
                    </div>

                    <Badge className="border-emerald-200 bg-emerald-50 text-emerald-700 hover:bg-emerald-50">
                      <CheckCircle2
                        aria-hidden="true"
                        className="mr-1 size-3.5"
                      />
                      Ready
                    </Badge>
                  </div>

                  <div className="pt-3">
                    <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
                      {workflow.phase}
                    </p>

                    <CardTitle className="mt-2 text-lg text-slate-950">
                      {workflow.title}
                    </CardTitle>
                  </div>

                  <CardDescription className="leading-6 text-slate-600">
                    {workflow.description}
                  </CardDescription>
                </CardHeader>

                <CardContent className="space-y-2 pt-0">
                  <Button
                    asChild
                    variant="outline"
                    className="w-full justify-between border-slate-200 group-hover:border-sky-300 group-hover:text-sky-800"
                  >
                    <Link to={workflow.path}>
                      {workflow.actionLabel}
                      <ArrowRight
                        aria-hidden="true"
                        className="size-4 transition-transform group-hover:translate-x-1"
                      />
                    </Link>
                  </Button>

                  {workflow.secondaryPath && workflow.secondaryLabel && (
                    <Button
                      asChild
                      variant="ghost"
                      className="w-full justify-between"
                    >
                      <Link to={workflow.secondaryPath}>
                        {workflow.secondaryLabel}
                        <ArrowRight aria-hidden="true" className="size-4" />
                      </Link>
                    </Button>
                  )}
                </CardContent>
              </Card>
            );
          })}
        </div>
      </section>

      <section
        aria-labelledby="governance-title"
        className="rounded-2xl bg-slate-100 p-5 sm:p-6"
      >
        <div className="flex items-start gap-3">
          <div className="flex size-11 shrink-0 items-center justify-center rounded-xl bg-slate-900 text-white">
            <Wind aria-hidden="true" className="size-5" />
          </div>

          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
              Project governance
            </p>
            <h2
              id="governance-title"
              className="mt-1 text-xl font-semibold tracking-tight text-slate-950"
            >
              Engineering Records &amp; Governance
            </h2>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-600">
              Continue into controlled records, assessment registers, and
              authorized engineering reports.
            </p>
          </div>
        </div>

        <div className="mt-5 grid gap-4 md:grid-cols-3">
          {governanceWorkspaces.map((workspace) => {
            const Icon = workspace.icon;

            return (
              <Card
                key={workspace.title}
                className="border-slate-200/80 bg-white shadow-sm"
              >
                <CardHeader>
                  <Icon aria-hidden="true" className="size-5 text-slate-500" />
                  <CardTitle className="pt-2 text-base">
                    {workspace.title}
                  </CardTitle>
                  <CardDescription className="leading-6">
                    {workspace.description}
                  </CardDescription>
                </CardHeader>

                <CardContent>
                  <Button
                    asChild
                    variant="outline"
                    className="w-full justify-between"
                  >
                    <Link to={workspace.path}>
                      {workspace.actionLabel}
                      <ArrowRight aria-hidden="true" className="size-4" />
                    </Link>
                  </Button>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </section>
    </main>
  );
}
