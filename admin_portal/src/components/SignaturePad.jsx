import React, { useRef, useState, useEffect } from 'react';
import SignatureCanvas from 'react-signature-canvas';
import { Button, Box, Typography, Paper } from '@mui/material';

const trimCanvasWhitespace = (canvas) => {
  if (!canvas) {
    return null;
  }
  const ctx = canvas.getContext('2d');
  const { width, height } = canvas;
  const imageData = ctx.getImageData(0, 0, width, height).data;

  let top = height;
  let bottom = 0;
  let left = width;
  let right = 0;
  let hasStroke = false;

  for (let y = 0; y < height; y += 1) {
    for (let x = 0; x < width; x += 1) {
      const alpha = imageData[(y * width + x) * 4 + 3];
      if (alpha !== 0) {
        hasStroke = true;
        if (x < left) left = x;
        if (x > right) right = x;
        if (y < top) top = y;
        if (y > bottom) bottom = y;
      }
    }
  }

  if (!hasStroke) {
    return null;
  }

  const trimmed = document.createElement('canvas');
  const trimmedWidth = right - left + 1;
  const trimmedHeight = bottom - top + 1;
  trimmed.width = trimmedWidth;
  trimmed.height = trimmedHeight;
  const trimmedCtx = trimmed.getContext('2d');
  trimmedCtx.putImageData(ctx.getImageData(left, top, trimmedWidth, trimmedHeight), 0, 0);
  return trimmed;
};

/**
 * SignaturePad Component
 *
 * Reusable signature capture component with clear and save functionality
 */
const SignaturePad = ({ onSave = () => {}, label = 'Signature', disabled = false }) => {
  const sigCanvas = useRef(null);
  const containerRef = useRef(null);
  const [isEmpty, setIsEmpty] = useState(true);
  const [canvasWidth, setCanvasWidth] = useState(700);

  useEffect(() => {
    const updateWidth = () => {
      if (containerRef.current) {
        setCanvasWidth(containerRef.current.offsetWidth || 700);
      }
    };
    updateWidth();
    window.addEventListener('resize', updateWidth);
    return () => window.removeEventListener('resize', updateWidth);
  }, []);

  const emitSignature = () => {
    if (!sigCanvas.current || sigCanvas.current.isEmpty()) {
      return null;
    }
    const baseCanvas = sigCanvas.current.getCanvas
      ? sigCanvas.current.getCanvas()
      : sigCanvas.current._canvas;
    const trimmed = trimCanvasWhitespace(baseCanvas) || baseCanvas;
    const signatureData = trimmed.toDataURL('image/png');
    onSave(signatureData);
    return signatureData;
  };

  const handleClear = () => {
    if (sigCanvas.current) {
      sigCanvas.current.clear();
    }
    setIsEmpty(true);
    onSave(null);
  };

  const handleEnd = () => {
    if (!sigCanvas.current) {
      return;
    }
    const empty = sigCanvas.current.isEmpty();
    setIsEmpty(empty);
    if (!empty) {
      emitSignature();
    }
  };

  return (
    <Box sx={{ mb: 3 }}>
      <Typography variant="subtitle1" gutterBottom>
        {label}
      </Typography>

      <Box ref={containerRef}>
        <Paper
          elevation={0}
          sx={{
            border: '2px dashed',
            borderColor: 'primary.light',
            borderRadius: 2,
            overflow: 'hidden',
            backgroundColor: '#fff',
          }}
        >
          <SignatureCanvas
            ref={sigCanvas}
            penColor="#101828"
            canvasProps={{
              width: canvasWidth,
              height: 220,
              style: {
                width: '100%',
                height: '220px',
                background: '#fff',
              },
            }}
            backgroundColor="#fff"
            onEnd={handleEnd}
            disabled={disabled}
          />
        </Paper>
      </Box>

      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
        <Typography variant="caption" color="text.secondary">
          Use your mouse, stylus, or touch input to sign.
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button variant="text" color="secondary" onClick={handleClear} disabled={isEmpty || disabled}>
            Clear
          </Button>
        </Box>
      </Box>
    </Box>
  );
};

export default SignaturePad;
