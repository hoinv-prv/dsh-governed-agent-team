#!/usr/bin/env python3
"""Create or refresh a Wiki Source Meta artifact from a source + profile.

A source meta is a small, memory-friendly markdown file with YAML frontmatter
describing a source artifact (code file, design doc, table, etc.) so that
Wiki authors can look up + orient before opening the full source.

Curation-state là của HUMAN — builder chỉ được đổi khi flag tương ứng được truyền
tường minh; refresh mặc định carry giá trị cũ (CURATION_PRESERVE_FIELDS trong
_common.py — CR-AIWS-2026-08-058).

Profiles describe HOW to interpret a source type — see
`.ai-work/wiki_sources/profiles/README.md`. Profiles optionally
include: format_signature, summary_extraction, t1_key_extraction,
hints_extraction.

Usage:
  build_wiki_source_meta.py --artifact <path> --source-id <id> \
      --source-type <type> --profile <profile.yml> \
      [--title <title>] [--out <meta.md>] [--mode create|refresh]

Semantic override args (AI-derived content takes priority over profile):
  --summary "..."                AI-derived summary
  --knowledge-targets "a,b,c"   Comma-separated, overrides profile targets
  --lookup-keys "k1,k2"         Pinned T1/T2/T3 keys at top of list
  --hints-depth N               Max heading depth for Source-Specific Hints (default: 2)

Format validation (Phase 1 = WARNING only — never blocks):
  Mismatch prints a warning but always proceeds.
  --skip-format-check           Bypass format validation entirely (requires all 4 semantic args)
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (  # noqa: E402
    dump_frontmatter,
    find_ai_work_root,
    meta_roots,
    parse_frontmatter,
    read_text,
    source_mtime_iso,
    write_text,
    # CR-AIWS-2026-06-043 Change A: stopword sets/helpers now live in _common (moved + extended).
    STOPWORDS,
    PROJECT_DESIGN_STOPWORDS,
    lookup_key_stopwords,
    strip_html,
    _HTML_HINT_RE,
)
from _common import (  # noqa: E402  centralized multi-system primitives (CR-AIWS-2026-06-061 §8.5; was lookup_wiki_source per CR-058) · CR-AIWS-2026-08-128 C3
    ProjectProfileUnreadable, read_project_config as _project_config, validate_system,
)
from _common import carry_curation_state  # noqa: E402  CR-AIWS-2026-08-058: refresh preserves HUMAN curation-state

IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]{2,}")
HEADING_MD_RE = re.compile(r"^#{1,6}\s+(.+)$", re.MULTILINE)
_VERSION_RE = re.compile(r"^v\d+(?:_\d+)*$", re.IGNORECASE)
_FILE_EXT_NOISE = {"md", "txt", "py", "yml", "yaml", "json", "js", "ts", "csv", "xml", "html",
                   # CR-AIWS-2026-08-063 (IR-08b A4-4): image/binary extensions were absent, and
                   # the noise filter never ran on BODY tokens — a bare `png` reached the keys.
                   "png", "jpg", "jpeg", "gif", "svg", "webp", "bmp", "pdf", "docx", "xlsx"}
_BOM = "﻿"


def _load_profile(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"error: profile not found: {path}")
    text = read_text(path)
    meta, _ = parse_frontmatter("---\n" + text + "\n---\n")
    return meta or {}


def _unquote_yaml(s: str) -> str:
    """Strip YAML quotes; process escape sequences for double-quoted strings."""
    s = s.strip()
    if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
        inner = s[1:-1]
        inner = inner.replace('\\\\', '\x00').replace('\\"', '"').replace('\x00', '\\')
        return inner
    if len(s) >= 2 and s[0] == "'" and s[-1] == "'":
        return s[1:-1]
    return s


def _coerce_yaml_scalar(s: str):
    """Coerce a PMP scalar: unquoted true/false -> bool, null/~ -> None, int if integer, else str.
    (CR-AIWS-2026-06-043 Change B added bool/null so emit_scaffold:false in a PMP is honored; int retained.)"""
    low = s.lower()
    if low in ("true", "false"):
        return low == "true"
    if low in ("null", "~"):
        return None
    try:
        return int(s)
    except ValueError:
        return s


def _parse_yaml_nested(lines: list[str], start: int, parent_indent: int) -> tuple[dict, int]:
    """Parse indented YAML lines into a nested dict. Returns (dict, next_line_idx).

    Handles: scalars (int-coerced), flow lists, block lists, nested dicts,
    and double-quoted YAML escape sequences (backslash-backslash to backslash).
    """
    result: dict = {}
    i = start
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            i += 1
            continue
        indent = len(line) - len(line.lstrip())
        if parent_indent >= 0 and indent <= parent_indent:
            break
        if ':' not in stripped:
            i += 1
            continue
        key, _, val_raw = stripped.partition(':')
        key = key.strip()
        val_raw = val_raw.strip()
        if val_raw.startswith('[') and val_raw.endswith(']'):
            inner = val_raw[1:-1].strip()
            result[key] = [_unquote_yaml(p)
                           for p in inner.split(',') if p.strip()] if inner else []
            i += 1
        elif val_raw in ('', '>'):
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j >= len(lines) or (len(lines[j]) - len(lines[j].lstrip())) <= indent:
                result[key] = None
                i = j
                continue
            child_indent = len(lines[j]) - len(lines[j].lstrip())
            if lines[j].lstrip().startswith('- '):
                items: list[str] = []
                i = j
                while i < len(lines):
                    cl = lines[i]
                    if not cl.strip():
                        i += 1
                        continue
                    if (len(cl) - len(cl.lstrip())) < child_indent:
                        break
                    cs = cl.lstrip()
                    if cs.startswith('- '):
                        items.append(_unquote_yaml(cs[2:]))
                        i += 1
                    else:
                        break
                result[key] = items
            else:
                nested, i = _parse_yaml_nested(lines, j, indent)
                result[key] = nested
        else:
            result[key] = _coerce_yaml_scalar(_unquote_yaml(val_raw))
            i += 1
    return result, i


def _load_pmp(profile_path: Path) -> dict:
    """Load the Project Mapping Pattern for this profile, if it exists.

    PMP lives alongside profiles at pmp_<profile_id>.yml.
    Returns {} (empty dict) if no PMP found — callers must handle gracefully.
    """
    try:
        profile = _load_profile(profile_path)
        profile_id = profile.get("profile_id", "")
    except SystemExit:
        return {}
    if not profile_id:
        return {}
    pmp_path = profile_path.parent / f"pmp_{profile_id}.yml"
    if not pmp_path.exists():
        return {}
    text = read_text(pmp_path)
    result, _ = _parse_yaml_nested(text.splitlines(), 0, -1)
    return result


def _is_path_noise(token: str) -> bool:
    """Return True for path/filesystem tokens with no lookup value."""
    t = token.lower()
    if t.endswith(":"):
        return True
    if _VERSION_RE.match(t):
        return True
    if t in _FILE_EXT_NOISE:
        return True
    return False


_MD_LINK_TARGET_RE = re.compile(r"!?\[([^\]]*)\]\([^)]*\)")


def _strip_md_link_targets(text: str) -> str:
    """Drop the parenthesized (url) TARGET of markdown images `![alt](url)` and links `[text](url)`,
    KEEPING the alt/link text (CR-AIWS-2026-07-021 IR-E1). The raw target path/filename tokens
    (assets/images/screenshot/png/…) otherwise leak into lookup keys via IDENT_RE; the alt/link text
    can carry real domain keywords, so it is preserved."""
    return _MD_LINK_TARGET_RE.sub(r"\1", text)


def _extract_lookup_keys(text: str, path_tokens: list[str],
                         source_type: str, max_keys: int = 40,
                         pinned_keys: list[str] | None = None,
                         profile_path: "Path | None" = None) -> list[str]:
    # CR-AIWS-2026-06-043 Change A: config-driven stopwords (universal ∪ project/profile config) +
    # HTML-strip for HTML/ui_mockup sources so domain words are seen, not Tailwind/DOM tokens.
    stopwords = (lookup_key_stopwords(profile_path) if profile_path is not None
                 else STOPWORDS | PROJECT_DESIGN_STOPWORDS)
    if source_type == "ui_mockup" or _HTML_HINT_RE.search(text or ""):
        text = strip_html(text)
    text = _strip_md_link_targets(text)   # CR-021 IR-E1: drop image/link url targets, keep alt/text
    keys: dict[str, int] = {}
    for t in path_tokens:
        # CR-AIWS-2026-08-092 C1 (IR-2026-08-17 G5): the SAME filter as body tokens. Before this,
        # a file-stem token went straight to +5 even when it sat in the project's stopword list —
        # the body branch below filtered it, the path branch did not, so `RD_CreateBooking.md`
        # produced `createbooking` at rank 0 in defiance of `project_stopwords.yml`.
        if len(t) < 3 or t.lower() in stopwords or _is_path_noise(t):
            continue
        keys[t.lower()] = keys.get(t.lower(), 0) + 5
    for m in IDENT_RE.findall(text):
        # CR-AIWS-2026-08-063 (IR-08b A4-1): store body tokens LOWERCASE — aligns with path tokens
        # and pinned_lower, so a capitalized body token equal to a pin can no longer survive the
        # ranked-exclusion and appear twice (closes the E3 case twin). A4-4: body tokens go through
        # the same path-noise filter as path tokens (image/file extensions are not lookup keys).
        k = m.strip().lower()
        if len(k) < 3 or k in stopwords or _is_path_noise(k):
            continue
        keys[k] = keys.get(k, 0) + 1
    # CR-021 IR-E3: dedupe pinned keys order-preserving + case-insensitive (when title==_stem the
    # emitter pins two identical compounds; a capitalized body token equal to a pin must not re-appear).
    pinned: list[str] = []
    pinned_lower: set = set()
    for k in (pinned_keys or []):
        if k and k.lower() not in pinned_lower:
            pinned_lower.add(k.lower())
            pinned.append(k)
    ranked = [k for k, _ in sorted(keys.items(), key=lambda kv: -kv[1])
              if k not in pinned_lower]
    return pinned + ranked[:max(0, max_keys - len(pinned))]


# STOPWORDS + PROJECT_DESIGN_STOPWORDS moved to _common.py (CR-AIWS-2026-06-043 Change A) and
# imported above — single shared home so all builders use one mechanism + projects tune via config.


# CR-AIWS-2026-07-070: a summary that is structurally NOT prose (ordered-list item, directory-tree
# line, tree-drawing glyph). Used to skip such lines in the fallback (T1a) and — crucially — to mark
# the profile branch low-confidence (T2) so the existing CR-054 `needs_completion` gate fires.
_OLIST_RE = re.compile(r"^\d+[.)]\s")
_NON_PROSE_RE = (
    _OLIST_RE,
    re.compile(r"^[\w./-]+/$"),
    re.compile(r"^[├│└]"),
)


def _is_non_prose(s: str) -> bool:
    """True when the extracted summary is structurally a list/tree line rather than prose."""
    s = (s or "").strip()
    return bool(s) and any(p.match(s) for p in _NON_PROSE_RE)


def _summary_from_text(text: str, max_chars: int = 400) -> str:
    """Fallback: return first non-heading, non-special, non-metadata line."""
    _META_LINE_RE = re.compile(
        r"^(Version|Project|Document\s*ID|Function\s*ID|Function\s*name|Date|Author|Status|Phase|Scope|doc[-_]?id|doc_type|document_type|title|version)\s*:",
        re.IGNORECASE,
    )
    # CR-AIWS-2026-07-070 T1a: track fence STATE, not just the fence marker. Skipping only the ```
    # line let the first line INSIDE a code block become the summary ('project-root/' from a directory
    # tree). Third time fence-awareness is fixed in this repo (CR-006 sections, CR-052 headings).
    in_fence, fence_mark = False, ""
    for line in text.splitlines():
        s = line.strip().lstrip(_BOM)
        if in_fence:
            if s.startswith(fence_mark):
                in_fence = False
            continue
        if s.startswith(("```", "~~~")):
            in_fence, fence_mark = True, s[:3]
            continue
        if not s:
            continue
        if s.startswith(("#", "---", "//", "*", "-", "|", ">")):
            continue
        if _OLIST_RE.match(s):        # CR-070 T1a: `1.`/`2)` is a list item — symmetric with `-`/`*`
            continue
        if _META_LINE_RE.match(s):
            continue
        return s[:max_chars - 3] + "..." if len(s) > max_chars else s
    return ""


def _summary_from_table(rows: list[str], max_chars: int = 400) -> str:
    """Extract a meaningful summary from markdown table rows (IR-14).

    Prefers a row whose first cell labels Summary/Overview/Purpose/Description
    (incl. JP 概要/概略); otherwise joins the first data row after the header.
    Skips separator rows (|---|---|)."""
    def cells(row: str) -> list[str]:
        return [c.strip() for c in row.strip().strip("|").split("|")]

    data_rows = [r for r in rows if set(r.replace("|", "").strip()) - set("-: ")]
    label_re = re.compile(r"(summary|overview|purpose|description|概要|概略)", re.IGNORECASE)
    for r in data_rows:
        cs = cells(r)
        if cs and label_re.search(cs[0]):
            val = " ".join(c for c in cs[1:] if c) or " ".join(c for c in cs if c)
            if val.strip():
                return val.strip()
    # fallback: first data row that isn't the header row
    for r in (data_rows[1:] if len(data_rows) > 1 else data_rows):
        cs = [c for c in cells(r) if c]
        if cs:
            return " — ".join(cs)
    return ""


def _extract_section_first_paragraph(text: str, section_name: str,
                                     max_chars: int = 400) -> str:
    """Find section by name and return its full content (prose + bullets), truncated to max_chars.

    If the section body is a table (IR-14), extract a meaningful row instead of
    skipping all table lines, so table-formatted target sections don't yield an
    empty summary that silently degrades to a low-confidence fallback."""
    in_section = False
    collected: list[str] = []
    table_rows: list[str] = []
    # CR-AIWS-2026-07-070 T1b: fence STATE, checked BEFORE both the section-start match and the body
    # collection — a `## Summary` inside a code block must not open a section, and fenced content
    # (template skeletons, ASCII dialogs, API blocks) must never be collected as summary prose.
    in_fence, fence_mark = False, ""
    for line in text.splitlines():
        s = line.strip().lstrip(_BOM)
        if in_fence:
            if s.startswith(fence_mark):
                in_fence = False
            continue
        if s.startswith(("```", "~~~")):
            in_fence, fence_mark = True, s[:3]
            continue
        if re.search(rf"^#{{1,6}}\s+.*{re.escape(section_name)}\s*$", s, re.IGNORECASE):
            in_section = True
            continue
        if in_section:
            if s.startswith("#"):
                break
            if s.startswith("|"):
                table_rows.append(s)
                continue
            if not s or s.startswith(">"):
                continue
            item = s.lstrip("-* ").strip() if s.startswith(("-", "*")) else s
            if item:
                collected.append(item)
    result = " ".join(collected)
    if not result and table_rows:
        result = _summary_from_table(table_rows, max_chars)
    return result[:max_chars - 3] + "..." if len(result) > max_chars else result


def _summary_from_profile(text: str, spec: dict, max_chars: int = 400) -> str:
    """Extract summary using extraction spec (PMP if available, else profile)."""
    extraction = spec.get("summary_extraction") or {}
    target_sections = extraction.get("target_sections") or []
    # Stdlib YAML parser yields strings for scalars; coerce max_chars to int.
    chars = extraction.get("max_chars", max_chars)
    try:
        chars = int(chars)
    except (TypeError, ValueError):
        chars = max_chars
    for section_name in target_sections:
        content = _extract_section_first_paragraph(text, section_name, chars)
        if content:
            return content
    return ""


def _headings(text: str, max_depth: int = 2) -> list[str]:
    """Headings up to max_depth — fence-aware (CR-AIWS-2026-07-052 T1, see _common.md_headings)."""
    from _common import md_headings
    return md_headings(text, max_depth)


def _validate_format_signature(text: str, spec: dict) -> dict | None:
    """Check artifact against format_signature from extraction spec (PMP if available).
    Returns None if OK (or no signature defined), dict with mismatch details otherwise."""
    sig = spec.get("format_signature") or {}
    required = sig.get("required_headings") or []
    if not required:
        return None
    found = [h.lower() for h in HEADING_MD_RE.findall(text)]
    missing = [r for r in required if not any(r.lower() in h for h in found)]
    if not missing:
        return None
    return {
        "missing_headings": missing,
        "required_headings": required,
        "profile_id": spec.get("profile_id", spec.get("pmp_id", "unknown")),
    }


def _extract_t1_keys_from_profile(text: str, spec: dict) -> list[str]:
    """Extract T1 keys using t1_key_extraction from extraction spec (PMP if available)."""
    t1_spec = spec.get("t1_key_extraction") or {}
    pattern = t1_spec.get("pattern")
    patterns = t1_spec.get("patterns") or ([pattern] if pattern else [])
    keys: list[str] = []
    seen: set[str] = set()
    for pat in patterns:
        for m in re.findall(pat, text):
            if m not in seen:
                keys.append(m)
                seen.add(m)
    return keys


def _h1_compound_key(text: str) -> list[str]:
    """Q1 (CR-AIWS-2026-07-001): a discriminative compound T1 key from the artifact's first H1
    heading. The H1 carries the doc identity (id + name + doc-type, e.g.
    'Requirement Definition - F02 Search Room'); kept as ONE multi-word key so it stays
    discriminative (Lookup_Key_Strategy_Spec K-3: compound = discriminative), never split into
    generic single tokens. Section separators (-, —, :) collapse to space. Returns [] when no
    usable H1. This is the auto-build lever that lets a meta be found without hand-curation
    (front-loaded into pinned_keys ahead of frequency-ranked tokens)."""
    for h in _headings(text, max_depth=1):
        s = re.sub(r"[|#>*`]", " ", h)
        s = re.sub(r"\s*[-—–:]\s*", " ", s)
        s = re.sub(r"\s+", " ", s).strip()
        if len(s) >= 4 and any(c.isalnum() for c in s):
            return [s]
    return []


def _clean_heading(h: str) -> str:
    s = re.sub(r"[|#>*`]", " ", h)
    s = re.sub(r"^\s*\d+(\.\d+)*[.)]?\s*", "", s)   # drop a leading section number ("2.1 " / "8) ")
    s = re.sub(r"\s*[-—–:]\s*", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def _doc_compound_keys(text: str, max_keys: int = 5) -> list[str]:
    """Q1b (CR-AIWS-2026-07-004): front-load SEVERAL discriminative compound keys, not just one.
    The self-test checks a meta's FIRST N lookup_keys — Q1 made key #1 discriminative (H1 identity)
    but keys 2-3 were still generic frequency single-tokens ('source'/'AIP'/'Wiki'…) and kept failing.
    This emits the H1 identity PLUS '<doc-identity> <section-heading>' for the first few `## ` sections,
    so the first keys are all discriminative (doc + section) and self-findable. Generic frequency keys
    still follow (for recall) but land past the tested window."""
    h1 = _h1_compound_key(text)
    keys: list[str] = list(h1)
    if h1:
        core = h1[0]
        # keep the core compact if the H1 is very long (use its last ~5 tokens as the doc handle)
        core_toks = core.split()
        handle = " ".join(core_toks[-5:]) if len(core_toks) > 6 else core
        seen = {core.lower()}
        for h, _s, _e in _sections_with_lines(text):
            hc = _clean_heading(h)
            if not hc or len(hc) < 3:
                continue
            k = f"{handle} {hc}"
            if k.lower() not in seen:
                keys.append(k)
                seen.add(k.lower())
            if len(keys) >= max_keys:
                break
    return keys


def _print_mismatch_warning(mismatch: dict) -> None:
    """Print format mismatch as WARNING — always proceeds (Phase 1 behaviour)."""
    pid = mismatch["profile_id"]
    missing = mismatch["missing_headings"]
    print(f"\nWARNING: Format partially matches extraction spec '{pid}'", file=sys.stderr)
    print(f"  Missing required_headings: {missing}", file=sys.stderr)
    print("  Proceeding anyway. Options to resolve:", file=sys.stderr)
    print("    (a) Create a new profile/PMP for this format, then retry", file=sys.stderr)
    print("    (b) Use a different profile: --profile <other.yml>", file=sys.stderr)
    print("    (c) Suppress: --skip-format-check (also requires --lookup-keys)",
          file=sys.stderr)


# ── Related Sources scaffold (CR-AIWS-2026-05-017) ───────────────────────────
RS_ROLES = ("upstream_input", "downstream_navigation", "downstream_target", "triggered_flow",
            "system_foundation", "companion_design", "companion_requirement",
            "output_template", "related")


def _extract_md_section(text: str, heading: str) -> str:
    """Return the '## <heading>' section (heading line + body up to next '## ') or ''."""
    out: list[str] = []
    capturing = False
    for ln in text.splitlines():
        if ln.strip().startswith("## "):
            if capturing:
                break
            capturing = ln.strip()[3:].strip().lower() == heading.lower()
            if capturing:
                out.append(ln)
            continue
        if capturing:
            out.append(ln)
    return "\n".join(out).strip()


def _is_rs_scaffold_only(section: str) -> bool:
    """True if the Related Sources section is still unresolved scaffold (TODO markers, no real ids)."""
    return ("<SRC-id: TODO>" in section) or ("TODO: fill real source_ids" in section)


def _preserved_rs_edges(existing_rs: str, contains_ids: set) -> "list[str]":
    """Non-`contains` resolved RS bullets to carry across a chunked-parent refresh (CR-AIWS-2026-07-021
    IR-B). The chunked parent regenerates its `## Related Sources` as the ordered `contains` list only,
    silently dropping hand-resolved upstream_input/related/downstream_* edges (violates the CR-017
    'refresh preserves a resolved RS section' contract). Keep each `- **<id>** — role: <role> — …`
    bullet whose role != contains and whose id is not already in the freshly-regenerated contains set;
    skip scaffold `<SRC-id: TODO>` and HTML-comment lines; dedupe by target id (keep first)."""
    kept: list[str] = []
    seen: set = set()
    for ln in existing_rs.splitlines():
        s = ln.strip()
        if not s.startswith("- ") or "role:" not in s:
            continue
        if "<SRC-id: TODO>" in s or "role: contains" in s:
            continue
        m = re.match(r"-\s+\*\*([^*]+)\*\*", s)
        tid = m.group(1).strip() if m else ""
        if not tid or tid in contains_ids or tid in seen:
            continue
        seen.add(tid)
        kept.append(ln.rstrip())
    return kept


def _related_sources_scaffold(rs_cfg: dict) -> "list[str]":
    """Lớp 1 (spec-driven role slots) + Lớp 3 (always-on enum + TODO marker)."""
    lines = ["", "## Related Sources",
             "<!-- roles: " + " · ".join(RS_ROLES[:4]) + " ·",
             "     " + " · ".join(RS_ROLES[4:]) + " -->"]
    roles: list[str] = []
    for r in (rs_cfg.get("expected_roles") or []):
        if isinstance(r, str) and r.strip():
            roles.append(r.strip())          # flat list form: "- upstream_input"
        elif isinstance(r, dict) and r.get("role"):
            roles.append(str(r["role"]))     # dict form (real YAML): "- role: upstream_input"
    for role in roles:
        lines.append(f"- **<SRC-id: TODO>** — role: {role} — <why/when to open>")
    # CR-AIWS-2026-08-092 C3: the instruction must name an action the tool RESPECTS. The old text
    # said "delete this section" — and refresh re-scaffolded it on the next run (IR-2026-08-17 G4).
    lines.append("<!-- TODO: fill real source_ids, or set frontmatter `related_sources: none_by_design` "
                 "if this source has no relationships (refresh + lint honour it) -->")
    return lines


# CR-AIWS-2026-08-092 C3 — per-meta curator decision "no relationships, by design".
RS_NONE_BY_DESIGN = "none_by_design"


def rs_none_by_design(frontmatter: dict) -> bool:
    """True when the meta's frontmatter carries `related_sources: none_by_design`."""
    return str((frontmatter or {}).get("related_sources", "")).strip() == RS_NONE_BY_DESIGN


# ── H6 chunked meta for large sources (CR-AIWS-2026-07-002) ──────────────────
_H2_HEADING_RE = re.compile(r"^##\s+(.+?)\s*$")


def _sections_with_lines(text: str) -> "list[tuple[str, int, int]]":
    """[(heading, start_line, end_line)] per level-2 (`## `) section — 1-indexed, inclusive.
    A section runs from its heading line to the line before the next `## ` (or EOF).
    CR-AIWS-2026-07-006 A1 fix: `## ` lines INSIDE fenced code blocks (```/~~~) are NOT section
    boundaries — specs embedding example meta/markdown bodies must not be split at example
    headings (dogfood 2026-07-07: WIKI_META_INDEX_SPEC §14 examples produced garbage children)."""
    lines = text.splitlines()
    heads: list = []
    in_fence = False
    fence_mark = ""
    for i, ln in enumerate(lines):
        stripped = ln.lstrip()
        if in_fence:
            if stripped.startswith(fence_mark):
                in_fence = False
            continue
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = True
            fence_mark = stripped[:3]
            continue
        if (m := _H2_HEADING_RE.match(ln)):
            heads.append((i, m.group(1).strip()))
    out: list = []
    for j, (idx, h) in enumerate(heads):
        end = heads[j + 1][0] if j + 1 < len(heads) else len(lines)
        out.append((h, idx + 1, end))
    return out


def _sec_slug(heading: str, used: set) -> str:
    """CR-AIWS-2026-07-006 A1: heading-keyed child-id slug (id-stability across re-chunks) with
    dedup for duplicate `## ` headings in one doc (later duplicates get -2, -3, …)."""
    from _common import wiki_fold
    base = re.sub(r"-{2,}", "-", re.sub(r"[^a-z0-9]+", "-", wiki_fold(heading))).strip("-")[:40] or "sec"
    slug, n = base, 1
    while slug in used:
        n += 1
        slug = f"{base}-{n}"
    used.add(slug)
    return slug


def _sec_hash(sec_text: str) -> str:
    """Content hash of a section body — carry-over key across heading renames (CR-006 A1)."""
    import hashlib
    return hashlib.sha1(sec_text.strip().encode("utf-8")).hexdigest()[:12]


def _carry_body(body: str, heading: str) -> str:
    """Body-only text under '## <heading>' for chunk-child CARRY (CR-AIWS-2026-07-021 IR-A), with the
    heading line STRIPPED — the emitter re-adds a single heading, so carry must never include one
    (the old code stored `_extract_md_section` output, which INCLUDES the heading, then re-emitted the
    heading → a duplicate `## Summary`/`## Lookup Keys` each refresh, and body loss on the second).
    SELF-HEALING: absorbs consecutive duplicate '## <heading>' lines so a child already corrupted by
    the pre-fix bug (heading duplicated, body still present) RECOVERS its real body on the next refresh
    instead of decaying to boilerplate; stops at the next DIFFERENT '## ' section."""
    want = heading.strip().lower()
    out: list[str] = []
    capturing = False
    in_fence = False
    fence_mark = ""
    for ln in body.splitlines():
        # CR-AIWS-2026-08-061 (IR-08b A1-6): a `## ` inside a ```/~~~ fence is content, not a
        # section boundary — same rule `_sections_with_lines` already applies to the SOURCE.
        st = ln.strip()
        if st.startswith("```") or st.startswith("~~~"):
            mark = st[:3]
            if not in_fence:
                in_fence, fence_mark = True, mark
            elif mark == fence_mark:
                in_fence, fence_mark = False, ""
            if capturing:
                out.append(ln)
            continue
        if in_fence:
            if capturing:
                out.append(ln)
            continue
        if ln.strip().startswith("## "):
            name = ln.strip()[3:].strip().lower()
            if not capturing:
                capturing = (name == want)
                continue                      # never emit the heading line
            if name == want:
                continue                      # absorb a duplicate heading (self-heal), keep capturing
            break                             # next different section ends the body
        if capturing:
            out.append(ln)
    return "\n".join(out).strip()


def _existing_children(out_dir, source_id: str) -> dict:
    """Child metas already on disk for this source, keyed for carry-over (empty when never chunked).

    CR-AIWS-2026-08-061 (IR-08b A1-7): keyed by the COMPOSITE (section_hash, child_id) — two
    sections with identical bodies used to collide on the body-only hash and the last one won, so
    both children received the SAME carried curation (one section's work silently lost). Lookup
    (`_carry_lookup`) tries the composite first, then falls back to hash-only ONLY when no child
    with that id survives (heading rename → new slug, same body: COH-5 rename-carry preserved).
    Each entry also carries the child's non-`part_of` Related Sources bullets (A1-2)."""
    out: dict = {}
    for f in sorted(out_dir.glob(f"{source_id}-SEC-*.md")):
        try:
            fm, body = parse_frontmatter(read_text(f))
        except Exception:  # noqa: BLE001
            continue
        h = fm.get("section_hash", "")
        cid = str(fm.get("source_id", "") or f.stem)
        summary_txt = _carry_body(body, "Summary")     # CR-021 IR-A: heading-stripped, self-healing
        keys_txt = _carry_body(body, "Lookup Keys")
        rs_txt = _carry_body(body, "Related Sources")
        # A1-2: hand-resolved child edges (anything but the regenerated `part_of` bullet)
        rs_extra = [ln.rstrip() for ln in rs_txt.splitlines()
                    if ln.strip().startswith("- ") and "role: part_of" not in ln]
        rec = {"fm": fm, "summary": summary_txt, "keys": keys_txt, "rs_extra": rs_extra,
               "source_id": cid, "path": f}
        out[(h, cid)] = rec
        out.setdefault(("hash-only", h), rec)   # first-seen fallback for renamed headings
    return out


def _carry_lookup(prior: dict, h: str, cid: str) -> "dict | None":
    """Composite-first carry lookup (CR-AIWS-2026-08-061 A1-7): exact (hash, id) → else hash-only
    fallback, but ONLY if that id does not exist under another hash (i.e. a genuine rename, not a
    same-body sibling)."""
    rec = prior.get((h, cid))
    if rec is not None:
        return rec
    if any(k[1] == cid for k in prior if k[0] != "hash-only"):
        return None    # this id lives on with different content → changed section, no carry
    return prior.get(("hash-only", h))


def _emit_chunked(*, text: str, meta: dict, source_id: str, title: str, source_type: str,
                  profile_path, summary: str, lookup_keys: list, out_path,
                  threshold_lines: int, threshold_kb: int, mode: str = "create",
                  emit_partial: bool = False, summary_explicit: bool = False) -> bool:
    """H6: keep the large source file intact but split its META: write a PARENT meta + one SECTION
    meta per `## ` section. A section meta carries the SAME `artifact_locator` plus `section_heading`
    + `section_lines` ("start-end") so runtime Reads just that line range instead of the whole file.
    Parent↔section linked via `## Related Sources` (contains / part_of — parent list is in DOCUMENT
    ORDER, the ordered-`contains` contract of CR-AIWS-2026-07-006 A3). Returns True iff it chunked.

    CR-AIWS-2026-07-006 A1 (re-chunk on refresh): child ids are heading-slug-keyed (stable across
    reorders; slug-dedup for duplicate headings); on refresh, existing children are matched by
    `section_hash` (content hash) — unchanged content KEEPS its completed Summary/Lookup Keys even
    when the heading was renamed; changed/new sections are re-emitted mechanically (and flagged
    `needs_completion: [summary]` when --emit-partial); orphan children are deleted. A previously
    chunked source stays chunked on refresh even if it shrank below threshold.

    CR-AIWS-2026-08-061 (IR-08b A1 family, closes A1-8): refresh does not throw away LLM/HUMAN
    work — every completed block is carried by default (child Summary/Keys/non-part_of RS; parent
    Summary/Keys; composite carry-key; fence-aware carry; line-ref regen); regenerate only when the
    content changed or an explicit flag (--summary) says so. Orphan cleanup deletes only metas that
    carry the positive child marker (A1-1)."""
    n_lines = text.count("\n") + 1
    size_kb = len(text.encode("utf-8")) / 1024
    out_dir = out_path.parent
    prior = _existing_children(out_dir, source_id) if mode == "refresh" else {}
    if n_lines <= threshold_lines and size_kb <= threshold_kb and not prior:
        return False
    sections = _sections_with_lines(text)
    if len(sections) < 2:
        return False  # nothing meaningful to chunk into
    text_lines = text.splitlines()
    section_ids: list = []
    kept = renewed = 0
    emitted_paths: set = set()
    used_slugs: set = set()
    for heading, start, end in sections:
        sid = f"{source_id}-SEC-{_sec_slug(heading, used_slugs)}"
        section_ids.append((sid, heading))
        sec_text = "\n".join(text_lines[start - 1:end])
        # Hash EXCLUDES the heading line itself → a heading RENAME with unchanged body still
        # hash-matches and keeps its completed Summary/Lookup Keys (COH-5 / CR-006 A1).
        h = _sec_hash("\n".join(text_lines[start:end]))
        carry = _carry_lookup(prior, h, sid) if prior else None   # CR-061 A1-7 composite key
        # CR-006 A2 (deterministic part): pin THREE discriminative compounds so the child's
        # first-3 keys are all self-findable (self-test gate) — full-title+heading, doc-stem+heading,
        # bare heading; frequency-extracted tokens only rank AFTER these (MP1 guard).
        _stem = re.sub(r"\.(md|txt)$", "", re.split(r"[\\/]", title.strip())[-1], flags=re.IGNORECASE)
        _stem = _stem.replace("_", " ").strip()
        sec_keys = _extract_lookup_keys(sec_text, [], source_type,
                                        pinned_keys=[f"{title} {heading}",
                                                     f"{_stem} {heading}", heading],
                                        profile_path=profile_path)[:20]
        sf = {
            "artifact_type": "wiki_source_meta", "source_id": sid,
            "title": f"{title} — {heading}", "source_type": source_type,
            "artifact_locator": meta["artifact_locator"], "profile_id": meta.get("profile_id", ""),
            "status": "active", "updated_at": meta.get("updated_at", ""),
            "section_heading": heading, "section_lines": f"{start}-{end}",
            "section_hash": h,
        }
        if carry:
            kept += 1
        else:
            renewed += 1
            if emit_partial:
                sf["needs_completion"] = ["summary"]  # A2: H1 completion pass fills a semantic summary
        if meta.get("system"):
            sf["system"] = meta["system"]
        # CR-AIWS-2026-07-005: a chunk child is the retrieval target (lookup returns the narrow
        # section, not the whole doc), so it must be self-describing about source fidelity — inherit
        # the parent's representation-status / caution / provenance so a direct hit on a section meta
        # does not silently drop the low-fidelity (partial / OCR / diagram) warning. Additive AND
        # signal-only: copy a field only when it carries a real signal — skip the no-review defaults
        # ("unknown" status / the boilerplate caution) so a clean/unreviewed source's children stay
        # lean (no false or noise fidelity fields).
        _fidelity_noise = {"", "unknown", "Representation quality has not been reviewed."}
        for _f in ("source_representation_status", "source_representation_caution",
                   "representation_type", "conversion_method", "conversion_limitations",
                   "original_source_locator", "conversion_date", "converted_by"):
            _v = meta.get(_f)
            # skip the no-review defaults for string fields; non-str (e.g. list conversion_limitations)
            # is a real signal whenever truthy.
            if _v and (not isinstance(_v, str) or _v not in _fidelity_noise):
                sf[_f] = _v
        # A1 carry-over: unchanged content (hash match) keeps its completed Summary + Lookup Keys
        # verbatim (LLM work never silently reverts to boilerplate); changed/new → mechanical emit.
        if carry and carry["summary"].strip():
            summary_block = carry["summary"].rstrip()
            # CR-AIWS-2026-08-061 (IR-08b A1-5): a carried MECHANICAL summary keeps the OLD
            # "lines X-Y" while frontmatter section_lines moves — refresh the range in place.
            # Curated prose (no mechanical pattern) is left untouched.
            summary_block = re.sub(rf"(Section '{re.escape(heading)}' \(lines )\d+-\d+(\))",
                                   rf"\g<1>{start}-{end}\g<2>", summary_block, count=1)
        else:
            summary_block = (f"Section '{heading}' (lines {start}-{end}) of {title}. Read ONLY this "
                             f"line range in the source (`{meta['artifact_locator']}`); do not open "
                             f"the whole file.")
        if carry and carry["keys"].strip():
            keys_block = carry["keys"].rstrip().splitlines()
        else:
            keys_block = [f"- {k}" for k in sec_keys]
        sb = [f"# Wiki Source Meta — {title} — {heading}", "",
              "## Summary", summary_block, "",
              "## Knowledge Targets", "- section", "",
              "## Lookup Keys"]
        sb += keys_block
        sb += ["", "## Related Sources",
               f"- **{source_id}** — role: part_of — Section of the parent document `{title}`; "
               f"open the parent for whole-document context. [asserted]"]
        # CR-AIWS-2026-08-061 (IR-08b A1-2): carry the child's hand-resolved non-part_of edges —
        # symmetric to the parent's `_preserved_rs_edges` (CR-021 IR-B); refresh must not throw
        # away resolved child edges just because the part_of bullet is regenerated.
        if carry and carry.get("rs_extra"):
            sb += carry["rs_extra"]
        sb.append("")
        cpath = out_dir / f"{sid}.md"
        emitted_paths.add(cpath.name)
        write_text(cpath, dump_frontmatter(sf) + "\n".join(sb))
    # A1: orphan children (section removed / merged away) are deleted — no dangling -SEC- metas.
    removed = 0
    for f in sorted(out_dir.glob(f"{source_id}-SEC-*.md")):
        if f.name in emitted_paths:
            continue
        # CR-AIWS-2026-08-061 (IR-08b A1-1, OQ-3): POSITIVE-MARKER gate — only a real child of THIS
        # source is deleted (frontmatter section_hash present AND artifact_locator == parent's). An
        # independent meta whose id merely shares the `<source_id>-SEC-` prefix is never touched.
        try:
            _ofm, _ = parse_frontmatter(read_text(f))
        except Exception:  # noqa: BLE001
            continue
        if not _ofm.get("section_hash") or \
                str(_ofm.get("artifact_locator", "")) != str(meta.get("artifact_locator", "")):
            print(f"  orphan-cleanup: SKIP {f.name} — not a child of {source_id} (no positive marker); "
                  "left untouched (CR-AIWS-2026-08-061 A1-1)", file=sys.stderr)
            continue
        f.unlink()
        removed += 1
    # CR-AIWS-2026-08-061 (IR-08b A1-3 / A1-4): on refresh, the PARENT keeps its existing Summary
    # prose (unless --summary was passed explicitly — `summary_explicit`) and its existing Lookup
    # Keys block (build-arg keys only seed a parent that has none). Same rule as the children:
    # refresh must not throw away LLM/HUMAN work — regenerate only on explicit flag / empty block.
    _old_parent_summary = _old_parent_keys = ""
    if mode == "refresh" and out_path.exists():
        try:
            _, _pbody_old = parse_frontmatter(read_text(out_path))
            _old_parent_summary = _carry_body(_pbody_old, "Summary")
            _old_parent_keys = _carry_body(_pbody_old, "Lookup Keys")
        except Exception:  # noqa: BLE001
            pass
    _mech_tail = (f"LARGE source ({n_lines} lines) — split into {len(sections)} section metas; use a "
                  f"section's section_lines to Read just the relevant range.")
    if _old_parent_summary.strip() and not summary_explicit:
        # keep the curated head, refresh only the mechanical LARGE-source tail (line count may move)
        _head = re.sub(r"LARGE source \(\d+ lines\) — split into \d+ section metas;.*$", "",
                       _old_parent_summary, flags=re.S).strip()
        summary_line = (_head.rstrip(".") + ". " if _head else "") + _mech_tail
    else:
        summary_line = (summary.rstrip(".") + ". " if summary else "") + _mech_tail
    pbody = [f"# Wiki Source Meta — {title}", "",
             "## Summary", summary_line, "",
             "## Knowledge Targets", "- document", "- toc", "",
             "## Lookup Keys"]
    if _old_parent_keys.strip():
        pbody += [ln for ln in _old_parent_keys.splitlines() if ln.strip()]
    else:
        pbody += [f"- {k}" for k in (lookup_keys or [title])[:15]]
    pbody += ["", "## Related Sources"]
    # A3 ordered-`contains` contract: children listed in DOCUMENT ORDER — sequence is derivable
    # one-hop from the parent (no sibling next/prev edges needed).
    for sid, heading in section_ids:
        pbody.append(f"- **{sid}** — role: contains — Section '{heading}' of this document. [asserted]")
    # CR-AIWS-2026-07-021 (IR-B): on refresh, preserve hand-resolved non-`contains` RS edges the
    # parent already carries (the `contains` list is regenerated fresh above; a removed section
    # correctly loses its edge). Idempotent: re-extracting after a fixed refresh yields the same set.
    if mode == "refresh" and out_path.exists():
        _contains_ids = {sid for sid, _h in section_ids}
        for _edge in _preserved_rs_edges(
                _extract_md_section(read_text(out_path), "Related Sources"), _contains_ids):
            pbody.append(_edge)
    pbody.append("")
    write_text(out_path, dump_frontmatter(meta) + "\n".join(pbody))
    print(f"source meta CHUNKED ({mode}): {out_path} (parent) + {len(sections)} section metas "
          f"({n_lines} lines / {size_kb:.0f}KB; thresholds {threshold_lines} lines / {threshold_kb}KB) "
          f"— diff: {kept} kept (hash match), {renewed} new/changed, {removed} removed")
    return True


def main() -> int:
    p = argparse.ArgumentParser(description="Build Wiki Source Meta")
    p.add_argument("--artifact", required=True, help="Source artifact path")
    p.add_argument("--source-id", required=True, help="Unique source id")
    p.add_argument("--source-type", required=True,
                   help="Category, e.g. basic_design|requirement_spec")
    p.add_argument("--profile", required=True, help="Source Interpretation Profile file")
    p.add_argument("--title", help="Human title (default: filename)")
    p.add_argument("--out", help="Output meta path (default: wiki_sources/meta/<source-id>.md)")
    p.add_argument("--mode", choices=["create", "refresh"], default="create")
    p.add_argument("--authority-level", default="unknown")
    p.add_argument("--freshness-status", default="unknown")
    p.add_argument("--source-representation-status", default="unknown")
    p.add_argument("--source-representation-caution",
                   default="Representation quality has not been reviewed.")
    p.add_argument("--source-representation-quality-issue", action="store_true")
    p.add_argument("--knowledge-value", default="unknown")
    p.add_argument("--intended-ai-use", default="unknown")
    p.add_argument("--promotion-status", default="draft")
    p.add_argument("--maintenance-status", default="needs_review")
    p.add_argument("--original-source-locator", default="")
    p.add_argument("--representation-locator", default="")
    p.add_argument("--representation-type", default="markdown")
    p.add_argument("--conversion-method", default="unknown")
    p.add_argument("--conversion-date", default="")
    p.add_argument("--converted-by", default="")
    p.add_argument("--conversion-limitations", default="",
                   help="Comma-separated conversion limitations")
    p.add_argument("--representation-scope", default="unknown")
    # Semantic override args (AI-derived content)
    p.add_argument("--summary", default="",
                   help="Override auto-extracted summary with AI-derived semantic summary")
    p.add_argument("--knowledge-targets", default="",
                   help="Comma-separated list to override profile knowledge_targets")
    p.add_argument("--lookup-keys", default="",
                   help="Comma-separated T1/T2/T3 keys pinned to top of lookup key list")
    p.add_argument("--hints-depth", type=int, default=None,
                   help="Max heading depth for Source-Specific Hints (default: PMP value or 2)")
    p.add_argument("--skip-format-check", action="store_true",
                   help="Bypass format validation. Requires --summary, --knowledge-targets, "
                        "and --lookup-keys.")
    p.add_argument("--no-related-sources", action="store_true",
                   help="Do not emit the ## Related Sources scaffold (opt-out for artifacts "
                        "with no relationships).")
    # H6 (CR-AIWS-2026-07-002): chunked meta for large sources.
    p.add_argument("--chunk-threshold-lines", type=int, default=None,
                   help="H6: chunk a source into parent + per-section metas when it exceeds this many "
                        "lines (default 1000; profile `chunk_threshold_lines` overrides).")
    p.add_argument("--chunk-threshold-kb", type=int, default=None,
                   help="H6: chunk when the source exceeds this size in KB (default 50; profile "
                        "`chunk_threshold_kb` overrides).")
    p.add_argument("--no-chunk", action="store_true",
                   help="H6: never chunk — always write a single meta regardless of size.")
    # H1 (CR-AIWS-2026-07-002): completion layer — emit a PARTIAL meta for an LLM completion pass.
    p.add_argument("--emit-partial", action="store_true",
                   help="H1: mark the meta `needs_completion: [summary, lookup_keys, related_sources]` "
                        "so a downstream LLM step improves those fields; lint blocks a partial from "
                        "being treated as a finished (index-ready) meta until completion clears it.")
    # H5 (CR-AIWS-2026-07-002): diagram handling.
    p.add_argument("--diagrams-rerepresented", action="store_true",
                   help="H5: the caller already re-represented the source's diagrams as text/mermaid — "
                        "do NOT auto-mark the representation partial for images.")
    # CR-AIWS-2026-06-058: set the meta's multi-system `system:` at create time (mirror the lookup gate).
    p.add_argument("--system", default=None, metavar="ID",
                   help="Multi-system (CR-017): tag this meta to system <id> (validated against "
                        "project_profile.systems). In a multi_system project pass this or --common.")
    p.add_argument("--common", action="store_true",
                   help="Multi-system: mark this meta system-agnostic/common (emit NO system key). "
                        "Mutually exclusive with --system.")
    ns = p.parse_args()

    artifact = Path(ns.artifact).resolve()
    if not artifact.exists():
        print(f"error: artifact not found: {artifact}", file=sys.stderr)
        return 2

    profile_path = Path(ns.profile).resolve()
    profile = _load_profile(profile_path)
    pmp = _load_pmp(profile_path)
    extraction_spec = pmp if pmp else profile

    ai_work = find_ai_work_root(artifact) / ".ai-work"
    out_path = Path(ns.out).resolve() if ns.out else (
        ai_work / "wiki_sources" / "meta" / f"{ns.source_id}.md")
    # CR-AIWS-2026-08-033 C1: a refresh without an explicit --out must write where the meta
    # actually LIVES. Resolve the existing meta for this source_id across every namespace root
    # (meta_roots(): project meta/ first, then aiws_meta/ — CR-049 discipline) instead of
    # defaulting blindly to wiki_sources/meta/, which used to fork a duplicate chunk set into
    # the wrong namespace (37 stray files — AIP-EXEC-1029). Explicit --out always wins; sort key
    # is POSIX-relative so the pick is OS-stable (sorted(Path) flips between Windows/POSIX).
    if not ns.out and ns.mode == "refresh":
        for _mroot in meta_roots(ai_work):
            _hits = sorted(
                (p for p in _mroot.rglob(f"{ns.source_id}.md")
                 if not p.name.endswith(".refresh.md")),
                key=lambda p: p.relative_to(_mroot).as_posix(),
            )
            if _hits:
                out_path = _hits[0]
                break

    if ns.mode == "create" and out_path.exists():
        print(f"error: {out_path} already exists (use --mode refresh)", file=sys.stderr)
        return 2

    # ── Multi-system `system:` resolution (CR-AIWS-2026-06-058) ───────────────
    # Mirror lookup_wiki_source's gate: in a multi_system project require --system or --common.
    # Single-system → flags ignored unless --system explicitly given. Refresh preserves an
    # existing system: when no flag is passed (never silently drops it).
    if ns.system and ns.common:
        print("error: --system and --common are mutually exclusive", file=sys.stderr)
        return 2
    try:
        _cfg = _project_config(ai_work)
    except ProjectProfileUnreadable as e:                # CR-AIWS-2026-08-128 C3
        print(f"error: .ai-work/project_profile.yml exists but could not be parsed: {e}",
              file=sys.stderr)
        return 2
    _existing_system = None
    if ns.mode == "refresh" and out_path.exists():
        _existing_system = (parse_frontmatter(read_text(out_path))[0] or {}).get("system") or None
    system_val = None
    if ns.system:
        system_val = ns.system.strip()
        if not validate_system(system_val, _cfg):           # CR-AIWS-2026-06-061 §8.5: centralized writer validation
            print(f"error: --system {system_val!r} is not in this project's systems "
                  f"{_cfg['systems']}.", file=sys.stderr)
            return 2
    elif ns.common:
        system_val = None                                   # explicit common (no key)
    elif ns.mode == "refresh" and _existing_system:
        system_val = _existing_system                       # preserve on refresh
    elif _cfg["multi_system"]:
        print("error: this is a multi_system project — pass --system <id> (the meta's system) "
              "or --common (system-agnostic). No silent default.", file=sys.stderr)
        return 2
    # single-system + no flag → system_val stays None (byte-identical to pre-CR behavior)

    text = read_text(artifact)
    title = ns.title or artifact.stem

    # ── Format validation ────────────────────────────────────────────────────
    if ns.skip_format_check:
        missing_args = [a for a, v in [
            ("--summary", ns.summary.strip()),
            ("--knowledge-targets", ns.knowledge_targets.strip()),
            ("--lookup-keys", ns.lookup_keys.strip()),
        ] if not v and v != ""]
        if missing_args:
            print(f"error: --skip-format-check requires: {', '.join(missing_args)}",
                  file=sys.stderr)
            return 2
    else:
        mismatch = _validate_format_signature(text, extraction_spec)
        if mismatch:
            _print_mismatch_warning(mismatch)  # always proceeds (Phase 1)

    # ── Summary (priority: arg > extraction_spec > fallback) ─────────────────
    summary_low_conf = False  # CR-054: the builder could not determine a real summary
    if ns.summary.strip():
        summary = ns.summary.strip()
    else:
        summary = _summary_from_profile(text, extraction_spec)
        # CR-AIWS-2026-07-070 T2: the profile branch never raised a confidence signal — any non-empty
        # result was trusted, so a list/tree line extracted from a targeted section sailed past the
        # CR-054 `needs_completion` gate silently. Reuse that gate instead of adding a second one.
        if summary and _is_non_prose(summary):
            summary_low_conf = True
            print("WARNING: profile/PMP section yielded a non-prose summary (list item / tree line). "
                  "Pass --summary for a quality meta.", file=sys.stderr)
        if not summary:
            summary = _summary_from_text(text)
            if summary:
                summary_low_conf = True
                print("WARNING: summary came from low-confidence fallback (no profile/PMP "
                      "section matched). Pass --summary for a quality meta.", file=sys.stderr)
        if not summary:
            summary_low_conf = True
            summary = "(no semantic summary — re-run with --summary \"...\" for quality meta)"
            print("WARNING: could not extract summary. Use --summary for quality meta.",
                  file=sys.stderr)

    # ── Knowledge targets (priority: arg > profile) ──────────────────────────
    if ns.knowledge_targets.strip():
        knowledge_targets = [k.strip() for k in ns.knowledge_targets.split(",") if k.strip()]
    else:
        knowledge_targets = profile.get("knowledge_targets") or []
    if not knowledge_targets:
        knowledge_targets = [ns.source_type]

    # ── Lookup keys: H1 compound T1 (Q1) + T1 patterns (PMP/profile) + pinned arg + auto-extract
    # Q1 (CR-AIWS-2026-07-001): front-load the H1-derived compound key so an auto-built meta is
    # discoverable without hand-curation, then PMP-pattern T1, then CLI --lookup-keys. Order-preserving
    # dedup (case-insensitive) so a repeated key is pinned once.
    spec_t1_keys = _extract_t1_keys_from_profile(text, extraction_spec)
    _cli_keys = [k.strip() for k in ns.lookup_keys.split(",") if k.strip()]
    pinned_keys: list[str] = []
    _seen_pin: set[str] = set()
    for _k in _doc_compound_keys(text) + spec_t1_keys + _cli_keys:
        if _k and _k.lower() not in _seen_pin:
            pinned_keys.append(_k)
            _seen_pin.add(_k.lower())
    # Q1b (CR-AIWS-2026-07-004): the self-test checks the FIRST N keys, so a lone generic single-token
    # key (e.g. 'wiki'/'source' from a profile T1 tier) must never occupy a tested slot ahead of a
    # discriminative compound. Stable-partition multi-word keys ahead of single-word ones — order within
    # each group preserved, so the H1 identity key stays at position 1 and single tokens sink past the
    # tested window (they still serve recall, just lower).
    pinned_keys = ([k for k in pinned_keys if len(k.split()) > 1]
                   + [k for k in pinned_keys if len(k.split()) == 1])
    path_tokens = [
        t for t in re.split(r"[\\/._\-]", artifact.stem) if t and len(t) > 2
    ]
    lookup_keys = _extract_lookup_keys(text, path_tokens, ns.source_type,
                                       pinned_keys=pinned_keys, profile_path=profile_path)

    # ── Headings for Source-Specific Hints ───────────────────────────────────
    # CLI --hints-depth wins; fall back to PMP value, then default 2
    if ns.hints_depth is not None:
        hints_depth_val = ns.hints_depth
    else:
        hints_depth_val = extraction_spec.get("hints_extraction", {}).get("max_depth", 2)
    hints_depth = max(1, min(hints_depth_val, 6))
    headings = _headings(text, max_depth=hints_depth)

    try:
        _rel = artifact.relative_to(ai_work.parent).as_posix()
    except ValueError:
        print("WARNING: artifact is outside project root; storing absolute path in artifact_locator",
              file=sys.stderr)
        _rel = str(artifact)
    if "\\" in _rel:
        print(f"WARNING: relative path still contains backslashes after normalization: {_rel}",
              file=sys.stderr)
    representation_locator = ns.representation_locator or _rel
    original_source_locator = ns.original_source_locator or ""
    conversion_limitations = [
        x.strip() for x in ns.conversion_limitations.split(",") if x.strip()
    ]

    # H5 (CR-AIWS-2026-07-002): detect diagrams/images the text representation cannot convey. If any
    # are present and not yet re-represented, record the count so the representation is not silently
    # treated as complete (status set to `partial` after the meta dict below).
    _diagrams = (len(re.findall(r"!\[[^\]]*\]\([^)]+\)", text))
                 + len(re.findall(r"<img\b", text, re.IGNORECASE)))
    _diagram_partial = bool(_diagrams) and not ns.diagrams_rerepresented
    if _diagram_partial:
        conversion_limitations.append(f"diagrams_present:{_diagrams}")
        conversion_limitations.append("diagrams_rerepresented:0")

    meta: dict = {
        "artifact_type": "wiki_source_meta",
        "source_id": ns.source_id,
        "title": title,
        "source_type": ns.source_type,
        "artifact_locator": representation_locator,
        "profile_id": profile.get("profile_id", profile_path.stem),
        "status": "active",
        "updated_at": source_mtime_iso(artifact),  # CR-AIWS-2026-06-024: source-backed = source file mtime
        "authority_level": ns.authority_level,
        "freshness_status": ns.freshness_status,
        "promotion_status": ns.promotion_status,
        "source_representation_status": ns.source_representation_status,
        "source_representation_caution": ns.source_representation_caution,
        # CR-AIWS-2026-07-066 T2 (A2-1/A2-2/A2-3): these three were parsed into `ns` and then
        # dropped on the floor — so lint's meta_representation_issue / meta_maintenance_status
        # guards could never fire on built metas, and --representation-scope was discarded while
        # meta_sri_field kept asking for it. Defaults are unchanged; only the plumbing is.
        "source_representation_quality_issue": ns.source_representation_quality_issue,
        "maintenance_status": ns.maintenance_status,
        "representation_scope": ns.representation_scope,
        "knowledge_value": ns.knowledge_value,
        "intended_ai_use": ns.intended_ai_use,
        "representation_type": ns.representation_type,
        "conversion_method": ns.conversion_method,
        "conversion_limitations": conversion_limitations,
    }
    if system_val:                                          # CR-058: conditional — absent = common
        meta["system"] = system_val
    # CR-AIWS-2026-08-058 — refresh preserves HUMAN curation-state: mọi curation field còn ở
    # builder-default sẽ CARRY giá trị của meta cũ (mirror luật preserve-`system` ở trên); builder
    # chỉ được đổi khi flag tương ứng truyền tường minh.
    if ns.mode == "refresh" and out_path.exists():
        try:
            _existing_fm, _ = parse_frontmatter(read_text(out_path))
        except Exception:
            _existing_fm = {}
        _carried = carry_curation_state(meta, _existing_fm)
        if _carried:
            print(f"  refresh: curation-state preserved ({', '.join(_carried)}) — CR-AIWS-2026-08-058")
    # H5: mark representation partial when unre-represented diagrams remain (CR-D7: partial → wiki_only).
    if _diagram_partial and meta.get("source_representation_status") in ("", "unknown", "complete", None):
        meta["source_representation_status"] = "partial"
        if str(meta.get("source_representation_caution", "")).startswith("Representation quality has not"):
            meta["source_representation_caution"] = (
                f"{_diagrams} diagram(s) present but not re-represented as text/mermaid — open the "
                "source or request re-representation; do not claim evidence beyond the text.")
    # H1: partial meta flagged for a downstream LLM completion pass.
    if ns.emit_partial:
        meta["needs_completion"] = ["summary", "lookup_keys", "related_sources"]
    if original_source_locator:
        meta["original_source_locator"] = original_source_locator
    if ns.conversion_date:
        meta["conversion_date"] = ns.conversion_date
    if ns.converted_by:
        meta["converted_by"] = ns.converted_by

    body_lines: list[str] = [
        f"# Wiki Source Meta — {title}",
        "",
        "## Summary",
        summary,
        "",
        "## Knowledge Targets",
    ]
    for kt in knowledge_targets:
        body_lines.append(f"- {kt}")
    body_lines += ["", "## Lookup Keys"]
    for k in lookup_keys:
        body_lines.append(f"- {k}")
    if headings:
        body_lines += ["", "## Source-Specific Hints"]
        for h in headings:
            body_lines.append(f"- heading: {h}")
    # ## Profile Mapping body section dropped (CR-AIWS-2026-05-024): it mirrored the
    # frontmatter `profile_id` verbatim (zero AI-orientation value). The frontmatter
    # profile_id stays the single source of truth.

    # ── Related Sources scaffold (CR-017): spec-driven roles + always-on TODO ──
    # Refresh preserves a human/AI-RESOLVED section; only (re)writes the scaffold otherwise.
    # CR-AIWS-2026-08-092 C3: a meta whose curator recorded `related_sources: none_by_design`
    # gets NO scaffold on refresh — absence is the curated state. `_existing_fm` was read above
    # (CR-058 carry) and now carries the marker forward via CURATION_PRESERVE_FIELDS.
    _rs_none = (ns.mode == "refresh" and rs_none_by_design(meta))
    if not ns.no_related_sources and not _rs_none:
        rs_cfg = extraction_spec.get("related_sources") or {}
        if rs_cfg.get("emit_scaffold", True):
            existing_rs = ""
            if ns.mode == "refresh" and out_path.exists():
                existing_rs = _extract_md_section(read_text(out_path), "Related Sources")
            if existing_rs and not _is_rs_scaffold_only(existing_rs):
                body_lines += ["", existing_rs.rstrip()]   # keep resolved section as-is
            else:
                body_lines += _related_sources_scaffold(rs_cfg)
    body_lines.append("")

    # H6 (CR-AIWS-2026-07-002): if the source is large, write a parent + per-section metas instead
    # of one meta (keeps the file intact; section metas carry section_lines for range-Read).
    # CR-AIWS-2026-07-006 A1: re-chunk now runs in REFRESH mode too (hash carry-over + orphan
    # cleanup inside _emit_chunked); a profile may opt in/out via `chunk_enabled` (A4 —
    # per-profile dogfood knob, DP-912-1 nhịp 1). CLI --no-chunk still wins.
    _thr_lines = ns.chunk_threshold_lines if ns.chunk_threshold_lines is not None else \
        int(extraction_spec.get("chunk_threshold_lines", 1000) or 1000)
    _thr_kb = ns.chunk_threshold_kb if ns.chunk_threshold_kb is not None else \
        int(extraction_spec.get("chunk_threshold_kb", 50) or 50)
    _profile_chunk = extraction_spec.get("chunk_enabled")
    _chunk_allowed = (not ns.no_chunk) and (_profile_chunk is not False)
    if _chunk_allowed and _emit_chunked(
            text=text, meta=meta, source_id=ns.source_id, title=title, source_type=ns.source_type,
            profile_path=profile_path, summary=summary, lookup_keys=lookup_keys, out_path=out_path,
            threshold_lines=_thr_lines, threshold_kb=_thr_kb, mode=ns.mode,
            emit_partial=ns.emit_partial, summary_explicit=bool(ns.summary.strip())):
        return 0

    # CR-AIWS-2026-07-054 (R4-01): arm the completion gate on the DEFAULT (single-meta) CREATE path.
    # The H1 layer was unreachable — nothing passed --emit-partial — so a default `--mode create`
    # shipped a raw scaffold with `lint errors=0`. Flag ONLY what the builder could not determine,
    # so a fully-specified build (--summary + resolved enums + resolved related) sets an EMPTY list
    # and the gate (lint `if _nc:`) leaves it green. Placed after body assembly so the scaffold
    # check reads the ACTUAL emitted body; chunked emission returned above, so this is the leaf path.
    # CR-054 fires the completion gate on a genuinely UNUSABLE meta: one whose SUMMARY is a
    # low-confidence fallback (no real content). That is exactly the R4-01 case — a raw scaffold
    # ALWAYS trips the low-confidence summary — so flagging summary makes it non-green, which is the
    # whole complaint. SCOPE = create only (a refresh preserves an accepted meta; unknown enums are a
    # legal steady state, CR-038). The CR text proposed flagging two more things; both were dropped
    # after dogfood (declared deviations in the Apply Outcome):
    #   - `unknown` enum fields: the completion step (register-batch B7) never fills enums and
    #     `unknown` is a legal enum member (the demo itself rejected "reject unknown enums" in §3) →
    #     flagging them is an UNCLEARABLE gate.
    #   - unresolved `<SRC-id: TODO>` scaffold: already covered by the WARNING
    #     `meta_related_sources_todo` (lint_wiki.py); escalating it to a blocking ERROR would
    #     double-signal AND break the build→lint→resolve ordering that build-then-lint flows use.
    if ns.mode != "refresh":
        needs = list(meta.get("needs_completion") or [])   # keep --emit-partial's list if it ran
        if summary_low_conf and "summary" not in needs:
            needs.append("summary")
        if needs:
            meta["needs_completion"] = needs
    else:
        needs = list(meta.get("needs_completion") or [])

    write_text(out_path, dump_frontmatter(meta) + "\n".join(body_lines))
    print(f"source meta {'refreshed' if ns.mode == 'refresh' else 'created'}: {out_path}")
    if needs:
        print(f"needs_completion: {needs} — run the completion step (fill a real summary / resolve "
              f"the Related Sources scaffold) before index/done; lint ERRORs (meta_needs_completion) "
              f"until cleared.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
