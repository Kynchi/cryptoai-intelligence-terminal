import ReactECharts from "echarts-for-react";

import { accent, baseChart } from "@/charts/chartTheme";
import type { PredictionPayload } from "@/models/terminal";

export function FeatureImportanceChart({ prediction }: { prediction: PredictionPayload }) {
  const items = prediction.explainability.feature_importance.slice(0, 10).reverse();
  const option = {
    ...baseChart,
    grid: { left: 110, right: 12, top: 12, bottom: 24 },
    xAxis: { ...baseChart.xAxis, type: "value" },
    yAxis: { ...baseChart.yAxis, type: "category", data: items.map((item) => item.feature) },
    series: [
      {
        type: "bar",
        barWidth: 8,
        itemStyle: { color: accent, borderRadius: [0, 5, 5, 0] },
        data: items.map((item) => item.importance)
      }
    ]
  };
  return <ReactECharts option={option} style={{ height: 270, width: "100%" }} />;
}
