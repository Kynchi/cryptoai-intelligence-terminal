from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from training.train import TrainingPipeline
from utils.config import Settings, load_settings


@dataclass
class TuningResult:
    best_params: dict[str, Any]
    best_value: float
    trials: int


class HyperparameterTuner:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or load_settings()
        self.pipeline = TrainingPipeline(self.settings)

    def tune_with_optuna(self, symbol: str, model_name: str, trials: int | None = None) -> TuningResult:
        try:
            import optuna
        except ImportError as exc:
            raise RuntimeError("optuna is required for Bayesian hyperparameter tuning.") from exc

        tuning = self.settings.get("tuning", {})
        max_trials = int(trials or tuning.get("max_trials", 25))

        def objective(trial):
            params = {
                "sequence_length": trial.suggest_categorical("sequence_length", tuning.get("sequence_length", [60])),
                "learning_rate": trial.suggest_float(
                    "learning_rate",
                    float(tuning.get("learning_rate", [0.0001, 0.003])[0]),
                    float(tuning.get("learning_rate", [0.0001, 0.003])[1]),
                    log=True,
                ),
                "hidden_units": trial.suggest_categorical("hidden_units", tuning.get("hidden_units", [64, 96])),
                "dropout": trial.suggest_float(
                    "dropout",
                    float(tuning.get("dropout", [0.1, 0.5])[0]),
                    float(tuning.get("dropout", [0.1, 0.5])[1]),
                ),
                "batch_size": trial.suggest_categorical("batch_size", tuning.get("batch_size", [32])),
                "epochs": min(int(self.settings.get("training.epochs", 80)), 40),
                "verbose": 0,
            }
            if "cnn" in model_name:
                params["filters"] = trial.suggest_categorical("filters", tuning.get("filters", [64]))
            if "attention" in model_name or "transformer" in model_name:
                params["attention_dim"] = trial.suggest_categorical(
                    "attention_dim",
                    tuning.get("attention_dim", [32, 64]),
                )
            result = self.pipeline.train(symbol=symbol, model_name=model_name, overrides=params)
            return result["metadata"]["metrics"]["val_rmse"]

        study = optuna.create_study(direction="minimize", study_name=f"{symbol}-{model_name}")
        study.optimize(objective, n_trials=max_trials)
        return TuningResult(study.best_params, float(study.best_value), len(study.trials))

    def tune_with_keras_tuner(self, symbol: str, model_name: str) -> TuningResult:
        try:
            import keras_tuner  # noqa: F401
        except ImportError as exc:
            raise RuntimeError("keras-tuner is required for Keras Tuner workflows.") from exc
        return self.tune_with_optuna(symbol, model_name)
