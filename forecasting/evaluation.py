from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from forecasting.probabilistic import ProbabilisticForecaster


@dataclass
class EvaluationReport:
    mae: float
    rmse: float
    mape: float
    smape: float
    directional_accuracy: float
    rows_evaluated: int


def regression_metrics(actual: np.ndarray, predicted: np.ndarray) -> EvaluationReport:
    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)
    error = predicted - actual
    mae = float(np.mean(np.abs(error)))
    rmse = float(np.sqrt(np.mean(error**2)))
    mape = float(np.mean(np.abs(error / np.maximum(np.abs(actual), 1e-9))) * 100)
    smape = float(np.mean(2 * np.abs(error) / np.maximum(np.abs(actual) + np.abs(predicted), 1e-9)) * 100)
    if len(actual) > 1:
        directional_accuracy = float(np.mean(np.sign(np.diff(actual)) == np.sign(np.diff(predicted))))
    else:
        directional_accuracy = 0.0
    return EvaluationReport(mae, rmse, mape, smape, directional_accuracy, len(actual))


class EvaluationPipeline:
    def __init__(self, forecaster: ProbabilisticForecaster | None = None):
        self.forecaster = forecaster or ProbabilisticForecaster(n_paths=200)

    def evaluate_baseline(self, df: pd.DataFrame, horizon: int = 1, windows: int = 120) -> EvaluationReport:
        if len(df) <= windows + horizon + 30:
            windows = max(10, len(df) - horizon - 31)
        if windows <= 0:
            raise ValueError("Not enough rows to evaluate.")

        actual: list[float] = []
        predicted: list[float] = []
        start = len(df) - windows - horizon
        for idx in range(start, len(df) - horizon):
            train_slice = df.iloc[:idx].copy()
            point = self.forecaster.simulate_from_history(train_slice, [horizon])[0]
            actual.append(float(df["Close"].iloc[idx + horizon - 1]))
            predicted.append(point.predicted_close)
        return regression_metrics(np.array(actual), np.array(predicted))
