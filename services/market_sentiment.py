from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd


@dataclass
class MarketSentimentSnapshot:
    symbol: str
    score: float
    label: str
    normalized_score: float
    derived_from: list[str] = field(
        default_factory=lambda: ["Price Action", "Volume Analysis", "RSI", "MACD", "EMA Trend"]
    )
    components: dict[str, float] = field(default_factory=dict)


class MarketSentimentService:
    """Market-derived sentiment with no external APIs or credentials."""

    def snapshot(self, symbol: str, df: pd.DataFrame) -> MarketSentimentSnapshot:
        numeric = df.copy()
        for column in ["Close", "Volume", "RSI_14", "MACD_hist", "EMA_50", "EMA_200"]:
            if column in numeric.columns:
                numeric[column] = pd.to_numeric(numeric[column], errors="coerce")

        close = numeric["Close"].ffill().bfill()
        volume = numeric["Volume"].ffill().bfill()
        current_price = float(close.iloc[-1])
        previous_price = float(close.iloc[-2]) if len(close) > 1 else current_price
        price_momentum = (current_price - previous_price) / max(abs(previous_price), 1e-9)

        volume_avg = float(volume.tail(min(20, len(volume))).mean())
        volume_momentum = (float(volume.iloc[-1]) - volume_avg) / max(abs(volume_avg), 1e-9)

        rsi_score = float(np.clip(numeric.get("RSI_14", pd.Series([50])).iloc[-1], 0, 100))
        macd_hist = float(numeric.get("MACD_hist", pd.Series([0])).iloc[-1])
        macd_score = _bounded_score(macd_hist / max(abs(current_price), 1e-9), scale=120)
        price_score = _bounded_score(price_momentum, scale=80)
        volume_score = _bounded_score(volume_momentum, scale=2.2)

        ema_50 = float(numeric.get("EMA_50", close).iloc[-1])
        ema_200 = float(numeric.get("EMA_200", close).iloc[-1])
        ema_trend_score = _bounded_score((ema_50 - ema_200) / max(abs(ema_200), 1e-9), scale=30)

        raw_score = (
            0.30 * rsi_score
            + 0.30 * macd_score
            + 0.20 * volume_score
            + 0.20 * price_score
        )
        score = float(np.clip(0.85 * raw_score + 0.15 * ema_trend_score, 0, 100))
        return MarketSentimentSnapshot(
            symbol=symbol.upper(),
            score=score,
            label=_label(score),
            normalized_score=(score - 50) / 50,
            components={
                "rsi": rsi_score,
                "macd": macd_score,
                "volume_momentum": volume_score,
                "price_momentum": price_score,
                "ema_trend": ema_trend_score,
            },
        )


def _bounded_score(value: float, scale: float) -> float:
    return float(np.clip(50 + 50 * np.tanh(value * scale), 0, 100))


def _label(score: float) -> str:
    if score <= 30:
        return "Extreme Fear"
    if score <= 45:
        return "Bearish"
    if score <= 55:
        return "Neutral"
    if score <= 70:
        return "Bullish"
    return "Extreme Greed"
