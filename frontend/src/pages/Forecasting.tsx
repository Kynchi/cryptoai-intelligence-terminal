import { ForecastChart } from "@/charts/ForecastChart";
import { Panel, PanelHeader } from "@/components/ui/Panel";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { useTerminalData } from "@/hooks/useTerminalData";
import { money } from "@/utils/format";

export default function Forecasting() {
  const { data } = useTerminalData();
  if (!data) return null;
  return (
    <div className="space-y-3">
      <Panel>
        <PanelHeader
          title="Professional Forecasting Workbench"
          kicker="Historical price, AI forecast, confidence interval, prediction band"
          action={<StatusBadge tone="accent">{data.prediction.model_used}</StatusBadge>}
        />
        <ForecastChart prediction={data.prediction} height={560} />
      </Panel>
      <Panel>
        <PanelHeader title="Multi-Horizon Forecast Table" kicker="Institutional horizon ladder" />
        <div className="terminal-table-wrap">
          <table className="terminal-table">
            <thead>
              <tr>
                <th>Horizon</th>
                <th>Forecast</th>
                <th>80% Lower</th>
                <th>80% Upper</th>
                <th>95% Lower</th>
                <th>95% Upper</th>
              </tr>
            </thead>
            <tbody>
              {data.prediction.forecast.map((point) => (
                <tr key={point.horizon}>
                  <td>{point.horizon} Day</td>
                  <td>{money(point.predicted_close)}</td>
                  <td>{money(point.lower_80)}</td>
                  <td>{money(point.upper_80)}</td>
                  <td>{money(point.lower_95)}</td>
                  <td>{money(point.upper_95)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>
    </div>
  );
}
