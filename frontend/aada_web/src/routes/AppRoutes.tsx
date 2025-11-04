import { Navigate, Outlet, useRoutes } from 'react-router-dom';
import type { RouteObject } from 'react-router-dom';
import { AppLayout } from '@/components/layout/AppLayout';
import { LoginPage } from '@/features/auth/LoginPage';
import { DashboardPage } from '@/features/dashboard/DashboardPage';
import { ModulesPage } from '@/features/modules/ModulesPage';
import { ModuleDetailPage } from '@/features/modules/ModuleDetailPage';
import { PaymentsPage } from '@/features/payments/PaymentsPage';
import { ExternshipsPage } from '@/features/externships/ExternshipsPage';
import { DocumentsPage } from '@/features/documents/DocumentsPage';
import { useAuthStore } from '@/stores/auth-store';

const Protected = () => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <AppLayout />;
};

const routes: RouteObject[] = [
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    element: <Protected />,
    children: [
      {
        element: <Outlet />,
        children: [
          { index: true, element: <DashboardPage /> },
          { path: 'modules', element: <ModulesPage /> },
          { path: 'modules/:moduleId', element: <ModuleDetailPage /> },
          { path: 'payments', element: <PaymentsPage /> },
          { path: 'externships', element: <ExternshipsPage /> },
          { path: 'documents', element: <DocumentsPage /> },
        ],
      },
    ],
  },
  {
    path: '*',
    element: <Navigate to="/" replace />,
  },
];

export const AppRoutes = () => {
  return useRoutes(routes);
};
