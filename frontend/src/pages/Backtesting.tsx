import { EquityCurve } from "@/charts/EquityCurve";
import { MetricCard } from "@/components/ui/MetricCard";
import { Panel, PanelHeader } from "@/components/ui/Panel";
import { useTerminalData } from "@/hooks/useTerminalData";
import { money, number, percent } from "@/utils/format";

export default function Backtesting() {
  const { data } = useTerminalData();
  if (!data) return null;
  return (
    <div className="space-y-3">
      <Panel>
        <PanelHeader title="Backtesting Module" kicker="ROI, Sharpe, Sortino, Calmar, Win Rate, Drawdown, Profit Factor" />
        <div className="grid gap-3 md:grid-cols-4 xl:grid-cols-7">
          <MetricCard label="Total Return" value={percent(data.backtest.roi)} tone={data.backtest.roi >= 0 ? "success" : "danger"} />
          <MetricCard label="Sharpe" value={number(data.backtest.sharpe_ratio)} tone="accent" />
          <MetricCard label="Sortino" value={number(data.backtest.sortino_ratio)} tone="accent" />
          <MetricCard label="Calmar" value={number(data.backtest.calmar_ratio)} tone="warning" />
          <MetricCard label="Win Rate" value={percent(data.backtest.win_rate)} />
          <MetricCard label="Max Drawdown" value={percent(data.backtest.max_drawdown)} tone="danger" />
          <MetricCard label="Profit Factor" value={number(data.backtest.profit_factor)} tone="success" />
        </div>
      </Panel>
      <Panel>
        <PanelHeader title="Equity Curve" kicker={`Final Equity ${money(data.backtest.final_equity)} | ${data.backtest.trades} trades`} />
        <EquityCurve backtest={data.backtest} height={460} />
      </Panel>
    </div>
  );
}
