import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
  Box,
  Chip,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  Visibility as ViewIcon,
  Send as SendIcon,
  Edit as SignIcon,
  Cancel as VoidIcon,
} from '@mui/icons-material';
import { getDocumentAuditTrail } from '../api/documents';

const AuditTrailDialog = ({ open, onClose, documentId, documentName }) => {
  const [auditLogs, setAuditLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (open && documentId) {
      loadAuditTrail();
    }
  }, [open, documentId]);

  const loadAuditTrail = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getDocumentAuditTrail(documentId);
      setAuditLogs(data.audit_logs || []);
    } catch (err) {
      setError('Failed to load audit trail');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getEventIcon = (eventType) => {
    const icons = {
      viewed: <ViewIcon fontSize="small" />,
      sent: <SendIcon fontSize="small" />,
      signed: <SignIcon fontSize="small" />,
      document_signed: <SignIcon fontSize="small" />,
      voided: <VoidIcon fontSize="small" />,
    };
    return icons[eventType] || null;
  };

  const getEventColor = (eventType) => {
    const colors = {
      viewed: 'info',
      sent: 'primary',
      signed: 'success',
      document_signed: 'success',
      voided: 'error',
    };
    return colors[eventType] || 'default';
  };

  const formatEventType = (eventType) => {
    return eventType
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      timeZoneName: 'short',
    });
  };

  const parseEventDetails = (details) => {
    try {
      return details ? JSON.parse(details) : null;
    } catch {
      return null;
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        Audit Trail
        {documentName && (
          <Typography variant="subtitle2" color="text.secondary">
            Document: {documentName}
          </Typography>
        )}
      </DialogTitle>
      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <CircularProgress />
          </Box>
        ) : (
          <TableContainer component={Paper} variant="outlined">
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Event</TableCell>
                  <TableCell>Timestamp</TableCell>
                  <TableCell>IP Address</TableCell>
                  <TableCell>User Agent</TableCell>
                  <TableCell>Details</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {auditLogs.map((log, index) => {
                  const details = parseEventDetails(log.event_details);
                  return (
                    <TableRow key={log.id || index}>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          {getEventIcon(log.event_type)}
                          <Chip
                            label={formatEventType(log.event_type)}
                            color={getEventColor(log.event_type)}
                            size="small"
                          />
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" sx={{ whiteSpace: 'nowrap' }}>
                          {formatDate(log.occurred_at)}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" fontFamily="monospace">
                          {log.ip_address || 'N/A'}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" sx={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                          {log.user_agent || 'N/A'}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        {details ? (
                          <Box>
                            {Object.entries(details).map(([key, value]) => (
                              <Typography key={key} variant="caption" display="block">
                                <strong>{key}:</strong> {String(value)}
                              </Typography>
                            ))}
                          </Box>
                        ) : (
                          <Typography variant="body2" color="text.secondary">
                            -
                          </Typography>
                        )}
                      </TableCell>
                    </TableRow>
                  );
                })}
                {auditLogs.length === 0 && !loading && (
                  <TableRow>
                    <TableCell colSpan={5} align="center">
                      <Typography variant="body2" color="text.secondary" sx={{ py: 2 }}>
                        No audit log entries found
                      </Typography>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        )}

        <Box sx={{ mt: 2, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
          <Typography variant="caption" color="text.secondary">
            This audit trail provides a complete record of all actions taken on this document
            in compliance with the ESIGN Act. All timestamps are recorded in UTC and converted to local time for display.
          </Typography>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
};

export default AuditTrailDialog;
