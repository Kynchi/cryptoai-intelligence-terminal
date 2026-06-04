from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

from forecasting.preprocessing import build_sequence_dataset, chronological_split
from models.architectures import DEEP_MODEL_NAMES, build_deep_model, compile_deep_model
from models.hybrid import HYBRID_MODEL_NAMES, train_hybrid_model
from models.registry import ModelMetadata, ModelRegistry
from services.dataset_repository import DatasetRepository
from utils.config import Settings, load_settings


LOGGER = logging.getLogger(__name__)


class TrainingPipeline:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or load_settings()
        self.repository = DatasetRepository(self.settings)
        self.registry = ModelRegistry(self.settings)

    def train(
        self,
        symbol: str,
        model_name: str | None = None,
        overrides: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        symbol = symbol.upper()
        model_name = (model_name or self.settings.get("models.default", "cnn_lstm_attention")).lower()
        params = dict(self.settings.get("training", {}))
        params.update(overrides or {})

        sequence_length = int(params.get("sequence_length", self.settings.get("forecasting.default_sequence_length", 60)))
        horizons = [int(item) for item in params.get("horizons", self.settings.horizons)]
        target_column = self.settings.get("forecasting.target_column", "Close")

        df = self.repository.load_processed(symbol, refresh=True)
        min_rows = int(self.settings.get("forecasting.min_training_rows", 180))
        if len(df) < min_rows:
            raise ValueError(f"{symbol} needs at least {min_rows} rows for training, got {len(df)}.")

        dataset = build_sequence_dataset(df, sequence_length, horizons, target_column)
        split = chronological_split(
            dataset,
            validation_size=float(params.get("validation_size", 0.15)),
            test_size=float(params.get("test_size", 0.15)),
        )
        artifact_dir = self.registry.new_artifact_dir(symbol, model_name)
        scaler_path = artifact_dir / "scaler.pkl"
        dataset.scaler.save(scaler_path)

        if model_name in DEEP_MODEL_NAMES:
            metrics, model_path = self._train_deep(model_name, params, dataset, split, artifact_dir)
            backend = "tensorflow"
        elif model_name in HYBRID_MODEL_NAMES:
            metrics, model_path = self._train_hybrid(model_name, params, dataset, split, artifact_dir)
            backend = model_name
        else:
            supported = sorted(DEEP_MODEL_NAMES | HYBRID_MODEL_NAMES)
            raise ValueError(f"Unsupported model '{model_name}'. Supported: {', '.join(supported)}")

        metadata = ModelMetadata(
            symbol=symbol,
            model_name=model_name,
            backend=backend,
            artifact_dir=str(artifact_dir),
            model_path=str(model_path),
            scaler_path=str(scaler_path),
            trained_at=datetime.now(timezone.utc).isoformat(),
            sequence_length=sequence_length,
            horizons=horizons,
            feature_names=dataset.feature_names,
            target_column=target_column,
            metrics=metrics,
        )
        metadata_path = self.registry.register(metadata)
        self._track_experiment(metadata, params, artifact_dir)
        return {"metadata": metadata.__dict__, "metadata_path": str(metadata_path)}

    def _train_deep(
        self,
        model_name: str,
        params: dict[str, Any],
        dataset,
        split: dict[str, tuple[np.ndarray, np.ndarray]],
        artifact_dir: Path,
    ) -> tuple[dict[str, float], Path]:
        tf_model = build_deep_model(
            model_name,
            input_shape=dataset.X.shape[1:],
            output_dim=len(dataset.horizons),
            params=params,
        )
        model = compile_deep_model(tf_model, params)

        import tensorflow as tf

        callbacks = [
            tf.keras.callbacks.EarlyStopping(
                patience=int(params.get("early_stopping_patience", 12)),
                restore_best_weights=True,
                monitor="val_loss",
            ),
            tf.keras.callbacks.ReduceLROnPlateau(
                patience=int(params.get("reduce_lr_patience", 6)),
                factor=float(params.get("reduce_lr_factor", 0.5)),
                monitor="val_loss",
            ),
        ]
        history = model.fit(
            split["train"][0],
            split["train"][1],
            validation_data=split["validation"],
            epochs=int(params.get("epochs", 80)),
            batch_size=int(params.get("batch_size", 32)),
            callbacks=callbacks,
            verbose=int(params.get("verbose", 1)),
        )
        model_path = artifact_dir / "model.keras"
        model.save(model_path)
        predictions = model.predict(split["validation"][0], verbose=0)
        metrics = self._scaled_metrics(split["validation"][1], predictions, dataset)
        metrics["best_val_loss"] = float(min(history.history.get("val_loss", [np.nan])))
        return metrics, model_path

    def _train_hybrid(
        self,
        model_name: str,
        params: dict[str, Any],
        dataset,
        split: dict[str, tuple[np.ndarray, np.ndarray]],
        artifact_dir: Path,
    ) -> tuple[dict[str, float], Path]:
        artifact = train_hybrid_model(model_name, split["train"][0], split["train"][1], params)
        model_path = artifact_dir / "model.joblib"
        artifact.save(model_path)
        predictions = artifact.predict(split["validation"][0])
        metrics = self._scaled_metrics(split["validation"][1], predictions, dataset)
        return metrics, model_path

    @staticmethod
    def _scaled_metrics(y_true: np.ndarray, y_pred: np.ndarray, dataset) -> dict[str, float]:
        true = dataset.scaler.inverse_target(y_true, dataset.target_index)
        pred = dataset.scaler.inverse_target(y_pred, dataset.target_index)
        errors = pred - true
        mae = float(np.mean(np.abs(errors)))
        rmse = float(np.sqrt(np.mean(errors**2)))
        mape = float(np.mean(np.abs(errors / np.maximum(np.abs(true), 1e-9))) * 100)
        return {"val_mae": mae, "val_rmse": rmse, "val_mape": mape}

    @staticmethod
    def _track_experiment(metadata: ModelMetadata, params: dict[str, Any], artifact_dir: Path) -> None:
        try:
            import mlflow
        except ImportError:
            LOGGER.info("MLflow is not installed; skipping experiment tracking.")
            return

        mlflow.set_tracking_uri(params.get("mlflow_tracking_uri", "mlruns"))
        mlflow.set_experiment(params.get("experiment_name", "crypto-forecasting"))
        with mlflow.start_run(run_name=f"{metadata.symbol}-{metadata.model_name}"):
            mlflow.log_params(
                {
                    "symbol": metadata.symbol,
                    "model_name": metadata.model_name,
                    "sequence_length": metadata.sequence_length,
                    "horizons": ",".join(map(str, metadata.horizons)),
                    **{key: value for key, value in params.items() if isinstance(value, (str, int, float, bool))},
                }
            )
            mlflow.log_metrics(metadata.metrics)
            mlflow.log_artifacts(str(artifact_dir))
