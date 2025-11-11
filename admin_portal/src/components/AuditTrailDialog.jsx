import { useState, useEffect } from 'react';
import { getDocumentAuditTrail } from '../api/documents';

const AuditTrailDialog = ({ open, onClose, documentId, documentName }) => {
  const [auditLogs, setAuditLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (open && documentId) {
      loadAuditTrail();
    }
  }, [open, documentId]);

  const loadAuditTrail = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getDocumentAuditTrail(documentId);
      setAuditLogs(data.audit_logs || []);
    } catch (err) {
      setError('Failed to load audit trail');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getEventColor = (eventType) => {
    const colors = {
      viewed: 'bg-primary-100 text-primary-700',
      sent: 'bg-purple-100 text-purple-700',
      signed: 'bg-green-100 text-green-700',
      document_signed: 'bg-green-100 text-green-700',
      voided: 'bg-red-100 text-red-700',
    };
    return colors[eventType] || 'bg-gray-100 text-gray-700';
  };

  const formatEventType = (eventType) => {
    return eventType
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      timeZoneName: 'short',
    });
  };

  const parseEventDetails = (details) => {
    try {
      return details ? JSON.parse(details) : null;
    } catch {
      return null;
    }
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-5xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b border-slate-200 flex justify-between items-start">
          <div>
            <h3 className="text-xl font-semibold text-primary-700">Audit Trail</h3>
            {documentName && (
              <p className="text-sm text-slate-500 mt-1">Document: {documentName}</p>
            )}
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

        <div className="p-6">
          {error && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}

          {loading ? (
            <div className="text-center py-8 text-slate-500">Loading audit trail...</div>
          ) : (
            <>
              <div className="overflow-x-auto border border-slate-200 rounded">
                <table className="w-full text-left text-sm">
                  <thead className="bg-slate-50 border-b border-slate-200">
                    <tr className="text-xs text-slate-500 uppercase tracking-wide">
                      <th className="px-4 py-3">Event</th>
                      <th className="px-4 py-3">Timestamp</th>
                      <th className="px-4 py-3">IP Address</th>
                      <th className="px-4 py-3">User Agent</th>
                      <th className="px-4 py-3">Details</th>
                    </tr>
                  </thead>
                  <tbody>
                    {auditLogs.map((log, index) => {
                      const details = parseEventDetails(log.event_details);
                      return (
                        <tr key={log.id || index} className="border-b border-slate-100 hover:bg-slate-50">
                          <td className="px-4 py-3">
                            <span className={`inline-block px-2 py-1 rounded text-xs font-medium ${getEventColor(log.event_type)}`}>
                              {formatEventType(log.event_type)}
                            </span>
                          </td>
                          <td className="px-4 py-3 whitespace-nowrap text-sm">
                            {formatDate(log.occurred_at)}
                          </td>
                          <td className="px-4 py-3">
                            <code className="text-xs bg-slate-100 px-2 py-1 rounded">
                              {log.ip_address || 'N/A'}
                            </code>
                          </td>
                          <td className="px-4 py-3">
                            <div className="max-w-xs overflow-hidden text-ellipsis text-xs text-slate-600">
                              {log.user_agent || 'N/A'}
                            </div>
                          </td>
                          <td className="px-4 py-3">
                            {details ? (
                              <div className="space-y-1">
                                {Object.entries(details).map(([key, value]) => (
                                  <div key={key} className="text-xs">
                                    <span className="font-medium text-slate-700">{key}:</span>{' '}
                                    <span className="text-slate-600">{String(value)}</span>
                                  </div>
                                ))}
                              </div>
                            ) : (
                              <span className="text-slate-400 text-xs">-</span>
                            )}
                          </td>
                        </tr>
                      );
                    })}
                    {auditLogs.length === 0 && !loading && (
                      <tr>
                        <td colSpan={5} className="px-4 py-8 text-center text-slate-500">
                          No audit log entries found
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>

              <div className="mt-4 p-4 bg-primary-50 border border-primary-200 rounded">
                <p className="text-xs text-primary-700">
                  This audit trail provides a complete record of all actions taken on this document
                  in compliance with the ESIGN Act. All timestamps are recorded in UTC and converted to local time for display.
                </p>
              </div>
            </>
          )}
        </div>

        <div className="p-6 border-t border-slate-200 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-200 text-slate-700 text-sm font-semibold rounded-lg hover:bg-slate-300 transition"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default AuditTrailDialog;
