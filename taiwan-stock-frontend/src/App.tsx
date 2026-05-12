import { Navigate, Route, Routes } from "react-router-dom";
import Navbar from "./components/Navbar";
import StocksPage from "./pages/StocksPage";
import DividendsPage from "./pages/DividendsPage";
import StockDividendsPage from "./pages/StockDividendsPage";
import RefreshLogsPage from "./pages/RefreshLogsPage";
import SchedulerPage from "./pages/SchedulerPage";

export default function App() {
  return (
    <div
      style={{
        minHeight: "100vh",
        backgroundColor: "#f8fafc",
      }}
    >
      <Navbar />

      <main>
        <Routes>
          <Route path="/" element={<Navigate to="/stocks" replace />} />
          <Route path="/stocks" element={<StocksPage />} />
          <Route path="/stocks/:stockCode/dividends" element={<StockDividendsPage />} />
          <Route path="/dividends" element={<DividendsPage />} />
          <Route path="/admin/refresh-logs" element={<RefreshLogsPage />} />
          <Route path="/admin/scheduler" element={<SchedulerPage />} />
        </Routes>
      </main>
    </div>
  );
}