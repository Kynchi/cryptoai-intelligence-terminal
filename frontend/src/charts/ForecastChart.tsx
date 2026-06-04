import ReactECharts from "echarts-for-react";

import { accent, baseChart, danger, success } from "@/charts/chartTheme";
import type { PredictionPayload } from "@/models/terminal";

export function ForecastChart({ prediction, height = 430 }: { prediction: PredictionPayload; height?: number }) {
  const history = prediction.historical.slice(-150);
  const lastDate = new Date(history[history.length - 1]?.Timestamp ?? Date.now());
  const forecastDates = prediction.forecast.map((point) => {
    const next = new Date(lastDate);
    next.setDate(next.getDate() + point.horizon);
    return next.toISOString().slice(0, 10);
  });
  const historyDates = history.map((row) => row.Timestamp.slice(0, 10));
  const forecastAxis = [...historyDates, ...forecastDates];
  const prefix = new Array(historyDates.length - 1).fill(null);

  const option = {
    ...baseChart,
    legend: {
      top: 0,
      right: 8,
      textStyle: { color: "#8B98AE" },
      data: ["Historical Price", "AI Forecast", "95% Prediction Band"]
    },
    xAxis: {
      ...baseChart.xAxis,
      type: "category",
      data: forecastAxis,
      boundaryGap: false
    },
    yAxis: { ...baseChart.yAxis, type: "value", scale: true },
    dataZoom: [{ type: "inside" }],
    series: [
      {
        name: "Historical Price",
        type: "line",
        smooth: true,
        showSymbol: false,
        lineStyle: { color: success, width: 2 },
        areaStyle: { color: "rgba(72,187,120,0.05)" },
        data: history.map((row) => row.Close)
      },
      {
        name: "95% Prediction Band",
        type: "line",
        symbol: "none",
        lineStyle: { opacity: 0 },
        stack: "confidence",
        data: [...prefix, history[history.length - 1]?.Close, ...prediction.forecast.map((point) => point.lower_95)]
      },
      {
        name: "95% Prediction Band",
        type: "line",
        symbol: "none",
        lineStyle: { opacity: 0 },
        areaStyle: { color: "rgba(99,179,237,0.16)" },
        stack: "confidence",
        data: [
          ...prefix,
          0,
          ...prediction.forecast.map((point) => Math.max(point.upper_95 - point.lower_95, 0))
        ]
      },
      {
        name: "AI Forecast",
        type: "line",
        smooth: true,
        symbol: "circle",
        symbolSize: 7,
        lineStyle: { color: accent, width: 3, type: "dashed" },
        itemStyle: { color: accent },
        data: [...prefix, history[history.length - 1]?.Close, ...prediction.forecast.map((point) => point.predicted_close)]
      },
      {
        name: "Risk Marker",
        type: "scatter",
        symbolSize: 8,
        itemStyle: { color: danger },
        data: []
      }
    ]
  };

  return <ReactECharts option={option} style={{ height, width: "100%" }} notMerge lazyUpdate />;
}
