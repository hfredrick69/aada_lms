import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ThemeProvider, CssBaseline, createTheme } from "@mui/material";
import App from "./App";
import "./index.css";

const queryClient = new QueryClient();

const theme = createTheme({
  palette: {
    mode: "light",
    primary: { main: "#F5B800" },
    background: { default: "#F9FAFB" },
  },
  typography: {
    fontFamily: "'Inter', sans-serif",
  },
});

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </ThemeProvider>
    </QueryClientProvider>
  </React.StrictMode>
);
