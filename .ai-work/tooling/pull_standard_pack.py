#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""pull_standard_pack.py — snapshot a Standard Pack from OUTSIDE the repo into `product/standard_pack/`.

Spec: `Standard_Pack_Contract_Spec_MVP` §10 (the rule-8 exception), §2.1 (`pack.yml` carries
`pack_id`/`pack_version`), §8.1 (the pack tree is owned by the pack and replaced wholesale),
§9 (three version layers — the pack layer is what `PACK_SOURCE.md` records).

    py .ai-work/tooling/pull_standard_pack.py --from <dir> [--ref <commit>]
                                              [--dest product/standard_pack] [--dry-run]

Why this tool exists and why it lints
-------------------------------------
Rule 8 of this repo says every canonical change under `product/` needs an approved CR.
`product/standard_pack/` is the tường minh exception (§10): its content is pack-owned and enters
the repo through exactly ONE door — this tool — which records provenance in `PACK_SOURCE.md`.
The price of dropping the human gate is stated in the same section: *không có người gác thì phải
có máy gác*. So the lint is not a convenience here, it is the substitute for the review round:

    lint FIRST, write SECOND. A red lint means rc=2 and NOT ONE BYTE written — the dest is not
    created, not emptied, not touched. A half-pulled pack is worse than no pull (the same
    reasoning §9.3 applies to install).

The snapshot is a REPLACEMENT, not a merge (§8.1): a file that exists in dest but no longer
exists in the source is deleted, because a pack tree that accumulates the union of every version
it has ever had is not a snapshot of anything.

Exit codes
  0  pulled (or planned, under --dry-run)
  1  usage / unsafe request — source is not a directory, dest is not a directory, dest is not a
     pack snapshot, source and dest overlap. Nothing written.
  2  lint of the SOURCE reported errors. Nothing written; the findings are printed.

Deletion safety (this tool removes files, so the guards are explicit):
  * every path removed is verified to resolve INSIDE dest before `unlink`;
  * symlinks are never followed and never copied — a symlink inside the source cannot make this
    tool write or delete outside dest;
  * dest must be either absent, empty, or an existing pack snapshot (it carries `pack.yml` or
    `PACK_SOURCE.md`). Pointing `--dest` at an arbitrary populated directory is refused, not
    emptied;
  * `--dry-run` prints the exact add/update/delete plan and returns without touching the disk.

Python 3.8+, stdlib only. The pack format is read through `lint_standard_pack` (import, not
subprocess): the linter's findings are needed as DATA before deciding to write, and
`tooling_authoring_conventions` Rule 2 forbids a second implementation of a reader that already
exists next door.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _common import (  # noqa: E402  (also forces UTF-8 stdout — Windows cp932)
    SEV_ERROR,
    find_ai_work_root,
    now_utc_iso,
    portable_locator,
    render_report,
    write_text,
)
from lint_standard_pack import (  # noqa: E402
    YamlSubsetError,
    detect_aiws_version,
    lint_pack,
    parse_yaml,
)

#: Written by THIS tool at the dest root. Never copied in from the source: a pull from a
#: directory that is itself a previous snapshot must re-derive its own provenance, not inherit
#: someone else's.
PACK_SOURCE_NAME = "PACK_SOURCE.md"

#: Directories whose content is never part of a pack (VCS metadata, editor/tool droppings).
SKIP_DIRS = frozenset({".git", ".hg", ".svn", "__pycache__", ".idea", ".vscode", ".pytest_cache"})

#: Files that are never part of a pack.
SKIP_NAMES = frozenset({".DS_Store", "Thumbs.db", "desktop.ini"})

#: Marks a dest directory as an existing pack snapshot that may be replaced wholesale.
SNAPSHOT_MARKERS = ("pack.yml", PACK_SOURCE_NAME)


# ---------------------------------------------------------------- filesystem helpers

def _is_inside(child: Path, parent: Path) -> bool:
    """True when `child` resolves to `parent` itself or something under it."""
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except (ValueError, OSError):
        return False


def iter_pack_files(root: Path):
    """Relative POSIX paths of every file that belongs to the pack, sorted.

    Rule 12 (`tooling_authoring_conventions`): the sort key is the explicit relative POSIX path,
    not the default ordering of `Path`, because this list decides the copy/delete plan and the
    default ordering is case-folded on Windows and case-sensitive on POSIX.
    """
    out = []
    root_res = root.resolve()
    for path in root.rglob("*"):
        try:
            rel = path.relative_to(root)
        except ValueError:                       # pragma: no cover - rglob always yields children
            continue
        parts = rel.parts
        if any(part in SKIP_DIRS for part in parts):
            continue
        if path.is_symlink():                    # never follow, never copy (see module docstring)
            continue
        if not path.is_file():
            continue
        if path.name in SKIP_NAMES:
            continue
        rel_posix = rel.as_posix()
        if rel_posix == PACK_SOURCE_NAME:
            continue
        # Paranoia, cheap: a path that does not resolve inside root is not part of this pack.
        if not _is_inside(path, root_res):
            continue
        out.append(rel_posix)
    out.sort()
    return out


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read_bytes(path: Path) -> bytes:
    return path.read_bytes()


def _prune_empty_dirs(dest: Path) -> list:
    """Remove directories left empty inside dest after a delete. Returns the removed ones.

    Bottom-up, and every candidate is re-checked to be INSIDE dest before `rmdir`. dest itself is
    never removed even when the pull leaves it empty (it cannot: `PACK_SOURCE.md` is written).
    """
    removed = []
    dirs = [p for p in dest.rglob("*") if p.is_dir() and not p.is_symlink()]
    dirs.sort(key=lambda p: len(p.relative_to(dest).parts), reverse=True)
    for d in dirs:
        if not _is_inside(d, dest) or d.resolve() == dest.resolve():
            continue
        try:
            next(d.iterdir())
        except StopIteration:
            d.rmdir()
            removed.append(d.relative_to(dest).as_posix())
        except OSError:                          # pragma: no cover - unreadable dir
            continue
    return removed


# ---------------------------------------------------------------- PACK_SOURCE.md

def render_pack_source(pack_id: str, pack_version: str, source: str, ref: str, pulled_at: str,
                       manifest) -> str:
    """The provenance document §10 requires: source, commit, moment, pack_id, version.

    `manifest` is a list of `(rel_path, sha256)` for exactly the bytes written into dest. The
    hashes are of the RAW bytes as pulled: this tool copies bytes verbatim (Rule 11 — a writer
    does not change a file's eol), so a later drift check compares like with like.
    """
    lines = [
        "---",
        "artifact_type: standard_pack_source",
        f"pack_id: {pack_id}",
        f"pack_version: {pack_version}",
        f"source: {source}",
        f"ref: {ref}",                      # empty string = the pull declared no commit/tag
        f"pulled_at: {pulled_at}",
        "pulled_by: .ai-work/tooling/pull_standard_pack.py",
        f"file_count: {len(manifest)}",
        "---",
        "",
        f"# PACK_SOURCE — {pack_id} {pack_version}",
        "",
        "Snapshot provenance, written by `pull_standard_pack.py` (Standard_Pack_Contract_Spec_MVP",
        "§10). **Do not edit this tree by hand and do not edit this file**: every pull replaces the",
        "whole directory, so a hand edit here is lost at the next pull and, worse, is invisible",
        "until then. Change the pack at its source and pull again.",
        "",
        f"- **source:** `{source}`",
        f"- **ref:** {('`' + ref + '`') if ref else '_(none declared)_'}",
        f"- **pulled_at:** {pulled_at} (UTC)",
        f"- **pack_id / pack_version:** `{pack_id}` / `{pack_version}`",
        "",
        "The pull ran `lint_standard_pack.py` against the source BEFORE writing anything; a red",
        "lint refuses the pull (§10: the machine gate is what stands in for the CR review round).",
        "",
        f"## Files ({len(manifest)})",
        "",
        "sha256 of the raw bytes written here.",
        "",
        "| file | sha256 |",
        "|---|---|",
    ]
    for rel, digest in manifest:
        lines.append(f"| `{rel}` | `{digest}` |")
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------- the pull

class PullError(Exception):
    """A refusal that is a usage/safety problem rather than a lint failure (rc=1)."""


def plan_pull(src: Path, dest: Path):
    """(added, updated, unchanged, deleted) — relative POSIX paths, computed, nothing written."""
    src_files = iter_pack_files(src)
    dest_files = set(iter_pack_files(dest)) if dest.is_dir() else set()

    added, updated, unchanged = [], [], []
    for rel in src_files:
        if rel not in dest_files:
            added.append(rel)
        elif _read_bytes(src / rel) != _read_bytes(dest / rel):
            updated.append(rel)
        else:
            unchanged.append(rel)
    deleted = sorted(dest_files - set(src_files))
    return added, updated, unchanged, deleted


def check_dest(dest: Path, src: Path) -> None:
    """Every reason to refuse BEFORE a byte moves. Raises PullError."""
    if dest.exists() and not dest.is_dir():
        raise PullError(f"--dest {dest} exists and is not a directory")
    if dest.is_symlink():
        raise PullError(f"--dest {dest} is a symlink — refusing to write through it")
    if dest.exists() and src.resolve() == dest.resolve():
        raise PullError("--from and --dest are the same directory")
    if dest.exists() and _is_inside(src, dest):
        raise PullError(f"--from {src} lies INSIDE --dest {dest} — the replace would delete the "
                        f"source it is reading")
    if _is_inside(dest, src):
        raise PullError(f"--dest {dest} lies INSIDE --from {src} — a pull must not write into the "
                        f"pack it is reading")
    if dest.is_dir():
        existing = list(iter_pack_files(dest))
        if existing and not any((dest / m).is_file() for m in SNAPSHOT_MARKERS):
            raise PullError(
                f"--dest {dest} is a non-empty directory that carries neither "
                f"{' nor '.join(SNAPSHOT_MARKERS)} — it does not look like a pack snapshot, and "
                f"this tool would REPLACE its contents. Refusing; point --dest at the pack "
                f"snapshot directory or empty it deliberately.")


def read_pack_identity(src: Path):
    """(pack_id, pack_version) from the SOURCE `pack.yml` — never invented here (§2.1)."""
    path = src / "pack.yml"
    try:
        data = parse_yaml(path.read_text(encoding="utf-8", errors="replace"))
    except (YamlSubsetError, OSError) as exc:    # pragma: no cover - lint already refused this
        raise PullError(f"cannot read {path}: {exc}")
    pack_id = str(data.get("pack_id") or "").strip()
    pack_version = str(data.get("pack_version") or "").strip()
    if not pack_id or not pack_version:         # pragma: no cover - lint already refused this
        raise PullError("pack.yml is missing pack_id/pack_version (should have been caught by "
                        "lint — refusing to write a snapshot with no identity)")
    return pack_id, pack_version


def apply_pull(src: Path, dest: Path, added, updated, deleted):
    """Copy/delete, then prune. Returns the list of removed empty dirs."""
    for rel in deleted:
        target = dest / rel
        if not _is_inside(target, dest):         # pragma: no cover - guarded twice on purpose
            raise PullError(f"refusing to delete {target}: outside --dest {dest}")
        if target.is_file() or target.is_symlink():
            target.unlink()
    dest.mkdir(parents=True, exist_ok=True)
    for rel in list(added) + list(updated):
        target = dest / rel
        if not _is_inside(target.parent if target.parent.exists() else dest, dest):
            raise PullError(f"refusing to write {target}: outside --dest {dest}")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(_read_bytes(src / rel))   # bytes verbatim: eol is the source's (Rule 11)
    return _prune_empty_dirs(dest)


# ---------------------------------------------------------------- CLI

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Snapshot a Standard Pack into product/standard_pack/ (lint-gated, §10).")
    ap.add_argument("--from", dest="src", required=True,
                    help="path to the pack root to pull FROM (the dir holding pack.yml)")
    ap.add_argument("--ref", default="",
                    help="commit/tag of the source recorded in PACK_SOURCE.md (not resolved by "
                         "this tool — it is provenance the caller declares)")
    ap.add_argument("--dest", default="product/standard_pack",
                    help="destination pack tree (default: product/standard_pack, relative to "
                         "--project-root)")
    ap.add_argument("--dry-run", action="store_true",
                    help="print the add/update/delete plan and exit without touching the disk")
    ap.add_argument("--format", choices=("text", "json"), default="text", help="output format")
    ap.add_argument("--project-root", default="",
                    help="AIWS project root (default: walk up from cwd) — resolves a relative "
                         "--dest and the AIWS version used by the lint")
    ap.add_argument("--aiws-version", default="",
                    help="override the AIWS version used by the lint's aiws_min_version check")
    ns = ap.parse_args(argv)

    if ns.project_root:
        project_root = Path(ns.project_root).resolve()
    else:
        try:
            project_root = find_ai_work_root(Path.cwd())
        except SystemExit:
            project_root = Path.cwd()

    src = Path(ns.src)
    dest = Path(ns.dest)
    if not dest.is_absolute():
        dest = project_root / dest

    def fail(msg: str) -> int:
        if ns.format == "json":
            print(json.dumps({"status": "refused", "error": msg,
                              "source": src.as_posix(), "dest": dest.as_posix(),
                              "dry_run": bool(ns.dry_run)}, ensure_ascii=False, indent=2))
        else:
            print(f"pull refused: {msg}")
        return 1

    if not src.is_dir():
        return fail(f"--from {src} is not a directory")

    # ---- gate: lint the SOURCE before anything else looks at dest -------------------------
    aiws_version = (ns.aiws_version or "").strip() or detect_aiws_version(project_root)
    report = lint_pack(src, project_root, aiws_version)
    errors = [f for f in report.findings if f.severity == SEV_ERROR]
    if errors:
        if ns.format == "json":
            print(json.dumps({
                "status": "lint_failed",
                "source": src.as_posix(),
                "dest": dest.as_posix(),
                "dry_run": bool(ns.dry_run),
                "lint": json.loads(render_report(report, "json")),
            }, ensure_ascii=False, indent=2))
        else:
            print(render_report(report, "text"))
            print(f"pull refused: lint reported {len(errors)} error(s) in {src} — "
                  f"nothing was written to {dest} (Standard_Pack_Contract_Spec_MVP §10)")
        return 2

    try:
        check_dest(dest, src)
        pack_id, pack_version = read_pack_identity(src)
        added, updated, unchanged, deleted = plan_pull(src, dest)
    except PullError as exc:
        return fail(str(exc))

    source_locator = portable_locator(src.resolve(), project_root)
    payload = {
        "status": "planned" if ns.dry_run else "pulled",
        "pack_id": pack_id,
        "pack_version": pack_version,
        "source": source_locator,
        "ref": ns.ref,
        "dest": dest.as_posix(),
        "dry_run": bool(ns.dry_run),
        "added": added,
        "updated": updated,
        "unchanged": unchanged,
        "deleted": deleted,
        "file_count": len(added) + len(updated) + len(unchanged),
    }

    if ns.dry_run:
        if ns.format == "json":
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(f"DRY RUN — would pull {pack_id} {pack_version} from {source_locator} "
                  f"into {dest} (nothing written)")
            for rel in added:
                print(f"  + {rel}")
            for rel in updated:
                print(f"  ~ {rel}")
            for rel in deleted:
                print(f"  - {rel}")
            print(f"  = {len(unchanged)} unchanged, {PACK_SOURCE_NAME} would be rewritten")
        return 0

    try:
        pruned = apply_pull(src, dest, added, updated, deleted)
    except (PullError, OSError) as exc:
        return fail(f"write failed after the lint gate passed: {exc}")

    manifest = [(rel, sha256_bytes(_read_bytes(dest / rel))) for rel in iter_pack_files(dest)]
    write_text(dest / PACK_SOURCE_NAME,
               render_pack_source(pack_id, pack_version, source_locator, ns.ref, now_utc_iso(),
                                  manifest))

    payload["pruned_dirs"] = pruned
    payload["pack_source"] = (dest / PACK_SOURCE_NAME).as_posix()
    payload["file_count"] = len(manifest)
    if ns.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"pulled {pack_id} {pack_version} from {source_locator} into {dest}")
        for rel in added:
            print(f"  + {rel}")
        for rel in updated:
            print(f"  ~ {rel}")
        for rel in deleted:
            print(f"  - {rel}")
        print(f"  = {len(unchanged)} unchanged · {len(manifest)} file(s) now in the snapshot · "
              f"wrote {PACK_SOURCE_NAME}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
