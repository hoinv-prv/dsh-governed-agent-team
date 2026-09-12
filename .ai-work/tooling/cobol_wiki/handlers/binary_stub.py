"""Binary-by-design artifacts: emit a `not_meta_applicable` stub, never a fake summary.

Policy lives in the project's binary meta policy; the stub records WHY the artifact has no
text meta so the gap is a documented decision rather than an omission.
"""
from __future__ import annotations

from .base import Extraction, decode


def extract(path, data: bytes, cfg, file_type: str = "") -> Extraction:
    _text, enc = decode(data, cfg)
    out = Extraction(file_type=file_type, encoding="binary", line_count=0)
    out.facts["not_meta_applicable"] = True
    out.facts["binary_reason"] = f"{file_type or 'unknown'}_binary"
    if enc != "binary":
        out.facts["binary_reason"] = f"{file_type or 'unknown'}_by_policy"
    return out
