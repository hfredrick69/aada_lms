import { useEffect, useState } from "react";
import { listInvoices, markInvoicePaid } from "../api/payments.js";
import { useAuth } from "../context/AuthContext.jsx";

const Payments = () => {
  const { hasRole } = useAuth();
  const [invoices, setInvoices] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  const canEdit = hasRole(["admin", "finance", "staff"]);

  const loadInvoices = async () => {
    setLoading(true);
    try {
      const data = await listInvoices();
      setInvoices(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error(err);
      setError("Unable to load payment transactions. Showing placeholder data.");
      setInvoices([
        { id: "demo-1", student: "Alice Student", amount_cents: 420000, line_type: "tuition", description: "Program tuition" },
        { id: "demo-2", student: "Bob Learner", amount_cents: -380000, line_type: "payment", description: "Payment received" }
      ]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadInvoices();
  }, []);

  const handleMarkPaid = async (invoiceId) => {
    if (!canEdit) return;
    try {
      await markInvoicePaid(invoiceId);
      setInvoices((prev) =>
        prev.map((invoice) =>
          invoice.id === invoiceId ? { ...invoice, status: "paid", paid_at: new Date().toISOString() } : invoice
        )
      );
    } catch (err) {
      console.error(err);
      setError("Unable to update invoice. Please try again later.");
    }
  };

  return (
    <div className="space-y-6">
      <header>
        <h2 className="text-2xl font-semibold text-primary-700">Payments & Invoices</h2>
        <p className="text-sm text-slate-500">
          Monitor Square invoices, tuition status, and GNPEC refund compliance.
        </p>
      </header>

      {error && <div className="glass-card p-4 text-sm text-red-600">{error}</div>}

      <section className="glass-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200">
            <thead className="bg-primary-100 text-primary-700">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide">Invoice</th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide">Student</th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide">Amount</th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide">Status</th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide">Due date</th>
                {canEdit && <th className="px-4 py-3" />}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan={canEdit ? 6 : 5} className="px-4 py-6 text-center text-sm text-slate-500">
                    Loading invoices...
                  </td>
                </tr>
              ) : invoices.length === 0 ? (
                <tr>
                  <td colSpan={canEdit ? 6 : 5} className="px-4 py-6 text-center text-sm text-slate-500">
                    No invoices found.
                  </td>
                </tr>
              ) : (
                invoices.map((invoice) => {
                  // Map line_type to display values
                  const isCharge = ["tuition", "fee"].includes(invoice.line_type);
                  const isPayment = ["payment", "refund"].includes(invoice.line_type);
                  const displayType = invoice.line_type.charAt(0).toUpperCase() + invoice.line_type.slice(1);

                  return (
                    <tr key={invoice.id}>
                      <td className="px-4 py-3 text-sm text-slate-600">{invoice.id}</td>
                      <td className="px-4 py-3 text-sm text-slate-600">{invoice.student_name || invoice.student || "N/A"}</td>
                      <td className="px-4 py-3 text-sm text-slate-700">
                        ${(Math.abs(invoice.amount_cents) / 100).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                      </td>
                      <td className="px-4 py-3 text-sm">
                        <span
                          className={`inline-flex rounded-full px-2 py-1 text-xs font-semibold ${
                            isPayment
                              ? "bg-emerald-100 text-emerald-600"
                              : "bg-amber-100 text-amber-600"
                          }`}
                        >
                          {displayType}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm text-slate-500">{invoice.due_date || invoice.created_at?.substring(0, 10) || "N/A"}</td>
                      {canEdit && (
                        <td className="px-4 py-3 text-right">
                          {isCharge && (
                            <button
                              onClick={() => handleMarkPaid(invoice.id)}
                              className="text-xs font-medium text-primary-600 hover:text-primary-700"
                            >
                              Record Payment
                            </button>
                          )}
                        </td>
                      )}
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
};

export default Payments;
