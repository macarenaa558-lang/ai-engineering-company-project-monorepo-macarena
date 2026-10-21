"""Resultados de análisis por usuario, versionados y solo en memoria del proceso."""

from itertools import count
from threading import Lock
from typing import Any

_lock = Lock()
_versions = count(1)
_results: dict[str, tuple[int, dict[str, Any]]] = {}


def save(user_id: str, analysis: dict[str, Any]) -> int:
    with _lock:
        version = next(_versions)
        _results[user_id] = (version, analysis)
        return version


def get(user_id: str) -> tuple[int, dict[str, Any]] | None:
    with _lock:
        return _results.get(user_id)


def clear() -> None:
    with _lock:
        _results.clear()
