from __future__ import annotations

import numpy as np
import pandas as pd


OHLCV_COLUMNS = ["Open", "High", "Low", "Close", "Volume"]


def _series(df: pd.DataFrame, column: str) -> pd.Series:
    if column not in df.columns:
        raise ValueError(f"Required column '{column}' is missing from market data.")
    return pd.to_numeric(df[column], errors="coerce")


def rsi(close: pd.Series, window: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(window).mean()
    loss = (-delta.clip(upper=0)).rolling(window).mean()
    relative_strength = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + relative_strength))


def ema(close: pd.Series, span: int = 20) -> pd.Series:
    return close.ewm(span=span, adjust=False).mean()


def sma(close: pd.Series, window: int = 20) -> pd.Series:
    return close.rolling(window).mean()


def macd(close: pd.Series) -> pd.DataFrame:
    fast = close.ewm(span=12, adjust=False).mean()
    slow = close.ewm(span=26, adjust=False).mean()
    macd_line = fast - slow
    signal = macd_line.ewm(span=9, adjust=False).mean()
    histogram = macd_line - signal
    return pd.DataFrame(
        {
            "MACD": macd_line,
            "MACD_signal": signal,
            "MACD_hist": histogram,
        },
        index=close.index,
    )


def bollinger_bands(close: pd.Series, window: int = 20, std_multiplier: float = 2.0) -> pd.DataFrame:
    middle = close.rolling(window).mean()
    std = close.rolling(window).std()
    upper = middle + std_multiplier * std
    lower = middle - std_multiplier * std
    width = (upper - lower) / middle.replace(0, np.nan)
    return pd.DataFrame(
        {
            "BB_upper": upper,
            "BB_middle": middle,
            "BB_lower": lower,
            "BB_width": width,
        },
        index=close.index,
    )


def atr(high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14) -> pd.Series:
    previous_close = close.shift(1)
    true_range = pd.concat(
        [
            high - low,
            (high - previous_close).abs(),
            (low - previous_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return true_range.rolling(window).mean()


def vwap(high: pd.Series, low: pd.Series, close: pd.Series, volume: pd.Series, window: int = 20) -> pd.Series:
    typical_price = (high + low + close) / 3
    traded_value = typical_price * volume
    return traded_value.rolling(window).sum() / volume.rolling(window).sum().replace(0, np.nan)


def obv(close: pd.Series, volume: pd.Series) -> pd.Series:
    direction = np.sign(close.diff()).fillna(0)
    return (direction * volume).cumsum()


def roc(close: pd.Series, window: int = 12) -> pd.Series:
    return close.pct_change(window) * 100


def momentum(close: pd.Series, window: int = 10) -> pd.Series:
    return close - close.shift(window)


def volatility(close: pd.Series, window: int = 20) -> pd.Series:
    return close.pct_change().rolling(window).std() * np.sqrt(window)


def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add OHLCV-derived indicators used by every model pipeline."""
    enriched = df.copy()
    for column in OHLCV_COLUMNS:
        enriched[column] = _series(enriched, column)

    close = enriched["Close"]
    high = enriched["High"]
    low = enriched["Low"]
    volume = enriched["Volume"]

    enriched["RSI_14"] = rsi(close)
    enriched["EMA_12"] = ema(close, 12)
    enriched["EMA_26"] = ema(close, 26)
    enriched["EMA_50"] = ema(close, 50)
    enriched["EMA_200"] = ema(close, 200)
    enriched["SMA_20"] = sma(close, 20)
    enriched["SMA_50"] = sma(close, 50)
    enriched = pd.concat([enriched, macd(close)], axis=1)
    enriched = pd.concat([enriched, bollinger_bands(close)], axis=1)
    enriched["ATR_14"] = atr(high, low, close)
    enriched["VWAP_20"] = vwap(high, low, close, volume)
    enriched["OBV"] = obv(close, volume)
    enriched["ROC_12"] = roc(close)
    enriched["Momentum_10"] = momentum(close)
    enriched["Volatility_20"] = volatility(close)
    enriched["Log_Return"] = np.log(close / close.shift(1))
    enriched["Range_Pct"] = (high - low) / close.replace(0, np.nan)
    enriched["Volume_Change"] = volume.pct_change()

    numeric_columns = enriched.select_dtypes(include=[np.number]).columns
    enriched[numeric_columns] = (
        enriched[numeric_columns]
        .replace([np.inf, -np.inf], np.nan)
        .ffill()
        .bfill()
        .fillna(0)
    )
    return enriched


def feature_columns(df: pd.DataFrame, target_column: str = "Close") -> list[str]:
    columns = [
        column
        for column in df.select_dtypes(include=[np.number]).columns
        if column != target_column
    ]
    return [target_column] + columns
