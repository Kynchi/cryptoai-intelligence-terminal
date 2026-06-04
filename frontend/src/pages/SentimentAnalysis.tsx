import { GaugeChart } from "@/charts/GaugeChart";
import { MetricCard } from "@/components/ui/MetricCard";
import { Panel, PanelHeader } from "@/components/ui/Panel";
import { useTerminalData } from "@/hooks/useTerminalData";
import { number } from "@/utils/format";

export default function SentimentAnalysis() {
  const { data } = useTerminalData();
  if (!data) return null;
  const sentiment = data.prediction.sentiment;
  return (
    <div className="dashboard-grid">
      <Panel className="xl:col-span-4">
        <PanelHeader title="Market Sentiment" kicker="Realtime Sentiment Gauge" />
        <GaugeChart value={sentiment.score} title={sentiment.label} />
      </Panel>
      <Panel className="xl:col-span-8">
        <PanelHeader title="Internal Market-Derived Sentiment" kicker="No external APIs or credentials required" />
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          {Object.entries(sentiment.components).map(([name, score]) => (
            <MetricCard
              key={name}
              label={name.replaceAll("_", " ")}
              value={`${number(score, 0)}%`}
              sub="Internal market signal"
              tone={score > 55 ? "success" : score < 45 ? "danger" : "warning"}
            />
          ))}
        </div>
        <div className="mt-4 derived-list">
          <p className="terminal-kicker">Sentiment derived from</p>
          {sentiment.derived_from.map((item) => (
            <div key={item} className="derived-row">
              <span>✓</span>
              <strong>{item}</strong>
            </div>
          ))}
        </div>
      </Panel>
    </div>
  );
}
