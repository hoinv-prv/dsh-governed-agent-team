"""ASP CL handler.

Absorbed from the project's matured `extract_cl_call_edges_v2.py` (AIP-EXEC-043), whose
patterns exist because an earlier extractor missed five invocation forms. Re-deriving
them from the syntax documentation alone was measured at precision 37% / recall 9%;
copying the documented regexes but not the surrounding handling reached 64% / 62%; the
real thing reaches 100% / 99.2%. The gap is entirely in what follows the regexes —
comment state, quoted literals, label lines, and job-submission block lookahead.

Two things are deliberately changed while absorbing:

  * the system list comes from config instead of a hardcoded two-value choice, which was
    the pack's portability blocker;
  * decoding goes through the configured encoding order rather than always UTF-8.
"""
from __future__ import annotations

import re

from ..syscmd import SYSCMD_KIND
from .base import (
    Extraction,
    RawRef,
    business_name,
    decode,
    is_label,
    line_count,
    live_cl_lines,
    strip_inline_comment,
    strip_quotes,
)

RE_CALL_PGM = re.compile(r"\bCALL\s+PGM-([A-Z0-9_]+)(?:\.([A-Z0-9_]+))?\b", re.IGNORECASE)
RE_CALL_BARE = re.compile(
    r"\bCALL\s+(?!PGM-|[\"'])([A-Z][A-Z0-9_]*)(?:\.([A-Z0-9_]+))?\b", re.IGNORECASE
)
RE_PGM_TOKEN = re.compile(r"PGM-([A-Z0-9_]+)(?:\.([A-Z0-9_]+))?", re.IGNORECASE)
RE_SBMJOB = re.compile(r"\bSBMJOB\b", re.IGNORECASE)
RE_SBMXJOB = re.compile(r"\bSBMXJOB\b", re.IGNORECASE)
# A CL file command names its file either as `FILE-<name>[.<lib>]` or as the first
# positional argument — `DLTFILE FILE-MONTHF7.AQUINO` and `CRTFILE WORKX,SIZE-237` both
# occur. `SNDMSG` is not in the command list: a file name inside a message string is not a
# reference to that file, and treating it as one was measured to invent 255 edges.
# EVERY file-bearing parameter on the line, not just the first: `OVRPF FILE-X,TOFILE-Y`
# names two files and the reference records both. The keyword may be bare `FILE-` or
# carry a direction prefix (`TOFILE-`, `INFILE-`, `OUTFILE-`, `SORTFILE-`), so match the
# `*FILE-` suffix. `TOFILE-*.@LIBL` yields nothing because `*` is outside the name class.
RE_FILE_PARAM = re.compile(r"\b[A-Z]*FILE-([A-Z0-9$#@_-]+)(?:\.([A-Z0-9_]+))?", re.IGNORECASE)
# The positional form accepts ONLY a bare alphanumeric token, deliberately excluding
# anything containing `-`. Every parameter in this dialect is spelled `KEYWORD-value`
# (`SIZE-237`, `IN-A`, `OUT-B`), so allowing a dash made the first parameter look like a
# file name and invented 1667 edges on one system alone. A file name never carries one.
RE_FIRST_ARG = re.compile(
    r"^\s*[A-Z][A-Z0-9]*\s+([A-Z][A-Z0-9$#@_]*)(?:\.([A-Z0-9_]+))?\s*(?:,|$)",
    re.IGNORECASE,
)
# The CL header sits inside a `/. … ./` banner whose lines carry a leading `*`, so the
# keyword is NOT at the start of the line. Anchoring without allowing that prefix missed
# every title and let the generic ladder pick a neighbouring REMARKS or command line.
#
# The quoted form is tried first and does not require a CLOSING quote: real headers run the
# value into the banner padding (`'ＦＴＰでのファイル送信（分工場）      *`), so demanding a
# terminator would drop exactly the titles that are there.
# `[^'\r\n]` and NOT `[^']`: a negated character class matches a newline, so without the
# line terminators excluded an unterminated quote ran on until the next `'` anywhere in the
# file — twelve lines later, in four real headers — and the multi-line value then destroyed
# the frontmatter it was written into.
RE_CL_TITLE_Q = re.compile(r"^\s*\*?\s*TITLE\.\s*'([^'\r\n]*)", re.IGNORECASE | re.MULTILINE)
RE_CL_TITLE = re.compile(r"^\s*\*?\s*TITLE\.\s*(.+?)\s*\*?\s*$", re.IGNORECASE | re.MULTILINE)
RE_CL_REMARKS = re.compile(r"^\s*\*?\s*REMARKS\.\s*(.+?)\s*\*?\s*$", re.IGNORECASE | re.MULTILINE)
#: Banner padding uses IDEOGRAPHIC SPACE, which `str.strip()` does not remove.
_TITLE_JUNK = " \t*'　"
#: Hiragana, katakana, kanji, half-width katakana, full-width forms.
_CJK = re.compile(r"[぀-ヿ一-鿿｡-ﾟ！-｠]")
#: The header banner; these keywords never appear meaningfully below it.
HEADER_LINES = 20
# The leading VERB of a statement. The name must not run into `-`, `_` or another
# alphanumeric: every parameter in this dialect is spelled `KEYWORD-value`, so
# `DLTFILE FILE-MONTHF7` is the verb DLTFILE plus a parameter that merely BEGINS with the
# catalogued name `FILE`. Without the lookahead that parameter was read as an invocation of
# a `FILE` command and minted a node for it.
RE_VERB = re.compile(r"^(//[A-Z*]+|[A-Z][A-Z0-9]*)(?![A-Z0-9_-])", re.IGNORECASE)
#: A statement may carry a label; the verb is what follows it.
RE_LEADING_LABEL = re.compile(r"^[A-Z][A-Z0-9_]*\s*:\s*", re.IGNORECASE)
#: Role placeholder for a file reference whose category is not knowable at extraction time.
PENDING_FILE_ROLE = "file:pending"


def _clean_title(value: str) -> str:
    return value.strip(_TITLE_JUNK).strip()


def _pick_business_name(text: str) -> str:
    """Choose between the header's candidate fields by CONTENT, not by field order.

    Neither keyword reliably holds the business name. One family of headers puts the
    Japanese name in `TITLE.` and technical notes in `REMARKS.`; another does the exact
    reverse, with `TITLE. ' ACTLF ABDETLK*'` naming a file and key while `REMARKS.` carries
    `受入異常ディテール`. Preferring one keyword outright was measured to fix one family and
    break the other by roughly the same amount.

    The field is the BUSINESS name, and in this corpus a business name is written in
    Japanese — so prefer the candidate that actually contains Japanese, and fall back to
    field order only when none does.
    """
    # Only the header banner — these keywords belong there, and scanning whole files with
    # three backtracking patterns turned a 45-second corpus pass into a 10-minute one.
    header = "\n".join(text.split("\n")[:HEADER_LINES])
    candidates: list[str] = []
    for rx in (RE_CL_TITLE_Q, RE_CL_TITLE, RE_CL_REMARKS):
        for m in rx.finditer(header):
            value = _clean_title(m.group(1))
            if value:
                candidates.append(value)
    for value in candidates:
        if _CJK.search(value):
            return value
    return candidates[0] if candidates else ""

#: A job-submission block ends at the next statement. Continuation lines carry the
#: parameters we need, so the scan must look past the trigger line.
STATEMENT_KEYWORDS = {
    "SBMJOB", "SBMXJOB", "CALL", "IF", "GOTO", "SNDMSG", "SNDPGMMSG", "CLRFILE",
    "DLTOVRF", "OVRDBF", "ACTMSGQ", "INIT", "END", "CASE", "WHEN", "OTHERWISE",
    "RETURN", "PGM", "VAR", "DCL", "MONMSG", "CHKOBJ", "DSPOBJ", "OPEN", "CLOSE",
    "STRDPSD1", "PAUSE",
}
BLOCK_LOOKAHEAD_MAX = 8


def _terminates_block(stripped: str) -> bool:
    if not stripped:
        return True
    if is_label(stripped):
        return True
    first = stripped.split(None, 1)[0].rstrip(",.:").upper()
    if first == "PARA-":
        return False
    return first in STATEMENT_KEYWORDS


def _block_from(lines: list[str], start: int) -> list[tuple[int, str]]:
    block = [(start + 1, lines[start])]
    for offset in range(1, BLOCK_LOOKAHEAD_MAX + 1):
        idx = start + offset
        if idx >= len(lines):
            break
        if _terminates_block(lines[idx].strip()):
            break
        block.append((idx + 1, lines[idx]))
    return block


def _pgm_in_block(block: list[tuple[int, str]]):
    """First `PGM-` token in a submission block.

    Quotes are NOT stripped here: `PARA-'…PGM-X.LIB'` legitimately carries the program
    name inside a literal. That is the opposite of the CALL path, where a literal must be
    blanked so its contents are not read as code.
    """
    for line_no, raw in block:
        m = RE_PGM_TOKEN.search(strip_inline_comment(raw))
        if m:
            return line_no, raw.rstrip("\n"), m.group(1).upper(), (m.group(2) or "").upper()
    return None


def extract(path, data: bytes, cfg, file_type: str = "cl") -> Extraction:
    text, enc = decode(data, cfg)
    out = Extraction(file_type=file_type, encoding=enc, line_count=line_count(text))
    if enc == "binary":
        out.facts["binary"] = True
        return out

    out.business_name = _pick_business_name(text) or business_name(text, cfg)

    lines = text.split("\n")
    consumed: set[int] = set()
    for line_no, raw in live_cl_lines(text):
        if line_no in consumed:
            continue
        live = strip_inline_comment(raw)

        # Job submissions first: their trigger line must not also be read as a CALL.
        for rx, kind in ((RE_SBMXJOB, "SBMXJOB"), (RE_SBMJOB, "SBMJOB")):
            if rx.search(live):
                block = _block_from(lines, line_no - 1)
                hit = _pgm_in_block(block)
                if hit:
                    hit_line, hit_src, callee, lib = hit
                    out.refs.append(
                        RawRef(callee, "calls", lib, kind, hit_line, hit_src.strip())
                    )
                else:
                    out.cautions.append(
                        f"L{line_no}: {kind} block carries no PGM- token within "
                        f"{BLOCK_LOOKAHEAD_MAX} lines — invocation target unresolved"
                    )
                consumed.update(n for n, _ in block)
                break
        else:
            code = strip_quotes(live)
            for m in RE_CALL_PGM.finditer(code):
                out.refs.append(
                    RawRef(m.group(1).upper(), "calls", (m.group(2) or "").upper(),
                           "CALL", line_no, raw.strip())
                )
            for m in RE_CALL_BARE.finditer(code):
                out.refs.append(
                    RawRef(m.group(1).upper(), "calls", (m.group(2) or "").upper(),
                           "CALL", line_no, raw.strip())
                )

    # File references. A CL command names a file without any device prefix, so the
    # category cannot be read off the token the way `SELECT … ASSIGN TO DA-VI-x` allows.
    # The role is left UNDECIDED here and filled in after the whole tree is scanned, from
    # the majority category the pack itself derived for that file where a prefix did exist.
    if cfg.file_commands:
        commands = set(cfg.file_commands)
        for line_no, raw in live_cl_lines(text):
            stripped = RE_LEADING_LABEL.sub("", strip_inline_comment(raw).strip())
            head = RE_VERB.match(stripped)
            if not head or head.group(1).upper() not in commands:
                continue
            matches = list(RE_FILE_PARAM.finditer(stripped))
            if not matches:
                m = RE_FIRST_ARG.match(stripped)
                matches = [m] if m else []
            for m in matches:
                out.refs.append(
                    RawRef(m.group(1).upper(), PENDING_FILE_ROLE, (m.group(2) or "").upper(),
                           f"CLFILE/{head.group(1).upper()}", line_no, stripped[:120])
                )

    # System commands are a SECOND `calls` population; one reference corpus recorded
    # 2805 of these in one system and zero in the other while both used them heavily.
    if cfg.syscmd_catalog and cfg.syscmd_emit_caller_edges:
        catalog = set(cfg.syscmd_catalog)
        for line_no, raw in live_cl_lines(text):
            stripped = RE_LEADING_LABEL.sub("", strip_inline_comment(raw).strip())
            if not stripped:
                continue
            head = RE_VERB.match(stripped)
            if head and head.group(1).upper() in catalog:
                out.refs.append(
                    RawRef(head.group(1).upper(), "calls", "", SYSCMD_KIND, line_no, stripped)
                )

    out.facts["call_count"] = sum(1 for r in out.refs if r.kind in ("CALL", "SBMJOB", "SBMXJOB"))
    out.facts["syscmd_count"] = sum(1 for r in out.refs if r.kind == SYSCMD_KIND)
    return out
