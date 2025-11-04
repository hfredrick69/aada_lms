import { Navigate, Outlet } from "react-router-dom";
import { useAuthStore } from "@/stores/auth-store";
import { useEffect, useState } from "react";

export default function Protected() {
  const { accessToken, isAuthenticated } = useAuthStore();
  const [checked, setChecked] = useState(false);

  // Wait until Zustand has hydrated before deciding where to go
  useEffect(() => {
    // Zustand persist rehydrates asynchronously
    const stored = localStorage.getItem("aada-auth");
    setChecked(true);
  }, []);

  // Prevent rendering until store hydration is complete
  if (!checked) return null;

  // Only redirect if user is not authenticated
  if (!accessToken || !isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
}
