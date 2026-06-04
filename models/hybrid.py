from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np


HYBRID_MODEL_NAMES = {"xgboost_hybrid", "lightgbm_hybrid", "random_forest_hybrid"}


@dataclass
class HybridModelArtifact:
    model: Any
    backend: str

    def predict(self, X: np.ndarray) -> np.ndarray:
        flattened = X.reshape(X.shape[0], -1)
        return np.asarray(self.model.predict(flattened), dtype=float)

    def save(self, path: str | Path) -> None:
        try:
            import joblib
        except ImportError as exc:
            raise RuntimeError("joblib is required to save hybrid models.") from exc
        joblib.dump({"backend": self.backend, "model": self.model}, path)

    @staticmethod
    def load(path: str | Path) -> "HybridModelArtifact":
        try:
            import joblib
        except ImportError as exc:
            raise RuntimeError("joblib is required to load hybrid models.") from exc
        payload = joblib.load(path)
        return HybridModelArtifact(model=payload["model"], backend=payload["backend"])


def train_hybrid_model(model_name: str, X: np.ndarray, y: np.ndarray, params: dict[str, Any]) -> HybridModelArtifact:
    flattened = X.reshape(X.shape[0], -1)
    try:
        from sklearn.multioutput import MultiOutputRegressor
    except ImportError as exc:
        raise RuntimeError("scikit-learn is required for hybrid models.") from exc

    if model_name == "xgboost_hybrid":
        try:
            from xgboost import XGBRegressor
        except ImportError as exc:
            raise RuntimeError("xgboost is required for xgboost_hybrid.") from exc
        base = XGBRegressor(
            n_estimators=int(params.get("n_estimators", 400)),
            max_depth=int(params.get("max_depth", 4)),
            learning_rate=float(params.get("learning_rate", 0.03)),
            subsample=float(params.get("subsample", 0.85)),
            colsample_bytree=float(params.get("colsample_bytree", 0.85)),
            objective="reg:squarederror",
            tree_method=params.get("tree_method", "hist"),
        )
    elif model_name == "lightgbm_hybrid":
        try:
            from lightgbm import LGBMRegressor
        except ImportError as exc:
            raise RuntimeError("lightgbm is required for lightgbm_hybrid.") from exc
        base = LGBMRegressor(
            n_estimators=int(params.get("n_estimators", 500)),
            max_depth=int(params.get("max_depth", -1)),
            learning_rate=float(params.get("learning_rate", 0.03)),
            subsample=float(params.get("subsample", 0.85)),
            colsample_bytree=float(params.get("colsample_bytree", 0.85)),
        )
    elif model_name == "random_forest_hybrid":
        from sklearn.ensemble import RandomForestRegressor

        base = RandomForestRegressor(
            n_estimators=int(params.get("n_estimators", 500)),
            max_depth=params.get("max_depth", None),
            min_samples_leaf=int(params.get("min_samples_leaf", 2)),
            random_state=int(params.get("random_state", 42)),
            n_jobs=int(params.get("n_jobs", -1)),
        )
    else:
        supported = ", ".join(sorted(HYBRID_MODEL_NAMES))
        raise ValueError(f"Unsupported hybrid model '{model_name}'. Supported: {supported}")

    model = MultiOutputRegressor(base)
    model.fit(flattened, y)
    return HybridModelArtifact(model=model, backend=model_name)
