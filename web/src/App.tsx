import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { Shell } from "@/components/Shell";
import { AboutPage } from "@/pages/AboutPage";
import { AskPage } from "@/pages/AskPage";
import { ComparePage } from "@/pages/ComparePage";
import { PrivacyPage } from "@/pages/PrivacyPage";
import { RunsPage } from "@/pages/RunsPage";
import { TermsPage } from "@/pages/TermsPage";
import { AskChatProvider } from "@/providers/AskChatProvider";

export default function App() {
  return (
    <BrowserRouter>
      <AskChatProvider>
        <Routes>
          <Route element={<Shell />}>
            <Route index element={<AskPage />} />
            <Route path="runs" element={<RunsPage />} />
            <Route path="compare" element={<ComparePage />} />
            <Route path="about" element={<AboutPage />} />
            <Route path="terms" element={<TermsPage />} />
            <Route path="privacy" element={<PrivacyPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </AskChatProvider>
    </BrowserRouter>
  );
}
