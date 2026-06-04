import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react";

import { api } from "@/api/client";
import type { TerminalPayload } from "@/models/terminal";

interface TerminalDataContextValue {
  symbol: string;
  setSymbol: (symbol: string) => void;
  data: TerminalPayload | null;
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
  updateData: () => Promise<void>;
}

const TerminalDataContext = createContext<TerminalDataContextValue | null>(null);

export function useTerminalData(): TerminalDataContextValue {
  const context = useContext(TerminalDataContext);
  if (!context) {
    throw new Error("useTerminalData must be used within TerminalDataProvider.");
  }
  return context;
}

export function TerminalDataProvider({ children }: { children: ReactNode }) {
  const [symbol, setSymbol] = useState("BTC");
  const [data, setData] = useState<TerminalPayload | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const payload = await api.terminal(symbol);
      setData(payload);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown API error.");
    } finally {
      setLoading(false);
    }
  }, [symbol]);

  const updateData = useCallback(async () => {
    await api.realtime(symbol);
    api.clearCache();
    await refresh();
  }, [refresh, symbol]);

  useEffect(() => {
    void refresh();
    const timer = window.setInterval(() => void refresh(), 60_000);
    return () => window.clearInterval(timer);
  }, [refresh]);

  const value = useMemo(
    () => ({ symbol, setSymbol, data, loading, error, refresh, updateData }),
    [data, error, loading, refresh, symbol, updateData]
  );

  return <TerminalDataContext.Provider value={value}>{children}</TerminalDataContext.Provider>;
}
