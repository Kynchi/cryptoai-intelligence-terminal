import { DatabaseZap, RefreshCw } from "lucide-react";

import { CryptoAILogo } from "@/assets/CryptoAILogo";
import { Button } from "@/components/ui/Button";
import type { TerminalPayload } from "@/models/terminal";
import { cn } from "@/utils/cn";
import { money, signedPercent } from "@/utils/format";

const symbols = ["BTC", "ETH", "SOL", "XRP"];

export function TopNavigation({
  symbol,
  setSymbol,
  data,
  loading,
  onRefresh,
  onUpdate
}: {
  symbol: string;
  setSymbol: (symbol: string) => void;
  data: TerminalPayload | null;
  loading: boolean;
  onRefresh: () => Promise<void>;
  onUpdate: () => Promise<void>;
}) {
  const allocation = data?.portfolio.asset_allocation ?? [];
  return (
    <header className="terminal-topbar">
      <div className="flex min-w-0 items-center gap-3">
        <CryptoAILogo />
        <div className="min-w-0">
          <div className="brand-gradient truncate font-outfit text-base font-extrabold">CryptoAI</div>
          <div className="terminal-kicker truncate">Intelligence Terminal</div>
        </div>
      </div>

      <div className="ticker-strip">
        {symbols.map((item) => {
          const row = allocation.find((entry) => entry.symbol === item);
          const change = row?.pnl_30d ?? 0;
          return (
            <button
              key={item}
              onClick={() => setSymbol(item)}
              className={cn("ticker-chip", symbol === item && "ticker-chip-active")}
            >
              <span>{item}</span>
              <strong>{money(row?.price ?? (item === symbol ? data?.market.price ?? 0 : 0), item === "XRP" ? 4 : 2)}</strong>
              <em className={change >= 0 ? "text-terminal-success" : "text-terminal-danger"}>
                {signedPercent(change)}
              </em>
            </button>
          );
        })}
      </div>

      <div className="flex items-center gap-2">
        <span className="live-pill">
          <span className="live-dot" />
          LIVE
        </span>
        <Button size="icon" title="Refresh terminal" onClick={() => void onRefresh()} disabled={loading}>
          <RefreshCw className={cn("h-4 w-4", loading && "animate-spin")} />
        </Button>
        <Button size="icon" title="Realtime dataset update" onClick={() => void onUpdate()}>
          <DatabaseZap className="h-4 w-4" />
        </Button>
      </div>
    </header>
  );
}
