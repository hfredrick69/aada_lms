import { Alert, AlertTitle, Box, Button } from '@mui/material';

interface ErrorStateProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
}

export const ErrorState = ({
  title = 'Something went wrong',
  message = 'Please try again or contact support if the issue persists.',
  onRetry,
}: ErrorStateProps) => (
  <Box sx={{ py: 4 }}>
    <Alert severity="error" action={onRetry && <Button color="inherit" size="small" onClick={onRetry}>Retry</Button>}>
      <AlertTitle>{title}</AlertTitle>
      {message}
    </Alert>
  </Box>
);
