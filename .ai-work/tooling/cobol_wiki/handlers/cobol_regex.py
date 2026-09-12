"""ASP / Fujitsu COBOL handler — REGEX implementation, kept as the fallback.

`handlers.cobol` is the default and reads a parse instead of matching text; use this one
only where the `cobol_parser` library cannot be installed. Text matching cannot see
structure, and the corpus shows what that costs (AIP-EXEC-048 adjudication, all 5467 COBOL
files, 61 disagreements, the parse right on every one):

  * `COPY KEY OF <book>` yields a reference NAMED `KEY` whose "library" is the real
    copybook (49 files); `COPY ALL OF <book>` yields `ALL` and loses the copybook (6);
  * the `COPY` inside the paragraph name `TBL-COPY SECTION.` yields `SECTION` (5), and the
    one inside `DISPLAY "ITEM COPY ERROR …"` yields `ERROR` (1);
  * `^`-anchored patterns lose the library on a mid-line `COPY x OF lib` and miss
    PROGRAM-ID / SELECT entirely on a member stored with sequence numbers.

COBOL invocation is far simpler than CL — a `CALL 'literal'` and nothing exotic — and a
plain literal matcher measured precision 100% / recall 96.3% against the reference corpus,
with every miss traced to a resolution-index gap rather than to extraction. The COPY
syntax variants are absorbed from the project's `extract_cobol_copy_deps.py`.

`SELECT … ASSIGN TO` is captured here but its device-prefix normalization and the choice
of edge role (accesses / reads / writes) belong to the file-access pass, which is the one
part of this pack with no prior implementation to absorb.
"""
from __future__ import annotations

import re

from .base import Extraction, RawRef, business_name, decode, is_comment_cobol, line_count

RE_PROGRAM_ID = re.compile(r"^\s*PROGRAM-ID\.\s*([A-Z0-9$#@_-]+)", re.IGNORECASE | re.MULTILINE)
RE_CALL_LIT = re.compile(r"\bCALL\s+['\"]([^'\"]+)['\"]", re.IGNORECASE)
RE_CALL_IDENT = re.compile(r"\bCALL\s+(?!['\"])([A-Z][A-Z0-9-]*)", re.IGNORECASE)

# `COPY x.` / `COPY x OF lib.` / `COPY ALL RECORDS OF x` / `COPY KEY OF x` / `COPY x REPLACING …`
#
# The keyword forms name the copybook AFTER the keyword. Reading the keyword itself as the
# name does double damage: the real target is lost AND a bogus one is invented — measured
# on `COPY KEY OF ITEMK1 JOINING 'NA' TO ALL NAMES PREFIX END-COPY.`, which yielded a
# copybook called `KEY`.
RE_COPY_KEYWORD_OF = re.compile(
    r"\bCOPY\s+(?:ALL\s+RECORDS|KEY|RECORD)\s+OF\s+([A-Z0-9$#@_-]+)", re.IGNORECASE
)
RE_COPY_OF_LIB = re.compile(
    r"^\s*COPY\s+([A-Z0-9$#@_-]+)\s+OF\s+([A-Z0-9$#@_-]+)", re.IGNORECASE | re.MULTILINE
)
# NOT anchored to the line start: a copybook is routinely pulled in mid-line after a data
# item, e.g. `01  CREC.       COPY CTRKJNR.` — anchoring lost 79 edges on one system alone.
# `END-COPY.` cannot match because no whitespace follows the keyword there.
RE_COPY_PLAIN = re.compile(r"\bCOPY\s+([A-Z0-9$#@_-]+)", re.IGNORECASE)
#: Words that follow COPY as syntax, never as a copybook name.
COPY_KEYWORDS = {"ALL", "REPLACING", "OF", "IN", "SUPPRESS", "KEY", "RECORD", "RECORDS"}
# `TO` is OPTIONAL: `SELECT AFILE ASSIGN ITEMK1.` occurs alongside the `ASSIGN TO` form in
# the same corpus, and requiring the keyword dropped those file references entirely.
# The trailing period is stripped by the caller — leaving it in made the token compare
# unequal to every other spelling of the same file name.
RE_SELECT = re.compile(
    r"^\s*SELECT\s+(?:OPTIONAL\s+)?\S+\s+ASSIGN\s+(?:TO\s+)?([A-Z0-9$#@_.-]+)",
    re.IGNORECASE | re.MULTILINE,
)
#: Screen/form definitions pulled in by name, e.g. `COPY <form>FM OF XMDLIB`.
RE_SMD_COPY = re.compile(
    r"^\s*COPY\s+([A-Z0-9$#@_-]+)FM\s+OF\s+([A-Z0-9$#@_-]+)", re.IGNORECASE | re.MULTILINE
)


def _code_only(text: str, include_comments: bool) -> str:
    if include_comments:
        return text
    return "\n".join(ln for ln in text.split("\n") if not is_comment_cobol(ln))


def _line_of(text: str, needle_line: str) -> int:
    for i, ln in enumerate(text.split("\n"), 1):
        if ln.strip() == needle_line.strip():
            return i
    return 0


def extract(path, data: bytes, cfg, file_type: str = "cobol") -> Extraction:
    text, enc = decode(data, cfg)
    out = Extraction(file_type=file_type, encoding=enc, line_count=line_count(text))
    if enc == "binary":
        out.facts["binary"] = True
        return out

    out.business_name = business_name(text, cfg)

    body = _code_only(text, cfg.include_commented_statements)
    m = RE_PROGRAM_ID.search(body)
    out.program_id = m.group(1).upper() if m else ""

    seen: set[tuple[str, str]] = set()

    def add(name: str, role: str, kind: str, lib: str = "", line: str = "") -> None:
        key = (role, name.upper())
        if key in seen:
            return
        seen.add(key)
        out.refs.append(
            RawRef(name.upper(), role, lib.upper(), kind, _line_of(text, line), line.strip())
        )

    for raw in body.split("\n"):
        for m in RE_CALL_LIT.finditer(raw):
            add(m.group(1), "calls", "CALL", line=raw)
        # A `CALL <identifier>` passes a program name held in a variable; the target is
        # not knowable from source, so record a caution instead of inventing an edge.
        for m in RE_CALL_IDENT.finditer(raw):
            token = m.group(1).upper()
            if token not in ("USING", "BY", "RETURNING"):
                out.cautions.append(
                    f"CALL via identifier {token!r} — target resolved at runtime, no edge emitted"
                )

    for m in RE_SMD_COPY.finditer(body):
        add(m.group(1), "x:uses", "COPY-FORM", m.group(2), m.group(0))
    for m in RE_COPY_KEYWORD_OF.finditer(body):
        add(m.group(1), "x:uses", "COPY-KEYWORD-OF", line=m.group(0))
    for m in RE_COPY_OF_LIB.finditer(body):
        add(m.group(1), "x:uses", "COPY-OF", m.group(2), m.group(0))
    for m in RE_COPY_PLAIN.finditer(body):
        token = m.group(1).upper()
        if token not in COPY_KEYWORDS:
            add(token, "x:uses", "COPY", line=m.group(0))

    # File access. The ASSIGN device prefix carries the file's CATEGORY and the category
    # picks the role -- `data` reads, everything else a generic access. The raw token is
    # kept in facts as well, because a report that only shows the normalized name cannot
    # explain why a file was classified the way it was.
    for m in RE_SELECT.finditer(body):
        token = m.group(1).upper().rstrip(".")
        out.facts.setdefault("assigns", []).append(token)
        name, kind, role = cfg.classify_assign(token)
        if name:
            add(name, role, f"ASSIGN/{kind}", line=m.group(0))

    out.facts["call_count"] = sum(1 for r in out.refs if r.role == "calls")
    out.facts["copy_count"] = sum(1 for r in out.refs if r.role == "x:uses")
    return out
