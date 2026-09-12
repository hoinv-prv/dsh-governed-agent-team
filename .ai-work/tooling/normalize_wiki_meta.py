#!/usr/bin/env python3
"""Batch-normalize legacy Wiki Source Meta fields to current lint-conformant form.

Fixes the two deterministic, scriptable issues flagged by lint_wiki on the
project source metas (.ai-work/wiki_sources/meta/**/*.md):

  meta_absolute_locator
      artifact_locator stored as an absolute path (e.g. c:\\...\\product\\x.md)
      -> rewritten to a bare project-relative POSIX path (product/x.md), which is
         exactly what build_wiki_source_meta.py emits and what the lint orphan-check
         resolves. Touches the frontmatter line AND any "- artifact_locator:" line in
         the body (Profile Mapping). Left untouched: the __OBJECT__ sentinel, the
         __PROJECT_ROOT__ placeholder, URLs (contain "://"), and absolute paths that
         resolve OUTSIDE the project root (reported, not changed).

  meta_authority
      authority_level holding a value outside the valid enum
      -> remapped via --authority-map (default: project_canonical=curated_reference).
         Values already in the enum are never touched.

  ## Profile Mapping  (opt-in: --drop-profile-mapping)
      The deprecated body section dropped from the meta builder by CR-AIWS-2026-05-024.
      It mirrored frontmatter `profile_id` verbatim and is the only place legacy metas
      still carry an absolute `profile_path`. Frontmatter `profile_id` stays the single
      source of truth, so the whole section (heading -> next ##/# heading or EOF, incl.
      its trailing blank line) is removed. Off by default; combine with --no-locators
      --no-authority to run the section drop alone.

Scriptable parts ONLY. Missing optional WTA/SRI fields (meta_sri_field /
meta_wta_field info) need real curated values and are deliberately NOT touched.

Dry-run by default; pass --apply to write. After --apply, pass --reproject to
rebuild index.jsonl (build_wiki_source_index.py --scope project) so the index
matches the normalized metas.

Stdlib only. Edits are line-level (regex), so field order, comments and the rest
of each file are preserved byte-for-byte aside from the changed values.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import find_ai_work_root, meta_roots, read_text, write_text  # noqa: E402

VALID_AUTHORITY = {
    "source_of_truth", "curated_reference", "working_reference",
    "history_reference", "candidate", "unknown",
}
DEFAULT_AUTHORITY_MAP = {"project_canonical": "curated_reference"}

OBJECT_SENTINEL = "__OBJECT__"
PLACEHOLDER = "__PROJECT_ROOT__"

# Matches "artifact_locator: <value>" and "- artifact_locator: <value>".
# The optional "-" prefix lets it catch the body Profile Mapping line too.
# `original_source_locator` / `representation_locator` do NOT match (key is anchored).
LOC_RE = re.compile(r"^(\s*-?\s*)artifact_locator(\s*:\s*)(\S.*?)\s*$")
AUTH_RE = re.compile(r"^(\s*)authority_level(\s*:\s*)(\S.*?)\s*$")

# Deprecated body section dropped from the meta builder by CR-AIWS-2026-05-024:
# `## Profile Mapping` mirrored frontmatter `profile_id` verbatim (zero AI-orientation
# value) and is the only place legacy metas still carry an absolute `profile_path`.
# Frontmatter `profile_id` stays the single source of truth, so the whole section is
# safe to remove. Heading match is exact (level-2, title "Profile Mapping").
PROFILE_MAPPING_HEADING_RE = re.compile(r"^##\s+Profile Mapping\s*$")
# A section boundary = the next level-1 or level-2 heading (## or #), NOT a level-3+
# sub-heading (### …), which would belong to the section being removed.
SECTION_BOUNDARY_RE = re.compile(r"^#{1,2}\s+\S")


def _is_absolute(v: str) -> bool:
    return (len(v) >= 2 and v[1] == ":") or v.startswith("/") or v.startswith("\\")


def normalize_locator(value: str, project_root_posix: str):
    """Return (new_value, note) or None if no change is needed.

    note is one of: "abs->rel", "backslash->slash", or "OUTSIDE" (left unchanged).
    """
    raw = value.strip().strip('"').strip("'")
    if not raw or raw == OBJECT_SENTINEL or raw.startswith(PLACEHOLDER) or "://" in raw:
        return None
    if not _is_absolute(raw):
        if "\\" in raw:                       # relative but with backslashes
            return raw.replace("\\", "/"), "backslash->slash"
        return None
    norm = raw.replace("\\", "/")
    pr = project_root_posix.rstrip("/")
    if norm.lower().startswith(pr.lower() + "/"):
        return norm[len(pr) + 1:], "abs->rel"
    return raw, "OUTSIDE"                       # absolute, outside project root


def drop_profile_mapping(text: str):
    """Remove the deprecated `## Profile Mapping` section (heading through the line
    before the next ##/# heading, or EOF). Returns (new_text, dropped: bool).

    A single trailing blank line that belonged to the dropped section is consumed
    with it, so adjacent sections keep their one-blank-line separation byte-for-byte.
    """
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    i, n = 0, len(lines)
    dropped = False
    while i < n:
        if PROFILE_MAPPING_HEADING_RE.match(lines[i].rstrip("\n")):
            dropped = True
            i += 1  # skip the heading
            while i < n and not SECTION_BOUNDARY_RE.match(lines[i].rstrip("\n")):
                i += 1  # skip the section body (incl. its trailing blank line)
            continue
        out.append(lines[i])
        i += 1
    return "".join(out), dropped


def process_file(path: Path, project_root_posix: str, authority_map: dict[str, str],
                 do_locators: bool, drop_pm: bool = False):
    """Return (new_text_or_None, changes:list[str], warnings:list[str])."""
    original_text = read_text(path)
    text = original_text
    if drop_pm:
        text, was_dropped = drop_profile_mapping(text)
        # `changes` is populated below; record the section drop up front.
    else:
        was_dropped = False
    lines = text.splitlines(keepends=True)
    changes: list[str] = []
    warnings: list[str] = []
    out: list[str] = []
    if was_dropped:
        changes.append("dropped deprecated section: ## Profile Mapping (CR-AIWS-2026-05-024)")

    for line in lines:
        nl = "\n" if line.endswith("\n") else ""
        body = line[:-1] if nl else line

        m = LOC_RE.match(body) if do_locators else None
        if m:
            res = normalize_locator(m.group(3), project_root_posix)
            if res is not None:
                new_val, note = res
                if note == "OUTSIDE":
                    warnings.append(f"artifact_locator absolute & outside project root, left as-is: {new_val}")
                elif new_val != m.group(3).strip().strip('"').strip("'"):
                    body = f"{m.group(1)}artifact_locator{m.group(2)}{new_val}"
                    changes.append(f"artifact_locator [{note}]: {m.group(3)} -> {new_val}")
            out.append(body + nl)
            continue

        a = AUTH_RE.match(body)
        if a:
            cur = a.group(3).strip().strip('"').strip("'")
            if cur not in VALID_AUTHORITY and cur in authority_map:
                new_val = authority_map[cur]
                body = f"{a.group(1)}authority_level{a.group(2)}{new_val}"
                changes.append(f"authority_level: {cur} -> {new_val}")
            elif cur not in VALID_AUTHORITY:
                warnings.append(f"authority_level '{cur}' invalid but no mapping provided (left as-is)")
            out.append(body + nl)
            continue

        out.append(line)

    new_text = "".join(out)
    return (new_text if new_text != original_text else None), changes, warnings


def parse_authority_map(pairs: list[str]) -> dict[str, str]:
    mapping = dict(DEFAULT_AUTHORITY_MAP)
    for p in pairs or []:
        if "=" not in p:
            raise SystemExit(f"error: --authority-map expects old=new, got: {p}")
        old, new = p.split("=", 1)
        old, new = old.strip(), new.strip()
        if new not in VALID_AUTHORITY:
            raise SystemExit(f"error: target authority '{new}' not in valid enum {sorted(VALID_AUTHORITY)}")
        mapping[old] = new
    return mapping


def main() -> int:
    ap = argparse.ArgumentParser(description="Batch-normalize legacy wiki source metas (locator + authority).")
    ap.add_argument("--apply", action="store_true", help="Write changes (default: dry-run).")
    ap.add_argument("--meta-dir", help="Override meta directory (default: .ai-work/wiki_sources/meta).")
    ap.add_argument("--no-locators", action="store_true", help="Skip artifact_locator normalization.")
    ap.add_argument("--no-authority", action="store_true", help="Skip authority_level remapping.")
    ap.add_argument("--authority-map", action="append", default=[],
                    help="Extra/override mapping old=new (repeatable). Default: project_canonical=curated_reference.")
    ap.add_argument("--drop-profile-mapping", action="store_true",
                    help="Remove the deprecated `## Profile Mapping` body section (CR-AIWS-2026-05-024); "
                         "frontmatter profile_id stays the single source of truth. Off by default.")
    ap.add_argument("--reproject", action="store_true",
                    help="After --apply, rebuild index.jsonl (build_wiki_source_index.py --scope project).")
    ns = ap.parse_args()

    project_root = find_ai_work_root(Path(__file__).resolve().parent)
    project_root_posix = project_root.as_posix()
    # CR-AIWS-2026-07-049: default scans EVERY meta namespace via the shared helper (project meta/
    # + shipped aiws_meta/) — an explicit --meta-dir still wins (single-dir batch runs).
    if ns.meta_dir:
        roots = [Path(ns.meta_dir)]
    else:
        roots = meta_roots(project_root / ".ai-work")
    roots = [d for d in roots if d.is_dir()]
    if not roots:
        raise SystemExit("error: no meta dir found")

    authority_map = parse_authority_map(ns.authority_map)
    if ns.no_authority:
        authority_map = {}
    do_locators = not ns.no_locators

    files = sorted(f for root in roots for f in root.rglob("*.md"))
    changed_files = 0
    total_changes = 0
    total_warnings = 0

    print(f"mode: {'APPLY' if ns.apply else 'DRY-RUN'}   meta-dir: {meta_dir}")
    print(f"locators: {'off' if ns.no_locators else 'on'}   authority-map: {authority_map or 'off'}   "
          f"drop-profile-mapping: {'on' if ns.drop_profile_mapping else 'off'}")
    print("-" * 70)

    for path in files:
        new_text, changes, warnings = process_file(
            path, project_root_posix, authority_map, do_locators, ns.drop_profile_mapping)
        if changes or warnings:
            rel = path.relative_to(project_root).as_posix()
            print(rel)
            for c in changes:
                print(f"    CHANGE  {c}")
            for w in warnings:
                print(f"    WARN    {w}")
            total_changes += len(changes)
            total_warnings += len(warnings)
        if new_text is not None and changes:
            changed_files += 1
            if ns.apply:
                write_text(path, new_text)

    print("-" * 70)
    print(f"files scanned: {len(files)}   files to change: {changed_files}   "
          f"changes: {total_changes}   warnings: {total_warnings}")
    if not ns.apply and changed_files:
        print("dry-run only — re-run with --apply to write.")

    if ns.apply and ns.reproject:
        idx_tool = project_root / ".ai-work" / "tooling" / "build_wiki_source_index.py"
        print("-" * 70)
        print(f"reprojecting index: {idx_tool} --scope project")
        r = subprocess.run([sys.executable, str(idx_tool), "--scope", "project"],
                           cwd=str(project_root))
        if r.returncode != 0:
            print(f"WARNING: index rebuild exited {r.returncode}", file=sys.stderr)
            return r.returncode
    elif not ns.reproject and ns.apply and not ns.no_locators and changed_files:
        print("note: artifact_locator values changed — run "
              "`py .ai-work/tooling/build_wiki_source_index.py --scope project` "
              "(or re-run with --reproject) to refresh index.jsonl.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
