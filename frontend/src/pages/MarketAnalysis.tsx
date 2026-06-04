import { Activity, ArrowDownToLine, ArrowUpFromLine, Gauge, Waves } from "lucide-react";

import { LiquidationHeatmap } from "@/charts/Heatmap";
import { MetricCard } from "@/components/ui/MetricCard";
import { Panel, PanelHeader } from "@/components/ui/Panel";
import { useTerminalData } from "@/hooks/useTerminalData";
import { compactMoney, percent, signedPercent } from "@/utils/format";

export default function MarketAnalysis() {
  const { data } = useTerminalData();
  if (!data) return null;
  return (
    <div className="dashboard-grid">
      <Panel className="xl:col-span-8">
        <PanelHeader title="Market Intelligence" kicker="Whales, exchange flow, derivatives, and structure" />
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          <MetricCard label="Whale Activity" value={percent(data.intelligence.whale_activity)} icon={Waves} tone="accent" />
          <MetricCard label="Exchange Inflow" value={compactMoney(data.intelligence.exchange_inflow)} icon={ArrowDownToLine} tone="danger" />
          <MetricCard label="Exchange Outflow" value={compactMoney(data.intelligence.exchange_outflow)} icon={ArrowUpFromLine} tone="success" />
          <MetricCard label="Open Interest" value={compactMoney(data.intelligence.open_interest)} icon={Activity} />
          <MetricCard label="Funding Rate" value={signedPercent(data.intelligence.funding_rate, 3)} icon={Gauge} tone={data.intelligence.funding_rate >= 0 ? "success" : "danger"} />
          <MetricCard label="Market Structure" value={data.intelligence.market_structure} mono={false} tone="warning" />
          <MetricCard label="30D Momentum" value={signedPercent(data.intelligence.trend_analysis.momentum_30d)} tone="accent" />
          <MetricCard label="EMA200 Distance" value={signedPercent(data.intelligence.trend_analysis.ema200_distance)} tone="accent" />
        </div>
      </Panel>
      <Panel className="xl:col-span-4">
        <PanelHeader title="Liquidation Heatmap" kicker="Volatility-weighted local pressure map" />
        <LiquidationHeatmap heatmap={data.intelligence.liquidation_heatmap} />
      </Panel>
    </div>
  );
}
