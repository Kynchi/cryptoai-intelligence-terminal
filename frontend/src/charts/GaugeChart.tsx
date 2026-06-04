import ReactECharts from "echarts-for-react";

export function GaugeChart({
  value,
  title,
  formatter = "{value}%"
}: {
  value: number;
  title: string;
  formatter?: string;
}) {
  const option = {
    series: [
      {
        type: "gauge",
        startAngle: 210,
        endAngle: -30,
        min: 0,
        max: 100,
        radius: "96%",
        progress: { show: true, width: 10, itemStyle: { color: "#63B3ED" } },
        axisLine: { lineStyle: { width: 10, color: [[1, "#1A2338"]] } },
        axisTick: { show: false },
        splitLine: { show: false },
        axisLabel: { show: false },
        pointer: { width: 3, length: "58%", itemStyle: { color: "#E8EDF5" } },
        anchor: { show: true, size: 8, itemStyle: { color: "#E8EDF5" } },
        title: { offsetCenter: [0, "64%"], color: "#8B98AE", fontSize: 10 },
        detail: {
          valueAnimation: true,
          offsetCenter: [0, "28%"],
          color: "#E8EDF5",
          fontFamily: "DM Mono",
          formatter
        },
        data: [{ value, name: title }]
      }
    ]
  };

  return <ReactECharts option={option} style={{ height: 190, width: "100%" }} />;
}
