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
import { AccountBalanceWallet, Receipt } from '@mui/icons-material';
import { format } from 'date-fns';
import { useMeQuery } from '@/api/hooks';
import { useStudentBalance, usePaymentHistory } from '@/api/payments';
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
  const { data: currentUser } = useMeQuery();
  const balanceQuery = useStudentBalance(currentUser?.id);
  const historyQuery = usePaymentHistory(currentUser?.id);

  const paymentHistory = useMemo(
    () => (historyQuery.data ?? []).slice().sort((a, b) =>
      new Date(b.created_at ?? 0).getTime() - new Date(a.created_at ?? 0).getTime(),
    ),
    [historyQuery.data],
  );

  const charges = paymentHistory.filter((item) => ['tuition', 'fee'].includes(item.line_type));
  const payments = paymentHistory.filter((item) => ['payment', 'refund'].includes(item.line_type));

  if (balanceQuery.isLoading || historyQuery.isLoading) {
    return <LoadingState label="Loading payment history" />;
  }

  if (balanceQuery.isError || historyQuery.isError) {
    return <ErrorState message="We were unable to load payment data." />;
  }

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
              avatar={<AccountBalanceWallet color={balanceQuery.data && balanceQuery.data.balance_cents > 0 ? 'warning' : 'success'} />}
              title="Current Balance"
              subheader="Charges minus payments"
            />
            <CardContent>
              <Typography variant="h4" fontWeight={700} gutterBottom>
                {formatCurrency(balanceQuery.data?.balance_cents ?? 0)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {balanceQuery.data && balanceQuery.data.balance_cents > 0
                  ? 'Amount due to AADA'
                  : balanceQuery.data && balanceQuery.data.balance_cents < 0
                  ? 'Credit balance in your favor'
                  : 'Your account is paid in full'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader
              avatar={<Receipt color="primary" />}
              title="Total Payments"
              subheader="Payments and refunds received"
            />
            <CardContent>
              <Typography variant="h4" fontWeight={700} gutterBottom>
                {formatCurrency(balanceQuery.data?.total_payments_cents ?? 0)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total amount paid toward tuition and fees.
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} lg={6}>
          <Card>
            <CardHeader title="Charges" subheader="Tuition and fees assessed" />
            <CardContent>
              {charges.length === 0 ? (
                <Typography variant="body2" color="text.secondary">
                  No charges recorded.
                </Typography>
              ) : (
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Date</TableCell>
                      <TableCell>Type</TableCell>
                      <TableCell>Description</TableCell>
                      <TableCell align="right">Amount</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {charges.map((charge) => (
                      <TableRow key={charge.id} hover>
                        <TableCell>{formatDate(charge.created_at)}</TableCell>
                        <TableCell>
                          <Chip
                            size="small"
                            color={charge.line_type === 'tuition' ? 'primary' : 'default'}
                            label={charge.line_type}
                          />
                        </TableCell>
                        <TableCell>{charge.description ?? '—'}</TableCell>
                        <TableCell align="right">{formatCurrency(charge.amount_cents)}</TableCell>
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
            <CardHeader title="Payments & Refunds" subheader="Amounts received and returned" />
            <CardContent>
              {payments.length === 0 ? (
                <Typography variant="body2" color="text.secondary">
                  No payments or refunds recorded.
                </Typography>
              ) : (
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Date</TableCell>
                      <TableCell>Type</TableCell>
                      <TableCell>Description</TableCell>
                      <TableCell align="right">Amount</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {payments.map((payment) => (
                      <TableRow key={payment.id} hover>
                        <TableCell>{formatDate(payment.created_at)}</TableCell>
                        <TableCell>
                          <Chip
                            size="small"
                            color={payment.line_type === 'payment' ? 'success' : 'info'}
                            label={payment.line_type}
                          />
                        </TableCell>
                        <TableCell>{payment.description ?? '—'}</TableCell>
                        <TableCell align="right">{formatCurrency(payment.amount_cents)}</TableCell>
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
