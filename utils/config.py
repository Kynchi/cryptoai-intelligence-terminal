from __future__ import annotations

import json
import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from utils.paths import resolve_path


class ConfigError(RuntimeError):
    """Raised when the platform configuration cannot be loaded."""


def _load_yaml(path: Path) -> dict[str, Any]:
    try:
        import yaml
    except ImportError as exc:
        raise ConfigError(
            "PyYAML is required to read YAML configs. Install project dependencies with "
            "`pip install -r requirements.txt`."
        ) from exc

    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)
    if not isinstance(data, dict):
        raise ConfigError(f"Configuration file {path} does not contain an object.")
    return data


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise ConfigError(f"Configuration file {path} does not contain an object.")
    return data


@dataclass(frozen=True)
class Settings:
    values: dict[str, Any]

    def get(self, dotted_key: str, default: Any = None) -> Any:
        value: Any = self.values
        for part in dotted_key.split("."):
            if not isinstance(value, dict) or part not in value:
                return default
            value = value[part]
        return value

    @property
    def coins(self) -> dict[str, dict[str, Any]]:
        return self.values.get("coins", {})

    @property
    def horizons(self) -> list[int]:
        return list(self.get("forecasting.horizons", [1, 3, 7, 30]))

    def coin(self, symbol: str) -> dict[str, Any]:
        symbol = symbol.upper()
        coins = self.coins
        if symbol not in coins:
            allowed = ", ".join(sorted(coins))
            raise ConfigError(f"Unsupported coin '{symbol}'. Supported coins: {allowed}.")
        return coins[symbol]

    def path(self, dotted_key: str) -> Path:
        configured = self.get(f"paths.{dotted_key}")
        if configured is None:
            raise ConfigError(f"Missing path configuration: paths.{dotted_key}")
        return resolve_path(configured)


@lru_cache(maxsize=1)
def load_settings(config_path: str | Path | None = None) -> Settings:
    env_config = os.getenv("CRYPTO_FORECAST_CONFIG")
    resolved = resolve_path(config_path or env_config or "configs/config.json")
    if not resolved.exists():
        raise ConfigError(f"Configuration file not found: {resolved}")
    if resolved.suffix.lower() in {".yaml", ".yml"}:
        return Settings(_load_yaml(resolved))
    if resolved.suffix.lower() == ".json":
        return Settings(_load_json(resolved))
    raise ConfigError(f"Unsupported configuration format: {resolved.suffix}")
