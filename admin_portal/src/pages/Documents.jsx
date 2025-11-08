import { useEffect, useState } from "react";
import {
  listDocumentTemplates,
  createDocumentTemplate,
  sendDocumentToUser,
  sendDocumentToLead,
  getUserDocuments,
  getLeadDocuments,
  getAllDocuments,
  downloadDocument,
} from "../api/documents.js";
import { listStudents } from "../api/students.js";
import { listLeads } from "../api/leads.js";
import { useAuth } from "../context/AuthContext.jsx";
import AuditTrailDialog from "../components/AuditTrailDialog.jsx";

const Documents = () => {
  const { hasRole } = useAuth();
  const [activeTab, setActiveTab] = useState("templates");
  const [templates, setTemplates] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [users, setUsers] = useState([]);
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [recipientType, setRecipientType] = useState("user");
  const [selectedRecipientId, setSelectedRecipientId] = useState("");
  const [selectedTemplateId, setSelectedTemplateId] = useState("");
  const [auditTrailOpen, setAuditTrailOpen] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState(null);

  // Template upload form
  const [templateForm, setTemplateForm] = useState({
    name: "",
    version: "1.0",
    description: "",
    requires_counter_signature: false,
  });
  const [selectedFile, setSelectedFile] = useState(null);

  const canEdit = hasRole(["admin", "staff"]);

  const loadTemplates = async () => {
    setLoading(true);
    try {
      const data = await listDocumentTemplates(false);
      setTemplates(Array.isArray(data) ? data : []);
      setError(null);
    } catch (err) {
      console.error(err);
      setError("Unable to load document templates");
      setTemplates([]);
    } finally {
      setLoading(false);
    }
  };

  const loadUsers = async () => {
    try {
      const data = await listStudents();
      setUsers(Array.isArray(data.students) ? data.students : []);
    } catch (err) {
      console.error(err);
    }
  };

  const loadLeads = async () => {
    try {
      const data = await listLeads({});
      setLeads(Array.isArray(data.leads) ? data.leads : []);
    } catch (err) {
      console.error(err);
    }
  };

  const loadDocumentsByUser = async (userId) => {
    setLoading(true);
    try {
      const data = await getUserDocuments(userId);
      setDocuments(Array.isArray(data.documents) ? data.documents : []);
      setError(null);
    } catch (err) {
      console.error(err);
      setError("Unable to load user documents");
      setDocuments([]);
    } finally {
      setLoading(false);
    }
  };

  const loadDocumentsByLead = async (leadId) => {
    setLoading(true);
    try {
      const data = await getLeadDocuments(leadId);
      setDocuments(Array.isArray(data.documents) ? data.documents : []);
      setError(null);
    } catch (err) {
      console.error(err);
      setError("Unable to load lead documents");
      setDocuments([]);
    } finally {
      setLoading(false);
    }
  };

  const loadAllDocuments = async () => {
    setLoading(true);
    try {
      const data = await getAllDocuments();
      setDocuments(Array.isArray(data.documents) ? data.documents : []);
      setError(null);
    } catch (err) {
      console.error(err);
      setError("Unable to load all documents");
      setDocuments([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTemplates();
    loadUsers();
    loadLeads();
  }, []);

  useEffect(() => {
    if (activeTab === "all") {
      loadAllDocuments();
    } else if (activeTab === "documents" && selectedRecipientId) {
      if (recipientType === "user") {
        loadDocumentsByUser(selectedRecipientId);
      } else {
        loadDocumentsByLead(selectedRecipientId);
      }
    }
  }, [activeTab, selectedRecipientId, recipientType]);

  const handleTemplateFormChange = (e) => {
    const { name, value, type, checked } = e.target;
    setTemplateForm((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0]);
  };

  const handleTemplateSubmit = async (e) => {
    e.preventDefault();
    if (!canEdit) return;
    if (!selectedFile) {
      setError("Please select a PDF file");
      return;
    }

    const formData = new FormData();
    formData.append("name", templateForm.name);
    formData.append("version", templateForm.version);
    formData.append("description", templateForm.description);
    formData.append("requires_counter_signature", templateForm.requires_counter_signature);
    formData.append("pdf_file", selectedFile);

    try {
      await createDocumentTemplate(formData);
      setTemplateForm({
        name: "",
        version: "1.0",
        description: "",
        requires_counter_signature: false,
      });
      setSelectedFile(null);
      loadTemplates();
      setError(null);
    } catch (err) {
      console.error(err);
      setError(err?.response?.data?.detail || "Unable to upload template");
    }
  };

  const handleSendDocument = async () => {
    if (!selectedTemplateId || !selectedRecipientId) {
      setError("Please select both a template and a recipient");
      return;
    }

    try {
      if (recipientType === "user") {
        await sendDocumentToUser(selectedTemplateId, selectedRecipientId);
      } else {
        await sendDocumentToLead(selectedTemplateId, selectedRecipientId);
      }
      setError(null);
      alert("Document sent successfully!");
      setSelectedTemplateId("");
      if (activeTab === "documents") {
        if (recipientType === "user") {
          loadDocumentsByUser(selectedRecipientId);
        } else {
          loadDocumentsByLead(selectedRecipientId);
        }
      }
    } catch (err) {
      console.error(err);
      setError(err?.response?.data?.detail || "Unable to send document");
    }
  };

  const handleDownload = async (doc) => {
    try {
      await downloadDocument(doc.id, `${doc.template_name}_${doc.id}.pdf`);
    } catch (err) {
      console.error(err);
      setError("Unable to download document");
    }
  };

  const handleViewAuditTrail = (doc) => {
    setSelectedDocument(doc);
    setAuditTrailOpen(true);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const getStatusBadge = (status) => {
    const colors = {
      pending: "bg-yellow-100 text-yellow-700",
      signed: "bg-green-100 text-green-700",
      partially_signed: "bg-blue-100 text-blue-700",
      voided: "bg-red-100 text-red-700",
    };
    return colors[status] || "bg-gray-100 text-gray-700";
  };

  return (
    <div className="space-y-6">
      <header className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-primary-700">Document Management</h2>
          <p className="text-sm text-slate-500">
            Manage document templates and send documents for electronic signature.
          </p>
        </div>
      </header>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      {/* Tabs */}
      <div className="border-b border-slate-200">
        <div className="flex gap-4">
          <button
            onClick={() => setActiveTab("templates")}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition ${
              activeTab === "templates"
                ? "border-primary-600 text-primary-600"
                : "border-transparent text-slate-500 hover:text-slate-700"
            }`}
          >
            Templates
          </button>
          <button
            onClick={() => setActiveTab("documents")}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition ${
              activeTab === "documents"
                ? "border-primary-600 text-primary-600"
                : "border-transparent text-slate-500 hover:text-slate-700"
            }`}
          >
            Documents
          </button>
          <button
            onClick={() => setActiveTab("all")}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition ${
              activeTab === "all"
                ? "border-primary-600 text-primary-600"
                : "border-transparent text-slate-500 hover:text-slate-700"
            }`}
          >
            All Documents
          </button>
        </div>
      </div>

      {/* Templates Tab */}
      {activeTab === "templates" && (
        <>
          {canEdit && (
            <section className="glass-card p-6">
              <h3 className="text-lg font-semibold text-primary-700 mb-4">Upload New Template</h3>
              <form onSubmit={handleTemplateSubmit} className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-500 uppercase tracking-wide">
                    Template Name
                  </label>
                  <input
                    name="name"
                    value={templateForm.name}
                    onChange={handleTemplateFormChange}
                    required
                    className="mt-1 block w-full rounded-md border border-slate-200 px-3 py-2 text-sm focus:border-primary-400 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-500 uppercase tracking-wide">
                    Version
                  </label>
                  <input
                    name="version"
                    value={templateForm.version}
                    onChange={handleTemplateFormChange}
                    required
                    className="mt-1 block w-full rounded-md border border-slate-200 px-3 py-2 text-sm focus:border-primary-400 focus:outline-none"
                  />
                </div>
                <div className="sm:col-span-2">
                  <label className="block text-xs font-medium text-slate-500 uppercase tracking-wide">
                    Description
                  </label>
                  <textarea
                    name="description"
                    value={templateForm.description}
                    onChange={handleTemplateFormChange}
                    rows={3}
                    className="mt-1 block w-full rounded-md border border-slate-200 px-3 py-2 text-sm focus:border-primary-400 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-500 uppercase tracking-wide">
                    PDF File
                  </label>
                  <input
                    type="file"
                    accept=".pdf"
                    onChange={handleFileChange}
                    required
                    className="mt-1 block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100"
                  />
                </div>
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="requires_counter_signature"
                    name="requires_counter_signature"
                    checked={templateForm.requires_counter_signature}
                    onChange={handleTemplateFormChange}
                    className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-slate-300 rounded"
                  />
                  <label htmlFor="requires_counter_signature" className="ml-2 text-sm text-slate-700">
                    Requires counter-signature
                  </label>
                </div>
                <div className="sm:col-span-2">
                  <button
                    type="submit"
                    className="px-4 py-2 bg-primary-600 text-white text-sm font-semibold rounded-lg hover:bg-primary-700 transition"
                  >
                    Upload Template
                  </button>
                </div>
              </form>
            </section>
          )}

          <section className="glass-card p-6">
            <h3 className="text-lg font-semibold text-primary-700 mb-4">Available Templates</h3>
            {loading ? (
              <div className="text-center py-8 text-slate-500">Loading templates...</div>
            ) : templates.length === 0 ? (
              <div className="text-center py-8 text-slate-500">No templates found</div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead className="border-b border-slate-200">
                    <tr className="text-xs text-slate-500 uppercase tracking-wide">
                      <th className="px-4 py-3">Name</th>
                      <th className="px-4 py-3">Version</th>
                      <th className="px-4 py-3">Description</th>
                      <th className="px-4 py-3">Counter-Sig</th>
                      <th className="px-4 py-3">Active</th>
                      <th className="px-4 py-3">Created</th>
                    </tr>
                  </thead>
                  <tbody>
                    {templates.map((template) => (
                      <tr key={template.id} className="border-b border-slate-100 hover:bg-slate-50">
                        <td className="px-4 py-3 font-medium">{template.name}</td>
                        <td className="px-4 py-3">{template.version}</td>
                        <td className="px-4 py-3 max-w-xs truncate">{template.description || "-"}</td>
                        <td className="px-4 py-3">
                          {template.requires_counter_signature ? (
                            <span className="text-green-600">Yes</span>
                          ) : (
                            <span className="text-slate-400">No</span>
                          )}
                        </td>
                        <td className="px-4 py-3">
                          {template.is_active ? (
                            <span className="text-green-600">Active</span>
                          ) : (
                            <span className="text-red-600">Inactive</span>
                          )}
                        </td>
                        <td className="px-4 py-3">{new Date(template.created_at).toLocaleDateString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        </>
      )}

      {/* Documents Tab */}
      {activeTab === "documents" && (
        <>
          <section className="glass-card p-6">
            <h3 className="text-lg font-semibold text-primary-700 mb-4">Send Document</h3>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div>
                <label className="block text-xs font-medium text-slate-500 uppercase tracking-wide">
                  Recipient Type
                </label>
                <select
                  value={recipientType}
                  onChange={(e) => {
                    setRecipientType(e.target.value);
                    setSelectedRecipientId("");
                  }}
                  className="mt-1 block w-full rounded-md border border-slate-200 px-3 py-2 text-sm focus:border-primary-400 focus:outline-none"
                >
                  <option value="user">Student/User</option>
                  <option value="lead">Lead</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-500 uppercase tracking-wide">
                  {recipientType === "user" ? "Select Student" : "Select Lead"}
                </label>
                <select
                  value={selectedRecipientId}
                  onChange={(e) => setSelectedRecipientId(e.target.value)}
                  className="mt-1 block w-full rounded-md border border-slate-200 px-3 py-2 text-sm focus:border-primary-400 focus:outline-none"
                >
                  <option value="">Choose {recipientType}...</option>
                  {recipientType === "user"
                    ? users.map((user) => (
                        <option key={user.id} value={user.id}>
                          {user.first_name} {user.last_name} ({user.email})
                        </option>
                      ))
                    : leads.map((lead) => (
                        <option key={lead.id} value={lead.id}>
                          {lead.first_name} {lead.last_name} ({lead.email})
                        </option>
                      ))}
                </select>
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-500 uppercase tracking-wide">
                  Select Template
                </label>
                <select
                  value={selectedTemplateId}
                  onChange={(e) => setSelectedTemplateId(e.target.value)}
                  className="mt-1 block w-full rounded-md border border-slate-200 px-3 py-2 text-sm focus:border-primary-400 focus:outline-none"
                >
                  <option value="">Choose template...</option>
                  {templates
                    .filter((t) => t.is_active)
                    .map((template) => (
                      <option key={template.id} value={template.id}>
                        {template.name} (v{template.version})
                      </option>
                    ))}
                </select>
              </div>
            </div>
            <button
              onClick={handleSendDocument}
              className="mt-4 px-4 py-2 bg-primary-600 text-white text-sm font-semibold rounded-lg hover:bg-primary-700 transition"
            >
              Send Document
            </button>
          </section>

          {selectedRecipientId && (
            <section className="glass-card p-6">
              <h3 className="text-lg font-semibold text-primary-700 mb-4">
                Documents for {recipientType === "user" ? "Student" : "Lead"}
              </h3>
              {loading ? (
                <div className="text-center py-8 text-slate-500">Loading documents...</div>
              ) : documents.length === 0 ? (
                <div className="text-center py-8 text-slate-500">No documents found</div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-sm">
                    <thead className="border-b border-slate-200">
                      <tr className="text-xs text-slate-500 uppercase tracking-wide">
                        <th className="px-4 py-3">Template</th>
                        <th className="px-4 py-3">Status</th>
                        <th className="px-4 py-3">Sent</th>
                        <th className="px-4 py-3">Signed</th>
                        <th className="px-4 py-3">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {documents.map((doc) => (
                        <tr key={doc.id} className="border-b border-slate-100 hover:bg-slate-50">
                          <td className="px-4 py-3 font-medium">{doc.template_name || "Unknown"}</td>
                          <td className="px-4 py-3">
                            <span className={`inline-block px-2 py-1 rounded text-xs font-medium ${getStatusBadge(doc.signature_status)}`}>
                              {doc.signature_status}
                            </span>
                          </td>
                          <td className="px-4 py-3">{formatDate(doc.created_at)}</td>
                          <td className="px-4 py-3">{doc.signed_at ? formatDate(doc.signed_at) : "-"}</td>
                          <td className="px-4 py-3 space-x-2">
                            <button
                              onClick={() => handleDownload(doc)}
                              className="text-primary-600 hover:text-primary-800 text-sm"
                            >
                              Download
                            </button>
                            <button
                              onClick={() => handleViewAuditTrail(doc)}
                              className="text-blue-600 hover:text-blue-800 text-sm"
                            >
                              Audit Trail
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </section>
          )}
        </>
      )}

      {/* All Documents Tab */}
      {activeTab === "all" && (
        <section className="glass-card p-6">
          <h3 className="text-lg font-semibold text-primary-700 mb-4">All Documents</h3>
          {loading ? (
            <div className="text-center py-8 text-slate-500">Loading documents...</div>
          ) : documents.length === 0 ? (
            <div className="text-center py-8 text-slate-500">No documents found</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="border-b border-slate-200">
                  <tr className="text-xs text-slate-500 uppercase tracking-wide">
                    <th className="px-4 py-3">Template</th>
                    <th className="px-4 py-3">Recipient</th>
                    <th className="px-4 py-3">Type</th>
                    <th className="px-4 py-3">Status</th>
                    <th className="px-4 py-3">Sent</th>
                    <th className="px-4 py-3">Signed</th>
                    <th className="px-4 py-3">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {documents.map((doc) => (
                    <tr key={doc.id} className="border-b border-slate-100 hover:bg-slate-50">
                      <td className="px-4 py-3 font-medium">{doc.template_name || "Unknown"}</td>
                      <td className="px-4 py-3">
                        {doc.user_id ? `User ${doc.user_id.slice(0, 8)}...` : `Lead ${doc.lead_id.slice(0, 8)}...`}
                      </td>
                      <td className="px-4 py-3">{doc.user_id ? "Student" : "Lead"}</td>
                      <td className="px-4 py-3">
                        <span className={`inline-block px-2 py-1 rounded text-xs font-medium ${getStatusBadge(doc.signature_status)}`}>
                          {doc.signature_status}
                        </span>
                      </td>
                      <td className="px-4 py-3">{formatDate(doc.created_at)}</td>
                      <td className="px-4 py-3">{doc.signed_at ? formatDate(doc.signed_at) : "-"}</td>
                      <td className="px-4 py-3 space-x-2">
                        <button
                          onClick={() => handleDownload(doc)}
                          className="text-primary-600 hover:text-primary-800 text-sm"
                        >
                          Download
                        </button>
                        <button
                          onClick={() => handleViewAuditTrail(doc)}
                          className="text-blue-600 hover:text-blue-800 text-sm"
                        >
                          Audit Trail
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      )}

      {/* Audit Trail Dialog */}
      {auditTrailOpen && selectedDocument && (
        <AuditTrailDialog
          open={auditTrailOpen}
          onClose={() => setAuditTrailOpen(false)}
          documentId={selectedDocument.id}
          documentName={selectedDocument.template_name}
        />
      )}
    </div>
  );
};

export default Documents;
