from __future__ import annotations

import logging
from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from forecasting.explainability import ExplainabilityService
from forecasting.preprocessing import RobustMinMaxScaler, latest_sequence
from forecasting.probabilistic import ProbabilisticForecaster
from forecasting.signals import TradingSignalEngine
from models.hybrid import HybridModelArtifact
from models.registry import ModelMetadata, ModelRegistry
from services.dataset_repository import DatasetRepository
from services.market_sentiment import MarketSentimentService
from utils.config import Settings, load_settings


LOGGER = logging.getLogger(__name__)


class ForecastingEngine:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or load_settings()
        self.repository = DatasetRepository(self.settings)
        self.registry = ModelRegistry(self.settings)
        self.probabilistic = ProbabilisticForecaster(
            n_paths=int(self.settings.get("forecasting.probabilistic_paths", 300))
        )
        self.explainability = ExplainabilityService()
        self.sentiment = MarketSentimentService()
        self.signal_engine = TradingSignalEngine(
            buy_threshold=float(self.settings.get("backtesting.buy_threshold", 0.015)),
            sell_threshold=float(self.settings.get("backtesting.sell_threshold", -0.015)),
        )

    def predict(
        self,
        symbol: str,
        horizons: list[int] | None = None,
        model_name: str | None = None,
    ) -> dict[str, Any]:
        symbol = symbol.upper()
        horizons = sorted({int(item) for item in (horizons or self.settings.horizons)})
        df = self.repository.load_processed(symbol)
        metadata = self.registry.best(symbol, model_name=model_name)

        if metadata:
            try:
                points = self._predict_with_artifact(df, metadata, horizons)
                model_status = "trained-artifact"
                model_used = metadata.model_name
            except Exception as exc:
                LOGGER.exception("Model artifact inference failed; falling back to probabilistic baseline: %s", exc)
                points = self.probabilistic.simulate_from_history(df, horizons)
                model_status = f"fallback-after-artifact-error:{exc}"
                model_used = "probabilistic_baseline"
        else:
            points = self.probabilistic.simulate_from_history(df, horizons)
            model_status = "probabilistic-baseline"
            model_used = "probabilistic_baseline"

        close = pd.to_numeric(df["Close"], errors="coerce")
        current_price = float(close.iloc[-1])
        volatility = float(close.pct_change().tail(30).std())
        sentiment = self.sentiment.snapshot(symbol, df)
        signal_point = self._select_signal_point(points)
        signal = self.signal_engine.generate(
            current_price=current_price,
            forecast_price=signal_point.predicted_close,
            lower_95=signal_point.lower_95,
            upper_95=signal_point.upper_95,
            volatility=max(volatility, 1e-6),
            sentiment_score=sentiment.normalized_score,
        )
        explanation = self.explainability.feature_importance_from_data(df)

        historical = df.tail(240)[["Timestamp", "Open", "High", "Low", "Close", "Volume"]].copy()
        historical["Timestamp"] = historical["Timestamp"].astype(str)

        return {
            "symbol": symbol,
            "model_used": model_used,
            "model_status": model_status,
            "current_price": current_price,
            "forecast": [asdict(point) for point in points],
            "signal": asdict(signal),
            "sentiment": asdict(sentiment),
            "explainability": asdict(explanation),
            "historical": historical.to_dict(orient="records"),
            "leaderboard": self.registry.leaderboard(symbol),
        }

    def _predict_with_artifact(
        self,
        df: pd.DataFrame,
        metadata: ModelMetadata,
        requested_horizons: list[int],
    ):
        trained_horizons = [int(item) for item in metadata.horizons]
        missing = [horizon for horizon in requested_horizons if horizon not in trained_horizons]
        if missing:
            LOGGER.info("Requested horizons %s missing in artifact; using probabilistic baseline.", missing)
            return self.probabilistic.simulate_from_history(df, requested_horizons)

        scaler = RobustMinMaxScaler.load(metadata.scaler_path)
        sequence = latest_sequence(df, scaler, metadata.sequence_length)

        if metadata.backend == "tensorflow":
            try:
                import tensorflow as tf
            except ImportError as exc:
                raise RuntimeError("TensorFlow is required to load this trained artifact.") from exc
            model = tf.keras.models.load_model(metadata.model_path)
            scaled_predictions = np.asarray(model.predict(sequence, verbose=0)[0], dtype=float)
        elif metadata.backend in {"xgboost_hybrid", "lightgbm_hybrid"}:
            artifact = HybridModelArtifact.load(metadata.model_path)
            scaled_predictions = artifact.predict(sequence)[0]
        else:
            raise RuntimeError(f"Unsupported artifact backend: {metadata.backend}")

        prediction_map = {
            horizon: value for horizon, value in zip(trained_horizons, scaler.inverse_target(scaled_predictions))
        }
        predictions = np.array([prediction_map[horizon] for horizon in requested_horizons], dtype=float)
        return self.probabilistic.intervals_around_predictions(df, predictions, requested_horizons)

    @staticmethod
    def _select_signal_point(points):
        return next((point for point in points if point.horizon == 7), points[min(len(points) - 1, 0)])

    def realtime_snapshot(self, symbols: list[str] | None = None) -> dict[str, Any]:
        symbols = symbols or sorted(self.settings.coins)
        return {"symbols": [self.predict(symbol, horizons=[1, 3, 7]) for symbol in symbols]}
