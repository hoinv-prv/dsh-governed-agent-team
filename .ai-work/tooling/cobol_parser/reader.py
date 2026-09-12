"""Fixed-format reader — 文法書 2.7.2 正書法 (SRC-ASP-04-…-ch-ng-2-part3-b58c).

TWO physical layouts coexist (CAP-003, measured across 3053 corpus files):

  seq6   the manual's reference format (byte columns):
             cols 1-6 sequence | col 7 indicator | 8-72 areas A+B | 73-80 prog-id
  noseq  how this corpus actually stores members — the sequence area is NOT in
         the file (the library system owns it):
             col 1 indicator | cols 2-66 areas A+B | (nothing beyond col 66)

Both layouts have a 65-byte content region. Detection is per file: a majority
of lines carrying a 6-digit prefix means seq6 (exactly one corpus file does —
MGSUB013.cbl); everything else is noseq. Callers may force `layout=`.

The reader ACCOUNTS for bytes; it does not interpret content. Every physical
line keeps its exact raw bytes (body + EOL), regions are slices of the body,
and render() is the concatenation proof. Lines beginning with 0x1A (DOS EOF
padding, present in this corpus) are kind "padding".
"""
from __future__ import annotations

from dataclasses import dataclass, field

#: Indicator byte → line kind (2.7.2.2 continuation, 2.7.2.4 comment; D = debug line).
_INDICATOR_KINDS = {
    b"*": "comment",
    b"/": "comment",
    b"-": "continuation",
    b"D": "debug",
    b"d": "debug",
    b" ": "code",
    b"": "code",  # line ends before the indicator column
}

#: (indicator_start, content_start, content_end) byte offsets per layout.
#: `indent6` has NO indicator column: six columns are reserved and Area A starts
#: at column 7, so a `*` there is the first character of the content region.
_BOUNDS = {"seq6": (6, 7, 72), "noseq": (0, 1, 66), "indent6": (6, 6, 72)}


@dataclass
class PhysicalLine:
    """One source line, byte-exact: body + eol == raw, regions tile body."""

    line_no: int  # 1-based
    body: bytes
    eol: bytes  # b"\r\n" | b"\n" | b"" (EOF without newline)
    layout: str = "noseq"
    kind: str = "code"  # code | comment | continuation | debug | blank | padding
    cautions: list = field(default_factory=list)

    @property
    def raw(self) -> bytes:
        return self.body + self.eol

    @property
    def seq(self) -> bytes:
        return self.body[0 : _BOUNDS[self.layout][0]]

    @property
    def indicator(self) -> bytes:
        ind, start, _ = _BOUNDS[self.layout]
        return self.body[ind:start]

    @property
    def content(self) -> bytes:
        _, start, end = _BOUNDS[self.layout]
        return self.body[start:end]

    @property
    def progid(self) -> bytes:
        return self.body[_BOUNDS[self.layout][2] :]

    @property
    def content_base_col(self) -> int:
        """1-based source column of the content region's first byte."""
        return _BOUNDS[self.layout][1] + 1

    @property
    def content_width(self) -> int:
        """Bytes the content region spans when the record is fully padded."""
        _, start, end = _BOUNDS[self.layout]
        return end - start


def split_lines(data: bytes) -> list[PhysicalLine]:
    """Split into physical lines preserving every byte (EOL kept per line)."""
    lines: list[PhysicalLine] = []
    start = 0
    n = len(data)
    while start < n:
        nl = data.find(b"\n", start)
        if nl == -1:
            body, eol, next_start = data[start:], b"", n
        elif nl > start and data[nl - 1 : nl] == b"\r":
            body, eol, next_start = data[start : nl - 1], b"\r\n", nl + 1
        else:
            body, eol, next_start = data[start:nl], b"\n", nl + 1
        lines.append(PhysicalLine(line_no=len(lines) + 1, body=body, eol=eol))
        start = next_start
    return lines


def detect_layout(lines: list[PhysicalLine]) -> str:
    """Which physical layout is this file written in?

    Two signals, because the sequence area is user data and is often left BLANK
    — a member with no digits is still seq6, and reading it as noseq turns
    `      *    CALL 'X'` into live code:

    1. a majority of lines carrying a 6-digit sequence number;
    2. no line putting ANYTHING in the first six columns — a blank sequence area
       reserved on every line, which noseq never does (its Area A starts at
       column 2, so a level number or a comment indicator lands there);
    3. otherwise, where the comment indicator sits — column 7 (seq6) or column 1
       (noseq). Only a line whose first six bytes are blank counts for column 7,
       so a noseq banner (`*****…`) cannot be mistaken for one.
    """
    counted = [ln for ln in lines if ln.body.strip()]
    if not counted:
        return "noseq"
    if sum(1 for ln in counted if ln.body[:6].isdigit()) > len(counted) * 0.5:
        return "seq6"
    if all(not ln.body[:6].strip() for ln in counted):
        # Nothing ever uses the first six columns. Column 7 decides which of the
        # two remaining shapes it is: an indicator column there only ever holds
        # an indicator, so a LETTER there means Area A starts at column 7.
        letters = sum(1 for ln in counted if ln.body[6:7].isalpha() and ln.body[6:7] != b"D")
        return "indent6" if letters else "seq6"
    at_1 = sum(1 for ln in counted if ln.body[:1] in (b"*", b"/"))
    at_7 = sum(
        1 for ln in counted if ln.body[6:7] in (b"*", b"/") and not ln.body[:6].strip()
    )
    return "seq6" if at_7 > at_1 else "noseq"


def _classify(line: PhysicalLine) -> None:
    if line.body[:1] == b"\x1a":  # DOS EOF padding tail (corpus reality)
        line.kind = "padding"
        return
    ind_off, _, end = _BOUNDS[line.layout]
    # 2.7.2.3: blank when boundary C..R is all blank — the sequence area is user
    # data and the prog-id area is identification; neither affects the kind.
    if line.body[ind_off:end].strip() == b"":
        line.kind = "blank"
        return
    # `indent6` has no indicator column, so a comment announces itself with a
    # `*` or `/` as the first non-blank character of the content region.
    if not line.indicator and line.content.lstrip()[:1] in (b"*", b"/"):
        line.kind = "comment"
        return
    ind = line.indicator
    kind = _INDICATOR_KINDS.get(ind)
    if kind is None:
        line.kind = "code"
        line.cautions.append(
            f"unknown indicator byte {ind!r} at line {line.line_no} — treated as code"
        )
        return
    line.kind = kind


def read_lines(data: bytes, layout: str | None = None) -> list[PhysicalLine]:
    """Read + classify. `layout` None = auto-detect per file (see module doc)."""
    lines = split_lines(data)
    resolved = layout or detect_layout(lines)
    for line in lines:
        line.layout = resolved
        _classify(line)
    return lines


def render(lines: list[PhysicalLine]) -> bytes:
    """The round-trip proof: the model reproduces the file byte-for-byte."""
    return b"".join(ln.raw for ln in lines)
