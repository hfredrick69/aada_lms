import { useState } from "react";
import axiosClient from "../api/axiosClient.js";

const RESOURCES = [
  { key: "attendance", label: "Attendance Logs" },
  { key: "complaints", label: "Complaints" },
  { key: "credentials", label: "Credentials" },
  { key: "externships", label: "Externships" },
  { key: "skills", label: "Skills Checkoffs" },
  { key: "withdrawals", label: "Withdrawals" },
  { key: "refunds", label: "Refunds" },
  { key: "transcripts", label: "Transcripts" }
];

const Reports = () => {
  const [format, setFormat] = useState("csv");
  const [downloading, setDownloading] = useState(false);
  const [message, setMessage] = useState(null);

  const handleDownload = async (resource) => {
    setDownloading(true);
    setMessage(null);
    try {
      const response = await axiosClient.get(`/reports/compliance/${resource}`, {
        params: { format },
        responseType: "blob"
      });
      const blob = new Blob([response.data], { type: response.headers["content-type"] });
      const link = document.createElement("a");
      link.href = window.URL.createObjectURL(blob);
      const extension = format === "pdf" ? "pdf" : "csv";
      link.download = `${resource}_report.${extension}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      setMessage(`Downloaded ${resource} report as ${extension.toUpperCase()}.`);
    } catch (error) {
      console.error(error);
      setMessage("Unable to export report. Verify CORS and API availability.");
    } finally {
      setDownloading(false);
    }
  };

  return (
    <div className="space-y-6">
      <header>
        <h2 className="text-2xl font-semibold text-brand-700">Compliance Reporting</h2>
        <p className="text-sm text-slate-500">
          Generate GNPEC-ready exports for attendance, refunds, externships, and credential audits.
        </p>
      </header>

      <section className="glass-card p-6 space-y-4">
        <div className="flex items-center gap-4">
          <label className="text-sm font-medium text-slate-600">Format</label>
          <select
            value={format}
            onChange={(event) => setFormat(event.target.value)}
            className="rounded-md border border-slate-200 px-3 py-2 text-sm focus:border-brand-400 focus:outline-none"
          >
            <option value="csv">CSV</option>
            <option value="pdf">PDF</option>
          </select>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {RESOURCES.map((resource) => (
            <button
              key={resource.key}
              onClick={() => handleDownload(resource.key)}
              disabled={downloading}
              className="glass-card hover:bg-brand-100 hover:text-brand-700 transition px-4 py-3 text-left text-sm font-medium disabled:opacity-60"
            >
              {resource.label}
            </button>
          ))}
        </div>
        {message && <p className="text-sm text-slate-600">{message}</p>}
      </section>
    </div>
  );
};

export default Reports;
