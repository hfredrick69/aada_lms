import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Container,
  IconButton,
  InputAdornment,
  Paper,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { Visibility, VisibilityOff } from "@mui/icons-material";
import { useQueryClient } from "@tanstack/react-query";
import { useLoginMutation } from "@/api/hooks";
import { getMeApiAuthMeGetQueryOptions } from "@/api/generated/auth/auth";
import { useAuthStore } from "@/stores/auth-store";

export default function LoginPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { isAuthenticated, setUser } = useAuthStore();

  const loginMutation = useLoginMutation({
    mutation: {
      onSuccess: async () => {
        // Tokens are stored in httpOnly cookies (Phase 4), no need to store in state
        try {
          const { queryFn, queryKey } = getMeApiAuthMeGetQueryOptions();
          const userResponse = await queryClient.fetchQuery({ queryKey, queryFn });
          setUser(userResponse.data);
          navigate("/dashboard", { replace: true });
        } catch (error) {
          console.error("Failed to fetch user profile:", error);
        }
      },
    },
  });

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  useEffect(() => {
    if (isAuthenticated) {
      navigate("/dashboard", { replace: true });
    }
  }, [isAuthenticated, navigate]);

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault(); // 🔥 prevents reload
    loginMutation.mutate({ data: { email, password } });
  };

  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        bgcolor: "#f0f6ff",
      }}
    >
      <Container maxWidth="sm">
        <Paper
          elevation={4}
          sx={{ p: 4, borderRadius: 4 }}
          component="form"
          onSubmit={handleSubmit}
          noValidate
        >
          <Stack spacing={3}>
            <Box textAlign="center">
              <Typography variant="h4" fontWeight={700}>
                Student Portal
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Sign in to continue learning with AADA
              </Typography>
            </Box>

            {loginMutation.isError && (
              <Alert severity="error">
                Invalid email or password. Please try again.
              </Alert>
            )}

            <TextField
              label="Email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              fullWidth
            />

            <TextField
              label="Password"
              type={showPassword ? "text" : "password"}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              fullWidth
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton onClick={() => setShowPassword((prev) => !prev)}>
                      {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />

            <Button
              type="submit"
              variant="contained"
              fullWidth
              size="large"
              sx={{ bgcolor: "#d4af37", color: "#fff", "&:hover": { bgcolor: "#b5942d" } }}
              disabled={loginMutation.isPending}
            >
              {loginMutation.isPending ? (
                <CircularProgress size={24} color="inherit" />
              ) : (
                "Sign In"
              )}
            </Button>
          </Stack>
        </Paper>
      </Container>
    </Box>
  );
}
