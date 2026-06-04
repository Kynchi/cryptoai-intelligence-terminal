from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class BacktestResult:
    roi: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    win_rate: float
    max_drawdown: float
    profit_factor: float
    final_equity: float
    trades: int
    equity_curve: list[dict[str, float | str]]


class BacktestingEngine:
    def __init__(
        self,
        initial_cash: float = 10000,
        fee_rate: float = 0.001,
        buy_threshold: float = 0.015,
        sell_threshold: float = -0.015,
    ):
        self.initial_cash = initial_cash
        self.fee_rate = fee_rate
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold

    def run_signal_backtest(self, df: pd.DataFrame, lookahead: int = 7) -> BacktestResult:
        data = df.copy().reset_index(drop=True)
        if len(data) <= lookahead + 30:
            raise ValueError("Not enough rows for backtesting.")

        cash = self.initial_cash
        units = 0.0
        trades = 0
        winning_trades = 0
        trade_profits: list[float] = []
        last_buy_price = 0.0
        last_buy_equity = 0.0
        equity_curve: list[dict[str, float | str]] = []

        close = pd.to_numeric(data["Close"], errors="coerce")
        momentum = close.pct_change(7).fillna(0)
        volatility = close.pct_change().rolling(20).std().fillna(0)

        for idx in range(30, len(data) - lookahead):
            price = float(close.iloc[idx])
            expected_return = float(momentum.iloc[idx] - 0.35 * volatility.iloc[idx])

            if units == 0 and expected_return > self.buy_threshold:
                units = (cash * (1 - self.fee_rate)) / price
                cash = 0.0
                last_buy_price = price
                last_buy_equity = units * price
                trades += 1
            elif units > 0 and expected_return < self.sell_threshold:
                cash = units * price * (1 - self.fee_rate)
                trade_profits.append(cash - last_buy_equity)
                if price > last_buy_price:
                    winning_trades += 1
                units = 0.0
                trades += 1

            equity = cash + units * price
            equity_curve.append(
                {
                    "timestamp": str(data["Timestamp"].iloc[idx]),
                    "equity": float(equity),
                    "close": price,
                    "position": float(units),
                }
            )

        if units > 0:
            final_price = float(close.iloc[-1])
            cash = units * final_price * (1 - self.fee_rate)
            trade_profits.append(cash - last_buy_equity)
            if final_price > last_buy_price:
                winning_trades += 1
            trades += 1

        returns = pd.Series([point["equity"] for point in equity_curve], dtype=float).pct_change().dropna()
        sharpe = 0.0
        if len(returns) and returns.std() > 0:
            sharpe = float(np.sqrt(252) * returns.mean() / returns.std())
        downside_returns = returns[returns < 0]
        sortino = 0.0
        if len(downside_returns) and downside_returns.std() > 0:
            sortino = float(np.sqrt(252) * returns.mean() / downside_returns.std())

        equities = pd.Series([point["equity"] for point in equity_curve], dtype=float)
        drawdown = (equities / equities.cummax() - 1).min() if len(equities) else 0.0
        final_equity = float(cash)
        roi = (final_equity - self.initial_cash) / self.initial_cash
        calmar = float(roi / abs(drawdown)) if drawdown < 0 else 0.0
        gross_profit = sum(profit for profit in trade_profits if profit > 0)
        gross_loss = abs(sum(profit for profit in trade_profits if profit < 0))
        profit_factor = float(gross_profit / gross_loss) if gross_loss > 0 else float(gross_profit > 0)
        sell_trades = max(1, trades // 2)
        win_rate = winning_trades / sell_trades

        return BacktestResult(
            roi=float(roi),
            sharpe_ratio=float(sharpe),
            sortino_ratio=float(sortino),
            calmar_ratio=float(calmar),
            win_rate=float(win_rate),
            max_drawdown=float(drawdown),
            profit_factor=profit_factor,
            final_equity=final_equity,
            trades=trades,
            equity_curve=equity_curve,
        )
