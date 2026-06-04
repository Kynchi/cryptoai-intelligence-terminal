export const chartText = "#8B98AE";
export const chartGrid = "rgba(255,255,255,0.055)";
export const accent = "#63B3ED";
export const success = "#48BB78";
export const danger = "#FC8181";
export const warning = "#F6C90E";

export const baseChart = {
  backgroundColor: "transparent",
  textStyle: {
    fontFamily: "Inter, sans-serif",
    color: chartText
  },
  grid: {
    left: 42,
    right: 20,
    top: 34,
    bottom: 36
  },
  tooltip: {
    trigger: "axis",
    backgroundColor: "#0F1520",
    borderColor: "rgba(255,255,255,0.12)",
    textStyle: { color: "#E8EDF5", fontFamily: "DM Mono, monospace" }
  },
  xAxis: {
    axisLine: { lineStyle: { color: chartGrid } },
    axisTick: { show: false },
    axisLabel: { color: chartText, fontFamily: "DM Mono, monospace" },
    splitLine: { lineStyle: { color: chartGrid } }
  },
  yAxis: {
    axisLine: { lineStyle: { color: chartGrid } },
    axisTick: { show: false },
    axisLabel: { color: chartText, fontFamily: "DM Mono, monospace" },
    splitLine: { lineStyle: { color: chartGrid } }
  }
};
