import { Suspense, lazy, useMemo, useState, type LazyExoticComponent } from "react";
import { AnimatePresence, motion } from "framer-motion";

import { Sidebar, type NavKey } from "@/components/layout/Sidebar";
import { TopNavigation } from "@/components/layout/TopNavigation";
import { TerminalSkeleton } from "@/components/ui/Skeleton";
import { useTerminalData } from "@/hooks/useTerminalData";

const Dashboard = lazy(() => import("@/pages/Dashboard"));
const MarketAnalysis = lazy(() => import("@/pages/MarketAnalysis"));
const Forecasting = lazy(() => import("@/pages/Forecasting"));
const ModelLab = lazy(() => import("@/pages/ModelLab"));
const SentimentAnalysis = lazy(() => import("@/pages/SentimentAnalysis"));
const Portfolio = lazy(() => import("@/pages/Portfolio"));
const Backtesting = lazy(() => import("@/pages/Backtesting"));
const RiskAnalysis = lazy(() => import("@/pages/RiskAnalysis"));
const Leaderboard = lazy(() => import("@/pages/Leaderboard"));
const Settings = lazy(() => import("@/pages/Settings"));

const pages: Record<NavKey, LazyExoticComponent<() => JSX.Element>> = {
  dashboard: Dashboard,
  market: MarketAnalysis,
  forecasting: Forecasting,
  models: ModelLab,
  sentiment: SentimentAnalysis,
  portfolio: Portfolio,
  backtesting: Backtesting,
  risk: RiskAnalysis,
  leaderboard: Leaderboard,
  settings: Settings
};

export default function App() {
  const [activePage, setActivePage] = useState<NavKey>("dashboard");
  const terminal = useTerminalData();
  const Page = useMemo(() => pages[activePage], [activePage]);

  return (
    <div className="min-h-screen bg-terminal-bg text-terminal-text">
      <TopNavigation
        symbol={terminal.symbol}
        setSymbol={terminal.setSymbol}
        data={terminal.data}
        loading={terminal.loading}
        onRefresh={terminal.refresh}
        onUpdate={terminal.updateData}
      />
      <div className="terminal-shell">
        <Sidebar active={activePage} onChange={setActivePage} />
        <main className="terminal-main">
          {terminal.error && <div className="terminal-alert">{terminal.error}</div>}
          <AnimatePresence mode="wait">
            <motion.div
              key={activePage}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.18, ease: "easeOut" }}
            >
              <Suspense fallback={<TerminalSkeleton />}>
                <Page />
              </Suspense>
            </motion.div>
          </AnimatePresence>
        </main>
      </div>
    </div>
  );
}
