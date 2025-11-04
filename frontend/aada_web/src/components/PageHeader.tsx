import { Box, Stack, Typography } from '@mui/material';
import type { ReactNode } from 'react';

interface PageHeaderProps {
  title: string;
  subtitle?: string;
  action?: ReactNode;
}

export const PageHeader = ({ title, subtitle, action }: PageHeaderProps) => (
  <Stack
    direction={{ xs: 'column', sm: 'row' }}
    spacing={2}
    alignItems={{ xs: 'flex-start', sm: 'center' }}
    justifyContent="space-between"
    sx={{ mb: 3 }}
  >
    <Box>
      <Typography variant="h4" component="h1" fontWeight={700} gutterBottom>
        {title}
      </Typography>
      {subtitle && (
        <Typography variant="body1" color="text.secondary">
          {subtitle}
        </Typography>
      )}
    </Box>
    {action}
  </Stack>
);
