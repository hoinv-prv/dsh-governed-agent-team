"""Reference extraction over a parsed program (AIP-EXEC-048 STEP-02).

The golden-diff counterpart is the pack's regex implementation, now
`cobol_wiki/handlers/cobol_regex.py`.

Reads statements, not raw text, so a `CALL` inside a literal or a `COPY` on a
comment line can never match. Emits the SAME shapes and dedup behavior as the
regex handler — including its two-refs quirk for form copies (`COPY xxFM OF
lib` → base/COPY-FORM + full/COPY-OF) — so every golden diff is attributable.
"""
from __future__ import annotations

from .decode import sniff_encoding
from .lexer import lex
from .reader import read_lines
from .structure import parse_program

#: Words that follow COPY as syntax, never as a copybook name (regex handler parity).
_COPY_KEYWORDS = {"ALL", "REPLACING", "OF", "IN", "SUPPRESS", "KEY", "RECORD", "RECORDS"}
_CALL_SKIP = {"USING", "BY", "RETURNING"}


def _sig(tokens):
    return [t for t in tokens if t.type in ("WORD", "NUMBER", "STRING")]


def extract_refs(data: bytes) -> dict:
    enc = sniff_encoding(data)
    if enc in ("binary", "undecodable"):
        return {"program_id": "", "refs": [], "assigns": [], "cautions": [],
                "encoding": enc, "status": "unreadable"}
    lines = read_lines(data)
    cautions: list[str] = []
    tokens = lex(lines, encoding=enc, cautions=cautions)
    prog = parse_program(lines, tokens)
    out = extract_from_model(prog)
    out["encoding"] = enc
    # Every layer's diagnostics, in reading order: the reader saw the columns,
    # the lexer saw the bytes, the parser saw the shape. A consumer that only
    # got the extraction's own cautions would report clean output over a file
    # whose content region never decoded.
    out["cautions"] = (
        [c for ln in lines for c in ln.cautions] + cautions + prog.cautions + out["cautions"]
    )
    return out


def extract_from_model(prog) -> dict:
    """Extraction over an already-parsed Program (adapter entry point)."""
    out = {"program_id": prog.program_id, "refs": [], "assigns": [], "cautions": []}

    seen: set[tuple[str, str]] = set()

    def add(name: str, role: str, kind: str, lib: str = "", line_no: int = 0) -> None:
        key = (role, name.upper())
        if key in seen:
            return
        seen.add(key)
        out["refs"].append(
            {"name": name.upper(), "role": role, "lib": lib.upper(), "kind": kind, "line": line_no}
        )

    for div in prog.divisions:
        # SELECT … ASSIGN [TO] — a sentence-level clause, not a statement verb.
        # Scan EVERY SELECT in the sentence: a line missing its period glues the
        # next SELECT into the same sentence (corpus reality, e.g. AC600M1.PRC).
        for sent in div.sentences():
            words = [t.text.upper() for t in _sig(sent.tokens)]
            if not words or words[0] != "SELECT":
                continue
            for k, w in enumerate(words):
                if w != "ASSIGN":
                    continue
                j = k + 1
                if j < len(words) and words[j] == "TO":
                    j += 1
                if j < len(words) and words[j] != "SELECT":
                    out["assigns"].append(words[j])

        # COPY hides inside data entries too — see Division.compiler_directing
        for st in div.compiler_directing("COPY"):
            _extract_copy(st, add)

        for st in div.statements():
            if st.verb == "CALL":
                args = _sig(st.tokens[1:])
                if not args:
                    continue
                target = args[0]
                if target.type == "STRING":
                    # A literal split across lines keeps the blanks running to
                    # the end of the continued line (文法書 2.7.2.2) — that is
                    # what the compiler sees, so the halves are NOT joined. Such
                    # a name can never resolve, so say so instead of emitting a
                    # reference that quietly matches nothing.
                    if " " in target.text.strip():
                        out["cautions"].append(
                            f"CALL target {target.text.strip()!r} contains blanks — a "
                            f"continuation literal carries the blanks to the end of the "
                            f"continued line; verify the source"
                        )
                    add(target.text, "calls", "CALL", line_no=st.line_no)
                elif target.type == "WORD" and target.text.upper() not in _CALL_SKIP:
                    out["cautions"].append(
                        f"CALL via identifier {target.text.upper()!r} — target resolved "
                        f"at runtime, no edge emitted"
                    )
            elif st.verb == "COPY":
                _extract_copy(st, add)

    return out


def _extract_copy(st, add) -> None:
    words = [
        (t.text.upper() if t.type in ("WORD", "NUMBER") else None)
        for t in _sig(st.tokens)
    ]
    # words[0] == 'COPY'
    if len(words) < 2 or words[1] is None:
        return
    first = words[1]

    # keyword forms name the copybook AFTER the keyword: ALL RECORDS OF x / KEY OF x / RECORD OF x
    if first in ("ALL", "KEY", "RECORD"):
        try:
            k = words.index("OF", 1)
        except ValueError:
            return
        if k + 1 < len(words) and words[k + 1]:
            add(words[k + 1], "x:uses", "COPY-KEYWORD-OF", line_no=st.line_no)
        return

    if first in _COPY_KEYWORDS:
        return

    name = first
    lib = ""
    if len(words) > 3 and words[2] in ("OF", "IN") and words[3]:
        lib = words[3]

    if lib:
        # regex-handler parity: a form copy emits both the FM-stripped COPY-FORM
        # ref and the full-name COPY-OF ref (different dedup keys)
        if name.endswith("FM") and len(name) > 2:
            add(name[:-2], "x:uses", "COPY-FORM", lib, st.line_no)
        add(name, "x:uses", "COPY-OF", lib, st.line_no)
    else:
        add(name, "x:uses", "COPY", line_no=st.line_no)
