import { Activity, BarChart3, BrainCircuit, DollarSign, Gauge, ShieldAlert, TrendingUp, Waves } from "lucide-react";

import { ConfidenceChart } from "@/charts/ConfidenceChart";
import { FeatureImportanceChart } from "@/charts/FeatureImportanceChart";
import { ForecastChart } from "@/charts/ForecastChart";
import { GaugeChart } from "@/charts/GaugeChart";
import { LiquidationHeatmap } from "@/charts/Heatmap";
import { MetricCard } from "@/components/ui/MetricCard";
import { Panel, PanelHeader } from "@/components/ui/Panel";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { useTerminalData } from "@/hooks/useTerminalData";
import { compactMoney, money, number, percent, signedPercent } from "@/utils/format";

export default function Dashboard() {
  const { data, loading } = useTerminalData();
  if (!data || loading) {
    return <div className="terminal-panel h-[520px] animate-pulse" />;
  }

  const signalTone = data.market.ai_recommendation === "BUY" ? "success" : data.market.ai_recommendation === "SELL" ? "danger" : "warning";
  const forecast30 = data.prediction.forecast.find((point) => point.horizon === 30) ?? data.prediction.forecast.at(-1);

  return (
    <div className="space-y-3">
      <section className="hero-grid">
        <Panel className="hero-panel">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <p className="terminal-kicker">Current Market</p>
              <h1 className="mt-2 font-outfit text-3xl font-extrabold text-terminal-text md:text-5xl">
                {data.symbol} Intelligence Desk
              </h1>
              <p className="mt-3 max-w-3xl text-sm leading-6 text-terminal-muted">{data.ai_insight.narrative}</p>
            </div>
            <div className="recommendation-card">
              <span>AI Recommendation</span>
              <strong className={signalTone === "success" ? "text-terminal-success" : signalTone === "danger" ? "text-terminal-danger" : "text-terminal-warning"}>
                {data.market.ai_recommendation}
              </strong>
              <em>{number(data.market.confidence, 0)}% Confidence</em>
            </div>
          </div>
          <div className="mt-6 grid gap-3 md:grid-cols-3 xl:grid-cols-6">
            <MetricCard label={`${data.symbol} Price`} value={money(data.market.price)} sub={signedPercent(data.market.change_24h)} icon={DollarSign} tone={data.market.change_24h >= 0 ? "success" : "danger"} />
            <MetricCard label="24H Volume" value={compactMoney(data.market.volume_24h)} icon={Activity} />
            <MetricCard label="Market Cap" value={compactMoney(data.market.market_cap)} icon={BarChart3} />
            <MetricCard label="Dominance" value={percent(data.market.dominance)} icon={Waves} />
            <MetricCard label="Market Sentiment" value={number(data.market.market_sentiment_score, 0)} icon={Gauge} tone="warning" />
            <MetricCard label="Target 30D" value={money(forecast30?.predicted_close ?? 0)} icon={TrendingUp} tone="accent" />
          </div>
        </Panel>
      </section>

      <section className="dashboard-grid">
        <Panel className="xl:col-span-8">
          <PanelHeader
            title="Forecasting Chart"
            kicker="Historical Price / AI Forecast / Confidence Interval"
            action={<StatusBadge tone="accent">{data.prediction.model_status}</StatusBadge>}
          />
          <ForecastChart prediction={data.prediction} />
        </Panel>

        <Panel className="xl:col-span-4">
          <PanelHeader title="Market Sentiment" kicker="Realtime Sentiment Gauge" />
          <GaugeChart value={data.prediction.sentiment.score} title={data.prediction.sentiment.label} />
          <div className="derived-list">
            <p className="terminal-kicker">Sentiment derived from</p>
            {data.prediction.sentiment.derived_from.map((source) => (
              <div key={source} className="derived-row">
                <span>✓</span>
                <strong>{source}</strong>
              </div>
            ))}
          </div>
        </Panel>

        <Panel className="xl:col-span-4">
          <PanelHeader title="Multi-Horizon Forecast" kicker="1D / 3D / 7D / 30D / 90D / 180D / 365D" />
          <div className="grid gap-2">
            {data.prediction.forecast.map((point) => (
              <div key={point.horizon} className="horizon-row">
                <span>{point.horizon} Day</span>
                <strong>{money(point.predicted_close)}</strong>
                <em>
                  {money(point.lower_95)} - {money(point.upper_95)}
                </em>
              </div>
            ))}
          </div>
        </Panel>

        <Panel className="xl:col-span-4">
          <PanelHeader title="Confidence Visualization" kicker="Prediction Band Width" />
          <ConfidenceChart forecast={data.prediction.forecast} />
        </Panel>

        <Panel className="xl:col-span-4">
          <PanelHeader title="AI Insight Panel" kicker={data.ai_insight.headline} />
          <div className="insight-box">
            <BrainCircuit className="h-5 w-5 text-terminal-accent" />
            <p>{data.ai_insight.narrative}</p>
          </div>
          <div className="mt-3 grid grid-cols-3 gap-2">
            <MetricCard label="Bull Prob." value={`${number(data.ai_insight.probability, 0)}%`} mono={false} tone="accent" />
            <MetricCard label="Risk" value={data.ai_insight.risk_level} mono={false} tone="warning" />
            <MetricCard label="Target" value={money(data.ai_insight.target_30d)} tone="success" />
          </div>
        </Panel>

        <Panel className="xl:col-span-4">
          <PanelHeader title="Market Intelligence" kicker="Whale / Exchange / Derivatives" />
          <div className="grid gap-2">
            <MetricCard label="Whale Activity" value={percent(data.intelligence.whale_activity)} icon={Waves} tone="accent" />
            <MetricCard label="Open Interest" value={compactMoney(data.intelligence.open_interest)} icon={Activity} />
            <MetricCard label="Funding Rate" value={signedPercent(data.intelligence.funding_rate, 3)} icon={TrendingUp} tone={data.intelligence.funding_rate >= 0 ? "success" : "danger"} />
          </div>
        </Panel>

        <Panel className="xl:col-span-4">
          <PanelHeader title="Liquidation Heatmap" kicker={data.intelligence.market_structure} />
          <LiquidationHeatmap heatmap={data.intelligence.liquidation_heatmap} />
        </Panel>

        <Panel className="xl:col-span-4">
          <PanelHeader title="Risk Meter" kicker="Volatility / VaR / CVaR" />
          <GaugeChart value={data.risk.risk_score} title="Risk" />
          <div className="grid grid-cols-3 gap-2">
            <MetricCard label="Vol" value={percent(data.risk.volatility)} icon={ShieldAlert} tone="warning" />
            <MetricCard label="VaR" value={percent(data.risk.var_95)} tone="danger" />
            <MetricCard label="CVaR" value={percent(data.risk.cvar_95)} tone="danger" />
          </div>
        </Panel>

        <Panel className="xl:col-span-8">
          <PanelHeader title="Explainable Prediction Dashboard" kicker={data.prediction.explainability.method} />
          <FeatureImportanceChart prediction={data.prediction} />
        </Panel>
      </section>
    </div>
  );
}
