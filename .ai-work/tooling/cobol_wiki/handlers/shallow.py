"""Minimal handler: a meta exists and is findable, but the artifact is not text-parsable.

Used for formats the reference corpus records with a `(binary)` summary rather than a
`not_meta_applicable` stub — they are real artifacts worth finding, just not readable here.
"""
from __future__ import annotations

from .base import Extraction, decode, line_count


def extract(path, data: bytes, cfg, file_type: str = "") -> Extraction:
    text, enc = decode(data, cfg)
    out = Extraction(
        file_type=file_type, encoding=enc, line_count=0 if enc == "binary" else line_count(text)
    )
    out.facts["shallow"] = True
    if enc == "binary":
        out.facts["binary"] = True
    return out
