import {
  BrowserRouter,
  Route,
  Routes,
} from "react-router";

import { AppLayout } from "../layouts/AppLayout";
import { AssessmentsPage } from "../pages/AssessmentsPage";
import { BrownfieldPlantAssessmentPage } from "../pages/BrownfieldPlantAssessmentPage";
import { DashboardPage } from "../pages/DashboardPage";
import { GasPropertiesPage } from "../pages/GasPropertiesPage";
import { GreenfieldSystemDesignPage } from "../pages/GreenfieldSystemDesignPage";
import { PerformanceEnergyAnalysisPage } from "../pages/PerformanceEnergyAnalysisPage";
import { CompressorEngineeringPage } from "../pages/CompressorEngineeringPage";
import { CompressionEngineeringPage } from "../pages/CompressionEngineeringPage";
import { ReciprocatingEngineeringPage } from "../pages/ReciprocatingEngineeringPage";
import { CentrifugalEngineeringPage } from "../pages/CentrifugalEngineeringPage";
import { CalculationHistoryPage } from "../pages/CalculationHistoryPage";
import { CalculationDetailPage } from "../pages/CalculationDetailPage";
import { CompressorSelectionPage } from "../pages/CompressorSelectionPage";
import { LoginPage } from "../pages/LoginPage";
import { ProjectsPage } from "../pages/ProjectsPage";
import { ProjectWorkspacePage } from "../pages/ProjectWorkspacePage";
import { ReportsPage } from "../pages/ReportsPage";
import { ProtectedRoute } from "./ProtectedRoute";

function ProtectedPage({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ProtectedRoute>
      <AppLayout>
        {children}
      </AppLayout>
    </ProtectedRoute>
  );
}

export function AppRouter() {
  return (
    <BrowserRouter>
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
    </BrowserRouter>
  );
}
