import { useState, useEffect, useRef, useMemo, useCallback } from "react";
import { useParams } from "react-router-dom";
import SignatureCanvas from "react-signature-canvas";
import axios from "axios";

import { resolveApiBaseUrl } from "@/utils/apiBase";
import type {
  AgreementSchema,
  AgreementSection,
  SchemaElement,
  FieldDefinition,
  FieldGroupElement,
  TableElement,
  ListElement,
  AcknowledgementListElement,
} from "@/types/enrollmentAgreement";

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
  agreement_schema?: AgreementSchema;
}

const steps = [
  { id: "agreement", title: "Agreement & Details" },
  { id: "signature", title: "Sign" },
];

const ACK_PATH_PREFIX = "acknowledgements";
const TODAY_TOKEN = "__today__";
const formatToday = () => new Date().toISOString().split("T")[0];
const WIOA_PAYMENT_OPTIONS = ["wioa_grant", "wioa_only"];

type FormValues = Record<string, any>;
type ValidationErrors = Record<string, string>;

const cloneData = (value?: Record<string, any>): Record<string, any> =>
  JSON.parse(JSON.stringify(value ?? {}));

const getValueAtPath = (data: FormValues, path: string): any => {
  if (!path) return undefined;
  return path.split(".").reduce((acc: any, segment: string) => {
    if (acc === undefined || acc === null) return undefined;
    return acc[segment];
  }, data);
};

const setValueAtPath = (data: FormValues, path: string, value: any): void => {
  const segments = path.split(".");
  let cursor = data;
  segments.forEach((segment, idx) => {
    if (idx === segments.length - 1) {
      cursor[segment] = value;
    } else {
      if (typeof cursor[segment] !== "object" || cursor[segment] === null) {
        cursor[segment] = {};
      }
      cursor = cursor[segment];
    }
  });
};

const valueIsPresent = (value: unknown): boolean => {
  if (typeof value === "string") {
    return value.trim().length > 0;
  }
  if (typeof value === "number") {
    return true;
  }
  if (value instanceof Date) {
    return !Number.isNaN(value.valueOf());
  }
  return value !== undefined && value !== null;
};

const resolveDefaultValue = (field: FieldDefinition): any => {
  if (field.defaultValue === TODAY_TOKEN) {
    return formatToday();
  }
  return field.defaultValue ?? "";
};

const initializeFormValues = (
  schema: AgreementSchema | null,
  existingFormData?: Record<string, unknown>
): FormValues => {
  const initial = cloneData(existingFormData as Record<string, any> | undefined);
  if (typeof initial[ACK_PATH_PREFIX] !== "object" || initial[ACK_PATH_PREFIX] === null) {
    initial[ACK_PATH_PREFIX] = {};
  }

  if (!schema) {
    return initial;
  }

  schema.sections.forEach((section) => {
    section.elements.forEach((element) => {
      if (element.type === "field_group") {
        element.fields.forEach((field) => {
          const currentValue = getValueAtPath(initial, field.name);
          if (currentValue === undefined) {
            setValueAtPath(initial, field.name, resolveDefaultValue(field));
          }
        });
      }

      if (element.type === "acknowledgement_list") {
        element.acknowledgements.forEach((ack) => {
          if (!initial[ACK_PATH_PREFIX][ack.id]) {
            initial[ACK_PATH_PREFIX][ack.id] = "";
          }
        });
      }
    });
  });

  return initial;
};

const validateFormValues = (
  schema: AgreementSchema | null,
  values: FormValues,
  paymentSelection: string | undefined
): ValidationErrors => {
  if (!schema) {
    return {};
  }

  const errors: ValidationErrors = {};

  schema.sections.forEach((section) => {
    section.elements.forEach((element) => {
      if (element.type === "field_group") {
        element.fields.forEach((field) => {
          if (field.required && !shouldHideField(field, paymentSelection)) {
            const currentValue = getValueAtPath(values, field.name);
            if (!valueIsPresent(currentValue)) {
              errors[field.name] = "This field is required.";
            }
          }
        });
      }

      if (element.type === "acknowledgement_list") {
        element.acknowledgements.forEach((ack) => {
          const ackValue = values?.[ACK_PATH_PREFIX]?.[ack.id];
          if (ack.required && (!ackValue || !ackValue.trim())) {
            errors[`${ACK_PATH_PREFIX}.${ack.id}`] = "Initials are required.";
          }
        });
      }
    });
  });

  return errors;
};

const parseCurrency = (value: unknown): number => {
  if (value === null || value === undefined) return 0;
  if (typeof value === "number") return value;
  const sanitized = `${value}`.replace(/[^0-9.-]/g, "");
  const parsed = parseFloat(sanitized);
  return Number.isFinite(parsed) ? parsed : 0;
};

const getProgramTotalFromSchema = (schema: AgreementSchema | null): number | null => {
  if (!schema) return null;
  for (const section of schema.sections) {
    for (const element of section.elements) {
      if (element.type === "table" && element.title?.toLowerCase().includes("program cost")) {
        for (const row of element.rows) {
          const label = typeof row[0] === "string" ? row[0].toLowerCase() : null;
          if (label && label.includes("program total")) {
            return parseCurrency(row[1]);
          }
        }
      }
    }
  }
  return null;
};

const shouldHideField = (field: FieldDefinition, paymentSelection: string | undefined) => {
  if (field.name === "program.wioa_county" || field.name === "program.wioa_advisor_name" || field.name === "program.wioa_advisor_email") {
    return !WIOA_PAYMENT_OPTIONS.includes(paymentSelection || "");
  }
  return false;
};

const findFieldLabel = (schema: AgreementSchema | null, fieldPath: string): string | null => {
  if (!schema) {
    return null;
  }
  if (fieldPath.startsWith(`${ACK_PATH_PREFIX}.`)) {
    const ackId = fieldPath.split(".")[1];
    for (const section of schema.sections) {
      for (const element of section.elements) {
        if (element.type === "acknowledgement_list") {
          const match = element.acknowledgements.find((ack) => ack.id === ackId);
          if (match) {
            return match.label;
          }
        }
      }
    }
  }
  for (const section of schema.sections) {
    for (const element of section.elements) {
      if (element.type === "field_group") {
        const match = element.fields.find((field) => field.name === fieldPath);
        if (match) {
          return match.label;
        }
      }
    }
  }
  return null;
};

export default function PublicSign() {
  const { token } = useParams();
  const sigPad = useRef<SignatureCanvas | null>(null);

  const [loading, setLoading] = useState(true);
  const [document, setDocument] = useState<DocumentData | null>(null);
  const [agreementSchema, setAgreementSchema] = useState<AgreementSchema | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [typedName, setTypedName] = useState("");
  const [signing, setSigning] = useState(false);
  const [signed, setSigned] = useState(false);
  const [signatureError, setSignatureError] = useState("");
  const [activeStep, setActiveStep] = useState(0);
  const [formError, setFormError] = useState<string | null>(null);
  const [validationErrors, setValidationErrors] = useState<ValidationErrors>({});
  const [formValues, setFormValues] = useState<FormValues>({});

  const updateFormValue = useCallback((path: string, value: any) => {
    setFormValues((prev) => {
      const draft = cloneData(prev);
      setValueAtPath(draft, path, value);
      return draft;
    });
  }, []);

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
        setAgreementSchema(response.data.agreement_schema || null);
        setTypedName(response.data.signer_name || "");
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

  useEffect(() => {
    if (!document) {
      return;
    }
    const schema = document.agreement_schema || agreementSchema;
    if (!schema) {
      return;
    }
    setFormValues(initializeFormValues(schema, document.form_data as Record<string, unknown>));
  }, [document, agreementSchema]);


  const programTotalAmount = useMemo(() => getProgramTotalFromSchema(agreementSchema), [agreementSchema]);
  const depositValue = getValueAtPath(formValues, "financial.deposit_amount");
  const remainingBalanceValue = getValueAtPath(formValues, "financial.remaining_balance");
  const paymentSelection = useMemo(
    () => getValueAtPath(formValues, "program.payment_selection"),
    [formValues]
  );

  useEffect(() => {
    if (programTotalAmount === null) {
      return;
    }
    const depositNumber = parseCurrency(depositValue);
    const computed = Math.max(programTotalAmount - depositNumber, 0);
    const formatted = computed.toFixed(2);

    if (remainingBalanceValue !== formatted) {
      setFormValues((prev) => {
        const next = cloneData(prev);
        setValueAtPath(next, "financial.remaining_balance", formatted);
        return next;
      });
    }
  }, [depositValue, remainingBalanceValue, programTotalAmount]);

  useEffect(() => {
    if (WIOA_PAYMENT_OPTIONS.includes(paymentSelection || "")) {
      return;
    }
    setFormValues((prev) => {
      const county = getValueAtPath(prev, "program.wioa_county");
      const advisorName = getValueAtPath(prev, "program.wioa_advisor_name");
      const advisorEmail = getValueAtPath(prev, "program.wioa_advisor_email");
      if (!county && !advisorName && !advisorEmail) {
        return prev;
      }
      const next = cloneData(prev);
      setValueAtPath(next, "program.wioa_county", "");
      setValueAtPath(next, "program.wioa_advisor_name", "");
      setValueAtPath(next, "program.wioa_advisor_email", "");
      return next;
    });
  }, [paymentSelection]);

  const clearSignature = () => {
    sigPad.current?.clear();
    setSignatureError("");
  };

  const handleNextStep = () => {
    if (activeStep === 0) {
      const paymentSelection = getValueAtPath(formValues, "program.payment_selection");
      const errors = validateFormValues(agreementSchema, formValues, paymentSelection);
      setValidationErrors(errors);
      if (Object.keys(errors).length) {
        const firstKey = Object.keys(errors)[0];
        const label = findFieldLabel(agreementSchema, firstKey);
        setFormError(
          label
            ? `Please complete “${label}” before continuing.`
            : "Please complete all required fields before continuing."
        );
        return;
      }
    }

    setFormError(null);
    setSignatureError("");
    setValidationErrors({});
    setActiveStep((prev) => Math.min(prev + 1, steps.length - 1));
  };

  const handleBack = () => {
    setFormError(null);
    setSignatureError("");
    setValidationErrors({});
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

  const renderTextElement = (element: SchemaElement) => {
    if (element.type !== "text") return null;
    const baseClass = "text-sm text-slate-700";
    if (element.style === "heading") {
      return <p className="text-xl font-semibold text-slate-900">{element.content}</p>;
    }
    if (element.style === "subheading") {
      return <p className="text-lg font-semibold text-slate-800">{element.content}</p>;
    }
    return <p className={baseClass}>{element.content}</p>;
  };

  const renderField = (field: FieldDefinition) => {
    const paymentSelection = getValueAtPath(formValues, "program.payment_selection");
    if (shouldHideField(field, paymentSelection)) {
      return null;
    }
    const value = getValueAtPath(formValues, field.name) ?? "";
    const error = validationErrors[field.name];
    const commonClasses = "mt-1 w-full border border-slate-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:bg-slate-100 disabled:text-slate-500";

    if (field.component === "textarea") {
      return (
        <div className={field.width === "full" ? "md:col-span-2" : "md:col-span-1"} key={field.name}>
          <label className="text-sm font-medium text-slate-700" htmlFor={field.name}>
            {field.label}
          </label>
          <textarea
            id={field.name}
            name={field.name}
            value={value}
            onChange={(e) => updateFormValue(field.name, e.target.value)}
            className={commonClasses}
            rows={4}
            placeholder={field.placeholder}
            disabled={field.readOnly}
          />
          {field.helperText && <p className="text-xs text-slate-500 mt-1">{field.helperText}</p>}
          {error && <p className="text-xs text-red-600 mt-1">{error}</p>}
        </div>
      );
    }

    if (field.component === "select") {
      return (
        <div className={field.width === "full" ? "md:col-span-2" : "md:col-span-1"} key={field.name}>
          <label className="text-sm font-medium text-slate-700" htmlFor={field.name}>
            {field.label}
          </label>
          <select
            id={field.name}
            name={field.name}
            value={value}
            onChange={(e) => updateFormValue(field.name, e.target.value)}
            className={commonClasses}
            disabled={field.readOnly}
          >
            <option value="">Select</option>
            {field.options?.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          {field.helperText && <p className="text-xs text-slate-500 mt-1">{field.helperText}</p>}
          {error && <p className="text-xs text-red-600 mt-1">{error}</p>}
        </div>
      );
    }

    const inputType =
      field.component === "email"
        ? "email"
        : field.component === "tel"
        ? "tel"
        : field.component === "date"
        ? "date"
        : "text";

    return (
      <div className={field.width === "full" ? "md:col-span-2" : "md:col-span-1"} key={field.name}>
        <label className="text-sm font-medium text-slate-700" htmlFor={field.name}>
          {field.label}
        </label>
        <input
          id={field.name}
          name={field.name}
          type={inputType}
          value={value}
          onChange={(e) => {
            if (field.component === "currency") {
              const sanitized = e.target.value.replace(/[^0-9.]/g, "");
              updateFormValue(field.name, sanitized);
              return;
            }
            updateFormValue(field.name, e.target.value);
          }}
          className={commonClasses}
          placeholder={field.placeholder}
          disabled={field.readOnly}
          inputMode={field.component === "currency" ? "decimal" : undefined}
          maxLength={field.maxLength}
        />
        {field.helperText && <p className="text-xs text-slate-500 mt-1">{field.helperText}</p>}
        {error && <p className="text-xs text-red-600 mt-1">{error}</p>}
      </div>
    );
  };

  const renderFieldGroup = (element: FieldGroupElement) => (
    <div className="space-y-3">
      {element.title && <h4 className="text-lg font-semibold text-slate-900">{element.title}</h4>}
      {element.description && <p className="text-sm text-slate-600">{element.description}</p>}
      <div
        className={`grid gap-4 ${
          element.layout === "two-column" ? "md:grid-cols-2" : "md:grid-cols-1"
        }`}
      >
        {element.fields.map((field) => renderField(field))}
      </div>
    </div>
  );

  const renderTable = (element: TableElement) => (
    <div className="overflow-hidden rounded-xl border border-slate-200">
      {element.title && <div className="bg-slate-50 px-4 py-2 text-sm font-semibold text-slate-700">{element.title}</div>}
      <table className="w-full text-sm">
        <thead>
          <tr className="bg-slate-100 text-left text-slate-600">
            {element.headers.map((header) => (
              <th key={header} className="px-4 py-2 font-medium">
                {header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {element.rows.map((row, idx) => (
            <tr key={`${element.title}-${idx}`} className="border-t border-slate-100">
              {row.map((cell, cellIdx) => (
                <td key={`${element.title}-${idx}-${cellIdx}`} className="px-4 py-2 text-slate-700">
                  {cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );

  const renderList = (element: ListElement) => {
    const ListTag = (element.ordered ? "ol" : "ul") as "ol" | "ul";
    const listClass = element.ordered ? "list-decimal" : "list-disc";
    return (
      <ListTag className={`${listClass} pl-5 text-sm text-slate-700 space-y-2`}>
        {element.items.map((item, idx) => (
          <li key={`list-item-${idx}`}>{item}</li>
        ))}
      </ListTag>
    );
  };

  const renderAcknowledgements = (element: AcknowledgementListElement) => (
    <div className="space-y-3">
      {element.acknowledgements.map((ack) => {
        const path = `${ACK_PATH_PREFIX}.${ack.id}`;
        const value = formValues?.[ACK_PATH_PREFIX]?.[ack.id] ?? "";
        const error = validationErrors[path];
        return (
          <div key={ack.id} className="bg-slate-50 border border-slate-200 rounded-xl p-4">
            <div className="flex items-start gap-4">
              <div className="flex flex-col items-center">
                <input
                  type="text"
                  value={value}
                  onChange={(e) => updateFormValue(path, e.target.value.toUpperCase())}
                  className="w-20 text-center uppercase border border-slate-300 rounded-lg px-3 py-2 focus:ring-primary-500 focus:border-primary-500 tracking-wide"
                  placeholder="ABC"
                  maxLength={ack.maxLength ?? 4}
                />
                <span className="text-xs text-slate-500 mt-1">Initials</span>
              </div>
              <p className="text-sm text-slate-700 flex-1">{ack.label}</p>
            </div>
            {error && <p className="text-xs text-red-600 mt-2">{error}</p>}
          </div>
        );
      })}
    </div>
  );

  const renderSection = (section: AgreementSection) => (
    <div key={section.id} className="rounded-2xl border border-slate-200 p-5 space-y-4">
      <div>
        <h3 className="text-lg font-semibold text-slate-900">{section.title}</h3>
        {section.description && <p className="text-sm text-slate-600 mt-1">{section.description}</p>}
      </div>
      <div className="space-y-4">
        {section.elements.map((element, idx) => {
          if (element.type === "field_group") {
            return <div key={`${section.id}-fields-${idx}`}>{renderFieldGroup(element as FieldGroupElement)}</div>;
          }
          if (element.type === "table") {
            return <div key={`${section.id}-table-${idx}`}>{renderTable(element as TableElement)}</div>;
          }
          if (element.type === "list") {
            return <div key={`${section.id}-list-${idx}`}>{renderList(element as ListElement)}</div>;
          }
          if (element.type === "acknowledgement_list") {
            return <div key={`${section.id}-ack-${idx}`}>{renderAcknowledgements(element as AcknowledgementListElement)}</div>;
          }
          return <div key={`${section.id}-text-${idx}`}>{renderTextElement(element)}</div>;
        })}
      </div>
    </div>
  );

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
              <p className="mt-4 text-sm text-gray-500">Document: {document.template_name}</p>
            )}
            <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
              <p className="text-sm text-blue-800">
                <strong>What's next?</strong>
              </p>
              <p className="text-sm text-blue-700 mt-1">
                You will receive a copy of the signed document via email. A school representative will contact you
                regarding next steps.
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
              <h1 className="text-2xl font-semibold text-slate-900">{document?.template_name || "Enrollment Agreement"}</h1>
              {document?.template_description && (
                <p className="text-sm text-slate-500 mt-1">{document.template_description}</p>
              )}
            </div>
            <div className="flex flex-col items-end text-sm text-slate-500">
              <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-50 text-amber-700 text-xs font-semibold">
                Awaiting signature
              </span>
              {document?.expires_at && (
                <span className="mt-2">Link expires {new Date(document.expires_at).toLocaleDateString()}</span>
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
                      idx <= activeStep ? "bg-primary-600 text-white" : "bg-slate-100 text-slate-500"
                    }`}
                  >
                    {idx + 1}
                  </div>
                  <span className={idx === activeStep ? "text-primary-700" : "text-slate-500"}>{step.title}</span>
                  {idx < steps.length - 1 && <div className="hidden md:block w-12 h-px bg-slate-200 mx-1" />}
                </div>
              ))}
            </div>
            <p className="text-xs text-slate-500">Step {activeStep + 1} of {steps.length}</p>
          </div>

          <div className="p-6 space-y-6">
            {activeStep === 0 && (
              <div className="space-y-4">
                <h2 className="text-xl font-semibold text-slate-900">Review and complete the agreement</h2>
                <p className="text-sm text-slate-600">
                  All content below is rendered from the digital enrollment agreement schema. Provide any missing
                  details, confirm tuition information, and initial each acknowledgement.
                </p>
                {formError && (
                  <p className="text-sm text-red-600 bg-red-50 border border-red-100 rounded-lg px-3 py-2">{formError}</p>
                )}
                {agreementSchema ? (
                  <div className="space-y-4">
                    {agreementSchema.sections.map((section) => renderSection(section))}
                  </div>
                ) : (
                  <p className="text-sm text-slate-600">
                    Agreement schema is unavailable. Please contact the admissions team.
                  </p>
                )}
              </div>
            )}

            {activeStep === 1 && (
              <div className="space-y-4">
                <h2 className="text-xl font-semibold text-slate-900">Sign your agreement</h2>
                <p className="text-sm text-slate-600">
                  Please type your full legal name and draw your signature. Both will appear on the final enrollment
                  agreement.
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
                  <label className="block text-sm font-medium text-slate-700 mb-2">Draw signature</label>
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
                  {signatureError && <p className="text-xs text-red-600 mt-2">{signatureError}</p>}
                </div>

                <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 text-sm text-slate-600">
                  <strong className="text-slate-800">Electronic Signature Consent:</strong> By submitting this form you
                  agree that your electronic signature is the legal equivalent of your handwritten signature on this
                  agreement.
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
                  Next
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
          This secure workflow meets ESIGN and HIPAA requirements. Need help? Email admissions@aada.edu.
        </footer>
      </div>
    </div>
  );
}
