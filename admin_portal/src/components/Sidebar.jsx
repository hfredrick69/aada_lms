import { NavLink } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";
import { useMemo } from "react";

const baseLinks = [
  { to: "/dashboard", label: "Dashboard", icon: "📊" },
  { to: "/students", label: "Students", icon: "🎓", roles: ["Admin", "Registrar"] },
  { to: "/courses", label: "Courses", icon: "📘", roles: ["Admin", "Instructor"] },
  { to: "/payments", label: "Payments", icon: "💳", roles: ["Admin", "Finance"] },
  { to: "/externships", label: "Externships", icon: "🏥", roles: ["Admin", "Instructor"] },
  { to: "/reports", label: "Reports", icon: "🧾", roles: ["Admin", "Finance", "Registrar"] },
  { to: "/settings", label: "Settings", icon: "⚙️", roles: ["Admin"] }
];

const Sidebar = ({ mobile = false, onNavigate }) => {
  const { user, hasRole } = useAuth();

  const links = useMemo(() => {
    if (!user) return [];
    return baseLinks.filter((link) => {
      if (!link.roles) return true;
      return hasRole(link.roles);
    });
  }, [user, hasRole]);

  const containerClass = mobile
    ? "flex flex-col w-64 bg-white min-h-full"
    : "hidden lg:flex lg:flex-col w-64 bg-white border-r border-slate-200 min-h-screen";

  return (
    <aside className={containerClass}>
      <div className="px-6 py-5 border-b border-slate-200">
        <h1 className="text-xl font-semibold text-brand-700">AADA Admin</h1>
        <p className="text-xs text-slate-500 mt-1">{user?.roles?.join(" • ")}</p>
      </div>
      <nav className="flex-1 px-3 py-4 space-y-1">
        {links.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition ${
                isActive
                  ? "bg-brand-100 text-brand-700"
                  : "text-slate-600 hover:bg-slate-100 hover:text-slate-800"
              }`
            }
            onClick={() => onNavigate?.()}
          >
            <span className="text-lg" aria-hidden="true">
              {link.icon}
            </span>
            {link.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
};

export default Sidebar;
