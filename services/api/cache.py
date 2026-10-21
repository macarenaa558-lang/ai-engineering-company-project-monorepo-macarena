from __future__ import annotations

from copy import deepcopy
from threading import Lock
from time import monotonic
from typing import Any


CACHE_TTL_SECONDS = 60

_cache: dict[str, tuple[float, Any]] = {}
_lock = Lock()


def get_cached(key: str) -> Any | None:
    with _lock:
        entry = _cache.get(key)

        if entry is None:
            return None

        expires_at, value = entry

        if monotonic() >= expires_at:
            del _cache[key]
            return None

        return deepcopy(value)


def set_cached(key: str, value: Any) -> None:
    with _lock:
        now = monotonic()

        for stale in [k for k, (exp, _) in _cache.items() if now >= exp]:
            del _cache[stale]

        _cache[key] = (now + CACHE_TTL_SECONDS, deepcopy(value))


def invalidate_prefix(prefix: str) -> None:
    with _lock:
        for key in [k for k in _cache if k.startswith(prefix)]:
            del _cache[key]


def invalidate_cache() -> None:
    with _lock:
        _cache.clear()
