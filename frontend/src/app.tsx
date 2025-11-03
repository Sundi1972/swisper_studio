import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { LoginPage } from './features/auth/components/login-page';
import { ProjectListPage } from './features/projects/components/project-list-page';
import { ProjectLayout } from './features/projects/components/project-layout';
import { ProjectOverview } from './features/projects/components/project-overview';
import { TraceListPage } from './features/traces/components/trace-list-page';
import { TraceDetailPage } from './features/traces/components/trace-detail-page';
import { ConfigPage } from './features/config/components/config-page';
import { SystemArchitectureView } from './features/swisper-builder';
import { ProtectedRoute } from './features/auth/components/protected-route';
import { UserManagementPage } from './features/admin/components/user-management-page';

export function App() {
  return (
    <BrowserRouter>
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
          {/* Phase 4+: Add more routes as we build them */}
          {/* <Route path="analytics" element={<AnalyticsPage />} /> */}
        </Route>
        
        <Route path="/" element={<Navigate to="/projects" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

