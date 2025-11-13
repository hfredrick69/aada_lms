import { useEffect, useMemo, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { format } from "date-fns";
import {
  listDocumentTemplates,
  getAllDocuments,
  sendEnrollmentAgreement,
  counterSignDocument,
  fetchDocumentBlob,
} from "../api/documents.js";
import { listStudents } from "../api/students.js";
import SignaturePad from "../components/SignaturePad.jsx";
import { useAuth } from "../context/AuthContext.jsx";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  MenuItem,
  Alert,
} from "@mui/material";

const COURSE_OPTIONS = [
  { value: "twenty_week", label: "20-Week Course" },
  { value: "expanded_functions", label: "Expanded Functions Course", disabled: true },
];

const STATUS_OPTIONS = [
  { value: "all", label: "All statuses" },
  { value: "pending", label: "Pending (draft)" },
  { value: "student_signed", label: "Awaiting AADA signature" },
  { value: "completed", label: "Completed" },
];

const statusStyles = {
  pending: "bg-slate-100 text-slate-700",
  student_signed: "bg-amber-100 text-amber-800",
  completed: "bg-emerald-100 text-emerald-800",
};

const Agreements = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { hasRole } = useAuth();
  const canCounterSign = hasRole(["admin", "registrar"]);
  const [students, setStudents] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [agreements, setAgreements] = useState([]);
  const [courseFilter, setCourseFilter] = useState("twenty_week");
  const [statusFilter, setStatusFilter] = useState("all");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState("");

  const [sendForm, setSendForm] = useState({
    studentId: "",
    templateId: "",
    courseType: "twenty_week",
    signerName: "",
    signerEmail: "",
    advisorNotes: "",
  });
  const [sending, setSending] = useState(false);

  const [counterModal, setCounterModal] = useState({
    open: false,
    document: null,
    typedName: "",
    signatureData: null,
    saving: false,
    error: null,
  });
  const [viewerModal, setViewerModal] = useState({
    open: false,
    document: null,
    pdfUrl: "",
    loading: false,
    error: null,
  });

  const enrollmentTemplates = useMemo(
    () =>
      templates.filter((tpl) =>
        (tpl.name || "").toLowerCase().includes("enrollment agreement")
      ),
    [templates]
  );

  const studentsById = useMemo(() => {
    const map = new Map();
    students.forEach((student) => map.set(student.id, student));
    return map;
  }, [students]);

  const courseLabel = (slug) =>
    COURSE_OPTIONS.find((c) => c.value === slug)?.label || "General Agreement";

  const loadStudents = async () => {
    try {
      const data = await listStudents();
      setStudents(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error(err);
    }
  };

  const loadTemplates = async () => {
    try {
      const data = await listDocumentTemplates(false);
      setTemplates(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error(err);
    }
  };

  const loadAgreements = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = {};
      if (courseFilter && courseFilter !== "all") {
        params.course_type = courseFilter;
      }
      if (statusFilter && statusFilter !== "all") {
        params.status = statusFilter;
      }
      const data = await getAllDocuments(params);
      setAgreements(Array.isArray(data.documents) ? data.documents : []);
    } catch (err) {
      console.error(err);
      setError("Unable to load agreements");
      setAgreements([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStudents();
    loadTemplates();
  }, []);

  useEffect(() => {
    loadAgreements();
  }, [courseFilter, statusFilter]);

  useEffect(() => {
    if (location.state?.statusFilter) {
      setStatusFilter(location.state.statusFilter);
      navigate(location.pathname, { replace: true, state: {} });
    }
  }, [location.state, navigate, location.pathname]);

  useEffect(() => {
    return () => {
      if (viewerModal.pdfUrl) {
        URL.revokeObjectURL(viewerModal.pdfUrl);
      }
    };
  }, [viewerModal.pdfUrl]);

  const handleSend = async (event) => {
    event.preventDefault();
    if (!sendForm.studentId) {
      setError("Select a student to send the agreement.");
      return;
    }

    setSending(true);
    setError(null);
    try {
      await sendEnrollmentAgreement({
        user_id: sendForm.studentId,
        template_id: sendForm.templateId || undefined,
        course_type: sendForm.courseType,
        signer_name: sendForm.signerName || undefined,
        signer_email: sendForm.signerEmail || undefined,
        form_data: {
          advisor_notes: sendForm.advisorNotes || undefined,
          course_label: courseLabel(sendForm.courseType),
        },
      });
      setSuccessMessage("Enrollment agreement sent successfully.");
      setSendForm({
        studentId: "",
        templateId: "",
        courseType: "twenty_week",
        signerName: "",
        signerEmail: "",
        advisorNotes: "",
      });
      loadAgreements();
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || "Unable to send agreement.");
    } finally {
      setSending(false);
      setTimeout(() => setSuccessMessage(""), 4000);
    }
  };

  const openCounterSign = (document) => {
    setCounterModal({
      open: true,
      document,
      typedName: "",
      signatureData: null,
      saving: false,
      error: null,
    });
  };

  const closeCounterModal = () => {
    setCounterModal((prev) => ({
      ...prev,
      open: false,
      document: null,
      typedName: "",
      signatureData: null,
      error: null,
    }));
  };

  const handleCounterSignatureSave = (dataUrl) => {
    const base64 = dataUrl?.split(",")[1] || null;
    setCounterModal((prev) => ({
      ...prev,
      signatureData: base64,
      error: null,
    }));
  };

  const submitCounterSignature = async () => {
    if (!counterModal.document) return;
    if (!counterModal.typedName.trim()) {
      setCounterModal((prev) => ({
        ...prev,
        error: "Please enter your full name.",
      }));
      return;
    }
    if (!counterModal.signatureData) {
      setCounterModal((prev) => ({
        ...prev,
        error: "Please provide and save your signature.",
      }));
      return;
    }

    setCounterModal((prev) => ({ ...prev, saving: true, error: null }));
    try {
      await counterSignDocument(counterModal.document.id, {
        typed_name: counterModal.typedName.trim(),
        signature_data: counterModal.signatureData,
      });
      closeCounterModal();
      loadAgreements();
      setViewerModal((prev) =>
        prev.document?.id === counterModal.document.id
          ? { ...prev, document: { ...prev.document, status: "completed" } }
          : prev
      );
    } catch (err) {
      console.error(err);
      setCounterModal((prev) => ({
        ...prev,
        error: err.response?.data?.detail || "Unable to counter-sign document.",
        saving: false,
      }));
    }
  };

  const openDocumentViewer = async (doc) => {
    if (!doc) return;
    setViewerModal((prev) => {
      if (prev.pdfUrl) {
        URL.revokeObjectURL(prev.pdfUrl);
      }
      return {
        open: true,
        document: doc,
        pdfUrl: "",
        loading: true,
        error: null,
      };
    });
    try {
      const blobResponse = await fetchDocumentBlob(doc.id);
      const fileBlob = blobResponse instanceof Blob ? blobResponse : new Blob([blobResponse], { type: "application/pdf" });
      const url = URL.createObjectURL(fileBlob);
      setViewerModal((prev) => ({
        ...prev,
        loading: false,
        pdfUrl: url,
      }));
    } catch (err) {
      console.error(err);
      setViewerModal((prev) => ({
        ...prev,
        loading: false,
        error: err?.response?.data?.detail || "Unable to load document preview.",
      }));
    }
  };

  const closeViewerModal = () => {
    setViewerModal((prev) => {
      if (prev.pdfUrl) {
        URL.revokeObjectURL(prev.pdfUrl);
      }
      return {
        open: false,
        document: null,
        pdfUrl: "",
        loading: false,
        error: null,
      };
    });
  };

  const stats = useMemo(() => {
    const total = agreements.length;
    const awaiting = agreements.filter((doc) => doc.status === "student_signed").length;
    const completed = agreements.filter((doc) => doc.status === "completed").length;
    return { total, awaiting, completed };
  }, [agreements]);

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-primary-800">Enrollment Agreements</h1>
        <p className="text-sm text-slate-600">
          Send, track, and counter-sign enrollment agreements for each cohort.
        </p>
      </div>

      {error && (
        <div className="rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-red-700">
          {error}
        </div>
      )}
      {successMessage && (
        <div className="rounded-lg bg-emerald-50 border border-emerald-200 px-4 py-3 text-emerald-700">
          {successMessage}
        </div>
      )}

      <div className="grid gap-4 md:grid-cols-3">
        <div className="bg-white rounded-xl border border-slate-200 p-4">
          <p className="text-sm text-slate-500">Active agreements</p>
          <p className="text-3xl font-semibold text-primary-700 mt-1">{stats.total}</p>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-4">
          <p className="text-sm text-slate-500">Awaiting AADA signature</p>
          <p className="text-3xl font-semibold text-amber-600 mt-1">{stats.awaiting}</p>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-4">
          <p className="text-sm text-slate-500">Completed this term</p>
          <p className="text-3xl font-semibold text-emerald-600 mt-1">{stats.completed}</p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-5">
        <form
          onSubmit={handleSend}
          className="bg-white border border-slate-200 rounded-2xl p-5 space-y-4 lg:col-span-2"
        >
          <div>
            <h2 className="text-lg font-semibold text-primary-800">Send new agreement</h2>
            <p className="text-sm text-slate-500">
              Choose the student and course track to generate the enrollment agreement.
            </p>
          </div>

          <div className="space-y-1">
            <label className="text-sm font-medium text-slate-700">Student</label>
            <select
              data-testid="agreement-student-select"
              value={sendForm.studentId}
              onChange={(e) =>
                setSendForm((prev) => ({ ...prev, studentId: e.target.value }))
              }
              className="w-full border border-slate-300 rounded-lg px-3 py-2 focus:ring-primary-500 focus:border-primary-500"
              required
            >
              <option value="">Select a student</option>
              {students.map((student) => (
                <option key={student.id} value={student.id}>
                  {student.first_name} {student.last_name} • {student.email}
                </option>
              ))}
            </select>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-700">Course</label>
            <div className="flex flex-wrap gap-2">
              {COURSE_OPTIONS.map((course) => (
                <button
                  type="button"
                  key={course.value}
                  disabled={course.disabled}
                  onClick={() =>
                    !course.disabled &&
                    setSendForm((prev) => ({ ...prev, courseType: course.value }))
                  }
                  className={`px-3 py-1.5 rounded-full text-sm border transition ${
                    sendForm.courseType === course.value
                      ? "border-primary-500 bg-primary-50 text-primary-700"
                      : "border-slate-300 text-slate-600 hover:border-primary-300"
                  } ${course.disabled ? "opacity-50 cursor-not-allowed" : ""}`}
                >
                  {course.label}
                </button>
              ))}
            </div>
          </div>

          <div className="space-y-1">
            <label className="text-sm font-medium text-slate-700">Template</label>
            <select
              data-testid="agreement-template-select"
              value={sendForm.templateId}
              onChange={(e) =>
                setSendForm((prev) => ({ ...prev, templateId: e.target.value }))
              }
              className="w-full border border-slate-300 rounded-lg px-3 py-2 focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="">Latest enrollment template</option>
              {enrollmentTemplates.map((tpl) => (
                <option key={tpl.id} value={tpl.id}>
                  {tpl.name} v{tpl.version}
                </option>
              ))}
            </select>
            {enrollmentTemplates.length === 0 && (
              <p className="text-xs text-amber-600 mt-1">
                Upload an “Enrollment Agreement” template first.
              </p>
            )}
          </div>

          <div className="grid grid-cols-1 gap-3">
            <TextField
              size="small"
              label="Override signer name"
              value={sendForm.signerName}
              onChange={(e) =>
                setSendForm((prev) => ({ ...prev, signerName: e.target.value }))
              }
            />
            <TextField
              size="small"
              label="Override signer email"
              value={sendForm.signerEmail}
              onChange={(e) =>
                setSendForm((prev) => ({ ...prev, signerEmail: e.target.value }))
              }
            />
            <TextField
              size="small"
              label="Advisor notes"
              multiline
              minRows={2}
              value={sendForm.advisorNotes}
              onChange={(e) =>
                setSendForm((prev) => ({ ...prev, advisorNotes: e.target.value }))
              }
            />
          </div>

          <Button
            type="submit"
            variant="contained"
            disabled={sending || (enrollmentTemplates.length === 0 && !sendForm.templateId)}
            sx={{ mt: 1, textTransform: "none", bgcolor: "#d4af37", "&:hover": { bgcolor: "#bb972e" } }}
            fullWidth
          >
            {sending ? "Sending..." : "Send Agreement"}
          </Button>
        </form>

        <div className="bg-white border border-slate-200 rounded-2xl p-5 lg:col-span-3">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div className="flex gap-2">
              {COURSE_OPTIONS.map((course) => (
                <button
                  key={course.value}
                  disabled={course.disabled}
                  onClick={() => !course.disabled && setCourseFilter(course.value)}
                  className={`px-4 py-2 rounded-full text-sm font-medium border transition ${
                    courseFilter === course.value
                      ? "border-primary-500 bg-primary-50 text-primary-700"
                      : "border-slate-300 text-slate-600 hover:border-primary-300"
                  } ${course.disabled ? "opacity-40 cursor-not-allowed" : ""}`}
                >
                  {course.label}
                </button>
              ))}
            </div>
            <TextField
              select
              size="small"
              label="Status"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              sx={{ minWidth: 200 }}
            >
              {STATUS_OPTIONS.map((status) => (
                <MenuItem key={status.value} value={status.value}>
                  {status.label}
                </MenuItem>
              ))}
            </TextField>
          </div>

          <div className="mt-4 overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200 text-sm">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-4 py-2 text-left font-semibold text-slate-600">Student</th>
                  <th className="px-4 py-2 text-left font-semibold text-slate-600">Course</th>
                  <th className="px-4 py-2 text-left font-semibold text-slate-600">Status</th>
                  <th className="px-4 py-2 text-left font-semibold text-slate-600">Sent</th>
                  <th className="px-4 py-2 text-left font-semibold text-slate-600">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {loading && (
                  <tr>
                    <td colSpan={5} className="px-4 py-6 text-center text-slate-500">
                      Loading agreements...
                    </td>
                  </tr>
                )}
                {!loading && agreements.length === 0 && (
                  <tr>
                    <td colSpan={5} className="px-4 py-6 text-center text-slate-500">
                      No agreements match the selected filters.
                    </td>
                  </tr>
                )}
                {!loading &&
                  agreements.map((doc) => {
                    const student = studentsById.get(doc.user_id);
                    const statusClass = statusStyles[doc.status] || "bg-slate-100 text-slate-700";
                    return (
                      <tr
                        key={doc.id}
                        className="hover:bg-slate-50 cursor-pointer"
                        onClick={() => openDocumentViewer(doc)}
                        role="button"
                        tabIndex={0}
                        onKeyDown={(event) => {
                          if (event.key === "Enter" || event.key === " ") {
                            event.preventDefault();
                            openDocumentViewer(doc);
                          }
                        }}
                      >
                        <td className="px-4 py-3">
                          <div className="font-medium text-slate-900">
                            {student ? `${student.first_name} ${student.last_name}` : "Student"}
                          </div>
                          <div className="text-xs text-slate-500">{student?.email || "N/A"}</div>
                        </td>
                        <td className="px-4 py-3">
                          <div className="text-sm text-slate-700">{courseLabel(doc.course_type)}</div>
                          {doc.form_data?.advisor_notes && (
                            <div className="text-xs text-slate-500 truncate max-w-xs">
                              Notes: {doc.form_data.advisor_notes}
                            </div>
                          )}
                        </td>
                        <td className="px-4 py-3">
                          <span className={`inline-flex px-3 py-1 rounded-full text-xs font-semibold ${statusClass}`}>
                            {doc.status === "student_signed"
                              ? "Awaiting counter-sign"
                              : doc.status.charAt(0).toUpperCase() + doc.status.slice(1)}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-sm text-slate-600">
                          {doc.sent_at
                            ? format(new Date(doc.sent_at), "MMM d, yyyy")
                            : format(new Date(doc.created_at), "MMM d, yyyy")}
                        </td>
                        <td className="px-4 py-3">
                          {doc.status === "student_signed" ? (
                            <button
                              type="button"
                              className="px-3 py-1.5 rounded-lg text-sm font-medium bg-primary-600 text-white hover:bg-primary-700"
                              onClick={(event) => {
                                event.stopPropagation();
                                openCounterSign(doc);
                              }}
                            >
                              Counter-sign
                            </button>
                          ) : (
                            <span className="text-xs text-slate-500">No actions</span>
                          )}
                        </td>
                      </tr>
                    );
                  })}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <Dialog open={counterModal.open} onClose={closeCounterModal} maxWidth="md" fullWidth>
        <DialogTitle>Counter-sign enrollment agreement</DialogTitle>
        <DialogContent>
          {counterModal.error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {counterModal.error}
            </Alert>
          )}
          <div className="space-y-3 mt-1">
            <TextField
              label="Authorized signer name"
              value={counterModal.typedName}
              onChange={(e) =>
                setCounterModal((prev) => ({ ...prev, typedName: e.target.value }))
              }
              fullWidth
              variant="outlined"
              size="small"
            />
            <SignaturePad onSave={handleCounterSignatureSave} label="Draw signature" />
            <p className="text-xs text-slate-500">
              Saved signatures are stored securely with the document audit log.
            </p>
          </div>
        </DialogContent>
        <DialogActions>
          <Button onClick={closeCounterModal} disabled={counterModal.saving}>
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={submitCounterSignature}
            disabled={counterModal.saving}
          >
            {counterModal.saving ? "Submitting..." : "Submit signature"}
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={viewerModal.open} onClose={closeViewerModal} maxWidth="lg" fullWidth>
        <DialogTitle>Enrollment agreement</DialogTitle>
        <DialogContent dividers>
          {viewerModal.document && (
            <div className="mb-4 text-sm text-slate-600 space-y-1">
              <p>
                <span className="font-medium text-slate-700">Status:</span>{" "}
                {viewerModal.document.status === "student_signed"
                  ? "Awaiting counter-sign"
                  : viewerModal.document.status?.replace("_", " ")}
              </p>
              {viewerModal.document.sent_at && (
                <p>
                  <span className="font-medium text-slate-700">Sent:</span>{" "}
                  {format(new Date(viewerModal.document.sent_at), "MMM d, yyyy")}
                </p>
              )}
            </div>
          )}
          {viewerModal.loading && (
            <div className="py-10 text-center text-primary-700">Loading document preview...</div>
          )}
          {viewerModal.error && <Alert severity="error">{viewerModal.error}</Alert>}
          {!viewerModal.loading && !viewerModal.error && viewerModal.pdfUrl && (
            <iframe
              title="Agreement Preview"
              src={viewerModal.pdfUrl}
              className="w-full h-[600px] border border-slate-200 rounded-lg"
            />
          )}
        </DialogContent>
        <DialogActions>
          {viewerModal.document?.status === "student_signed" && canCounterSign && (
            <Button
              variant="contained"
              onClick={() => {
                openCounterSign(viewerModal.document);
              }}
              sx={{ textTransform: "none" }}
            >
              Counter-sign
            </Button>
          )}
          <Button onClick={closeViewerModal}>Close</Button>
        </DialogActions>
      </Dialog>
    </div>
  );
};

export default Agreements;
