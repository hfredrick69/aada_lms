import { useEffect, useState } from "react";
import { listModules, listPrograms } from "../api/courses.js";

const Courses = () => {
  const [programs, setPrograms] = useState([]);
  const [selectedProgram, setSelectedProgram] = useState(null);
  const [modules, setModules] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchPrograms = async () => {
      try {
        const data = await listPrograms();
        setPrograms(Array.isArray(data) ? data : []);
        if (Array.isArray(data) && data.length > 0) {
          setSelectedProgram(data[0]);
        }
      } catch (err) {
        console.error(err);
        setError("Unable to load programs; review backend connectivity.");
        setPrograms([
          { id: "demo-program", name: "Medical Assistant Diploma", total_clock_hours: 480, modules: 12 }
        ]);
      }
    };
    fetchPrograms();
  }, []);

  useEffect(() => {
    const fetchModules = async () => {
      if (!selectedProgram?.id) return;
      try {
        const data = await listModules(selectedProgram.id);
        setModules(Array.isArray(data) ? data : []);
      } catch (err) {
        console.error(err);
        setModules([
          { id: "demo-mod-1", code: "MA-101", title: "Medical Foundations", clock_hours: 120, delivery_type: "hybrid" },
          { id: "demo-mod-2", code: "MA-201", title: "Clinical Procedures", clock_hours: 180, delivery_type: "in_person" }
        ]);
      }
    };
    fetchModules();
  }, [selectedProgram]);

  return (
    <div className="space-y-6">
      <header>
        <h2 className="text-2xl font-semibold text-primary-700">Programs & Modules</h2>
        <p className="text-sm text-slate-500">
          Inspect curriculum structure, delivery type, and clock hours required for compliance audits.
        </p>
      </header>

      {error && <div className="glass-card p-4 text-sm text-red-600">{error}</div>}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <section className="glass-card p-4">
          <h3 className="text-sm font-semibold text-slate-600 uppercase tracking-wide mb-3">Programs</h3>
          <ul className="space-y-2">
            {programs.map((program) => (
              <li key={program.id}>
                <button
                  onClick={() => setSelectedProgram(program)}
                  className={`w-full text-left px-3 py-2 rounded-md text-sm ${
                    selectedProgram?.id === program.id
                      ? "bg-primary-100 text-primary-700"
                      : "bg-white hover:bg-slate-100 text-slate-600"
                  }`}
                >
                  <span className="block font-medium">{program.name}</span>
                  <span className="block text-xs text-slate-500">{program.total_clock_hours} clock hours</span>
                </button>
              </li>
            ))}
            {programs.length === 0 && <li className="text-sm text-slate-500">No programs available.</li>}
          </ul>
        </section>

        <section className="glass-card lg:col-span-2 p-4">
          <h3 className="text-sm font-semibold text-slate-600 uppercase tracking-wide mb-3">Modules</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200">
              <thead className="bg-primary-100 text-primary-700">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide">Code</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide">Title</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide">Delivery</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide">Clock hours</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {modules.length === 0 ? (
                  <tr>
                    <td colSpan={4} className="px-4 py-6 text-center text-sm text-slate-500">
                      Select a program to view modules.
                    </td>
                  </tr>
                ) : (
                  modules.map((module) => (
                    <tr key={module.id}>
                      <td className="px-4 py-3 text-sm text-slate-700">{module.code}</td>
                      <td className="px-4 py-3 text-sm text-slate-600">{module.title}</td>
                      <td className="px-4 py-3 text-sm">
                        <span className="inline-flex rounded-full bg-slate-100 px-2 py-1 text-xs text-slate-600">
                          {module.delivery_type}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm text-slate-600">{module.clock_hours}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </div>
  );
};

export default Courses;
