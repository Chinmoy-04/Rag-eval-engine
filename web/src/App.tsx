import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { Shell } from "@/components/Shell";
import { AskPage } from "@/pages/AskPage";
import { ComparePage } from "@/pages/ComparePage";
import { RunsPage } from "@/pages/RunsPage";
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
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </AskChatProvider>
    </BrowserRouter>
  );
}
