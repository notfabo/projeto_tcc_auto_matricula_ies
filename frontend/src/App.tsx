import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';

import { LoginPage } from './pages/LoginPage';
import { DocumentUploadPage } from './pages/DocumentUploadPage';
import { DocumentReviewPage } from './pages/DocumentReviewPage';
import { ApprovedPage } from './pages/ApprovedPage';
import { AdminPage } from './pages/AdminPage';
import { AdminApiConfigPage } from './pages/AdminApiConfigPage';
import RevisaoList from './pages/RevisaoList';
import RevisaoDetalhes from './pages/RevisaoDetalhes';
import AdminUsersPage from './pages/AdminUsersPage';
import { LegacyRevisaoRedirect } from './pages/LegacyRevisaoRedirect';

import { ProtectedRoute } from './components/ProtectedRoute';
import { DashboardLayout } from './components/layout/DashboardLayout';

function App() {
  return (
    <>
      <Toaster position="top-right" />
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />

          <Route 
            path="/dashboard" 
            element={
              <ProtectedRoute userType="student">
                <DashboardLayout />
              </ProtectedRoute>
            }
          >
            <Route path="upload" element={<DocumentUploadPage />} />
            <Route path="review" element={<DocumentReviewPage />} />
            <Route path="approved" element={<ApprovedPage />} />
          </Route>

          <Route 
            path="/admin/usuarios" 
            element={
              <ProtectedRoute userType="admin">
                <AdminUsersPage />
              </ProtectedRoute>
            }
          >
            <Route path="revisao" element={<RevisaoList />} />
            <Route path="revisao/:id" element={<RevisaoDetalhes />} />
          </Route>

          <Route path="/revisao" element={<LegacyRevisaoRedirect />} />
          <Route path="/revisao/:id" element={<LegacyRevisaoRedirect />} />

          <Route 
            path="/admin" 
            element={
              <ProtectedRoute userType="admin">
                <AdminPage onLogout={() => window.location.href = '/login'} />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/admin/export" 
            element={
              <ProtectedRoute userType="admin">
                <AdminApiConfigPage onLogout={() => window.location.href = '/login'} />
              </ProtectedRoute>
            } 
          />
          
          <Route path="*" element={<Navigate to="/login" />} />
        </Routes>
      </BrowserRouter>
    </>
  );
}

export default App;