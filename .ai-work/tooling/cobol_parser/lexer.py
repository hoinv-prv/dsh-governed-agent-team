"""Lexer — 文法書 2.4.2 分離符・語・定数 + 2.7.2.2 行のつなぎ.

Authority: SRC-ASP-04-asp-cobol-g-v13-0a47-ch-ng-2-part1-20c6 (lexical),
…-ch-ng-2-part3-b58c (continuation), …-ph-l-c-e-e578 (reserved words).

Two distinct notions per token, on purpose:
  - `text`      the logical VALUE (a continued literal's value includes the
                continued line's trailing blanks but not the resume quote)
  - `segments`  the byte FOOTPRINT [(line_no, start, end) within the content
                region] — the tile invariant says the footprints of all tokens
                exactly cover every lexed line's content region.

The lexer is a view; render() never depends on it. A line whose content region
does not decode (e.g. a DBCS char split by the col-72 boundary) becomes one RAW
token with a caution — the view degrades, the byte model does not.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from .reserved import RESERVED_WORDS

_LEXABLE = ("code", "continuation", "debug")
_PREFIXED_QUOTE = re.compile(r"(NC|NX|X|B)?(['\"])", re.IGNORECASE)
_OPERATORS = ("**", "<=", ">=", "<>", "+", "-", "*", "/", "=", "<", ">")
_SINGLE_SEPS = ".,;():"
#: ID-division paragraphs whose body is a 注記項 (comment-entry, 2.4.2.2.4) —
#: free text, ends at the next line starting in Area A (2.7.3.4). All are
#: reserved words, so they cannot be user paragraph names elsewhere.
_COMMENT_ENTRY_PARAS = frozenset(
    ("AUTHOR", "INSTALLATION", "DATE-WRITTEN", "DATE-COMPILED", "SECURITY", "REMARKS")
)


def _is_word_char(ch: str) -> bool:
    return ch.isalnum() and ch.isascii() or ch == "-" or not ch.isascii() and not ch.isspace()


@dataclass
class Token:
    type: str  # WORD | NUMBER | STRING | PICTURE | SEP | OP | SPACE | COMMENT | RAW
    text: str
    segments: list = field(default_factory=list)  # [(line_no, byte_start, byte_end)]
    reserved: bool = False
    prefix: str = ""  # STRING only: "" | X | NC | NX | B
    quote: str = ""  # STRING only


class _Lexer:
    def __init__(self, encoding: str):
        self.encoding = encoding
        self.tokens: list[Token] = []
        self.cautions: list[str] = []
        # cross-line state
        self.open_string: Token | None = None
        self.pic_pending = False
        self.fw_warned = False  # full-width-space caution: once per file
        self.ce_armed = False  # saw a comment-entry paragraph word in area A
        self.ce_mode = False  # inside a 注記項 until a line starts in area A
        # per-line state
        self.line_no = 0
        self.chars = ""
        self.offs: list[int] = []  # offs[i] = byte offset of char i; offs[len] = region size

    # -- helpers ------------------------------------------------------------

    def _emit(self, tok: Token, a: int, b: int) -> Token:
        """Append (or extend) token with footprint chars [a, b) of this line.

        Identity check against the LAST token only: the sole re-emit path is a
        continued literal, which is by construction the most recent token. A
        value-equality `in` scan here is both wrong (two identical SPACE tokens
        compare equal) and O(n²) over the file.
        """
        if a != b:
            seg = (self.line_no, self.offs[a], self.offs[b])
            tok.segments.append(seg)
        if not self.tokens or self.tokens[-1] is not tok:
            self.tokens.append(tok)
        return tok

    def _last_nonblank(self) -> Token | None:
        for tok in reversed(self.tokens):
            if tok.type not in ("SPACE", "COMMENT"):
                return tok
        return None

    # -- literal scanning ---------------------------------------------------

    def _scan_string_body(self, tok: Token, i: int) -> int:
        """Consume literal chars from i until closing quote or end of region.

        Returns the char index after what was consumed. Leaves `open_string`
        set when the region ends before the literal closes (2.7.2.2: the
        blanks to the end of the continued line belong to the value).
        """
        q = tok.quote
        n = len(self.chars)
        start = i
        while i < n:
            ch = self.chars[i]
            if ch == q:
                if self.chars[i + 1 : i + 2] == q:  # doubled quote → one quote char
                    tok.text += self.chars[start:i] + q
                    i += 2
                    start = i
                    continue
                tok.text += self.chars[start:i]
                self._emit(tok, self.token_start, i + 1)
                self.open_string = None
                return i + 1
            i += 1
        # Region ended, literal still open: the blanks to the END of the line
        # belong to the value (2.7.2.2) — and a fixed-format record is notionally
        # space-padded to col 72, so a physically short line contributes those
        # notional blanks to the VALUE (they have no bytes, so no footprint).
        tok.text += self.chars[start:n] + " " * max(0, self.content_width - self.offs[-1])
        self._emit(tok, self.token_start, n)
        self.open_string = tok
        return n

    # -- picture scanning ---------------------------------------------------

    def _scan_picture(self, i: int) -> int:
        """PICTURE string: delimited ONLY by blank / , ; . followed by blank-or-end
        (2.4.2.1(2), 2.4.2.2.3). Any other character — including the ¥ currency
        symbol, which cp932 decodes as a backslash — belongs to the string."""
        n = len(self.chars)
        j = i
        while j < n:
            ch = self.chars[j]
            if ch in " 　":
                break
            if ch in ",;." and (j + 1 == n or self.chars[j + 1] in " 　"):
                break
            j += 1
        tok = Token("PICTURE", self.chars[i:j])
        self.token_start = i
        self._emit(tok, i, j)
        self.pic_pending = False
        return j

    # -- per-line -----------------------------------------------------------

    def feed(self, line) -> None:
        self.line_no = line.line_no
        self.base_col = line.content_base_col
        self.content_width = line.content_width
        content: bytes = line.content
        try:
            self.chars = content.decode(self.encoding)
        except (UnicodeDecodeError, LookupError):
            self._feed_raw(line, content)
            return
        # byte offset of each char within the region
        self.offs = [0]
        for ch in self.chars:
            self.offs.append(self.offs[-1] + len(ch.encode(self.encoding)))

        i = 0
        n = len(self.chars)
        if self.ce_mode:
            # comment-entry runs until a line whose first non-blank is in area A
            j = 0
            while j < n and self.chars[j] in " 　":
                j += 1
            if j < n and j >= 4:
                if j:
                    self._emit(Token("SPACE", self.chars[:j]), 0, j)
                self.token_start = j
                self._emit(Token("COMMENT_ENTRY", self.chars[j:]), j, n)
                return
            self.ce_mode = False  # area-A line (or blank region) ends the entry
        if line.kind == "continuation":
            i = self._resume_continuation(n)
        elif self.open_string is not None:
            self.cautions.append(
                f"line {self.line_no}: literal left open with no continuation line — closed as-is"
            )
            self.open_string = None

        while i < n:
            i = self._scan_one(i)

    def _feed_raw(self, line, content: bytes) -> None:
        if self.open_string is not None:
            self.cautions.append(
                f"line {self.line_no}: undecodable line while literal open — literal closed as-is"
            )
            self.open_string = None
        tok = Token("RAW", content.decode(self.encoding, errors="replace"))
        tok.segments.append((self.line_no, 0, len(content)))
        self.tokens.append(tok)
        self.cautions.append(
            f"line {self.line_no}: content region does not decode as {self.encoding} — RAW token"
        )

    def _resume_continuation(self, n: int) -> int:
        """Entry rules of a continuation line (2.7.2.2)."""
        i = 0
        while i < n and self.chars[i] == " ":
            i += 1
        if self.open_string is not None:
            tok = self.open_string
            if i < n and self.chars[i] == tok.quote:
                # leading blanks + resume quote: footprint of the literal, not value
                self.token_start = 0
                return self._scan_string_body(tok, i + 1)
            self.cautions.append(
                f"line {self.line_no}: continuation of open literal does not resume "
                f"with a quote — literal closed as-is"
            )
            self.open_string = None
            if i:
                self._emit(Token("SPACE", self.chars[:i]), 0, i)
            return i
        if i:
            self._emit(Token("SPACE", self.chars[:i]), 0, i)
        if i < n and i < 4:
            self.cautions.append(
                f"line {self.line_no}: continuation text begins in area A (col {self.base_col + i})"
            )
        # join: first non-blank continues the last non-blank token when both are wordish
        last = self._last_nonblank()
        if last is not None and last.type in ("WORD", "NUMBER", "PICTURE") and i < n and _is_word_char(self.chars[i]):
            j = i
            while j < n and _is_word_char(self.chars[j]):
                j += 1
            last.text += self.chars[i:j]
            last.segments.append((self.line_no, self.offs[i], self.offs[j]))
            if last.type == "WORD":
                last.reserved = last.text.upper() in RESERVED_WORDS
            elif last.type == "NUMBER" and not _NUM_RE.fullmatch(last.text):
                last.type = "WORD"
                last.reserved = last.text.upper() in RESERVED_WORDS
            return j
        return i

    # -- main scanner -------------------------------------------------------

    def _scan_one(self, i: int) -> int:
        chars, n = self.chars, len(self.chars)
        ch = chars[i]
        self.token_start = i

        if ch in " 　":
            j = i
            while j < n and chars[j] in " 　":
                j += 1
            if "　" in chars[i:j] and not self.fw_warned:
                # corpus uses U+3000 as whitespace; the reference knows only the
                # ASCII blank as a separator (2.4.2.1 「英字の空白」) — flag once
                self.fw_warned = True
                self.cautions.append(
                    f"line {self.line_no}: full-width space used as whitespace"
                )
            self._emit(Token("SPACE", chars[i:j]), i, j)
            return j

        # inline comment *> …to boundary R (2.7.2.5); needs a separator before it
        if chars.startswith("*>", i) and (i == 0 or chars[i - 1] == " "):
            self._emit(Token("COMMENT", chars[i:]), i, n)
            return n

        if chars.startswith("==", i):
            self._emit(Token("SEP", "=="), i, i + 2)
            return i + 2

        m = _PREFIXED_QUOTE.match(chars, i)
        if m and (m.group(1) is None or _at_word_boundary(chars, i)):
            prefix = (m.group(1) or "").upper()
            tok = Token("STRING", "", prefix=prefix, quote=m.group(2))
            return self._scan_string_body(tok, m.end())

        if self.pic_pending:
            # 'IS' between PIC and the string survives the pending state; every
            # OTHER non-blank character starts the picture — word chars, but also
            # ¥ (cp932 backslash), '*', '+' etc. (2.4.2.2.3 has its own alphabet)
            if chars[i : i + 2].upper() == "IS" and (i + 2 >= n or chars[i + 2] in " 　"):
                self._emit(Token("WORD", chars[i : i + 2], reserved=True), i, i + 2)
                return i + 2
            return self._scan_picture(i)

        if ch.isdigit() or ch in "+-" and i + 1 < n and chars[i + 1].isdigit() and _prev_is_sep(chars, i):
            return self._scan_number(i)

        if _is_word_char(ch):
            j = i
            while j < n and _is_word_char(chars[j]):
                j += 1
            word = chars[i:j]
            tok = Token("WORD", word, reserved=word.upper() in RESERVED_WORDS)
            self._emit(tok, i, j)
            if word.upper() in ("PIC", "PICTURE"):
                self.pic_pending = True
            # comment-entry paragraph name in area A arms 注記項 mode (fires at '.')
            self.ce_armed = word.upper() in _COMMENT_ENTRY_PARAS and self.offs[i] < 4
            return j

        for op in _OPERATORS:
            if chars.startswith(op, i):
                self._emit(Token("OP", op), i, i + len(op))
                return i + len(op)

        if ch in _SINGLE_SEPS:
            self._emit(Token("SEP", ch), i, i + 1)
            if ch == "." and self.ce_armed:
                # `REMARKS.` etc. — the rest of the line is 注記項 free text
                self.ce_armed = False
                self.ce_mode = True
                if i + 1 < n:
                    self.token_start = i + 1
                    self._emit(Token("COMMENT_ENTRY", chars[i + 1 :]), i + 1, n)
                    return n
            self.ce_armed = False
            return i + 1

        self._emit(Token("SEP", ch), i, i + 1)
        self.cautions.append(f"line {self.line_no}: unexpected character {ch!r} at col {self.base_col + i}")
        return i + 1

    def _scan_number(self, i: int) -> int:
        chars, n = self.chars, len(self.chars)
        j = i
        if chars[j] in "+-":
            j += 1
        seen_point = False
        while j < n:
            ch = chars[j]
            if ch.isdigit():
                j += 1
            elif ch == "." and not seen_point and j + 1 < n and chars[j + 1].isdigit():
                seen_point = True  # 2.4.2.2.2.2(3): decimal point never rightmost
                j += 1
            elif _is_word_char(ch):
                # not a number after all (e.g. 100-INIT): fall back to word scan
                while j < n and _is_word_char(chars[j]):
                    j += 1
                word = chars[i:j]
                self._emit(Token("WORD", word, reserved=word.upper() in RESERVED_WORDS), i, j)
                return j
            else:
                break
        self._emit(Token("NUMBER", chars[i:j]), i, j)
        return j


_NUM_RE = re.compile(r"[+-]?\d+(\.\d+)?")


def _at_word_boundary(chars: str, i: int) -> bool:
    return i == 0 or not _is_word_char(chars[i - 1])


def _prev_is_sep(chars: str, i: int) -> bool:
    return i == 0 or chars[i - 1] in " ,;(" or chars[i - 1] == ":"


def lex(lines, encoding: str = "cp932", cautions: list | None = None):
    """Tokenize the code/continuation/debug lines of a physical-line model.

    Pass `cautions` to receive the lexer's diagnostics — an undecodable region,
    a literal left open, a full-width space used as whitespace. A caller that
    drops them reports clean output over input it could not fully read, so every
    consumer path in this package passes the list.
    """
    lx = _Lexer(encoding)
    for line in lines:
        if line.kind in _LEXABLE:
            lx.feed(line)
    if lx.open_string is not None:
        lx.cautions.append("EOF with literal still open — closed as-is")
        lx.open_string = None
    if cautions is not None:
        cautions.extend(lx.cautions)
    return lx.tokens
