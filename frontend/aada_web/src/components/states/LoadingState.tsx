import { Box, CircularProgress, Typography } from '@mui/material';

export const LoadingState = ({ label = 'Loading data...' }: { label?: string }) => (
  <Box
    sx={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      gap: 2,
      py: 6,
    }}
  >
    <CircularProgress />
    <Typography variant="body2" color="text.secondary">
      {label}
    </Typography>
  </Box>
);
