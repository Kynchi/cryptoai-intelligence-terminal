import {
  Activity,
  BarChart3,
  BrainCircuit,
  Gauge,
  LayoutDashboard,
  LineChart,
  Medal,
  PieChart,
  Radar,
  Settings,
  ShieldAlert
} from "lucide-react";

import { Button } from "@/components/ui/Button";
import { cn } from "@/utils/cn";

export type NavKey =
  | "dashboard"
  | "market"
  | "forecasting"
  | "models"
  | "sentiment"
  | "portfolio"
  | "backtesting"
  | "risk"
  | "leaderboard"
  | "settings";

const nav = [
  { key: "dashboard", label: "Dashboard", icon: LayoutDashboard },
  { key: "market", label: "Market Analysis", icon: BarChart3 },
  { key: "forecasting", label: "Forecasting", icon: LineChart },
  { key: "models", label: "Model Lab", icon: BrainCircuit },
  { key: "sentiment", label: "Sentiment Analysis", icon: Radar },
  { key: "portfolio", label: "Portfolio", icon: PieChart },
  { key: "backtesting", label: "Backtesting", icon: Activity },
  { key: "risk", label: "Risk Analysis", icon: ShieldAlert },
  { key: "leaderboard", label: "Leaderboard", icon: Medal },
  { key: "settings", label: "Settings", icon: Settings }
] as const;

export function Sidebar({ active, onChange }: { active: NavKey; onChange: (value: NavKey) => void }) {
  return (
    <aside className="terminal-sidebar">
      <div className="px-3 py-3">
        <p className="terminal-kicker px-2">Terminal Modules</p>
        <div className="mt-3 grid gap-1">
          {nav.map((item) => {
            const Icon = item.icon;
            return (
              <Button
                key={item.key}
                variant="ghost"
                className={cn(
                  "h-10 justify-start rounded-lg px-3 text-left font-semibold",
                  active === item.key && "border-terminal-accent/40 bg-terminal-accent/10 text-terminal-text"
                )}
                onClick={() => onChange(item.key)}
              >
                <Icon className="h-4 w-4" />
                <span className="truncate">{item.label}</span>
              </Button>
            );
          })}
        </div>
      </div>
      <div className="mx-3 mb-3 rounded-xl border border-terminal-accent/20 bg-terminal-accent/10 p-3">
        <div className="flex items-center gap-2 text-terminal-accent">
          <Gauge className="h-4 w-4" />
          <span className="font-outfit text-xs font-bold">AI Quant Engine</span>
        </div>
        <p className="mt-2 text-[11px] leading-relaxed text-terminal-muted">
          Live probabilistic inference, risk analytics, market-derived sentiment, and institutional backtesting.
        </p>
      </div>
    </aside>
  );
}
