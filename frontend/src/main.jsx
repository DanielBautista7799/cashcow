import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App.jsx";
import { AuthProvider } from "./context/AuthContext.jsx";
import { ThemeProvider, CssBaseline } from "@mui/material";
import theme from "./theme.js"




createRoot(document.getElementById("root")).render(
  <ThemeProvider theme={theme}>
    <CssBaseline />
  <StrictMode>
    <AuthProvider>
      <App />
    </AuthProvider>
  </StrictMode>
  </ThemeProvider>

);