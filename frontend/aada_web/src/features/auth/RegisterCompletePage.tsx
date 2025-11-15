import { useMemo, useState } from "react";
import {
  Alert,
  Box,
  Button,
  Container,
  Link,
  Paper,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { Link as RouterLink } from "react-router-dom";
import type { ApiError } from "@/api/http-client";
import { completeRegistration } from "@/api/registration";

const REGISTRATION_TOKEN_STORAGE_KEY = "aada_registration_token";

export default function RegisterCompletePage() {
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const registrationToken = useMemo(
    () => (typeof window !== "undefined" ? sessionStorage.getItem(REGISTRATION_TOKEN_STORAGE_KEY) : null),
    []
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const clearToken = () => {
    if (typeof window !== "undefined") {
      sessionStorage.removeItem(REGISTRATION_TOKEN_STORAGE_KEY);
      sessionStorage.removeItem("aada_registration_token_exp");
    }
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!registrationToken) {
      setError("Registration token missing. Please restart the process.");
      return;
    }
    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);
    setError(null);
    try {
      await completeRegistration({
        registration_token: registrationToken,
        first_name: firstName,
        last_name: lastName,
        password,
      });
      clearToken();
      setSuccess(true);
    } catch (err) {
      const apiError = err as ApiError;
      setError(apiError.response?.data?.detail ?? "Unable to complete registration.");
    } finally {
      setLoading(false);
    }
  };

  if (!registrationToken && !success) {
    return (
      <Box
        sx={{
          minHeight: "100vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          bgcolor: "#f0f6ff",
          px: 2,
        }}
      >
        <Container maxWidth="sm">
          <Paper elevation={4} sx={{ p: 4, borderRadius: 4 }}>
            <Stack spacing={3} textAlign="center">
              <Typography variant="h5" fontWeight={700}>
                Registration link expired
              </Typography>
              <Typography color="text.secondary">
                We couldn't find an active registration session. Please restart the process.
              </Typography>
              <Button variant="contained" component={RouterLink} to="/register" sx={{ bgcolor: "#d4af37" }}>
                Restart registration
              </Button>
            </Stack>
          </Paper>
        </Container>
      </Box>
    );
  }

  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        bgcolor: "#f0f6ff",
        px: 2,
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
                Finish setting up your profile
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Add your details and create a password to access the student portal.
              </Typography>
            </Box>

            {error && <Alert severity="error">{error}</Alert>}
            {success && (
              <Alert severity="success">
                Registration complete! You can now{" "}
                <Link component={RouterLink} to="/login" underline="hover">
                  sign in
                </Link>
                .
              </Alert>
            )}

            {!success && (
              <>
                <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
                  <TextField
                    label="First name"
                    value={firstName}
                    onChange={(e) => setFirstName(e.target.value)}
                    fullWidth
                    required
                  />
                  <TextField
                    label="Last name"
                    value={lastName}
                    onChange={(e) => setLastName(e.target.value)}
                    fullWidth
                    required
                  />
                </Stack>

                <TextField
                  label="Password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  helperText="Use at least 12 characters with upper, lower, number, and symbol."
                  required
                  fullWidth
                />

                <TextField
                  label="Confirm password"
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                  fullWidth
                />

                <Button
                  type="submit"
                  variant="contained"
                  fullWidth
                  size="large"
                  disabled={loading}
                  sx={{ bgcolor: "#d4af37", color: "#fff", "&:hover": { bgcolor: "#b5942d" } }}
                >
                  {loading ? "Creating account..." : "Create account"}
                </Button>
              </>
            )}

            {success && (
              <Button variant="contained" component={RouterLink} to="/login" sx={{ bgcolor: "#d4af37" }}>
                Go to login
              </Button>
            )}
          </Stack>
        </Paper>
      </Container>
    </Box>
  );
}
