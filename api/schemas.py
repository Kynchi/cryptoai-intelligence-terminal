from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    symbol: str = Field(default="BTC", description="Crypto symbol, e.g. BTC, ETH, SOL, XRP.")
    horizons: list[int] | None = Field(default=None, description="Forecast horizons in days.")
    model_name: str | None = Field(default=None, description="Optional registered model name.")


class TrainRequest(BaseModel):
    symbol: str = "BTC"
    model_name: str | None = None
    overrides: dict[str, Any] = Field(default_factory=dict)


class EvaluateRequest(BaseModel):
    symbol: str = "BTC"
    horizon: int = 1
    windows: int = 120


class BacktestRequest(BaseModel):
    symbol: str = "BTC"
    lookahead: int = 7


class RealtimeRequest(BaseModel):
    symbols: list[str] | None = None
    retrain: bool = False
    model_name: str | None = None
