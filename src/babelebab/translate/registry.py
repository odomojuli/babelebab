"""A tiny process-global registry of named engines."""
from __future__ import annotations

from .base import Engine

_ENGINES: dict[str, Engine] = {}


def register(engine: Engine, *, name: str | None = None) -> Engine:
    """Register ``engine`` under ``name`` (defaults to ``engine.name``)."""
    _ENGINES[name or engine.name] = engine
    return engine


def get(name: str) -> Engine:
    """Return the engine registered as ``name``."""
    try:
        return _ENGINES[name]
    except KeyError:
        raise KeyError(
            f"No engine registered as {name!r}. Available: {sorted(_ENGINES)}"
        ) from None


def available() -> list[str]:
    """Return the sorted names of all registered engines."""
    return sorted(_ENGINES)


def unregister(name: str) -> None:
    """Remove ``name`` from the registry if present."""
    _ENGINES.pop(name, None)
