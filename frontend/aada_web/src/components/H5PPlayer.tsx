import { useEffect, useRef, useState } from 'react';
import { Box, Alert, CircularProgress, Typography } from '@mui/material';
import { axiosInstance } from '@/api/http-client';

export interface H5PPlayerProps {
  /** H5P activity ID (e.g., 'M1_H5P_EthicsBranching') */
  activityId: string;
  /** Optional title to display above the player */
  title?: string;
  /** Optional height for the iframe */
  height?: string | number;
  /** Callback when H5P activity is completed */
  onComplete?: (result: unknown) => void;
}

/**
 * H5P Player Component
 *
 * Embeds H5P interactive content via iframe.
 * The backend serves H5P activities at /api/h5p/{activityId}
 *
 * @example
 * <H5PPlayer
 *   activityId="M1_H5P_EthicsBranching"
 *   title="Ethics Branching Scenario"
 *   height={600}
 * />
 */
export const H5PPlayer = ({
  activityId,
  title,
  height = 600,
  onComplete
}: H5PPlayerProps) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const iframeRef = useRef<HTMLIFrameElement>(null);

  // TEMPORARY: Hardcode URL to test - environment variable not being read
  const apiBaseUrl = 'http://localhost:8000';
  const h5pUrl = `${apiBaseUrl}/api/h5p/${activityId}`;

  // Debug logging
  console.log('[H5PPlayer] API Base URL:', apiBaseUrl);
  console.log('[H5PPlayer] H5P URL:', h5pUrl);
  console.log('[H5PPlayer] Env check:', import.meta.env.VITE_API_BASE_URL);

  useEffect(() => {
    // Listen for xAPI statements from H5P and post them to backend
    const handleMessage = async (event: MessageEvent) => {
      // H5P may post xAPI statements - capture and send to backend
      if (event.data?.statement) {
        console.log('[H5P xAPI Statement]', event.data.statement);

        try {
          // Post xAPI statement to backend for tracking
          await axiosInstance({
            url: '/api/xapi/statements',
            method: 'POST',
            data: {
              actor: event.data.statement.actor,
              verb: event.data.statement.verb,
              object: event.data.statement.object,
              result: event.data.statement.result,
              context: event.data.statement.context,
              timestamp: event.data.statement.timestamp || new Date().toISOString()
            }
          });
          console.log('[H5P] xAPI statement posted to backend');
        } catch (err) {
          console.error('[H5P] Failed to post xAPI statement:', err);
        }

        // Check if this is a completion statement
        if (event.data.statement?.verb?.id?.includes('completed')) {
          onComplete?.(event.data.statement);
        }
      }
    };

    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, [onComplete]);

  const handleIframeLoad = () => {
    setLoading(false);
    setError(null);
  };

  const handleIframeError = () => {
    setLoading(false);
    setError('Failed to load H5P activity. Please try again or contact support.');
  };

  return (
    <Box sx={{ width: '100%', my: 2 }}>
      {title && (
        <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
          {title}
        </Typography>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {loading && (
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            minHeight: typeof height === 'number' ? height : 400,
            bgcolor: 'grey.100',
            borderRadius: 1
          }}
        >
          <Box sx={{ textAlign: 'center' }}>
            <CircularProgress size={40} />
            <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
              Loading interactive content...
            </Typography>
          </Box>
        </Box>
      )}

      <Box
        sx={{
          width: '100%',
          height: typeof height === 'number' ? `${height}px` : height,
          border: '1px solid',
          borderColor: 'divider',
          borderRadius: 1,
          overflow: 'hidden',
          display: loading ? 'none' : 'block',
        }}
      >
        <iframe
          ref={iframeRef}
          src={h5pUrl}
          title={title || `H5P Activity: ${activityId}`}
          style={{
            width: '100%',
            height: '100%',
            border: 'none',
          }}
          allowFullScreen
          onLoad={() => {
            console.log('[H5PPlayer] iframe loaded, src:', iframeRef.current?.src);
            handleIframeLoad();
          }}
          onError={handleIframeError}
        />
        {/* Debug: Show the URL being used */}
        {import.meta.env.DEV && (
          <Typography variant="caption" sx={{ display: 'block', mt: 1, color: 'text.secondary' }}>
            Debug: {h5pUrl}
          </Typography>
        )}
      </Box>
    </Box>
  );
};

export default H5PPlayer;
