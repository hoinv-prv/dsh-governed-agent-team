#!/usr/bin/env python3
"""Refresh a Wiki Source Meta against the current source artifact.

Compares the freshly-projected meta with the existing meta, writes a new
draft under `wiki_sources/_drafts/` (mirroring the meta-relative subpath —
CR-AIWS-2026-07-032 T2; drafts NEVER sit in meta/ where index/lint/relations/
detector would ingest them) OR updates in-place (`--apply`, which also clears
the pending draft), and reports whether material change was detected
(lookup_keys, summary, size).

Scope guards (CR-AIWS-2026-08-062): a CHUNKED PARENT is refused with a pointer to
`build_wiki_source_meta --mode refresh` — this tool refreshes ONE meta in place, while a chunked
set (parent + `-SEC-` children) must be re-chunked as a set by the builder; running it here made
the builder emit children into the TEMP out-dir and left the real children stale (IR-08b A5-1).
NOTE (CAP-P003-01): a RELATIVE `artifact_locator` resolves against the CURRENT WORKING DIRECTORY
(`resolve_locator` returns Path(s) verbatim for non-__PROJECT_ROOT__ locators) — run this tool
from the project root of the meta, or the artifact reads as unreachable.
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (  # noqa: E402
    append_maintenance_log,
    extract_sections,
    find_ai_work_root,
    locator_str,
    parse_frontmatter,
    portable_locator,
    read_text,
    resolve_data_file,
    write_text,
)

# Reuse build_wiki_source_meta.py by importing it as a module
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Body sections intentionally NOT preserved on refresh:
#  - Profile Mapping: dropped by builder (CR-AIWS-2026-05-024); mirrors frontmatter profile_id.
#  - Artifact Reference: mirrors frontmatter artifact_locator.
_BODY_PRESERVE_DENY = {"profile mapping", "artifact reference"}

_FALLBACK_SUMMARY_RE = re.compile(r"^(phase|scope|version|status)\s*:", re.IGNORECASE)


def draft_path_for(meta_path: Path) -> Path:
    """CR-AIWS-2026-07-032 T2a: pending refresh drafts live under `wiki_sources/_drafts/`,
    MIRRORING the meta-relative subpath (meta/ has subdirs — a flat _drafts/ would collide
    basenames and mis-match apply-cleanup).

    CR-AIWS-2026-08-079 fixed the anchor. It used to look for an ancestor named EXACTLY `meta`,
    which no meta under `wiki_sources/aiws_meta/` has — all 189 of them fell to the sibling
    fallback and got a `_drafts/` INSIDE the curated namespace, the one thing T2a exists to avoid.
    Anchoring on `wiki_sources` is correct for both `meta/` and `aiws_meta/`, and is the same
    anchor `backup_path_for` uses: one rule, two consumers, instead of two rules one of which
    is wrong.

    Fallback for a meta outside a `wiki_sources` tree: a `_drafts/` sibling next to it.
    """
    name = meta_path.stem + ".refresh.md"
    # Anchor 1 (UNCHANGED, CR-07-032): a dir named exactly `meta` -> mirror the subpath BELOW it.
    # Kept verbatim because CR-079 is scoped to the aiws_meta/ miss; moving where meta/ drafts land
    # would relocate every existing draft and is a behaviour change nobody authorised. Three tests
    # pin this layout (test_refresh_draft_hygiene B5, test_wiki_regression x2) — they are pinning a
    # real contract, not an accident.
    meta_root = next((p for p in meta_path.parents if p.name == "meta"), None)
    if meta_root is not None:
        return meta_root.parent / "_drafts" / meta_path.parent.relative_to(meta_root) / name
    # Anchor 2 (CR-AIWS-2026-08-079): any OTHER namespace under wiki_sources — aiws_meta/ and any
    # future sibling. Mirror INCLUDING the namespace segment, so meta/<g>/X and aiws_meta/<g>/X
    # cannot collide on one basename in _drafts/.
    root = next((p for p in meta_path.parents if p.name == "wiki_sources"), None)
    if root is not None:
        return root / "_drafts" / meta_path.parent.relative_to(root) / name
    # Anchor 3: outside any wiki_sources tree -> sibling _drafts/ (unchanged fallback).
    return meta_path.parent / "_drafts" / name


def backup_path_for(meta_path: Path) -> Path:
    """CR-AIWS-2026-08-075 C1: `--apply` backups live under `wiki_sources/_backups/`, MIRRORING the
    meta-relative subpath — not beside the meta, where they pollute the curated namespace and get
    projected as stray metas by tools that glob `*.md*`.

    DELIBERATELY NOT reusing `draft_path_for`'s anchor (DP-075-A = a). That one looks for an ancestor
    named EXACTLY `meta`, so `.ai-work/wiki_sources/aiws_meta/...` finds none, falls through to the
    sibling branch, and lands the directory INSIDE the namespace — reproducing the very disease this
    change removes, for all 189 aiws_meta metas. Anchoring on `wiki_sources` instead is correct for
    both `meta/` and `aiws_meta/`. `draft_path_for` keeps its behaviour: it belongs to
    CR-AIWS-2026-07-032 and this CR is not authorised to change it (the bug is logged separately).

    Fallback for a meta outside a `wiki_sources` tree: a `_backups/` sibling next to it.
    Name keeps the historical `<meta-name>.bak` form, so a backup stays greppable by meta name.
    """
    root = next((p for p in meta_path.parents if p.name == "wiki_sources"), None)
    name = meta_path.name + ".bak"
    if root is None:
        return meta_path.parent / "_backups" / name
    return root / "_backups" / meta_path.parent.relative_to(root) / name


def _looks_curated_summary(s: str) -> bool:
    """Heuristic: curated summary (worth preserving) vs a mechanical fallback
    line like 'Phase: X'. Curated = long-ish or multi-sentence, not a metadata line."""
    s = (s or "").strip()
    if not s or s.startswith("(no semantic summary"):
        return False
    if _FALLBACK_SUMMARY_RE.match(s):
        return False
    return len(s) >= 60 or s.count(".") >= 2


def _project(artifact: Path, source_id: str, source_type: str, profile: Path,
             title: str | None, summary: str | None = None,
             seed_text: str | None = None) -> str:
    """Run build_wiki_source_meta.py in a subprocess to avoid import coupling.

    `summary`, when provided, is passed through as --summary so a curated summary
    is preserved instead of being regenerated mechanically (Fix 1). `seed_text`,
    when provided, is written to the temp out-file so the builder's refresh-mode
    preserve logic sees the existing meta — keeping a RESOLVED ## Related Sources
    section instead of overwriting it with a fresh scaffold (Fix R1). Builder
    WARNINGs on stderr are surfaced, not swallowed (Fix 4 — guardrail visibility)."""
    import subprocess
    from tempfile import NamedTemporaryFile

    tmp = NamedTemporaryFile(suffix=".md", delete=False)
    tmp.close()
    if seed_text:
        Path(tmp.name).write_text(seed_text, encoding="utf-8")
    cmd = [
        sys.executable,
        str(Path(__file__).resolve().parent / "build_wiki_source_meta.py"),
        "--artifact", str(artifact),
        "--source-id", source_id,
        "--source-type", source_type,
        "--profile", str(profile),
        "--out", tmp.name,
        "--mode", "refresh",
    ]
    if title:
        cmd += ["--title", title]
    if summary:
        cmd += ["--summary", summary]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"build_wiki_source_meta failed: {r.stderr}")
    if r.stderr.strip():
        for line in r.stderr.splitlines():
            if line.strip():
                print(f"  [builder] {line.strip()}", file=sys.stderr)
    content = Path(tmp.name).read_text(encoding="utf-8")
    Path(tmp.name).unlink(missing_ok=True)
    return content



def _append_maintenance_log(meta_path: Path, action: str, source_id: str,
                            target_artifact: Path, old_locator: str,
                            new_locator: str, change_summary: str,
                            impact_level: str, review_decision: str,
                            rollback_hint: str) -> None:
    """Append a minimal WSM maintenance log entry.

    This log is traceability support only. It is not promotion approval.
    """
    from datetime import datetime, timezone

    ai_work = None
    for parent in [meta_path.parent, *meta_path.parents]:
        if parent.name == ".ai-work":
            ai_work = parent
            break
    if ai_work is None:
        # Expected path: .ai-work/wiki_sources/meta/<file>
        for parent in meta_path.parents:
            candidate = parent / ".ai-work"
            if candidate.exists():
                ai_work = candidate
                break
    if ai_work is None:
        ai_work = meta_path.parent.parent if meta_path.parent.name == "meta" else meta_path.parent

    log_path = ai_work / "wiki_sources" / "maintenance_log.jsonl"
    # Store portable __PROJECT_ROOT__-relative locators (not absolute paths).
    project_root = ai_work.parent
    entry = {
        "log_id": f"WSMLOG-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{source_id}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "maintenance_model_version": "wsm_v1",
        "action": action,
        "source_id": source_id,
        "target_artifact": portable_locator(target_artifact, project_root),
        "old_locator": portable_locator(old_locator, project_root) if old_locator else "",
        "new_locator": portable_locator(new_locator, project_root) if new_locator else "",
        "change_summary": change_summary,
        "reason": "Wiki Source Meta refresh",
        "impact_level": impact_level,
        "review_decision": review_decision,
        "applied_by": "tool:refresh_wiki_source_meta.py",
        "rollback_hint": rollback_hint,
        "runtime_boundary": "maintenance log records apply/draft; it is not promotion approval",
    }
    append_maintenance_log(log_path, entry)


def _parse_bullets(section_text: str) -> list[str]:
    """Parse a '- key' bullet list section into a list of keys (order-preserving)."""
    out: list[str] = []
    for line in (section_text or "").splitlines():
        s = line.strip()
        if s.startswith("- "):
            v = s[2:].strip()
            if v:
                out.append(v)
    return out


def _dedupe_stable(keys: list[str]) -> list[str]:
    """Case-insensitive de-dup, preserving first-seen casing and order."""
    seen: set[str] = set()
    out: list[str] = []
    for k in keys:
        lk = k.lower()
        if lk not in seen:
            seen.add(lk)
            out.append(k)
    return out


def _render_bullets(keys: list[str]) -> str:
    return "\n".join(f"- {k}" for k in keys)


_SECTION_HDR_RE = re.compile(r"^#{1,6}\s+(.+?)\s*$")


def _replace_section(body: str, heading: str, new_content: str) -> str:
    """Replace the body of the named section (keeping its heading) with new_content.
    Line-based; no-op if the heading is not found."""
    lines = body.splitlines()
    out: list[str] = []
    i, n = 0, len(lines)
    while i < n:
        m = _SECTION_HDR_RE.match(lines[i])
        if m and m.group(1).strip() == heading:
            out.append(lines[i])                 # keep heading
            out.extend(new_content.splitlines())  # new section body
            i += 1
            while i < n and not _SECTION_HDR_RE.match(lines[i]):
                i += 1                            # drop old section body
            if i < n:
                out.append("")                    # single blank line before next heading
        else:
            out.append(lines[i])
            i += 1
    return "\n".join(out) + ("\n" if body.endswith("\n") else "")


# Fields the refresh legitimately rewrites every run — comparing them would make every refresh
# report "material change" and drown the real signal.
VOLATILE_FIELDS = {
    "updated_at", "maintenance_status", "review_required", "review_status", "status",
}


def _signature(text: str) -> dict:
    """CR-AIWS-2026-07-052 T3: the signature now includes the FRONTMATTER FIELD SET.

    Before, it tracked only 4 things (summary / lookup_keys / knowledge_targets / artifact_locator).
    That is why a refresh could silently DROP 7 populated fields (authority_level, freshness_status,
    knowledge_value, intended_ai_use, source_representation_status, conversion_method,
    conversion_limitations) and report the whole event as `field changed: knowledge_targets`.
    Losing a field is data loss, not a field change — so the fields have to be in the signature.
    """
    meta, body = parse_frontmatter(text)
    sections = extract_sections(body)
    return {
        "summary": sections.get("Summary", "").strip(),
        "lookup_keys": sections.get("Lookup Keys", "").strip(),
        "knowledge_targets": sections.get("Knowledge Targets", "").strip(),
        "artifact_locator": meta.get("artifact_locator", ""),
        "_fields": {k: str(v) for k, v in (meta or {}).items() if k not in VOLATILE_FIELDS},
    }


def _is_placeholder(v: str) -> bool:
    """A field holding `unknown` / `[]` / empty carries NO assessment — pruning it is deliberate
    (the builder re-emits these defaults every run and refresh drops the pure placeholders).
    Only the loss of an ASSESSED value is data loss."""
    return v.strip() in ("", "unknown", "[]", "None", "none")


def _report_delta(old_sig: dict, new_sig: dict) -> list:
    """Return human-readable delta lines. A DROP is always reported as a drop, never as a change."""
    lines: list = []
    old_f, new_f = old_sig.get("_fields", {}), new_sig.get("_fields", {})
    for k in sorted(set(old_f) - set(new_f)):
        if _is_placeholder(old_f[k]):
            lines.append(f"  placeholder pruned: {k} (was {old_f[k].strip() or 'empty'!r} — no assessment lost)")
        else:
            lines.append(f"  field DROPPED: {k} (was: {old_f[k][:60]!r}) — DATA LOSS")
    for k in sorted(set(new_f) - set(old_f)):
        lines.append(f"  field added: {k}")
    for k in sorted(set(old_f) & set(new_f)):
        if old_f[k] != new_f[k]:
            lines.append(f"  field changed: {k}")
    for k in ("summary", "lookup_keys", "knowledge_targets", "artifact_locator"):
        if old_sig.get(k) != new_sig.get(k):
            lines.append(f"  section changed: {k}")
    return lines


def main() -> int:
    p = argparse.ArgumentParser(description="Refresh Wiki Source Meta")
    p.add_argument("--meta", required=True, help="Existing meta path")
    p.add_argument("--profile", default="",
                   help="Source Interpretation Profile (.yml). Default: the meta's own profile_id, "
                        "resolved under wiki_sources/profiles/. Note this is NOT a project profile "
                        "(WKP-*.yml) — passing one silently reshapes the meta.")
    p.add_argument("--allow-profile-switch", action="store_true",
                   help="Permit --profile that differs from the meta's profile_id (it rewrites the "
                        "meta against a different schema and may DROP fields)")
    p.add_argument("--apply", action="store_true",
                   help="Overwrite existing meta (default writes .refresh.md draft)")
    p.add_argument("--review-decision", default="draft_created",
                   help="Review decision for traceability; use approved_to_apply when applying after review")
    p.add_argument("--impact-level", default="unknown")
    p.add_argument("--change-summary", default="Refresh Wiki Source Meta from current source artifact.")
    p.add_argument("--regenerate-summary", action="store_true",
                   help="Re-derive summary mechanically instead of preserving the curated one")
    p.add_argument("--regenerate-lookup-keys", action="store_true",
                   help="Re-derive lookup keys mechanically from scratch (DROPS every curated key)")
    p.add_argument("--union-lookup-keys", action="store_true",
                   help="Legacy union merge: curated + newly derived keys (CR-012 Fix 6 semantics). "
                        "Opt-in since CR-AIWS-2026-07-038 (DP-038-2=C) — the default now PRESERVES "
                        "curated keys and only SUGGESTS new ones")
    p.add_argument("--preserve-lookup-keys", action="store_true",
                   help="Explicitly request the default: keep ## Lookup Keys byte-identical; print "
                        "newly derived keys as suggestions without writing them")
    ns = p.parse_args()
    if ns.regenerate_lookup_keys + ns.union_lookup_keys + ns.preserve_lookup_keys > 1:
        print("error: --regenerate-lookup-keys / --union-lookup-keys / --preserve-lookup-keys "
              "are mutually exclusive", file=sys.stderr)
        return 2

    meta_path = Path(ns.meta).resolve()
    if not meta_path.exists():
        print(f"error: meta not found: {meta_path}", file=sys.stderr)
        return 2

    old_text = read_text(meta_path)
    old_meta, old_body = parse_frontmatter(old_text)
    old_sections = extract_sections(old_body)

    # CR-AIWS-2026-07-052 T2: the profile is a property OF THE META. Making --profile required meant
    # the caller re-supplied it every run, and supplying a DIFFERENT one silently rewrote the meta
    # against a foreign schema — the trap that cost 7 fields in AIP-EXEC-958, where a *project*
    # profile (WKP-*.yml) was passed where a *source interpretation* profile was expected. Two file
    # kinds, one flag, no complaint. Default to the meta's own profile_id; a switch must be explicit.
    meta_profile_id = str(old_meta.get("profile_id", "") or "").strip()
    ai_work_root = find_ai_work_root(meta_path) / ".ai-work"
    if not ns.profile:
        if not meta_profile_id:
            print("error: meta has no profile_id and --profile was not given", file=sys.stderr)
            return 2
        ns.profile = str(ai_work_root / "wiki_sources" / "profiles" / f"{meta_profile_id}.yml")
        if not Path(ns.profile).exists():
            print(f"error: profile '{meta_profile_id}' (from the meta) not found at {ns.profile}",
                  file=sys.stderr)
            return 2
    elif meta_profile_id and Path(ns.profile).stem != meta_profile_id and not ns.allow_profile_switch:
        print(f"error: --profile '{Path(ns.profile).stem}' differs from the meta's profile_id "
              f"'{meta_profile_id}'. Rewriting a meta against a different profile can DROP fields it "
              f"already has. Re-run without --profile to use the meta's own profile, or pass "
              f"--allow-profile-switch if the switch is intended.", file=sys.stderr)
        return 2
    # CR-AIWS-2026-07-038 T2: object node (artifact_locator __OBJECT__, CR-2026-06-004) has no
    # backing file BY DESIGN — source re-read does not apply. Graceful no-op (rc=0), never the
    # misleading "unreachable" error (round-3 R3-01).
    # CR-AIWS-2026-07-064 B1 (Rule 9): normalize ONCE before the value becomes a path — a bare
    # `artifact_locator:` key parses to [] and `null` to None (Path() -> TypeError), while ""
    # collapses to Path(".") which passes exists() and reaches the builder as a directory.
    loc = locator_str(old_meta.get("artifact_locator"))
    if loc == "__OBJECT__":
        print("object node — nothing to re-derive (hand-authored); refresh by hand per "
              "aiws-wiki refresh-meta (Sourceless refresh)")
        return 0
    artifact = resolve_data_file(loc, ai_work_root.parent) if loc else None
    if artifact is None:
        print(f"error: artifact locator unreachable: {loc!r}", file=sys.stderr)
        return 2

    # CR-AIWS-2026-08-062 C1 (IR-08b A5-1) — refuse a CHUNKED PARENT. Detection: the meta's own
    # Related Sources carries `role: contains` edges to `<source_id>-SEC-*` children, OR sibling
    # child files exist on disk. Refuse-with-pointer (rc=2), never auto re-route: re-chunking is a
    # set-level operation the caller must run deliberately on the parent via the builder.
    _sid = str(old_meta.get("source_id", "") or meta_path.stem)
    _rs_old = old_sections.get("Related Sources", "")
    _has_contains = bool(re.search(r"role:\s*contains\b", _rs_old)) and (f"{_sid}-SEC-" in _rs_old)
    _has_children = any(meta_path.parent.glob(f"{_sid}-SEC-*.md"))
    if not old_meta.get("section_lines") and (_has_contains or _has_children):
        print(f"error: {meta_path.name} is a CHUNKED PARENT ({_sid} has -SEC- children). This tool "
              "refreshes ONE meta in place and would leave the real children stale (builder writes "
              "the set into a temp out-dir). Re-chunk the whole set instead:\n"
              f"  py .ai-work/tooling/build_wiki_source_meta.py --artifact <src> --source-id {_sid} "
              "--source-type <t> --profile <p> --title <t> --out <this meta path> --mode refresh "
              "[--system <id>]   (CR-AIWS-2026-08-062 / CR-AIWS-2026-07-006 A1)", file=sys.stderr)
        return 2

    # Fix 1 — preserve curated Summary unless explicitly regenerating.
    old_summary = old_sections.get("Summary", "").strip()
    preserve_summary = None
    if not ns.regenerate_summary and old_summary:
        preserve_summary = old_summary
        if not _looks_curated_summary(old_summary):
            print(f"WARNING: preserving an old summary that looks low-quality "
                  f"({old_summary[:50]!r}); pass --regenerate-summary to re-derive it.",
                  file=sys.stderr)

    new_text = _project(
        artifact=artifact,
        source_id=old_meta.get("source_id", meta_path.stem),
        source_type=old_meta.get("source_type", "unknown"),
        profile=Path(ns.profile).resolve(),
        title=old_meta.get("title"),
        summary=preserve_summary,
        seed_text=old_text,
    )

    # Preserve curated frontmatter from old meta. Refresh ≠ re-assessment, so the
    # builder's placeholder defaults must neither clobber an assessed value nor
    # bloat a minimal meta with un-assessed stubs.
    new_meta, new_body = parse_frontmatter(new_text)
    _PLACEHOLDERS = ("", "unknown", None, [])

    # (a) Builder always re-emits these with placeholder defaults: keep a
    #     previously-assessed value, else drop the pure placeholder (Fix 5).
    for key in (
        "authority_level", "freshness_status", "source_representation_status",
        "source_representation_caution", "knowledge_value", "intended_ai_use",
        "conversion_method", "conversion_limitations", "representation_type",
    ):
        old_val = old_meta.get(key)
        if old_val not in _PLACEHOLDERS:
            new_meta[key] = old_val
        elif new_meta.get(key) in _PLACEHOLDERS:
            new_meta.pop(key, None)

    # (b) Builder may not emit these; preserve curated value if new lacks it.
    #     H6 + CR-AIWS-2026-07-006 A1: re-chunk-on-refresh is now IMPLEMENTED in
    #     build_wiki_source_meta (--mode refresh re-emits children with hash carry-over + orphan
    #     cleanup) — the correct refresh path for a CHUNKED source is the builder on the PARENT
    #     (children rebuild as a set). This tool refreshes ONE meta in place; when pointed at a
    #     chunk CHILD it still preserves the section fields verbatim (never regenerate a child in
    #     isolation — ranges are a set-level property) and reminds the caller to re-chunk.
    for key in (
        "source_representation_quality_issue", "representation_scope",
        "converted_by", "conversion_date", "representation_locator",
        "original_source_locator", "section_heading", "section_lines", "section_hash",
    ):
        if key in old_meta and key not in new_meta:
            new_meta[key] = old_meta[key]
    if old_meta.get("section_lines"):
        print("note: this is a CHUNKED SECTION meta — per CR-AIWS-2026-07-006 A1, refresh the "
              "PARENT via build_wiki_source_meta --mode refresh (re-chunks the whole set with "
              "hash carry-over); section_lines preserved verbatim here.", file=sys.stderr)

    # CR-AIWS-2026-06-061 §8.5 (writer obligation — a refresh MUST preserve the meta's `system`):
    # thread the existing meta's `system` explicitly so refresh never drops it, independent of
    # build_meta's seed-based refresh-preserve (defense in depth — keeps refresh correct on its own).
    if old_meta.get("system"):
        new_meta["system"] = old_meta["system"]

    new_meta.setdefault("promotion_status", "draft")
    # Fix R2 — reflect review outcome in apply mode; keep draft markers otherwise.
    # An applied, human-approved refresh must not keep claiming "not approved".
    if ns.apply and ns.review_decision == "approved_to_apply":
        new_meta["maintenance_status"] = "active"
        new_meta["review_required"] = False
        new_meta["review_status"] = ns.review_decision
    else:
        new_meta.setdefault("maintenance_status", "needs_review")
        new_meta.setdefault("review_required", True)
        new_meta["review_status"] = "draft_refresh_not_approved"

    # Fix 2 — preserve enriched body sections the builder does not regenerate
    # (e.g. ## Cautions, ## Change Impact Hints, or sections added by other tools).
    new_sections = extract_sections(new_body)
    new_names_lower = {k.strip().lower() for k in new_sections}
    preserved_blocks = [
        (name, content)
        for name, content in old_sections.items()
        if name.strip().lower() not in new_names_lower
        and name.strip().lower() not in _BODY_PRESERVE_DENY
    ]
    if preserved_blocks:
        extra = "".join(f"\n## {name}\n{content}\n" for name, content in preserved_blocks)
        new_body = new_body.rstrip() + "\n" + extra
        print("preserved body sections: " + ", ".join(n for n, _ in preserved_blocks))

    # Lookup Keys on refresh — three modes (CR-AIWS-2026-07-038 T6, DP-038-2=C):
    #   DEFAULT / --preserve-lookup-keys : keep the curated ## Lookup Keys byte-identical;
    #       newly derived keys are PRINTED as suggestions, never written silently. Rationale:
    #       union was monotonic — mechanical junk (raw headings, generic single words)
    #       accumulated on every refresh and degraded retrieval precision (round-3 R3-07);
    #       with the lossless index (CR-037) nothing downstream caps it either.
    #   --union-lookup-keys : legacy Fix 6 union (curated + new, de-dup, CR-044 re-filter).
    #   --regenerate-lookup-keys : re-derive from scratch (drops curated — explicit only).
    if not ns.regenerate_lookup_keys:
        old_lookup = _parse_bullets(old_sections.get("Lookup Keys", ""))
        if old_lookup:
            new_lookup = _parse_bullets(new_sections.get("Lookup Keys", ""))
            new_only = [k for k in new_lookup
                        if k.lower() not in {o.lower() for o in old_lookup}]
            if ns.union_lookup_keys:
                merged = _dedupe_stable(old_lookup + new_lookup)
                # CR-AIWS-2026-06-044: re-filter the UNIONED single-token keys against the profile's
                # CURRENT stopword union, so a stopword-config change (project_stopwords.yml /
                # extra_stopwords) propagates to existing metas on a normal refresh — without
                # --regenerate-lookup-keys (which drops ALL curated keys). Multi-word/curated keys kept;
                # fail-open (never drop keys) if the profile/stopwords cannot be resolved.
                try:
                    from _common import lookup_key_stopwords, code_key_stopwords
                    _prof = Path(ns.profile).resolve()
                    _stype = old_meta.get("source_type", "")
                    _stop = (code_key_stopwords(_prof) if _stype in ("java_source", "code")
                             else lookup_key_stopwords(_prof))
                    merged = [k for k in merged
                              if (" " in k.strip()) or (k.strip().lower() not in _stop)]
                except Exception:  # noqa: BLE001 — never drop keys without a valid stopword union
                    pass
                if merged != new_lookup:
                    new_body = _replace_section(new_body, "Lookup Keys", _render_bullets(merged))
                    print(f"merged lookup keys: {len(old_lookup)} curated + {len(new_only)} new "
                          f"-> {len(merged)} total (union; --regenerate-lookup-keys to re-derive)")
            else:
                # default preserve: re-emit the curated section EXACTLY as authored
                new_body = _replace_section(new_body, "Lookup Keys",
                                            old_sections.get("Lookup Keys", "").rstrip("\n"))
                if new_only:
                    print(f"preserved {len(old_lookup)} curated lookup keys; "
                          f"{len(new_only)} new candidate keys (not written): "
                          f"{', '.join(new_only[:10])}"
                          f"{' …' if len(new_only) > 10 else ''} "
                          f"(--union-lookup-keys to merge)")
                else:
                    print(f"preserved {len(old_lookup)} curated lookup keys (no new candidates)")

    from _common import dump_frontmatter, strip_lint_accept
    strip_lint_accept(new_meta)  # reset accepts on rewrite (strip-on-refresh, CR-AIWS-2026-06-065)
    new_text = dump_frontmatter(new_meta) + new_body

    old_sig = _signature(old_text)
    new_sig = _signature(new_text)
    changed = old_sig != new_sig

    if ns.apply:
        # CR-AIWS-2026-08-075 C1 — backup goes to wiki_sources/_backups/, not beside the meta.
        # mkdir first: shutil.copy2 does NOT create parent dirs (the draft branch below mkdirs
        # explicitly for the same reason), and _backups/ does not exist on a fresh clone.
        # Still copy2, not a text write: the backup must be a BYTE copy — a text write would
        # normalise the meta's EOL and the backup would no longer reproduce what was replaced.
        backup = backup_path_for(meta_path)
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(meta_path, backup)
        write_text(meta_path, new_text)
        # CR-AIWS-2026-07-032 T2c: applying a refresh CLEARS the pending draft — both the
        # current _drafts/ location and the legacy beside-the-meta location (pre-CR-032).
        # CR-AIWS-2026-08-079 DP-079-A = a: a THIRD location can hold a stale draft — the one the
        # pre-fix anchor produced for aiws_meta/ metas (`<ns>/<group>/_drafts/<stem>.refresh.md`).
        # The tuple already cleaned the current + the pre-CR-032 legacy spot; adding this keeps a
        # draft written by the old code from outliving the code that wrote it.
        _legacy_ns_draft = meta_path.parent / "_drafts" / (meta_path.stem + ".refresh.md")
        for stale in (draft_path_for(meta_path), meta_path.with_suffix(".refresh.md"),
                      _legacy_ns_draft):
            if stale.exists():
                stale.unlink()
                print(f"cleaned pending draft: {stale}")
        rollback_hint = f"Restore backup at {backup} and rebuild Wiki Source Index if needed."
        _append_maintenance_log(
            meta_path=meta_path,
            action="meta_applied",
            source_id=old_meta.get("source_id", meta_path.stem),
            target_artifact=meta_path,
            old_locator=str(backup),
            new_locator=str(meta_path),
            change_summary=ns.change_summary,
            impact_level=ns.impact_level,
            review_decision=ns.review_decision,
            rollback_hint=rollback_hint,
        )
        print(f"applied refresh: {meta_path} (backup at {backup})")
        print(f"rollback_hint: {rollback_hint}")
        print("note: apply writes the file, but does not by itself prove Knowledge Hub promotion/approval.")
    else:
        draft = draft_path_for(meta_path)
        draft.parent.mkdir(parents=True, exist_ok=True)
        write_text(draft, new_text)
        _append_maintenance_log(
            meta_path=meta_path,
            action="refresh_draft_created",
            source_id=old_meta.get("source_id", meta_path.stem),
            target_artifact=draft,
            old_locator=str(meta_path),
            new_locator=str(draft),
            change_summary=ns.change_summary,
            impact_level=ns.impact_level,
            review_decision="draft_created",
            rollback_hint="Delete draft if rejected; no canonical meta was changed.",
        )
        print(f"draft written: {draft}")
        print("status: draft_created — review required before apply/promotion")

    delta = _report_delta(old_sig, new_sig)
    print(f"material change: {'yes' if changed else 'no'}")
    for line in delta:
        print(line)
    if any("DROPPED" in d for d in delta):
        print("WARNING: this refresh REMOVES fields the meta already had. Review the draft before "
              "applying — a dropped field is data loss, not a refresh.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
