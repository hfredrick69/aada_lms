import { Routes, Route, Navigate } from "react-router-dom";
import LoginPage from "@/features/auth/LoginPage";
import DashboardPage from "@/features/dashboard/DashboardPage";
import DocumentsPage from "@/features/documents/DocumentsPage";
import ModulesPage from "@/features/modules/ModulesPage";
import ModulePlayerPage from "@/features/modules/ModulePlayerPage";
import PaymentsPage from "@/features/payments/PaymentsPage";
import ExternshipsPage from "@/features/externships/ExternshipsPage";
import PublicSign from "@/pages/PublicSign";
import AppLayout from "@/components/layout/AppLayout";
import Protected from "@/routes/Protected";

export default function App() {
  return (
    <Routes>
      {/* Default route */}
      <Route path="/" element={<Navigate to="/login" replace />} />

      {/* Public routes */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/sign/:token" element={<PublicSign />} />

      {/* Protected routes */}
      <Route element={<Protected />}>
        <Route element={<AppLayout />}>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/documents" element={<DocumentsPage />} />
          <Route path="/modules" element={<ModulesPage />} />
          <Route path="/modules/:id" element={<ModulePlayerPage />} />
          <Route path="/payments" element={<PaymentsPage />} />
          <Route path="/externships" element={<ExternshipsPage />} />
        </Route>
      </Route>
    </Routes>
  );
}
