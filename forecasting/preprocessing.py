from __future__ import annotations

import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import numpy as np
import pandas as pd

from indicators.technical import feature_columns


@dataclass
class RobustMinMaxScaler:
    min_: np.ndarray | None = None
    max_: np.ndarray | None = None
    feature_names: list[str] | None = None
    epsilon: float = 1e-9

    def fit(self, frame: pd.DataFrame, feature_names: Sequence[str]) -> "RobustMinMaxScaler":
        self.feature_names = list(feature_names)
        values = frame[self.feature_names].astype(float).to_numpy()
        self.min_ = np.nanmin(values, axis=0)
        self.max_ = np.nanmax(values, axis=0)
        return self

    def transform(self, frame: pd.DataFrame) -> np.ndarray:
        if self.min_ is None or self.max_ is None or self.feature_names is None:
            raise RuntimeError("Scaler has not been fitted.")
        values = frame[self.feature_names].astype(float).to_numpy()
        return (values - self.min_) / (self.max_ - self.min_ + self.epsilon)

    def inverse_target(self, values: np.ndarray, target_index: int = 0) -> np.ndarray:
        if self.min_ is None or self.max_ is None:
            raise RuntimeError("Scaler has not been fitted.")
        return values * (self.max_[target_index] - self.min_[target_index] + self.epsilon) + self.min_[target_index]

    def save(self, path: str | Path) -> None:
        with Path(path).open("wb") as file:
            pickle.dump(self, file)

    @staticmethod
    def load(path: str | Path) -> "RobustMinMaxScaler":
        with Path(path).open("rb") as file:
            scaler = pickle.load(file)
        if not isinstance(scaler, RobustMinMaxScaler):
            raise TypeError(f"Unexpected scaler type in {path}: {type(scaler)!r}")
        return scaler


@dataclass
class SequenceDataset:
    X: np.ndarray
    y: np.ndarray
    dates: pd.Series
    feature_names: list[str]
    target_index: int
    scaler: RobustMinMaxScaler
    sequence_length: int
    horizons: list[int]


def build_sequence_dataset(
    df: pd.DataFrame,
    sequence_length: int,
    horizons: Sequence[int],
    target_column: str = "Close",
) -> SequenceDataset:
    if "Timestamp" not in df.columns:
        raise ValueError("DataFrame must contain a Timestamp column.")
    horizons = sorted({int(horizon) for horizon in horizons})
    if any(horizon <= 0 for horizon in horizons):
        raise ValueError("Forecast horizons must be positive integers.")

    features = feature_columns(df, target_column=target_column)
    target_index = features.index(target_column)
    scaler = RobustMinMaxScaler().fit(df, features)
    scaled = scaler.transform(df)

    max_horizon = max(horizons)
    X: list[np.ndarray] = []
    y: list[np.ndarray] = []
    target_dates: list[pd.Timestamp] = []

    last_start = len(df) - sequence_length - max_horizon + 1
    if last_start <= 0:
        raise ValueError(
            f"Not enough rows ({len(df)}) for sequence_length={sequence_length} "
            f"and max_horizon={max_horizon}."
        )

    for start in range(last_start):
        end = start + sequence_length
        X.append(scaled[start:end])
        y.append([scaled[end + horizon - 1, target_index] for horizon in horizons])
        target_dates.append(pd.to_datetime(df["Timestamp"].iloc[end - 1]))

    return SequenceDataset(
        X=np.asarray(X, dtype=np.float32),
        y=np.asarray(y, dtype=np.float32),
        dates=pd.Series(target_dates),
        feature_names=features,
        target_index=target_index,
        scaler=scaler,
        sequence_length=sequence_length,
        horizons=list(horizons),
    )


def chronological_split(
    dataset: SequenceDataset,
    validation_size: float,
    test_size: float,
) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    n = len(dataset.X)
    test_n = max(1, int(n * test_size))
    validation_n = max(1, int(n * validation_size))
    train_n = n - validation_n - test_n
    if train_n <= 0:
        raise ValueError("Dataset split leaves no training samples.")

    return {
        "train": (dataset.X[:train_n], dataset.y[:train_n]),
        "validation": (
            dataset.X[train_n : train_n + validation_n],
            dataset.y[train_n : train_n + validation_n],
        ),
        "test": (dataset.X[train_n + validation_n :], dataset.y[train_n + validation_n :]),
    }


def latest_sequence(df: pd.DataFrame, scaler: RobustMinMaxScaler, sequence_length: int) -> np.ndarray:
    if len(df) < sequence_length:
        raise ValueError(f"Need at least {sequence_length} rows for inference, got {len(df)}.")
    scaled = scaler.transform(df)
    return scaled[-sequence_length:].reshape(1, sequence_length, len(scaler.feature_names or []))
