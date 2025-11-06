import axiosClient from "./axiosClient.js";

// Lead Sources
export const listLeadSources = async () => {
  const { data } = await axiosClient.get("/crm/leads/sources");
  return data;
};

export const createLeadSource = async (payload) => {
  const { data } = await axiosClient.post("/crm/leads/sources", payload);
  return data;
};

// Leads
export const listLeads = async (params = {}) => {
  const { data } = await axiosClient.get("/crm/leads", { params });
  return data;
};

export const getLead = async (id) => {
  const { data } = await axiosClient.get(`/crm/leads/${id}`);
  return data;
};

export const createLead = async (payload) => {
  const { data } = await axiosClient.post("/crm/leads", payload);
  return data;
};

export const updateLead = async (id, payload) => {
  const { data } = await axiosClient.put(`/crm/leads/${id}`, payload);
  return data;
};

export const deleteLead = async (id) => {
  await axiosClient.delete(`/crm/leads/${id}`);
};

// Activities
export const listLeadActivities = async (leadId) => {
  const { data } = await axiosClient.get(`/crm/leads/${leadId}/activities`);
  return data;
};

export const createLeadActivity = async (leadId, payload) => {
  const { data } = await axiosClient.post(`/crm/leads/${leadId}/activities`, payload);
  return data;
};
