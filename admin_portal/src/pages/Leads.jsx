import { useEffect, useState } from "react";
import {
  listLeads,
  getLead,
  createLead,
  updateLead,
  deleteLead,
  listLeadSources,
  listLeadActivities,
  createLeadActivity,
} from "../api/leads.js";
import { listPrograms } from "../api/programs.js";
import { useAuth } from "../context/AuthContext.jsx";
import SendDocumentModal from "../components/SendDocumentModal.jsx";

const LEAD_STATUSES = ["new", "contacted", "qualified", "unqualified", "converted"];
const ACTIVITY_TYPES = ["call", "email", "sms", "meeting", "note", "task"];

const Leads = () => {
  const { hasRole } = useAuth();
  const [leads, setLeads] = useState([]);
  const [leadSources, setLeadSources] = useState([]);
  const [programs, setPrograms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedLead, setSelectedLead] = useState(null);
  const [activities, setActivities] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [showActivityModal, setShowActivityModal] = useState(false);
  const [showDocumentModal, setShowDocumentModal] = useState(false);

  // Form states
  const [form, setForm] = useState({
    first_name: "",
    last_name: "",
    email: "",
    phone: "",
    lead_source_id: "",
    program_interest_id: "",
    notes: "",
  });

  const [activityForm, setActivityForm] = useState({
    activity_type: "note",
    subject: "",
    description: "",
  });

  const [filters, setFilters] = useState({
    status: "",
    lead_source_id: "",
  });

  const canEdit = hasRole(["admin", "staff", "admissions_counselor", "admissions_manager"]);

  const loadLeads = async () => {
    setLoading(true);
    try {
      const params = {};
      if (filters.status) params.status = filters.status;
      if (filters.lead_source_id) params.lead_source_id = filters.lead_source_id;

      const data = await listLeads(params);
      setLeads(Array.isArray(data.leads) ? data.leads : []);
      setError(null);
    } catch (err) {
      console.error(err);
      setError("Unable to load leads from API");
      setLeads([]);
    } finally {
      setLoading(false);
    }
  };

  const loadLeadSources = async () => {
    try {
      const data = await listLeadSources();
      setLeadSources(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error(err);
    }
  };

  const loadPrograms = async () => {
    try {
      const data = await listPrograms();
      setPrograms(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error(err);
    }
  };

  const loadLeadDetail = async (leadId) => {
    try {
      const lead = await getLead(leadId);
      const acts = await listLeadActivities(leadId);
      setSelectedLead(lead);
      setActivities(Array.isArray(acts) ? acts : []);
      setShowModal(true);
    } catch (err) {
      console.error(err);
      setError("Unable to load lead details");
    }
  };

  useEffect(() => {
    loadLeads();
    loadLeadSources();
    loadPrograms();
  }, []);

  useEffect(() => {
    loadLeads();
  }, [filters]);

  const handleChange = (event) => {
    setForm((prev) => ({ ...prev, [event.target.name]: event.target.value }));
  };

  const handleActivityChange = (event) => {
    setActivityForm((prev) => ({ ...prev, [event.target.name]: event.target.value }));
  };

  const handleFilterChange = (event) => {
    setFilters((prev) => ({ ...prev, [event.target.name]: event.target.value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!canEdit) return;
    try {
      // Clean up form data - convert empty strings to null for optional UUID fields
      const payload = {
        ...form,
        program_interest_id: form.program_interest_id || null,
        phone: form.phone || null,
        notes: form.notes || null,
      };

      const created = await createLead(payload);
      setLeads((prev) => [created, ...prev]);
      setForm({
        first_name: "",
        last_name: "",
        email: "",
        phone: "",
        lead_source_id: "",
        program_interest_id: "",
        notes: "",
      });
      setError(null);
    } catch (err) {
      console.error(err);
      // Handle Pydantic validation errors (422)
      const detail = err?.response?.data?.detail;
      if (Array.isArray(detail)) {
        // Pydantic validation error - format the messages
        const messages = detail.map(e => `${e.loc?.slice(1).join('.')}: ${e.msg}`).join('; ');
        setError(messages || "Validation error");
      } else if (typeof detail === 'string') {
        setError(detail);
      } else {
        setError("Unable to create lead");
      }
    }
  };

  const handleStatusUpdate = async (leadId, newStatus) => {
    if (!canEdit) return;
    try {
      await updateLead(leadId, { lead_status: newStatus });
      loadLeads();
      if (selectedLead?.id === leadId) {
        loadLeadDetail(leadId);
      }
    } catch (err) {
      console.error(err);
      setError("Unable to update lead status");
    }
  };

  const handleDelete = async (leadId) => {
    if (!canEdit) return;
    if (!window.confirm("Delete this lead?")) return;
    try {
      await deleteLead(leadId);
      setLeads((prev) => prev.filter((lead) => lead.id !== leadId));
      setShowModal(false);
    } catch (err) {
      console.error(err);
      setError("Unable to delete lead");
    }
  };

  const handleAddActivity = async (event) => {
    event.preventDefault();
    if (!canEdit || !selectedLead) return;
    try {
      const payload = {
        entity_type: "lead",
        entity_id: selectedLead.id,
        ...activityForm,
      };
      await createLeadActivity(selectedLead.id, payload);
      setActivityForm({ activity_type: "note", subject: "", description: "" });
      setShowActivityModal(false);
      loadLeadDetail(selectedLead.id);
    } catch (err) {
      console.error(err);
      setError("Unable to add activity");
    }
  };

  const getStatusBadge = (status) => {
    const colors = {
      new: "bg-primary-100 text-primary-700",
      contacted: "bg-yellow-100 text-yellow-700",
      qualified: "bg-green-100 text-green-700",
      unqualified: "bg-red-100 text-red-700",
      converted: "bg-purple-100 text-purple-700",
    };
    return colors[status] || "bg-gray-100 text-gray-700";
  };

  return (
    <div className="space-y-6">
      <header className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-primary-700">Lead Management</h2>
          <p className="text-sm text-slate-500">
            Track and manage prospective student leads through the admissions pipeline.
          </p>
        </div>
      </header>

      {error && (
        <div className="glass-card p-4 bg-red-50 border border-red-200">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      {canEdit && (
        <section className="glass-card p-6">
          <h3 className="text-lg font-semibold text-primary-700">Add new lead</h3>
          <form onSubmit={handleSubmit} className="mt-4 grid grid-cols-1 sm:grid-cols-4 gap-4">
            <div>
              <label className="block text-xs font-medium text-slate-500 uppercase tracking-wide">
                First name
              </label>
              <input
                name="first_name"
                value={form.first_name}
                onChange={handleChange}
                required
                className="mt-1 block w-full rounded-md border border-slate-200 px-3 py-2 text-sm focus:border-primary-400 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-500 uppercase tracking-wide">
                Last name
              </label>
              <input
                name="last_name"
                value={form.last_name}
                onChange={handleChange}
                required
                className="mt-1 block w-full rounded-md border border-slate-200 px-3 py-2 text-sm focus:border-primary-400 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-500 uppercase tracking-wide">
                Email
              </label>
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
              <label className="block text-xs font-medium text-slate-500 uppercase tracking-wide">
                Phone
              </label>
              <input
                name="phone"
                value={form.phone}
                onChange={handleChange}
                className="mt-1 block w-full rounded-md border border-slate-200 px-3 py-2 text-sm focus:border-primary-400 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-500 uppercase tracking-wide">
                Lead source
              </label>
              <select
                name="lead_source_id"
                value={form.lead_source_id}
                onChange={handleChange}
                required
                className="mt-1 block w-full rounded-md border border-slate-200 px-3 py-2 text-sm focus:border-primary-400 focus:outline-none"
              >
                <option value="">Select source</option>
                {leadSources.map((source) => (
                  <option key={source.id} value={source.id}>
                    {source.name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-500 uppercase tracking-wide">
                Program interest
              </label>
              <select
                name="program_interest_id"
                value={form.program_interest_id}
                onChange={handleChange}
                className="mt-1 block w-full rounded-md border border-slate-200 px-3 py-2 text-sm focus:border-primary-400 focus:outline-none"
              >
                <option value="">No preference</option>
                {programs.map((program) => (
                  <option key={program.id} value={program.id}>
                    {program.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="sm:col-span-2">
              <label className="block text-xs font-medium text-slate-500 uppercase tracking-wide">
                Notes
              </label>
              <input
                name="notes"
                value={form.notes}
                onChange={handleChange}
                className="mt-1 block w-full rounded-md border border-slate-200 px-3 py-2 text-sm focus:border-primary-400 focus:outline-none"
              />
            </div>
            <div className="flex items-end">
              <button
                type="submit"
                className="w-full px-4 py-2 bg-primary-600 text-white text-sm font-semibold rounded-lg hover:bg-primary-700 transition"
              >
                Add Lead
              </button>
            </div>
          </form>
        </section>
      )}

      <section className="glass-card p-6">
        <div className="flex flex-col sm:flex-row gap-4 mb-4">
          <div className="flex-1">
            <label className="block text-xs font-medium text-slate-500 uppercase tracking-wide">
              Filter by status
            </label>
            <select
              name="status"
              value={filters.status}
              onChange={handleFilterChange}
              className="mt-1 block w-full rounded-md border border-slate-200 px-3 py-2 text-sm focus:border-primary-400 focus:outline-none"
            >
              <option value="">All statuses</option>
              {LEAD_STATUSES.map((status) => (
                <option key={status} value={status}>
                  {status.charAt(0).toUpperCase() + status.slice(1)}
                </option>
              ))}
            </select>
          </div>
          <div className="flex-1">
            <label className="block text-xs font-medium text-slate-500 uppercase tracking-wide">
              Filter by source
            </label>
            <select
              name="lead_source_id"
              value={filters.lead_source_id}
              onChange={handleFilterChange}
              className="mt-1 block w-full rounded-md border border-slate-200 px-3 py-2 text-sm focus:border-primary-400 focus:outline-none"
            >
              <option value="">All sources</option>
              {leadSources.map((source) => (
                <option key={source.id} value={source.id}>
                  {source.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        {loading ? (
          <div className="text-center py-8 text-slate-500">Loading leads...</div>
        ) : leads.length === 0 ? (
          <div className="text-center py-8 text-slate-500">No leads found</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-slate-200">
                <tr className="text-xs text-slate-500 uppercase tracking-wide">
                  <th className="px-4 py-3">Name</th>
                  <th className="px-4 py-3">Email</th>
                  <th className="px-4 py-3">Phone</th>
                  <th className="px-4 py-3">Source</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Score</th>
                  <th className="px-4 py-3">Created</th>
                  <th className="px-4 py-3">Actions</th>
                </tr>
              </thead>
              <tbody>
                {leads.map((lead) => (
                  <tr key={lead.id} className="border-b border-slate-100 hover:bg-slate-50">
                    <td className="px-4 py-3">
                      <button
                        onClick={() => loadLeadDetail(lead.id)}
                        className="text-primary-600 hover:text-primary-800 font-medium"
                      >
                        {lead.first_name} {lead.last_name}
                      </button>
                    </td>
                    <td className="px-4 py-3">{lead.email}</td>
                    <td className="px-4 py-3">{lead.phone || "-"}</td>
                    <td className="px-4 py-3">
                      {leadSources.find((s) => s.id === lead.lead_source_id)?.name || "-"}
                    </td>
                    <td className="px-4 py-3">
                      {canEdit ? (
                        <select
                          value={lead.lead_status}
                          onChange={(e) => handleStatusUpdate(lead.id, e.target.value)}
                          className={`px-2 py-1 rounded text-xs font-medium ${getStatusBadge(
                            lead.lead_status
                          )}`}
                        >
                          {LEAD_STATUSES.map((status) => (
                            <option key={status} value={status}>
                              {status.charAt(0).toUpperCase() + status.slice(1)}
                            </option>
                          ))}
                        </select>
                      ) : (
                        <span
                          className={`inline-block px-2 py-1 rounded text-xs font-medium ${getStatusBadge(
                            lead.lead_status
                          )}`}
                        >
                          {lead.lead_status.charAt(0).toUpperCase() + lead.lead_status.slice(1)}
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3">{lead.lead_score}</td>
                    <td className="px-4 py-3">
                      {new Date(lead.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-4 py-3">
                      <button
                        onClick={() => loadLeadDetail(lead.id)}
                        className="text-primary-600 hover:text-primary-800 text-sm"
                      >
                        View
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {/* Lead Detail Modal */}
      {showModal && selectedLead && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-slate-200 flex justify-between items-start">
              <div>
                <h3 className="text-xl font-semibold text-primary-700">
                  {selectedLead.first_name} {selectedLead.last_name}
                </h3>
                <p className="text-sm text-slate-500">{selectedLead.email}</p>
              </div>
              <button
                onClick={() => setShowModal(false)}
                className="text-slate-400 hover:text-slate-600"
              >
                ✕
              </button>
            </div>

            <div className="p-6 space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-xs text-slate-500 uppercase tracking-wide">Phone</p>
                  <p className="text-sm font-medium">{selectedLead.phone || "-"}</p>
                </div>
                <div>
                  <p className="text-xs text-slate-500 uppercase tracking-wide">Status</p>
                  <p className="text-sm font-medium">
                    {selectedLead.lead_status.charAt(0).toUpperCase() +
                      selectedLead.lead_status.slice(1)}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-slate-500 uppercase tracking-wide">Lead Score</p>
                  <p className="text-sm font-medium">{selectedLead.lead_score}</p>
                </div>
                <div>
                  <p className="text-xs text-slate-500 uppercase tracking-wide">Program Interest</p>
                  <p className="text-sm font-medium">
                    {selectedLead.program_interest_name || "No preference"}
                  </p>
                </div>
              </div>

              {selectedLead.notes && (
                <div>
                  <p className="text-xs text-slate-500 uppercase tracking-wide">Notes</p>
                  <p className="text-sm mt-1">{selectedLead.notes}</p>
                </div>
              )}

              <div>
                <div className="flex justify-between items-center mb-4">
                  <h4 className="text-sm font-semibold text-slate-700">Activity Timeline</h4>
                  {canEdit && (
                    <button
                      onClick={() => setShowActivityModal(true)}
                      className="px-3 py-1 bg-primary-600 text-white text-xs font-semibold rounded hover:bg-primary-700 transition"
                    >
                      Add Activity
                    </button>
                  )}
                </div>

                {activities.length === 0 ? (
                  <p className="text-sm text-slate-500 text-center py-4">No activities yet</p>
                ) : (
                  <div className="space-y-3">
                    {activities.map((activity) => (
                      <div
                        key={activity.id}
                        className="border-l-2 border-primary-300 pl-4 py-2"
                      >
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-semibold text-primary-600 uppercase">
                            {activity.activity_type}
                          </span>
                          <span className="text-xs text-slate-500">
                            {new Date(activity.created_at).toLocaleString()}
                          </span>
                        </div>
                        {activity.subject && (
                          <p className="text-sm font-medium mt-1">{activity.subject}</p>
                        )}
                        {activity.description && (
                          <p className="text-sm text-slate-600 mt-1">{activity.description}</p>
                        )}
                        {activity.created_by_name && (
                          <p className="text-xs text-slate-500 mt-1">
                            by {activity.created_by_name}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {canEdit && (
                <div className="flex gap-2 justify-end pt-4 border-t border-slate-200">
                  <button
                    onClick={() => setShowDocumentModal(true)}
                    className="px-4 py-2 bg-primary-600 text-white text-sm font-semibold rounded-lg hover:bg-primary-700 transition"
                  >
                    Send Document
                  </button>
                  <button
                    onClick={() => handleDelete(selectedLead.id)}
                    className="px-4 py-2 bg-red-600 text-white text-sm font-semibold rounded-lg hover:bg-red-700 transition"
                  >
                    Delete Lead
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Add Activity Modal */}
      {showActivityModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-lg w-full">
            <div className="p-6 border-b border-slate-200 flex justify-between items-center">
              <h3 className="text-lg font-semibold text-primary-700">Add Activity</h3>
              <button
                onClick={() => setShowActivityModal(false)}
                className="text-slate-400 hover:text-slate-600"
              >
                ✕
              </button>
            </div>
            <form onSubmit={handleAddActivity} className="p-6 space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-500 uppercase tracking-wide">
                  Activity Type
                </label>
                <select
                  name="activity_type"
                  value={activityForm.activity_type}
                  onChange={handleActivityChange}
                  required
                  className="mt-1 block w-full rounded-md border border-slate-200 px-3 py-2 text-sm focus:border-primary-400 focus:outline-none"
                >
                  {ACTIVITY_TYPES.map((type) => (
                    <option key={type} value={type}>
                      {type.charAt(0).toUpperCase() + type.slice(1)}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-500 uppercase tracking-wide">
                  Subject
                </label>
                <input
                  name="subject"
                  value={activityForm.subject}
                  onChange={handleActivityChange}
                  required
                  className="mt-1 block w-full rounded-md border border-slate-200 px-3 py-2 text-sm focus:border-primary-400 focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-500 uppercase tracking-wide">
                  Description
                </label>
                <textarea
                  name="description"
                  value={activityForm.description}
                  onChange={handleActivityChange}
                  rows={4}
                  className="mt-1 block w-full rounded-md border border-slate-200 px-3 py-2 text-sm focus:border-primary-400 focus:outline-none"
                ></textarea>
              </div>
              <div className="flex gap-2 justify-end">
                <button
                  type="button"
                  onClick={() => setShowActivityModal(false)}
                  className="px-4 py-2 bg-slate-200 text-slate-700 text-sm font-semibold rounded-lg hover:bg-slate-300 transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-primary-600 text-white text-sm font-semibold rounded-lg hover:bg-primary-700 transition"
                >
                  Add Activity
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Send Document Modal */}
      {showDocumentModal && selectedLead && (
        <SendDocumentModal
          lead={selectedLead}
          onClose={() => setShowDocumentModal(false)}
        />
      )}
    </div>
  );
};

export default Leads;
