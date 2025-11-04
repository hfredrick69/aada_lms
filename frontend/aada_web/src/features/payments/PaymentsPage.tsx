import { useMemo } from 'react';
import {
  Box,
  Card,
  CardContent,
  CardHeader,
  Chip,
  Divider,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material';
import Grid from '@mui/material/Grid';
import { CreditCard, MonetizationOn } from '@mui/icons-material';
import { format } from 'date-fns';
import { useRefundsQuery, useWithdrawalsQuery } from '@/api/hooks';
import type { RefundRead, WithdrawalRead } from '@/api/generated/models';
import { PageHeader } from '@/components/PageHeader';
import { LoadingState } from '@/components/states/LoadingState';
import { ErrorState } from '@/components/states/ErrorState';

const formatCurrency = (amountCents: number) => (amountCents / 100).toLocaleString('en-US', {
  style: 'currency',
  currency: 'USD',
});

const formatDate = (value?: string | null) => {
  if (!value) return '—';
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return '—';
  return format(parsed, 'MMM d, yyyy');
};

export const PaymentsPage = () => {
  const withdrawalsQuery = useWithdrawalsQuery();
  const refundsQuery = useRefundsQuery();

  if (withdrawalsQuery.isLoading || refundsQuery.isLoading) {
    return <LoadingState label="Loading payment history" />;
  }

  if (withdrawalsQuery.isError || refundsQuery.isError) {
    return <ErrorState message="We were unable to load payment data." />;
  }

  const withdrawals = useMemo(
    () => ((withdrawalsQuery.data?.data as WithdrawalRead[]) ?? []).slice().sort((a, b) =>
      new Date(b.requested_at).getTime() - new Date(a.requested_at).getTime(),
    ),
    [withdrawalsQuery.data],
  );

  const refunds = useMemo(
    () => ((refundsQuery.data?.data as RefundRead[]) ?? []).slice().sort((a, b) =>
      new Date(b.approved_at ?? 0).getTime() - new Date(a.approved_at ?? 0).getTime(),
    ),
    [refundsQuery.data],
  );

  const totalRefunds = refunds.reduce((sum, record) => sum + (record.amount_cents ?? 0), 0);
  const pendingWithdrawals = withdrawals.filter((record) => !record.admin_processed_at).length;

  return (
    <Box>
      <PageHeader
        title="Payments & Tuition"
        subtitle="Review tuition withdrawals, refund decisions, and maintain compliance with state reporting." 
      />

      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader
              avatar={<CreditCard color="primary" />}
              title="Withdrawals in progress"
              subheader="Awaiting administrative review"
            />
            <CardContent>
              <Typography variant="h4" fontWeight={700} gutterBottom>
                {pendingWithdrawals}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Once processed, you&apos;ll receive status updates and any related documentation here.
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader
              avatar={<MonetizationOn color="success" />}
              title="Refunds issued"
              subheader="Policy-compliant remittances"
            />
            <CardContent>
              <Typography variant="h4" fontWeight={700} gutterBottom>
                {formatCurrency(totalRefunds)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Track remittance dates and approval notes to confirm funds were delivered.
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} lg={6}>
          <Card>
            <CardHeader title="Withdrawal requests" subheader="Student-initiated tuition adjustments" />
            <CardContent>
              {withdrawals.length === 0 ? (
                <Typography variant="body2" color="text.secondary">
                  No withdrawal requests recorded.
                </Typography>
              ) : (
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Date requested</TableCell>
                      <TableCell>Progress %</TableCell>
                      <TableCell>Reason</TableCell>
                      <TableCell>Status</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {withdrawals.map((withdrawal) => (
                      <TableRow key={withdrawal.id} hover>
                        <TableCell>{formatDate(withdrawal.requested_at)}</TableCell>
                        <TableCell>{withdrawal.progress_pct_at_withdrawal ?? '—'}</TableCell>
                        <TableCell>{withdrawal.reason ?? 'Not provided'}</TableCell>
                        <TableCell>
                          <Chip
                            size="small"
                            color={withdrawal.admin_processed_at ? 'success' : 'warning'}
                            label={withdrawal.admin_processed_at ? 'Processed' : 'Pending'}
                          />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} lg={6}>
          <Card>
            <CardHeader title="Refund remittances" subheader="Amounts returned per GNPEC policy" />
            <CardContent>
              {refunds.length === 0 ? (
                <Typography variant="body2" color="text.secondary">
                  No refunds have been issued yet.
                </Typography>
              ) : (
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Approved</TableCell>
                      <TableCell>Amount</TableCell>
                      <TableCell>Policy basis</TableCell>
                      <TableCell>Remitted</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {refunds.map((refund) => (
                      <TableRow key={refund.id} hover>
                        <TableCell>{formatDate(refund.approved_at)}</TableCell>
                        <TableCell>{formatCurrency(refund.amount_cents)}</TableCell>
                        <TableCell>{refund.policy_basis ?? '—'}</TableCell>
                        <TableCell>
                          {refund.remitted_at ? (
                            <Chip size="small" color="success" label={formatDate(refund.remitted_at)} />
                          ) : (
                            <Chip size="small" color="warning" label="Pending" />
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

      <Divider sx={{ my: 4 }} />
      <Typography variant="body2" color="text.secondary">
        Financial data syncs directly from the FastAPI ledger endpoints. Contact finance@aada.edu for payment plans or to reconcile any discrepancies.
      </Typography>
    </Box>
  );
};
export default PaymentsPage;
