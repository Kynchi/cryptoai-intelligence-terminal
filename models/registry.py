from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from utils.config import Settings, load_settings
from utils.paths import ensure_directory


@dataclass
class ModelMetadata:
    symbol: str
    model_name: str
    backend: str
    artifact_dir: str
    model_path: str
    scaler_path: str
    trained_at: str
    sequence_length: int
    horizons: list[int]
    feature_names: list[str]
    target_column: str
    metrics: dict[str, float] = field(default_factory=dict)
    status: str = "trained"


class ModelRegistry:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or load_settings()
        self.artifacts_dir = ensure_directory(self.settings.path("model_artifacts"))
        self.registry_dir = ensure_directory(self.settings.path("model_registry"))

    def new_artifact_dir(self, symbol: str, model_name: str) -> Path:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        return ensure_directory(self.artifacts_dir / symbol.upper() / model_name / stamp)

    def register(self, metadata: ModelMetadata) -> Path:
        artifact_dir = ensure_directory(metadata.artifact_dir)
        metadata_path = artifact_dir / "metadata.json"
        metadata_path.write_text(json.dumps(asdict(metadata), indent=2), encoding="utf-8")

        registry_path = self.registry_dir / f"{metadata.symbol.upper()}.json"
        records: list[dict[str, Any]] = []
        if registry_path.exists():
            records = json.loads(registry_path.read_text(encoding="utf-8"))
        records.append(asdict(metadata))
        records = sorted(records, key=lambda item: item.get("metrics", {}).get("val_rmse", float("inf")))
        registry_path.write_text(json.dumps(records, indent=2), encoding="utf-8")
        return metadata_path

    def leaderboard(self, symbol: str | None = None) -> list[dict[str, Any]]:
        symbols = [symbol.upper()] if symbol else sorted(self.settings.coins)
        rows: list[dict[str, Any]] = []
        for item in symbols:
            path = self.registry_dir / f"{item}.json"
            if path.exists():
                rows.extend(json.loads(path.read_text(encoding="utf-8")))
        return sorted(rows, key=lambda item: item.get("metrics", {}).get("val_rmse", float("inf")))

    def best(self, symbol: str, model_name: str | None = None) -> ModelMetadata | None:
        records = self.leaderboard(symbol)
        if model_name:
            records = [record for record in records if record.get("model_name") == model_name]
        for record in records:
            model_path = Path(record.get("model_path", ""))
            scaler_path = Path(record.get("scaler_path", ""))
            if model_path.exists() and scaler_path.exists():
                return ModelMetadata(**record)
        return None
