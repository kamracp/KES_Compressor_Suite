import {
  Activity,
  AlertTriangle,
  ArrowRight,
  Calculator,
  ClipboardCheck,
  Factory,
  FileText,
  Gauge,
  History,
  Package,
  Search,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { Link, useParams } from "react-router";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

type WorkflowStatus = "Available" | "Integration Pending";

type EngineeringWorkflow = {
  title: string;
  description: string;
  icon: LucideIcon;
  status: WorkflowStatus;
  path?: string;
  secondaryPath?: string;
  secondaryLabel?: string;
};

export function ProjectWorkspacePage() {
  const { projectId } = useParams();

  if (!projectId) {
    throw new Error("Project ID is required.");
  }

  const workflows: EngineeringWorkflow[] = [
    {
      title: "Greenfield System Design",
      description:
        "Design a new factory compressed-air system from consumer demand through pressure, station capacity, treatment, storage, energy, and engineering review.",
      icon: Factory,
      status: "Available",
      path: `/projects/${projectId}/greenfield`,
    },
    {
      title: "Brownfield Plant Assessment",
      description:
        "Assess an existing compressor station, operating profile, system condition, capacity utilisation, losses, controls, and improvement opportunities.",
      icon: Search,
      status: "Available",
      path: `/projects/${projectId}/brownfield`,
    },
    {
      title: "Performance & Energy Analysis",
      description:
        "Evaluate compressor and system specific power, operating efficiency, energy consumption, cost, deviation, and improvement potential.",
      icon: Gauge,
      status: "Available",
      path: `/projects/${projectId}/performance`,
    },
    {
      title: "Leakage Management",
      description:
        "Quantify compressed-air leakage, energy loss, annual cost, repair priority, and verified post-repair savings.",
      icon: AlertTriangle,
      status: "Available",
      path: `/projects/${projectId}/leakage`,
    },
    {
      title: "Allied Equipment Engineering",
      description:
        "Engineer receivers, storage, dryers, treatment, aftercoolers, moisture separators, filters, condensate drains, and allied-equipment pressure losses.",
      icon: Package,
      status: "Available",
      path: `/projects/${projectId}/allied-equipment`,
      secondaryPath: `/projects/${projectId}/skid`,
      secondaryLabel: "Open Skid Engineering",
    },
    {
      title: "Advanced Compressor Engineering",
      description:
        "Open specialist gas-property, compressor-selection, compression, reciprocating, centrifugal, and saved calculation workflows.",
      icon: Calculator,
      status: "Available",
      path: `/projects/${projectId}/compressor`,
    },
  ];

  return (
    <main className="space-y-6">
      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
        <div className="max-w-3xl">
          <Badge variant="outline">
            Project Engineering Workspace
          </Badge>

          <h1 className="mt-4 text-3xl font-bold tracking-tight text-slate-950 sm:text-4xl">
            Complete Compressed-Air Engineering
          </h1>

          <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-600 sm:text-base">
            Select the engineering problem to solve. The project acts as the
            common engineering record for system design, assessment,
            calculations, optimization, and future reporting.
          </p>

          <div className="mt-4 flex flex-wrap gap-2">
            <Badge variant="secondary">
              Project {projectId}
            </Badge>

            <Badge variant="outline">
              Vendor Neutral
            </Badge>

            <Badge variant="outline">
              Manufacturing Engineering
            </Badge>
          </div>
        </div>
      </section>

      <section>
        <div className="mb-4">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
            Engineering Workflows
          </p>

          <h2 className="mt-1 text-2xl font-semibold tracking-tight text-slate-950">
            Choose Engineering Work
          </h2>

          <p className="mt-2 text-sm text-slate-600">
            Greenfield and Advanced Engineering are connected now. Remaining
            system workflows will be activated as their engineering integration
            is completed.
          </p>
        </div>

        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {workflows.map((workflow) => {
            const Icon = workflow.icon;
            const available = workflow.status === "Available";

            return (
              <Card
                key={workflow.title}
                className="group flex flex-col transition-shadow hover:shadow-md"
              >
                <CardHeader className="flex-1">
                  <div className="mb-3 flex items-start justify-between gap-3">
                    <div className="flex size-11 items-center justify-center rounded-xl bg-slate-100 text-slate-700">
                      <Icon className="size-5" />
                    </div>

                    <Badge
                      variant={available ? "secondary" : "outline"}
                    >
                      {workflow.status}
                    </Badge>
                  </div>

                  <CardTitle className="text-lg">
                    {workflow.title}
                  </CardTitle>

                  <CardDescription className="leading-6">
                    {workflow.description}
                  </CardDescription>
                </CardHeader>

                <CardContent>
                  {available && workflow.path ? (
                    <div className="space-y-2">
                      <Button
                        asChild
                        variant="ghost"
                        className="w-full justify-between"
                      >
                        <Link to={workflow.path}>
                          Open Engineering Workspace
                          <ArrowRight className="size-4 transition-transform group-hover:translate-x-1" />
                        </Link>
                      </Button>

                      {workflow.secondaryPath &&
                        workflow.secondaryLabel && (
                          <Button
                            asChild
                            variant="outline"
                            className="w-full justify-between"
                          >
                            <Link to={workflow.secondaryPath}>
                              {workflow.secondaryLabel}
                              <ArrowRight className="size-4" />
                            </Link>
                          </Button>
                        )}
                    </div>
                  ) : (
                    <Button
                      type="button"
                      variant="ghost"
                      className="w-full justify-between"
                      disabled
                    >
                      Engineering Integration Pending
                      <Activity className="size-4" />
                    </Button>
                  )}
                </CardContent>
              </Card>
            );
          })}
        </div>
      </section>

      <section>
        <div className="mb-4">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
            Project Records
          </p>

          <h2 className="mt-1 text-xl font-semibold text-slate-950">
            Engineering Records & Governance
          </h2>
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          <Card>
            <CardHeader>
              <History className="mb-2 size-5 text-slate-500" />

              <CardTitle className="text-base">
                Calculation Records
              </CardTitle>

              <CardDescription>
                Saved engineering calculations, revisions, results, and notes.
              </CardDescription>
            </CardHeader>

            <CardContent>
              <Button
                asChild
                variant="outline"
                className="w-full"
              >
                <Link to={`/projects/${projectId}/calculations`}>
                  Open Records
                </Link>
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <ClipboardCheck className="mb-2 size-5 text-slate-500" />

              <CardTitle className="text-base">
                Assessments
              </CardTitle>

              <CardDescription>
                Assessment workspace exists; project-level workflow integration
                will follow Brownfield implementation.
              </CardDescription>
            </CardHeader>

            <CardContent>
              <Button
                asChild
                variant="outline"
                className="w-full"
              >
                <Link to="/assessments">
                  Open Assessment Workspace
                </Link>
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <FileText className="mb-2 size-5 text-slate-500" />

              <CardTitle className="text-base">
                Reports
              </CardTitle>

              <CardDescription>
                Report presentation is retained, but secure export and PDF
                integration remains gated until report security is completed.
              </CardDescription>
            </CardHeader>

            <CardContent>
              <Button
                asChild
                variant="outline"
                className="w-full"
              >
                <Link to="/reports">
                  Open Report Workspace
                </Link>
              </Button>
            </CardContent>
          </Card>
        </div>
      </section>
    </main>
  );
}
