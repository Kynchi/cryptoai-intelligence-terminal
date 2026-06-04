import type { MarketIntelligence } from "@/models/terminal";
import { money } from "@/utils/format";

export function LiquidationHeatmap({ heatmap }: { heatmap: MarketIntelligence["liquidation_heatmap"] }) {
  return (
    <div className="heatmap-grid">
      {heatmap.map((cell) => (
        <div
          key={cell.bucket}
          title={`${money(cell.price)} ${cell.side}`}
          className={cell.side === "long" ? "heat-cell-long" : "heat-cell-short"}
          style={{ opacity: 0.35 + cell.intensity * 0.65 }}
        />
      ))}
    </div>
  );
}
