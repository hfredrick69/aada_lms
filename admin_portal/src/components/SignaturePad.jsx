import React, { useRef, useState } from 'react';
import SignatureCanvas from 'react-signature-canvas';
import { Button, Box, Typography, Paper } from '@mui/material';

/**
 * SignaturePad Component
 *
 * Reusable signature capture component with clear and save functionality
 */
const SignaturePad = ({ onSave, label = 'Signature', disabled = false }) => {
  const sigCanvas = useRef(null);
  const [isEmpty, setIsEmpty] = useState(true);

  const handleClear = () => {
    sigCanvas.current.clear();
    setIsEmpty(true);
  };

  const handleSave = () => {
    if (sigCanvas.current.isEmpty()) {
      alert('Please provide a signature first');
      return;
    }

    // Get base64 data URL of signature
    const signatureData = sigCanvas.current.toDataURL('image/png');
    onSave(signatureData);
  };

  const handleEnd = () => {
    setIsEmpty(sigCanvas.current.isEmpty());
  };

  return (
    <Box sx={{ mb: 3 }}>
      <Typography variant="subtitle1" gutterBottom>
        {label}
      </Typography>

      <Paper
        elevation={2}
        sx={{
          border: '2px solid',
          borderColor: 'grey.300',
          borderRadius: 1,
          overflow: 'hidden',
          mb: 2,
        }}
      >
        <SignatureCanvas
          ref={sigCanvas}
          canvasProps={{
            width: 500,
            height: 200,
            className: 'signature-canvas',
            style: { width: '100%', height: '200px', background: '#fff' },
          }}
          onEnd={handleEnd}
          disabled={disabled}
        />
      </Paper>

      <Box sx={{ display: 'flex', gap: 2 }}>
        <Button
          variant="outlined"
          color="secondary"
          onClick={handleClear}
          disabled={isEmpty || disabled}
        >
          Clear
        </Button>
        <Button
          variant="contained"
          color="primary"
          onClick={handleSave}
          disabled={isEmpty || disabled}
        >
          Save Signature
        </Button>
      </Box>

      <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
        Draw your signature above using your mouse or touch screen
      </Typography>
    </Box>
  );
};

export default SignaturePad;
