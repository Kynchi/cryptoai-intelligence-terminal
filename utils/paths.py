from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def resolve_path(*parts: str | Path) -> Path:
    """Resolve a path relative to the project root unless it is already absolute."""
    if len(parts) == 1:
        candidate = Path(parts[0])
    else:
        candidate = Path(*parts)
    return candidate if candidate.is_absolute() else PROJECT_ROOT / candidate


def ensure_directory(path: str | Path) -> Path:
    resolved = resolve_path(path)
    resolved.mkdir(parents=True, exist_ok=True)
    return resolved
