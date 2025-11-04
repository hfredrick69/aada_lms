import { useMemo, useState } from 'react';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  CardHeader,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from '@mui/material';
import Grid from '@mui/material/Grid';
import { CloudUpload } from '@mui/icons-material';
import { format } from 'date-fns';
import { useQueryClient } from '@tanstack/react-query';
import { useCredentialsQuery, useCreateCredentialMutation, useTranscriptsQuery, useEnrollmentsQuery } from '@/api/hooks';
import { getListCredentialsApiCredentialsGetQueryKey } from '@/api/generated/credentials/credentials';
import type { CredentialRead, TranscriptRead } from '@/api/generated/models';
import { PageHeader } from '@/components/PageHeader';
import { LoadingState } from '@/components/states/LoadingState';
import { ErrorState } from '@/components/states/ErrorState';
import { useAuthStore } from '@/stores/auth-store';
import { enrollmentListSchema } from '@/types/enrollment';

const formatDate = (value?: string | null) => {
  if (!value) return '—';
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return '—';
  return format(parsed, 'MMM d, yyyy');
};

export const DocumentsPage = () => {
  const queryClient = useQueryClient();
  const user = useAuthStore((state) => state.user);
  const credentialsQuery = useCredentialsQuery();
  const transcriptsQuery = useTranscriptsQuery();
  const enrollmentsQuery = useEnrollmentsQuery();
  const createCredentialMutation = useCreateCredentialMutation({
    mutation: {
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: getListCredentialsApiCredentialsGetQueryKey() });
        setFormState({ credentialType: '', serialNumber: '', issuedAt: '' });
        setFeedback({ type: 'success', message: 'Credential record uploaded successfully.' });
      },
      onError: () => setFeedback({ type: 'error', message: 'Unable to upload document. Please try again.' }),
    },
  });

  const [formState, setFormState] = useState({ credentialType: '', serialNumber: '', issuedAt: '' });
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  const enrollments = useMemo(() => {
    const raw = enrollmentsQuery.data?.data ?? [];
    const parsed = enrollmentListSchema.safeParse(raw);
    return parsed.success ? parsed.data : [];
  }, [enrollmentsQuery.data]);

  const activeEnrollment = enrollments.find((enrollment) => enrollment.status === 'active');
  const credentialRows = (credentialsQuery.data?.data as CredentialRead[]) ?? [];
  const transcripts = (transcriptsQuery.data?.data as TranscriptRead[]) ?? [];

  if (credentialsQuery.isLoading || transcriptsQuery.isLoading || enrollmentsQuery.isLoading) {
    return <LoadingState label="Loading documents" />;
  }

  if (credentialsQuery.isError || transcriptsQuery.isError || enrollmentsQuery.isError) {
    return <ErrorState message="We were unable to load documents." />;
  }

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!user || !activeEnrollment) {
      setFeedback({ type: 'error', message: 'You must have an active enrollment to upload documents.' });
      return;
    }
    createCredentialMutation.mutate({
      data: {
        user_id: user.id,
        program_id: activeEnrollment.program_id,
        credential_type: formState.credentialType,
        cert_serial: formState.serialNumber,
        issued_at: formState.issuedAt ? new Date(formState.issuedAt).toISOString() : undefined,
      },
    });
  };

  return (
    <Box>
      <PageHeader
        title="Documents & Uploads"
        subtitle="Store official credentials, download transcripts, and maintain compliance records."
      />

      <Grid container spacing={3}>
        <Grid item xs={12} md={5}>
          <Card component="form" onSubmit={handleSubmit}>
            <CardHeader title="Upload credential" subheader="Record completion certificates or externship attestations." />
            <CardContent>
              <Stack spacing={2}>
                {feedback && <Alert severity={feedback.type}>{feedback.message}</Alert>}
                <TextField
                  label="Credential type"
                  value={formState.credentialType}
                  onChange={(event) => setFormState((prev) => ({ ...prev, credentialType: event.target.value }))}
                  required
                />
                <TextField
                  label="Certificate serial"
                  value={formState.serialNumber}
                  onChange={(event) => setFormState((prev) => ({ ...prev, serialNumber: event.target.value }))}
                  required
                />
                <TextField
                  label="Issued date"
                  type="date"
                  value={formState.issuedAt}
                  onChange={(event) => setFormState((prev) => ({ ...prev, issuedAt: event.target.value }))}
                  InputLabelProps={{ shrink: true }}
                />
                <Button
                  type="submit"
                  variant="contained"
                  startIcon={<CloudUpload />}
                  disabled={createCredentialMutation.isPending}
                >
                  {createCredentialMutation.isPending ? 'Uploading...' : 'Upload record'}
                </Button>
                <Typography variant="caption" color="text.secondary">
                  Uploaded records sync with the FastAPI credentials endpoint. Attach supporting files to your submission email if required.
                </Typography>
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={7}>
          <Card sx={{ mb: 3 }}>
            <CardHeader title="Credential archive" />
            <CardContent>
              {credentialRows.length === 0 ? (
                <Typography variant="body2" color="text.secondary">
                  No credentials uploaded yet. Submit your first document using the form on the left.
                </Typography>
              ) : (
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Type</TableCell>
                      <TableCell>Serial</TableCell>
                      <TableCell>Issued</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {credentialRows.map((credential) => (
                      <TableRow key={credential.id} hover>
                        <TableCell>{credential.credential_type}</TableCell>
                        <TableCell>{credential.cert_serial}</TableCell>
                        <TableCell>{formatDate(credential.issued_at)}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader title="Transcripts" subheader="Download PDF copies for employer or state submissions." />
            <CardContent>
              {transcripts.length === 0 ? (
                <Typography variant="body2" color="text.secondary">
                  Your transcripts will appear here once generated.
                </Typography>
              ) : (
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Issued</TableCell>
                      <TableCell>Program</TableCell>
                      <TableCell>GPA</TableCell>
                      <TableCell>PDF</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {transcripts.map((transcript) => (
                      <TableRow key={transcript.id} hover>
                        <TableCell>{formatDate(transcript.generated_at)}</TableCell>
                        <TableCell>{transcript.program_id}</TableCell>
                        <TableCell>{transcript.gpa ?? '—'}</TableCell>
                        <TableCell>
                          {transcript.pdf_url ? (
                            <Button
                              size="small"
                              component="a"
                              href={transcript.pdf_url}
                              target="_blank"
                              rel="noopener noreferrer"
                            >
                              Download
                            </Button>
                          ) : (
                            <Typography variant="body2" color="text.secondary">—</Typography>
                          )}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};
export default DocumentsPage;
