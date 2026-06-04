import { Panel, PanelHeader } from "@/components/ui/Panel";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { useTerminalData } from "@/hooks/useTerminalData";
import { number } from "@/utils/format";

export default function Leaderboard() {
  const { data } = useTerminalData();
  if (!data) return null;
  return (
    <Panel>
      <PanelHeader title="Model Leaderboard" kicker="Kaggle-style model ranking" />
      <div className="terminal-table-wrap">
        <table className="terminal-table">
          <thead>
            <tr>
              <th>Rank</th>
              <th>Model</th>
              <th>Accuracy</th>
              <th>MAPE</th>
              <th>RMSE</th>
              <th>Last Training</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {data.model_comparison.map((row, index) => (
              <tr key={row.model}>
                <td className={index === 0 ? "text-terminal-warning" : ""}>#{index + 1}</td>
                <td className="font-semibold text-terminal-text">{row.model}</td>
                <td>{number(row.accuracy)}%</td>
                <td>{number(row.mape)}%</td>
                <td>{number(row.rmse)}</td>
                <td>{row.last_training}</td>
                <td><StatusBadge tone={row.status === "trained" ? "success" : "warning"}>{row.status}</StatusBadge></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Panel>
  );
}
