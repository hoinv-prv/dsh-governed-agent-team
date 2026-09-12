"""Encoding sniff — same semantics as the cobol-wiki pack config (.ai-work/
cobol_wiki.config.yml `encoding:`): try order IS the label, narrowest first;
NUL in the head window means binary.

The parser itself works on BYTES (reader) and decodes per region (lexer); this
module only answers "which label, and is it text at all".
"""
from __future__ import annotations

TRY_ORDER = ("utf-8", "shift_jis", "cp932")
NUL_WINDOW = 4096


def sniff_encoding(data: bytes, try_order=TRY_ORDER, nul_window: int = NUL_WINDOW) -> str:
    """Return the encoding label for `data`: one of try_order, 'binary', 'undecodable'."""
    if b"\x00" in data[:nul_window]:
        return "binary"
    for enc in try_order:
        try:
            data.decode(enc)
            return enc
        except (UnicodeDecodeError, LookupError):
            continue
    return "undecodable"
