"""Handler registry — resolved from config dotted paths, never a hardcoded table."""
from __future__ import annotations

import importlib
from functools import lru_cache


@lru_cache(maxsize=None)
def _load(dotted: str):
    module = importlib.import_module(dotted)
    if not hasattr(module, "extract"):
        raise ImportError(f"handler {dotted!r} has no `extract(path, data, cfg, file_type)`")
    return module


def for_file_type(file_type: str, cfg):
    """The handler configured for this file_type, else the `*` fallback."""
    dotted = cfg.handlers.get(file_type) or cfg.handlers.get("*")
    if not dotted:
        raise KeyError(f"no handler configured for file_type {file_type!r} and no '*' fallback")
    return _load(dotted)
