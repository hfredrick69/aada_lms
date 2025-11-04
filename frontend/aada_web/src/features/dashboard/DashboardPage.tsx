import { Typography, Box } from "@mui/material";

export default function DashboardPage() {
  return (
    <Box>
      <Typography variant="h6" fontWeight={600} gutterBottom>
        Dashboard
      </Typography>
      <Typography variant="body2" color="text.secondary">
        You've successfully logged into the AADA Learning Portal.
      </Typography>
    </Box>
  );
}
