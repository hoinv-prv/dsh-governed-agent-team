#!/usr/bin/env python3
"""Build the PRESET AIWS wiki — the shipped `aiws` namespace a downstream project can query
right after install: `index.aiws.jsonl` + `relations.aiws.jsonl` (CR-AIWS-2026-08-064 C1).

Source = the curated AIWS metas (`aiws_meta/`, shipped as `payload/aiws_wiki/`, CR-040), whose
`artifact_locator` already points at the install layout (`.ai-work/truth/canonical/**`,
`.ai-work/preset_knowledge/**` — rebased at package build, CR-052 C7). This tool is an
ORCHESTRATOR: it never builds an index or an edge itself — it delegates to
`build_wiki_source_index.py` (`--scope aiws`) and `build_relations.py --namespace aiws`
(Rule 6: one builder per projection).

Two modes:

  # (a) inside an installed project — install Step 4 / quick-install / upgrade / manual rebuild
  py .ai-work/tooling/build_preset_wiki.py --target <project_root>
      → <target>/.ai-work/wiki_sources/index.aiws.jsonl + relations.aiws.jsonl
        (from <target>/.ai-work/wiki_sources/aiws_meta/)

  # (b) at package build — pre-build from the rebased payload so install can just COPY
  py .ai-work/tooling/build_preset_wiki.py --payload <pkg>/payload/aiws_wiki --out-dir <pkg>/payload/aiws_wiki_index
      → stages <tmp>/.ai-work/wiki_sources/aiws_meta/ := payload (copy), builds with
        project_root=<tmp> so meta_locator = __PROJECT_ROOT__/.ai-work/wiki_sources/aiws_meta/…
        (portable), copies the two files into --out-dir, removes the staging tree.

Guards (never silent):
  - `--target` on a repo with `wiki_single_index: true` (the AIWS source repo, CR-052) → rc=2.
    That repo keeps ONE index.jsonl / relations.jsonl; the preset exists only downstream.
  - `aiws_meta/` (or the payload dir) missing / without *.md → rc=2, no empty files written.
  - a delegated builder failing → rc propagated, partial output reported.
Prints entry + edge counts (+ broken-ref count passed through from build_relations) and appends a
`preset_wiki_built` maintenance-log entry in --target mode (projection maintenance, not promotion).
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (  # noqa: E402
    PROJECT_PROFILE_SCHEMA_VERSION,
    append_maintenance_log,
    portable_locator,
    read_project_config,
    read_text,
    write_meta_if_changed,
)

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:  # noqa: BLE001
    pass

TOOLING = Path(__file__).resolve().parent
INDEX_NAME = "index.aiws.jsonl"
RELATIONS_NAME = "relations.aiws.jsonl"


def _count_lines(p: Path) -> int:
    if not p.exists():
        return 0
    return sum(1 for ln in p.read_text(encoding="utf-8", errors="replace").splitlines() if ln.strip())


def _run(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *args], cwd=str(cwd), capture_output=True,
                          text=True, encoding="utf-8", errors="replace")


def build_in_project(project_root: Path, *, tooling: Path = TOOLING,
                     write_log: bool = True) -> int:
    """Build index.aiws.jsonl + relations.aiws.jsonl inside `project_root` from its aiws_meta/.
    Returns rc (0 ok · 2 refused / precondition · builder rc otherwise)."""
    project_root = project_root.resolve()
    ai_work = project_root / ".ai-work"
    ws = ai_work / "wiki_sources"
    aiws_meta = ws / "aiws_meta"

    if read_project_config(ai_work)["wiki_single_index"]:  # CR-128 C3: one reader
        print("refuse: this project declares wiki_single_index: true (the AIWS source repo, "
              "CR-AIWS-2026-08-052) — it keeps ONE index.jsonl / relations.jsonl and ships no "
              "index.aiws.jsonl / relations.aiws.jsonl in-repo. Use build_wiki_source_index.py / "
              "build_relations.py as usual.", file=sys.stderr)
        return 2
    if not aiws_meta.is_dir() or not any(aiws_meta.rglob("*.md")):
        print(f"refuse: no AIWS metas under {aiws_meta} — nothing to build (install/copy "
              f"payload/aiws_wiki/ first; not writing empty preset files).", file=sys.stderr)
        return 2

    idx_out = ws / INDEX_NAME
    rel_out = ws / RELATIONS_NAME

    r = _run([str(tooling / "build_wiki_source_index.py"), "--scope", "aiws"], project_root)
    if r.returncode != 0:
        print(r.stdout, end="")
        print(r.stderr, end="", file=sys.stderr)
        print(f"error: index build failed rc={r.returncode}", file=sys.stderr)
        return r.returncode
    n_idx = _count_lines(idx_out)

    r = _run([str(tooling / "build_relations.py"), "--namespace", "aiws", "--quiet"], project_root)
    if r.returncode != 0:
        print(r.stdout, end="")
        print(r.stderr, end="", file=sys.stderr)
        print(f"error: relations build failed rc={r.returncode}", file=sys.stderr)
        return r.returncode
    n_rel = _count_lines(rel_out)
    broken = ""
    for ln in (r.stdout + r.stderr).splitlines():
        if "broken refs:" in ln:
            broken = ln[ln.index("(") :] if "(" in ln else ln
            break

    print(f"preset wiki built → {idx_out}  ({n_idx} entries)")
    print(f"                    {rel_out}  ({n_rel} edges) {broken}".rstrip())
    if write_log:
        try:
            _write_log(ai_work, idx_out, rel_out, n_idx, n_rel)
        except Exception as e:  # noqa: BLE001 — log is best-effort, never blocks the build
            print(f"note: maintenance_log not written ({e})", file=sys.stderr)
    return 0


def build_from_payload(payload: Path, out_dir: Path, *, tooling: Path = TOOLING) -> int:
    """Pre-build the preset from an already-rebased payload/aiws_wiki tree (package build)."""
    payload = payload.resolve()
    if not payload.is_dir() or not any(payload.rglob("*.md")):
        print(f"refuse: payload dir {payload} missing or holds no metas", file=sys.stderr)
        return 2
    staging = Path(tempfile.mkdtemp(prefix="aiws-preset-"))
    try:
        ws = staging / ".ai-work" / "wiki_sources"
        shutil.copytree(payload, ws / "aiws_meta")
        # Schema-valid minimal profile (CR-AIWS-2026-08-128 C1): single-system, dual-index.
        # It must satisfy the schema the single reader now enforces - a one-key stub would be
        # rejected as unparseable, and staging would fail for the wrong reason.
        _stage_profile = (staging / ".ai-work" / "project_profile.yml")
        _stage_profile.write_text(
            f"# AIWS:BEGIN project_profile v{PROJECT_PROFILE_SCHEMA_VERSION}\n"
            f"schema_version: {PROJECT_PROFILE_SCHEMA_VERSION}\n"
            "multi_system: false\n"
            "wiki_single_index: false\n"
            "# AIWS:END\n", encoding="utf-8", newline="\n")
        rc = build_in_project(staging, tooling=tooling, write_log=False)
        if rc != 0:
            return rc
        out_dir.mkdir(parents=True, exist_ok=True)
        for name in (INDEX_NAME, RELATIONS_NAME):
            shutil.copyfile(ws / name, out_dir / name)
        print(f"pre-built preset copied → {out_dir}")
        return 0
    finally:
        shutil.rmtree(staging, ignore_errors=True)



def sync_metas_from_payload(payload: Path, target_root: Path) -> "tuple[int, int, int]":
    """PRECISE APPLY of the shipped aiws_meta bundle — CR-AIWS-2026-08-073 C1/C2.

    Returns (added, updated, unchanged).

    WHY NOT rmtree-and-copy. `upgrade.md` step 7b used to say "replace the bundle". Taken
    literally that rewrites every meta, so a run whose real delta is a few dozen files reports the
    whole bundle as changed — the payload ships LF, a CRLF tree then shows every file dirty and the
    genuine diff is buried (IR-2026-08-15 F5, measured downstream: 189 files touched, 44 real).
    Step 5 already promises precise apply for every other section; 7b was the odd one out.

    Comparison is delegated to `write_meta_if_changed`, which compares DECODED TEXT (so a BOM or an
    EOL flavour alone never counts as a change) and additionally neutralises an `updated_at`-only
    delta. Reusing it keeps one definition of "changed" instead of a second, subtly different one.

    Never deletes: a meta the project added under aiws_meta/ is left alone. Removal of a retired
    meta stays a HUMAN decision, same as everywhere else in upgrade.
    """
    payload = payload.resolve()
    dest_root = (target_root / ".ai-work" / "wiki_sources" / "aiws_meta").resolve()
    added = updated = unchanged = 0
    for src in sorted(payload.rglob("*.md")):
        rel = src.relative_to(payload)
        dst = dest_root / rel
        if not dst.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(read_text(src), encoding="utf-8")
            added += 1
            continue
        if write_meta_if_changed(dst, read_text(src)):
            updated += 1
        else:
            unchanged += 1
    print(f"aiws_meta precise apply → {added} added · {updated} updated · {unchanged} unchanged "
          f"(CR-AIWS-2026-08-073 C2; untouched files keep their bytes)")
    return added, updated, unchanged


def _write_log(ai_work: Path, idx_out: Path, rel_out: Path, n_idx: int, n_rel: int) -> None:
    from datetime import datetime, timezone

    log_path = ai_work / "wiki_sources" / "maintenance_log.jsonl"
    root = ai_work.parent
    now = datetime.now(timezone.utc)
    entry = {
        "log_id": f"WSMLOG-{now.strftime('%Y%m%d%H%M%S')}-PRESET-WIKI",
        "timestamp": now.isoformat(),
        "maintenance_model_version": "wsm_v1",
        "action": "preset_wiki_built",
        "source_id": "(aiws-preset-projection)",
        "target_artifact": portable_locator(idx_out, root),
        "old_locator": "",
        "new_locator": portable_locator(rel_out, root),
        "change_summary": f"Built AIWS preset wiki: {n_idx} index entries, {n_rel} edges "
                          f"({INDEX_NAME} + {RELATIONS_NAME}).",
        "reason": "AIWS preset wiki build (CR-AIWS-2026-08-064)",
        "impact_level": "unknown",
        "review_decision": "projection_rebuilt",
        "applied_by": "tool:build_preset_wiki.py",
        "rollback_hint": f"Re-run build_preset_wiki.py --target . (or restore {INDEX_NAME}/{RELATIONS_NAME} from the package).",
        "runtime_boundary": "preset build is projection maintenance of the aiws namespace, not Knowledge Hub promotion",
    }
    append_maintenance_log(log_path, entry)


def main() -> int:
    p = argparse.ArgumentParser(description="Build the preset AIWS wiki (index.aiws.jsonl + relations.aiws.jsonl)")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--target", help="installed project root (builds in-place from its aiws_meta/)")
    g.add_argument("--payload", help="package payload/aiws_wiki dir (pre-build; needs --out-dir)")
    p.add_argument("--out-dir", help="with --payload: where to write the two pre-built files")
    p.add_argument("--sync-metas", metavar="PAYLOAD_AIWS_WIKI",
                   help="with --target: PRECISE-APPLY the shipped aiws_meta bundle into the "
                        "target before building (CR-AIWS-2026-08-073 C2) — writes only metas "
                        "whose content differs; never rmtree-and-copy, never deletes")
    ns = p.parse_args()

    if ns.target:
        if ns.sync_metas:
            sync_metas_from_payload(Path(ns.sync_metas), Path(ns.target))
        return build_in_project(Path(ns.target))
    if ns.sync_metas:
        p.error("--sync-metas is for --target (an installed tree), not --payload")
    if not ns.out_dir:
        p.error("--payload requires --out-dir")
    return build_from_payload(Path(ns.payload), Path(ns.out_dir))


if __name__ == "__main__":
    raise SystemExit(main())
