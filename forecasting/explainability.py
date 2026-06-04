from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd


@dataclass
class Explanation:
    method: str
    feature_importance: list[dict[str, float | str]]
    attention: list[dict[str, float]] | None
    summary: str


class ExplainabilityService:
    def feature_importance_from_data(self, df: pd.DataFrame, target_column: str = "Close") -> Explanation:
        numeric = df.select_dtypes(include=[np.number])
        correlations: list[dict[str, float | str]] = []
        if target_column not in numeric.columns:
            raise ValueError(f"{target_column} is not available for explainability.")

        target = numeric[target_column].pct_change().shift(-1)
        for column in numeric.columns:
            if column == target_column:
                continue
            values = numeric[column].pct_change().replace([np.inf, -np.inf], np.nan)
            corr = values.corr(target)
            if pd.notna(corr):
                correlations.append({"feature": column, "importance": float(abs(corr))})

        correlations = sorted(correlations, key=lambda item: float(item["importance"]), reverse=True)[:20]
        return Explanation(
            method="correlation-fallback",
            feature_importance=correlations,
            attention=None,
            summary="Feature importance is estimated from absolute correlation with next-period returns.",
        )

    def shap_explanation(self, model: Any, X: np.ndarray, feature_names: list[str]) -> Explanation:
        try:
            import shap
        except ImportError:
            return Explanation(
                method="shap-unavailable",
                feature_importance=[],
                attention=None,
                summary="Install shap to enable model-native SHAP explanations.",
            )

        flattened = X.reshape(X.shape[0], -1)
        explainer = shap.Explainer(model, flattened)
        values = explainer(flattened[: min(64, len(flattened))])
        mean_abs = np.abs(values.values).mean(axis=0)
        grouped: dict[str, float] = {}
        for idx, importance in enumerate(mean_abs):
            feature = feature_names[idx % len(feature_names)]
            grouped[feature] = grouped.get(feature, 0.0) + float(importance)

        ranked = sorted(grouped.items(), key=lambda item: item[1], reverse=True)[:20]
        return Explanation(
            method="shap",
            feature_importance=[{"feature": key, "importance": value} for key, value in ranked],
            attention=None,
            summary="SHAP values are aggregated across sequence steps.",
        )
