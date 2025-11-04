import { Typography, Box, Stack, Button } from "@mui/material";
import { useAuthStore } from "@/stores/auth-store";
import { useNavigate } from "react-router-dom";

export default function DashboardPage() {
  const user = useAuthStore((s) => s.user);
  const clearAuth = useAuthStore((s) => s.clearAuth);
  const navigate = useNavigate();

  const handleLogout = () => {
    clearAuth();
    navigate("/login", { replace: true });
  };

  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        bgcolor: "#f8fafc",
      }}
    >
      <Stack spacing={2} alignItems="center">
        <Typography variant="h3" fontWeight={700} color="primary">
          Welcome, {user?.first_name ?? "Student"}!
        </Typography>
        <Typography variant="body1" color="text.secondary">
          You’ve successfully logged into the AADA Learning Portal.
        </Typography>
        <Button
          variant="contained"
          color="primary"
          sx={{ mt: 3, px: 4, py: 1 }}
          onClick={handleLogout}
        >
          Logout
        </Button>
      </Stack>
    </Box>
  );
}
