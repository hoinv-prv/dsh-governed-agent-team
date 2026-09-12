#!/usr/bin/env python3
"""Detect which wiki source artifacts may have changed.

Strategy: maintain a snapshot of (size, mtime, sha1) per artifact under
`.ai-work/wiki_sources/.snapshot.json`. On each run, compare the current
state of artifacts referenced in source metas against the snapshot and
report changed / missing / new ones.

Git is NOT required. If `--use-git` is passed and a .git/ is present, we
also include modified files under git's output as a soft signal.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (  # noqa: E402
    find_ai_work_root, meta_roots, parse_frontmatter, read_text, write_text,
)


def _fingerprint(path: Path) -> dict:
    # CR-AIWS-2026-07-063 T2 — tripwire, not the primary guard: every caller must classify
    # non-file paths BEFORE calling (Path("") == Path("."), an existing directory, slips past
    # bare exists() checks). If this ever fires, the bug is at the call site.
    if not path.is_file():
        raise ValueError(f"not a file: {path}")
    b = path.read_bytes()
    return {
        "size": len(b),
        "mtime": int(path.stat().st_mtime),
        "sha1": hashlib.sha1(b).hexdigest(),
    }


def _git_modified(root: Path) -> set[str]:
    try:
        r = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=root, capture_output=True, text=True, check=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return set()
    out: set[str] = set()
    for line in r.stdout.splitlines():
        if len(line) > 3:
            out.add(str((root / line[3:].strip()).resolve()))
    return out


def main() -> int:
    p = argparse.ArgumentParser(description="Detect changed wiki sources")
    p.add_argument("--refresh-snapshot", action="store_true",
                   help="Write new snapshot after comparing")
    p.add_argument("--use-git", action="store_true")
    p.add_argument("--format", choices=["text", "json"], default="text")
    p.add_argument("--paths",
                   help="Comma-separated path prefixes (relative to project root, or absolute): "
                        "only REPORT sources whose artifact (meta file, for __OBJECT__ nodes) lies "
                        "under one of them. Scopes reporting + exit code only — the inventory and "
                        "--refresh-snapshot stay repo-wide, so a scoped run never truncates the "
                        "baseline (CR-AIWS-2026-08-033 C2, DP-033-A=b).")
    ns = p.parse_args()

    root = find_ai_work_root(Path.cwd())
    ai_work = root / ".ai-work"
    # CR-AIWS-2026-07-049: walk EVERY meta namespace (project meta/ + shipped aiws_meta/) via the
    # shared helper — before this the detector only saw meta/, so a change to any of the 188 AIWS
    # metas was NEVER reported (verified: 150 aiws metas edited -> 0 aiws records).
    roots = meta_roots(ai_work)
    snap_path = ai_work / "wiki_sources" / ".snapshot.json"

    if not roots:
        print(f"error: no meta dir found under {ai_work / 'wiki_sources'}", file=sys.stderr)
        return 2

    snapshot_existed = snap_path.exists()
    old_snap: dict[str, dict] = {}
    if snapshot_existed:
        try:
            old_snap = json.loads(snap_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            old_snap = {}

    current: dict[str, dict] = {}
    meta_by_sid: dict[str, dict] = {}
    missing: list[str] = []
    for meta_file in sorted(f for root in roots for f in root.rglob("*.md")):
        if meta_file.name.endswith(".refresh.md"):
            continue  # pending refresh draft, not a meta (CR-AIWS-2026-07-032 T2 — never inventory)
        meta, _ = parse_frontmatter(read_text(meta_file))
        sid = meta.get("source_id", meta_file.stem)
        # CR-AIWS-2026-07-063 T1: normalize ONCE and classify BEFORE building any Path. A bare
        # `artifact_locator:` key parses to [] (list); a 0-byte meta has no key at all.
        # Path("") == Path(".") — an existing DIRECTORY — so exists() alone can never reject an
        # empty locator, and read_bytes() on it aborts the whole run.
        raw_loc = meta.get("artifact_locator", "")
        loc = raw_loc.strip() if isinstance(raw_loc, str) else ""
        if loc == "__OBJECT__":
            # Object node (CR-AIWS-2026-06-004): no artifact BY DESIGN — never "missing"
            # (CR-AIWS-2026-07-032 T3 / H-03). The object changes when its META changes, so
            # fingerprint the meta file; the record keeps artifact_locator = __OBJECT__ and
            # surfaces the meta path via representation_locator.
            meta = {**meta, "representation_locator": meta.get("representation_locator")
                    or str(meta_file)}
            meta_by_sid[sid] = meta
            current[sid] = {"path": "__OBJECT__", **_fingerprint(meta_file)}
            continue
        meta_by_sid[sid] = meta
        if not loc:
            missing.append(sid)
            continue
        artifact = Path(loc)
        if not artifact.exists() or not artifact.is_file():
            missing.append(sid)
            continue
        current[sid] = {"path": str(artifact), **_fingerprint(artifact)}
        # H2 (CR-AIWS-2026-07-002 / CAP-902-006): also fingerprint the ORIGINAL binary so a change to
        # the un-converted source (Excel/PDF) is detected even when the MD representation is stale.
        # CR-AIWS-2026-07-063 T1b: same guard class as the artifact leg. A non-resolving orig stays a
        # SILENT no-op (unchanged semantics — reclassifying orig-not-found is out of scope here).
        raw_orig = meta.get("original_source_locator", "")
        orig = raw_orig.strip() if isinstance(raw_orig, str) else ""
        if orig:
            orig_p = Path(orig)
            if orig_p.is_file():
                current[sid]["orig_path"] = str(orig_p)
                current[sid]["orig_sha1"] = _fingerprint(orig_p)["sha1"]

    changed: list[str] = []
    new: list[str] = []
    orig_changed: list[str] = []  # H2: original binary drifted but MD representation unchanged
    obj_changed: list[str] = []   # CR-AIWS-2026-07-038 T1: hand-edited object metas — a DISTINCT
    #   signal class: routed to HAND refresh (refresh-meta "Sourceless refresh"), NEVER to
    #   refresh_wiki_source_meta.py (no artifact to re-read). Keeping them out of "modified"
    #   un-dead-ends the documented detect→refresh flow (round-3 R3-01).
    for sid, fp in current.items():
        old = old_snap.get(sid)
        if old is None:
            new.append(sid)
        elif old.get("sha1") != fp["sha1"]:
            if fp.get("path") == "__OBJECT__":
                obj_changed.append(sid)
            else:
                changed.append(sid)
        elif fp.get("orig_sha1") and old.get("orig_sha1") and fp["orig_sha1"] != old["orig_sha1"]:
            orig_changed.append(sid)

    removed = [sid for sid in old_snap if sid not in current]

    git_hits: set[str] = set()
    if ns.use_git:
        git_hits = _git_modified(root)

    git_modified = sorted(
        sid for sid, fp in current.items() if fp["path"] in git_hits
    )

    # CR-AIWS-2026-08-033 C2 (DP-033-A=b): --paths filters the REPORT, never the inventory.
    # Filtering during inventory would misclassify every out-of-scope source as "removed" and let
    # --refresh-snapshot write a truncated baseline — so the full comparison above always runs and
    # only the reported category lists (and thus the exit code) are narrowed here.
    path_prefixes: list[Path] = []
    if ns.paths:
        for _tok in ns.paths.split(","):
            _tok = _tok.strip()
            if _tok:
                _q = Path(_tok)
                path_prefixes.append((_q if _q.is_absolute() else root / _q).resolve())

    def _in_scope(sid: str) -> bool:
        if not path_prefixes:
            return True
        fp = current.get(sid) or old_snap.get(sid) or {}
        cand = fp.get("path", "")
        if cand == "__OBJECT__":
            cand = (meta_by_sid.get(sid) or {}).get("representation_locator", "")
        if not cand:
            cand_raw = (meta_by_sid.get(sid) or {}).get("artifact_locator", "")
            cand = cand_raw.strip() if isinstance(cand_raw, str) else ""
        if not cand or cand == "__OBJECT__":
            return False
        _c = Path(cand)
        try:
            cp = (_c if _c.is_absolute() else root / _c).resolve()
        except OSError:
            return False
        return any(cp == pref or pref in cp.parents for pref in path_prefixes)

    if path_prefixes:
        changed = [s for s in changed if _in_scope(s)]
        new = [s for s in new if _in_scope(s)]
        obj_changed = [s for s in obj_changed if _in_scope(s)]
        orig_changed = [s for s in orig_changed if _in_scope(s)]
        removed = [s for s in removed if _in_scope(s)]
        missing = [s for s in missing if _in_scope(s)]
        git_modified = [s for s in git_modified if _in_scope(s)]

    changed_sources: list[dict] = []
    def _record(sid: str, change_type: str, reason: str, next_action: str = "") -> None:
        fp = current.get(sid, {})
        old_fp = old_snap.get(sid, {})
        meta = meta_by_sid.get(sid, {})
        changed_sources.append({
            "source_id": sid,
            "change_type": change_type,
            "change_signal": reason,
            "artifact_locator": fp.get("path", old_fp.get("path", "")),
            "previous_artifact_locator": old_fp.get("path", ""),
            "original_source_locator": meta.get("original_source_locator", ""),
            "representation_locator": meta.get("representation_locator", meta.get("artifact_locator", "")),
            "source_representation_status": meta.get("source_representation_status", ""),
            "source_representation_caution": meta.get("source_representation_caution", ""),
            "fingerprint_old": old_fp.get("sha1", ""),
            "fingerprint_new": fp.get("sha1", ""),
            "requires_impact_evaluation": change_type != "unchanged",
            "reason": reason,
            "recommended_next_action": next_action or (
                "evaluate impact and create review/update candidate if needed"
                if change_type != "unchanged" else "no_action"
            ),
            "candidate_type": "wiki_meta_update_candidate" if change_type != "unchanged" else "",
            "runtime_boundary": "change detection is signal, not approval",
            "maintenance_model_version": "wsm_v1",
        })

    for sid in sorted(new):
        _record(sid, "added", "source appears in current inventory but not previous snapshot")
    for sid in sorted(changed):
        _record(sid, "modified", "source fingerprint changed")
    for sid in sorted(obj_changed):
        _record(sid, "object_meta_changed", "object meta content changed (hand-edit)",
                next_action="object node is hand-authored — re-validate by hand per aiws-wiki "
                            "refresh-meta (Sourceless refresh); do NOT run refresh_wiki_source_meta.py")
    for sid in sorted(orig_changed):
        _record(sid, "original_changed_needs_reconversion",
                "original binary changed but the MD representation did not — re-convert (pre_convert) then rebuild")
    for sid in sorted(removed):
        _record(sid, "deleted", "source_id existed in previous snapshot but not current inventory")
    for sid in sorted(missing):
        _record(sid, "missing", "Wiki Source Meta artifact_locator is missing/unreachable")
    for sid in sorted(git_modified):
        if sid not in {r["source_id"] for r in changed_sources}:
            _record(sid, "modified", "git reports source path modified")

    result = {
        "changed": sorted(changed),
        "object_meta_changed": sorted(obj_changed),
        "original_changed": sorted(orig_changed),
        "new": sorted(new),
        "removed": sorted(removed),
        "missing_artifacts": sorted(missing),
        "git_modified": git_modified,
        "snapshot_status": "missing_baseline" if not snapshot_existed else "ok",
        "changed_sources": changed_sources,
        "runtime_boundary": "change detection is signal, not approval",
        "recommended_next_action": "evaluate impact and create review/update candidate if needed",
        "candidate_type": "wiki_meta_update_candidate",
        "maintenance_model_version": "wsm_v1",
    }

    if ns.refresh_snapshot:
        write_text(snap_path, json.dumps(current, indent=2, ensure_ascii=False))

    if not snapshot_existed and ns.format == "text":
        print("NOTE: no baseline snapshot (.snapshot.json) found — all sources are "
              "reported as 'new'. This is expected on first run; run with "
              "--refresh-snapshot to initialize the baseline (then 'new' clears).")

    if ns.format == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        for k, v in result.items():
            if k == "changed_sources":
                print("changed_sources:")
                for rec in v:
                    print(f"  - {rec.get('source_id')} [{rec.get('change_type')}] {rec.get('reason')}")
                continue
            if isinstance(v, list):
                print(f"{k}: {', '.join(v) if v else '(none)'}")
            else:
                print(f"{k}: {v}")
    any_changed = bool(changed or obj_changed or new or removed or missing or orig_changed)
    return 0 if not any_changed else 1


if __name__ == "__main__":
    raise SystemExit(main())
