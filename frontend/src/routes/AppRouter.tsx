import {
  lazy,
  Suspense,
  type ReactNode,
} from "react";

import {
  BrowserRouter,
  Route,
  Routes,
  useParams,
} from "react-router";

import { ProjectContextRoute } from "../features/projects/ProjectContextRoute";
import { AppLayout } from "../layouts/AppLayout";
import { AssessmentsPage } from "../pages/AssessmentsPage";
import { DashboardPage } from "../pages/DashboardPage";
import { LoginPage } from "../pages/LoginPage";
import { ProjectsPage } from "../pages/ProjectsPage";
import { ProjectWorkspacePage } from "../pages/ProjectWorkspacePage";
import { ReportsPage } from "../pages/ReportsPage";
import { ProtectedRoute } from "./ProtectedRoute";

const BrownfieldPlantAssessmentPage = lazy(
  async () => ({
    default: (
      await import("../pages/BrownfieldPlantAssessmentPage")
    ).BrownfieldPlantAssessmentPage,
  }),
);

const GasPropertiesPage = lazy(
  async () => ({
    default: (
      await import("../pages/GasPropertiesPage")
    ).GasPropertiesPage,
  }),
);

const GreenfieldSystemDesignPage = lazy(
  async () => ({
    default: (
      await import("../pages/GreenfieldSystemDesignPage")
    ).GreenfieldSystemDesignPage,
  }),
);

const LeakageManagementPage = lazy(
  async () => ({
    default: (
      await import("../pages/LeakageManagementPage")
    ).LeakageManagementPage,
  }),
);

const AlliedEquipmentEngineeringPage = lazy(
  async () => ({
    default: (
      await import("../pages/AlliedEquipmentEngineeringPage")
    ).AlliedEquipmentEngineeringPage,
  }),
);

const SkidEngineeringPage = lazy(
  async () => ({
    default: (
      await import("../pages/SkidEngineeringPage")
    ).SkidEngineeringPage,
  }),
);

const PerformanceEnergyAnalysisPage = lazy(
  async () => ({
    default: (
      await import("../pages/PerformanceEnergyAnalysisPage")
    ).PerformanceEnergyAnalysisPage,
  }),
);

const CompressorEngineeringPage = lazy(
  async () => ({
    default: (
      await import("../pages/CompressorEngineeringPage")
    ).CompressorEngineeringPage,
  }),
);

const CompressionEngineeringPage = lazy(
  async () => ({
    default: (
      await import("../pages/CompressionEngineeringPage")
    ).CompressionEngineeringPage,
  }),
);

const ReciprocatingEngineeringPage = lazy(
  async () => ({
    default: (
      await import("../pages/ReciprocatingEngineeringPage")
    ).ReciprocatingEngineeringPage,
  }),
);

const CentrifugalEngineeringPage = lazy(
  async () => ({
    default: (
      await import("../pages/CentrifugalEngineeringPage")
    ).CentrifugalEngineeringPage,
  }),
);

const CalculationHistoryPage = lazy(
  async () => ({
    default: (
      await import("../pages/CalculationHistoryPage")
    ).CalculationHistoryPage,
  }),
);

const CalculationDetailPage = lazy(
  async () => ({
    default: (
      await import("../pages/CalculationDetailPage")
    ).CalculationDetailPage,
  }),
);

const CompressorSelectionPage = lazy(
  async () => ({
    default: (
      await import("../pages/CompressorSelectionPage")
    ).CompressorSelectionPage,
  }),
);

function RouteLoadingFallback() {
  return (
    <main className="grid min-h-screen place-items-center bg-slate-50 p-6">
      <p
        role="status"
        className="text-sm font-medium text-slate-600"
      >
        Loading engineering workspace...
      </p>
    </main>
  );
}

function ProtectedPage({
  children,
}: {
  children: ReactNode;
}) {
  const { projectId } = useParams();

  return (
    <ProtectedRoute>
      <AppLayout>
        {projectId ? (
          <ProjectContextRoute>
            {children}
          </ProjectContextRoute>
        ) : (
          children
        )}
      </AppLayout>
    </ProtectedRoute>
  );
}

export function AppRouter() {
  return (
    <BrowserRouter>
      <Suspense fallback={<RouteLoadingFallback />}>
        <Routes>
          <Route
            path="/login"
            element={<LoginPage />}
          />

          <Route
            path="/"
            element={
              <ProtectedPage>
                <DashboardPage />
              </ProtectedPage>
            }
          />

          <Route
            path="/projects"
            element={
              <ProtectedPage>
                <ProjectsPage />
              </ProtectedPage>
            }
          />

          <Route
            path="/projects/:projectId"
            element={
              <ProtectedPage>
                <ProjectWorkspacePage />
              </ProtectedPage>
            }
          />

          <Route
            path="/projects/:projectId/brownfield"
            element={
              <ProtectedPage>
                <BrownfieldPlantAssessmentPage />
              </ProtectedPage>
            }
          />

          <Route
            path="/projects/:projectId/performance"
            element={
              <ProtectedPage>
                <PerformanceEnergyAnalysisPage />
              </ProtectedPage>
            }
          />

          <Route
            path="/projects/:projectId/leakage"
            element={
              <ProtectedPage>
                <LeakageManagementPage />
              </ProtectedPage>
            }
          />

          <Route
            path="/projects/:projectId/allied-equipment"
            element={
              <ProtectedPage>
                <AlliedEquipmentEngineeringPage />
              </ProtectedPage>
            }
          />

          <Route
            path="/projects/:projectId/skid"
            element={
              <ProtectedPage>
                <SkidEngineeringPage />
              </ProtectedPage>
            }
          />

          <Route
            path="/projects/:projectId/greenfield"
            element={
              <ProtectedPage>
                <GreenfieldSystemDesignPage />
              </ProtectedPage>
            }
          />

          <Route
            path="/projects/:projectId/compressor"
            element={
              <ProtectedPage>
                <CompressorEngineeringPage />
              </ProtectedPage>
            }
          />

          <Route
            path="/projects/:projectId/compressor/gas"
            element={
              <ProtectedPage>
                <GasPropertiesPage />
              </ProtectedPage>
            }
          />

          <Route
            path="/projects/:projectId/compressor/compression"
            element={
              <ProtectedPage>
                <CompressionEngineeringPage />
              </ProtectedPage>
            }
          />

          <Route
            path="/projects/:projectId/compressor/reciprocating"
            element={
              <ProtectedPage>
                <ReciprocatingEngineeringPage />
              </ProtectedPage>
            }
          />

          <Route
            path="/projects/:projectId/compressor/centrifugal"
            element={
              <ProtectedPage>
                <CentrifugalEngineeringPage />
              </ProtectedPage>
            }
          />

          <Route
            path="/projects/:projectId/compressor/selection"
            element={
              <ProtectedPage>
                <CompressorSelectionPage />
              </ProtectedPage>
            }
          />

          <Route
            path="/projects/:projectId/calculations"
            element={
              <ProtectedPage>
                <CalculationHistoryPage />
              </ProtectedPage>
            }
          />

          <Route
            path="/projects/:projectId/calculations/:calculationCaseId"
            element={
              <ProtectedPage>
                <CalculationDetailPage />
              </ProtectedPage>
            }
          />

          <Route
            path="/assessments"
            element={
              <ProtectedPage>
                <AssessmentsPage />
              </ProtectedPage>
            }
          />

          <Route
            path="/reports"
            element={
              <ProtectedPage>
                <ReportsPage />
              </ProtectedPage>
            }
          />
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}