import { MonteCarloChart } from "@/charts/MonteCarloChart";
import { GaugeChart } from "@/charts/GaugeChart";
import { MetricCard } from "@/components/ui/MetricCard";
import { Panel, PanelHeader } from "@/components/ui/Panel";
import { useTerminalData } from "@/hooks/useTerminalData";
import { percent } from "@/utils/format";

export default function RiskAnalysis() {
  const { data } = useTerminalData();
  if (!data) return null;
  return (
    <div className="dashboard-grid">
      <Panel className="xl:col-span-4">
        <PanelHeader title="Risk Meter" kicker="Institutional risk score" />
        <GaugeChart value={data.risk.risk_score} title="Risk" />
        <div className="grid gap-2">
          <MetricCard label="Volatility" value={percent(data.risk.volatility)} tone="warning" />
          <MetricCard label="VaR 95%" value={percent(data.risk.var_95)} tone="danger" />
          <MetricCard label="CVaR 95%" value={percent(data.risk.cvar_95)} tone="danger" />
        </div>
      </Panel>
      <Panel className="xl:col-span-8">
        <PanelHeader title="Monte Carlo Simulation" kicker="30-day percentile cone" />
        <MonteCarloChart risk={data.risk} />
      </Panel>
    </div>
  );
}
