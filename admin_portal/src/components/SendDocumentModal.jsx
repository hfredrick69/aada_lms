import { useState, useEffect } from "react";
import { listDocumentTemplates, sendDocumentToLead } from "../api/documents.js";

const SendDocumentModal = ({ lead, onClose }) => {
  const [templates, setTemplates] = useState([]);
  const [selectedTemplate, setSelectedTemplate] = useState("");
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);
  const [signingLink, setSigningLink] = useState("");
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadTemplates = async () => {
      try {
        const data = await listDocumentTemplates(true);
        setTemplates(Array.isArray(data) ? data : []);
      } catch (err) {
        console.error(err);
        setError("Unable to load document templates");
      }
    };
    loadTemplates();
  }, []);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!selectedTemplate) {
      setError("Please select a document template");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const document = await sendDocumentToLead(selectedTemplate, lead.id);
      
      // Generate signing link
      const baseUrl = window.location.origin.replace(':5173', ':5174');
      const link = `${baseUrl}/sign/${document.signing_token}`;
      setSigningLink(link);
      setSent(true);
    } catch (err) {
      console.error(err);
      setError(err?.response?.data?.detail || "Unable to send document");
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(signingLink);
    alert("Signing link copied to clipboard!");
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h3 className="text-xl font-semibold text-primary-700">Send Document for Signature</h3>
              <p className="text-sm text-slate-500 mt-1">
                {lead.first_name} {lead.last_name} ({lead.email})
              </p>
            </div>
            <button
              onClick={onClose}
              className="text-slate-400 hover:text-slate-600"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {error && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}

          {!sent ? (
            <form onSubmit={handleSend}>
              <div className="mb-4">
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Select Document Template
                </label>
                <select
                  value={selectedTemplate}
                  onChange={(e) => setSelectedTemplate(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded focus:outline-none focus:ring-2 focus:ring-primary-500"
                  required
                >
                  <option value="">Choose a template...</option>
                  {templates.map((template) => (
                    <option key={template.id} value={template.id}>
                      {template.name} (v{template.version})
                    </option>
                  ))}
                </select>
                {templates.length === 0 && (
                  <p className="text-sm text-slate-500 mt-2">No active templates available</p>
                )}
              </div>

              <div className="bg-blue-50 border border-blue-200 rounded p-4 mb-4">
                <h4 className="text-sm font-semibold text-blue-900 mb-2">How it works:</h4>
                <ol className="text-sm text-blue-700 space-y-1 list-decimal list-inside">
                  <li>Select a document template above</li>
                  <li>Click "Generate Signing Link"</li>
                  <li>Copy the secure link and send it to {lead.first_name} via email or SMS</li>
                  <li>The link expires in 30 days</li>
                </ol>
              </div>

              <div className="flex justify-end gap-3">
                <button
                  type="button"
                  onClick={onClose}
                  className="px-4 py-2 border border-slate-300 rounded text-slate-700 hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading || templates.length === 0}
                  className="px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? "Generating..." : "Generate Signing Link"}
                </button>
              </div>
            </form>
          ) : (
            <div>
              <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded">
                <div className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-green-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <div>
                    <h4 className="text-sm font-semibold text-green-900">Signing link generated!</h4>
                    <p className="text-sm text-green-700 mt-1">
                      Send this secure link to {lead.first_name} {lead.last_name} to complete the signature.
                    </p>
                  </div>
                </div>
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Secure Signing Link
                </label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={signingLink}
                    readOnly
                    className="flex-1 px-3 py-2 border border-slate-300 rounded bg-slate-50 text-sm font-mono"
                  />
                  <button
                    onClick={copyToClipboard}
                    className="px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700"
                  >
                    Copy
                  </button>
                </div>
                <p className="text-xs text-slate-500 mt-2">
                  This link expires in 30 days and can only be used once.
                </p>
              </div>

              <div className="bg-yellow-50 border border-yellow-200 rounded p-4 mb-4">
                <h4 className="text-sm font-semibold text-yellow-900 mb-2">Next Steps:</h4>
                <ul className="text-sm text-yellow-700 space-y-1 list-disc list-inside">
                  <li>Copy the link above and send it to {lead.email}</li>
                  <li>You can also send via SMS to {lead.phone || "(phone not provided)"}</li>
                  <li>Track signature status in the lead's activity log</li>
                </ul>
              </div>

              <div className="flex justify-end">
                <button
                  onClick={onClose}
                  className="px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700"
                >
                  Done
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SendDocumentModal;
