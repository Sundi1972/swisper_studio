import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Box } from '@mui/material';
import { GlobalHeader } from './components/global-header';
import { LoginPage } from './features/auth/components/login-page';
import { ProjectListPage } from './features/projects/components/project-list-page';
import { ProjectLayout } from './features/projects/components/project-layout';
import { ProjectOverview } from './features/projects/components/project-overview';
import { ProjectSettingsPage } from './features/projects/components/project-settings-page';
import { TraceListPage } from './features/traces/components/trace-list-page';
import { TraceDetailPage } from './features/traces/components/trace-detail-page';
import { ConfigPage } from './features/config/components/config-page';
import { SystemArchitectureView } from './features/swisper-builder';
import { ProtectedRoute } from './features/auth/components/protected-route';
import { UserManagementPage } from './features/admin/components/user-management-page';
import { CostManagementPage } from './features/admin/components/cost-management-page';
import { getUser } from './features/auth/utils/auth-storage';

export function App() {
  const user = getUser();
  const showGlobalHeader = user !== null; // Show header when authenticated

  return (
    <BrowserRouter>
      {showGlobalHeader && <GlobalHeader />}
      
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        
        {/* Projects list (no sidebar) */}
        <Route
          path="/projects"
          element={
            <ProtectedRoute>
              <ProjectListPage />
            </ProtectedRoute>
          }
        />
        
        {/* Admin: User Management */}
        <Route
          path="/admin/users"
          element={
            <ProtectedRoute>
              <UserManagementPage />
            </ProtectedRoute>
          }
        />
        
        {/* Admin: Cost Management */}
        <Route
          path="/admin/cost-management"
          element={
            <ProtectedRoute>
              <CostManagementPage />
            </ProtectedRoute>
          }
        />
        
        {/* System Architecture (global view) */}
        <Route
          path="/system-architecture"
          element={
            <ProtectedRoute>
              <Box sx={{ p: 3 }}>
                <SystemArchitectureView />
              </Box>
            </ProtectedRoute>
          }
        />
        
        {/* Project workspace with sidebar navigation */}
        <Route
          path="/projects/:projectId"
          element={
            <ProtectedRoute>
              <ProjectLayout />
            </ProtectedRoute>
          }
        >
          {/* Nested routes render in <Outlet /> */}
          <Route index element={<ProjectOverview />} />
          <Route path="tracing" element={<TraceListPage />} />
          <Route path="tracing/:traceId" element={<TraceDetailPage />} />
          <Route path="graphs" element={<SystemArchitectureView />} />
          <Route path="config" element={<ConfigPage />} />
          <Route path="settings" element={<ProjectSettingsPage />} />
          {/* Phase 4+: Add more routes as we build them */}
          {/* <Route path="analytics" element={<AnalyticsPage />} /> */}
        </Route>
        
        <Route path="/" element={<Navigate to="/projects" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

