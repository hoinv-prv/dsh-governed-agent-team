"""ASP COBOL G parser front-end — a standalone COBOL parsing library.

Authority: ASP COBOL G 文法書 V13～ (wiki sources SRC-ASP-04-asp-cobol-g-v13-0a47-*).
Design: docs/superpowers/specs/2026-08-07-asp-cobol-parser-design.md (AIP-EXEC-048).

STANDALONE BY CONTRACT: stdlib only, no dependency on cobol_wiki, on AIWS
tooling, or on any project layout — consumers depend on this package, never the
reverse (enforced by tests/test_standalone.py). Today's consumers are the
cobol-wiki meta builder, migration analysis, and source transformation.

Ground truth is BYTES: the model never re-encodes text to reproduce a file —
`render()` concatenates the original byte regions, and the round-trip gate
proves every byte of every file is accounted for by the model.

    import cobol_parser
    prog = cobol_parser.parse(open("PGM.COB", "rb").read())
    refs = cobol_parser.extract_refs(open("PGM.COB", "rb").read())

Layers, each usable on its own:
    decode.sniff_encoding  bytes -> encoding label (or 'binary')
    reader.read_lines      bytes -> physical lines (fixed-format regions)
    reader.render          lines -> bytes (byte-identical round trip)
    lexer.lex              lines -> tokens (value + byte footprint)
    structure.parse_program lines+tokens -> Program (divisions … statements)
    extract.extract_refs   bytes -> references (calls / copybooks / file assigns)
"""
from .decode import TRY_ORDER, sniff_encoding
from .expand import Expansion, ExpansionError, expand
from .extract import extract_from_model, extract_refs
from .lexer import Token, lex
from .rewrite import RewriteError, TokenRewriter
from .reader import PhysicalLine, detect_layout, read_lines, render, split_lines
from .reserved import RESERVED_WORDS
from .structure import (
    VERBS,
    DataEntry,
    Division,
    Paragraph,
    Program,
    Section,
    Sentence,
    Statement,
    classify_sentence,
    parse_program,
)

__all__ = [
    "TRY_ORDER", "sniff_encoding",
    "PhysicalLine", "split_lines", "read_lines", "render", "detect_layout",
    "Token", "lex", "RESERVED_WORDS",
    "Program", "Division", "Section", "Paragraph", "Sentence", "Statement",
    "DataEntry", "VERBS", "parse_program", "classify_sentence",
    "extract_refs", "extract_from_model",
    "expand", "Expansion", "ExpansionError",
    "TokenRewriter", "RewriteError",
    "parse",
]


def parse(data: bytes, encoding: str = "") -> Program:
    """bytes -> Program, in one call. `encoding` empty = sniff it."""
    enc = encoding or sniff_encoding(data)
    if enc in ("binary", "undecodable"):
        raise ValueError(f"not COBOL text: {enc}")
    lines = read_lines(data)
    return parse_program(lines, lex(lines, encoding=enc))
