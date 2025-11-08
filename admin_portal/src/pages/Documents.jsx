import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tabs,
  Tab,
  Chip,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControlLabel,
  Checkbox,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  IconButton,
} from '@mui/material';
import {
  Upload as UploadIcon,
  Send as SendIcon,
  Download as DownloadIcon,
  Edit as EditIcon,
  Visibility as VisibilityIcon,
  History as HistoryIcon,
} from '@mui/icons-material';
import documentsApi from '../api/documents';
import usersApi from '../api/users';
import DocumentSignatureDialog from '../components/DocumentSignatureDialog';
import AuditTrailDialog from '../components/AuditTrailDialog';

const Documents = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [templates, setTemplates] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  // Upload template dialog state
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [uploadForm, setUploadForm] = useState({
    name: '',
    version: '',
    description: '',
    requires_counter_signature: true,
    file: null,
  });

  // Send document dialog state
  const [sendDialogOpen, setSendDialogOpen] = useState(false);
  const [sendForm, setSendForm] = useState({
    template_id: '',
    user_id: '',
  });

  // Signature dialog state
  const [signatureDialogOpen, setSignatureDialogOpen] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState(null);

  // Audit trail dialog state
  const [auditTrailDialogOpen, setAuditTrailDialogOpen] = useState(false);
  const [auditDocument, setAuditDocument] = useState(null);

  useEffect(() => {
    loadTemplates();
    loadUsers();
  }, []);

  const loadTemplates = async () => {
    try {
      const data = await documentsApi.listTemplates();
      setTemplates(data);
    } catch (err) {
      setError('Failed to load templates');
    }
  };

  const loadUsers = async () => {
    try {
      const data = await usersApi.getAllUsers();
      setUsers(data);
    } catch (err) {
      setError('Failed to load users');
    }
  };

  const loadDocumentsByUser = async (userId) => {
    try {
      const data = await documentsApi.getUserDocuments(userId);
      setDocuments(data.documents);
    } catch (err) {
      setError('Failed to load documents');
    }
  };

  const handleUploadTemplate = async () => {
    if (!uploadForm.name || !uploadForm.version || !uploadForm.file) {
      setError('Please fill in all required fields');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', uploadForm.file);
      formData.append('name', uploadForm.name);
      formData.append('version', uploadForm.version);
      formData.append('description', uploadForm.description);
      formData.append('requires_counter_signature', uploadForm.requires_counter_signature);

      await documentsApi.createTemplate(formData);
      setSuccess('Template uploaded successfully');
      setUploadDialogOpen(false);
      setUploadForm({
        name: '',
        version: '',
        description: '',
        requires_counter_signature: true,
        file: null,
      });
      await loadTemplates();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to upload template');
    } finally {
      setLoading(false);
    }
  };

  const handleSendDocument = async () => {
    if (!sendForm.template_id || !sendForm.user_id) {
      setError('Please select a template and user');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await documentsApi.sendDocument(sendForm.template_id, sendForm.user_id);
      setSuccess('Document sent successfully');
      setSendDialogOpen(false);
      setSendForm({ template_id: '', user_id: '' });
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to send document');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadDocument = async (documentId, filename) => {
    try {
      await documentsApi.downloadDocument(documentId, filename);
    } catch (err) {
      setError('Failed to download document');
    }
  };

  const handleOpenSignatureDialog = (document) => {
    setSelectedDocument(document);
    setSignatureDialogOpen(true);
  };

  const handleSignatureComplete = async () => {
    setSuccess('Document signed successfully');
    if (sendForm.user_id) {
      await loadDocumentsByUser(sendForm.user_id);
    }
  };

  const getStatusChip = (status) => {
    const statusConfig = {
      pending: { label: 'Pending', color: 'warning' },
      student_signed: { label: 'Student Signed', color: 'info' },
      completed: { label: 'Completed', color: 'success' },
    };

    const config = statusConfig[status] || { label: status, color: 'default' };
    return <Chip label={config.label} color={config.color} size="small" />;
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Document Management
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}

      <Box sx={{ mb: 3, display: 'flex', gap: 2 }}>
        <Button
          variant="contained"
          startIcon={<UploadIcon />}
          onClick={() => setUploadDialogOpen(true)}
        >
          Upload Template
        </Button>
        <Button
          variant="contained"
          color="secondary"
          startIcon={<SendIcon />}
          onClick={() => setSendDialogOpen(true)}
        >
          Send Document
        </Button>
      </Box>

      <Paper sx={{ mb: 3 }}>
        <Tabs value={activeTab} onChange={(e, v) => setActiveTab(v)}>
          <Tab label="Templates" />
          <Tab label="Documents" />
        </Tabs>

        {activeTab === 0 && (
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Version</TableCell>
                  <TableCell>Description</TableCell>
                  <TableCell>Counter-Signature</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Created</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {templates.map((template) => (
                  <TableRow key={template.id}>
                    <TableCell>{template.name}</TableCell>
                    <TableCell>{template.version}</TableCell>
                    <TableCell>{template.description || '-'}</TableCell>
                    <TableCell>{template.requires_counter_signature ? 'Yes' : 'No'}</TableCell>
                    <TableCell>
                      {template.is_active ? (
                        <Chip label="Active" color="success" size="small" />
                      ) : (
                        <Chip label="Inactive" color="default" size="small" />
                      )}
                    </TableCell>
                    <TableCell>
                      {new Date(template.created_at).toLocaleDateString()}
                    </TableCell>
                  </TableRow>
                ))}
                {templates.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={6} align="center">
                      No templates found. Upload a template to get started.
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        )}

        {activeTab === 1 && (
          <Box sx={{ p: 3 }}>
            <FormControl fullWidth sx={{ mb: 3 }}>
              <InputLabel>Select User</InputLabel>
              <Select
                value={sendForm.user_id}
                onChange={(e) => {
                  setSendForm({ ...sendForm, user_id: e.target.value });
                  loadDocumentsByUser(e.target.value);
                }}
                label="Select User"
              >
                {users.map((user) => (
                  <MenuItem key={user.id} value={user.id}>
                    {user.first_name} {user.last_name} ({user.email})
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            {documents.length > 0 ? (
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Template</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Sent</TableCell>
                      <TableCell>Student Signed</TableCell>
                      <TableCell>Counter-Signed</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {documents.map((doc) => (
                      <TableRow key={doc.id}>
                        <TableCell>{doc.template_name}</TableCell>
                        <TableCell>{getStatusChip(doc.status)}</TableCell>
                        <TableCell>
                          {doc.sent_at ? new Date(doc.sent_at).toLocaleDateString() : '-'}
                        </TableCell>
                        <TableCell>
                          {doc.student_signed_at
                            ? new Date(doc.student_signed_at).toLocaleDateString()
                            : '-'}
                        </TableCell>
                        <TableCell>
                          {doc.counter_signed_at
                            ? new Date(doc.counter_signed_at).toLocaleDateString()
                            : '-'}
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', gap: 1 }}>
                            <IconButton
                              size="small"
                              color="primary"
                              onClick={() => handleDownloadDocument(doc.id, `${doc.template_name}.pdf`)}
                              title="Download"
                            >
                              <DownloadIcon />
                            </IconButton>
                            <IconButton
                              size="small"
                              color="info"
                              onClick={() => {
                                setAuditDocument({ id: doc.id, name: doc.template_name });
                                setAuditTrailDialogOpen(true);
                              }}
                              title="View Audit Trail"
                            >
                              <HistoryIcon />
                            </IconButton>
                            {doc.status === 'student_signed' && doc.requires_counter_signature && (
                              <IconButton
                                size="small"
                                color="secondary"
                                onClick={() => handleOpenSignatureDialog(doc)}
                                title="Counter-Sign"
                              >
                                <EditIcon />
                              </IconButton>
                            )}
                          </Box>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            ) : (
              <Typography variant="body2" color="text.secondary">
                {sendForm.user_id
                  ? 'No documents found for this user.'
                  : 'Select a user to view their documents.'}
              </Typography>
            )}
          </Box>
        )}
      </Paper>

      {/* Upload Template Dialog */}
      <Dialog open={uploadDialogOpen} onClose={() => setUploadDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Upload Document Template</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Template Name"
            value={uploadForm.name}
            onChange={(e) => setUploadForm({ ...uploadForm, name: e.target.value })}
            margin="normal"
            required
          />
          <TextField
            fullWidth
            label="Version"
            value={uploadForm.version}
            onChange={(e) => setUploadForm({ ...uploadForm, version: e.target.value })}
            margin="normal"
            required
          />
          <TextField
            fullWidth
            label="Description"
            value={uploadForm.description}
            onChange={(e) => setUploadForm({ ...uploadForm, description: e.target.value })}
            margin="normal"
            multiline
            rows={3}
          />
          <FormControlLabel
            control={
              <Checkbox
                checked={uploadForm.requires_counter_signature}
                onChange={(e) =>
                  setUploadForm({ ...uploadForm, requires_counter_signature: e.target.checked })
                }
              />
            }
            label="Requires school official counter-signature"
          />
          <Button variant="outlined" component="label" fullWidth sx={{ mt: 2 }}>
            Choose PDF File
            <input
              type="file"
              accept=".pdf"
              hidden
              onChange={(e) => setUploadForm({ ...uploadForm, file: e.target.files[0] })}
            />
          </Button>
          {uploadForm.file && (
            <Typography variant="body2" sx={{ mt: 1 }}>
              Selected: {uploadForm.file.name}
            </Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setUploadDialogOpen(false)} disabled={loading}>
            Cancel
          </Button>
          <Button onClick={handleUploadTemplate} variant="contained" disabled={loading}>
            Upload
          </Button>
        </DialogActions>
      </Dialog>

      {/* Send Document Dialog */}
      <Dialog open={sendDialogOpen} onClose={() => setSendDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Send Document to Student</DialogTitle>
        <DialogContent>
          <FormControl fullWidth margin="normal">
            <InputLabel>Template</InputLabel>
            <Select
              value={sendForm.template_id}
              onChange={(e) => setSendForm({ ...sendForm, template_id: e.target.value })}
              label="Template"
            >
              {templates.map((template) => (
                <MenuItem key={template.id} value={template.id}>
                  {template.name} ({template.version})
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <FormControl fullWidth margin="normal">
            <InputLabel>Student</InputLabel>
            <Select
              value={sendForm.user_id}
              onChange={(e) => setSendForm({ ...sendForm, user_id: e.target.value })}
              label="Student"
            >
              {users.map((user) => (
                <MenuItem key={user.id} value={user.id}>
                  {user.first_name} {user.last_name} ({user.email})
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSendDialogOpen(false)} disabled={loading}>
            Cancel
          </Button>
          <Button onClick={handleSendDocument} variant="contained" disabled={loading}>
            Send
          </Button>
        </DialogActions>
      </Dialog>

      {/* Signature Dialog */}
      {selectedDocument && (
        <DocumentSignatureDialog
          open={signatureDialogOpen}
          onClose={() => setSignatureDialogOpen(false)}
          documentId={selectedDocument.id}
          signatureType="school_official"
          onSignatureComplete={handleSignatureComplete}
        />
      )}

      {/* Audit Trail Dialog */}
      {auditDocument && (
        <AuditTrailDialog
          open={auditTrailDialogOpen}
          onClose={() => setAuditTrailDialogOpen(false)}
          documentId={auditDocument.id}
          documentName={auditDocument.name}
        />
      )}
    </Box>
  );
};

export default Documents;
