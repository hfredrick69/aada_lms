import { useEffect, useState } from "react";
import { assignExternship, listExternships, updateExternship } from "../api/externships.js";
import { useAuth } from "../context/AuthContext.jsx";

const defaultForm = {
  user_id: "",
  site_name: "",
  total_hours: 0
};

const Externships = () => {
  const { hasRole } = useAuth();
  const [externships, setExternships] = useState([]);
  const [form, setForm] = useState(defaultForm);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const canEdit = hasRole(["Admin", "Instructor"]);

  const loadExternships = async () => {
    setLoading(true);
    try {
      const data = await listExternships();
      setExternships(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error(err);
      setError("Externship endpoint unavailable. Displaying sample data.");
      setExternships([
        {
          id: "demo-extern-1",
          student_name: "Alice Student",
          site_name: "Acme Care Clinic",
          total_hours: 160,
          verified: true,
          verification_doc_url: "https://cdn.aada.edu/docs/externship/alice.pdf"
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadExternships();
  }, []);

  const handleChange = (event) => {
    setForm((prev) => ({ ...prev, [event.target.name]: event.target.value }));
  };

  const handleAssign = async (event) => {
    event.preventDefault();
    if (!canEdit) return;
    try {
      const created = await assignExternship({
        ...form,
        total_hours: Number(form.total_hours)
      });
      setExternships((prev) => [created, ...prev]);
      setForm(defaultForm);
      setError(null);
    } catch (err) {
      console.error(err);
      setError(err?.response?.data?.detail || "Unable to assign externship.");
    }
  };

  const handleApprove = async (externship) => {
    if (!canEdit) return;
    try {
      const updated = await updateExternship(externship.id, { verified: true, verified_at: new Date().toISOString() });
      setExternships((prev) => prev.map((item) => (item.id === externship.id ? updated : item)));
    } catch (err) {
      console.error(err);
      setError("Unable to approve externship.");
    }
  };

  return (
    <div className="space-y-6">
      <header>
        <h2 className="text-2xl font-semibold text-brand-700">Externship Placement</h2>
        <p className="text-sm text-slate-500">
          Track placement sites, verification documents, and approval workflow for clinical hours.
        </p>
      </header>

      {canEdit && (
        <section className="glass-card p-6">
          <h3 className="text-lg font-semibold text-brand-700">Assign externship</h3>
          <form onSubmit={handleAssign} className="mt-4 grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="md:col-span-1">
              <label className="block text-xs font-medium text-slate-500 uppercase tracking-wide">Student ID</label>
              <input
                name="user_id"
                value={form.user_id}
                onChange={handleChange}
                placeholder="UUID"
                required
                className="mt-1 block w-full rounded-md border border-slate-200 px-3 py-2 text-sm focus:border-brand-400 focus:outline-none"
              />
            </div>
            <div className="md:col-span-2">
              <label className="block text-xs font-medium text-slate-500 uppercase tracking-wide">Site name</label>
              <input
                name="site_name"
                value={form.site_name}
                onChange={handleChange}
                placeholder="Partner clinic"
                required
                className="mt-1 block w-full rounded-md border border-slate-200 px-3 py-2 text-sm focus:border-brand-400 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-500 uppercase tracking-wide">Hours</label>
              <input
                name="total_hours"
                type="number"
                value={form.total_hours}
                onChange={handleChange}
                min={0}
                className="mt-1 block w-full rounded-md border border-slate-200 px-3 py-2 text-sm focus:border-brand-400 focus:outline-none"
              />
            </div>
            <div className="md:col-span-4 flex justify-end">
              <button
                type="submit"
                className="px-4 py-2 rounded-md bg-brand-500 text-white text-sm font-medium hover:bg-brand-600 transition"
              >
                Assign externship
              </button>
            </div>
          </form>
        </section>
      )}

      {error && <div className="glass-card p-4 text-sm text-red-600">{error}</div>}

      <section className="glass-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200">
            <thead className="bg-brand-100 text-brand-700">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide">Student</th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide">Site</th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide">Hours</th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide">Verified</th>
                {canEdit && <th className="px-4 py-3" />}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan={canEdit ? 5 : 4} className="px-4 py-6 text-center text-sm text-slate-500">
                    Loading externships...
                  </td>
                </tr>
              ) : externships.length === 0 ? (
                <tr>
                  <td colSpan={canEdit ? 5 : 4} className="px-4 py-6 text-center text-sm text-slate-500">
                    No externships assigned yet.
                  </td>
                </tr>
              ) : (
                externships.map((externship) => (
                  <tr key={externship.id}>
                    <td className="px-4 py-3 text-sm text-slate-600">
                      {externship.student_name || externship.user_id}
                    </td>
                    <td className="px-4 py-3 text-sm text-slate-600">{externship.site_name}</td>
                    <td className="px-4 py-3 text-sm text-slate-600">{externship.total_hours}</td>
                    <td className="px-4 py-3 text-sm">
                      {externship.verified ? (
                        <span className="inline-flex rounded-full bg-emerald-100 px-2 py-1 text-xs font-semibold text-emerald-600">
                          Verified
                        </span>
                      ) : (
                        <span className="inline-flex rounded-full bg-amber-100 px-2 py-1 text-xs font-semibold text-amber-600">
                          Pending
                        </span>
                      )}
                    </td>
                    {canEdit && (
                      <td className="px-4 py-3 text-right">
                        {!externship.verified && (
                          <button
                            onClick={() => handleApprove(externship)}
                            className="text-xs font-medium text-brand-600 hover:text-brand-700"
                          >
                            Approve
                          </button>
                        )}
                        {externship.verification_doc_url && (
                          <a
                            href={externship.verification_doc_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="ml-3 text-xs font-medium text-slate-500 hover:text-slate-700"
                          >
                            Evidence
                          </a>
                        )}
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

export default Externships;
