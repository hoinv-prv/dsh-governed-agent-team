"""Surgical source edits through the parse.

Change the tokens you meant to change; every other byte — columns, comments,
odd spacing, the DOS EOF marker, the line endings — comes back identical. That
is what makes an automated migration edit reviewable: the diff shows only what
was intended, so a reviewer reads the change instead of hunting for it.

Fixed format adds a rule no text editor enforces. Content lives between two
margins, so a replacement is padded when it is shorter (later columns must not
shift) and REFUSED when it would run past the right margin — better to fail here
than to have the compiler truncate the line later.
"""
from __future__ import annotations


class RewriteError(Exception):
    """An edit that cannot be made safely."""


class TokenRewriter:
    """Collects token replacements and renders the file with them applied."""

    def __init__(self, lines, tokens):
        self._lines = lines
        self._tokens = tokens
        self._by_line: dict[int, list] = {}
        self._edited: set[int] = set()

    def replace(self, token, text: str) -> None:
        """Replace one token's text, keeping the quotes of a literal."""
        if id(token) in self._edited:
            raise RewriteError(f"token {token.text!r} was already replaced")
        if len(token.segments) != 1:
            # A token continued across lines has no single byte span to swap.
            raise RewriteError(
                f"token {token.text!r} spans {len(token.segments)} lines; "
                f"rewrite it through the continuation instead"
            )
        line_no, start, end = token.segments[0]
        line = self._line(line_no)
        encoding = "cp932"

        new = f"{token.quote}{text}{token.quote}" if token.type == "STRING" else text
        raw = new.encode(encoding)
        room = len(line.content) - start if end >= len(line.content) else end - start
        if len(raw) > room:
            width = line.content_width
            raise RewriteError(
                f"{new!r} needs {len(raw)} bytes but only {room} are left before the "
                f"right margin (content region is {width} bytes)"
            )
        # Pad so that everything to the right keeps its column.
        raw = raw.ljust(end - start) if end - start >= len(raw) else raw
        self._by_line.setdefault(line_no, []).append((start, end, raw))
        self._edited.add(id(token))

    def render(self) -> bytes:
        """The file, with every replacement applied and nothing else changed."""
        out = bytearray()
        for line in self._lines:
            edits = self._by_line.get(line.line_no)
            if not edits:
                out += line.raw
                continue
            _, content_start, _ = _bounds(line)
            body = bytearray(line.body)
            for start, end, raw in sorted(edits, reverse=True):
                a, b = content_start + start, content_start + end
                body[a:b] = raw
            out += bytes(body) + line.eol
        return bytes(out)

    def _line(self, line_no: int):
        for line in self._lines:
            if line.line_no == line_no:
                return line
        raise RewriteError(f"no line {line_no}")


def _bounds(line):
    from .reader import _BOUNDS

    return _BOUNDS[line.layout]
