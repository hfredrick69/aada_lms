import { Navigate, Outlet } from "react-router-dom";
import { useAuthStore } from "@/stores/auth-store";

export default function Protected() {
  const { isAuthenticated } = useAuthStore();

  // Phase 4: Tokens are in httpOnly cookies, check isAuthenticated only
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
}
