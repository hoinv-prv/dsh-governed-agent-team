"""Shared helpers for AI Work System MVP tooling.

Deterministic, zero-dependency utilities: YAML frontmatter parsing,
Markdown section extraction, JSONL helpers, lint result formatting.
"""
from __future__ import annotations

import json
import re
import sys
import unicodedata
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Iterable

# Force UTF-8 stdout/stderr so non-ASCII (— etc.) works on Windows cp932.
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except Exception:
        pass


FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", re.DOTALL)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def write_text(path: Path, content: str) -> None:
    """LF-stable by contract (CR-AIWS-2026-08-059): mọi artifact do tool sinh ghi LF, mọi OS.

    Thiếu `newline=` thì text-mode dịch `\\n` → os.linesep (CRLF trên Windows) — chính là cỗ máy
    sinh EOL churn đã trả giá 4 lần (CAP-1008-02; lần 4 = 37 metas, CAP-1051-02). Dùng open()
    thay vì Path.write_text(newline=...) vì floor Python 3.8 (tham số đó chỉ có từ 3.10)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        f.write(content)


def write_meta_if_changed(path: Path, content: str) -> bool:
    """Write a meta only when something OTHER than its `updated_at` stamp changed.

    Returns True if written, False if the file was left alone.

    A fresh stamp is not a change worth a rewrite, and that is the whole point rather than a
    side effect: a refresh whose only delta is the date lands every meta in `git status` and
    buries the handful of genuine edits in date noise. Measured on the corpus this helper was
    adopted from (CR-AIWS-2026-08-026): 144 live metas rewritten on one run, none of them
    different in substance. So a stamp-only delta leaves the OLD stamp on disk — deliberately;
    `git diff` after a refresh then shows content and nothing else.

    Two comparisons, in order: exact text, then text with the frontmatter `updated_at` line
    neutralised on both sides. Callers that are not metas (no frontmatter) get the exact
    comparison alone, since neutralisation is then a no-op.

    Comparison is on decoded text, not bytes, so a file written earlier with a BOM still
    compares equal — `read_text` strips it, and comparing bytes would churn the tree once.
    """
    path = Path(path)
    if path.is_file():
        try:
            existing = read_text(path)
        except (OSError, UnicodeDecodeError):
            existing = None          # unreadable → fall through and rewrite
        if existing is not None and (
            existing == content or _stamp_neutral(existing) == _stamp_neutral(content)
        ):
            return False
    write_text(path, content)
    return True


_UPDATED_AT_RE = re.compile(r"^updated_at:.*$", re.MULTILINE)


def _stamp_neutral(text: str) -> str:
    """`text` with the FRONTMATTER `updated_at` line blanked. Body left untouched.

    Scoped to the frontmatter on purpose: a body line that happens to start with
    `updated_at:` is content, and blanking it would hide a real change.
    """
    m = FRONTMATTER_RE.match(text)
    if not m:
        return text
    return _UPDATED_AT_RE.sub("updated_at: \x00", m.group(1)) + "\n\x00BODY\x00\n" + m.group(2)


# ---------- YAML frontmatter (minimal) ----------

def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Parse YAML-ish frontmatter. Supports scalars, lists (block + flow).

    Returns (meta, body). If no frontmatter, returns ({}, text).
    """
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    raw, body = m.group(1), m.group(2)
    return _parse_yaml_block(raw), body


def _parse_yaml_block(raw: str) -> dict[str, Any]:
    meta, _ = _parse_yaml_mapping(raw.splitlines(), 0, -1)
    return meta


def _coerce_scalar(val: str):
    """Coerce a frontmatter/profile scalar. Quoted -> literal string. Unquoted
    true/false -> bool; null/~ -> None; everything else stays a string (NO int
    coercion — version strings, ids, dates, paths stay as-is). CR-AIWS-2026-06-043
    Change B: booleans MUST coerce so a profile's `emit_scaffold: false` is bool False
    (not the truthy string 'false') and is honored by gates."""
    if len(val) >= 2 and val[0] == val[-1] and val[0] in ("'", '"'):
        return val[1:-1]
    low = val.lower()
    if low in ("true", "false"):
        return low == "true"
    if low in ("null", "~"):
        return None
    # CR-AIWS-2026-08-063 (IR-08b A3-9): the balanced-pair case is handled above; an UNBALANCED
    # leading/trailing quote is part of the value ('"abc' stays '"abc'), never silently stripped.
    return val


def _strip_inline_comment(raw_val: str) -> str:
    """Strip a YAML inline comment (' #…' — a '#' preceded by whitespace) from an UNQUOTED
    value and return it stripped. A '#' with NO preceding whitespace (regex 'BD#\\d+', hex
    '#fff', a fragment 'a#b') is not a comment and is left intact. Callers MUST skip quoted
    values (a '#' inside quotes is literal). CR-AIWS-2026-06-058 (IR-C)."""
    h = 1
    while True:
        h = raw_val.find("#", h)
        if h < 1:
            break
        if raw_val[h - 1] in (" ", "\t"):
            return raw_val[:h].strip()
        h += 1
    return raw_val.strip()


def _split_flow_list(inner: str) -> list:
    """Split the inside of a YAML flow list `[...]` on TOP-LEVEL commas only — commas inside a
    quoted item stay part of the item (CR-AIWS-2026-08-063 / IR-08b A3-7: `["a,b", c]` is 2
    items, not 3). Items coerce like scalars (A3-5: `[true, null]` -> [True, None]); a quoted item
    is a literal string."""
    items: list = []
    buf: list[str] = []
    q: str | None = None
    for ch in inner:
        if q:
            buf.append(ch)
            if ch == q:
                q = None
        elif ch in ('"', "'"):
            q = ch
            buf.append(ch)
        elif ch == ",":
            items.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    if buf or items:
        items.append("".join(buf))
    return [_coerce_scalar(s.strip()) for s in items if s.strip()]


def _read_block_scalar(lines: list[str], j: int, key_indent: int) -> tuple[str, int]:
    """Read the continuation lines of a YAML block scalar (`|` literal / `>` folded) that starts
    at lines[j-1]. Returns (text, next_index). CR-AIWS-2026-08-063 (IR-08b A3-4): before this the
    parser stored the indicator character itself and DROPPED every continuation line silently."""
    body: list[str] = []
    k = j
    block_indent: int | None = None
    while k < len(lines):
        ln = lines[k]
        if not ln.strip():
            body.append("")
            k += 1
            continue
        ind = len(ln) - len(ln.lstrip())
        if ind <= key_indent:
            break
        if block_indent is None:
            block_indent = ind
        body.append(ln[block_indent:] if ind >= block_indent else ln.lstrip())
        k += 1
    while body and body[-1] == "":
        body.pop()
    return "\n".join(body), k


def _dump_scalar(v: object) -> str:
    """Emit ONE scalar so that parse(dump(x)) == x (CR-AIWS-2026-08-063 / IR-08b A3-6):
    None -> `null`; bool -> true/false; a string that would be mis-read (contains ` #`, starts
    with a quote/bracket, or equals a coercible literal like `true`/`null`) is double-quoted with
    inner quotes escaped. Plain strings stay bare — byte-identical to the previous dumper."""
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    s = str(v)
    needs_quote = (
        " #" in s or "\t#" in s
        or s[:1] in ('"', "'", "[", "{")
        or s.lower() in ("true", "false", "null", "~")
        or s != s.strip()
    )
    if needs_quote:
        return '"' + s.replace('"', '\\"') + '"'
    return s


def _dump_value(out: list, key: str, v: object, indent: str = "") -> None:
    """Recursive emitter used by dump_frontmatter (CR-AIWS-2026-08-063): nested dict, list of
    scalars, list of dicts (`lint_accept` shape) all round-trip. Scalars via _dump_scalar."""
    if isinstance(v, dict):
        if not v:
            out.append(f"{indent}{key}: {{}}")
            return
        out.append(f"{indent}{key}:")
        for k2, v2 in v.items():
            _dump_value(out, str(k2), v2, indent + "  ")
    elif isinstance(v, list):
        if not v:
            out.append(f"{indent}{key}: []")
            return
        out.append(f"{indent}{key}:")
        for item in v:
            if isinstance(item, dict):
                first = True
                for k2, v2 in item.items():
                    if isinstance(v2, (dict, list)):
                        # nested container inside a list item — emit under the dash line
                        if first:
                            out.append(f"{indent}  -")
                            first = False
                        _dump_value(out, str(k2), v2, indent + "    ")
                    else:
                        prefix = f"{indent}  - " if first else f"{indent}    "
                        out.append(f"{prefix}{k2}: {_dump_scalar(v2)}")
                        first = False
                if first:  # empty dict item
                    out.append(f"{indent}  - {{}}")
            else:
                out.append(f"{indent}  - {_dump_scalar(item)}")
    else:
        out.append(f"{indent}{key}: {_dump_scalar(v)}")


def _parse_block_mapping_list(lines: list[str], start: int,
                              item_indent: int) -> tuple[list[dict], int]:
    """Parse a YAML block list whose items are mappings (CR-AIWS-2026-06-065):
        - key: val
          key2: val2
        - key: val3
    Returns (list_of_dicts, next_line_index). The dash line may carry the first
    'key: val'; deeper-indented 'key: val' lines extend the current item. A dedent
    (indent < item_indent) ends the list. Quoted values + a '#' with no preceding
    space are kept intact (mirrors the scalar parser)."""
    out: list[dict] = []
    cur: "dict | None" = None
    i = start
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        indent = len(line) - len(line.lstrip())
        if indent < item_indent:
            break
        s = line.lstrip()
        if s.startswith("- "):
            if cur is not None:
                out.append(cur)
            cur = {}
            rest = s[2:].strip()
            if ":" in rest:
                k, _, raw = rest.partition(":")
                v = raw.strip()
                v = v if v[:1] in ('"', "'") else _strip_inline_comment(raw)
                cur[k.strip()] = _coerce_scalar(v)
            i += 1
        elif cur is not None and indent > item_indent and ":" in s:
            k, _, raw = s.partition(":")
            v = raw.strip()
            v = v if v[:1] in ('"', "'") else _strip_inline_comment(raw)
            cur[k.strip()] = _coerce_scalar(v)
            i += 1
        else:
            break
    if cur is not None:
        out.append(cur)
    return out, i


def _parse_yaml_mapping(lines: list[str], start: int,
                        parent_indent: int) -> tuple[dict[str, Any], int]:
    """Parse an indented YAML-ish mapping: scalars, flow lists, block lists, and
    NESTED mappings. Unquoted booleans/null coerce (true/false -> bool, null/~ -> None;
    see _coerce_scalar, CR-AIWS-2026-06-043 Change B); other scalars stay strings (no
    int coercion). Returns (dict, next_line_index)."""
    result: dict[str, Any] = {}
    i = start
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        indent = len(line) - len(line.lstrip())
        if parent_indent >= 0 and indent <= parent_indent:
            break
        if ":" not in line:
            i += 1
            continue
        key, _, raw_val = line.partition(":")
        key = key.strip()
        val = raw_val.strip()
        # IR-C (CR-AIWS-2026-06-058): drop a YAML inline comment (' #…') from an UNQUOTED value
        # so 'systems:  # note' before a block list reads as an empty value, and 'scalar  # note'
        # coerces from the scalar. A '#' with no preceding space is never a comment.
        if val[:1] in ('"', "'"):
            # CR-AIWS-2026-07-066 T1-b (A3-2): a QUOTED value ends at its closing quote — whatever
            # follows (typically an inline comment) is not part of the value. CR-058 skipped quoted
            # values entirely, so 'title: "My Doc"  # note' kept the comment inside the value.
            q = val[0]
            end = val.find(q, 1)
            if end != -1:
                val = val[:end + 1]
        elif val.startswith("["):
            # CR-AIWS-2026-07-066 T1-c (A3-3): recognise a flow list BEFORE stripping comments.
            # '#' is legal inside one ('[#101, #102]'), and stripping first truncated the value at
            # ' #' — destroying the closing bracket and with it the flow-list branch below.
            close = val.rfind("]")
            val = val[:close + 1] if close != -1 else _strip_inline_comment(raw_val)
        else:
            val = _strip_inline_comment(raw_val)
        if val in ("|", ">", "|-", ">-", "|+", ">+"):
            # CR-AIWS-2026-08-063 (IR-08b A3-4): block scalar — read the continuation lines
            # instead of storing the indicator and dropping them. `>` folds single newlines to
            # spaces (YAML folded); `|` keeps them (literal). Chomping suffixes are accepted but
            # trailing blank lines are always trimmed (good enough for frontmatter prose).
            text, i = _read_block_scalar(lines, i + 1, indent)
            if val.startswith(">"):
                text = " ".join(seg.strip() for seg in text.split("\n") if seg.strip())
            result[key] = text
            continue
        if val == "":
            # Look ahead: nested mapping, block list, or empty value.
            # CR-AIWS-2026-07-066 T1-a (A3-1): skip COMMENT lines as well as blanks. A comment as
            # the first line under the key used to read as a nested mapping, so the whole block
            # list collapsed to {} — and an empty `systems` silently disarms validate_system's
            # `and cfg.get("systems")` guard, i.e. rule #12 accepts ANY system id.
            j = i + 1
            while j < len(lines) and (not lines[j].strip() or lines[j].lstrip().startswith("#")):
                j += 1
            child_indent = (len(lines[j]) - len(lines[j].lstrip())) if j < len(lines) else -1
            if j >= len(lines) or child_indent <= indent:
                result[key] = []                      # empty value (backward-compatible)
                i = j
            elif lines[j].lstrip().startswith("- "):
                first_rest = lines[j].lstrip()[2:].strip()
                # mapping-style item: 'key: value' after the dash (':' followed by space/eol)
                is_mapping = bool(re.match(r"[^:\s][^:]*:(\s|$)", first_rest))
                if is_mapping:
                    result[key], i = _parse_block_mapping_list(lines, j, child_indent)
                else:
                    items: list[str] = []                 # block list (scalars)
                    k = j
                    while k < len(lines):
                        l2 = lines[k]
                        # CR-AIWS-2026-07-021 (IR-D): skip blank AND comment lines (comment-first,
                        # BEFORE the dedent check) so an interleaved comment inside a block list does
                        # not terminate the list and silently drop the items after it. Scoped to
                        # comment/blank only — a real `key: val` sibling still ends the list (else:break).
                        if not l2.strip() or l2.lstrip().startswith("#"):
                            k += 1
                            continue
                        if (len(l2) - len(l2.lstrip())) < child_indent:
                            break
                        s2 = l2.lstrip()
                        if s2.startswith("- "):
                            # CR-AIWS-2026-07-042 T1: strip the inline comment on a block-list ITEM
                            # too — CR-058 covered value lines and comment lines but not items, so
                            # `- sys_a  # primary` parsed as the literal 'sys_a  # primary' and
                            # SILENTLY DISARMED the multi-system guard (rule #12) and the
                            # fixture_under_real_system guard (systems / synthetic_systems both
                            # became unmatchable). Quoted items keep a literal '#' (same rule as
                            # value lines above).
                            raw_item = s2[2:].strip()
                            item = (raw_item if raw_item[:1] in ('"', "'")
                                    else _strip_inline_comment(raw_item))
                            # CR-AIWS-2026-08-063 (IR-08b A3-5): coerce like the scalar path
                            # (`- false` -> False, `- null` -> None); quoted items stay literal.
                            items.append(_coerce_scalar(item.strip()))
                            k += 1
                        else:
                            break
                    result[key] = items
                    i = k
            else:
                nested, i = _parse_yaml_mapping(lines, j, indent)   # nested mapping
                result[key] = nested
        elif val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            result[key] = _split_flow_list(inner)   # CR-AIWS-2026-08-063 (A3-7 quote-aware, A3-5 coerce)
            i += 1
        else:
            result[key] = _coerce_scalar(val)
            i += 1
    return result, i


def dump_frontmatter(meta: dict[str, Any]) -> str:
    """Serialize meta back to minimal YAML-ish frontmatter.

    Contract (CR-AIWS-2026-08-063 / IR-08b A3-6): parse(dump(m)) == m on the supported corpus —
    None, bool, nested dict, list of scalars, list of dicts, and scalars that need quoting all
    round-trip; anything the reader could mis-read is quoted on the way out. Plain scalars and
    scalar lists dump byte-identical to the previous emitter, so existing metas do not churn."""
    out: list[str] = ["---"]
    for k, v in meta.items():
        _dump_value(out, str(k), v)
    out.append("---")
    return "\n".join(out) + "\n"


def strip_lint_accept(meta: dict[str, Any]) -> dict[str, Any]:
    """Remove the lint_accept block so an accept never survives a content rewrite
    (strip-on-refresh reset, CR-AIWS-2026-06-065). Mutates and returns meta."""
    meta.pop("lint_accept", None)
    return meta


# ---------- Illustration spans (CR-AIWS-2026-08-078 C5) ----------

# Markers that make a line a COUNTER-EXAMPLE — text showing what NOT to write. A path inside such a
# line is meant to be wrong; a link/ref gate that flags it is reporting the document working.
_ILLUSTRATION_MARKERS = ("❌", "✗")

# A path token containing a literal ellipsis is an ABBREVIATION, not a path: `core/.../SPEC.md`
# stands for "some directories here". It cannot resolve and was never meant to.
_ELLIPSIS_IN_PATH = "/.../"


def illustration_lines(lines: "list[str]") -> "set[int]":
    """1-indexed line numbers that are ILLUSTRATION, not live pointers.

    CR-AIWS-2026-08-078 C5 gives the concept one name and one implementation. Three shapes were
    being handled separately, or not at all, by two different tools:

      (i)  inside a ``` fenced block — sample output. Introduced as `_payload_unfenced` by
           CR-AIWS-2026-08-071 r3 after F3 was re-verdicted not-a-bug: DOCLING_ENGINE.md:638 shows
           the markdown docling GENERATES, and treating that as a broken ref failed the build on a
           correct document.
      (ii) a counter-example line (❌ / ✗) — the path is wrong ON PURPOSE.
      (iii) a token carrying `/.../` — an abbreviation, checked per-token by `is_ellipsis_path`.

    The fence toggle counts ``` lines themselves as illustration, so an opening/closing fence never
    leaks into the scanned set.

    NOTE what this is NOT: it does not skip the REST of a file after a fence or a marker. A real
    broken link on the line after a code block must still be caught — that is probe (h) of C7. A
    suppression that swallows the tail of a file is worse than the false positive it removes.
    """
    out: "set[int]" = set()
    fenced = False
    for i, line in enumerate(lines, 1):
        if line.strip().startswith("```"):
            fenced = not fenced
            out.add(i)
            continue
        if fenced or any(m in line for m in _ILLUSTRATION_MARKERS):
            out.add(i)
    return out


def is_ellipsis_path(token: str) -> bool:
    """CR-AIWS-2026-08-078 C5 (iii) — `core/.../SPEC.md` is shorthand, not a path to resolve."""
    return _ELLIPSIS_IN_PATH in token.replace("\\", "/")


def unfenced_lines(lines: "list[str]") -> "list[tuple[int, str]]":
    """(1-indexed lineno, line) for every line that is NOT illustration.

    Replaces `_payload_unfenced` (CR-AIWS-2026-08-071 r3) — same call shape, wider concept, ONE
    definition shared by lint_wiki.py and build_aiws_install_package.py.
    """
    skip = illustration_lines(lines)
    return [(i, line) for i, line in enumerate(lines, 1) if i not in skip]


# ---------- Markdown section extraction ----------

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")


def extract_sections(body: str) -> dict[str, str]:
    """Map heading text -> section body (any level). Later duplicates overwrite."""
    sections: dict[str, str] = {}
    current_key: str | None = None
    buf: list[str] = []
    for line in body.splitlines():
        m = HEADING_RE.match(line)
        if m:
            if current_key is not None:
                sections[current_key] = "\n".join(buf).strip()
            current_key = m.group(2).strip()
            buf = []
        else:
            if current_key is not None:
                buf.append(line)
    if current_key is not None:
        sections[current_key] = "\n".join(buf).strip()
    return sections


def has_section(body: str, name: str) -> bool:
    n = name.strip().lower()
    for line in body.splitlines():
        m = HEADING_RE.match(line)
        if m and m.group(2).strip().lower() == n:
            return True
    return False


def _h2_span(body: str, key: str) -> str:
    """Extract text from an H2 section to the next H2, including H3+ children.

    Finds heading matching '## key' (case-insensitive) and returns all lines until
    the next heading starting with '##' (stops at another H2 level). Returns empty
    string if key not found.

    Used to read H2 sections where H3+ children contain the actual content
    (e.g., '## Execution Scope' with '### In Scope', '### Out of Scope' children).

    CR-AIWS-2026-08-25 Item 1: parser-level fix for scope rendering bug.
    """
    lines = body.splitlines()
    h2_pattern = re.compile(r"^##\s+" + re.escape(key) + r"(?:\s|$)", re.IGNORECASE)

    # Find the H2 heading
    start_idx = -1
    for i, line in enumerate(lines):
        if h2_pattern.match(line):
            start_idx = i
            break

    if start_idx < 0:
        return ""

    # Collect lines from H2+1 until next ## heading (any level ## stops)
    end_idx = start_idx + 1
    for i in range(start_idx + 1, len(lines)):
        if lines[i].startswith("## "):
            end_idx = i
            break
    else:
        end_idx = len(lines)

    # Collect body (skip the H2 line itself)
    body_lines = lines[start_idx + 1:end_idx]
    return "\n".join(body_lines).strip()


# ---------- Step parsing for AIP ----------

STEP_HEADING_RE = re.compile(r"^#{2,4}\s+Step:\s*(STEP-[A-Za-z0-9_-]+)\s*—\s*(.+?)\s*$")


def parse_aip_steps(body: str) -> list[dict[str, str]]:
    """Parse 'Step: STEP-xx — title' blocks with simple 'Field:' lines.

    Recognises: Objective, Recommended Mode, Applicable Guidelines,
    Recommended Skills, Inputs, Expected Outputs, Done Condition,
    Notes / Constraints, Workspace Actions, Step Dependencies, Review Note,
    Step Output / Execution Artifact, Assigned Agent (CR-AIWS-2026-07-018),
    Difficulty, Kind (CR-AIWS-2026-07-059), Procedure, Acceptance (CR-AIWS-2026-08-25 Item 6).
    """
    fields = [
        "Objective", "Recommended Mode", "Applicable Guidelines",
        "Recommended Skills", "Inputs", "Expected Outputs", "Done Condition",
        "Notes / Constraints", "Workspace Actions", "Step Dependencies",
        "Review Note", "Step Output / Execution Artifact",
        "Assigned Agent",  # optional (CR-AIWS-2026-07-018) — agent instance_id expected to run the step
        "Difficulty", "Kind",  # optional (CR-AIWS-2026-07-059) — capability-routing inputs (Difficulty low|medium|high; Kind = task-kind tags)
        "Executor",  # optional (CR-AIWS-2026-08-044 C4) — plan-time executor for an assigned step (main_session | claude_subagent)
        "Procedure",  # optional (CR-AIWS-2026-08-25 Item 6) — step-level guidance on execution approach
        "Acceptance",  # optional (CR-AIWS-2026-08-25 Item 6) — step-level acceptance criteria beyond Done Condition
    ]
    field_re = re.compile(r"^(" + "|".join(re.escape(f) for f in fields) + r")\s*:\s*$")
    # CR-AIWS-2026-08-127 C9 — the two single-line optional fields are accepted INLINE too (`Kind: review, code`).
    # Measured 2026-08-27 over 402 AIPs: Kind written inline 114× vs bare 5×, Difficulty 80× vs 5×, every mandatory
    # field 100% bare — so until this line, the Kind-vocab lint, the ASC "Difficulty / Kind" section and the
    # Operating Memory slice by Kind never saw 96% of the values. Deliberately limited to these two fields: a
    # multi-line field written inline would be a different (unobserved) authoring error, not this one.
    inline_re = re.compile(r"^(Difficulty|Kind)\s*:\s*(\S.*)$")

    steps: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    current_field: str | None = None
    buf: list[str] = []
    in_fence = False  # inside a fenced code block (``` ... ```)

    def flush_field() -> None:
        nonlocal current_field, buf
        if current is not None and current_field is not None:
            current[current_field] = "\n".join(buf).strip()
        current_field = None
        buf = []

    def flush_step() -> None:
        nonlocal current
        flush_field()
        if current is not None:
            steps.append(current)
        current = None

    for line in body.splitlines():
        # Toggle fence state on ``` lines; collect as content but skip structural parsing
        if line.startswith("```"):
            in_fence = not in_fence
            if current_field is not None:
                buf.append(line)
            continue
        if in_fence:
            if current_field is not None:
                buf.append(line)
            continue

        sm = STEP_HEADING_RE.match(line)
        if sm:
            flush_step()
            current = {"step_id": sm.group(1), "title": sm.group(2)}
            continue
        if current is None:
            continue
        # New top-level H2 heading (not a Step: heading) ends the current step
        if HEADING_RE.match(line) and line.startswith("## ") and not line.lstrip("#").strip().startswith("Step:"):
            flush_step()
            continue
        fm = field_re.match(line)
        if fm:
            flush_field()
            current_field = fm.group(1)
            continue
        im = inline_re.match(line)
        if im:  # CR-127 C9: value on the same line — assign directly, no buffer opened
            flush_field()
            current[im.group(1)] = im.group(2).strip()
            continue
        if current_field is not None:
            buf.append(line)
    flush_step()
    return steps


# ---------- JSONL ----------

def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    out: list[dict[str, Any]] = []
    for i, raw in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), start=1):
        raw = raw.strip().strip('\x00')
        if not raw:
            continue
        try:
            out.append(json.loads(raw))
        except json.JSONDecodeError as e:
            raise ValueError(f"{path}: invalid JSON on line {i}: {e}") from e
    return out


def write_jsonl(path: Path, records: Iterable[dict[str, Any]]) -> None:
    # LF-stable by contract (CR-AIWS-2026-08-059) — see write_text.
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(r, ensure_ascii=False) for r in records]
    with path.open("w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + ("\n" if lines else ""))


# ---------- Payload -> install mapping (moved here by IR-2026-08-17 F1) ----------
# Lived in `quick_install_aiws.py`, which the builder DELIBERATELY does not ship
# (build_aiws_install_package.py `exclude` + MANIFEST "Intentional exclusions"). Every shipped tool
# that imported it at module scope therefore died with ModuleNotFoundError on any install —
# `check_dual_tree.py` since it was written, `diff_payload_tree.py` from its first release. The map
# is still ONE source; it just had to live in a module that actually ships. `quick_install_aiws.py`
# re-exports these names so its own public surface is unchanged.
#
# Mirrors install_guide.md Step 2. Source is "payload/<key>" inside the built package; destination
# is relative to the TARGET project root.
PAYLOAD_MAP: "list[tuple[str, str]]" = [
    ("methodology",          ".ai-work/truth/canonical/methodology"),
    ("wiki_guidelines",      ".ai-work/truth/canonical/wiki_guidelines"),
    ("skills",               ".claude/skills"),
    ("commands",             ".claude/commands"),
    ("tooling",              ".ai-work/tooling"),
    ("aip_templates",        ".ai-work/aip/templates"),
    ("workspace_templates",  ".ai-work/workspace_templates"),
    ("preset_knowledge",     ".ai-work/preset_knowledge"),
    ("procedural",           ".ai-work/procedural"),
    ("truth_templates",      ".ai-work/truth/templates"),
    ("guidelines",           ".ai-work/guidelines"),
    ("wiki_source_profiles", ".ai-work/wiki_sources/profiles"),
    ("aiws_wiki",            ".ai-work/wiki_sources/aiws_meta"),
    ("agents",               ".ai-work/agents"),
    ("upstream_requests",    ".ai-work/upstream_requests"),
    ("project_change_requests", ".ai-work/change_requests"),
    ("install_templates",    ".ai-work/install_templates"),
]

# ---------- "Cái gì SHIP" — nguồn sự thật (CR-AIWS-2026-08-102 C1) ----------
# `PAYLOAD_MAP` ở trên trả lời "section nào đi đâu trong dự án đích". Nó KHÔNG trả lời được câu
# hỏi thực tế mà lint/CR cần: *một path cụ thể có đi vào bản cài không?* — vì exclusion trước đây
# chỉ sống trong `build_aiws_install_package.PAYLOAD_SECTIONS`. Hệ quả đo được: một rule chỉ đọc
# `PAYLOAD_MAP` kết luận SAI rằng `aiws-council-review` có ship (nó bị loại ở CẢ HAI section
# `skills` và `procedural`). Vì vậy nguồn gốc của section + exclusion về đây, cạnh `PAYLOAD_MAP`.
#
# BẤT ĐỐI XỨNG CÓ CHỦ Ý: `PAYLOAD_MAP` có 17 khoá, `PAYLOAD_SRC` có 16 — `aiws_wiki` là bundle
# được dựng riêng bởi `build_aiws_wiki_bundle()`, không đi qua cơ chế section, nên không có
# thư mục nguồn dạng `product/<x>`. Đừng "sửa" cho hai danh sách bằng nhau.

#: Thư mục nguồn (repo-relative) của mỗi payload section. Khoá khớp `Section.name` của builder.
PAYLOAD_SRC: "dict[str, str]" = {
    "methodology":             "product/methodology/ai_work_system",
    "wiki_guidelines":         "product/wiki_guidelines",
    "skills":                  "product/skills",
    "commands":                "product/commands",
    "tooling":                 "product/tooling",
    "aip_templates":           "product/aip_templates",
    "workspace_templates":     "product/workspace_templates",
    "preset_knowledge":        "product/preset_knowledge",
    "procedural":              "product/procedural",
    "truth_templates":         "product/truth_templates",
    "guidelines":              "product/guidelines",
    "wiki_source_profiles":    "product/wiki_source_profiles",
    "agents":                  "product/agents",
    "upstream_requests":       "product/upstream_requests",
    "project_change_requests": "product/project_change_requests",
    "install_templates":       "product/install_templates",
}

#: Path (relative to the section source root) KHÔNG được ship. Builder union subdir+file rồi so
#: theo TIỀN TỐ path, nên một danh sách phẳng là đủ và khớp đúng hành vi copy hiện có.
PAYLOAD_EXCLUDES: "dict[str, list[str]]" = {
    # internal design artefacts — không cần để chạy skill/tool, và lộ rationale thiết kế
    "methodology": ["00_brainstorming", "10_design", "90_delta_tracking"],
    # wiki-eval DOMAIN — project-local eval tooling, repo-coupled, không dành cho adopter
    #   (CR-013; loại cả domain theo CR-AIWS-2026-07-025 DP-025-C).
    # council DOMAIN — canonical trong repo này nhưng CHƯA ship cho tới khi có MỘT dogfood ĐO ĐƯỢC
    #   (CR-AIWS-2026-08-067 C9, ruling DP-1064-E). Điều kiện để gỡ nằm ở §7 của CR đó (noise floor
    #   -> control set -> mẫu số tường minh -> pre-registration); gỡ là một CR RIÊNG, không phải một
    #   lần sửa lặng lẽ ở đây. Phải loại ở CẢ `skills` lẫn `procedural`: loại một bên thì ship ra một
    #   stub trỏ tới phần thân procedural mà adopter không bao giờ nhận được.
    "skills": ["aiws-council-review", "aiws-eval"],
    # CR-AIWS-2026-08-113: `test_object_named_consumer.py` là GATE NỘI BỘ của repo AIWS — nó chỉ
    # có nghĩa khi đi kèm wrapper `.ai-work/tests/test_object_authoring_gate.py` (CAP-1027-03),
    # mà `.ai-work/tests/` KHÔNG ship. Adopter nhận file này sẽ có một test không gì chạy, cộng
    # một WARNING `test_outside_test_dir` do chính package tạo ra và họ không xử được.
    # KHÔNG di chuyển file khỏi `tooling/`: wrapper G1 neo vào đúng hai path của nó.
    # CR-AIWS-2026-08-115 C6 (HUMAN ruling 2026-08-19) — ba tool sau THÔI ship, mỗi cái một lý do
    # KHÁC NHAU; đừng gộp chúng thành một câu, vì điều kiện gỡ-bỏ-exclude của mỗi cái cũng khác:
    #
    #   * `council_tally.py` — consumer duy nhất của nó là skill `aiws-council-review`, mà skill đó
    #     nằm trong `PAYLOAD_EXCLUDES["skills"]` VÀ `["procedural"]` (CR-AIWS-2026-08-067 C9, ruling
    #     DP-1064-E). Adopter nhận 54 KB tool không có gì lái. ĐẢO NGƯỢC có chủ ý phần "tool vẫn ship"
    #     của DP-1064-E. ĐIỀU KIỆN QUAY LẠI: gỡ mục này TRONG CÙNG LƯỢT mà skill ra khỏi exclusion
    #     set của `procedural` — hai mục, một lượt; điều kiện để lượt đó xảy ra ở CR-067 §7.
    #   * `switch_system_mode.py` — docstring dòng 1 của chính nó tự khai "dev-only; NOT shipped",
    #     nhưng `ships()` vẫn True. Đây là một mục exclusion bị bỏ sót, không phải một quyết định.
    #   * `convert_excel_to_md.py` — hard-require `markitdown` KHÔNG có fallback stdlib, trái điều
    #     kiện của Approved Deviation 2026-07-04 và trái chính rule stdlib-only mà package render cho
    #     adopter. Chiều ngược lại (`convert_md_to_excel.py`) VẪN ship và CÓ trong README.
    #
    # KHÔNG xoá file khỏi hai cây (DP-115-F) — tiền lệ `quick_install_aiws.py`.
    # quick-install (CR-026) là TOOL bảo trì sống trong tooling nhưng không được tới tay adopter.
    "tooling": [
        "convert_excel_to_md.py",
        "council_tally.py",
        "quick_install_aiws.py",
        "switch_system_mode.py",
        "test_object_named_consumer.py",
    ],
    "aip_templates": ["tracking"],
    "procedural": [
        "skills/aiws-council-review",
        "skills/aiws-eval",
        # OPERATION dev-only — không ship (CR-026; gộp bởi CR-AIWS-2026-07-025)
        "skills/aiws-pkg/operations/quick-install.md",
        # checklist cắt release của CHÍNH AIWS — adopter không cắt release AIWS (CR-089 DP-089-C)
        "skills/aiws-pkg/operations/release-checklist.md",
    ],
    # term-data của dự án — không bao giờ ship/ghi đè stopwords của họ (CR-047 Change C)
    "wiki_source_profiles": ["project_stopwords.yml"],
    # desk state là dữ liệu CHẠY của dự án. Giữ CẢ tên trước và sau P2-rename (`instances` +
    # `task_desks`) một cách CỘNG DỒN: một guard chỉ biết tên cũ sẽ ngừng bảo vệ đúng lúc rename
    # hoàn tất — và một guard đã ngừng làm việc thì không tự nói ra.
    "agents": [
        "agents/instances", "agents/task_desks", "sample_project_package",
        "assistant_to_agent_mapping.md", "parity_verification_report.md",
    ],
}


#: Path ĐI VÀO PAYLOAD nhưng KHÔNG qua cơ chế Section (CR-AIWS-2026-08-105 C1).
#:
#: Vì sao danh sách này tồn tại: builder có ba đường ship không dùng `PAYLOAD_SECTIONS`, nên một
#: `ships()` chỉ đọc section sẽ trả ÂM TÍNH GIẢ — và vì `ships()` là đầu vào của quyết định
#: `upgrade_impact` (CR-AIWS-2026-08-102 C3/C4/C6), âm tính giả dẫn thẳng tới việc adopter KHÔNG
#: được báo về thay đổi họ thật sự nhận. Ba cơ chế đó:
#:
#:   1. `build_aiws_wiki_bundle()` copy `.ai-work/wiki_sources/aiws_meta/{group}/` -> `payload/aiws_wiki/`.
#:      `PAYLOAD_MAP` CÓ cặp ("aiws_wiki", …) nhưng `PAYLOAD_SECTIONS` thì không — đây chính là bất
#:      đối xứng 17-vs-16 mà CR-102 đã ghi nhận nhưng chưa xử lý cho `ships()`.
#:   2. `EXTRA_SINGLE_FILES` — copy từng file lẻ tới đích riêng (rename_map.json đi HAI nơi).
#:   3. `DESIGN_DOCS_STRIP_COPY` — 4 file dưới `10_design/` bị section exclude, rồi được copy LẠI
#:      sau khi lược phần rationale nội bộ. `Detail_Design_MVP.md` CỐ Ý không có mặt: mở cả thư mục
#:      `10_design/` sẽ biến âm tính giả thành DƯƠNG TÍNH GIẢ và làm loãng ledger (DP-105-A = a).
#:
#: Mỗi mục là một PREFIX path (repo-relative). Thêm đường ship mới ở builder ⇒ thêm ở đây, nếu không
#: `ships()` lại nói dối; `test_cr105_*` khoá cả hai chiều.
PAYLOAD_EXTRA_SHIPPED: "list[str]" = [
    ".ai-work/wiki_sources/aiws_meta",                                              # (1) bundle
    "product/rename_map.json",                                                      # (2) single file
    "product/methodology/ai_work_system/10_design/Architecture_Design_MVP.md",      # (3) strip-copy
    "product/methodology/ai_work_system/10_design/Basic_Design_MVP.md",
    "product/methodology/ai_work_system/10_design/Conceptual_Design_MVP.md",
    "product/methodology/ai_work_system/10_design/Methodology_Design_MVP.md",
]

#: Nguồn cho `EXTRA_SINGLE_FILES` của builder (CR-AIWS-2026-08-105 C3) — (src_rel, dst_rel).
PAYLOAD_SINGLE_FILES: "list[tuple[str, str]]" = [
    ("product/rename_map.json", "payload/tooling/rename_map.json"),
    ("product/rename_map.json", "rename_map.json"),
]

# CR-AIWS-2026-08-121 r3 — the release note is resolved from the PINNED VERSION, never hard-coded.
# It shipped as the literal `releases/AI_Work_System_MVP_v1.2.0_2026-08-20/RELEASE_NOTES.md`, which
# matched only because `aiws_version` happened to be v1.2.0. Two failures followed from that, and both
# were SILENT: ship v1.3.0 and every package still carries v1.2.0's notes under the new release's name;
# rename that directory and the note is simply not copied, because the builder's loop is
# `if src.exists(): copy` with no else. A literal in a constant cannot notice either.
RELEASE_NOTES_NAME = "RELEASE_NOTES.md"


def resolve_release_notes(project_root: Path, version: str = "") -> "tuple[str, str] | None":
    """`(src_rel, dst_rel)` for the currently pinned version's release note, or `None`.

    `version` defaults to `aiws_version` from `product/aiws_version.md` — the same pin the builder
    stamps into the package, so the note and the package cannot disagree about which release they are.

    When several release directories carry one version (this repo has three for v1.2.0: 08-15, 08-17,
    08-20) the NEWEST by directory name wins, and the caller is expected to say which it picked. Silent
    selection among equals is how the wrong file ships without anyone noticing.

    Returns None rather than raising: a tree with no `releases/` is legitimate (every adopter install),
    and the caller decides how loud to be.
    """
    root = Path(project_root)
    if not version:
        pin = root / "product" / "aiws_version.md"
        if not pin.is_file():
            return None
        for line in read_text(pin).splitlines():
            if line.strip().lower().startswith("aiws_version:"):
                version = line.split(":", 1)[1].strip()
                break
    version = (version or "").strip()
    if not version:
        return None

    rel_root = root / "releases"
    if not rel_root.is_dir():
        return None
    # Match the RELEASE naming convention, not merely "contains the version". Measured: a bare
    # substring match selected `_backup_v1.2.0_2026-08-20_before_guideline_refresh` as the newest,
    # because "_" sorts after uppercase letters - it would have shipped a BACKUP as the release note.
    # The paired probe caught that before anything was written; the pattern is now anchored.
    pat = re.compile(r"^AI_Work_System_MVP_" + re.escape(version) + r"_(\d{4}-\d{2}-\d{2})$")
    matches = sorted(
        ((m.group(1), d) for d, m in
         ((d, pat.match(d.name)) for d in rel_root.iterdir() if d.is_dir())
         if m and (d / RELEASE_NOTES_NAME).is_file()),
    )
    if not matches:
        return None
    chosen = matches[-1][1]          # newest by the DATE SUFFIX, which the pattern guarantees exists
    return (f"releases/{chosen.name}/{RELEASE_NOTES_NAME}", RELEASE_NOTES_NAME)

#: Nguồn cho `DESIGN_DOCS_STRIP_COPY` của builder (CR-AIWS-2026-08-105 C3). Detail_Design bị bỏ.
PAYLOAD_DESIGN_DOCS: "list[str]" = [
    "product/methodology/ai_work_system/10_design/Architecture_Design_MVP.md",
    "product/methodology/ai_work_system/10_design/Basic_Design_MVP.md",
    "product/methodology/ai_work_system/10_design/Conceptual_Design_MVP.md",
    "product/methodology/ai_work_system/10_design/Methodology_Design_MVP.md",
]


def ships(rel_path: str) -> bool:
    """Path (repo-relative) này có đi vào payload của bản cài không?

    Nhận cả `product/...` (nguồn thật) lẫn `.ai-work/...` (bản chạy dual-tree): với dạng thứ hai,
    thử luôn anh em `product/<phần còn lại>` vì mọi thứ ship đều phải sống ở `product/` trước.
    Trả về False cho path không nằm dưới section nào (vd `product/change_requests/...`).
    """
    q = str(rel_path).replace("\\", "/")
    if q.startswith("./"):
        q = q[2:]          # KHÔNG dùng lstrip("./"): nó ăn cả dấu chấm của ".ai-work/"
    candidates = [q]
    if q.startswith(".ai-work/"):
        candidates.append("product/" + q[len(".ai-work/"):])
    # CR-AIWS-2026-08-105 C2 — xét đường ship KHÔNG-qua-section TRƯỚC. Thứ tự này load-bearing:
    # 4 file design nằm DƯỚI một thư mục đang bị section exclude (`10_design`), nên nếu xét section
    # trước thì exclusion sẽ trả False và ta không bao giờ tới được danh sách extra.
    for cand in candidates:
        for extra in PAYLOAD_EXTRA_SHIPPED:
            if cand == extra or cand.startswith(extra + "/"):
                return True

    for cand in candidates:
        for name, src in PAYLOAD_SRC.items():
            if cand == src or cand.startswith(src + "/"):
                rest = cand[len(src):].lstrip("/")
                for ex in PAYLOAD_EXCLUDES.get(name, ()):
                    if rest == ex or rest.startswith(ex + "/"):
                        return False
                return True
    return False


#: Empty placeholders created when writing (never overwrites existing Truth).
TRUTH_STUBS = [
    ".ai-work/truth/SOP_MASTER.md",
    ".ai-work/truth/AI_WORK_CONTRACT.md",
]


# ---------- Operating Memory L2 (CR-AIWS-2026-08-022; promoted here by CR-AIWS-2026-08-029) ----------
# Lives here, not in build_active_step_context.py, because there are now TWO readers: the ASC
# builder (`aiws-aip run start|resume|step`) and `read_operating_memory.py` (which `aiws-aip
# create` calls). Two copies of the display rules -- ordering, age label, budget threshold, the
# "not a rule" caveat -- would drift, which is the failure `meta_roots()` was created to kill
# (Rule 2 / Rule 6).

#: Soft budget -- WARN + gợi ý rà, KHÔNG truncate, KHÔNG tự xoá (khuôn CR-AIWS-2026-07-037).
#: Đếm theo SỐ MỤC (DP-022-D).
OPERATING_MEMORY_BUDGET = 40
#: Mục cũ hơn ngưỡng này được đánh dấu — hint 6 tháng phải TRÔNG KHÁC hint tuần trước.
OPERATING_MEMORY_STALE_DAYS = 180
#: CR-AIWS-2026-08-127 C1/C4 (DP-127-B): MỘT ngưỡng cho cả render lẫn lint. Kho sau rà (AIP-1120) có body
#: max 373 B; kho cũ có 18/31 mục > 400 B — ngưỡng này bắt được kiểu cũ mà không cắt kiểu mới. Render: body
#: dài hơn chỉ in câu đầu + " …"; lint: WARN `operating_memory_body_long`. Đổi số ở ĐÂY, không ở hai chỗ.
OPERATING_MEMORY_BODY_MAX = 400
#: `evidence` = MỘT lệnh/output/locator, không phải chỗ kể chuyện (operating_memory.md §5 — CR-127 C5).
OPERATING_MEMORY_EVIDENCE_MAX = 150
#: Bảy nhóm của operating_memory.md §3 — nguồn duy nhất cho lint off-vocab và cho bảng Kind→nhóm của builder.
OPERATING_MEMORY_GROUPS = (
    "verification_trap", "tool_gotcha", "required_order", "recurring_shape",
    "cost_sizing", "where_to_look", "rejected_option")
#: Tách câu để đếm (>3 câu = body kể chuyện) và để cắt câu đầu khi render.
OPERATING_MEMORY_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")
#: `ref` phải là locator ỔN ĐỊNH (doc#mục · module.symbol · CR/AIP id). Những hình dạng này thì không:
#: workspace path (dời khi archive), CAP id (không có path), file temp, số dòng (chết sau refactor).
OPERATING_MEMORY_REF_UNSTABLE_RE = re.compile(r"workspaces/|\bCAP-\d|temp_|:L?\d+$|#L\d+")

#: Bốn nhóm mà một quyết định LÚC LẬP KẾ HOẠCH thật sự dùng tới (DP-029-A = a, PO chốt 2026-08-17):
#: định cỡ · thứ tự bắt buộc · chỗ-cần-tìm · phương án đã bị bác. `tool_gotcha` /
#: `verification_trap` / `recurring_shape` có giá trị lúc GÕ, và nhánh `run` đã phủ chúng.
OPERATING_MEMORY_PLANNING_GROUPS = (
    "cost_sizing", "required_order", "where_to_look", "rejected_option")


def read_jsonl_lenient(path: Path) -> list[dict[str, Any]]:
    """JSONL reader that SKIPS an unparseable line instead of raising — opposite of `read_jsonl`.

    Two readers, on purpose. `read_jsonl` raises because its callers act on the data: an index or
    a capture inbox with a line nobody can parse is data loss, and saying so loudly is the only
    honest answer. This one serves an ADVISORY store, where the caller must survive a bad line —
    a corrupt hint must never be able to stop an AIP from being created.
    """
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def age_label(verified_at: str, ref_day: "date | None" = None) -> str:
    """`verified_at` -> nhãn tuổi người đọc thấy ngay là cũ hay mới.

    Tuổi là thứ phân biệt một hint còn dùng được với một hint đã mục; hiển thị ngày suông thì
    người đọc phải tự trừ, và sẽ không trừ.
    """
    from datetime import date
    ref_day = ref_day or date.today()   # NB: `today` là helper của module này, đừng che nó
    try:
        d = date.fromisoformat(str(verified_at).strip()[:10])
    except (ValueError, TypeError):
        return "chưa rõ tuổi"
    days = (ref_day - d).days
    if days < 0:
        return f"{verified_at} (ngày ở tương lai?)"
    if days < 14:
        return f"{days} ngày trước"
    if days < 60:
        return f"~{days // 7} tuần trước"
    label = f"~{days // 30} tháng trước"
    return f"{label} — CŨ, rà lại" if days >= OPERATING_MEMORY_STALE_DAYS else label


def operating_memory_digest(ai_work: Path, max_items: int = 8,
                            groups: "Iterable[str] | None" = None,
                            top_up: bool = False) -> list[str]:
    """Digest của Operating Memory L2 — gợi ý tham khảo, KHÔNG phải rule.

    Digest chứ không phải toàn văn (DP-022-B): kho phình thì mỗi lượt đọc không được gánh thêm
    context. Store rỗng/không tồn tại → trả về một dòng nói rõ là rỗng, KHÔNG im lặng — im lặng
    thì không phân biệt được "chưa có gì" với "bước nạp không chạy".

    `groups=None` (mặc định) = không lọc. Lọc là quyết định của người GỌI, không phải của digest:
    `read_operating_memory.py` mặc định truyền `OPERATING_MEMORY_PLANNING_GROUPS`; builder ASC
    truyền lát cắt suy từ `Kind:` (CR-AIWS-2026-08-127 C2). Lọc mà không còn mục nào thì nói RÕ là
    do lọc — nếu in cùng câu với kho trống, người đọc sẽ kết luận sai rằng chưa ai ghi gì.

    Mỗi mục = MỘT dòng head + MỘT dòng body (CR-127 C1): head mang title · nhóm · tuổi · hậu tố
    `→ ref` khi mục có `ref` (đường đọc thêm — HUMAN quyết 2026-08-27); body in nguyên khi ≤
    `OPERATING_MEMORY_BODY_MAX`, dài hơn thì chỉ câu đầu + " …" — guard cho lúc kho trôi dài trở lại,
    cùng ngưỡng với lint `operating_memory_body_long` (DP-127-B). Caveat một dòng, bắt buộc chứa
    chuỗi "KHÔNG phải rule" (test C4 neo — §6 guardrail).

    `top_up=True` (DP-127-C = b): lát cắt ra ít hơn `max_items` thì bù bằng mục mới nhất của các
    nhóm còn lại, mỗi mục bù được ĐÁNH DẤU — người đọc luôn thấy đủ mục, và biết mục nào ngoài lát cắt.
    """
    rows = read_jsonl_lenient(ai_work / "memory" / "entries.jsonl")
    out = ["- Gợi ý tham khảo, **KHÔNG phải rule** — cần tuân thủ ⇒ thuộc canonical "
           "(`.ai-work/procedural/operating_memory.md`)."]
    if not rows:
        out.append("- (Operating Memory trống — chưa có mục nào)")
        return out
    if len(rows) > OPERATING_MEMORY_BUDGET:
        out.append(f"- ⚠️ **{len(rows)} mục > ngưỡng {OPERATING_MEMORY_BUDGET}** — đến lúc rà lại: "
                   f"mỗi mục quá hạn chọn *nâng lên canonical* / *giữ + cập nhật `verified_at`* / "
                   f"*xoá*. Không mục nào bị cắt bỏ tự động.")
    newest_first = sorted(rows, key=lambda r: str(r.get("verified_at", "")), reverse=True)
    total = len(rows)
    if groups is not None:
        want = {str(g).strip() for g in groups if str(g).strip()}
        in_slice = [r for r in newest_first if str(r.get("group", "")).strip() in want]
        if not in_slice and not top_up:
            out.append(f"- (0/{total} mục thuộc nhóm {', '.join(sorted(want))} — **do lọc nhóm**, "
                       f"không phải kho trống)")
            return out
        chosen = [(r, False) for r in in_slice[:max_items]]
        if top_up and len(chosen) < max_items:
            if not in_slice:
                out.append(f"- (0/{total} mục thuộc nhóm {', '.join(sorted(want))} — hiển thị mục mới "
                           f"nhất của mọi nhóm, đánh dấu *bù*)")
            seen = {id(r) for r, _ in chosen}
            for r in newest_first:
                if len(chosen) >= max_items:
                    break
                if id(r) not in seen:
                    chosen.append((r, True))
        remaining = total - len(chosen)
    else:
        chosen = [(r, False) for r in newest_first[:max_items]]
        remaining = total - len(chosen)
    for r, outside in chosen:
        title = str(r.get("title", "(không tiêu đề)")).strip()
        group = str(r.get("group", "")).strip()
        body = " ".join(str(r.get("body", "")).split())
        ref = str(r.get("ref", "")).strip()
        age = age_label(r.get("verified_at", ""))
        head = f"- **{title}**" + (f" `[{group}]`" if group else "") + f" — {age}"
        if ref:
            head += f" → `{ref}`"
        if outside:
            head += " · *(bù — ngoài lát cắt)*"
        out.append(head)
        if body:
            if len(body.encode("utf-8")) > OPERATING_MEMORY_BODY_MAX:
                body = OPERATING_MEMORY_SENTENCE_RE.split(body, maxsplit=1)[0].strip() + " …"
            out.append(f"  {body}")
    if remaining > 0:
        out.append(f"- … còn {remaining} mục — xem `.ai-work/memory/entries.jsonl`")
    return out


# ---------- Wiki index scope machinery (CR-AIWS-2026-07-024) ----------
# Promoted from lookup_wiki_source.py so every index-reading tool shares ONE
# scope/authorization resolver (no tool may re-implement its own index loader —
# that is exactly the drift that produced the corpus-invisible blocker OP-931-02).
# Semantics per CR-AIWS-2026-06-052: narrow-by-default; 'local' is rule-#11-gated.

DEFAULT_SCOPE = "project,aiws"   # lookup's default; build_wiki_page_base hard-requires --scope (DP-024-A)
VALID_SCOPES = {"project", "local", "aiws"}

_SCOPE_INDEX_FILES = (            # order preserved from lookup_wiki_source.py (byte-identical behavior)
    ("project", "index.jsonl"),
    ("local", "index.local.jsonl"),
    ("aiws", "index.aiws.jsonl"),
)


def parse_scope(raw: str, default: str = DEFAULT_SCOPE) -> set:
    """Parse a comma-list --scope value into a set of registered indices.

    'all' expands to the full set. Raises ValueError on an unknown token
    (CR-AIWS-2026-06-052).
    """
    toks = {t.strip().lower() for t in (raw or "").split(",") if t.strip()}
    if not toks:
        toks = {t.strip() for t in default.split(",")}
    if "all" in toks:
        return set(VALID_SCOPES)
    bad = toks - VALID_SCOPES
    if bad:
        raise ValueError(
            f"unknown --scope value(s) {sorted(bad)}; valid: "
            f"{sorted(VALID_SCOPES)} or 'all' (comma-list)"
        )
    return toks


# CR-AIWS-2026-08-058 — curation-state là CỦA HUMAN: builder refresh/regenerate phải CARRY các
# field này từ meta cũ khi caller không truyền giá trị khác default (builder chỉ được đổi khi flag
# tương ứng truyền tường minh). MỘT tuple chung để các builder không drift (Rule 6 tinh thần).
# (field, builder_default) — `system:` có luật preserve riêng sẵn (CR-AIWS-2026-06-058).
CURATION_PRESERVE_FIELDS = (
    ("maintenance_status", "needs_review"),
    ("promotion_status", "draft"),
    ("authority_level", "unknown"),
    ("freshness_status", "unknown"),
    ("knowledge_value", "unknown"),
    ("intended_ai_use", "unknown"),
    # CR-AIWS-2026-08-092 C3 — curator marker `related_sources: none_by_design` ("this source has
    # no relationships, on purpose"). The builder never emits it, so the empty default means the
    # old value always carries; builder + refresh then skip the RS scaffold and lint stops asking.
    ("related_sources", ""),
)


def carry_curation_state(meta: dict, existing_fm: dict) -> list:
    """CR-AIWS-2026-08-058 — áp CURATION_PRESERVE_FIELDS: field trong `meta` đang ở builder-default
    mà meta cũ có giá trị khác default → carry giá trị cũ. Trả về list field đã carry (log)."""
    carried = []
    for f, default in CURATION_PRESERVE_FIELDS:
        old = str((existing_fm or {}).get(f, "")).strip()
        if old and old != default and str(meta.get(f, "")).strip() in (default, ""):
            meta[f] = old
            carried.append(f)
    return carried


# `wiki_single_index(ai_work)` lived here until CR-AIWS-2026-08-128 C3. It re-read the profile with a
# REGEX for one key, inside the same module whose canonical reader documents itself as existing "so the
# config parser cannot drift between tools" — the drift the docstring warned about was two functions
# apart. The key is unchanged and still means what CR-AIWS-2026-08-052 defined; it now arrives through
# `read_project_config(ai_work)["wiki_single_index"]`, which is also why a damaged profile can no longer
# silently answer False here. Four call sites moved with it (build_canonical_package_metas,
# build_preset_wiki, build_relations, build_wiki_source_index).


def resolve_index_paths(wiki_sources: Path, scope_set) -> list:
    """Registered index files for a scope set — existing files only, stable order
    (project → local → aiws, matching lookup's historical concat order).

    CR-AIWS-2026-08-052 C5 — single-index fallback: when scope asks for 'aiws' but
    index.aiws.jsonl does not exist (single-index repo: aiws_meta entries folded into
    index.jsonl), the aiws scope is served by index.jsonl. In such repos the project/aiws
    scope distinction collapses (both read the one merged index); dual-index projects are
    byte-identical to before."""
    out = []
    for name, fname in _SCOPE_INDEX_FILES:
        if name in scope_set:
            p = wiki_sources / fname
            if p.exists():
                out.append(p)
    if "aiws" in set(scope_set) and not (wiki_sources / "index.aiws.jsonl").exists():
        merged = wiki_sources / "index.jsonl"
        if merged.exists() and merged not in out:
            out.append(merged)
    return out


_SCOPE_RELATIONS_FILES = (   # CR-AIWS-2026-08-064 C2 — mirrors _SCOPE_INDEX_FILES (same scope vocabulary)
    ("project", "relations.jsonl"),
    ("local", "relations.local.jsonl"),
    ("aiws", "relations.aiws.jsonl"),
)


def resolve_relations_paths(wiki_sources: Path, scope_set) -> list:
    """Relations projection files for a scope set — existing files only, stable order
    (project → local → aiws), symmetric with `resolve_index_paths` (CR-AIWS-2026-08-064 C2).

    THE ONE resolver for relations namespaces (Rule 6): consumers (`wiki_relations`,
    `build_reading_kit`, `build_wiki_overview`, `lint_wiki`) MUST NOT compose file names
    themselves. `relations.aiws.jsonl` = the shipped AIWS preset edges (built by
    `build_preset_wiki.py` / `build_relations.py --namespace aiws`); `relations.jsonl` = the
    project's own edges. `local` is authorization-gated exactly like `index.local.jsonl` —
    resolved only when the caller passes it in `scope_set`.

    Collapse rule (same shape as CR-052 C5 for indices): scope asks for `aiws` but
    `relations.aiws.jsonl` does not exist (single-index repo, or a downstream install that has
    not built the preset yet) → the aiws scope is served by `relations.jsonl`, which in those
    trees already carries every namespace (`build_relations --namespace all`). Projects that
    never build the preset are byte-identical to before."""
    out = []
    for name, fname in _SCOPE_RELATIONS_FILES:
        if name in scope_set:
            p = wiki_sources / fname
            if p.exists():
                out.append(p)
    if "aiws" in set(scope_set) and not (wiki_sources / "relations.aiws.jsonl").exists():
        merged = wiki_sources / "relations.jsonl"
        if merged.exists() and merged not in out:
            out.append(merged)
    return out


def scope_needs_authorization(scope_set) -> bool:
    """True when the scope extends beyond the narrow default project,aiws
    (e.g. includes 'local') — requires --authorized (rule #11 / CR-052)."""
    return bool(set(scope_set) - {"project", "aiws"})


# ── Namespace discipline (CR-AIWS-2026-07-049) ────────────────────────────────
# ONE source of truth for "which meta dirs exist" and "which indices resolve an id".
# Every tool that READS metas or resolves a source_id MUST use these — a tool that picks its own
# root is how the same blind-spot shipped FIVE times (lint meta-scan · build_relations ·
# _lint_relations · wiki_relations · detect_changed_wiki_sources), each one silently ignoring the
# 188 shipped AIWS metas. See procedural/tooling_authoring_conventions.md Rule 6.

def md_headings(text: str, max_depth: int = 2) -> list:
    """Markdown headings up to `max_depth`, IGNORING anything inside a fenced code block.

    CR-AIWS-2026-07-052 T1. The old regex-only scan treated `# comment` lines inside a ```python
    fence as headings: a doc whose code sample contained `# WRONG` / `# RIGHT` produced
    `- heading: WRONG` in its Source-Specific Hints. CR-AIWS-2026-07-006 made the section CHUNKER
    fence-aware but this scanner was never touched — same bug class, different call site.
    Both ``` and ~~~ fences count; an unterminated fence swallows the rest of the file (that is what
    a renderer does too).
    """
    import re as _re
    pat = _re.compile(r"^#{1,%d}\s+(.+)$" % max(1, min(int(max_depth), 6)))
    out: list = []
    fence = ""
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            marker = stripped[:3]
            if not fence:
                fence = marker
            elif marker == fence:
                fence = ""
            continue
        if fence:
            continue
        m = pat.match(line)
        if m:
            out.append(m.group(1).strip())
    return out


def meta_roots(ai_work: Path) -> list:
    """Every meta namespace that EXISTS: the project's `wiki_sources/meta/` and the shipped
    `wiki_sources/aiws_meta/`. Order is stable (project first). Callers still skip `*.refresh.md`
    drafts themselves (that is a per-tool concern, not a namespace one)."""
    ws = ai_work / "wiki_sources"
    return [d for d in (ws / "meta", ws / "aiws_meta") if d.is_dir()]


def all_index_paths(wiki_sources: Path) -> list:
    """Every index used to RESOLVE an id/endpoint: `index.jsonl` + `index.aiws.jsonl` (existing
    files only, stable order).

    Deliberately EXCLUDES `index.local.jsonl`: the local index is authorization-gated (rule #11 /
    #13). This helper is for *resolution* (does this source_id exist? what is its title?), never
    for *search* — a scoped search must still go through `parse_scope` + `resolve_index_paths` so
    the authorization gate keeps working."""
    out = []
    for fname in ("index.jsonl", "index.aiws.jsonl"):
        p = wiki_sources / fname
        if p.exists():
            out.append(p)
    return out


def index_inventory(wiki_sources: Path, include_local: bool = False) -> list:
    """Deterministic per-index metadata (scope name / path / exists / entry count /
    per-system counts) for Gate 0 of /aiws-wiki build-pages (CR-AIWS-2026-07-024).

    DP-024-B (PO override, rule #11): the local index is HIDDEN entirely unless
    include_local=True (explicit authorization) — not even its metadata is listed
    without it. Reads index records only — never artifact content.
    """
    out = []
    for name, fname in _SCOPE_INDEX_FILES:
        if name == "local" and not include_local:
            continue
        p = wiki_sources / fname
        entry = {"scope": name, "path": str(p), "exists": p.exists(),
                 "entries": 0, "by_system": {}}
        if p.exists():
            recs = read_jsonl(p)
            entry["entries"] = len(recs)
            for r in recs:
                sysid = r.get("system") or "(none)"
                entry["by_system"][sysid] = entry["by_system"].get(sysid, 0) + 1
        out.append(entry)
    return out


# ---------- Wiki Source maintenance-log writer (CR-AIWS-2026-05-006) ----------

# Single source of truth for required maintenance-log fields. lint_wiki imports
# this instead of keeping its own copy, so the writer and the linter cannot drift.
WSM_REQUIRED_LOG_FIELDS = [
    "log_id", "timestamp", "action", "source_id", "target_artifact",
    "change_summary", "review_decision", "rollback_hint",
]


def append_maintenance_log(log_path: Path, entry: dict[str, Any]) -> None:
    """Append one WSM maintenance entry, schema-checked and newline-safe.

    Newline-safe theo HAI nghĩa: (1) heal dòng cuối thiếu "\n" của lần append trước;
    (2) ghi bằng newline="\n" nên không sinh CRLF trên Windows.

    Used by every tool/skill that writes maintenance_log.jsonl so the schema and
    newline framing cannot drift between writers (CR-AIWS-2026-05-006, IR-07/08).

    - Raises ValueError if any WSM_REQUIRED_LOG_FIELDS is missing/empty.
    - Heals a prior missing trailing newline before appending (fixes IR-08:
      two JSON objects concatenated onto one physical line).
    - Writes exactly one record followed by a single newline.
    """
    missing = [k for k in WSM_REQUIRED_LOG_FIELDS if entry.get(k) in (None, "", [])]
    if missing:
        raise ValueError(f"maintenance_log entry missing required fields: {missing}")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    if log_path.exists():
        data = log_path.read_bytes()
        if data and not data.endswith(b"\n"):
            with log_path.open("ab") as f:
                f.write(b"\n")  # heal a prior append that omitted its newline
    # newline="\n": text-mode append trên Windows dịch "\n" -> CRLF, ghi CRLF vào file LF
    # (CR-AIWS-2026-08-096, lớp 2 của CR-059). Mọi writer text-mode trong tooling/ phải khai cờ này.
    with log_path.open("a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# ---------- Lint result model ----------

SEV_ERROR = "error"
SEV_WARNING = "warning"
SEV_INFO = "info"

# ---------- Inline lint_accept (CR-AIWS-2026-06-065) ----------
# Self-guard codes generated by apply_lint_accept itself — never acceptable.
LINT_ACCEPT_SELF_CODES = {"lint_accept_malformed", "lint_accept_unused",
                          "lint_accept_class_noise"}
# CR-AIWS-2026-07-036 T2 (DP-036-1 = N=3): muting the SAME code across this many distinct files
# is class-level noise — the signal is "refine the rule (via CR)", not "mute one more file".
# 2 is deliberately allowed: a dual-tree pair of the same content is a legitimate 2-file mute.
LINT_ACCEPT_CLASS_NOISE_THRESHOLD = 3
# Required fields on every lint_accept entry (governance audit trail).
LINT_ACCEPT_REQUIRED = ("code", "reason", "accepted_by")
# In-scope dirs (relative to .ai-work) for inline lint_accept.
# CR-AIWS-2026-08-091 DP-091-C: deliberately NOT widened to `agents/` — an immutable run record
# should not NEED an accept; the rule stops scanning that zone instead (check_dual_tree
# PROJECT_LOCAL_PREFIXES).
LINT_ACCEPT_SCOPE_DIRS = ("wiki_sources/meta", "wiki_sources/aiws_meta", "wiki", "aip")
# CR-AIWS-2026-08-091 C3 — RENAMED finding codes, honoured at the ACCEPT layer: an entry keyed on
# the OLD code mutes findings emitted under the NEW code (and vice-versa is unnecessary — only the
# new code is emitted). CR-078 C2 had tried to keep old accepts alive by EMITTING the old code as a
# second finding; that doubled `errors` and rescued nothing, because the match below is by exact
# string. Retirement horizon (DP-091-B = a): ONE release counted from CR-091's apply (the CR-078
# clock never ran — its alias never worked). When retiring, drop the entry here; a stale accept
# then surfaces as `lint_accept_unused`, which is the visible failure the alias exists to avoid.
LINT_ACCEPT_CODE_ALIASES: dict[str, str] = {
    "skill_link_broken": "dualtree_link_broken",   # CR-AIWS-2026-08-078 rename
}


def resolve_lint_accept_code(code: str) -> str:
    """Canonical finding code for a `lint_accept` entry (alias → current name; else unchanged)."""
    return LINT_ACCEPT_CODE_ALIASES.get(code, code)


@dataclass
class LintFinding:
    severity: str
    code: str
    message: str
    path: str = ""
    location: str = ""


@dataclass
class AcceptedFinding:
    """A finding muted by an inline lint_accept entry (CR-AIWS-2026-06-065)."""
    finding: LintFinding
    reason: str
    accepted_by: str


@dataclass
class LintReport:
    target: str
    findings: list[LintFinding] = field(default_factory=list)
    accepted: list[AcceptedFinding] = field(default_factory=list)

    def error(self, code: str, msg: str, path: str = "", loc: str = "") -> None:
        self.findings.append(LintFinding(SEV_ERROR, code, msg, path, loc))

    def warn(self, code: str, msg: str, path: str = "", loc: str = "") -> None:
        self.findings.append(LintFinding(SEV_WARNING, code, msg, path, loc))

    def info(self, code: str, msg: str, path: str = "", loc: str = "") -> None:
        self.findings.append(LintFinding(SEV_INFO, code, msg, path, loc))

    def counts(self) -> dict[str, int]:
        c = {SEV_ERROR: 0, SEV_WARNING: 0, SEV_INFO: 0}
        for f in self.findings:
            c[f.severity] = c.get(f.severity, 0) + 1
        c["accepted"] = len(self.accepted)
        return c

    def exit_code(self, strict: bool) -> int:
        c = self.counts()
        if c[SEV_ERROR] > 0:
            return 2
        if strict and c[SEV_WARNING] > 0:
            return 1
        return 0


def _is_lint_accept_scope(path: Path, ai_work: Path) -> bool:
    """True if path is a frontmatter-bearing file eligible for inline lint_accept
    (CR-AIWS-2026-06-065): an .md under wiki_sources/meta/, wiki/, or aip/ — plus, since
    CR-AIWS-2026-08-004, product/change_requests/ (CR docs carry their own grandfather accepts,
    e.g. applied_without_apply_outcome; the same inline-with-reason + strip-on-rewrite + class-noise
    guards apply unchanged)."""
    try:
        if path.suffix.lower() != ".md" or not path.is_file():
            return False
        rp = path.resolve()
        try:
            rp.relative_to((ai_work.parent / "product" / "change_requests").resolve())
            return True
        except ValueError:
            pass
        rel = rp.relative_to(ai_work.resolve()).as_posix()
    except (ValueError, OSError):
        return False
    return any(rel == d or rel.startswith(d + "/") for d in LINT_ACCEPT_SCOPE_DIRS)


def apply_lint_accept(report: LintReport, ai_work: Path) -> None:
    """Post-pass: honor inline `lint_accept` frontmatter on in-scope files.
    Moves accepted findings from report.findings to report.accepted; appends
    lint_accept_malformed (ERROR) / lint_accept_unused (WARNING) findings.
    Self-guard codes can never be accepted. (CR-AIWS-2026-06-065)"""
    by_path: dict[str, list[LintFinding]] = {}
    for f in report.findings:
        if f.path:
            by_path.setdefault(f.path, []).append(f)

    accepts: dict[str, list[dict]] = {}
    malformed: dict[str, list[str]] = {}
    for p in by_path:
        path = Path(p)
        if not _is_lint_accept_scope(path, ai_work):
            continue
        try:
            meta, _ = parse_frontmatter(read_text(path))
        except OSError:
            continue
        raw = meta.get("lint_accept")
        if not raw:
            continue
        entries: list[dict] = []
        msgs: list[str] = []
        if not isinstance(raw, list):
            msgs.append("lint_accept must be a list of mappings")
        else:
            for e in raw:
                if not isinstance(e, dict):
                    msgs.append(f"entry is not a mapping: {e!r}")
                    continue
                miss = [k for k in LINT_ACCEPT_REQUIRED if not str(e.get(k, "")).strip()]
                if miss:
                    msgs.append(f"entry missing {miss} (code={e.get('code')!r})")
                    continue
                if e["code"] in LINT_ACCEPT_SELF_CODES:
                    msgs.append(f"cannot accept self-guard code {e['code']}")
                    continue
                entries.append(e)
        accepts[p] = entries
        if msgs:
            malformed[p] = msgs

    active: list[LintFinding] = []
    for f in report.findings:
        # CR-AIWS-2026-08-091 C3 — match through the alias table: an accept keyed on a retired
        # code (`skill_link_broken`) mutes the finding emitted under its current name.
        entry = next((e for e in accepts.get(f.path, [])
                      if resolve_lint_accept_code(e["code"]) == f.code), None)
        if entry is not None:
            report.accepted.append(
                AcceptedFinding(f, str(entry["reason"]), str(entry["accepted_by"]))
            )
        else:
            active.append(f)
    report.findings = active

    for p, msgs in malformed.items():
        for m in msgs:
            report.error("lint_accept_malformed", m, path=p)
    for p, entries in accepts.items():
        present = {f.code for f in by_path.get(p, [])}
        for e in entries:
            # alias-aware: an old-code entry that matched through the alias is NOT unused
            if resolve_lint_accept_code(e["code"]) not in present:
                report.warn("lint_accept_unused",
                            f"lint_accept code '{e['code']}' matches no finding on this file",
                            path=p)

    # CR-AIWS-2026-07-036 T2 — class-noise guard: a code muted across >= N DISTINCT files means
    # the RULE is noisy, not that the files are exceptional. Mute is per-instance by design
    # (policy: aiws-lint operations/all.md); a repeated mute of one code is the signal to REFINE
    # the rule via CR. WARN only — a legitimate group-wide mute must not break the gate.
    files_by_code: dict[str, set] = {}
    for a in report.accepted:
        f = getattr(a, "finding", None)
        code = getattr(f, "code", None)
        path = getattr(f, "path", None)
        if code and path:
            files_by_code.setdefault(code, set()).add(path)
    for code, paths in sorted(files_by_code.items()):
        if len(paths) >= LINT_ACCEPT_CLASS_NOISE_THRESHOLD:
            report.warn(
                "lint_accept_class_noise",
                f"code '{code}' is accept-muted in {len(paths)} files — that is class-level "
                f"noise, not {len(paths)} exceptions: REFINE THE RULE via a CR instead of muting "
                f"another file (a rule people routinely mute has stopped being a guardrail; "
                f"CR-AIWS-2026-07-036 — see aiws-lint operations/all.md)")


def render_report(report: LintReport, fmt: str, show_accepted: bool = False) -> str:
    if fmt == "json":
        return json.dumps(
            {
                "target": report.target,
                "counts": report.counts(),
                "findings": [asdict(f) for f in report.findings],
                "accepted": [
                    {"finding": asdict(a.finding), "reason": a.reason,
                     "accepted_by": a.accepted_by}
                    for a in report.accepted
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
    # text
    lines = [f"lint target: {report.target}"]
    if not report.findings:
        lines.append("  OK — no findings")
    for f in report.findings:
        loc = f" @ {f.location}" if f.location else ""
        p = f" ({f.path})" if f.path else ""
        lines.append(f"  [{f.severity.upper()}] {f.code}: {f.message}{loc}{p}")
    if show_accepted:
        for a in report.accepted:
            p = f" ({a.finding.path})" if a.finding.path else ""
            lines.append(f"  [ACCEPTED] {a.finding.code}: {a.finding.message}{p}")
            lines.append(f"      reason: {a.reason!r} — by {a.accepted_by}")
    c = report.counts()
    summary = (f"summary: errors={c[SEV_ERROR]} warnings={c[SEV_WARNING]} "
               f"info={c[SEV_INFO]}")
    if c["accepted"]:
        summary += f" accepted={c['accepted']}"
    lines.append(summary)
    if c["accepted"] and not show_accepted:
        lines.append(f"  ({c['accepted']} findings hidden by lint_accept — "
                     f"run with --show-accepted to list)")
    return "\n".join(lines)


def emit_report(report: LintReport, fmt: str, strict: bool,
                show_accepted: bool = False) -> int:
    print(render_report(report, fmt, show_accepted))
    return report.exit_code(strict)


# ---------- Path helpers ----------

# AIP-EXEC-1137 — what makes a `.ai-work/` a REAL project root rather than a stray nested dir.
# `tooling/` and `wiki_sources/` are deliberately ABSENT, and widening this set is exactly how the
# bug comes back:
#   * `tooling/` is what the proven-causal stray held — `.ai-work/tooling/.ai-work/tooling/…`
#     (commit 528968e) re-rooted every tool run from the tooling dir and turned three battery tests
#     red. A marker set containing `tooling/` accepts that stray and fixes nothing.
#   * `wiki_sources/` is carried by BOTH shipped test fixtures, so it qualifies almost anything.
AIWS_ROOT_MARKERS = ("project_profile.yml", "truth", "AIWS.md")


def _is_aiws_root_dir(ai_work: Path) -> bool:
    """True when this `.ai-work/` carries at least one marker of a real AIWS project root."""
    return any((ai_work / m).exists() for m in AIWS_ROOT_MARKERS)


def find_ai_work_root(start: Path) -> Path:
    """Walk up from start to the project root — the directory containing `.ai-work/`.

    Returns the NEAREST ancestor whose `.ai-work/` carries an AIWS marker, so a stray nested
    `.ai-work/` cannot hijack the walk. Three of those were live in this repo on 2026-08-27: two
    empty dirs (one made `lint_aip` report `ref_missing` for 13 paths that existed) and one holding
    a misplaced tracked file (three red battery tests, proven by move-aside/restore). 38 tool files
    resolve the root through here, so a wrong answer is silently wrong everywhere downstream.

    PREFERENCE, NOT REQUIREMENT: when no candidate carries a marker, the first match is returned —
    the pre-guard behaviour. Being stricter would break trees that legitimately have none, e.g. the
    temp root built by `cobol_wiki_tests/test_units.py` holding only `.ai-work/tooling/_common.py`.
    So this is never worse than before: whatever resolved yesterday still resolves.
    """
    cur = start.resolve()
    candidates = [p for p in [cur, *cur.parents] if (p / ".ai-work").is_dir()]
    for i, p in enumerate(candidates):
        if _is_aiws_root_dir(p / ".ai-work"):
            if i:
                # Say it out loud. Silence is what made the original incident expensive: the wrong
                # root produced plausible-looking output for a day before anyone questioned it.
                sys.stderr.write(
                    "warning: ignoring %d nested .ai-work/ dir(s) between %s and the project root "
                    "%s — a stray .ai-work/ (often an empty dir or a misplaced file) does not make "
                    "a project root\n" % (i, start, p))
            return p
    if candidates:
        return candidates[0]
    raise SystemExit(f"error: no .ai-work/ ancestor found from {start}")


ACCOUNT_INFO_NAME = "account_info.yaml"

# ---------- Capture Backlog (CR-AIWS-2026-08-125 C3) ----------
# A capture deferred at AIP close leaves the workspace (gitignored, archived on close) and lands in a
# git-tracked, PER-ACCOUNT store. Per-account rather than per-AIP because the question the store has to
# answer is "what do I still owe?", which is a person's question, not an AIP's — measured on 3 projects,
# a per-AIP file would have scattered 76 rows across 41 files, none of which anyone would ever open.
CAPTURE_BACKLOG_DIRNAME = "capture_backlog"
CAPTURE_BACKLOG_BUDGET = 50          # rows past which `run status` starts nagging
CAPTURE_BACKLOG_STALE_DAYS = 90      # age past which an open row is called out by name

CAPTURE_BACKLOG_README = """# Capture Backlog

Captures deferred at AIP close, one JSONL file per account (`<account_id>.jsonl`).

A row here is a **decision already taken that lacks a destination**: someone judged it worth keeping but
not worth triaging in that session. It is NOT a parking space for undecided rows — an untriaged capture
stays `captured` in its workspace and blocks the close, on purpose.

Each row is **self-contained**: workspaces are gitignored and get archived, so a backlog row that merely
pointed at one would rot. Written only by `triage_capture.py`; never hand-edited.

- `status`: `open` | `triaged` | `promoted` | `discarded` — a backlog vocabulary, deliberately NOT part
  of `CAPTURE_STATUS_ENUM`.
- `resolution`: `{resolved_at, resolved_by, disposition_ref}`, where `disposition_ref` names what the row
  *became* — a CR id, a checklist item, a wiki `source_id`, a lint code.
"""


def capture_backlog_dir(ai_work: Path) -> Path:
    """`.ai-work/capture_backlog/` — created on demand by the writer, not by an installer."""
    return ai_work / CAPTURE_BACKLOG_DIRNAME


def capture_backlog_path(ai_work: Path, account_id: str = "") -> Path:
    """The backlog file for `account_id` (default: this checkout's account).

    Falls back to `_unassigned.jsonl` when no account is configured, so a deferral is never silently
    dropped on a checkout that has not run `account_id.py` — losing the row would be worse than
    filing it under a name that is obviously a placeholder.
    """
    acc = (account_id or read_account_id(ai_work) or "_unassigned").strip()
    return capture_backlog_dir(ai_work) / f"{acc}.jsonl"


def read_account_id(ai_work: Path) -> str:
    """Read account_id from .ai-work/account_info.yaml (CR-AIWS-2026-06-015 v2).

    The local, gitignored account_info.yaml carries the member identity + the per-member AIP id
    counter. Returns the account_id, or '' if the file is missing/unset — callers decide whether
    that is fatal (the allocator errors; init_workspace / run_aip fall back to legacy flat).
    """
    p = ai_work / ACCOUNT_INFO_NAME
    if not p.is_file():
        return ""
    try:
        meta, _ = parse_frontmatter("---\n" + read_text(p).strip("\n") + "\n---\n")
    except Exception:
        return ""
    return str(meta.get("account_id", "")).strip()


def account_identity_state(ai_work: Path) -> "tuple[str, str]":
    """`(account_id, state)` — danh tính account ĐÃ ĐƯỢC NGƯỜI PHÊ hay chưa (CR-AIWS-2026-08-117 C1).

    `state` ∈:
      * `"ratified"`            — file có `account_id` và KHÔNG mang `provisional: true`
      * `"provisional:<src>"`   — `account_id.py resolve` đã suy ra id từ env/namespace, chờ HUMAN phê
      * `"unset"`               — không có file, hoặc có file mà không đọc được `account_id`

    Vì sao `"unset"` cũng KHÔNG phải ratified: `CR-AIWS-2026-08-076` đặt cổng `draft → active` quanh cờ
    `provisional`, nhưng cờ đó chỉ tồn tại SAU KHI ai đó chạy `account_id.py resolve` — và chính CR-076
    đã tự khai *"`resolve` chưa được gọi từ đâu cả"*. Trên một cây chưa ai chạy nó, `account_info.yaml`
    hoặc vắng mặt hoặc rỗng, và một cổng chỉ hỏi `provisional == true` sẽ **im lặng cho qua** đúng cái
    ca đã sinh ra `IR-2026-08-20`. Câu hỏi đúng không phải *"có bị đánh dấu tạm không"* mà là
    *"đã có ai xác nhận danh tính này chưa"* — và cả hai trạng thái trên đều trả lời KHÔNG.

    `read_account_id()` giữ nguyên chữ ký và hành vi: nó có nhiều call site chỉ cần cái id.
    """
    p = ai_work / ACCOUNT_INFO_NAME
    if not p.is_file():
        return "", "unset"
    try:
        meta, _ = parse_frontmatter("---\n" + read_text(p).strip("\n") + "\n---\n")
    except Exception:  # noqa: BLE001
        return "", "unset"
    aid = str(meta.get("account_id", "")).strip()
    if not aid:
        return "", "unset"
    if str(meta.get("provisional", "")).strip().lower() in ("true", "yes", "1"):
        src = str(meta.get("provisional_source", "")).strip() or "unknown"
        return aid, f"provisional:{src}"
    return aid, "ratified"


# ---------- Multi-system scoping primitives (CR-AIWS-2026-06-017; centralized CR-AIWS-2026-06-061) ----------
# Single source of truth for the system-aware tooling contract (WIKI_META_INDEX_SPEC §8.5):
# config read, membership predicate, and id validation. Every meta writer / index projector /
# query / regression test / config reader MUST consume these rather than re-deriving them, so the
# parser (incl. inline-comment handling) and the gate cannot drift between tools.

# ---------- project_profile.yml schema (CR-AIWS-2026-08-128 C1) ----------
#: Bump when a key is added or its requirement changes. `project_profile.py refresh` writes this value
#: into the AIWS-managed block, so the supplement path can tell WHICH schema a file is completing —
#: without it, "incomplete" loses meaning the first time the schema moves.
PROJECT_PROFILE_SCHEMA_VERSION = 1

#: Every key is here because a READER READS IT — the schema was derived from the readers, not designed
#: (AIP-EXEC-1119 STEP-01). Nothing is inherited from the never-implemented DH-06 template: the HUMAN
#: ruled it ignored on 2026-08-27, and a grep confirmed no tool reads any of its 14 policy sections.
#:   required     — must be present for the profile to be COMPLETE
#:   gates_guard  — absence/emptiness of this key can DISARM a check; these are the fail-closed keys
PROJECT_PROFILE_SCHEMA: "dict[str, dict]" = {
    "schema_version":    {"required": True,  "default": PROJECT_PROFILE_SCHEMA_VERSION,
                          "gates_guard": False,
                          "doc": "which schema revision this file targets"},
    "multi_system":      {"required": True,  "default": False, "gates_guard": True,
                          "doc": "does this project host more than one system/subsystem?"},
    "systems":           {"required": False, "default": [], "gates_guard": True,
                          "required_iff": "multi_system",
                          "doc": "the valid system ids; REQUIRED when multi_system is true"},
    "synthetic_systems": {"required": False, "default": [], "gates_guard": True,
                          "doc": "which system ids are fixture/test corpora"},
    "capture_kinds":     {"required": False, "default": {}, "gates_guard": False,
                          "doc": "this project's own capture kinds, namespaced "
                                 "(CR-AIWS-2026-08-126 C4) - a project may add a KIND, never a "
                                 "`type` or a `suggested_target`"},
    "wiki_single_index": {"required": False, "default": False, "gates_guard": False,
                          "doc": "keep ONE index.jsonl instead of the dual-index layout"},
}

#: "Complete" is keys AND invariants (HUMAN ruling OP-1119-02). A file can carry every required key and
#: still be broken — `systems: []` under `multi_system: true` is exactly that shape, and it is the shape
#: that silently accepted any system id before CR-AIWS-2026-08-128. Each entry names the guard it
#: protects, so a reader can see why it is an invariant and not a preference.
#: (code, message, predicate over the parsed cfg dict, guard protected)
PROJECT_PROFILE_INVARIANTS = (
    ("multi_system_without_systems",
     "multi_system: true requires a non-empty `systems:` list",
     lambda cfg: not (cfg.get("multi_system") and not cfg.get("systems")),
     "validate_system — with an empty list it accepted ANY system id"),
    ("synthetic_not_in_systems",
     "every `synthetic_systems` id must also appear in `systems`",
     lambda cfg: set(cfg.get("synthetic_systems") or []) <= set(cfg.get("systems") or []),
     "fixture_under_real_system — an unlisted synthetic id is not recognised as synthetic"),
)


class ProjectProfileUnreadable(Exception):
    """The profile exists but could not be parsed (CR-AIWS-2026-08-128 C3).

    ABSENT and UNPARSEABLE are different facts and must not share a code path. Absent is legitimate —
    a single-system project simply has no profile, and the documented defaults apply. Unparseable means
    the file that gates system scoping is damaged, and before this exception it read as
    `multi_system: False` — indistinguishable from a healthy single-system project, with every guard
    fed by it silently off. Measured 2026-08-27: a garbage profile accepted a bogus system id.
    """


PROJECT_PROFILE_BLOCK_BEGIN = "# AIWS:BEGIN project_profile v"
PROJECT_PROFILE_BLOCK_END = "# AIWS:END"


def profile_upsert(path: "Path", updates: "dict", *, create_block: bool = True) -> "list[str]":
    """Set or insert top-level scalar keys in `project_profile.yml`, touching ONLY affected lines.

    Returns the list of keys actually changed (empty == the file already said this).

    THE WHOLE POINT IS WHAT IT DOES NOT TOUCH. Parsing this file and dumping it back collapses it:
    measured on the AIWS repo's own profile, 2470 B -> 124 B, taking all 30 comment lines with it — and
    those comments are where the reasons live, including the record of a parser bug that once disarmed
    a guard. So this is line-addressed, never a re-serialisation.

    The technique is generalised from `switch_system_mode._set_mode`, which had been editing this exact
    file safely for months: read bytes, tolerate a BOM, split lines, replace the ONE line that matches,
    preserve that line's own EOL, write bytes back. Everything else survives by construction.

    Keys that do not exist yet are appended inside the AIWS-managed block
    (`# AIWS:BEGIN project_profile v<N>` … `# AIWS:END`), created at EOF when absent. Everything
    outside the block is project-owned and is never rewritten — the same contract the rules file uses.
    """
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    if bom:
        raw = raw[3:]
    lines = raw.decode("utf-8").split("\n")

    changed: "list[str]" = []
    pending = dict(updates)

    for i, ln in enumerate(lines):
        stripped = ln.strip()
        for key in list(pending):
            if stripped.startswith(f"{key}:") and not stripped.startswith("#"):
                eol = "\r" if ln.endswith("\r") else ""
                new = f"{key}: {_profile_scalar(pending[key])}{eol}"
                if lines[i] != new:
                    lines[i] = new
                    changed.append(key)
                pending.pop(key)
                break

    if pending and create_block:
        begin_at = next((i for i, l in enumerate(lines)
                         if l.strip().startswith(PROJECT_PROFILE_BLOCK_BEGIN)), None)
        if begin_at is None:
            while lines and not lines[-1].strip():
                lines.pop()
            lines += [
                "",
                f"{PROJECT_PROFILE_BLOCK_BEGIN}{PROJECT_PROFILE_SCHEMA_VERSION}",
                "# Keys AIWS manages. Everything OUTSIDE this block is yours and is never overwritten.",
            ]
            insert_at = len(lines)
            tail = [PROJECT_PROFILE_BLOCK_END, ""]
        else:
            end_at = next((i for i in range(begin_at + 1, len(lines))
                           if lines[i].strip() == PROJECT_PROFILE_BLOCK_END), None)
            assert end_at is not None, f"{path}: AIWS:BEGIN without a matching AIWS:END"
            insert_at, tail = end_at, []
        added = [f"{k}: {_profile_scalar(v)}" for k, v in pending.items()]
        lines[insert_at:insert_at] = added + tail
        changed.extend(pending)

    out = "\n".join(lines).encode("utf-8")
    path.write_bytes((b"\xef\xbb\xbf" + out) if bom else out)
    return changed


def _profile_scalar(v) -> str:
    """Render a scalar the way this file writes them (lists are not upserted — they are hand-owned)."""
    if isinstance(v, bool):
        return "true" if v else "false"
    return str(v)


def project_profile_report(cfg: dict) -> "list[tuple[str, str, str]]":
    """Which invariants a parsed profile violates → [(code, message, guard_protected), ...].

    Empty list == the invariants hold. Callers decide the severity: `project_profile.py check` prints
    them, `lint_all` raises them as ERROR, and `validate_system` refuses while one is outstanding.
    """
    return [(code, msg, guard) for code, msg, pred, guard in PROJECT_PROFILE_INVARIANTS
            if not pred(cfg)]


# ---------- capture_kinds: the project's own kind registry (CR-AIWS-2026-08-126 C4) ----------
# A DELIBERATELY NARROW reader, not a YAML parser. The shape is fixed and small:
#
#   capture_kinds:
#     namespace: cec
#     kinds:
#       - id: checker_candidate
#         description: ...
#         improvement_scope: project
#         type: finding_candidate
#         suggested_target: tooling
#         consumer: project owner
#
# Writing a general parser here would be the third config parser in this file's history, and the last
# two are exactly what CR-AIWS-2026-08-128 C3 collapsed into one. This one refuses anything it does not
# recognise instead of guessing, so a malformed block yields no kinds rather than half of them.
CAPTURE_KINDS_FIELDS = ("id", "description", "improvement_scope", "type",
                        "suggested_target", "consumer")


def parse_capture_kinds(text: str) -> dict:
    """{'namespace': str, 'kinds': [ {...}, ... ]} or {} when the block is absent/unreadable."""
    lines = text.replace("\r\n", "\n").split("\n")
    start = None
    for i, l in enumerate(lines):
        if l.rstrip() == "capture_kinds:" and not l.startswith((" ", "\t")):
            start = i + 1
            break
    if start is None:
        return {}

    out: dict = {"namespace": "", "kinds": []}
    cur: "dict | None" = None
    in_kinds = False
    for l in lines[start:]:
        if not l.strip() or l.lstrip().startswith("#"):
            continue
        indent = len(l) - len(l.lstrip())
        if indent == 0:                      # the block ended at the next top-level key
            break
        s = l.strip()
        if s.startswith("- "):
            if not in_kinds:
                continue
            cur = {}
            out["kinds"].append(cur)
            s = s[2:].strip()
            if not s:
                continue
        if s == "kinds:":
            in_kinds = True
            cur = None
            continue
        if ":" not in s:
            continue
        k, v = s.split(":", 1)
        k, v = k.strip(), v.strip().strip('"').strip("'")
        if k == "namespace" and not in_kinds:
            out["namespace"] = v
        elif in_kinds and cur is not None and k in CAPTURE_KINDS_FIELDS:
            cur[k] = v
    out["kinds"] = [k for k in out["kinds"] if k.get("id")]
    return out if (out["namespace"] or out["kinds"]) else {}


def read_project_config(ai_work: "Path | str") -> dict:
    """Read .ai-work/project_profile.yml for multi-system scoping (CR-AIWS-2026-06-017).

    Returns {"multi_system": bool, "systems": [...], "synthetic_systems": [...],
             "wiki_single_index": bool, "schema_version": int|None, "_present": {keys seen}}.
    Absent file or multi_system:false → single-system (no scoping). `synthetic_systems`
    (CR-AIWS-2026-07-028) declares which system ids are SYNTHETIC (fixture/test corpora) — default []
    keeps the fixture-namespace guardrail a no-op.

    THE one canonical reader — lookup / lint / build_meta / smoke_test / refresh consume this
    (CR-AIWS-2026-06-061 §8.5) so the config parser cannot drift between tools. CR-AIWS-2026-08-128 C3
    made that true rather than aspirational: three other read paths existed when it was written (a
    regex in this same module, `load_yaml_lite` in build_wiki_page_base, and switch_system_mode's own
    parse), and `wiki_single_index` now comes from here instead of being re-read.

    ABSENT vs UNPARSEABLE (C3): an absent file is legitimate and yields the documented defaults; a file
    that exists but does not parse raises `ProjectProfileUnreadable`. Before this split, a damaged
    profile read as `multi_system: False` — indistinguishable from a healthy single-system project —
    and every guard it feeds went quiet. Pass `strict=False` only where a degraded read is genuinely
    better than a stop (the installer's pre-seed probe is the one such caller).
    """
    p = Path(ai_work) / "project_profile.yml"
    if not p.exists():
        return {"multi_system": False, "systems": [], "synthetic_systems": [],
                "wiki_single_index": False, "schema_version": None,
                "capture_kinds": {}, "_present": set()}
    raw = read_text(p)
    try:
        meta, _ = parse_frontmatter("---\n" + raw + "\n---\n")
    except Exception as e:  # noqa: BLE001
        raise ProjectProfileUnreadable(f"{p}: {e}") from e
    if not isinstance(meta, dict):
        raise ProjectProfileUnreadable(f"{p}: parsed to {type(meta).__name__}, expected a mapping")
    # A profile with none of its keys is not a profile — it is a file that failed to parse into one.
    # Distinguishing this from "absent" is the whole point of C3, so it must not fall through silently.
    if not (set(meta) & set(PROJECT_PROFILE_SCHEMA)):
        raise ProjectProfileUnreadable(
            f"{p}: no recognised key parsed (expected any of {sorted(PROJECT_PROFILE_SCHEMA)})")

    ms = str(meta.get("multi_system", "")).strip().lower() in ("true", "1", "yes")

    def _str_list(key: str) -> list:
        vals = meta.get(key) or []
        if not isinstance(vals, list):
            return []
        return [str(s).strip() for s in vals if str(s).strip()]

    try:
        sv = int(str(meta.get("schema_version", "")).strip())
    except (TypeError, ValueError):
        sv = None

    return {"multi_system": ms,
            "systems": _str_list("systems"),
            "synthetic_systems": _str_list("synthetic_systems"),
            "wiki_single_index": str(meta.get("wiki_single_index", "")).strip().lower()
                                 in ("true", "1", "yes"),
            "schema_version": sv,
            # CR-AIWS-2026-08-126 C4 - parsed from the RAW text, not from `meta`: the frontmatter
            # reader flattens, and this block is nested by nature.
            "capture_kinds": parse_capture_kinds(raw),
            "_present": set(meta)}


def in_system(record: dict, active_system) -> bool:
    """CR-AIWS-2026-06-017 multi-system membership: True if `record` belongs to `active_system`,
    where a common doc (no/blank `system`) is visible under every system. active_system None
    (single-system / --all-systems) → always True. Centralized (CR-AIWS-2026-06-061 §8.5) so the
    query (lookup) and the regression tool (smoke_test) share ONE predicate, not two copies."""
    if active_system is None:
        return True
    sysv = record.get("system", "")
    return (not sysv) or sysv == active_system


def validate_system(system_id, cfg: dict) -> bool:
    """True if `system_id` is acceptable to tag under project config `cfg` (from read_project_config).
    A meta writer validates a --system id before tagging (CR-AIWS-2026-06-061 §8.5 writer obligation):
    in a multi_system project with a non-empty `systems:` list the id MUST be one of them; a
    single-system project (no `multi_system`) accepts any id. Empty/None id → True (the caller handles
    'common' separately).

    FAILS CLOSED since CR-AIWS-2026-08-128 C4. Before it, `multi_system: true` with an empty or missing
    `systems:` list accepted **any** id — measured, with a deliberately bogus one — so a configuration
    that had lost its list looked exactly like a project that never scoped. That is the shape a 2026-07
    parser bug once produced (`CR-AIWS-2026-07-066`): the bug was fixed, the fail-open shape was not.
    The flip was free when made: 0 configurations newly errored (this repo satisfied the invariant; both
    downstream installs had no profile at all).

    Scope discipline: only the two keys that GATE a guard fail closed. `synthetic_systems` narrows and
    `wiki_single_index` selects a layout — making those strict would add noise with no safety gain.
    """
    sid = (str(system_id).strip() if system_id is not None else "")
    if not sid:
        return True
    if cfg.get("multi_system"):
        # Declared multi-system: the list is load-bearing. Missing/empty is an ERROR STATE, not a
        # licence to accept anything — the caller halts and asks rather than proceeding unguarded.
        if not cfg.get("systems"):
            return False
        return sid in cfg["systems"]
    return True


# ---------- Wiki lookup scoring (CR-AIWS-2026-07-001 Q3) ----------
# SINGLE SOURCE for lexical + semantic scoring, consumed by BOTH lookup_wiki_source.py and
# smoke_test_wiki_lookup.py (which previously kept a drifting inline copy — CAP-902-004). Adds the Q3
# boosts: an exact normalized match of the query against the title or a (compound) lookup_key lifts the
# canonical doc above derivatives that merely share tokens (fixes A1 rank-10); plus a small authority
# boost when authority_level / knowledge_class are curated/authoritative.
_WIKI_SEP_RE = re.compile(r"[\\/._\-\s]")


def wiki_fold(s: str) -> str:
    """CR-AIWS-2026-07-007 B1: diacritic-fold + casefold (VI-safe), applied TWO-WAY at
    SCORING time (query AND indexed fields) — no meta rebuild, curated keys untouched.
    ASCII text is unchanged (fold == lower), so EN behavior is identical.
    Đ/đ has no combining decomposition — mapped explicitly."""
    s = s.replace("Đ", "D").replace("đ", "d")
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if not unicodedata.combining(c)).casefold()


def wiki_tokens(s: str) -> list[str]:
    return [wiki_fold(t) for t in _WIKI_SEP_RE.split(s) if t]


def _wiki_norm(s: str) -> str:
    return " ".join(wiki_tokens(s))


# ---------- Query-time document frequency (CR-AIWS-2026-07-007 B3) ----------
# Down-weight tokens present in > DF_CUTOFF of the LOADED record set (whatever scope/index
# combination the caller resolved) — computed query-time over in-memory records, so no
# index.jsonl schema change and no cross-index staleness (sidecar option of CR-007 T3 was
# deliberately not taken: query-time DF is always consistent with the loaded set).
DF_CUTOFF = 0.4


def compute_token_df(records: list) -> dict:
    """{folded_token: fraction of records containing it} over lookup_keys + title tokens."""
    n = len(records)
    if not n:
        return {}
    counts: dict = {}
    for rec in records:
        toks: set = set()
        for k in rec.get("lookup_keys", []) or []:
            toks.update(wiki_tokens(k))
        toks.update(wiki_tokens(rec.get("title", "")))
        for t in toks:
            counts[t] = counts.get(t, 0) + 1
    return {t: c / n for t, c in counts.items()}


# ---------- Query alias expansion (CR-AIWS-2026-07-007 B2) ----------
def load_query_aliases(profiles_dir: "Path") -> list:
    """Read profiles/query_aliases.yml `aliases:` list of '"<phrase> => <target tokens>"' items
    → [(folded_phrase, [folded_target_tokens])]. Reuses the simple block-list parser."""
    out: list = []
    for item in _read_yaml_stopword_list(profiles_dir / "query_aliases.yml", "aliases"):
        if "=>" not in item:
            continue
        phrase, _, targets = item.partition("=>")
        phrase_f = wiki_fold(phrase.strip())
        target_toks = [t for t in wiki_tokens(targets.strip()) if t]
        if phrase_f and target_toks:
            out.append((phrase_f, target_toks))
    return out


def expand_query_tokens(query: str, qtokens: set, aliases: list) -> set:
    """Phrase-level expansion: alias phrase found in the folded query → add its target tokens."""
    if not aliases:
        return qtokens
    qf = wiki_fold(query)
    expanded = set(qtokens)
    for phrase_f, target_toks in aliases:
        if phrase_f in qf:
            expanded.update(target_toks)
    return expanded


_VER_TOK_RE = re.compile(r"v\d+(?:_\d+)*$", re.IGNORECASE)


def _title_core(title: str) -> str:
    """Normalized identity of a doc title. Auto-built metas title = the file PATH
    (e.g. 'wiki_guidelines / core/specs/WIKI_META_INDEX_SPEC.md'); take the LAST path segment
    (the filename), drop its extension + trailing version/status tokens (v0_2 / mvp / draft / a bare
    number), then normalize — so a query that NAMES the doc ('wiki meta index spec') exactly matches
    the canonical spec's identity but not a token-sharing derivative."""
    seg = re.split(r"[\\/]", title.strip())[-1].strip()
    seg = re.sub(r"\.(md|txt|py|yml|yaml|json)$", "", seg, flags=re.IGNORECASE)
    toks = [t.lower() for t in wiki_tokens(seg)]
    while toks and (_VER_TOK_RE.fullmatch(toks[-1]) or toks[-1].isdigit()
                    or toks[-1] in ("mvp", "draft", "final")):
        toks.pop()
    return " ".join(toks)


def _authority_boost(rec: dict) -> int:
    a = (rec.get("authority_level") or "").lower()
    kc = (rec.get("knowledge_class") or "").lower()
    b = 0
    if a in ("authoritative", "curated_reference", "source_of_truth"):
        b += 6
    if kc in ("source_of_truth", "curated"):
        b += 4
    return b


def score_lexical(rec: dict, query: str, qtokens: set) -> int:
    """Lexical score: whole-query substring matching with underscore/hyphen normalization + Q3 boosts.
    CR-007 B1: all comparisons run through wiki_fold (two-way diacritic fold; ASCII unchanged)."""
    score = 0
    q = wiki_fold(query)
    q_norm = q.replace("_", " ").replace("-", " ")
    sid_f = wiki_fold(rec.get("source_id", ""))
    if sid_f == q:
        score += 100
    if q in sid_f:
        score += 20
    if q in wiki_fold(rec.get("title", "")):
        score += 15
    for k in rec.get("lookup_keys", []) or []:
        kl = wiki_fold(k)
        kl_norm = kl.replace("_", " ").replace("-", " ")
        if kl == q or kl_norm == q_norm:
            score += 12
        elif q in kl or kl in q or q_norm in kl_norm or kl_norm in q_norm:
            score += 4
    path_tokens = set(wiki_tokens(rec.get("artifact_locator", "")))
    score += 3 * len(qtokens & path_tokens)
    if q in wiki_fold(rec.get("summary_short", "") or ""):
        score += 2
    if score:
        score += _authority_boost(rec)
    return score


def score_semantic(rec: dict, qtokens: set, query: str = "", df: dict = None) -> int:
    """Semantic score: per-token bag-of-words matching + Q3 exact-name + authority boosts.
    CR-007 B1: comparisons run through wiki_fold (two-way). CR-007 B3: with `df` (query-time
    document frequencies from compute_token_df), tokens present in > DF_CUTOFF of the loaded
    records contribute HALF weight (noise down-weight; coverage bonus unchanged)."""
    if not qtokens:
        return 0
    score = 0
    rec_keys = {wiki_fold(k) for k in (rec.get("lookup_keys", []) or [])}
    key_tokens: set = set()
    for k in rec_keys:
        key_tokens.update(wiki_tokens(k))
    title_tokens = set(wiki_tokens(rec.get("title", "")))
    summary = wiki_fold(rec.get("summary_short", "") or "")
    sid = wiki_fold(rec.get("source_id", ""))
    matched = 0
    for qt in qtokens:
        if len(qt) < 2:
            continue
        common = bool(df) and df.get(qt, 0.0) > DF_CUTOFF
        w = 1 if common else 2  # half-weight for ultra-common tokens (B3)
        if qt in key_tokens:
            score += 4 * w
            matched += 1
        elif any(qt in k or k in qt for k in rec_keys):
            score += 2 * w
            matched += 1
        if qt in title_tokens:
            score += 2 * w + (1 if not common else 0)
        if qt in summary:
            score += 1 * w + (1 if not common else 0)
        if qt in sid:
            score += 1 * w
    if matched >= max(1, len(qtokens) // 2):
        score += matched * 3
    # Q3: "the query names the doc" — an exact match of the query against the title's core identity
    # (filename stem, version-stripped) or a (compound) lookup_key lifts the canonical doc above
    # token-sharing derivatives (A1 fix: 'wiki meta index spec' == WIKI_META_INDEX_SPEC, not the
    # …_Minimal_Spec_Sprint_Merge_Summary derivative).
    if query:
        qn = _wiki_norm(query)
        if qn and qn == _title_core(rec.get("title", "")):
            score += 15
        elif qn and any(qn == _wiki_norm(k) for k in rec_keys):
            score += 10
    if score:
        score += _authority_boost(rec)
    return score


# ---------- Overview pages (CR-AIWS-2026-07-010) ----------
# Shared by build_wiki_overview.py (writer) and lint_wiki.py (checker) — ONE fingerprint algorithm.
OVERVIEW_SOURCE_TYPE = "overview_page"
OVERVIEW_MARKER_PREFIX = "<!-- GENERATED"


def overview_fingerprint(records: list, relations_raw: str = "") -> str:
    """Fingerprint of the overview generator's pre-projection inputs. EXCLUDES overview_page
    records — a page's own index entry must not invalidate its fingerprint (self-reference
    guard, CR-010/COH-9)."""
    import hashlib
    h = hashlib.sha1()
    for k in sorted(
        f"{r.get('source_id','')}|{r.get('updated_at','')}|{r.get('status','')}|{r.get('title','')}"
        for r in records if r.get("source_type") != OVERVIEW_SOURCE_TYPE
    ):
        h.update(k.encode("utf-8"))
        h.update(b"\n")
    h.update(relations_raw.encode("utf-8"))
    return h.hexdigest()[:12]


def overview_body_hash(text: str) -> str:
    """Hash of a generated page EXCLUDING its `<!-- GENERATED…` marker lines — hand-edit
    detection (lint ERROR `overview_hand_edit`, CR-010/GUARD-1)."""
    import hashlib
    body = "\n".join(ln for ln in text.splitlines()
                     if not ln.lstrip().startswith(OVERVIEW_MARKER_PREFIX)).strip()
    return hashlib.sha1(body.encode("utf-8")).hexdigest()[:12]


LOCATOR_PLACEHOLDER = "__PROJECT_ROOT__"

# ---------- Two-kind node model (CR-AIWS-2026-05-023) ----------
# A node_kind=object meta is a logical entity (function / screen / table / …) with NO
# backing source file; its artifact_locator is this sentinel. The sentinel is preserved
# verbatim by the index projection and is never resolved to a filesystem path (INV-9 / DP7).
# node_kind itself is a META-ONLY field — default 'artifact' when omitted (zero migration,
# DP2) — and MUST NOT be projected into the slim index (INV-7). Defined once here so the
# index builder, lint, and tests share one authoritative sentinel.
OBJECT_LOCATOR_SENTINEL = "__OBJECT__"
NODE_KIND_OBJECT = "object"
NODE_KIND_ARTIFACT = "artifact"

# CR-AIWS-2026-06-002: data-flow relationship types whose ## Related Sources edge carries real
# data/contract coupling — a bare (blank-basis-note) edge of these types is the failure mode the
# basis-note convention (Knowledge_Expansion_Link_Spec §4.4) targets. Defined once here so
# build_relations, lint_wiki, and tests share one authoritative set. WARN-only (never error).
# Representation (represents/represented_by) + companion roles are EXCLUDED (not data-flow).
DATA_FLOW_TYPES = frozenset({"upstream_input", "downstream_target", "x:reads", "x:writes"})


def resolve_locator(s: str, project_root: Path) -> Path:
    """Resolve a locator that may start with __PROJECT_ROOT__."""
    if s.startswith(LOCATOR_PLACEHOLDER):
        rel = s[len(LOCATOR_PLACEHOLDER):].lstrip("/\\")
        return project_root / rel
    return Path(s)


def locator_str(value: object) -> str:
    """Normalize a locator/path value READ FROM DATA (frontmatter, index record, JSON config).

    A bare YAML key parses to [], `null` to None, a flow list to a list — none of those are paths.
    Non-string or blank -> "" meaning ABSENT; the caller then classifies (skip / diagnostic /
    missing record). NEVER feed a raw data value to Path()/resolve_locator(): Path("") == Path(".")
    — an existing DIRECTORY — so an exists() check can never reject it.
    Rule 9 of tooling_authoring_conventions (CR-AIWS-2026-07-063/064).
    """
    return value.strip() if isinstance(value, str) else ""


def resolve_data_file(value: object, project_root: Path) -> "Path | None":
    """normalize -> resolve_locator -> is_file(). None when absent / malformed / not a real file.

    Use for EVERY data-derived path whose content will be READ. is_file() (not exists()) is the
    point: exists() is True for directories, which is exactly how the empty-locator crash happens.
    """
    loc = locator_str(value)
    if not loc:
        return None
    p = resolve_locator(loc, project_root)
    return p if p.is_file() else None


def portable_locator(path: "Path | str", project_root: Path) -> str:
    """Replace project_root prefix with __PROJECT_ROOT__ to make path portable.

    The object-meta sentinel (OBJECT_LOCATOR_SENTINEL) is a logical marker, not a path —
    it is returned verbatim (CR-AIWS-2026-05-023 INV-9), so a node_kind=object meta's
    artifact_locator survives index projection unchanged.
    """
    s = str(path)
    if s == OBJECT_LOCATOR_SENTINEL:
        return s
    pr = str(project_root)
    if s.lower().startswith(pr.lower()):
        # Emit a POSIX placeholder so the locator stays portable across OSes:
        # on Windows str(Path) yields backslashes, but the index / maintenance log
        # are shared, cross-platform artifacts. resolve_locator() reads both styles.
        return (LOCATOR_PLACEHOLDER + s[len(pr):]).replace("\\", "/")
    return s


def today() -> str:
    from datetime import date
    return date.today().isoformat()


def now_utc_iso() -> str:
    """Current time as a UTC ISO 8601 timestamp (CR-AIWS-2026-06-024).

    Used for wiki-meta updated_at on a SOURCELESS meta (object/__OBJECT__ or hand-authored)
    where there is no source file to anchor to."""
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


def source_mtime_iso(path: "Path | str") -> str:
    """A source file's mtime as a UTC ISO 8601 timestamp (CR-AIWS-2026-06-024).

    wiki-meta updated_at for a SOURCE-BACKED meta = the source file's mtime, so the value
    reflects when the source content changed (not when build/refresh ran). Sourceless metas
    use now_utc_iso() instead. CAVEAT: git does not preserve mtime — a fresh clone resets it
    to checkout time; the value is captured-then-frozen, so run build/refresh on the editing
    machine before committing."""
    import os
    from datetime import datetime, timezone
    return datetime.fromtimestamp(os.path.getmtime(path), tz=timezone.utc).isoformat()


# ─────────────────────────────────────────────────────────────────────────────
# Lookup-key stopwords (shared by all meta builders) — CR-AIWS-2026-06-043 Change A.
# Universal sets stay BUILT-IN here; PROJECT-specific generics are config-driven via
# `configured_stopwords()` (profiles/project_stopwords.yml + a profile's extra_stopwords),
# so a project adds its own generic terms WITHOUT editing any builder.
# (Upstreamed from the YPO Japanet PoC; see CR-AIWS-2026-06-043.)
# ─────────────────────────────────────────────────────────────────────────────

_HTML_HINT_RE = re.compile(r"<(?:!doctype|html|head|body|div|span|script|style)\b", re.IGNORECASE)
_SCRIPT_STYLE_RE = re.compile(r"<(script|style)\b[^>]*>.*?</\1>", re.IGNORECASE | re.DOTALL)
_TAG_RE = re.compile(r"<[^>]+>")
_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)


def strip_html(text: str) -> str:
    """Reduce HTML to its visible text: drop <script>/<style> blocks, comments, and all
    tags (with attributes). Leaves label/content text — so lookup-key extraction sees domain
    words (incl. Japanese labels), not Tailwind classes / DOM identifiers."""
    if not text:
        return text
    text = _HTML_COMMENT_RE.sub(" ", text)
    text = _SCRIPT_STYLE_RE.sub(" ", text)
    text = _TAG_RE.sub(" ", text)
    return text


STOPWORDS = {
    "the", "and", "for", "with", "this", "that", "from", "into", "when",
    "then", "not", "are", "was", "will", "can", "has", "have", "been",
    "but", "you", "your", "our", "all", "any", "use", "used", "using",
}

PROJECT_DESIGN_STOPWORDS = {
    # ── Vietnamese (romanized, no diacritics) ───────────────────────────────
    "nhi", "cho", "khi", "tri", "nay", "van", "voi", "cua", "hay",
    "trong", "theo", "danh", "hoac", "cung", "duoc", "viec", "khong",
    "nguoi", "cac", "mot", "nhu", "sau", "tren", "thi",
    "moi", "neu", "phai", "nhung", "dieu", "sang", "tiep",
    "nua", "roi", "lai", "luon", "rat", "vay",
    "nen", "luc", "tat", "biet", "den",
    "hien", "nhap", "chon", "xem", "tao", "xoa", "sua", "luu",
    "tim", "them", "muon",
    # added CR-AIWS-2026-06-068 — syllable fragments observed leaking as auto keys:
    "tin", "ang", "tra", "gian", "non", "duy", "qua", "kho", "truy", "nghi",
    # ── English — instruction / qualifier words ──────────────────────────────
    "yes", "must", "before", "per", "next", "applicable",
    "defined", "missing", "explicitly", "stated", "specified",
    "proceed", "above", "below", "item", "items", "section",
    "note", "notes", "rule", "rules",
    "shall", "ensure", "each", "other", "also", "only",
    "based", "such", "both", "given", "via",
    # ── English — UI / structure layout terms ────────────────────────────────
    "screen", "view", "display", "button", "form",
    "table", "column", "row", "list", "detail",
    "input", "text", "data",
    "field", "label", "icon", "link", "header", "footer",
    "panel", "modal", "popup", "tooltip", "placeholder",
    "layout", "format", "style",
    # ── English — generic CRUD / form action verbs ───────────────────────────
    "check", "select", "click", "apply", "navigate",
    "show", "hide", "open", "close", "save", "enter",
    "submit", "cancel", "confirm", "delete", "create", "add",
    "get", "set", "send", "load", "reset",
    # ── English — generic states / conditions ────────────────────────────────
    "error", "required", "optional", "initial", "empty",
    "active", "true", "false", "result", "status",
    "valid", "invalid", "enabled", "disabled", "visible",
    "success", "failed", "pending", "complete",
    # ── English — generic process / flow concepts ────────────────────────────
    "validation", "function", "design", "overview", "spec",
    "flow", "case", "mode", "step", "state", "event",
    "action", "message", "process", "scenario",
    # ── English — generic value / type descriptors ───────────────────────────
    "value", "values", "type", "types", "name", "number",
    "code", "level", "index", "count", "order",
    # ── English — review / checklist meta words ──────────────────────────────
    "pass", "fail", "review", "verify", "criteria",
    "correct", "accurate", "consistent", "compliant",
}

# Common English filler words with no domain signal.
COMMON_ENGLISH_STOPWORDS = {
    "one", "two", "three", "four", "five", "first", "second", "third", "last",
    "more", "most", "many", "much", "some", "few", "less", "least", "than",
    "over", "under", "after", "while", "during", "between", "within", "without",
    "about", "because", "since", "until", "though", "although", "however",
    "therefore", "thus", "hence", "too", "very", "just", "even", "still", "yet",
    "ever", "never", "always", "often", "same", "such", "own", "another", "every",
    "make", "made", "makes", "take", "takes", "took", "taken", "give", "gives",
    "got", "gets", "going", "goes", "come", "comes", "came", "need", "needs",
    "keep", "kept", "put", "say", "said", "see", "seen", "look", "find", "found",
    "work", "works", "way", "ways", "part", "parts", "thing", "things", "kind",
    "lot", "lots", "end", "begin", "start", "starts", "cold", "hot", "heavy",
    "light", "hard", "easy", "fast", "slow", "high", "low", "big", "small",
    "long", "short", "early", "late", "good", "best", "better", "new", "old",
    "full", "path", "cost", "costs", "price", "month", "months", "week", "weeks",
    "year", "years", "day", "days", "night", "time", "times", "today", "now",
    "version", "amount", "total", "main", "basic", "general", "common", "simple",
    "various", "several", "multiple", "single", "here", "there", "back", "down",
}

# HTML/CSS/JS/Tailwind tokens — for HTML mockups, attributes + <script>/<style> are stripped
# first (strip_html), but this catches residual leakage from any source.
WEB_TECH_STOPWORDS = {
    "div", "span", "html", "body", "head", "nav", "main", "section", "article",
    "aside", "ul", "img", "svg", "path", "rect", "circle", "src", "alt",
    "href", "class", "style", "onclick", "onchange", "onsubmit", "id", "role",
    "aria", "viewbox", "xmlns", "stroke", "fill",
    "const", "let", "var", "function", "return", "document", "window", "queryselector",
    "getelementbyid", "addeventlistener", "console", "null", "undefined", "async",
    "await", "import", "export", "default",
    "flex", "grid", "block", "inline", "hidden", "relative", "absolute", "fixed",
    "border", "rounded", "shadow", "ring", "outline", "opacity", "overflow",
    "font", "bold", "medium", "semibold", "italic", "uppercase", "center",
    "left", "right", "justify", "items", "gap", "space", "col", "row", "auto",
    "white", "black", "gray", "slate", "blue", "red", "green", "yellow",
    "indigo", "purple", "pink", "transition", "transform", "scale", "hover",
    "focus", "active", "group", "shrink", "grow", "min", "max", "none", "full",
    "lucide", "colors", "color", "background", "padding", "margin", "width", "height",
}


def _read_yaml_stopword_list(path: "Path", key: str) -> set:
    """Read a simple block list `<key>:` + `  - a` / `  - b` from a YAML file → lowercased set.
    Self-contained (no full YAML dep); tolerant of quotes and a trailing top-level key."""
    out: set = set()
    try:
        if not path.exists():
            return out
        in_list = False
        for line in read_text(path).splitlines():
            stripped = line.strip()
            if not in_list:
                if stripped == f"{key}:" or stripped.startswith(f"{key}:"):
                    in_list = True
                continue
            if stripped.startswith("- "):
                # CR-AIWS-2026-07-042 T1: same inline-comment rule as the block-list parser —
                # `- overview  # too generic` must yield the stopword 'overview', not the whole line.
                raw_w = stripped[2:].strip()
                w = (raw_w if raw_w[:1] in ('"', "'") else _strip_inline_comment(raw_w))
                w = w.strip().strip('"').strip("'")
                if w:
                    out.add(w.lower())
            elif stripped and not (line.startswith(" ") or line.startswith("\t")):
                break  # next top-level key ends the list
    except Exception:  # noqa: BLE001
        return out
    return out


def configured_stopwords(profile_path: "Path") -> set:
    """PROJECT-configurable stopwords (lowercased), self-contained from files:
      • the profile's own `extra_stopwords:` list (per source type), and
      • sibling `project_stopwords.yml` `stopwords:` list (project-wide).
    Adding project generics needs only these config files — never a builder edit."""
    out: set = set()
    out |= _read_yaml_stopword_list(profile_path, "extra_stopwords")
    out |= _read_yaml_stopword_list(profile_path.parent / "project_stopwords.yml", "stopwords")
    return out


def lookup_key_stopwords(profile_path: "Path") -> set:
    """Full prose/doc lookup-key stopword set: ALL universal built-ins ∪ project/profile config.
    Use for prose/doc + HTML-mockup metas (build_wiki_source_meta)."""
    return (STOPWORDS | PROJECT_DESIGN_STOPWORDS | COMMON_ENGLISH_STOPWORDS
            | WEB_TECH_STOPWORDS | configured_stopwords(profile_path))


def code_key_stopwords(profile_path: "Path") -> set:
    """Lookup-key stopword set tuned for SOURCE CODE (java/ts) — CR-AIWS-2026-06-043 Change A.
    Deliberately EXCLUDES PROJECT_DESIGN_STOPWORDS (it holds code-relevant words like event/
    state/type/message/data/status that are valid domain identifiers). Uses common-English
    filler + web-tech + project/profile config, so project generics (member/admin/…) drop from
    code keys WITHOUT discarding domain class/identifier names."""
    return COMMON_ENGLISH_STOPWORDS | WEB_TECH_STOPWORDS | configured_stopwords(profile_path)


# ─────────────────────────────────────────────────────────────────────────────
# Step-2 enrich engine (shared by all language meta builders) — CR-AIWS-2026-06-048.
# A language meta builder = canonical Step-1 (facts → lean meta, AIWS-owned) ⊕ project Step-2
# enrich (project-owned, NOT shipped). apply_enrich consumes the Step-1 FACTS DICT (engine-agnostic
# — identical under regex or tree-sitter) + the project's profile, and returns augmentations the
# builder folds in. Two mechanisms (HYBRID): (1) the profile's declarative `enrich:` block (PRIMARY),
# (2) an optional project code-hook `.ai-work/wiki_sources/enrich/<source_type>.py` (ESCAPE).
# Graceful by contract: no `enrich:` and no hook → empty augmentations; any error → that source is
# skipped (never raises), so Step-1 output is preserved. Deterministic + idempotent.
# ─────────────────────────────────────────────────────────────────────────────

ENRICH_AUG_KEYS = ("extra_lookup_keys", "extra_edges", "extra_concepts", "extra_sections")


def _load_profile_yaml(profile_path: "Path") -> dict:
    """Parse a profile .yml (no --- fence) into a dict, reusing the minimal frontmatter parser.
    Returns {} on any error. NOTE: the parser does NOT process YAML escapes — scalar values are
    taken verbatim (so regex patterns in `enrich:` use SINGLE backslashes, e.g. '\\b[MA]-\\d{2}\\b')."""
    try:
        p = Path(profile_path)
        if not p.is_file():
            return {}
        meta, _ = parse_frontmatter("---\n" + read_text(p).strip("\n") + "\n---\n")
        return meta or {}
    except Exception:  # noqa: BLE001
        return {}


def apply_enrich(facts: dict, profile_path: "Path", src: str) -> dict:
    """Step-2 enrich (CR-AIWS-2026-06-048). Returns augmentations:
    {extra_lookup_keys, extra_edges, extra_concepts, extra_sections} (deterministic, deduped).

    Declarative `enrich:` schema v1 (profile, project-owned):
      enrich:
        lookup_key_patterns:        # each is a Python regex, applied verbatim to raw `src`; every
          - '\\b[MA]-\\d{2}\\b'      #   match (group 0) becomes an extra lookup key
        concept_keywords:           # signal token (annotation / type-name / package) -> concepts
          Scheduled: ["batch job", "scheduled task"]
    Single-token added keys pass the CR-043 code-key stopword filter; multi-word keys are kept.
    Optional code-hook `.ai-work/wiki_sources/enrich/<source_type>.py` exposing
    `def enrich(facts, src, ctx) -> dict` is imported if present (its lists merge in)."""
    aug: dict = {k: [] for k in ENRICH_AUG_KEYS}
    profile = _load_profile_yaml(profile_path)
    enrich = profile.get("enrich") or {}

    if isinstance(enrich, dict):
        # (1) declarative — lookup_key_patterns: regex over raw src -> extra lookup keys
        stop = code_key_stopwords(Path(profile_path))
        patterns = enrich.get("lookup_key_patterns") or []
        if isinstance(patterns, list):
            for pat in patterns:
                try:
                    rx = re.compile(str(pat))
                except re.error:
                    continue
                for m in rx.finditer(src or ""):
                    k = (m.group(0) or "").strip()
                    if not k:
                        continue
                    # CR-043 single-token stopword filter; multi-word kept
                    if (" " in k) or (k.lower() not in stop):
                        if k not in aug["extra_lookup_keys"]:
                            aug["extra_lookup_keys"].append(k)
        # (1) declarative — concept_keywords: signal present in facts -> add its concepts
        ck = enrich.get("concept_keywords") or {}
        if isinstance(ck, dict) and ck:
            annos = [a for t in facts.get("types", []) for a in t.get("annotations", [])]
            names = [t.get("name", "") for t in facts.get("types", [])]
            haystack = " ".join(annos + names + [facts.get("package", "")])
            for signal, concepts in ck.items():
                if str(signal) and str(signal) in haystack:
                    vals = concepts if isinstance(concepts, list) else [concepts]
                    for c in vals:
                        c = str(c).strip()
                        if c and c not in aug["extra_concepts"]:
                            aug["extra_concepts"].append(c)

    # (2) optional project code-hook (ESCAPE) — never break Step-1 on hook trouble
    try:
        source_type = str(profile.get("source_type") or "").strip()
        if source_type:
            hook = Path(profile_path).parent.parent / "enrich" / f"{source_type}.py"
            if hook.is_file():
                import importlib.util
                spec = importlib.util.spec_from_file_location(f"_enrich_{source_type}", hook)
                if spec and spec.loader:
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    fn = getattr(mod, "enrich", None)
                    if callable(fn):
                        res = fn(facts, src, {"profile": profile, "profile_path": str(profile_path)}) or {}
                        if isinstance(res, dict):
                            for key in ENRICH_AUG_KEYS:
                                for v in (res.get(key) or []):
                                    if v not in aug[key]:
                                        aug[key].append(v)
    except Exception:  # noqa: BLE001 — hook error degrades to declarative-only
        pass

    return aug
