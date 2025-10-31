import { useAuth } from "../context/AuthContext.jsx";

const RoleGate = ({ allowedRoles, children }) => {
  const { hasRole } = useAuth();

  if (allowedRoles && !hasRole(allowedRoles)) {
    return (
      <div className="glass-card p-10 text-center">
        <h2 className="text-xl font-semibold text-brand-700">Restricted</h2>
        <p className="text-sm text-slate-600 mt-2">
          You do not have the correct role to access this feature. Please contact an administrator if you believe this
          is an error.
        </p>
      </div>
    );
  }

  return children;
};

export default RoleGate;
