"""Shared plumbing for handlers.

A handler EXTRACTS and nothing else: given a file's bytes and the config, it returns
facts and RAW references (names as written in source). It never resolves a name to a
`source_id`, never decides an id, never writes a file. That separation is what lets a
project add a dialect by dropping in one module.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class RawRef:
    """One reference as it appears in source, before any resolution."""

    name: str
    role: str  # calls | x:uses | x:accesses | reads | writes
    lib_hint: str = ""
    kind: str = ""  # CALL | SBMJOB | COPY | SELECT | ... (provenance, for reports)
    line_no: int = 0
    source_line: str = ""


@dataclass
class Extraction:
    """Everything one handler learned about one file."""

    file_type: str = ""
    encoding: str = ""
    line_count: int = 0
    program_id: str = ""
    business_name: str = ""
    refs: list[RawRef] = field(default_factory=list)
    facts: dict = field(default_factory=dict)  # handler-specific, used to build Summary
    cautions: list[str] = field(default_factory=list)


def decode(data: bytes, cfg) -> tuple[str, str]:
    """Decode with the configured order and report WHICH encoding named the result.

    Order is load-bearing, not cosmetic: a pure-ASCII file decodes under both UTF-8 and
    Shift-JIS, and whichever is tried first is the label that ends up in the meta. Getting
    it backwards mislabelled a third of the reference corpus.
    """
    if b"\x00" in data[: cfg.binary_nul_window]:
        return ("", "binary")
    for enc in cfg.encoding_try_order:
        try:
            return (data.decode(enc), enc)
        except (UnicodeDecodeError, LookupError):
            continue
    fallback = cfg.encoding_try_order[-1] if cfg.encoding_try_order else "utf-8"
    return (data.decode(fallback, errors="replace"), fallback)


def line_count(text: str) -> int:
    """Lines as an editor counts them — a trailing newline does not add one."""
    return len(text.splitlines())


_COBOL_COMMENT = re.compile(r"^\s*\*")


def is_comment_cobol(line: str) -> bool:
    """COBOL: `*` in the indicator column, or a line that simply starts with `*`."""
    if _COBOL_COMMENT.match(line):
        return True
    return len(line) > 6 and line[6:7] == "*"


_INLINE_CMT = re.compile(r"/\..*?\./")
_LABEL = re.compile(r"^[A-Z][A-Z0-9_]*\s*:", re.IGNORECASE)
_SINGLE_QUOTE = re.compile(r"'[^']*'")


def strip_inline_comment(line: str) -> str:
    """Remove `/. ... ./` regions from a live CL line."""
    return _INLINE_CMT.sub(" ", line)


def strip_quotes(line: str) -> str:
    """Blank out single-quoted literals so text inside them is not read as code."""
    return _SINGLE_QUOTE.sub("''", line)


def is_label(stripped: str) -> bool:
    return bool(_LABEL.match(stripped))


def live_cl_lines(text: str):
    """Yield (line_no, raw_line) for CL lines that are actual code.

    Implements the comment state machine the matured extractor uses: `*` line comments,
    single-line `/. ... ./`, and multi-line `/.` blocks that close on ANY line containing
    `./` — including lines with trailing garbage after the closer, which do occur.
    """
    in_block = False
    for idx, raw in enumerate(text.split("\n")):
        stripped = raw.strip()
        if in_block:
            if "./" in stripped:
                in_block = False
            continue
        if stripped.startswith("*"):
            continue
        if stripped.startswith("/.") and stripped.endswith("./"):
            continue
        if stripped.startswith("/."):
            in_block = True
            continue
        yield idx + 1, raw


def header_comment_lines(text: str, within: int) -> list[str]:
    """The first `within` lines, for header-block mining (business name lives there)."""
    return text.split("\n")[:within]


_BANNER = re.compile(r"^[\s*=＝\-−_]*$")
#: Decoration wrapped around a real value: `--  NAME  --`, `=== NAME ===`.
_DECOR = re.compile(r"^[\s*=＝\-−_]+|[\s*=＝\-−_]+$")
#: A header FIELD line, not a business name: `CL-NAME = X   USER = Y`, `DATE 1987.12.17`.
_LABEL_LINE = re.compile(r"^[A-Z][A-Z0-9 _-]{1,20}\s*[=:]", re.IGNORECASE)
_STAR_PREFIX = re.compile(r"^\s*\*+\s?")


#: Hiragana, katakana, kanji, half-width katakana, full-width forms.
_CJK = re.compile(r"[぀-ヿ一-鿿｡-ﾟ！-｠]")


def business_name(text: str, cfg) -> str:
    """Collect every rule's candidate, then prefer the one carrying Japanese.

    The value lives in the HEADER COMMENT block, not in code — measured across four
    coexisting dialects in one corpus (`*REMARKS.`, `*  TITLE 'x'`, a bare first comment
    line, and an uncommented `REMARKS.` in a handful of files).

    First-match-wins was the obvious design and the wrong one. Header families disagree
    about WHICH keyword holds the business name: some put it in `REMARKS.` with technical
    notes in `TITLE.`, others do the reverse. Ordering the rules fixes one family and
    breaks the other by about as much. Since the field is the BUSINESS name and in this
    corpus that is written in Japanese, the CONTENT decides; rule order is only the
    tie-break when no candidate has any.
    """
    candidates = _collect_candidates(cfg, text)
    for value in candidates:
        if _CJK.search(value):
            return value
    return candidates[0] if candidates else ""


def _collect_candidates(cfg, text: str) -> list[str]:
    """Run every rule, returning at most one candidate per rule, in rule order."""
    candidates: list[str] = []
    for rule in cfg.business_name_rules:
        if rule["kind"] == "regex":
            for line in header_comment_lines(text, 40):
                m = rule["re"].search(line)
                if m:
                    value = (m.group(1) if m.groups() else m.group(0)).strip()
                    value = value.rstrip(".").strip("*").strip()
                    if value and not _BANNER.match(value):
                        candidates.append(value)
                        break
        else:
            skip = tuple(rule.get("skip_prefixes") or ())
            for line in header_comment_lines(text, rule.get("within_lines", 14)):
                s = line.rstrip()
                if not s.lstrip().startswith("*"):
                    continue
                if rule.get("skip_banner", True) and _BANNER.match(s):
                    continue
                value = _STAR_PREFIX.sub("", s).strip().rstrip("*").strip()
                # Strip decoration BEFORE judging: `--  NAME  --` carries a real value that
                # a banner test would otherwise reject, and an undecorated leftover like
                # `ｵｵﾂｶ ﾎﾟﾘﾃｯｸ` is a system banner rather than this program's name.
                value = _DECOR.sub("", value).strip()
                if not value or _BANNER.match(value):
                    continue
                # `CL-NAME  = SR0110CL   USER = OPTF.` is header metadata, not a name.
                if _LABEL_LINE.match(value):
                    continue
                if skip and value.upper().startswith(skip):
                    continue
                candidates.append(value)
                break
    return candidates
