import { useAuth } from "../context/AuthContext.jsx";
import { Link } from "react-router-dom";

const Topbar = ({ onToggleSidebar }) => {
  const { user, logout } = useAuth();

  const appName = import.meta.env.VITE_APP_NAME || "AADA Admin Portal";

  return (
    <header className="sticky top-0 z-40 bg-white/80 backdrop-blur border-b border-slate-200">
      <div className="flex items-center justify-between px-4 lg:px-6 py-3">
        <div className="flex items-center gap-3">
          <button
            onClick={onToggleSidebar}
            className="lg:hidden inline-flex items-center justify-center p-2 rounded-md text-slate-600 hover:bg-slate-100"
            aria-label="Toggle navigation"
          >
            ☰
          </button>
          <Link to="/dashboard" className="text-lg font-semibold text-brand-700">
            {appName}
          </Link>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-right">
            <p className="text-sm font-medium text-slate-700">{user?.first_name} {user?.last_name}</p>
            <p className="text-xs text-slate-500">{user?.email}</p>
          </div>
          <button
            onClick={logout}
            className="px-3 py-1.5 rounded-md text-sm font-medium bg-brand-100 text-brand-700 hover:bg-brand-200 transition"
          >
            Sign out
          </button>
        </div>
      </div>
    </header>
  );
};

export default Topbar;
