import axiosClient from "./axiosClient.js";

// Document Templates
export const listDocumentTemplates = async (activeOnly = true) => {
  const { data } = await axiosClient.get("/documents/templates", {
    params: { active_only: activeOnly }
  });
  return data;
};

export const getDocumentTemplate = async (id) => {
  const { data } = await axiosClient.get(`/documents/templates/${id}`);
  return data;
};

export const createDocumentTemplate = async (formData) => {
  const { data } = await axiosClient.post("/documents/templates", formData, {
    headers: { "Content-Type": "multipart/form-data" }
  });
  return data;
};

export const toggleTemplateActive = async (templateId) => {
  const { data } = await axiosClient.patch(`/documents/templates/${templateId}/toggle-active`);
  return data;
};

export const deleteDocumentTemplate = async (templateId) => {
  const { data } = await axiosClient.delete(`/documents/templates/${templateId}`);
  return data;
};

// Send Document
export const sendDocumentToUser = async (templateId, userId) => {
  const { data } = await axiosClient.post("/documents/send", {
    template_id: templateId,
    user_id: userId
  });
  return data;
};

export const sendDocumentToLead = async (templateId, leadId) => {
  const { data } = await axiosClient.post("/documents/send", {
    template_id: templateId,
    lead_id: leadId
  });
  return data;
};

// Get Documents
export const getUserDocuments = async (userId) => {
  const { data } = await axiosClient.get(`/documents/user/${userId}`);
  return data;
};

export const getLeadDocuments = async (leadId) => {
  const { data } = await axiosClient.get(`/documents/lead/${leadId}`);
  return data;
};

export const getAllDocuments = async (params = {}) => {
  const { data } = await axiosClient.get('/documents', { params });
  return data;
};

export const getDocument = async (documentId) => {
  const { data } = await axiosClient.get(`/documents/${documentId}`);
  return data;
};

// Document Audit Trail
export const getDocumentAuditTrail = async (documentId) => {
  const { data } = await axiosClient.get(`/documents/${documentId}/audit-trail`);
  return data;
};

export const sendEnrollmentAgreement = async (payload) => {
  const { data } = await axiosClient.post('/documents/enrollment/send', payload);
  return data;
};

export const counterSignDocument = async (documentId, payload) => {
  const { data } = await axiosClient.post(`/documents/${documentId}/counter-sign`, payload);
  return data;
};

// Download Document
export const downloadDocument = async (documentId, filename) => {
  const response = await axiosClient.get(`/documents/${documentId}/download`, {
    responseType: 'blob'
  });

  // Create a blob URL and trigger download
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', filename || 'document.pdf');
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
};

// Default export
export default {
  listTemplates: listDocumentTemplates,
  getTemplate: getDocumentTemplate,
  createTemplate: createDocumentTemplate,
  sendDocument: sendDocumentToUser,
  sendDocumentToLead,
  getUserDocuments,
  getLeadDocuments,
  getAllDocuments,
  sendEnrollmentAgreement,
  counterSignDocument,
  getDocument,
  getDocumentAuditTrail,
  downloadDocument,
};
