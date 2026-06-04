from __future__ import annotations

import logging
import logging.config
from pathlib import Path

from utils.paths import ensure_directory, resolve_path


def setup_logging(config_path: str | Path = "configs/logging.yaml") -> None:
    ensure_directory("logs")
    resolved = resolve_path(config_path)
    if not resolved.exists():
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        )
        return

    try:
        import yaml
    except ImportError:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        )
        logging.getLogger(__name__).warning("PyYAML unavailable; using basic logging.")
        return

    with resolved.open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file)
    logging.config.dictConfig(config)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
