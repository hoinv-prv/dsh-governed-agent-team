"""P1 round-trip gate — the checks that prove the byte model is complete.

Per file:
  render_identity  render(read_lines(data)) == data   (reader accounts for every byte)
  tile             every lexed line's content region is exactly covered by
                   token footprints (lexer view is complete)

Status: pass | fail | unreadable (binary / undecodable). A fail carries the
first violations so each one can be traced to a file/line (AIP-EXEC-048 STEP-01
Done Condition).
"""
from __future__ import annotations

from .decode import sniff_encoding
from .lexer import lex
from .reader import read_lines, render

_LEXABLE = ("code", "continuation", "debug")


def check_tiles(lines, tokens) -> list[str]:
    """Return violations of the tile invariant (empty = complete coverage)."""
    lexable = {ln.line_no: len(ln.content) for ln in lines if ln.kind in _LEXABLE}
    covered = {no: [] for no in lexable}
    violations = []
    for tok in tokens:
        for (no, start, end) in tok.segments:
            if no not in covered:
                violations.append(f"line {no}: segment on non-lexable line")
                continue
            covered[no].append((start, end))
    for no, spans in sorted(covered.items()):
        spans.sort()
        pos = 0
        for start, end in spans:
            if start != pos:
                violations.append(f"line {no}: gap/overlap at byte {pos} (next segment starts {start})")
                break
            pos = end
        else:
            if pos != lexable[no]:
                violations.append(f"line {no}: bytes {pos}..{lexable[no]} not covered")
    return violations


def check_file(data: bytes) -> dict:
    enc = sniff_encoding(data)
    if enc in ("binary", "undecodable"):
        return {"status": "unreadable", "encoding": enc, "line_count": 0,
                "violations": [], "cautions": []}
    lines = read_lines(data)
    violations = []
    if render(lines) != data:
        violations.append("render() is not byte-identical")
    cautions: list[str] = [c for ln in lines for c in ln.cautions]
    tokens = lex(lines, encoding=enc, cautions=cautions)
    violations.extend(check_tiles(lines, tokens))
    return {
        "status": "fail" if violations else "pass",
        "encoding": enc,
        "line_count": len(lines),
        "violations": violations[:10],
        "cautions": cautions[:10],
        "caution_count": len(cautions),
    }
