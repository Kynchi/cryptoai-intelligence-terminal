from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class ForecastPoint:
    horizon: int
    predicted_close: float
    lower_80: float
    upper_80: float
    lower_95: float
    upper_95: float


class ProbabilisticForecaster:
    """Volatility and momentum-aware fallback forecaster.

    It gives the platform a real, deterministic forecasting path before a deep model
    has been trained, and the same uncertainty logic is reused around model outputs.
    """

    def __init__(self, n_paths: int = 300, random_seed: int = 42):
        self.n_paths = n_paths
        self.random_seed = random_seed

    def simulate_from_history(self, df: pd.DataFrame, horizons: list[int]) -> list[ForecastPoint]:
        close = pd.to_numeric(df["Close"], errors="coerce").dropna()
        if len(close) < 30:
            raise ValueError("At least 30 close prices are required for probabilistic forecasting.")

        returns = np.log(close / close.shift(1)).replace([np.inf, -np.inf], np.nan).dropna()
        recent = returns.tail(min(90, len(returns)))
        long_term = returns.tail(min(365, len(returns)))
        drift = 0.65 * recent.mean() + 0.35 * long_term.mean()
        volatility = max(float(recent.std()), 1e-6)

        if "RSI_14" in df.columns:
            latest_rsi = float(df["RSI_14"].iloc[-1])
            if latest_rsi > 70:
                drift -= volatility * 0.15
            elif latest_rsi < 30:
                drift += volatility * 0.15

        max_horizon = max(horizons)
        rng = np.random.default_rng(self.random_seed)
        shocks = rng.normal(
            loc=drift,
            scale=volatility,
            size=(self.n_paths, max_horizon),
        )
        paths = float(close.iloc[-1]) * np.exp(np.cumsum(shocks, axis=1))
        return self.points_from_paths(paths, horizons)

    @staticmethod
    def points_from_paths(paths: np.ndarray, horizons: list[int]) -> list[ForecastPoint]:
        points: list[ForecastPoint] = []
        for horizon in horizons:
            values = paths[:, horizon - 1]
            points.append(
                ForecastPoint(
                    horizon=int(horizon),
                    predicted_close=float(np.mean(values)),
                    lower_80=float(np.quantile(values, 0.10)),
                    upper_80=float(np.quantile(values, 0.90)),
                    lower_95=float(np.quantile(values, 0.025)),
                    upper_95=float(np.quantile(values, 0.975)),
                )
            )
        return points

    def intervals_around_predictions(
        self,
        df: pd.DataFrame,
        predictions: np.ndarray,
        horizons: list[int],
    ) -> list[ForecastPoint]:
        close = pd.to_numeric(df["Close"], errors="coerce").dropna()
        returns = np.log(close / close.shift(1)).replace([np.inf, -np.inf], np.nan).dropna()
        volatility = max(float(returns.tail(min(120, len(returns))).std()), 1e-6)

        points: list[ForecastPoint] = []
        for value, horizon in zip(predictions, horizons):
            sigma = volatility * np.sqrt(horizon)
            lower_80 = float(value * np.exp(-1.28155 * sigma))
            upper_80 = float(value * np.exp(1.28155 * sigma))
            lower_95 = float(value * np.exp(-1.95996 * sigma))
            upper_95 = float(value * np.exp(1.95996 * sigma))
            points.append(
                ForecastPoint(
                    horizon=int(horizon),
                    predicted_close=float(value),
                    lower_80=lower_80,
                    upper_80=upper_80,
                    lower_95=lower_95,
                    upper_95=upper_95,
                )
            )
        return points
