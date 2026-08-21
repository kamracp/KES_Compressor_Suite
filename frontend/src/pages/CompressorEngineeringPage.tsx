import {
  Atom,
  Calculator,
  Fan,
  Gauge,
  GitCompareArrows,
  History,
  MoveRight,
  Settings2,
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

import { useProjectContext } from "../features/projects/useProjectContext";

type EngineeringModule = {
  title: string;
  description: string;
  path: string;
  icon: typeof Atom;
  status: "Available" | "Planned";
};

export function CompressorEngineeringPage() {
  const {
    projectId,
    hasValidProjectId,
    project,
    projectQuery,
  } = useProjectContext();

  if (!hasValidProjectId) {
    throw new Error("Valid project ID is required.");
  }

  const modules: EngineeringModule[] = [
    {
      title: "Gas Properties",
      description:
        "Evaluate gas mixtures, pseudo-critical properties, compressibility factor, and real-gas density.",
      path: `/projects/${projectId}/compressor/gas`,
      icon: Atom,
      status: "Available",
    },
    {
      title: "Compressor Technology Selection",
      description:
        "Evaluate suitable compressor technology classes from engineering duty and operating requirements.",
      path: `/projects/${projectId}/compressor/selection`,
      icon: GitCompareArrows,
      status: "Available",
    },
    {
      title: "Compression Engineering",
      description:
        "Analyse pressure ratio, stages, discharge temperature, power, efficiency, and compression duty.",
      path: `/projects/${projectId}/compressor/compression`,
      icon: Calculator,
      status: "Available",
    },
    {
      title: "Reciprocating Compressor",
      description:
        "Engineer displacement, capacity, clearance, volumetric efficiency, compression ratio, and rod-load behaviour.",
      path: `/projects/${projectId}/compressor/reciprocating`,
      icon: Settings2,
      status: "Available",
    },
    {
      title: "Centrifugal Compressor",
      description:
        "Evaluate polytropic performance, head, stages, power requirement, surge margin, and operating limits.",
      path: `/projects/${projectId}/compressor/centrifugal`,
      icon: Fan,
      status: "Available",
    },
    {
      title: "Engineering Calculation Records",
      description:
        "Review saved calculations, revisions, engineering notes, results, and calculation history for this project.",
      path: `/projects/${projectId}/calculations`,
      icon: History,
      status: "Available",
    },
  ];

  return (
    <main className="space-y-6">
      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
          <div className="max-w-3xl">
            <Badge variant="outline">
              Advanced Engineering
            </Badge>

            <h1 className="mt-4 text-3xl font-bold tracking-tight text-slate-950 sm:text-4xl">
              Advanced Compressor Engineering
            </h1>

            <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-600 sm:text-base">
              Specialist compressor calculations for process, industrial,
              manufacturing, and compressed-air engineering applications.
            </p>

            <div className="mt-4 flex flex-wrap gap-2">
              <Badge variant="secondary">
                {project
                  ? `${project.project_code} · ${project.project_name}`
                  : projectQuery.isPending
                    ? "Loading project..."
                    : `Project ${projectId}`}
              </Badge>

              {project && (
                <Badge variant="outline">
                  {project.status}
                </Badge>
              )}

              <Badge variant="outline">
                Vendor Neutral
              </Badge>

              <Badge variant="outline">
                Calculation Persistence
              </Badge>
            </div>
          </div>

          <Button
            asChild
            variant="outline"
          >
            <Link to={`/projects/${projectId}`}>
              Project Workspace
            </Link>
          </Button>
        </div>
      </section>

      <section>
        <div className="mb-4">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
            Engineering Workbench
          </p>

          <h2 className="mt-1 text-2xl font-semibold tracking-tight text-slate-950">
            Select an Advanced Engineering Module
          </h2>

          <p className="mt-2 text-sm text-slate-600">
            Each module operates within the current project and can persist
            calculation results for engineering review and revision history.
          </p>
        </div>

        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {modules.map((module) => {
            const Icon = module.icon;

            return (
              <Card
                key={module.title}
                className="group transition-shadow hover:shadow-md"
              >
                <CardHeader>
                  <div className="mb-3 flex items-start justify-between gap-3">
                    <div className="flex size-11 items-center justify-center rounded-xl bg-slate-100 text-slate-700">
                      <Icon className="size-5" />
                    </div>

                    <Badge
                      variant={
                        module.status === "Available"
                          ? "secondary"
                          : "outline"
                      }
                    >
                      {module.status}
                    </Badge>
                  </div>

                  <CardTitle className="text-lg">
                    {module.title}
                  </CardTitle>

                  <CardDescription className="leading-6">
                    {module.description}
                  </CardDescription>
                </CardHeader>

                <CardContent>
                  <Button
                    asChild
                    variant="ghost"
                    className="w-full justify-between"
                  >
                    <Link to={module.path}>
                      Open Engineering Module
                      <MoveRight className="size-4 transition-transform group-hover:translate-x-1" />
                    </Link>
                  </Button>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </section>

      <Card>
        <CardHeader>
          <div className="flex items-center gap-3">
            <Gauge className="size-5 text-slate-500" />

            <div>
              <CardTitle>
                Role within KES Compressor Engineering Suite
              </CardTitle>

              <CardDescription className="mt-1">
                Advanced Engineering is the specialist calculation workbench.
                Greenfield, Brownfield, Performance, Leakage, and Allied
                Equipment remain separate system-level workflows.
              </CardDescription>
            </div>
          </div>
        </CardHeader>
      </Card>
    </main>
  );
}
