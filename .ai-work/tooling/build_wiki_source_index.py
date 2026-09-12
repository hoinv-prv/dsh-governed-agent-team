#!/usr/bin/env python3
"""Build the Wiki Source Index as a projection of all source metas.

Reads every source meta under <ai-work>/wiki_sources/meta/ and emits a
JSONL index of lightweight entries. The index is a PROJECTION: it must
not embed the full meta body.

Scopes:
  project  (default) — scans .ai-work/wiki_sources/meta/, writes index.jsonl
                        artifact/meta locators use __PROJECT_ROOT__ placeholder
  aiws     — scans .ai-work/wiki_sources/aiws_meta/, writes index.aiws.jsonl
             (the AIWS methodology index; first-class labeled build per CR-AIWS-2026-06-061
             §8.5 — was a --meta-dir/--out hack). __PROJECT_ROOT__ locators; projection
             (incl. `system`) identical to the prior hack.
  local    — reads index.local.sources.json for external meta dirs,
             writes index.local.jsonl; locators are kept as absolute paths
  all      — runs project + local (aiws stays opt-in; not bundled into 'all')
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (  # noqa: E402
    OBJECT_LOCATOR_SENTINEL,
    append_maintenance_log,
    extract_sections,
    find_ai_work_root,
    locator_str,
    parse_frontmatter,
    portable_locator,
    read_project_config,
    read_text,
    write_jsonl,
)


def _write_index_rebuild_log(ai_work: Path, out: Path, count: int, scope: str) -> None:
    """Append a lightweight WSM maintenance log entry for index rebuild.

    This is projection maintenance, not approval/promotion.
    """
    from datetime import datetime, timezone
    from uuid import uuid4

    log_path = ai_work / "wiki_sources" / "maintenance_log.jsonl"
    # Store a portable __PROJECT_ROOT__-relative locator (not an absolute path)
    # so the log stays portable across machines/checkouts. Outside-root paths
    # (e.g. local scope) are returned unchanged by portable_locator.
    out_locator = portable_locator(out, ai_work.parent)
    entry = {
        # CR-AIWS-2026-06-058 (IR-B): disambiguate by the output target stem + a uuid so --out-override
        # builds (e.g. the aiws index) and two same-second/same-target rebuilds never collide. The old
        # `-INDEX-{scope}` was a hardcoded literal (always 'project' for --out builds) at second
        # granularity → lint_wiki maintenance_log_dup. No reader parses log_id structure.
        "log_id": f"WSMLOG-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-INDEX-{out.stem}-{uuid4().hex[:8]}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "maintenance_model_version": "wsm_v1",
        "action": "index_rebuilt",
        # IR-01 (CR-006 Option A): index rebuild has no single source artifact;
        # use a meaningful sentinel so the required source_id field is never empty.
        "source_id": "(index-projection)",
        "target_artifact": out_locator,
        "old_locator": "",
        "new_locator": out_locator,
        "change_summary": f"Rebuilt Wiki Source Index projection with {count} entries.",
        "reason": "Wiki Source Index projection rebuild",
        "impact_level": "unknown",
        "review_decision": "projection_rebuilt",
        "applied_by": "tool:build_wiki_source_index.py",
        "rollback_hint": "Restore previous index from package/git/history if needed.",
        "runtime_boundary": "index rebuild is projection maintenance, not Knowledge Hub promotion",
    }
    append_maintenance_log(log_path, entry)


def _omit_blank(d: dict) -> dict:
    """Strip keys whose value is empty string, None, or empty list.

    Keeps index entries lean: tools use rec.get(k, "") so missing fields
    are equivalent to empty-string fields at read time.
    """
    return {k: v for k, v in d.items() if v not in ("", None, [])}


def _list_items(section_text: str) -> list[str]:
    out: list[str] = []
    for line in section_text.splitlines():
        s = line.strip()
        if s.startswith("- "):
            out.append(s[2:].strip())
    return out


def _project_meta(path: Path, project_root: Path | None) -> dict:
    """Project a single meta file to an index record.

    If project_root is given, artifact/meta locators are made portable
    (__PROJECT_ROOT__ prefix). If None, absolute paths are kept as-is.
    """
    raw_text = read_text(path)
    meta, body = parse_frontmatter(raw_text)
    if not meta and raw_text.strip():
        print(f"WARNING: {path} — frontmatter parse returned empty dict; possible BOM or malformed YAML. Entry may be incomplete.",
              file=sys.stderr)
    sections = extract_sections(body)
    summary_raw = sections.get("Summary", "").strip()
    summary_short = (summary_raw[:300] + "...") if len(summary_raw) > 300 else summary_raw
    # CR-AIWS-2026-07-037: index = LOSSLESS projection of the meta's ## Lookup Keys —
    # no positional cap (the old raw_keys[:30] silently dropped key 31+ from lookup).
    # Hygiene moved to the meta layer: lint_wiki WARN meta_lookup_keys_over_budget.
    lookup_keys = _list_items(sections.get("Lookup Keys", ""))
    knowledge_targets = _list_items(sections.get("Knowledge Targets", ""))

    # Two-kind node model (CR-AIWS-2026-05-023 / DP7): a node_kind=object meta carries
    # artifact_locator=OBJECT_LOCATOR_SENTINEL (no backing source file). The sentinel is
    # preserved verbatim — portable_locator returns it unchanged (INV-9) and _omit_blank keeps
    # it (non-empty) — so object metas land in the SAME index.jsonl, found by the SAME lookup.
    if project_root is not None:
        artifact_loc = portable_locator(meta.get("artifact_locator", ""), project_root)
        meta_loc = portable_locator(path, project_root)
        orig_loc = portable_locator(meta.get("original_source_locator", ""), project_root)
        repr_loc = portable_locator(
            meta.get("representation_locator", meta.get("artifact_locator", "")),
            project_root,
        )
    else:
        artifact_loc = meta.get("artifact_locator", "")
        meta_loc = str(path)
        orig_loc = meta.get("original_source_locator", "")
        repr_loc = meta.get("representation_locator", meta.get("artifact_locator", ""))

    record: dict = {
        # Required by lint (INDEX_REQUIRED) — always present
        "source_id": meta.get("source_id", path.stem),
        "title": meta.get("title", path.stem),
        "source_type": meta.get("source_type", ""),
        "artifact_locator": artifact_loc,
        "profile_id": meta.get("profile_id", ""),
        "summary_short": summary_short,
        "knowledge_targets": knowledge_targets,
        "status": meta.get("status", "active"),
        # Navigation — required by lookup + evaluate
        "meta_locator": meta_loc,
        "lookup_keys": lookup_keys,
        # Optional metadata — blanks stripped by _omit_blank
        "authority_level": meta.get("authority_level", ""),
        "freshness_status": meta.get("freshness_status", ""),
        "promotion_status": meta.get("promotion_status", ""),
        "source_representation_status": meta.get("source_representation_status", ""),
        "source_representation_caution": meta.get("source_representation_caution", ""),
        "representation_type": meta.get("representation_type", ""),
        "conversion_method": meta.get("conversion_method", ""),
        "conversion_limitations": meta.get("conversion_limitations", []),
        "intended_ai_use": meta.get("intended_ai_use", ""),
        # CR-AIWS-2026-06-017 (multi-system scoping): optional `system` scope axis.
        # omit-blank strips it when absent → absent == "common" (visible under every system).
        "system": meta.get("system", ""),
        # H6 (CR-AIWS-2026-07-002): section-addressing for chunked large sources. omit-blank strips
        # them for normal (non-section) metas → zero migration. section_lines = "start-end" so runtime
        # Reads just that range of the shared artifact_locator instead of the whole file.
        "section_heading": meta.get("section_heading", ""),
        "section_lines": meta.get("section_lines", ""),
    }

    # Include locators only when they add information beyond artifact_locator
    if orig_loc and orig_loc != artifact_loc:
        record["original_source_locator"] = orig_loc
    if repr_loc and repr_loc != artifact_loc:
        record["representation_locator"] = repr_loc

    # Binary-by-design stubs (CR-066): project the flag so the index linter can exempt them.
    # Emitted only when true → _omit_blank keeps False, so adding key conditionally keeps normal records lean.
    if meta.get("not_meta_applicable") is True:
        record["not_meta_applicable"] = True

    # Permanently removed: meta_id (dup of source_id), updated_at,
    # knowledge_value — not read by any tool from index.
    # Deliberately NOT projected: node_kind. It is a META-ONLY field (CR-AIWS-2026-05-023
    # INV-7) — object metas must be indistinguishable from artifact metas at the index/lookup
    # layer (DP7: no --kind flag, no scorer change). Do NOT add node_kind to this record.

    return _omit_blank(record)


def _build_project(project_root: Path, meta_dir_override: str | None,
                   out_override: str | None) -> int:
    ai_work = project_root / ".ai-work"
    meta_dir = Path(meta_dir_override).resolve() if meta_dir_override else (
        ai_work / "wiki_sources" / "meta")
    out = Path(out_override).resolve() if out_override else (
        ai_work / "wiki_sources" / "index.jsonl")

    if not meta_dir.is_dir():
        print(f"error: meta dir not found: {meta_dir}", file=sys.stderr)
        return 2

    # DESIGN-03: warn about stale entries in existing index before rebuilding
    if out.exists():
        try:
            prefix = "__PROJECT_ROOT__"
            for raw_line in out.read_text(encoding="utf-8").splitlines():
                raw_line = raw_line.strip()
                if not raw_line:
                    continue
                rec = json.loads(raw_line)
                meta_loc = rec.get("meta_locator", "")
                if meta_loc.startswith(prefix):
                    rel = meta_loc[len(prefix):].lstrip("/\\")
                    real = project_root / Path(rel)
                    if not real.exists():
                        print(f"WARNING: stale index entry — backing meta no longer exists for '{rec.get('source_id', meta_loc)}'",
                              file=sys.stderr)
        except Exception:
            pass

    # CR-AIWS-2026-08-052 C3 — single-index repo: aiws_meta/ folds into the SAME index.jsonl
    # (metas point at the product/ SoT; no in-repo index.aiws.jsonl). Dual-index projects scan
    # exactly the one dir as before.
    scan_dirs = [meta_dir]
    if not meta_dir_override and read_project_config(ai_work)["wiki_single_index"]:  # CR-128 C3
        aiws_meta = ai_work / "wiki_sources" / "aiws_meta"
        if aiws_meta.is_dir():
            scan_dirs.append(aiws_meta)

    records: list[dict] = []
    for d in scan_dirs:
        for f in sorted(d.rglob("*.md")):
            if f.name.endswith(".refresh.md"):
                continue  # pending refresh draft, not a meta (CR-AIWS-2026-07-032 T2 — never project)
            try:
                records.append(_project_meta(f, project_root))
            except Exception as e:  # noqa: BLE001
                print(f"warn: failed to project {f}: {e}", file=sys.stderr)

    write_jsonl(out, records)
    _write_index_rebuild_log(ai_work, out, len(records), "project")
    print(f"[project] wrote {len(records)} entries → {out}")
    print("note: index rebuild is projection maintenance, not approval/promotion")
    return 0


def _build_local(project_root: Path, out_override: str | None) -> int:
    ai_work = project_root / ".ai-work"
    config_path = ai_work / "wiki_sources" / "index.local.sources.json"
    out = Path(out_override).resolve() if out_override else (
        ai_work / "wiki_sources" / "index.local.jsonl")

    if not config_path.exists():
        print(f"error: local sources config not found: {config_path}", file=sys.stderr)
        print("  Create index.local.sources.json with: {\"meta_dirs\": [\"<path>\", ...]}",
              file=sys.stderr)
        return 2

    try:
        cfg = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"error: invalid JSON in {config_path}: {e}", file=sys.stderr)
        return 2

    meta_dirs = cfg.get("meta_dirs", [])
    if not meta_dirs:
        print(f"warn: no meta_dirs defined in {config_path}", file=sys.stderr)
        write_jsonl(out, [])
        print(f"[local] wrote 0 entries → {out}")
        return 0

    records: list[dict] = []
    for raw_dir in meta_dirs:
        # CR-AIWS-2026-07-064 C1 (Rule 9): meta_dirs comes from a hand-authored JSON config. An
        # empty entry became Path("") == Path(".") — the CWD, which IS a directory — so the guard
        # below passed and rglob swept the ENTIRE working tree into index.local.jsonl, silently.
        # A non-string entry raised TypeError outside the per-file try below and killed the run.
        raw_s = locator_str(raw_dir)
        if not raw_s:
            print(f"warn: invalid meta_dirs entry {raw_dir!r} (blank/non-string), skipping",
                  file=sys.stderr)
            continue
        meta_dir = Path(raw_s)
        if not meta_dir.is_dir():
            print(f"warn: meta dir not found, skipping: {meta_dir}", file=sys.stderr)
            continue
        for f in sorted(meta_dir.rglob("*.md")):
            if f.name.endswith(".refresh.md"):
                continue  # pending refresh draft, not a meta (CR-AIWS-2026-07-032 T2 — never project)
            try:
                records.append(_project_meta(f, project_root=None))
            except Exception as e:  # noqa: BLE001
                print(f"warn: failed to project {f}: {e}", file=sys.stderr)

    write_jsonl(out, records)
    _write_index_rebuild_log(ai_work, out, len(records), "local")
    print(f"[local] wrote {len(records)} entries → {out}")
    print("note: index rebuild is projection maintenance, not approval/promotion")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Build Wiki Source Index")
    p.add_argument("--scope", choices=["project", "aiws", "local", "all"], default="project",
                   help="Which index to build (default: project). 'aiws' builds index.aiws.jsonl "
                        "from aiws_meta/ (CR-AIWS-2026-06-061 §8.5); 'all' = project + local.")
    p.add_argument("--meta-dir", help="Override meta directory (project scope only)")
    p.add_argument("--out", help="Override output path")
    ns = p.parse_args()

    project_root = find_ai_work_root(Path.cwd())
    rc = 0

    if ns.scope in ("project", "all"):
        rc = max(rc, _build_project(project_root, ns.meta_dir, ns.out))

    if ns.scope == "aiws":
        # First-class aiws build (CR-AIWS-2026-06-061 §8.5): reuse _build_project with the AIWS
        # meta dir + index.aiws.jsonl so output is identical to the prior --meta-dir/--out hack.
        ai_work = project_root / ".ai-work"
        if read_project_config(ai_work)["wiki_single_index"]:  # CR-128 C3
            # CR-AIWS-2026-08-052 C3 — single-index repo: no in-repo index.aiws.jsonl; aiws_meta
            # folds into index.jsonl. Redirect the habitual invocation to the project build so a
            # stale runbook line cannot resurrect the retired index file.
            print("note: wiki_single_index=true — aiws_meta folds into index.jsonl "
                  "(no index.aiws.jsonl in this repo; CR-AIWS-2026-08-052). Building project index.")
            rc = max(rc, _build_project(project_root, None, None))
        else:
            aiws_meta = str(ai_work / "wiki_sources" / "aiws_meta")
            aiws_out = ns.out or str(ai_work / "wiki_sources" / "index.aiws.jsonl")
            rc = max(rc, _build_project(project_root, aiws_meta, aiws_out))

    if ns.scope in ("local", "all"):
        rc = max(rc, _build_local(project_root, ns.out if ns.scope == "local" else None))

    return rc


if __name__ == "__main__":
    raise SystemExit(main())
