import ReactECharts from "echarts-for-react";

import { accent, baseChart, warning } from "@/charts/chartTheme";
import type { ForecastPoint } from "@/models/terminal";

export function ConfidenceChart({ forecast }: { forecast: ForecastPoint[] }) {
  const option = {
    ...baseChart,
    grid: { left: 42, right: 14, top: 18, bottom: 34 },
    xAxis: { ...baseChart.xAxis, type: "category", data: forecast.map((point) => `${point.horizon}D`) },
    yAxis: { ...baseChart.yAxis, type: "value" },
    series: [
      {
        name: "80%",
        type: "bar",
        barWidth: 12,
        itemStyle: { color: warning, borderRadius: [4, 4, 0, 0] },
        data: forecast.map((point) => point.upper_80 - point.lower_80)
      },
      {
        name: "95%",
        type: "bar",
        barWidth: 12,
        itemStyle: { color: accent, borderRadius: [4, 4, 0, 0] },
        data: forecast.map((point) => point.upper_95 - point.lower_95)
      }
    ]
  };
  return <ReactECharts option={option} style={{ height: 260, width: "100%" }} />;
}
