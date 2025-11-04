import { useEffect, useMemo, useState } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
  Box,
  Card,
  CardActions,
  CardContent,
  Chip,
  InputAdornment,
  Tab,
  Tabs,
  TextField,
  Typography,
} from '@mui/material';
import Grid from '@mui/material/Grid';
import { Search } from '@mui/icons-material';
import { useProgramsQuery, useProgramModulesQuery } from '@/api/hooks';
import { PageHeader } from '@/components/PageHeader';
import { LoadingState } from '@/components/states/LoadingState';
import { ErrorState } from '@/components/states/ErrorState';
import { moduleListSchema, programListSchema } from '@/types/program';

export const ModulesPage = () => {
  const programsQuery = useProgramsQuery();
  const programs = useMemo(() => {
    const raw = programsQuery.data?.data ?? [];
    const parsed = programListSchema.safeParse(raw);
    return parsed.success ? parsed.data : [];
  }, [programsQuery.data]);

  const [activeProgramId, setActiveProgramId] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    if (!activeProgramId && programs.length > 0) {
      setActiveProgramId(programs[0].id);
    }
  }, [activeProgramId, programs]);

  const modulesQuery = useProgramModulesQuery(activeProgramId ?? 'noop', {
    query: {
      enabled: Boolean(activeProgramId),
      staleTime: 5 * 60_000,
    },
  });

  const modules = useMemo(() => {
    const raw = modulesQuery.data?.data ?? [];
    const parsed = moduleListSchema.safeParse(raw);
    if (!parsed.success) {
      return [];
    }
    return parsed.data
      .slice()
      .sort((a, b) => (a.position ?? 0) - (b.position ?? 0))
      .filter((module) =>
        module.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        module.code.toLowerCase().includes(searchTerm.toLowerCase()),
      );
  }, [modulesQuery.data, searchTerm]);

  if (programsQuery.isLoading || modulesQuery.isLoading) {
    return <LoadingState label="Loading modules" />;
  }

  if (programsQuery.isError || modulesQuery.isError) {
    return <ErrorState message="We were unable to load modules. Please try again." />;
  }

  return (
    <Box>
      <PageHeader
        title="Program Modules"
        subtitle="Review lesson objectives, delivery mode, and clock hours for each course module."
      />

      <Tabs
        value={activeProgramId}
        onChange={(_, value) => setActiveProgramId(value)}
        variant="scrollable"
        allowScrollButtonsMobile
        sx={{ mb: 3 }}
      >
        {programs.map((program) => (
          <Tab key={program.id} value={program.id} label={program.name} />
        ))}
      </Tabs>

      <TextField
        fullWidth
        placeholder="Search modules by name or code"
        value={searchTerm}
        onChange={(event) => setSearchTerm(event.target.value)}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <Search fontSize="small" />
            </InputAdornment>
          ),
        }}
        sx={{ mb: 3 }}
      />

      {modules.length === 0 ? (
        <Typography variant="body2" color="text.secondary">
          No modules match your search. Try adjusting the filters or check back later.
        </Typography>
      ) : (
        <Grid container spacing={3}>
          {modules.map((module) => (
            <Grid item xs={12} sm={6} lg={4} key={module.id}>
              <Card
                variant="outlined"
                sx={{
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                }}
              >
                <CardContent>
                  <Chip label={module.code} color="primary" size="small" sx={{ mb: 2 }} />
                  <Typography variant="h6" fontWeight={600} gutterBottom>
                    {module.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    {module.clock_hours ?? 0} clock hours • {module.delivery_type?.replace('_', ' ') ?? 'Self-paced'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Position {module.position ?? '—'} in program sequence.
                  </Typography>
                </CardContent>
                <CardActions sx={{ mt: 'auto', px: 2, pb: 2 }}>
                  <Typography
                    component={RouterLink}
                    to={`/modules/${module.id}`}
                    sx={{
                      textDecoration: 'none',
                      fontWeight: 600,
                      color: 'primary.main',
                    }}
                  >
                    View lessons
                  </Typography>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  );
};
export default ModulesPage;
