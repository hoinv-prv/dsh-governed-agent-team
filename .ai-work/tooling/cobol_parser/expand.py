"""COPY expansion — 付録B.2 書き方.

    COPY 原文名-1 [OF|IN 登録集名-1]
    [REPLACING {定数-1|語-1} BY {定数-2|語-2} …]
    [JOINING 語-3 [TO ALL NAMES] AS {PREFIX|SUFFIX}]

Expansion is OPT-IN and produces a VIEW: the file's bytes are never touched, so
the round-trip guarantee of the byte model still holds over the original. A wiki
builder wants the COPY statement itself; data-lineage work wants the text it
pulls in. Both read the same source.

The library never guesses where a copybook lives — the caller passes a resolver,
`(name, library_hint) -> bytes | None`. That is what keeps this package usable
outside the project it was written in.

A copybook that cannot be resolved leaves its COPY statement in place and raises
a caution: silently dropping the statement would make the reference disappear
from a view that is supposed to contain MORE than the source, not less.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .decode import sniff_encoding
from .lexer import lex
from .reader import read_lines
from .reserved import RESERVED_WORDS

#: Words that follow COPY as syntax, never as a copybook name (書き方 keywords).
_COPY_KEYWORDS = {"ALL", "REPLACING", "OF", "IN", "SUPPRESS", "KEY", "RECORD", "RECORDS"}
_MAX_DEPTH = 20


class ExpansionError(Exception):
    """A copybook cannot be expanded — today, only a cycle."""


@dataclass
class Expansion:
    """The expanded token view of one source file."""

    tokens: list = field(default_factory=list)
    cautions: list = field(default_factory=list)
    #: copybook name → how many times its text was inserted
    included: dict = field(default_factory=dict)


def _decode(data: bytes) -> tuple[list, list, str]:
    enc = sniff_encoding(data)
    if enc in ("binary", "undecodable"):
        raise ExpansionError(f"not COBOL text: {enc}")
    lines = read_lines(data)
    cautions: list[str] = []
    return lines, lex(lines, encoding=enc, cautions=cautions), cautions


def _significant(tokens):
    return [t for t in tokens if t.type not in ("SPACE", "COMMENT", "COMMENT_ENTRY")]


def _copy_span(tokens: list, start: int) -> int:
    """Index just past the COPY statement that begins at `start`.

    A COPY ends at its own period, or at END-COPY — the ASP form writes both.
    """
    i = start
    while i < len(tokens):
        tok = tokens[i]
        if tok.type == "SEP" and tok.text == ".":
            return i + 1
        if tok.type == "WORD" and tok.text.upper() == "END-COPY":
            j = i + 1
            if j < len(tokens) and tokens[j].type == "SEP" and tokens[j].text == ".":
                return j + 1
            return j
        i += 1
    return len(tokens)


def _parse_copy(tokens: list) -> dict:
    """The clauses of one COPY statement (書き方 付録B.2)."""
    words = _significant(tokens)[1:]  # drop COPY
    out = {"name": "", "lib": "", "replacing": [], "joining": "", "as": ""}
    if not words:
        return out

    # `COPY ALL|KEY|RECORD OF <book>` — the keyword forms name the book AFTER it
    first = words[0].text.upper() if words[0].type == "WORD" else ""
    idx = 0
    if first in ("ALL", "KEY", "RECORD", "RECORDS"):
        for j, tok in enumerate(words):
            if tok.type == "WORD" and tok.text.upper() in ("OF", "IN"):
                idx = j + 1
                break
        else:
            return out
    if idx >= len(words):
        return out
    head = words[idx]
    if head.type != "WORD" or head.text.upper() in _COPY_KEYWORDS:
        return out
    out["name"] = head.text.upper()
    rest = words[idx + 1 :]

    if rest and rest[0].type == "WORD" and rest[0].text.upper() in ("OF", "IN"):
        if len(rest) > 1 and rest[1].type == "WORD":
            out["lib"] = rest[1].text.upper()
        rest = rest[2:]

    def cut(word: str):
        for j, tok in enumerate(rest):
            if tok.type == "WORD" and tok.text.upper() == word:
                return j
        return -1

    r, j = cut("REPLACING"), cut("JOINING")
    if r != -1:
        chunk = rest[r + 1 : j if j > r else len(rest)]
        pair: list = []
        for tok in chunk:
            if tok.type == "WORD" and tok.text.upper() == "BY":
                continue
            if tok.type in ("WORD", "STRING", "NUMBER"):
                pair.append(tok)
                if len(pair) == 2:
                    out["replacing"].append((pair[0], pair[1]))
                    pair = []
    if j != -1:
        chunk = rest[j + 1 :]
        if chunk and chunk[0].type in ("STRING", "WORD"):
            out["joining"] = chunk[0].text.upper()
        for k, tok in enumerate(chunk):
            if tok.type == "WORD" and tok.text.upper() == "AS" and k + 1 < len(chunk):
                out["as"] = chunk[k + 1].text.upper()
        # `AS` is a 補助語 — 49 corpus statements write `JOINING x [TO ALL
        # NAMES] {PREFIX|SUFFIX}` without it. 48 say PREFIX, which the default
        # below happened to match; ONE says SUFFIX (ITM101CG.COB:63) and was
        # being PREFIXED instead, renaming every name from that copybook the
        # wrong way round with nothing to signal it.
        if not out["as"]:
            for tok in chunk[1:]:
                if tok.type == "WORD" and tok.text.upper() in ("PREFIX", "SUFFIX"):
                    out["as"] = tok.text.upper()
                    break
    return out


def _key(tok) -> str:
    return f"{tok.type}:{tok.text.upper()}"


def _apply(tokens: list, clauses: dict, origin: str) -> list:
    """REPLACING then JOINING, over a copybook's tokens (書き方 order)."""
    import copy as _copy

    pairs = {_key(a): b for a, b in clauses["replacing"]}
    joining, mode = clauses["joining"], clauses["as"]
    out = []
    for tok in tokens:
        new = _copy.copy(tok)
        new.origin = origin
        repl = pairs.get(_key(tok))
        if repl is not None:
            new.text = repl.text
            new.type = repl.type
        elif joining and new.type == "WORD" and new.text.upper() not in RESERVED_WORDS:
            # JOINING renames every user NAME — never a reserved word, never a
            # literal (書き方: 語-3 … TO ALL NAMES)
            if mode == "SUFFIX":
                new.text = f"{new.text}-{joining}"
            else:  # PREFIX is the default when AS is omitted
                new.text = f"{joining}-{new.text}"
        out.append(new)
    return out


def expand(data: bytes, resolve, *, _stack: tuple = (), _depth: int = 0) -> Expansion:
    """Token view of `data` with every COPY replaced by the text it pulls in.

    `resolve(name, library_hint) -> bytes | None` decides where a copybook lives.
    """
    lines, tokens, cautions = _decode(data)
    out = Expansion(cautions=list(cautions))

    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if not (tok.type == "WORD" and tok.text.upper() == "COPY" and tok.reserved):
            if not hasattr(tok, "origin"):
                tok.origin = ""
            out.tokens.append(tok)
            i += 1
            continue

        end = _copy_span(tokens, i)
        clauses = _parse_copy(tokens[i:end])
        name = clauses["name"]
        book = resolve(name, clauses["lib"]) if name else None

        if book is None:
            out.cautions.append(
                f"COPY {name or '?'} — not resolvable; statement left unexpanded"
            )
            for t in tokens[i:end]:
                if not hasattr(t, "origin"):
                    t.origin = ""
                out.tokens.append(t)
            i = end
            continue

        if name in _stack:
            raise ExpansionError(
                f"COPY {name} includes itself: {' -> '.join((*_stack, name))}"
            )
        if _depth >= _MAX_DEPTH:
            raise ExpansionError(f"COPY nesting deeper than {_MAX_DEPTH}: {name}")

        try:
            inner = expand(book, resolve, _stack=(*_stack, name), _depth=_depth + 1)
        except ExpansionError as exc:
            # A copybook that is binary, or that loops, says something about THAT
            # member — the program including it is still perfectly readable, and
            # failing the whole file loses everything else in it.
            out.cautions.append(f"COPY {name} — {exc}; statement left unexpanded")
            for t in tokens[i:end]:
                if not hasattr(t, "origin"):
                    t.origin = ""
                out.tokens.append(t)
            i = end
            continue
        out.cautions.extend(inner.cautions)
        for key, n in inner.included.items():
            out.included[key] = out.included.get(key, 0) + n
        out.included[name] = out.included.get(name, 0) + 1
        out.tokens.extend(_apply(inner.tokens, clauses, name))
        i = end

    return out
