import ReactECharts from "echarts-for-react";

import type { PortfolioSnapshot } from "@/models/terminal";

export function AllocationDonut({ portfolio }: { portfolio: PortfolioSnapshot }) {
  const option = {
    tooltip: { trigger: "item" },
    legend: { bottom: 0, textStyle: { color: "#8B98AE" } },
    series: [
      {
        type: "pie",
        radius: ["52%", "78%"],
        center: ["50%", "44%"],
        itemStyle: { borderColor: "#0F1520", borderWidth: 2 },
        label: { color: "#E8EDF5", fontFamily: "DM Mono" },
        data: portfolio.asset_allocation.map((asset) => ({
          name: asset.symbol,
          value: asset.weight
        })),
        color: ["#F7931A", "#627EEA", "#9945FF", "#00AAE4"]
      }
    ]
  };
  return <ReactECharts option={option} style={{ height: 300, width: "100%" }} />;
}
