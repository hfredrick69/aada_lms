import { useEffect, useState } from "react";
import { createStudent, deleteStudent, listStudents } from "../api/students.js";
import { useAuth } from "../context/AuthContext.jsx";

const Students = () => {
  const { hasRole } = useAuth();
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState({ first_name: "", last_name: "", email: "", password: "" });
  const [error, setError] = useState(null);

  const canEdit = hasRole(["admin", "staff"]);

  const loadStudents = async () => {
    setLoading(true);
    try {
      const data = await listStudents();
      setStudents(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error(err);
      setError("Unable to load students from API. Showing placeholder data.");
      setStudents([
        { id: "demo-1", first_name: "Demo", last_name: "Student", email: "demo.student@aada.edu", status: "active" }
      ]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStudents();
  }, []);

  const handleChange = (event) => {
    setForm((prev) => ({ ...prev, [event.target.name]: event.target.value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!canEdit) return;
    try {
      const created = await createStudent(form);
      setStudents((prev) => [created, ...prev]);
      setForm({ first_name: "", last_name: "", email: "", password: "" });
      setError(null);
    } catch (err) {
      console.error(err);
      setError(err?.response?.data?.detail || "Unable to create student");
    }
  };

  const handleDelete = async (studentId) => {
    if (!canEdit) return;
    if (!window.confirm("Remove this student?")) return;
    try {
      await deleteStudent(studentId);
      setStudents((prev) => prev.filter((student) => student.id !== studentId));
    } catch (err) {
      console.error(err);
      setError("Unable to delete student record.");
    }
  };

  return (
    <div className="space-y-6">
      <header className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-primary-700">Student Management</h2>
          <p className="text-sm text-slate-500">
            Search, onboard, and maintain student enrollments across programs.
          </p>
        </div>
      </header>

      {canEdit && (
        <section className="glass-card p-6">
          <h3 className="text-lg font-semibold text-primary-700">Add new student</h3>
          <form onSubmit={handleSubmit} className="mt-4 grid grid-cols-1 sm:grid-cols-4 gap-4">
            <div>
              <label className="block text-xs font-medium text-slate-500 uppercase tracking-wide">First name</label>
              <input
                name="first_name"
                value={form.first_name}
                onChange={handleChange}
                required
                className="mt-1 block w-full rounded-md border border-slate-200 px-3 py-2 text-sm focus:border-primary-400 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-500 uppercase tracking-wide">Last name</label>
              <input
                name="last_name"
                value={form.last_name}
                onChange={handleChange}
                required
                className="mt-1 block w-full rounded-md border border-slate-200 px-3 py-2 text-sm focus:border-primary-400 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-500 uppercase tracking-wide">Email</label>
              <input
                name="email"
                type="email"
                value={form.email}
                onChange={handleChange}
                required
                className="mt-1 block w-full rounded-md border border-slate-200 px-3 py-2 text-sm focus:border-primary-400 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-500 uppercase tracking-wide">Password</label>
              <input
                name="password"
                type="password"
                value={form.password}
                onChange={handleChange}
                required
                className="mt-1 block w-full rounded-md border border-slate-200 px-3 py-2 text-sm focus:border-primary-400 focus:outline-none"
              />
            </div>
            <div className="sm:col-span-4 flex justify-end">
              <button
                type="submit"
                className="px-4 py-2 rounded-md bg-primary-500 text-white text-sm font-medium hover:bg-primary-600 transition"
              >
                Create student
              </button>
            </div>
          </form>
        </section>
      )}

      {error && <div className="glass-card p-4 text-sm text-red-600">{error}</div>}

      <section className="glass-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200">
            <thead className="bg-primary-100 text-primary-700">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide">Name</th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide">Email</th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide">Status</th>
                {canEdit && <th className="px-4 py-3" />}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan={canEdit ? 4 : 3} className="px-4 py-6 text-center text-sm text-slate-500">
                    Loading students...
                  </td>
                </tr>
              ) : students.length === 0 ? (
                <tr>
                  <td colSpan={canEdit ? 4 : 3} className="px-4 py-6 text-center text-sm text-slate-500">
                    No students found.
                  </td>
                </tr>
              ) : (
                students.map((student) => (
                  <tr key={student.id}>
                    <td className="px-4 py-3 text-sm text-slate-700">
                      {student.first_name} {student.last_name}
                    </td>
                    <td className="px-4 py-3 text-sm text-slate-600">{student.email}</td>
                    <td className="px-4 py-3 text-sm">
                      <span className="inline-flex items-center rounded-full bg-primary-100 px-2 py-1 text-xs font-medium text-primary-700">
                        {student.status || "active"}
                      </span>
                    </td>
                    {canEdit && (
                      <td className="px-4 py-3 text-right">
                        <button
                          onClick={() => handleDelete(student.id)}
                          className="text-xs font-medium text-red-500 hover:text-red-600"
                        >
                          Remove
                        </button>
                      </td>
                    )}
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
};

export default Students;
