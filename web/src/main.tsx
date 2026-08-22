import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App.tsx";
import "./index.css";
import { SmoothScrollProvider } from "./providers/SmoothScrollProvider.tsx";
import { ThemeProvider } from "./providers/ThemeProvider.tsx";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ThemeProvider>
      <SmoothScrollProvider>
        <App />
      </SmoothScrollProvider>
    </ThemeProvider>
  </StrictMode>,
);
