import { useState, useEffect, useRef, useMemo } from "react";
import { useParams } from "react-router-dom";
import SignatureCanvas from "react-signature-canvas";
import axios from "axios";

import { resolveApiBaseUrl } from "@/utils/apiBase";

const API_BASE_URL = `${resolveApiBaseUrl()}/api`;

interface DocumentData {
  template_name?: string;
  template_description?: string;
  signer_name?: string;
  signer_email?: string;
  expires_at?: string;
  course_type?: string;
  course_label?: string;
  form_data?: Record<string, unknown>;
}

interface EnrollmentFormValues {
  phone: string;
  preferred_start: string;
  emergency_contact: string;
  housing_needs: string;
  questions: string;
  acknowledgements: Record<string, string>;
}

const steps = [
  { id: "overview", title: "Review agreement" },
  { id: "details", title: "Student details & acknowledgements" },
  { id: "signature", title: "Sign" },
];

const ACKNOWLEDGEMENT_FIELDS = [
  {
    key: "initial_agreement_catalog",
    label: "I have read and received the enrollment agreement and school catalog.",
  },
  {
    key: "initial_school_outcomes",
    label: "I reviewed the school's retention, graduation, placement, and licensure results.",
  },
  {
    key: "initial_employment",
    label: "I understand job placement assistance is offered but employment/salary are not guaranteed.",
  },
  {
    key: "initial_refund_policy",
    label: "I reviewed the refund policy provided in the catalog.",
  },
  {
    key: "initial_complaint_procedure",
    label: "I reviewed the complaint procedure and appeal options.",
  },
  {
    key: "initial_authorization",
    label:
      "I acknowledge the school's authorization status and that credits may not transfer to other institutions.",
  },
];

export default function PublicSign() {
  const { token } = useParams();
  const sigPad = useRef<SignatureCanvas | null>(null);

  const [loading, setLoading] = useState(true);
  const [document, setDocument] = useState<DocumentData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [typedName, setTypedName] = useState("");
  const [signing, setSigning] = useState(false);
  const [signed, setSigned] = useState(false);
  const [signatureError, setSignatureError] = useState("");
  const [activeStep, setActiveStep] = useState(0);
  const [formError, setFormError] = useState<string | null>(null);
  const [formValues, setFormValues] = useState<EnrollmentFormValues>({
    phone: "",
    preferred_start: "",
    emergency_contact: "",
    housing_needs: "not_needed",
    questions: "",
    acknowledgements: ACKNOWLEDGEMENT_FIELDS.reduce(
      (acc, field) => ({ ...acc, [field.key]: "" }),
      {}
    ),
  });

  const courseLabel = useMemo(() => {
    if (document?.course_label) return document.course_label;
    if (!document?.course_type) return "Enrollment Agreement";
    if (document.course_type === "twenty_week") return "20-Week Course";
    if (document.course_type === "expanded_functions") return "Expanded Functions Course";
    return "Enrollment Agreement";
  }, [document]);

  useEffect(() => {
    const fetchDocument = async () => {
      try {
        setLoading(true);
        const response = await axios.get(`${API_BASE_URL}/public/sign/${token}`);
        setDocument(response.data);
        setTypedName(response.data.signer_name || "");
        if (response.data.form_data) {
          setFormValues((prev) => ({
            ...prev,
            ...response.data.form_data,
            acknowledgements: {
              ...prev.acknowledgements,
              ...(response.data.form_data.acknowledgements || {}),
            },
          }));
        }
      } catch (err: any) {
        if (err.response?.status === 404) {
          setError("Document not found or link has expired");
        } else if (err.response?.status === 429) {
          setError("Too many requests. Please try again later.");
        } else if (
          err.response?.status === 400 &&
          err.response?.data?.detail?.includes("already been signed")
        ) {
          setError("This document has already been signed");
        } else {
          setError("Failed to load document. Please check your link and try again.");
        }
      } finally {
        setLoading(false);
      }
    };

    if (token) {
      fetchDocument();
    } else {
      setError("Invalid signing link");
      setLoading(false);
    }
  }, [token]);

  const clearSignature = () => {
    sigPad.current?.clear();
    setSignatureError("");
  };

  const handleNextStep = () => {
    if (activeStep === 1) {
      if (!formValues.phone.trim()) {
        setFormError("Please provide a phone number so our team can reach you.");
        return;
      }
      const missingAck = ACKNOWLEDGEMENT_FIELDS.find(
        (field) => !formValues.acknowledgements[field.key]?.trim()
      );
      if (missingAck) {
        setFormError("Please type your initials for every acknowledgement.");
        return;
      }
    }
    setFormError(null);
    setSignatureError("");
    setActiveStep((prev) => Math.min(prev + 1, steps.length - 1));
  };

  const handleBack = () => {
    setFormError(null);
    setSignatureError("");
    setActiveStep((prev) => Math.max(prev - 1, 0));
  };

  const handleSubmit = async () => {
    setSignatureError("");
    if (!typedName.trim()) {
      setSignatureError("Please type your full name");
      return;
    }
    if (sigPad.current?.isEmpty()) {
      setSignatureError("Please provide your signature");
      return;
    }

    try {
      setSigning(true);
      const signatureData = sigPad.current?.toDataURL()?.split(",")[1];
      await axios.post(`${API_BASE_URL}/public/sign/${token}`, {
        signature_data: signatureData,
        typed_name: typedName.trim(),
        form_data: formValues,
      });
      setSigned(true);
    } catch (err: any) {
      if (err.response?.status === 400) {
        setSignatureError(err.response.data?.detail || "Invalid signature data");
      } else if (err.response?.status === 404) {
        setSignatureError("Document not found or link has expired");
      } else if (err.response?.status === 429) {
        setSignatureError("Too many requests. Please try again later.");
      } else {
        setSignatureError("Failed to submit signature. Please try again.");
      }
    } finally {
      setSigning(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading document...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="max-w-md w-full bg-white shadow-lg rounded-lg p-8">
          <div className="text-center">
            <svg className="mx-auto h-12 w-12 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <h2 className="mt-4 text-xl font-semibold text-gray-900">Unable to Load Document</h2>
            <p className="mt-2 text-gray-600">{error}</p>
            <p className="mt-4 text-sm text-gray-500">
              If you believe this is an error, please contact the school administrator.
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (signed) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="max-w-md w-full bg-white shadow-lg rounded-lg p-8">
          <div className="text-center">
            <svg className="mx-auto h-12 w-12 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h2 className="mt-4 text-xl font-semibold text-gray-900">Document Signed Successfully!</h2>
            <p className="mt-2 text-gray-600">
              Your signature has been recorded and the document has been completed.
            </p>
            {document?.template_name && (
              <p className="mt-4 text-sm text-gray-500">
                Document: {document.template_name}
              </p>
            )}
            <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
              <p className="text-sm text-blue-800">
                <strong>What's next?</strong>
              </p>
              <p className="text-sm text-blue-700 mt-1">
                You will receive a copy of the signed document via email. A school representative will contact you regarding next steps.
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 py-10 px-4">
      <div className="max-w-4xl mx-auto space-y-6">
        <header className="bg-white rounded-2xl shadow p-6 space-y-2">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <p className="text-sm text-slate-500 uppercase tracking-wide">{courseLabel}</p>
              <h1 className="text-2xl font-semibold text-slate-900">
                {document?.template_name || "Enrollment Agreement"}
              </h1>
              {document?.template_description && (
                <p className="text-sm text-slate-500 mt-1">{document.template_description}</p>
              )}
            </div>
            <div className="flex flex-col items-end text-sm text-slate-500">
              <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-50 text-amber-700 text-xs font-semibold">
                Awaiting signature
              </span>
              {document?.expires_at && (
                <span className="mt-2">
                  Link expires {new Date(document.expires_at).toLocaleDateString()}
                </span>
              )}
            </div>
          </div>
          <dl className="grid grid-cols-1 gap-4 border-t border-slate-200 pt-4 md:grid-cols-2">
            <div>
              <dt className="text-xs uppercase tracking-wide text-slate-500">Student</dt>
              <dd className="text-sm text-slate-900">{document?.signer_name || "Student"}</dd>
            </div>
            <div>
              <dt className="text-xs uppercase tracking-wide text-slate-500">Email</dt>
              <dd className="text-sm text-slate-900">{document?.signer_email}</dd>
            </div>
          </dl>
        </header>

        <section className="bg-white rounded-2xl shadow divide-y divide-slate-100">
          <div className="flex flex-col gap-4 px-6 py-4 md:flex-row md:items-center md:justify-between">
            <div className="flex gap-2">
              {steps.map((step, idx) => (
                <div key={step.id} className="flex items-center gap-2 text-sm font-medium">
                  <div
                    className={`h-8 w-8 rounded-full flex items-center justify-center ${
                      idx <= activeStep
                        ? "bg-primary-600 text-white"
                        : "bg-slate-100 text-slate-500"
                    }`}
                  >
                    {idx + 1}
                  </div>
                  <span className={idx === activeStep ? "text-primary-700" : "text-slate-500"}>
                    {step.title}
                  </span>
                  {idx < steps.length - 1 && (
                    <div className="hidden md:block w-12 h-px bg-slate-200 mx-1" />
                  )}
                </div>
              ))}
            </div>
            <p className="text-xs text-slate-500">
              Step {activeStep + 1} of {steps.length}
            </p>
          </div>

          <div className="p-6 space-y-6">
            {activeStep === 0 && (
              <div className="space-y-4">
                <h2 className="text-xl font-semibold text-slate-900">Review the agreement</h2>
                <p className="text-sm text-slate-600">
                  Please take a moment to review the summary below. You can download the full PDF
                  in your welcome email or request a copy from the admissions team.
                </p>
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="rounded-xl border border-slate-200 p-4">
                    <p className="text-xs font-semibold text-slate-500 uppercase">Program</p>
                    <p className="text-lg text-slate-900 mt-1">{courseLabel}</p>
                    <p className="text-xs text-slate-500 mt-2">
                      Confirm this is the track you intend to enroll in.
                    </p>
                  </div>
                  <div className="rounded-xl border border-slate-200 p-4">
                    <p className="text-xs font-semibold text-slate-500 uppercase">Contact</p>
                    <p className="text-sm text-slate-900 mt-1">
                      admissions@aada.edu • (404) 555-1234
                    </p>
                    <p className="text-xs text-slate-500 mt-2">
                      Reach out if anything looks incorrect or you have questions.
                    </p>
                  </div>
                </div>
                <ul className="list-disc pl-6 text-sm text-slate-600 space-y-2">
                  <li>Review tuition, fees, and payment schedule outlined in the agreement.</li>
                  <li>Confirm that your contact information is accurate.</li>
                  <li>Plan for the listed clinical dates and required equipment.</li>
                </ul>
              </div>
            )}

            {activeStep === 1 && (
              <div className="space-y-4">
                <h2 className="text-xl font-semibold text-slate-900">Tell us about you</h2>
                <p className="text-sm text-slate-600">
                  We use this information to finalize your enrollment and connect you with our
                  student success team.
                </p>
                {formError && (
                  <p className="text-sm text-red-600 bg-red-50 border border-red-100 rounded-lg px-3 py-2">
                    {formError}
                  </p>
                )}
                <div className="space-y-3">
                  <div>
                    <label className="text-sm font-medium text-slate-700" htmlFor="student-phone">
                      Phone number
                    </label>
                  <input
                    id="student-phone"
                    name="student-phone"
                    type="tel"
                    value={formValues.phone}
                    onChange={(e) =>
                      setFormValues((prev) => ({ ...prev, phone: e.target.value }))
                    }
                    className="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                    placeholder="(555) 123-4567"
                  />
                  </div>
                  <div>
                    <label className="text-sm font-medium text-slate-700" htmlFor="student-start">
                      Preferred start date
                    </label>
                  <input
                    id="student-start"
                    name="student-start"
                    type="date"
                    value={formValues.preferred_start}
                    onChange={(e) =>
                      setFormValues((prev) => ({ ...prev, preferred_start: e.target.value }))
                    }
                    className="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2"
                  />
                  </div>
                  <div>
                    <label className="text-sm font-medium text-slate-700" htmlFor="student-emergency">
                      Emergency contact
                    </label>
                  <input
                    id="student-emergency"
                    name="student-emergency"
                    type="text"
                    value={formValues.emergency_contact}
                    onChange={(e) =>
                      setFormValues((prev) => ({ ...prev, emergency_contact: e.target.value }))
                    }
                    className="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2"
                    placeholder="Name & phone"
                  />
                  </div>
                  <div>
                    <label className="text-sm font-medium text-slate-700" htmlFor="student-housing">
                      Housing needs
                    </label>
                  <select
                    id="student-housing"
                    name="student-housing"
                    value={formValues.housing_needs}
                    onChange={(e) =>
                      setFormValues((prev) => ({ ...prev, housing_needs: e.target.value }))
                    }
                    className="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2"
                  >
                      <option value="not_needed">No housing support needed</option>
                      <option value="interested">I’d like housing resources</option>
                      <option value="undecided">Undecided</option>
                    </select>
                  </div>
                  <div>
                    <label
                      className="text-sm font-medium text-slate-700"
                      htmlFor="student-questions"
                    >
                      Questions or accessibility requests
                    </label>
                  <textarea
                    id="student-questions"
                    name="student-questions"
                    value={formValues.questions}
                    onChange={(e) =>
                      setFormValues((prev) => ({ ...prev, questions: e.target.value }))
                    }
                    className="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2"
                    rows={3}
                    placeholder="Let us know if there’s anything we can prepare before class begins."
                  />
                  </div>
                </div>

                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-slate-900">Acknowledgements</h3>
                  <p className="text-sm text-slate-600">
                    Please type your initials in each box to confirm you have read and understand the statements below.
                    These acknowledgements will appear on your final enrollment agreement.
                  </p>
                  <div className="space-y-4">
                    {ACKNOWLEDGEMENT_FIELDS.map((field) => (
                      <div
                        key={field.key}
                        className="bg-slate-50 border border-slate-200 rounded-xl p-4 space-y-3"
                      >
                        <p className="text-sm text-slate-700">{field.label}</p>
                        <div className="flex items-center gap-3">
                          <input
                            type="text"
                            maxLength={4}
                            value={formValues.acknowledgements[field.key] || ""}
                            onChange={(e) =>
                              setFormValues((prev) => ({
                                ...prev,
                                acknowledgements: {
                                  ...prev.acknowledgements,
                                  [field.key]: e.target.value.toUpperCase(),
                                },
                              }))
                            }
                            className="w-24 text-center uppercase border border-slate-300 rounded-lg px-3 py-2 focus:ring-primary-500 focus:border-primary-500 tracking-wide"
                            placeholder="ABC"
                          />
                          <span className="text-xs text-slate-500">Initials</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

              </div>
            )}

            {activeStep === 2 && (
              <div className="space-y-4">
                <h2 className="text-xl font-semibold text-slate-900">Sign your agreement</h2>
                <p className="text-sm text-slate-600">
                  Please type your full legal name and draw your signature. Both will appear on the
                  final enrollment agreement.
                </p>

                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-700" htmlFor="typedName">
                    Full name
                  </label>
                  <input
                    id="typedName"
                    name="typedName"
                    type="text"
                    value={typedName}
                    onChange={(e) => setTypedName(e.target.value)}
                    className="w-full border border-slate-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Draw signature
                  </label>
                  <div className="border-2 border-dashed border-slate-300 rounded-xl bg-white">
                    <SignatureCanvas
                      ref={sigPad}
                      canvasProps={{
                        className: "w-full h-48 cursor-crosshair",
                      }}
                      backgroundColor="white"
                    />
                  </div>
                  <div className="flex justify-between text-xs text-slate-500 mt-2">
                    <span>Use your mouse, stylus, or finger to sign.</span>
                    <button
                      type="button"
                      onClick={clearSignature}
                      className="text-primary-600 hover:text-primary-700 font-medium"
                    >
                      Clear signature
                    </button>
                  </div>
                  {signatureError && (
                    <p className="text-xs text-red-600 mt-2">{signatureError}</p>
                  )}
                </div>

                <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 text-sm text-slate-600">
                  <strong className="text-slate-800">Electronic Signature Consent:</strong> By
                  submitting this form you agree that your electronic signature is the legal
                  equivalent of your handwritten signature on this agreement.
                </div>
              </div>
            )}

            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <button
                type="button"
                onClick={handleBack}
                disabled={activeStep === 0}
                className="px-4 py-2 rounded-lg border border-slate-200 text-sm font-medium text-slate-600 disabled:opacity-40"
              >
                Back
              </button>

              {activeStep < steps.length - 1 ? (
                <button
                  type="button"
                  onClick={handleNextStep}
                  className="px-4 py-2 rounded-lg bg-primary-600 text-white text-sm font-semibold hover:bg-primary-700"
                >
                  Next step
                </button>
              ) : (
                <button
                  type="button"
                  onClick={handleSubmit}
                  disabled={signing}
                  className="px-4 py-2 rounded-lg bg-primary-600 text-white text-sm font-semibold hover:bg-primary-700 disabled:opacity-50"
                >
                  {signing ? "Submitting..." : "Submit signature"}
                </button>
              )}
            </div>
          </div>
        </section>

        <footer className="text-center text-xs text-slate-500">
          This secure workflow meets ESIGN and HIPAA requirements. Need help? Email
          admissions@aada.edu.
        </footer>
      </div>
    </div>
  );
}
