from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import pandas as pd

from services.dataset_repository import DatasetRepository
from utils.config import Settings, load_settings


LOGGER = logging.getLogger(__name__)


@dataclass
class IngestionResult:
    symbol: str
    provider: str
    rows: int
    path: str
    used_live_api: bool
    message: str


class CoinMarketCapClient:
    """CoinMarketCap adapter for realtime quote and OHLCV ingestion."""

    def __init__(self, settings: Settings | None = None, api_key: str | None = None):
        self.settings = settings or load_settings()
        self.api_key = api_key or os.getenv("COINMARKETCAP_API_KEY")
        self.base_url = self.settings.get("data_ingestion.base_url", "https://pro-api.coinmarketcap.com")
        self.timeout = int(self.settings.get("data_ingestion.request_timeout_seconds", 30))

    @property
    def configured(self) -> bool:
        return bool(self.api_key)

    def _headers(self) -> dict[str, str]:
        if not self.api_key:
            raise RuntimeError("COINMARKETCAP_API_KEY is not configured.")
        return {
            "Accepts": "application/json",
            "X-CMC_PRO_API_KEY": self.api_key,
        }

    def _request(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        try:
            import requests
        except ImportError as exc:
            raise RuntimeError("requests is required for CoinMarketCap ingestion.") from exc

        response = requests.get(
            f"{self.base_url}{path}",
            headers=self._headers(),
            params=params,
            timeout=self.timeout,
        )
        response.raise_for_status()
        payload = response.json()
        status = payload.get("status", {})
        if status.get("error_code"):
            raise RuntimeError(status.get("error_message", "CoinMarketCap API returned an error."))
        return payload

    def latest_quote(self, symbols: list[str]) -> pd.DataFrame:
        quote = self.settings.get("data_ingestion.quote_currency", "USD")
        payload = self._request(
            "/v2/cryptocurrency/quotes/latest",
            {"symbol": ",".join(symbols), "convert": quote},
        )
        rows: list[dict[str, Any]] = []
        for symbol, entries in payload.get("data", {}).items():
            entry = entries[0] if isinstance(entries, list) else entries
            quote_payload = entry.get("quote", {}).get(quote, {})
            price = float(quote_payload.get("price", 0))
            volume = float(quote_payload.get("volume_24h", 0))
            rows.append(
                {
                    "Timestamp": datetime.now(timezone.utc),
                    "Symbol": symbol,
                    "Open": price,
                    "High": price,
                    "Low": price,
                    "Close": price,
                    "Volume": volume,
                }
            )
        return pd.DataFrame(rows)

    def historical_ohlcv(self, symbol: str, limit: int = 365) -> pd.DataFrame:
        coin = self.settings.coin(symbol)
        quote = self.settings.get("data_ingestion.quote_currency", "USD")
        payload = self._request(
            "/v2/cryptocurrency/ohlcv/historical",
            {
                "id": coin["id"],
                "convert": quote,
                "count": limit,
                "interval": "daily",
            },
        )
        quotes = payload.get("data", {}).get("quotes", [])
        rows = []
        for item in quotes:
            q = item.get("quote", {}).get(quote, {})
            rows.append(
                {
                    "Timestamp": item.get("time_close") or item.get("timestamp"),
                    "Open": q.get("open"),
                    "High": q.get("high"),
                    "Low": q.get("low"),
                    "Close": q.get("close"),
                    "Volume": q.get("volume"),
                }
            )
        return pd.DataFrame(rows)


class DataIngestionService:
    def __init__(
        self,
        settings: Settings | None = None,
        repository: DatasetRepository | None = None,
        client: CoinMarketCapClient | None = None,
    ):
        self.settings = settings or load_settings()
        self.repository = repository or DatasetRepository(self.settings)
        self.client = client or CoinMarketCapClient(self.settings)

    def update_symbol(self, symbol: str, historical_limit: int = 365) -> IngestionResult:
        symbol = symbol.upper()
        if self.client.configured:
            live_rows = self.client.historical_ohlcv(symbol, limit=historical_limit)
            if live_rows.empty:
                latest = self.client.latest_quote([symbol])
                live_rows = latest.drop(columns=["Symbol"], errors="ignore")
            path = self.repository.upsert_raw(symbol, live_rows)
            return IngestionResult(
                symbol=symbol,
                provider="coinmarketcap",
                rows=len(live_rows),
                path=str(path),
                used_live_api=True,
                message="CoinMarketCap data ingested and processed.",
            )

        processed = self.repository.build_processed(symbol)
        return IngestionResult(
            symbol=symbol,
            provider="local-seed",
            rows=len(processed),
            path=str(self.repository.raw_path(symbol)),
            used_live_api=False,
            message="COINMARKETCAP_API_KEY is not set; refreshed processed data from local seed CSV.",
        )

    def update_all(self) -> list[IngestionResult]:
        return [self.update_symbol(symbol) for symbol in self.repository.available_symbols()]
