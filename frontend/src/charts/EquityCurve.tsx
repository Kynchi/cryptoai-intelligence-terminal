import ReactECharts from "echarts-for-react";

import { baseChart, warning } from "@/charts/chartTheme";
import type { BacktestPayload } from "@/models/terminal";

export function EquityCurve({ backtest, height = 280 }: { backtest: BacktestPayload; height?: number }) {
  const curve = backtest.equity_curve.slice(-260);
  const option = {
    ...baseChart,
    grid: { left: 48, right: 18, top: 18, bottom: 34 },
    xAxis: { ...baseChart.xAxis, type: "category", data: curve.map((point) => point.timestamp.slice(0, 10)) },
    yAxis: { ...baseChart.yAxis, type: "value", scale: true },
    series: [
      {
        type: "line",
        smooth: true,
        showSymbol: false,
        lineStyle: { color: warning, width: 2 },
        areaStyle: { color: "rgba(246,201,14,0.08)" },
        data: curve.map((point) => point.equity)
      }
    ]
  };
  return <ReactECharts option={option} style={{ height, width: "100%" }} />;
}
