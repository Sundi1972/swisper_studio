import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { LoginPage } from './features/auth/components/login-page';
import { ProjectListPage } from './features/projects/components/project-list-page';
import { TraceListPage } from './features/traces/components/trace-list-page';
import { ProtectedRoute } from './features/auth/components/protected-route';

export function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        
        <Route
          path="/projects"
          element={
            <ProtectedRoute>
              <ProjectListPage />
            </ProtectedRoute>
          }
        />
        
        <Route
          path="/projects/:projectId/traces"
          element={
            <ProtectedRoute>
              <TraceListPage />
            </ProtectedRoute>
          }
        />
        
        <Route path="/" element={<Navigate to="/projects" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

