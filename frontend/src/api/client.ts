import type { TerminalPayload } from "@/models/terminal";

const cache = new Map<string, { timestamp: number; data: unknown }>();
const CACHE_TTL = 30_000;

async function request<T>(path: string, init?: RequestInit, useCache = true): Promise<T> {
  const key = `${path}:${init?.body ?? ""}`;
  const cached = cache.get(key);
  if (useCache && cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return cached.data as T;
  }

  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...init
  });
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.detail || response.statusText);
  }
  const data = (await response.json()) as T;
  cache.set(key, { timestamp: Date.now(), data });
  return data;
}

export const api = {
  terminal(symbol: string) {
    return request<TerminalPayload>(`/terminal?symbol=${symbol}`);
  },
  realtime(symbol: string) {
    cache.clear();
    return request<{ updates: Array<{ message: string }> }>(
      "/realtime",
      {
        method: "POST",
        body: JSON.stringify({ symbols: [symbol], retrain: false })
      },
      false
    );
  },
  train(symbol: string, modelName: string) {
    cache.clear();
    return request(
      "/train",
      {
        method: "POST",
        body: JSON.stringify({
          symbol,
          model_name: modelName,
          overrides: { epochs: 20, verbose: 0 }
        })
      },
      false
    );
  },
  clearCache() {
    cache.clear();
  }
};
