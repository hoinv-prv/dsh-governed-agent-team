"""The COBOL handler: references read from a PARSE of the source.

References come from the token/statement model rather than from text matching,
so a `CALL` inside a literal or a `COPY` on a comment line can never match, a
`COPY x OF lib` keeps its library wherever it sits on the line, and a member
stored with sequence numbers is read on the right columns.

`handlers.cobol_regex` is the previous, regex-based implementation, kept as the
dependency-free fallback and as the thing this one is measured against. Over all
5467 COBOL files of the reference corpus (AIP-EXEC-048) the two disagree on 61
files and the parse is right on all 61: the regex version invents 64 references
whose "name" is a keyword or a word inside a string literal, loses the library
on 7, misses 6 copybooks, and misses one program's PROGRAM-ID together with all
three of its file assignments.

DEPENDENCY DIRECTION: cobol_wiki depends on `cobol_parser`, never the reverse.
`cobol_parser` is a standalone stdlib-only library (its own tests enforce that),
so it also serves consumers that have nothing to do with the wiki — migration
analysis, source transformation. Install it beside this package (this project
ships it at `.ai-work/tooling/cobol_parser`, source in `packages/cobol_parser`).
An install that cannot provide it can fall back in the pack config:

    handlers:
      cobol: cobol_wiki.handlers.cobol_regex

Fields the pack derives outside extraction (encoding label, line count,
business name) reuse `handlers.base` unchanged, so switching handlers changes
only what statement reading changes.
"""
from __future__ import annotations

#: Read by `build_pack.py` WITHOUT importing this module (it cannot be imported where the
#: dependency is missing — which is exactly the case being guarded). The pack build refuses
#: to ship a config naming a handler that fails to import and offers no working substitute,
#: so this constant is the difference between a documented dependency and a broken pack.
FALLBACK_HANDLER = "cobol_wiki.handlers.cobol_regex"

from cobol_parser.lexer import lex  # noqa: E402
from cobol_parser.reader import read_lines
from cobol_parser.structure import parse_program
from cobol_parser.extract import extract_from_model

from .base import Extraction, RawRef, business_name, decode, line_count


def extract(path, data: bytes, cfg, file_type: str = "cobol") -> Extraction:
    text, enc = decode(data, cfg)
    out = Extraction(file_type=file_type, encoding=enc, line_count=line_count(text))
    if enc == "binary":
        out.facts["binary"] = True
        return out

    out.business_name = business_name(text, cfg)

    lines = read_lines(data)
    lex_cautions: list[str] = []
    tokens = lex(lines, encoding=enc, cautions=lex_cautions)
    prog = parse_program(lines, tokens)
    res = extract_from_model(prog)

    out.program_id = res["program_id"]
    # Diagnostics from every layer, not just extraction: a content region that
    # did not decode, or a `*` in an unexpected column, is exactly what a
    # reviewer of this meta needs to see.
    out.cautions.extend(c for ln in lines for c in ln.cautions)
    out.cautions.extend(lex_cautions)
    out.cautions.extend(prog.cautions)
    out.cautions.extend(res["cautions"])

    content_of = {ln.line_no: ln.content for ln in lines}

    def src_line(no: int) -> str:
        return content_of.get(no, b"").decode(enc, errors="replace").strip()

    seen: set[tuple[str, str]] = set()
    for r in res["refs"]:
        seen.add((r["role"], r["name"]))
        out.refs.append(
            RawRef(r["name"], r["role"], r["lib"], r["kind"], r["line"], src_line(r["line"]))
        )

    # File access — same policy as the regex handler: the raw token is kept as a
    # fact, and the device-prefix classification stays owned by the config.
    for token in res["assigns"]:
        out.facts.setdefault("assigns", []).append(token)
        name, kind, role = cfg.classify_assign(token)
        if name and (role, name.upper()) not in seen:
            seen.add((role, name.upper()))
            out.refs.append(RawRef(name.upper(), role, "", f"ASSIGN/{kind}", 0, token))

    out.facts["call_count"] = sum(1 for r in out.refs if r.role == "calls")
    out.facts["copy_count"] = sum(1 for r in out.refs if r.role == "x:uses")
    return out
