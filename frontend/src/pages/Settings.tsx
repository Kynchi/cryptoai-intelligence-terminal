import { Button } from "@/components/ui/Button";
import { Panel, PanelHeader } from "@/components/ui/Panel";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { useTerminalData } from "@/hooks/useTerminalData";

export default function Settings() {
  const { symbol, updateData, refresh } = useTerminalData();
  return (
    <div className="dashboard-grid">
      <Panel className="xl:col-span-6">
        <PanelHeader title="Terminal Settings" kicker="Runtime controls" />
        <div className="grid gap-3">
          <div className="settings-row">
            <div>
              <strong>Active Symbol</strong>
              <p>{symbol}</p>
            </div>
            <StatusBadge tone="accent">Realtime</StatusBadge>
          </div>
          <div className="settings-row">
            <div>
              <strong>API Cache</strong>
              <p>30 second frontend cache for terminal payloads</p>
            </div>
            <Button onClick={() => void refresh()}>Refresh</Button>
          </div>
          <div className="settings-row">
            <div>
              <strong>Dataset Update</strong>
              <p>Runs CoinMarketCap ingestion when API credentials are configured</p>
            </div>
            <Button variant="primary" onClick={() => void updateData()}>Update</Button>
          </div>
        </div>
      </Panel>
      <Panel className="xl:col-span-6">
        <PanelHeader title="Design System" kicker="CryptoAI institutional theme" />
        <div className="palette-grid">
          {["#080B12", "#0F1520", "#141C2E", "#63B3ED", "#E8EDF5", "#48BB78", "#FC8181", "#F6C90E"].map((color) => (
            <div key={color} className="palette-chip"><span style={{ background: color }} />{color}</div>
          ))}
        </div>
      </Panel>
    </div>
  );
}
