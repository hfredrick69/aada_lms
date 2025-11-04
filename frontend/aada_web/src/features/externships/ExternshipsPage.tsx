import { useMemo } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  CardHeader,
  Chip,
  Divider,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material';
import { AddTask, UploadFile } from '@mui/icons-material';
import { format } from 'date-fns';
import { useExternshipsQuery } from '@/api/hooks';
import type { ExternshipRead } from '@/api/generated/models';
import { PageHeader } from '@/components/PageHeader';
import { LoadingState } from '@/components/states/LoadingState';
import { ErrorState } from '@/components/states/ErrorState';

const formatDate = (value?: string | null) => {
  if (!value) return '—';
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return '—';
  return format(parsed, 'MMM d, yyyy');
};

export const ExternshipsPage = () => {
  const externshipsQuery = useExternshipsQuery();

  if (externshipsQuery.isLoading) {
    return <LoadingState label="Loading externship records" />;
  }

  if (externshipsQuery.isError) {
    return <ErrorState message="We were unable to load externship data." />;
  }

  const externships = useMemo(
    () => ((externshipsQuery.data?.data as ExternshipRead[]) ?? []).slice().sort((a, b) =>
      (b.verified_at ? new Date(b.verified_at).getTime() : 0) -
      (a.verified_at ? new Date(a.verified_at).getTime() : 0),
    ),
    [externshipsQuery.data],
  );

  const totalHours = externships.reduce((sum, record) => sum + (record.total_hours ?? 0), 0);
  const verifiedCount = externships.filter((record) => record.verified).length;

  return (
    <Box>
      <PageHeader
        title="Externship Tracker"
        subtitle="Monitor clinical placement hours, supervisor sign-off, and verification documents."
        action={
          <Stack direction="row" spacing={1}>
            <Button startIcon={<AddTask />} variant="contained" color="primary">
              Log hours
            </Button>
            <Button startIcon={<UploadFile />} variant="outlined">
              Upload verification
            </Button>
          </Stack>
        }
      />

      <Card sx={{ mb: 3 }}>
        <CardHeader title="Progress summary" />
        <CardContent>
          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={3} divider={<Divider flexItem orientation="vertical" />}>
            <Box>
              <Typography variant="h4" fontWeight={700}>{totalHours}</Typography>
              <Typography variant="body2" color="text.secondary">Total hours completed</Typography>
            </Box>
            <Box>
              <Typography variant="h4" fontWeight={700}>{verifiedCount}</Typography>
              <Typography variant="body2" color="text.secondary">Verified placements</Typography>
            </Box>
            <Box>
              <Typography variant="h4" fontWeight={700}>{externships.length}</Typography>
              <Typography variant="body2" color="text.secondary">Sites on record</Typography>
            </Box>
          </Stack>
        </CardContent>
      </Card>

      <Card>
        <CardHeader title="Placement history" subheader="Each entry reflects a verified classroom-to-clinic experience." />
        <CardContent>
          {externships.length === 0 ? (
            <Typography variant="body2" color="text.secondary">
              Externship records will appear here once you submit your first placement.
            </Typography>
          ) : (
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Site</TableCell>
                  <TableCell>Supervisor</TableCell>
                  <TableCell>Hours</TableCell>
                  <TableCell>Verification</TableCell>
                  <TableCell>Document</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {externships.map((record) => (
                  <TableRow key={record.id} hover>
                    <TableCell>
                      <Typography fontWeight={600}>{record.site_name}</Typography>
                      <Typography variant="body2" color="text.secondary">{record.site_address ?? 'Address pending'}</Typography>
                    </TableCell>
                    <TableCell>
                      <Typography>{record.supervisor_name ?? '—'}</Typography>
                      <Typography variant="body2" color="text.secondary">{record.supervisor_email ?? '—'}</Typography>
                    </TableCell>
                    <TableCell>{record.total_hours ?? 0}</TableCell>
                    <TableCell>
                      <Chip
                        size="small"
                        color={record.verified ? 'success' : 'warning'}
                        label={record.verified ? `Verified ${formatDate(record.verified_at)}` : 'Pending review'}
                      />
                    </TableCell>
                    <TableCell>
                      {record.verification_doc_url ? (
                        <Button
                          size="small"
                          component="a"
                          href={record.verification_doc_url}
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          View
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
    </Box>
  );
};
export default ExternshipsPage;
