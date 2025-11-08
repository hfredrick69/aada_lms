import axiosClient from "./axiosClient.js";

// ============ MODULE CONTENT ============

export const listModulesWithContent = async () => {
  const { data } = await axiosClient.get("/content/modules");
  return data;
};

// ============ MARKDOWN ============

export const uploadModuleMarkdown = async (moduleId, file) => {
  const formData = new FormData();
  formData.append("file", file);

  const { data } = await axiosClient.post(
    `/content/modules/${moduleId}/markdown`,
    formData,
    {
      headers: { "Content-Type": "multipart/form-data" }
    }
  );
  return data;
};

// ============ H5P ACTIVITIES ============

export const listH5PActivities = async (moduleId) => {
  const { data } = await axiosClient.get(`/content/modules/${moduleId}/h5p`);
  return data;
};

export const uploadH5PActivity = async (moduleId, file, activityId) => {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("activity_id", activityId);

  const { data } = await axiosClient.post(
    `/content/modules/${moduleId}/h5p`,
    formData,
    {
      headers: { "Content-Type": "multipart/form-data" }
    }
  );
  return data;
};

export const deleteH5PActivity = async (moduleId, activityId) => {
  const { data } = await axiosClient.delete(`/content/modules/${moduleId}/h5p/${activityId}`);
  return data;
};

// ============ SUPPLEMENTAL FILES ============

export const listSupplementalFiles = async (moduleId, subfolder = null) => {
  const params = subfolder ? { subfolder } : {};
  const { data } = await axiosClient.get(`/content/modules/${moduleId}/files`, { params });
  return data;
};

export const uploadSupplementalFile = async (moduleId, file, subfolder = null) => {
  const formData = new FormData();
  formData.append("file", file);
  if (subfolder) {
    formData.append("subfolder", subfolder);
  }

  const { data } = await axiosClient.post(
    `/content/modules/${moduleId}/files`,
    formData,
    {
      headers: { "Content-Type": "multipart/form-data" }
    }
  );
  return data;
};

export const deleteSupplementalFile = async (moduleId, filePath) => {
  const { data } = await axiosClient.delete(`/content/modules/${moduleId}/files/${filePath}`);
  return data;
};
