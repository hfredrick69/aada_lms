import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import MetricCard from "../components/MetricCard.jsx";
import { listStudents } from "../api/students.js";
import { listPrograms } from "../api/courses.js";
import { listExternships } from "../api/externships.js";
import { getAllDocuments } from "../api/documents.js";

const Dashboard = () => {
  const [metrics, setMetrics] = useState({
    students: 0,
    programs: 0,
    openInvoices: 0,
    externships: 0,
    pendingAgreements: 0
  });
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    let mounted = true;
    const load = async () => {
      try {
        const [studentsResult, programsResult, externshipsResult, agreementsResult] = await Promise.allSettled([
          listStudents(),
          listPrograms(),
          listExternships(),
          getAllDocuments({ status: "student_signed" })
        ]);
        if (!mounted) return;
        setMetrics({
          students: studentsResult.status === "fulfilled" ? studentsResult.value.length : 0,
          programs: programsResult.status === "fulfilled" ? programsResult.value.length : 0,
          openInvoices: 0,  // TODO: Add invoices endpoint to backend
          externships: externshipsResult.status === "fulfilled" ? externshipsResult.value.length : 0,
          pendingAgreements:
            agreementsResult.status === "fulfilled"
              ? (agreementsResult.value?.documents?.length ?? 0)
              : 0
        });
      } catch (error) {
        console.error(error);
      } finally {
        if (mounted) setLoading(false);
      }
    };
    load();
    return () => {
      mounted = false;
    };
  }, []);

  return (
    <div className="space-y-6">
      <header className="flex flex-col gap-2">
        <h2 className="text-2xl font-semibold text-primary-700">Dashboard</h2>
        <p className="text-sm text-slate-500">Monitor enrollment, compliance, and financial health in real time.</p>
      </header>
      {loading ? (
        <div className="glass-card p-10 text-center text-primary-700">Loading metrics...</div>
      ) : (
        <>
          <section className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-5 gap-4">
            <MetricCard title="Active Students" value={metrics.students} trend="+3 new this week" />
            <MetricCard title="Programs & Modules" value={metrics.programs} trend="Updated nightly" />
            <MetricCard
              title="Open Invoices"
              value={metrics.openInvoices}
              trend="Review finance queue"
              onClick={() => navigate("/payments")}
              actionLabel="Go to billing"
            />
            <MetricCard title="Externship Placements" value={metrics.externships} trend="2 approvals pending" />
            <MetricCard
              title="Awaiting Counter-Sign"
              value={metrics.pendingAgreements}
              trend={
                metrics.pendingAgreements > 0
                  ? "Agreements need signatures"
                  : "All enrollment docs signed"
              }
              onClick={() => navigate("/agreements", { state: { statusFilter: "student_signed" } })}
              actionLabel="Review agreements"
            />
          </section>
          <section className="glass-card p-6">
            <h3 className="text-lg font-semibold text-primary-700">Compliance Reminders</h3>
            <ul className="mt-4 space-y-3 text-sm text-slate-600">
              <li>• Refunds must be remitted within 45 days of approval.</li>
              <li>• Ensure externship verification documents are uploaded for current cohort.</li>
              <li>• GNPEC complaints require resolution documentation within 30 days.</li>
            </ul>
          </section>
        </>
      )}
    </div>
  );
};

export default Dashboard;
