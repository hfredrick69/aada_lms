import { useEffect, useState } from "react";
import { Alert, Box, Button, CircularProgress, Container, Link, Paper, Stack, Typography } from "@mui/material";
import { Link as RouterLink, useNavigate, useSearchParams } from "react-router-dom";
import type { ApiError } from "@/api/http-client";
import { verifyRegistration } from "@/api/registration";

const REGISTRATION_TOKEN_STORAGE_KEY = "aada_registration_token";
const REGISTRATION_TOKEN_EXP_STORAGE_KEY = "aada_registration_token_exp";

export default function RegisterVerifyPage() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token");
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const run = async () => {
      if (!token) {
        setError("Verification link is missing a token.");
        setLoading(false);
        return;
      }
      try {
        const response = await verifyRegistration(token);
        if (typeof window !== "undefined") {
          sessionStorage.setItem(REGISTRATION_TOKEN_STORAGE_KEY, response.registration_token);
          sessionStorage.setItem(REGISTRATION_TOKEN_EXP_STORAGE_KEY, response.expires_at);
        }
        navigate("/register/complete", { replace: true });
      } catch (err) {
        const apiError = err as ApiError;
        setError(apiError.response?.data?.detail ?? "Verification link is invalid or has expired.");
        setLoading(false);
      }
    };

    run();
  }, [navigate, token]);

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
            <Typography variant="h4" fontWeight={700}>
              Verifying email
            </Typography>
            {loading && !error ? (
              <>
                <Typography variant="body1" color="text.secondary">
                  Please wait while we verify your link…
                </Typography>
                <CircularProgress sx={{ alignSelf: "center" }} />
              </>
            ) : (
              <>
                <Alert severity="error">{error}</Alert>
                <Button variant="outlined" component={RouterLink} to="/register">
                  Start over
                </Button>
              </>
            )}
            <Typography variant="body2" color="text.secondary">
              Already verified?{" "}
              <Link component={RouterLink} to="/login" underline="hover">
                Return to login
              </Link>
            </Typography>
          </Stack>
        </Paper>
      </Container>
    </Box>
  );
}
