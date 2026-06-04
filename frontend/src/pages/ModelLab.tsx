import { Cpu } from "lucide-react";

import { Button } from "@/components/ui/Button";
import { MetricCard } from "@/components/ui/MetricCard";
import { Panel, PanelHeader } from "@/components/ui/Panel";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { useTerminalData } from "@/hooks/useTerminalData";
import { number } from "@/utils/format";

export default function ModelLab() {
  const { data, symbol } = useTerminalData();
  if (!data) return null;
  return (
    <div className="space-y-3">
      <Panel>
        <PanelHeader
          title="Model Comparison Lab"
          kicker="LSTM / GRU / CNN-LSTM / Transformer / N-BEATS / XGBoost / Random Forest / Prophet / Hybrid"
          action={<Button size="sm" variant="primary"><Cpu className="h-3.5 w-3.5" /> Train Selected</Button>}
        />
        <div className="grid gap-3 md:grid-cols-4">
          <MetricCard label="Active Symbol" value={symbol} mono={false} tone="accent" />
          <MetricCard label="Best Model" value={data.model_comparison[0]?.model ?? "N/A"} mono={false} tone="success" />
          <MetricCard label="Best Accuracy" value={`${number(data.model_comparison[0]?.accuracy ?? 0)}%`} tone="success" />
          <MetricCard label="Candidates" value={String(data.model_comparison.length)} tone="accent" />
        </div>
      </Panel>
      <Panel>
        <div className="terminal-table-wrap">
          <table className="terminal-table">
            <thead>
              <tr>
                <th>Rank</th>
                <th>Model</th>
                <th>RMSE</th>
                <th>MAE</th>
                <th>MAPE</th>
                <th>R2</th>
                <th>Training Time</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {data.model_comparison.map((row, index) => (
                <tr key={row.model}>
                  <td>#{index + 1}</td>
                  <td className="font-semibold text-terminal-text">{row.model}</td>
                  <td>{number(row.rmse)}</td>
                  <td>{number(row.mae)}</td>
                  <td>{number(row.mape)}%</td>
                  <td>{number(row.r2, 3)}</td>
                  <td>{row.training_time}</td>
                  <td><StatusBadge tone={row.status === "trained" ? "success" : "warning"}>{row.status}</StatusBadge></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>
    </div>
  );
}
