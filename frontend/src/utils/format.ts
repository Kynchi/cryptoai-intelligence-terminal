export function money(value: number, maximumFractionDigits = 2) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits
  }).format(value);
}

export function compactMoney(value: number) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    notation: "compact",
    maximumFractionDigits: 2
  }).format(value);
}

export function percent(value: number, digits = 2) {
  return `${(value * 100).toFixed(digits)}%`;
}

export function number(value: number, digits = 2) {
  return new Intl.NumberFormat("en-US", { maximumFractionDigits: digits }).format(value);
}

export function signedPercent(value: number, digits = 2) {
  const prefix = value > 0 ? "+" : "";
  return `${prefix}${percent(value, digits)}`;
}
