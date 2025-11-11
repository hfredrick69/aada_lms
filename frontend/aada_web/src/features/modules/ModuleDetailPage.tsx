import { useMemo } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Box, Button } from '@mui/material';
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

      <Box sx={{ mt: 4, px: { xs: 0, md: 2 }, pb: { xs: 6, md: 8 } }}>
        {moduleContent ? (
          <Box
            className="module-html"
            sx={{
              maxWidth: 'min(960px, 100%)',
              mx: 'auto',
              bgcolor: 'background.paper',
              borderRadius: 3,
              border: '1px solid',
              borderColor: 'divider',
              boxShadow: { md: '0px 24px 70px rgba(15,23,42,0.08)' },
              p: { xs: 3, md: 5 },
              '& h1, & h2, & h3': {
                color: 'text.primary',
                fontFamily: 'inherit',
              },
              '& h1': {
                fontSize: { xs: '1.8rem', md: '2.2rem' },
                borderBottom: '2px solid',
                borderColor: 'primary.light',
                pb: 1,
                mb: 3,
              },
              '& h2': {
                fontSize: { xs: '1.4rem', md: '1.8rem' },
                borderBottom: '1px solid',
                borderColor: 'divider',
                pb: 1,
                mt: 5,
              },
              '& img': {
                maxWidth: '100%',
                height: 'auto',
                display: 'block',
                my: 3,
              },
              '& table': {
                width: '100%',
                borderCollapse: 'collapse',
                my: 3,
              },
              '& table th, & table td': {
                border: '1px solid',
                borderColor: 'divider',
                p: 1.5,
                textAlign: 'left',
                fontSize: '0.95rem',
              },
              '& blockquote': {
                borderLeft: '4px solid',
                borderColor: 'primary.main',
                pl: 3,
                color: 'text.secondary',
                my: 3,
              },
              '& iframe': {
                width: '100%',
                border: '1px solid',
                borderColor: 'divider',
                borderRadius: 2,
                boxShadow: '0px 8px 30px rgba(15,23,42,0.08)',
                minHeight: 420,
              },
            }}
            dangerouslySetInnerHTML={{ __html: moduleContent }}
          />
        ) : (
          <Box
            sx={{
              maxWidth: 600,
              mx: 'auto',
              textAlign: 'center',
              bgcolor: 'background.paper',
              borderRadius: 3,
              border: '1px dashed',
              borderColor: 'divider',
              p: { xs: 4, md: 6 },
              color: 'text.secondary',
            }}
          >
            This module does not contain published content yet.
          </Box>
        )}
      </Box>
    </Box>
  );
};
