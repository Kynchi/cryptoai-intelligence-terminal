from __future__ import annotations

import numpy as np
import pandas as pd

from indicators.technical import add_technical_indicators


def sample_frame(rows: int = 120) -> pd.DataFrame:
    close = np.linspace(100, 130, rows) + np.sin(np.arange(rows))
    return pd.DataFrame(
        {
            "Timestamp": pd.date_range("2024-01-01", periods=rows, freq="D", tz="UTC"),
            "Open": close - 0.5,
            "High": close + 1.5,
            "Low": close - 1.5,
            "Close": close,
            "Volume": np.linspace(1000, 3000, rows),
        }
    )


def test_add_technical_indicators_produces_multivariate_features():
    enriched = add_technical_indicators(sample_frame())
    for column in ["RSI_14", "MACD", "EMA_12", "SMA_20", "BB_upper", "ATR_14", "VWAP_20", "OBV"]:
        assert column in enriched.columns
    assert enriched.select_dtypes(include=[np.number]).isna().sum().sum() == 0
