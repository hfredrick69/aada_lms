import { useMemo } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Box, Button, Paper } from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import { PageHeader } from '@/components/PageHeader';
import { LoadingState } from '@/components/states/LoadingState';
import { ErrorState } from '@/components/states/ErrorState';
import { useModuleContentQuery } from '@/api/hooks';

export const ModuleDetailPage = () => {
  const navigate = useNavigate();
  const { moduleId } = useParams<{ moduleId: string }>();
  const moduleQuery = useModuleContentQuery(moduleId ?? 'noop', {
    query: {
      enabled: Boolean(moduleId),
      retry: 1,
    },
  });

  const moduleContent = useMemo(() => moduleQuery.data?.data ?? '', [moduleQuery.data]);

  if (moduleQuery.isLoading) {
    return <LoadingState label="Loading module" />;
  }

  if (moduleQuery.isError) {
    return <ErrorState message="We were unable to load this module. Please try again later." />;
  }

  return (
    <Box>
      <PageHeader
        title="Module Overview"
        subtitle="Dive into lesson plans, clinical videos, and compliance checklists for this module."
        action={
          <Button startIcon={<ArrowBackIcon />} onClick={() => navigate(-1)} variant="outlined">
            Back
          </Button>
        }
      />

      <Paper elevation={0} sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 3, overflow: 'hidden' }}>
        {moduleContent ? (
          <Box
            component="iframe"
            title="Module Content"
            srcDoc={moduleContent}
            sx={{
              width: '100%',
              minHeight: '70vh',
              border: 'none',
            }}
            sandbox="allow-popups allow-same-origin"
          />
        ) : (
          <Box sx={{ p: 4 }}>
            This module does not contain published content yet.
          </Box>
        )}
      </Paper>
    </Box>
  );
};
