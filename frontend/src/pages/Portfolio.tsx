import { AllocationDonut } from "@/charts/AllocationDonut";
import { MetricCard } from "@/components/ui/MetricCard";
import { Panel, PanelHeader } from "@/components/ui/Panel";
import { useTerminalData } from "@/hooks/useTerminalData";
import { money, percent, signedPercent } from "@/utils/format";

export default function Portfolio() {
  const { data } = useTerminalData();
  if (!data) return null;
  return (
    <div className="dashboard-grid">
      <Panel className="xl:col-span-4">
        <PanelHeader title="Portfolio Allocation" kicker="Risk-weighted crypto basket" />
        <AllocationDonut portfolio={data.portfolio} />
      </Panel>
      <Panel className="xl:col-span-8">
        <PanelHeader title="Portfolio Management" kicker="Value, allocation, exposure, PnL" />
        <div className="grid gap-3 md:grid-cols-4">
          <MetricCard label="Portfolio Value" value={money(data.portfolio.portfolio_value)} tone="accent" />
          <MetricCard label="PnL" value={money(data.portfolio.pnl)} tone={data.portfolio.pnl >= 0 ? "success" : "danger"} />
          <MetricCard label="Risk Exposure" value={percent(data.portfolio.risk_exposure)} tone="warning" />
          <MetricCard label="Assets" value={String(data.portfolio.asset_allocation.length)} />
        </div>
        <div className="mt-4 terminal-table-wrap">
          <table className="terminal-table">
            <thead>
              <tr><th>Asset</th><th>Weight</th><th>Value</th><th>Price</th><th>30D PnL</th><th>Risk Exposure</th></tr>
            </thead>
            <tbody>
              {data.portfolio.asset_allocation.map((asset) => (
                <tr key={asset.symbol}>
                  <td>{asset.symbol}</td>
                  <td>{percent(asset.weight)}</td>
                  <td>{money(asset.value)}</td>
                  <td>{money(asset.price, asset.symbol === "XRP" ? 4 : 2)}</td>
                  <td>{signedPercent(asset.pnl_30d)}</td>
                  <td>{percent(asset.risk_exposure)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>
    </div>
  );
}
