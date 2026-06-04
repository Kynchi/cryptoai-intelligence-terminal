import ReactECharts from "echarts-for-react";

import { baseChart } from "@/charts/chartTheme";
import type { RiskSnapshot } from "@/models/terminal";

export function MonteCarloChart({ risk }: { risk: RiskSnapshot }) {
  const option = {
    ...baseChart,
    grid: { left: 48, right: 18, top: 18, bottom: 34 },
    xAxis: { ...baseChart.xAxis, type: "category", data: Array.from({ length: 30 }, (_, index) => `D${index + 1}`) },
    yAxis: { ...baseChart.yAxis, type: "value", scale: true },
    series: risk.monte_carlo.map((path) => ({
      name: `P${path.percentile}`,
      type: "line",
      smooth: true,
      showSymbol: false,
      lineStyle: {
        width: path.percentile === 50 ? 3 : 1,
        color: path.percentile === 50 ? "#63B3ED" : "rgba(99,179,237,0.38)"
      },
      data: path.values
    }))
  };
  return <ReactECharts option={option} style={{ height: 290, width: "100%" }} />;
}
