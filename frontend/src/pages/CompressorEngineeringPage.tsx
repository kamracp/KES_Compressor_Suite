import {
  Atom,
  Calculator,
  CheckCircle2,
  ClipboardCheck,
  Fan,
  GitCompareArrows,
  History,
  MoveRight,
  Settings2,
  ShieldCheck,
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
  step: number;
  title: string;
  phase: string;
  description: string;
  path: string;
  icon: typeof Atom;
};

export function CompressorEngineeringPage() {
  const { projectId, hasValidProjectId, project, projectQuery } =
    useProjectContext();

  if (!hasValidProjectId) {
    throw new Error("Valid project ID is required.");
  }

  const modules: EngineeringModule[] = [
    {
      step: 1,
      title: "Gas Properties",
      phase: "Define Gas",
      description:
        "Establish gas composition, pseudo-critical properties, compressibility factor, and real-gas density.",
      path: `/projects/${projectId}/compressor/gas`,
      icon: Atom,
    },
    {
      step: 2,
      title: "Compressor Technology Selection",
      phase: "Select Technology",
      description:
        "Screen suitable compressor technologies against the defined duty, operating envelope, and service requirements.",
      path: `/projects/${projectId}/compressor/selection`,
      icon: GitCompareArrows,
    },
    {
      step: 3,
      title: "Compression Engineering",
      phase: "Establish Duty",
      description:
        "Calculate pressure ratio, staging, discharge temperature, power, efficiency, and overall compression duty.",
      path: `/projects/${projectId}/compressor/compression`,
      icon: Calculator,
    },
    {
      step: 4,
      title: "Reciprocating Compressor",
      phase: "Detailed Engineering",
      description:
        "Evaluate displacement, capacity, clearance, volumetric efficiency, compression ratio, and rod-load behaviour.",
      path: `/projects/${projectId}/compressor/reciprocating`,
      icon: Settings2,
    },
    {
      step: 5,
      title: "Centrifugal Compressor",
      phase: "Detailed Engineering",
      description:
        "Evaluate polytropic performance, head, stages, power requirement, surge margin, and operating limits.",
      path: `/projects/${projectId}/compressor/centrifugal`,
      icon: Fan,
    },
  ];

  const projectIdentity = project
    ? `${project.project_code} · ${project.project_name}`
    : projectQuery.isPending
      ? "Loading project..."
      : `Project ${projectId}`;

  return (
    <main className="space-y-8">
      <section
        aria-labelledby="engineering-hub-title"
        className="overflow-hidden rounded-2xl bg-slate-950 text-white shadow-sm"
      >
        <div className="grid gap-8 p-6 sm:p-8 lg:grid-cols-[minmax(0,1fr)_auto] lg:items-end">
          <div className="max-w-3xl">
            <div className="flex flex-wrap items-center gap-2">
              <Badge className="border-sky-400/30 bg-sky-400/10 text-sky-100 hover:bg-sky-400/10">
                Compressor Engineering Hub
              </Badge>
              <Badge className="border-emerald-400/30 bg-emerald-400/10 text-emerald-100 hover:bg-emerald-400/10">
                <CheckCircle2 aria-hidden="true" className="mr-1 size-3.5" />
                Operational
              </Badge>
            </div>

            <h1
              id="engineering-hub-title"
              className="mt-5 text-3xl font-bold tracking-tight sm:text-4xl"
            >
              Advanced Compressor Engineering
            </h1>
            <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-300 sm:text-base">
              Follow a controlled engineering sequence from gas definition and
              technology screening through detailed compressor calculations and
              auditable records.
            </p>

            <div className="mt-6 rounded-xl border border-white/10 bg-white/5 p-4">
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
                Active project
              </p>
              <div className="mt-2 flex flex-wrap items-center gap-2">
                <p className="font-semibold text-white">{projectIdentity}</p>
                {project && (
                  <Badge className="border-white/15 bg-white/10 text-slate-200 hover:bg-white/10">
                    {project.status}
                  </Badge>
                )}
              </div>
            </div>
          </div>

          <Button asChild variant="secondary" className="w-full sm:w-auto">
            <Link to={`/projects/${projectId}`}>
              Project Workspace
              <MoveRight aria-hidden="true" className="ml-2 size-4" />
            </Link>
          </Button>
        </div>

        <div className="border-t border-white/10 bg-slate-900/70 px-6 py-4 sm:px-8">
          <div className="flex flex-wrap gap-x-6 gap-y-2 text-xs font-medium text-slate-300">
            <span className="inline-flex items-center gap-2">
              <ShieldCheck aria-hidden="true" className="size-4 text-sky-300" />
              Vendor-neutral calculations
            </span>
            <span className="inline-flex items-center gap-2">
              <ClipboardCheck
                aria-hidden="true"
                className="size-4 text-sky-300"
              />
              Project-controlled records
            </span>
            <span className="inline-flex items-center gap-2">
              <History aria-hidden="true" className="size-4 text-sky-300" />
              Revision-ready workflow
            </span>
          </div>
        </div>
      </section>

      <section aria-labelledby="workflow-title">
        <div className="max-w-3xl">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-sky-700">
            Engineering workflow
          </p>
          <h2
            id="workflow-title"
            className="mt-1 text-2xl font-semibold tracking-tight text-slate-950"
          >
            Progress through the calculation sequence
          </h2>
          <p className="mt-2 text-sm leading-6 text-slate-600">
            Begin with the engineering basis, establish the compression duty,
            and then proceed to the applicable detailed technology workspace.
          </p>
        </div>

        <ol className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {modules.map((module) => {
            const Icon = module.icon;

            return (
              <li key={module.title} className="h-full">
                <Card className="group h-full border-slate-200/80 shadow-sm transition duration-200 hover:-translate-y-0.5 hover:border-sky-200 hover:shadow-md">
                  <CardHeader className="pb-4">
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
                        Step {module.step} · {module.phase}
                      </p>
                      <CardTitle className="mt-2 text-lg text-slate-950">
                        {module.title}
                      </CardTitle>
                    </div>
                    <CardDescription className="min-h-18 leading-6 text-slate-600">
                      {module.description}
                    </CardDescription>
                  </CardHeader>

                  <CardContent className="mt-auto pt-0">
                    <Button
                      asChild
                      variant="outline"
                      className="w-full justify-between border-slate-200 bg-white group-hover:border-sky-300 group-hover:text-sky-800"
                    >
                      <Link
                        aria-label={`Open ${module.title}`}
                        to={module.path}
                      >
                        Open workspace
                        <MoveRight
                          aria-hidden="true"
                          className="size-4 transition-transform group-hover:translate-x-1"
                        />
                      </Link>
                    </Button>
                  </CardContent>
                </Card>
              </li>
            );
          })}
        </ol>
      </section>

      <section
        aria-labelledby="records-title"
        className="rounded-2xl bg-slate-100 p-5 sm:p-6"
      >
        <div className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_auto] lg:items-center">
          <div className="flex items-start gap-4">
            <div className="flex size-12 shrink-0 items-center justify-center rounded-xl bg-slate-900 text-white">
              <History aria-hidden="true" className="size-5" />
            </div>
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
                  Governance and audit
                </p>
                <Badge className="border-emerald-200 bg-emerald-50 text-emerald-700 hover:bg-emerald-50">
                  <CheckCircle2 aria-hidden="true" className="mr-1 size-3.5" />
                  Ready
                </Badge>
              </div>
              <h2
                id="records-title"
                className="mt-2 text-xl font-semibold tracking-tight text-slate-950"
              >
                Engineering Calculation Records
              </h2>
              <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-600">
                Review saved calculations, engineering notes, revisions, and
                project-linked results without leaving the active project
                context.
              </p>
            </div>
          </div>

          <Button asChild className="w-full lg:w-auto">
            <Link to={`/projects/${projectId}/calculations`}>
              Open calculation records
              <MoveRight aria-hidden="true" className="ml-2 size-4" />
            </Link>
          </Button>
        </div>
      </section>

      <section
        aria-labelledby="suite-role-title"
        className="rounded-xl border border-slate-200/80 bg-white px-5 py-4"
      >
        <div className="flex items-start gap-3">
          <ShieldCheck
            aria-hidden="true"
            className="mt-0.5 size-5 shrink-0 text-slate-500"
          />
          <div>
            <h2
              id="suite-role-title"
              className="text-sm font-semibold text-slate-900"
            >
              Role within KES Compressor Engineering Suite
            </h2>
            <p className="mt-1 text-sm leading-6 text-slate-600">
              This hub provides specialist compressor calculations. New System
              Design, Existing Plant Assessment, Performance, Leakage, and
              Allied Equipment remain separate system-level workflows.
            </p>
          </div>
        </div>
      </section>
    </main>
  );
}
