"""ASP FDG (file definition) handler — shallow by design.

The reference corpus stores FDG metas without relations: a summary of the directives and
nothing else. Directive lines are prefixed with `/`, which must be stripped or every
summary carries noise.
"""
from __future__ import annotations

from .base import Extraction, decode, line_count


def extract(path, data: bytes, cfg, file_type: str = "fdg") -> Extraction:
    text, enc = decode(data, cfg)
    out = Extraction(file_type=file_type, encoding=enc, line_count=line_count(text))
    if enc == "binary":
        out.facts["binary"] = True
        return out
    directives = []
    for raw in text.split("\n"):
        s = raw.strip()
        if not s:
            continue
        directives.append(s.lstrip("/"))
    out.facts["directives"] = directives[:12]
    for d in directives:
        head = d.split(None, 1)
        if head and head[0].upper() == "FILE" and len(head) > 1:
            out.facts["file_name"] = head[1].split()[0]
            break
    return out
