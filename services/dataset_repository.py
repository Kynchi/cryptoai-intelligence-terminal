from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from indicators.technical import OHLCV_COLUMNS, add_technical_indicators
from utils.config import Settings, load_settings
from utils.paths import ensure_directory


LOGGER = logging.getLogger(__name__)


class DatasetRepository:
    """Centralized data access for raw and feature-enriched OHLCV datasets."""

    def __init__(self, settings: Settings | None = None):
        self.settings = settings or load_settings()
        self.raw_dir = ensure_directory(self.settings.path("raw_data"))
        self.processed_dir = ensure_directory(self.settings.path("processed_data"))
        self.legacy_dir = self.settings.path("legacy_data")

    def raw_path(self, symbol: str) -> Path:
        coin = self.settings.coin(symbol)
        return self.raw_dir / coin["dataset"]

    def processed_path(self, symbol: str) -> Path:
        coin = self.settings.coin(symbol)
        return self.processed_dir / coin["dataset"]

    def legacy_path(self, symbol: str) -> Path:
        coin = self.settings.coin(symbol)
        return self.legacy_dir / coin["dataset"]

    def load_raw(self, symbol: str) -> pd.DataFrame:
        path = self.raw_path(symbol)
        if not path.exists() and self.legacy_path(symbol).exists():
            path = self.legacy_path(symbol)
        if not path.exists():
            raise FileNotFoundError(f"No raw dataset found for {symbol}: {path}")
        df = pd.read_csv(path)
        return self._normalize_market_frame(df)

    def load_processed(self, symbol: str, refresh: bool = False) -> pd.DataFrame:
        path = self.processed_path(symbol)
        if refresh or not path.exists():
            return self.build_processed(symbol)
        return pd.read_csv(path, parse_dates=["Timestamp"])

    def build_processed(self, symbol: str) -> pd.DataFrame:
        raw = self.load_raw(symbol)
        enriched = add_technical_indicators(raw)
        path = self.processed_path(symbol)
        enriched.to_csv(path, index=False)
        LOGGER.info("Processed dataset saved for %s at %s", symbol.upper(), path)
        return enriched

    def upsert_raw(self, symbol: str, rows: pd.DataFrame) -> Path:
        normalized = self._normalize_market_frame(rows)
        path = self.raw_path(symbol)
        if path.exists():
            existing = self._normalize_market_frame(pd.read_csv(path))
            normalized = pd.concat([existing, normalized], ignore_index=True)
        normalized = (
            normalized.drop_duplicates(subset=["Timestamp"], keep="last")
            .sort_values("Timestamp")
            .reset_index(drop=True)
        )
        normalized.to_csv(path, index=False)
        self.build_processed(symbol)
        return path

    def available_symbols(self) -> list[str]:
        return sorted(self.settings.coins.keys())

    @staticmethod
    def _normalize_market_frame(df: pd.DataFrame) -> pd.DataFrame:
        normalized = df.copy()
        normalized.columns = [column.strip() for column in normalized.columns]

        timestamp_column = next(
            (column for column in normalized.columns if column.lower() in {"timestamp", "date", "time"}),
            None,
        )
        if timestamp_column:
            normalized["Timestamp"] = pd.to_datetime(normalized[timestamp_column], errors="coerce", utc=True)
        else:
            end = pd.Timestamp.utcnow().normalize()
            normalized["Timestamp"] = pd.date_range(
                end=end,
                periods=len(normalized),
                freq="D",
                tz="UTC",
            )

        for column in OHLCV_COLUMNS:
            if column not in normalized.columns:
                raise ValueError(f"Dataset is missing required OHLCV column: {column}")
            normalized[column] = pd.to_numeric(normalized[column], errors="coerce")

        normalized = normalized[["Timestamp", *OHLCV_COLUMNS]]
        normalized = normalized.dropna(subset=OHLCV_COLUMNS)
        normalized = normalized.sort_values("Timestamp").reset_index(drop=True)
        return normalized
