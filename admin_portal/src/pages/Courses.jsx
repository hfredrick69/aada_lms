import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext.jsx";
import {
  listPrograms,
  createProgram,
  updateProgram,
  deleteProgram,
  listModules,
  createModule,
  updateModule,
  deleteModule,
} from "../api/courses.js";

const Courses = () => {
  const { hasRole } = useAuth();
  const [programs, setPrograms] = useState([]);
  const [selectedProgram, setSelectedProgram] = useState(null);
  const [modules, setModules] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  // Modal states
  const [showProgramModal, setShowProgramModal] = useState(false);
  const [showModuleModal, setShowModuleModal] = useState(false);
  const [editingProgram, setEditingProgram] = useState(null);
  const [editingModule, setEditingModule] = useState(null);

  // Form states
  const [programForm, setProgramForm] = useState({
    code: "",
    name: "",
    credential_level: "certificate",
    total_clock_hours: 0,
  });

  const [moduleForm, setModuleForm] = useState({
    code: "",
    title: "",
    delivery_type: "online",
    clock_hours: 0,
    requires_in_person: false,
    position: 1,
  });

  const canEdit = hasRole(["Admin", "Instructor"]);
  const canDelete = hasRole(["Admin"]);

  // Load programs on mount
  useEffect(() => {
    fetchPrograms();
  }, []);

  // Load modules when selected program changes
  useEffect(() => {
    if (selectedProgram?.id) {
      fetchModules();
    } else {
      setModules([]);
    }
  }, [selectedProgram]);

  const fetchPrograms = async () => {
    setLoading(true);
    try {
      const data = await listPrograms();
      setPrograms(Array.isArray(data) ? data : []);
      if (Array.isArray(data) && data.length > 0 && !selectedProgram) {
        setSelectedProgram(data[0]);
      }
      setError(null);
    } catch (err) {
      console.error(err);
      setError("Unable to load programs");
      setPrograms([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchModules = async () => {
    if (!selectedProgram?.id) return;
    try {
      const data = await listModules(selectedProgram.id);
      setModules(Array.isArray(data) ? data : []);
      setError(null);
    } catch (err) {
      console.error(err);
      setError("Unable to load modules");
      setModules([]);
    }
  };

  // ============ PROGRAM HANDLERS ============

  const handleProgramChange = (event) => {
    setProgramForm((prev) => ({ ...prev, [event.target.name]: event.target.value }));
  };

  const openProgramModal = (program = null) => {
    if (program) {
      setEditingProgram(program);
      setProgramForm({
        code: program.code,
        name: program.name,
        credential_level: program.credential_level,
        total_clock_hours: program.total_clock_hours,
      });
    } else {
      setEditingProgram(null);
      setProgramForm({
        code: "",
        name: "",
        credential_level: "certificate",
        total_clock_hours: 0,
      });
    }
    setShowProgramModal(true);
  };

  const closeProgramModal = () => {
    setShowProgramModal(false);
    setEditingProgram(null);
    setProgramForm({
      code: "",
      name: "",
      credential_level: "certificate",
      total_clock_hours: 0,
    });
  };

  const handleProgramSubmit = async (event) => {
    event.preventDefault();
    if (!canEdit) return;

    try {
      if (editingProgram) {
        const updated = await updateProgram(editingProgram.id, programForm);
        setPrograms((prev) =>
          prev.map((p) => (p.id === editingProgram.id ? updated : p))
        );
        if (selectedProgram?.id === editingProgram.id) {
          setSelectedProgram(updated);
        }
      } else {
        const created = await createProgram(programForm);
        setPrograms((prev) => [created, ...prev]);
        if (!selectedProgram) {
          setSelectedProgram(created);
        }
      }
      closeProgramModal();
      setError(null);
    } catch (err) {
      console.error(err);
      setError(err?.response?.data?.detail || "Unable to save program");
    }
  };

  const handleProgramDelete = async (programId) => {
    if (!canDelete) return;
    if (!window.confirm("Delete this program and all its modules?")) return;

    try {
      await deleteProgram(programId);
      setPrograms((prev) => prev.filter((p) => p.id !== programId));
      if (selectedProgram?.id === programId) {
        setSelectedProgram(programs.length > 1 ? programs[0] : null);
      }
      setError(null);
    } catch (err) {
      console.error(err);
      setError("Unable to delete program");
    }
  };

  // ============ MODULE HANDLERS ============

  const handleModuleChange = (event) => {
    const { name, type, checked, value } = event.target;
    setModuleForm((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const openModuleModal = (module = null) => {
    if (module) {
      setEditingModule(module);
      setModuleForm({
        code: module.code,
        title: module.title,
        delivery_type: module.delivery_type,
        clock_hours: module.clock_hours,
        requires_in_person: module.requires_in_person || false,
        position: module.position,
      });
    } else {
      setEditingModule(null);
      const nextPosition = modules.length > 0 ? Math.max(...modules.map((m) => m.position)) + 1 : 1;
      setModuleForm({
        code: "",
        title: "",
        delivery_type: "online",
        clock_hours: 0,
        requires_in_person: false,
        position: nextPosition,
      });
    }
    setShowModuleModal(true);
  };

  const closeModuleModal = () => {
    setShowModuleModal(false);
    setEditingModule(null);
    setModuleForm({
      code: "",
      title: "",
      delivery_type: "online",
      clock_hours: 0,
      requires_in_person: false,
      position: 1,
    });
  };

  const handleModuleSubmit = async (event) => {
    event.preventDefault();
    if (!canEdit || !selectedProgram) return;

    try {
      if (editingModule) {
        const updated = await updateModule(
          selectedProgram.id,
          editingModule.id,
          moduleForm
        );
        setModules((prev) =>
          prev.map((m) => (m.id === editingModule.id ? updated : m))
        );
      } else {
        const created = await createModule(selectedProgram.id, moduleForm);
        setModules((prev) => [...prev, created].sort((a, b) => a.position - b.position));
      }
      closeModuleModal();
      setError(null);
    } catch (err) {
      console.error(err);
      setError(err?.response?.data?.detail || "Unable to save module");
    }
  };

  const handleModuleDelete = async (moduleId) => {
    if (!canDelete || !selectedProgram) return;
    if (!window.confirm("Delete this module?")) return;

    try {
      await deleteModule(selectedProgram.id, moduleId);
      setModules((prev) => prev.filter((m) => m.id !== moduleId));
      setError(null);
    } catch (err) {
      console.error(err);
      setError("Unable to delete module");
    }
  };

  return (
    <div className="space-y-6">
      <header className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-primary-700">Programs & Modules</h2>
          <p className="text-sm text-slate-500">
            Manage curriculum structure, delivery type, and clock hours required for compliance.
          </p>
        </div>
        {canEdit && (
          <button
            onClick={() => openProgramModal()}
            className="px-4 py-2 rounded-md bg-primary-500 text-white text-sm font-medium hover:bg-primary-600 transition"
          >
            Add Program
          </button>
        )}
      </header>

      {error && <div className="glass-card p-4 text-sm text-red-600">{error}</div>}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Programs List */}
        <section className="glass-card p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-slate-600 uppercase tracking-wide">
              Programs
            </h3>
          </div>
          {loading ? (
            <div className="text-sm text-slate-500">Loading programs...</div>
          ) : (
            <ul className="space-y-2">
              {programs.map((program) => (
                <li key={program.id} className="group">
                  <div
                    className={`flex items-start gap-2 px-3 py-2 rounded-md text-sm ${
                      selectedProgram?.id === program.id
                        ? "bg-primary-100 text-primary-700"
                        : "bg-white hover:bg-slate-100 text-slate-600"
                    }`}
                  >
                    <button
                      onClick={() => setSelectedProgram(program)}
                      className="flex-1 text-left"
                    >
                      <span className="block font-medium">{program.name}</span>
                      <span className="block text-xs text-slate-500">
                        {program.code} • {program.total_clock_hours}h
                      </span>
                    </button>
                    {canEdit && (
                      <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button
                          onClick={() => openProgramModal(program)}
                          className="text-xs font-medium text-primary-500 hover:text-primary-600"
                          title="Edit"
                        >
                          Edit
                        </button>
                        {canDelete && (
                          <button
                            onClick={() => handleProgramDelete(program.id)}
                            className="text-xs font-medium text-red-500 hover:text-red-600"
                            title="Delete"
                          >
                            Del
                          </button>
                        )}
                      </div>
                    )}
                  </div>
                </li>
              ))}
              {programs.length === 0 && (
                <li className="text-sm text-slate-500">No programs available.</li>
              )}
            </ul>
          )}
        </section>

        {/* Modules List */}
        <section className="glass-card lg:col-span-2 p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-slate-600 uppercase tracking-wide">
              Modules
              {selectedProgram && ` - ${selectedProgram.name}`}
            </h3>
            {canEdit && selectedProgram && (
              <button
                onClick={() => openModuleModal()}
                className="px-3 py-1 rounded-md bg-primary-500 text-white text-xs font-medium hover:bg-primary-600 transition"
              >
                Add Module
              </button>
            )}
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200">
              <thead className="bg-primary-100 text-primary-700">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide">
                    Pos
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide">
                    Code
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide">
                    Title
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide">
                    Delivery
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide">
                    Hours
                  </th>
                  {canEdit && <th className="px-4 py-3" />}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {modules.length === 0 ? (
                  <tr>
                    <td
                      colSpan={canEdit ? 6 : 5}
                      className="px-4 py-6 text-center text-sm text-slate-500"
                    >
                      {selectedProgram
                        ? "No modules found. Add one to get started."
                        : "Select a program to view modules."}
                    </td>
                  </tr>
                ) : (
                  modules.map((module) => (
                    <tr key={module.id} className="group hover:bg-slate-50">
                      <td className="px-4 py-3 text-sm text-slate-700">{module.position}</td>
                      <td className="px-4 py-3 text-sm text-slate-700">{module.code}</td>
                      <td className="px-4 py-3 text-sm text-slate-600">{module.title}</td>
                      <td className="px-4 py-3 text-sm">
                        <span className="inline-flex rounded-full bg-slate-100 px-2 py-1 text-xs text-slate-600">
                          {module.delivery_type}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm text-slate-600">{module.clock_hours}</td>
                      {canEdit && (
                        <td className="px-4 py-3 text-right opacity-0 group-hover:opacity-100 transition-opacity">
                          <button
                            onClick={() => openModuleModal(module)}
                            className="text-xs font-medium text-primary-500 hover:text-primary-600 mr-2"
                          >
                            Edit
                          </button>
                          {canDelete && (
                            <button
                              onClick={() => handleModuleDelete(module.id)}
                              className="text-xs font-medium text-red-500 hover:text-red-600"
                            >
                              Delete
                            </button>
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

      {/* Program Modal */}
      {showProgramModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-lg w-full p-6">
            <h3 className="text-lg font-semibold text-primary-700 mb-4">
              {editingProgram ? "Edit Program" : "Add New Program"}
            </h3>
            <form onSubmit={handleProgramSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-500 uppercase tracking-wide">
                  Code
                </label>
                <input
                  name="code"
                  value={programForm.code}
                  onChange={handleProgramChange}
                  required
                  className="mt-1 block w-full rounded-md border border-slate-200 px-3 py-2 text-sm focus:border-primary-400 focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-500 uppercase tracking-wide">
                  Name
                </label>
                <input
                  name="name"
                  value={programForm.name}
                  onChange={handleProgramChange}
                  required
                  className="mt-1 block w-full rounded-md border border-slate-200 px-3 py-2 text-sm focus:border-primary-400 focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-500 uppercase tracking-wide">
                  Credential Level
                </label>
                <select
                  name="credential_level"
                  value={programForm.credential_level}
                  onChange={handleProgramChange}
                  required
                  className="mt-1 block w-full rounded-md border border-slate-200 px-3 py-2 text-sm focus:border-primary-400 focus:outline-none"
                >
                  <option value="certificate">Certificate</option>
                  <option value="diploma">Diploma</option>
                  <option value="degree">Degree</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-500 uppercase tracking-wide">
                  Total Clock Hours
                </label>
                <input
                  name="total_clock_hours"
                  type="number"
                  value={programForm.total_clock_hours}
                  onChange={handleProgramChange}
                  required
                  min="0"
                  className="mt-1 block w-full rounded-md border border-slate-200 px-3 py-2 text-sm focus:border-primary-400 focus:outline-none"
                />
              </div>
              <div className="flex justify-end gap-3 pt-4">
                <button
                  type="button"
                  onClick={closeProgramModal}
                  className="px-4 py-2 rounded-md border border-slate-300 text-slate-700 text-sm font-medium hover:bg-slate-50 transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-md bg-primary-500 text-white text-sm font-medium hover:bg-primary-600 transition"
                >
                  {editingProgram ? "Update" : "Create"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Module Modal */}
      {showModuleModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-lg w-full p-6">
            <h3 className="text-lg font-semibold text-primary-700 mb-4">
              {editingModule ? "Edit Module" : "Add New Module"}
            </h3>
            <form onSubmit={handleModuleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-500 uppercase tracking-wide">
                    Code
                  </label>
                  <input
                    name="code"
                    value={moduleForm.code}
                    onChange={handleModuleChange}
                    required
                    className="mt-1 block w-full rounded-md border border-slate-200 px-3 py-2 text-sm focus:border-primary-400 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-500 uppercase tracking-wide">
                    Position
                  </label>
                  <input
                    name="position"
                    type="number"
                    value={moduleForm.position}
                    onChange={handleModuleChange}
                    required
                    min="1"
                    className="mt-1 block w-full rounded-md border border-slate-200 px-3 py-2 text-sm focus:border-primary-400 focus:outline-none"
                  />
                </div>
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-500 uppercase tracking-wide">
                  Title
                </label>
                <input
                  name="title"
                  value={moduleForm.title}
                  onChange={handleModuleChange}
                  required
                  className="mt-1 block w-full rounded-md border border-slate-200 px-3 py-2 text-sm focus:border-primary-400 focus:outline-none"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-500 uppercase tracking-wide">
                    Delivery Type
                  </label>
                  <select
                    name="delivery_type"
                    value={moduleForm.delivery_type}
                    onChange={handleModuleChange}
                    required
                    className="mt-1 block w-full rounded-md border border-slate-200 px-3 py-2 text-sm focus:border-primary-400 focus:outline-none"
                  >
                    <option value="online">Online</option>
                    <option value="hybrid">Hybrid</option>
                    <option value="in_person">In Person</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-500 uppercase tracking-wide">
                    Clock Hours
                  </label>
                  <input
                    name="clock_hours"
                    type="number"
                    value={moduleForm.clock_hours}
                    onChange={handleModuleChange}
                    required
                    min="0"
                    className="mt-1 block w-full rounded-md border border-slate-200 px-3 py-2 text-sm focus:border-primary-400 focus:outline-none"
                  />
                </div>
              </div>
              <div>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    name="requires_in_person"
                    type="checkbox"
                    checked={moduleForm.requires_in_person}
                    onChange={handleModuleChange}
                    className="rounded border-slate-300 text-primary-500 focus:ring-primary-400"
                  />
                  <span className="text-sm text-slate-700">Requires in-person attendance</span>
                </label>
              </div>
              <div className="flex justify-end gap-3 pt-4">
                <button
                  type="button"
                  onClick={closeModuleModal}
                  className="px-4 py-2 rounded-md border border-slate-300 text-slate-700 text-sm font-medium hover:bg-slate-50 transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-md bg-primary-500 text-white text-sm font-medium hover:bg-primary-600 transition"
                >
                  {editingModule ? "Update" : "Create"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Courses;
