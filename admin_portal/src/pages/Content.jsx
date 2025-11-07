import { useEffect, useState, useRef } from "react";
import { useAuth } from "../context/AuthContext.jsx";
import {
  listModulesWithContent,
  uploadModuleMarkdown,
  downloadModuleMarkdown,
  listH5PActivities,
  uploadH5PActivity,
  deleteH5PActivity,
  listSupplementalFiles,
  uploadSupplementalFile,
  deleteSupplementalFile,
} from "../api/content.js";

const Content = () => {
  const { hasRole } = useAuth();
  const [modules, setModules] = useState([]);
  const [selectedModule, setSelectedModule] = useState(null);
  const [activeTab, setActiveTab] = useState("markdown");
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [loading, setLoading] = useState(false);

  // State for different content types
  const [h5pActivities, setH5pActivities] = useState([]);
  const [supplementalFiles, setSupplementalFiles] = useState([]);
  const [uploadProgress, setUploadProgress] = useState(null);

  // File input refs
  const markdownInputRef = useRef(null);
  const h5pInputRef = useRef(null);
  const fileInputRef = useRef(null);

  // Form states
  const [h5pActivityId, setH5pActivityId] = useState("");
  const [fileSubfolder, setFileSubfolder] = useState("");

  const canEdit = hasRole(["admin"]);

  useEffect(() => {
    fetchModules();
  }, []);

  useEffect(() => {
    if (selectedModule && activeTab === "h5p") {
      fetchH5PActivities();
    } else if (selectedModule && activeTab === "files") {
      fetchSupplementalFiles();
    }
  }, [selectedModule, activeTab]);

  const fetchModules = async () => {
    setLoading(true);
    try {
      const data = await listModulesWithContent();
      setModules(data.modules || []);
      if (data.modules && data.modules.length > 0) {
        setSelectedModule(data.modules[0]);
      }
      setError(null);
    } catch (err) {
      console.error(err);
      setError("Unable to load modules");
      setModules([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchH5PActivities = async () => {
    if (!selectedModule) return;
    try {
      const data = await listH5PActivities(selectedModule.id);
      setH5pActivities(data.activities || []);
    } catch (err) {
      console.error(err);
      setError("Unable to load H5P activities");
    }
  };

  const fetchSupplementalFiles = async () => {
    if (!selectedModule) return;
    try {
      const data = await listSupplementalFiles(selectedModule.id);
      setSupplementalFiles(data.files || []);
    } catch (err) {
      console.error(err);
      setError("Unable to load supplemental files");
    }
  };

  // ============ MARKDOWN HANDLERS ============

  const handleMarkdownUpload = async (event) => {
    event.preventDefault();
    if (!canEdit || !selectedModule) return;

    const file = markdownInputRef.current?.files?.[0];
    if (!file) {
      setError("Please select a markdown file");
      return;
    }

    setUploadProgress("Uploading markdown...");
    try {
      await uploadModuleMarkdown(selectedModule.id, file);
      setSuccess("Markdown file uploaded successfully");
      setError(null);
      // Refresh modules list to update has_markdown flag
      fetchModules();
      markdownInputRef.current.value = "";
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || "Failed to upload markdown");
    } finally {
      setUploadProgress(null);
    }
  };

  const handleMarkdownDownload = async () => {
    if (!selectedModule) return;

    try {
      const blob = await downloadModuleMarkdown(selectedModule.id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${selectedModule.code}_module.md`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      setSuccess("Markdown downloaded successfully");
    } catch (err) {
      console.error(err);
      if (err.response?.status === 404) {
        setError("No markdown file found for this module");
      } else {
        setError("Failed to download markdown");
      }
    }
  };

  // ============ H5P HANDLERS ============

  const handleH5PUpload = async (event) => {
    event.preventDefault();
    if (!canEdit || !selectedModule) return;

    const file = h5pInputRef.current?.files?.[0];
    if (!file) {
      setError("Please select an H5P file");
      return;
    }

    if (!h5pActivityId.trim()) {
      setError("Please provide an activity ID");
      return;
    }

    setUploadProgress("Uploading H5P activity...");
    try {
      await uploadH5PActivity(selectedModule.id, file, h5pActivityId);
      setSuccess(`H5P activity "${h5pActivityId}" uploaded successfully`);
      setError(null);
      setH5pActivityId("");
      h5pInputRef.current.value = "";
      fetchH5PActivities();
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || "Failed to upload H5P activity");
    } finally {
      setUploadProgress(null);
    }
  };

  const handleH5PDelete = async (activityId) => {
    if (!canEdit || !selectedModule) return;
    if (!confirm(`Are you sure you want to delete "${activityId}"?`)) return;

    try {
      await deleteH5PActivity(selectedModule.id, activityId);
      setSuccess(`H5P activity "${activityId}" deleted successfully`);
      setError(null);
      fetchH5PActivities();
    } catch (err) {
      console.error(err);
      setError("Failed to delete H5P activity");
    }
  };

  // ============ SUPPLEMENTAL FILE HANDLERS ============

  const handleFileUpload = async (event) => {
    event.preventDefault();
    if (!canEdit || !selectedModule) return;

    const file = fileInputRef.current?.files?.[0];
    if (!file) {
      setError("Please select a file");
      return;
    }

    setUploadProgress("Uploading file...");
    try {
      await uploadSupplementalFile(selectedModule.id, file, fileSubfolder || null);
      setSuccess(`File "${file.name}" uploaded successfully`);
      setError(null);
      setFileSubfolder("");
      fileInputRef.current.value = "";
      fetchSupplementalFiles();
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || "Failed to upload file");
    } finally {
      setUploadProgress(null);
    }
  };

  const handleFileDelete = async (filePath) => {
    if (!canEdit || !selectedModule) return;
    if (!confirm(`Are you sure you want to delete "${filePath}"?`)) return;

    try {
      await deleteSupplementalFile(selectedModule.id, filePath);
      setSuccess(`File "${filePath}" deleted successfully`);
      setError(null);
      fetchSupplementalFiles();
    } catch (err) {
      console.error(err);
      setError("Failed to delete file");
    }
  };

  // ============ UTILITY FUNCTIONS ============

  const formatFileSize = (bytes) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + " " + sizes[i];
  };

  const formatDate = (timestamp) => {
    return new Date(timestamp * 1000).toLocaleString();
  };

  // ============ RENDER ============

  if (loading) {
    return (
      <div className="p-6">
        <div className="text-center py-12">
          <div className="text-lg text-slate-600">Loading modules...</div>
        </div>
      </div>
    );
  }

  const isInstructor = hasRole(["instructor"]) && !hasRole(["admin"]);

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-800">
          {isInstructor ? "Content Library" : "Content Management"}
        </h1>
        <p className="text-slate-600 mt-1">
          {isInstructor
            ? "View module content, H5P activities, and supplemental files"
            : "Manage module content, H5P activities, and supplemental files"}
        </p>
        {isInstructor && (
          <div className="mt-2 bg-blue-50 border border-blue-200 rounded-lg p-3">
            <p className="text-sm text-blue-800">
              ℹ️ You have read-only access. Contact an administrator to upload or modify content.
            </p>
          </div>
        )}
      </div>

      {/* Error/Success Messages */}
      {error && (
        <div className="mb-4 bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
        </div>
      )}
      {success && (
        <div className="mb-4 bg-green-50 border border-green-200 rounded-lg p-4">
          <p className="text-green-800">{success}</p>
        </div>
      )}
      {uploadProgress && (
        <div className="mb-4 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-blue-800">{uploadProgress}</p>
        </div>
      )}

      {/* Module Selector */}
      <div className="mb-6 bg-white rounded-lg border border-slate-200 p-4">
        <label className="block text-sm font-medium text-slate-700 mb-2">Select Module</label>
        <select
          value={selectedModule?.id || ""}
          onChange={(e) => {
            const module = modules.find((m) => m.id === e.target.value);
            setSelectedModule(module);
            setError(null);
            setSuccess(null);
          }}
          className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          {modules.map((module) => (
            <option key={module.id} value={module.id}>
              {module.code} - {module.title}
              {module.has_markdown && " 📄"}
              {module.h5p_count > 0 && ` (${module.h5p_count} H5P)`}
            </option>
          ))}
        </select>
      </div>

      {selectedModule && (
        <>
          {/* Tabs */}
          <div className="mb-6 border-b border-slate-200">
            <nav className="flex space-x-4">
              <button
                onClick={() => {
                  setActiveTab("markdown");
                  setError(null);
                  setSuccess(null);
                }}
                className={`px-4 py-2 border-b-2 font-medium text-sm ${
                  activeTab === "markdown"
                    ? "border-primary-500 text-primary-600"
                    : "border-transparent text-slate-600 hover:text-slate-800 hover:border-slate-300"
                }`}
              >
                📄 Module Markdown
              </button>
              <button
                onClick={() => {
                  setActiveTab("h5p");
                  setError(null);
                  setSuccess(null);
                }}
                className={`px-4 py-2 border-b-2 font-medium text-sm ${
                  activeTab === "h5p"
                    ? "border-primary-500 text-primary-600"
                    : "border-transparent text-slate-600 hover:text-slate-800 hover:border-slate-300"
                }`}
              >
                🎮 H5P Activities
              </button>
              <button
                onClick={() => {
                  setActiveTab("files");
                  setError(null);
                  setSuccess(null);
                }}
                className={`px-4 py-2 border-b-2 font-medium text-sm ${
                  activeTab === "files"
                    ? "border-primary-500 text-primary-600"
                    : "border-transparent text-slate-600 hover:text-slate-800 hover:border-slate-300"
                }`}
              >
                📎 Supplemental Files
              </button>
            </nav>
          </div>

          {/* Tab Content */}
          {activeTab === "markdown" && (
            <div className="bg-white rounded-lg border border-slate-200 p-6">
              <h2 className="text-lg font-semibold text-slate-800 mb-4">Module Markdown File</h2>
              <p className="text-sm text-slate-600 mb-4">
                Upload or replace the module's markdown content file (.md). Maximum size: 10 MB.
              </p>

              {canEdit && (
                <form onSubmit={handleMarkdownUpload} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                      Select Markdown File (.md)
                    </label>
                    <input
                      ref={markdownInputRef}
                      type="file"
                      accept=".md,.markdown"
                      className="block w-full text-sm text-slate-600
                        file:mr-4 file:py-2 file:px-4
                        file:rounded-md file:border-0
                        file:text-sm file:font-semibold
                        file:bg-primary-50 file:text-primary-700
                        hover:file:bg-primary-100"
                    />
                  </div>

                  <div className="flex space-x-3">
                    <button
                      type="submit"
                      disabled={!canEdit || uploadProgress}
                      className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:bg-slate-300 disabled:cursor-not-allowed"
                    >
                      Upload Markdown
                    </button>
                    {selectedModule.has_markdown && (
                      <button
                        type="button"
                        onClick={handleMarkdownDownload}
                        className="px-4 py-2 bg-slate-600 text-white rounded-md hover:bg-slate-700"
                      >
                        Download Current
                      </button>
                    )}
                  </div>
                </form>
              )}

              {!canEdit && selectedModule.has_markdown && (
                <button
                  type="button"
                  onClick={handleMarkdownDownload}
                  className="px-4 py-2 bg-slate-600 text-white rounded-md hover:bg-slate-700"
                >
                  Download Markdown
                </button>
              )}

              {selectedModule.has_markdown && (
                <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-md">
                  <p className="text-sm text-green-800">
                    ✓ This module has a markdown file uploaded
                  </p>
                </div>
              )}
            </div>
          )}

          {activeTab === "h5p" && (
            <div className="space-y-6">
              {/* Upload Form - Admin Only */}
              {canEdit && (
                <div className="bg-white rounded-lg border border-slate-200 p-6">
                  <h2 className="text-lg font-semibold text-slate-800 mb-4">Upload H5P Activity</h2>
                  <p className="text-sm text-slate-600 mb-4">
                    Upload H5P activity packages (.h5p files). Maximum size: 100 MB.
                  </p>

                  <form onSubmit={handleH5PUpload} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                      Activity ID
                    </label>
                    <input
                      type="text"
                      value={h5pActivityId}
                      onChange={(e) => setH5pActivityId(e.target.value)}
                      placeholder="e.g., M1_H5P_WelcomeCarousel"
                      className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                      Select H5P File (.h5p)
                    </label>
                    <input
                      ref={h5pInputRef}
                      type="file"
                      accept=".h5p"
                      className="block w-full text-sm text-slate-600
                        file:mr-4 file:py-2 file:px-4
                        file:rounded-md file:border-0
                        file:text-sm file:font-semibold
                        file:bg-primary-50 file:text-primary-700
                        hover:file:bg-primary-100"
                    />
                  </div>

                    <button
                      type="submit"
                      disabled={!canEdit || uploadProgress}
                      className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:bg-slate-300 disabled:cursor-not-allowed"
                    >
                      Upload H5P Activity
                    </button>
                  </form>
                </div>
              )}

              {/* H5P Activities List */}
              <div className="bg-white rounded-lg border border-slate-200 p-6">
                <h2 className="text-lg font-semibold text-slate-800 mb-4">
                  Existing H5P Activities ({h5pActivities.length})
                </h2>

                {h5pActivities.length === 0 ? (
                  <p className="text-slate-600 text-sm">No H5P activities uploaded for this module yet.</p>
                ) : (
                  <div className="space-y-2">
                    {h5pActivities.map((activity) => (
                      <div
                        key={activity.activity_id}
                        className="flex items-center justify-between p-3 bg-slate-50 rounded-md"
                      >
                        <div className="flex-1">
                          <p className="font-medium text-slate-800">{activity.activity_id}</p>
                          <p className="text-sm text-slate-600">
                            {formatFileSize(activity.file_size)} • Modified: {formatDate(activity.modified)}
                          </p>
                        </div>
                        {canEdit && (
                          <button
                            onClick={() => handleH5PDelete(activity.activity_id)}
                            className="ml-4 px-3 py-1 text-sm bg-red-600 text-white rounded hover:bg-red-700"
                          >
                            Delete
                          </button>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === "files" && (
            <div className="space-y-6">
              {/* Upload Form - Admin Only */}
              {canEdit && (
                <div className="bg-white rounded-lg border border-slate-200 p-6">
                  <h2 className="text-lg font-semibold text-slate-800 mb-4">Upload Supplemental File</h2>
                  <p className="text-sm text-slate-600 mb-4">
                    Upload supplemental files (PDFs, images, videos, etc.). Maximum size: 50 MB.
                  </p>

                  <form onSubmit={handleFileUpload} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                      Subfolder (optional)
                    </label>
                    <input
                      type="text"
                      value={fileSubfolder}
                      onChange={(e) => setFileSubfolder(e.target.value)}
                      placeholder="e.g., documents, images, videos"
                      className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                    />
                    <p className="text-xs text-slate-500 mt-1">
                      Organize files into subfolders. Leave empty for root folder.
                    </p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                      Select File
                    </label>
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept=".pdf,.png,.jpg,.jpeg,.gif,.svg,.mp4,.mp3,.zip"
                      className="block w-full text-sm text-slate-600
                        file:mr-4 file:py-2 file:px-4
                        file:rounded-md file:border-0
                        file:text-sm file:font-semibold
                        file:bg-primary-50 file:text-primary-700
                        hover:file:bg-primary-100"
                    />
                  </div>

                    <button
                      type="submit"
                      disabled={!canEdit || uploadProgress}
                      className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:bg-slate-300 disabled:cursor-not-allowed"
                    >
                      Upload File
                    </button>
                  </form>
                </div>
              )}

              {/* Files List */}
              <div className="bg-white rounded-lg border border-slate-200 p-6">
                <h2 className="text-lg font-semibold text-slate-800 mb-4">
                  Supplemental Files ({supplementalFiles.length})
                </h2>

                {supplementalFiles.length === 0 ? (
                  <p className="text-slate-600 text-sm">No supplemental files uploaded for this module yet.</p>
                ) : (
                  <div className="space-y-2">
                    {supplementalFiles.map((file) => (
                      <div
                        key={file.path}
                        className="flex items-center justify-between p-3 bg-slate-50 rounded-md"
                      >
                        <div className="flex-1">
                          <p className="font-medium text-slate-800">{file.filename}</p>
                          <p className="text-sm text-slate-600">
                            {file.path} • {file.type.toUpperCase()} • {formatFileSize(file.file_size)} •
                            Modified: {formatDate(file.modified)}
                          </p>
                        </div>
                        {canEdit && (
                          <button
                            onClick={() => handleFileDelete(file.path)}
                            className="ml-4 px-3 py-1 text-sm bg-red-600 text-white rounded hover:bg-red-700"
                          >
                            Delete
                          </button>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default Content;
