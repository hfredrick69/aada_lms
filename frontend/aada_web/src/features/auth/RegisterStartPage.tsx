import { useState } from "react";
import { Alert, Box, Button, Container, Link, Paper, Stack, TextField, Typography } from "@mui/material";
import { Link as RouterLink } from "react-router-dom";
import type { ApiError } from "@/api/http-client";
import { requestRegistration } from "@/api/registration";

const DEFAULT_MESSAGE =
  "If the email is valid, you'll receive verification instructions shortly.";

export default function RegisterStartPage() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await requestRegistration(email);
      setSubmitted(true);
    } catch (err) {
      const apiError = err as ApiError;
      setError(apiError.response?.data?.detail ?? "Unable to send verification email. Please try again.");
    } finally {
      setLoading(false);
    }
  };

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
                Create your account
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Enter your email to begin registration.
              </Typography>
            </Box>

            {submitted ? (
              <Alert severity="success">{DEFAULT_MESSAGE}</Alert>
            ) : (
              error && <Alert severity="error">{error}</Alert>
            )}

            <TextField
              label="Email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              fullWidth
              disabled={submitted}
            />

            <Button
              type="submit"
              variant="contained"
              fullWidth
              size="large"
              disabled={loading || submitted}
              sx={{ bgcolor: "#d4af37", color: "#fff", "&:hover": { bgcolor: "#b5942d" } }}
            >
              {submitted ? "Email Sent" : loading ? "Sending..." : "Send Verification Email"}
            </Button>

            <Typography variant="body2" textAlign="center" color="text.secondary">
              Already have an account?{" "}
              <Link component={RouterLink} to="/login" underline="hover">
                Sign in
              </Link>
            </Typography>
          </Stack>
        </Paper>
      </Container>
    </Box>
  );
}
