import { useAuth } from "../context/AuthContext.jsx";

const roleMatrix = [
  {
    role: "admin",
    description: "Full system access including role management, program configuration, and delete permissions.",
    permissions: ["Dashboard", "All CRUD operations", "Settings", "Delete permissions"]
  },
  {
    role: "staff",
    description: "Instructor permissions plus ability to create/update student records.",
    permissions: ["Dashboard", "Students CRUD", "Courses (view)", "Payments", "Externships", "Reports"]
  },
  {
    role: "instructor",
    description: "View courses/modules, manage grades/attendance for assigned students, and manage externships.",
    permissions: ["Dashboard", "Courses (view)", "Students (assigned, read-only)", "Externships", "Grades/Attendance"]
  },
  {
    role: "finance",
    description: "View and reconcile invoices, refunds, and compliance reports.",
    permissions: ["Dashboard", "Payments", "Reports"]
  },
  {
    role: "registrar",
    description: "Oversee student records, enrollments, and transcript requests.",
    permissions: ["Dashboard", "Students", "Reports"]
  },
  {
    role: "student",
    description: "Access own enrollment, coursework, grades, and progress.",
    permissions: ["Student Portal", "Own Records", "Course Materials"]
  }
];

const Settings = () => {
  const { user } = useAuth();

  return (
    <div className="space-y-6">
      <header>
        <h2 className="text-2xl font-semibold text-primary-700">Role & Permission Matrix</h2>
        <p className="text-sm text-slate-500">
          Administrators can reference roles below when provisioning new accounts through the API.
        </p>
      </header>

      <section className="glass-card p-6 space-y-4">
        <p className="text-sm text-slate-600">
          Signed in as <span className="font-medium text-primary-700">{user?.email}</span>
          {user?.roles?.length ? ` (${user.roles.join(", ")})` : ""}.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {roleMatrix.map((role) => (
            <div key={role.role} className="border border-slate-200 rounded-xl p-5 bg-white">
              <h3 className="text-lg font-semibold text-primary-700">{role.role}</h3>
              <p className="text-sm text-slate-500 mt-1">{role.description}</p>
              <ul className="mt-3 space-y-1 text-sm text-slate-600">
                {role.permissions.map((permission) => (
                  <li key={permission}>• {permission}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
        <p className="text-xs text-slate-400">
          Update roles by calling <code className="bg-slate-100 px-1 py-0.5 rounded">PATCH /api/users/:id</code> with the
          desired role assignments. Be sure to audit changes for GNPEC compliance.
        </p>
      </section>
    </div>
  );
};

export default Settings;
