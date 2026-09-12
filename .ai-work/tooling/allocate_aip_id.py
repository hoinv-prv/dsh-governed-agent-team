#!/usr/bin/env python3
"""Per-account AIP-id allocator — CR-AIWS-2026-06-015 v2.

Supersedes the v1 `id_claims.jsonl` ledger + `.alloc.lock` (both RETIRED). Member identity
and the per-member id counter now live in ONE local, gitignored file:

    .ai-work/account_info.yaml
        account_id: <id>
        next_aip_id:
          exec: N
          plan: N
          local: N

Allocation:
    n = max(next_aip_id[kind], _disk_max(.ai-work/aip/<account_id>/<kind>/) + 1,
            _git_max(git log --all, same account+kind) + 1)
    -> print AIP-<KIND>-NNN  and bump next_aip_id[kind] := n + 1

The disk-max term is a **fresh-clone safety**: because account_info.yaml is gitignored, a fresh
clone starts without the counter; seeding from the member's own committed AIPs means a re-clone
never re-issues a number the member already committed. The git-max term (CR-AIWS-2026-06-037 C1)
is a **cross-branch safety**: `_disk_max` only sees the current branch's working tree, so an id
committed on a not-checked-out branch / concurrent worktree is invisible to it — `git log --all`
catches it (graceful fallback to disk+counter if git is unavailable).

ID format is UNCHANGED (`AIP-<KIND>-NNN`, NO account prefix). The per-account FOLDER is the
namespace, so the same NNN may legitimately recur across members — duplicate-id detection is
ACCOUNT-SCOPED (see build_aip_index.py). New AIPs are written by aiws-aip create under
`.ai-work/aip/<account_id>/<kind>/`; legacy flat `.ai-work/aip/<kind>/` AIPs are untouched
(only-new-AIPs).

The counter increments on allocate (NOT on file-write): a cancelled draft just leaves a gap —
explicitly accepted (no system impact). No lock is needed — the counter is per-member/per-install,
so there is no cross-member contention; the only residual race is one member allocating twice in
the same instant (at worst a gap). run_aip._resolve_aip's post-hoc collision guard stays as a net.

Precondition: account_info.yaml exists. If missing, allocation STOPS and tells the human to set it
— the install-time set + prompt-on-create-if-missing flow is CR-AIWS-2026-06-016 (separate). The
allocator NEVER invents an account_id.

stdlib-only; Windows (NTFS) + POSIX safe. UTF-8.

Usage:
  py allocate_aip_id.py --kind exec [--slug short-slug] [--account-dir]
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (  # noqa: E402
    find_ai_work_root,
    parse_frontmatter,
    read_text,
    write_text,
)

KIND_DIR = {"exec": "exec", "plan": "plans", "local": "local"}
ACCOUNT_INFO_NAME = "account_info.yaml"
_ID_RE = re.compile(r"^AIP-([A-Z]+)-(\d+)$")
_NEXT_BLOCK_RE = re.compile(r"^next_aip_id\s*:\s*$")


def _prefix(kind: str) -> str:
    return f"AIP-{kind.upper()}-"


def _account_info_path(ai_work: Path) -> Path:
    return ai_work / ACCOUNT_INFO_NAME


def _read_account_info(ai_work: Path) -> tuple[str, dict, str]:
    """Return (account_id, next_aip_id_map, raw_text). Raise SystemExit if missing/invalid."""
    p = _account_info_path(ai_work)
    if not p.is_file():
        raise SystemExit(
            f"error: {p} not found.\n"
            f"AIP id allocation requires a local account_info.yaml carrying 'account_id' + "
            f"'next_aip_id'. Set it first (it is gitignored, one per install). The install-time "
            f"set / prompt-on-create flow is CR-AIWS-2026-06-016. Never invent an account_id."
        )
    raw = read_text(p)
    # Reuse the frontmatter parser (handles comments + the nested next_aip_id map) by wrapping.
    meta, _ = parse_frontmatter("---\n" + raw.strip("\n") + "\n---\n")
    account_id = str(meta.get("account_id", "")).strip()
    if not account_id:
        raise SystemExit(f"error: {p} is missing 'account_id'.")
    nxt = meta.get("next_aip_id")
    if not isinstance(nxt, dict):
        nxt = {}
    return account_id, nxt, raw


def _disk_max(ai_work: Path, account_id: str, kind: str) -> int:
    """Highest AIP-<KIND>-NNN number under .ai-work/aip/<account_id>/<KIND_DIR>/ (recursive).

    Matched by artifact_id PREFIX (not directory), so sub-folders (e.g. done/) still count.
    """
    pref = _prefix(kind)
    d = ai_work / "aip" / account_id / KIND_DIR[kind]
    if not d.is_dir():
        return 0
    best = 0
    for f in d.rglob("*.md"):
        try:
            meta, _ = parse_frontmatter(read_text(f))
        except Exception:
            continue
        aid = str(meta.get("artifact_id", ""))
        if aid.startswith(pref):
            # leading digits after the prefix; tolerate a `-slug` suffix (CR-037 C1 — the old
            # `^AIP-KIND-\d+$` end-anchor missed slug'd artifact_ids like AIP-EXEC-133-foo → undercount).
            m = re.match(rf"^{re.escape(pref)}(\d+)", aid)
            if m:
                best = max(best, int(m.group(1)))
    return best


def _git_max(ai_work: Path, account_id: str, kind: str) -> int:
    """Highest AIP-<KIND>-NNN committed on ANY branch (`git log --all`), scoped to the
    account's kind dir. Cross-branch safety (CR-AIWS-2026-06-037 C1): `_disk_max` only sees
    the CURRENT branch's working tree, so an id committed on a not-checked-out branch (or by
    a concurrent worktree) is invisible to it — that gap caused a concurrent-id collision.
    Returns 0 if git is unavailable / not a repo (graceful fallback to disk+counter)."""
    pref = _prefix(kind)
    needle = f"aip/{account_id}/{KIND_DIR[kind]}/{pref}"  # git uses forward slashes
    try:
        out = subprocess.run(
            ["git", "-C", str(ai_work.parent), "log", "--all", "--pretty=format:", "--name-only"],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30,
        ).stdout
    except Exception:
        return 0
    best = 0
    for line in out.splitlines():
        idx = line.find(needle)
        if idx == -1:
            continue
        base = line[idx:].rsplit("/", 1)[-1]  # AIP-<KIND>-NNN-...md
        m = re.match(rf"^{re.escape(pref)}(\d+)", base)
        if m:
            best = max(best, int(m.group(1)))
    return best


def _bump_counter(raw: str, kind: str, new_val: int) -> str:
    """Surgically set the `  <kind>: N` line under `next_aip_id:` to new_val, preserving
    comments + any other fields. Inserts the kind line (or the whole block) if absent."""
    lines = raw.split("\n")
    kind_re = re.compile(rf"^(\s+){re.escape(kind)}(\s*:\s*)(\d+)(.*)$")
    in_block = False
    block_indent = -1
    for idx, line in enumerate(lines):
        if not in_block:
            if _NEXT_BLOCK_RE.match(line):
                in_block = True
                block_indent = len(line) - len(line.lstrip())
            continue
        if line.strip() == "":
            continue
        indent = len(line) - len(line.lstrip())
        if indent <= block_indent:  # block ended without the kind line -> insert before this line
            lines.insert(idx, f"{' ' * (block_indent + 2)}{kind}: {new_val}")
            return "\n".join(lines)
        m = kind_re.match(line)
        if m:
            lines[idx] = f"{m.group(1)}{kind}{m.group(2)}{new_val}{m.group(4)}"
            return "\n".join(lines)
    # reached EOF
    if in_block:
        lines.append(f"  {kind}: {new_val}")
    else:
        lines.append("next_aip_id:")
        lines.append(f"  {kind}: {new_val}")
    return "\n".join(lines)


def _width(n: int) -> int:
    return max(3, len(str(n)))


def allocate(ai_work: Path, kind: str, slug: str = "") -> tuple[str, str]:
    """Allocate the next id for `kind`, bump the counter, return (aip_id, account_id)."""
    if kind not in KIND_DIR:
        raise SystemExit(f"error: --kind must be one of {sorted(KIND_DIR)}")
    account_id, nxt, raw = _read_account_info(ai_work)
    try:
        counter = int(str(nxt.get(kind, "0")).strip() or "0")
    except ValueError:
        counter = 0
    n = max(counter, _disk_max(ai_work, account_id, kind) + 1, _git_max(ai_work, account_id, kind) + 1)
    if n < 1:
        n = 1
    aip_id = f"{_prefix(kind)}{n:0{_width(n)}d}"
    write_text(_account_info_path(ai_work), _bump_counter(raw, kind, n + 1))
    return aip_id, account_id


def main() -> int:
    p = argparse.ArgumentParser(description="Per-account AIP-id allocator (CR-015 v2)")
    p.add_argument("--kind", choices=sorted(KIND_DIR), required=True,
                   help="AIP kind to allocate")
    p.add_argument("--slug", default="", help="optional slug (accepted for back-compat; unused)")
    p.add_argument("--account-dir", action="store_true",
                   help="also print the target AIP directory (.ai-work/aip/<account_id>/<kind>)")
    ns = p.parse_args()
    ai_work = find_ai_work_root(Path.cwd()) / ".ai-work"
    aip_id, account_id = allocate(ai_work, ns.kind, ns.slug)
    print(aip_id)
    if ns.account_dir:
        print(f".ai-work/aip/{account_id}/{KIND_DIR[ns.kind]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
