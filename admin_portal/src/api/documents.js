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

export const getDocument = async (documentId) => {
  const { data } = await axiosClient.get(`/documents/${documentId}`);
  return data;
};

// Document Audit Trail
export const getDocumentAuditTrail = async (documentId) => {
  const { data } = await axiosClient.get(`/documents/${documentId}/audit-trail`);
  return data;
};
