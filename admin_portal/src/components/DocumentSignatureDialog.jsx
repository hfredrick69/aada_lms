import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  Alert,
} from '@mui/material';
import SignaturePad from './SignaturePad';
import documentsApi from '../api/documents';

/**
 * DocumentSignatureDialog Component
 *
 * Modal dialog for signing documents with signature pad and typed name
 */
const DocumentSignatureDialog = ({
  open,
  onClose,
  documentId,
  signatureType = 'school_official',
  onSignatureComplete,
}) => {
  const [typedName, setTypedName] = useState('');
  const [signatureData, setSignatureData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSignatureSave = (data) => {
    setSignatureData(data);
  };

  const handleSubmit = async () => {
    if (!signatureData) {
      setError('Please provide a signature');
      return;
    }

    if (!typedName.trim()) {
      setError('Please enter your full name');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const result = await documentsApi.signDocument(documentId, {
        signature_type: signatureType,
        signature_data: signatureData,
        typed_name: typedName.trim(),
      });

      if (onSignatureComplete) {
        onSignatureComplete(result);
      }

      onClose();
      setTypedName('');
      setSignatureData(null);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to sign document');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    if (!loading) {
      setTypedName('');
      setSignatureData(null);
      setError(null);
      onClose();
    }
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>Sign Document</DialogTitle>
      <DialogContent sx={{ p: 0 }}>
        {error && (
          <Alert severity="error" sx={{ m: 3, mb: 0 }}>
            {error}
          </Alert>
        )}

        <Box sx={{ p: 3, pt: error ? 2 : 3 }}>
          <TextField
            fullWidth
            label="Full Name"
            value={typedName}
            onChange={(e) => setTypedName(e.target.value)}
            placeholder="Enter your full legal name"
            disabled={loading}
            required
            sx={{ mb: 3 }}
          />

          <SignaturePad
            onSave={handleSignatureSave}
            label="Draw Your Signature"
            disabled={loading}
          />

          <Alert severity="info" sx={{ mt: 2 }}>
            By signing this document, you acknowledge that you have read and agree to its terms.
            Your signature is legally binding under the Electronic Signatures in Global and
            National Commerce Act (ESIGN Act).
          </Alert>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose} disabled={loading}>
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          color="primary"
          disabled={loading || !signatureData || !typedName.trim()}
        >
          {loading ? 'Signing...' : 'Submit Signature'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default DocumentSignatureDialog;
