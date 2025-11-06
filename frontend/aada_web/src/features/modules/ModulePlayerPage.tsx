import { useEffect, useState, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Paper,
  Typography,
  Button,
  Alert,
  CircularProgress,
  Breadcrumbs,
  Link,
} from '@mui/material';
import { ArrowBack, Home } from '@mui/icons-material';
import { H5PPlayer } from '@/components/H5PPlayer';
import { ModuleProgressTracker } from '@/components/ModuleProgressTracker';
import { useAuthStore } from '@/stores/auth-store';
import { axiosInstance } from '@/api/http-client';

/**
 * Module Player Page
 *
 * Displays module content (markdown rendered as HTML) and embedded H5P activities.
 * Fetches content from /api/modules/{moduleId}
 */
export const ModulePlayerPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const user = useAuthStore((state) => state.user);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [htmlContent, setHtmlContent] = useState<string>('');
  const [enrollmentId, setEnrollmentId] = useState<string | null>(null);

  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

  // Extract H5P activity IDs from HTML content
  const h5pActivities = useMemo(() => {
    if (!htmlContent) return [];

    const activities: Array<{ id: string; title: string }> = [];

    // Look for H5P activity references in the HTML
    // Pattern: data-h5p-activity="M1_H5P_EthicsBranching" or similar
    const h5pPattern = /data-h5p-activity=["']([^"']+)["']/g;
    let match;
    while ((match = h5pPattern.exec(htmlContent)) !== null) {
      activities.push({
        id: match[1],
        title: match[1].replace(/^M\d+_H5P_/, '').replace(/_/g, ' '),
      });
    }

    // Also look for common Module 1 activities if none found
    if (activities.length === 0 && id === '1') {
      activities.push(
        { id: 'M1_H5P_EthicsBranching', title: 'Ethics Branching Scenario' },
        { id: 'M1_H5P_HIPAAHotspot', title: 'HIPAA Hotspot' }
      );
    }

    return activities;
  }, [htmlContent, id]);

  // Fetch user's active enrollment
  useEffect(() => {
    const fetchEnrollment = async () => {
      if (!user?.id) return;

      try {
        const response = await axiosInstance<{ id: string; user_id: string; program_id: string; status: string }[]>({
          method: 'GET',
          url: '/api/enrollments/',
          params: {
            user_id: user.id,
            status: 'active',
          },
        });

        if (response.data && response.data.length > 0) {
          setEnrollmentId(response.data[0].id);
        }
      } catch (err) {
        console.error('Failed to fetch enrollment:', err);
      }
    };

    fetchEnrollment();
  }, [user?.id]);

  useEffect(() => {
    const fetchModuleContent = async () => {
      if (!id) {
        setError('No module ID provided');
        setLoading(false);
        return;
      }

      setLoading(true);
      setError(null);

      try {
        const response = await fetch(`${apiBaseUrl}/api/modules/${id}`);

        if (!response.ok) {
          throw new Error(`Failed to load module: ${response.statusText}`);
        }

        const html = await response.text();
        setHtmlContent(html);
      } catch (err) {
        console.error('Error fetching module content:', err);
        setError(
          err instanceof Error
            ? err.message
            : 'Failed to load module content. Please try again.'
        );
      } finally {
        setLoading(false);
      }
    };

    fetchModuleContent();
  }, [id, apiBaseUrl]);

  const handleH5PComplete = (activityId: string, result: unknown) => {
    console.log(`[Module ${id}] H5P Activity ${activityId} completed:`, result);
    // TODO: Send xAPI statement to backend
    // TODO: Update module progress
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            minHeight: '50vh',
          }}
        >
          <CircularProgress size={48} />
          <Typography variant="body1" color="text.secondary" sx={{ mt: 2 }}>
            Loading module content...
          </Typography>
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
        <Button
          startIcon={<ArrowBack />}
          onClick={() => navigate('/modules')}
          variant="outlined"
        >
          Back to Modules
        </Button>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Progress Tracker - tracks scroll position, active time, and sections viewed */}
      {enrollmentId && id && (
        <ModuleProgressTracker
          moduleId={id}
          enrollmentId={enrollmentId}
          sectionSelector="h2, h3"
          saveInterval={30000}
          enableResumeScroll={true}
          onProgressSaved={(progress) => {
            console.log('[ModulePlayerPage] Progress saved:', progress);
          }}
        />
      )}

      {/* Breadcrumbs */}
      <Breadcrumbs sx={{ mb: 3 }}>
        <Link
          component="button"
          underline="hover"
          color="inherit"
          onClick={() => navigate('/dashboard')}
          sx={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}
        >
          <Home sx={{ mr: 0.5 }} fontSize="small" />
          Dashboard
        </Link>
        <Link
          component="button"
          underline="hover"
          color="inherit"
          onClick={() => navigate('/modules')}
          sx={{ cursor: 'pointer' }}
        >
          Modules
        </Link>
        <Typography color="text.primary">Module {id}</Typography>
      </Breadcrumbs>

      {/* Back Button */}
      <Button
        startIcon={<ArrowBack />}
        onClick={() => navigate('/modules')}
        variant="outlined"
        size="small"
        sx={{ mb: 3 }}
      >
        Back to Modules
      </Button>

      {/* Module Content */}
      <Paper
        elevation={0}
        sx={{
          p: { xs: 2, md: 4 },
          border: '1px solid',
          borderColor: 'divider',
          borderRadius: 2,
        }}
      >
        {/* Render HTML content */}
        <Box
          dangerouslySetInnerHTML={{ __html: htmlContent }}
          sx={{
            '& h1': {
              fontSize: { xs: '1.75rem', md: '2.5rem' },
              fontWeight: 700,
              mb: 2,
              color: 'primary.main',
            },
            '& h2': {
              fontSize: { xs: '1.5rem', md: '2rem' },
              fontWeight: 600,
              mt: 4,
              mb: 2,
            },
            '& h3': {
              fontSize: { xs: '1.25rem', md: '1.5rem' },
              fontWeight: 600,
              mt: 3,
              mb: 1.5,
            },
            '& p': {
              mb: 2,
              lineHeight: 1.7,
            },
            '& a': {
              color: 'primary.main',
              textDecoration: 'none',
              '&:hover': {
                textDecoration: 'underline',
              },
            },
            '& ul, & ol': {
              mb: 2,
              pl: 3,
            },
            '& li': {
              mb: 1,
            },
            '& table': {
              width: '100%',
              borderCollapse: 'collapse',
              mb: 3,
              '& th, & td': {
                border: '1px solid',
                borderColor: 'divider',
                p: 1.5,
              },
              '& th': {
                bgcolor: 'primary.main',
                color: 'primary.contrastText',
                fontWeight: 600,
              },
            },
            '& blockquote': {
              borderLeft: '4px solid',
              borderColor: 'primary.main',
              pl: 2,
              ml: 0,
              my: 2,
              fontStyle: 'italic',
              color: 'text.secondary',
            },
            '& code': {
              bgcolor: 'grey.100',
              px: 0.75,
              py: 0.25,
              borderRadius: 0.5,
              fontSize: '0.9em',
              fontFamily: 'monospace',
            },
            '& pre': {
              bgcolor: 'grey.100',
              p: 2,
              borderRadius: 1,
              overflow: 'auto',
              mb: 2,
            },
            '& img': {
              maxWidth: '100%',
              height: 'auto',
              borderRadius: 1,
            },
          }}
        />
      </Paper>

      {/* H5P Activities Section */}
      {h5pActivities.length > 0 && (
        <Box sx={{ mt: 4 }}>
          <Typography variant="h5" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
            Interactive Activities
          </Typography>

          {h5pActivities.map((activity) => (
            <Paper
              key={activity.id}
              elevation={0}
              sx={{
                p: 3,
                mb: 3,
                border: '1px solid',
                borderColor: 'divider',
                borderRadius: 2,
              }}
            >
              <H5PPlayer
                activityId={activity.id}
                title={activity.title}
                height={600}
                onComplete={(result) => handleH5PComplete(activity.id, result)}
              />
            </Paper>
          ))}
        </Box>
      )}

      {/* Bottom Navigation */}
      <Box sx={{ mt: 4, display: 'flex', justifyContent: 'space-between' }}>
        <Button
          startIcon={<ArrowBack />}
          onClick={() => navigate('/modules')}
          variant="outlined"
        >
          Back to Modules
        </Button>
      </Box>
    </Container>
  );
};

export default ModulePlayerPage;
