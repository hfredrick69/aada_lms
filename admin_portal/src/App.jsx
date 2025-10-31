import { Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Students from "./pages/Students.jsx";
import Courses from "./pages/Courses.jsx";
import Payments from "./pages/Payments.jsx";
import Externships from "./pages/Externships.jsx";
import Reports from "./pages/Reports.jsx";
import Settings from "./pages/Settings.jsx";
import ProtectedRoute from "./components/ProtectedRoute.jsx";
import RoleGate from "./components/RoleGate.jsx";

const App = () => {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route element={<ProtectedRoute />}>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route
          path="/students"
          element={
            <RoleGate allowedRoles={["Admin", "Registrar"]}>
              <Students />
            </RoleGate>
          }
        />
        <Route
          path="/courses"
          element={
            <RoleGate allowedRoles={["Admin", "Instructor"]}>
              <Courses />
            </RoleGate>
          }
        />
        <Route
          path="/payments"
          element={
            <RoleGate allowedRoles={["Admin", "Finance"]}>
              <Payments />
            </RoleGate>
          }
        />
        <Route
          path="/externships"
          element={
            <RoleGate allowedRoles={["Admin", "Instructor"]}>
              <Externships />
            </RoleGate>
          }
        />
        <Route
          path="/reports"
          element={
            <RoleGate allowedRoles={["Admin", "Finance", "Registrar"]}>
              <Reports />
            </RoleGate>
          }
        />
        <Route
          path="/settings"
          element={
            <RoleGate allowedRoles={["Admin"]}>
              <Settings />
            </RoleGate>
          }
        />
      </Route>
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
};

export default App;
