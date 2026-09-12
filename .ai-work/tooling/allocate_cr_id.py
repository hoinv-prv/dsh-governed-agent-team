#!/usr/bin/env python3
"""Cross-branch-aware CR-id allocator (month-scoped). Companion to allocate_aip_id.py.

CR ids are GLOBAL (not account-scoped) and MONTH-SCOPED — `CR-AIWS-YYYY-MM-NNN`, NNN unique
within `YYYY-MM` (AIWS_Change_Request_Spec_MVP §10). Hand-globbing the next id from a single
branch caused cross-branch collisions (CAP-001: `CR-025` was independently used on two branches).
This tool computes the next id from the MAX across, for the target month:

  - on-disk tree: `product/change_requests/**` (main, applied/, drafts/, rejected/)
  - `git log --all` CR filenames  (the cross-branch term — covers fetched branches)

…+ 1. The `git log --all` term is what makes it branch-aware (unlike a single-branch glob).

Caveat: it CANNOT prevent CROSS-MEMBER collisions on UNFETCHED branches in other clones — that
needs a central ledger (out of scope). `git fetch --all` before allocating for best coverage.

stdlib-only; Windows + POSIX safe; UTF-8.

Usage:
  py allocate_cr_id.py [--month YYYY-MM]      # default: current UTC month
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import find_ai_work_root  # noqa: E402

_PREFIX = "CR-AIWS-"


def _month_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m")


def _id_re(month: str) -> "re.Pattern[str]":
    return re.compile(r"CR-AIWS-" + re.escape(month) + r"-(\d{3,})")


def _disk_max(root: Path, month: str) -> int:
    rx = _id_re(month)
    best = 0
    d = root / "product" / "change_requests"
    if d.is_dir():
        for f in d.rglob("*.md"):
            m = rx.search(f.name)
            if m:
                best = max(best, int(m.group(1)))
    return best


def _git_max(root: Path, month: str) -> int:
    """Max CR-NNN for `month` across ALL git refs (fetched branches) — the cross-branch term."""
    rx = _id_re(month)
    best = 0
    try:
        out = subprocess.run(
            ["git", "log", "--all", "--name-only", "--pretty=format:"],
            cwd=str(root), capture_output=True, text=True, encoding="utf-8",
        )
        for m in rx.finditer(out.stdout or ""):
            best = max(best, int(m.group(1)))
    except Exception:
        pass  # no git / not a repo → disk-only (still better than nothing)
    return best


def allocate(root: Path, month: str) -> str:
    n = max(_disk_max(root, month), _git_max(root, month), 0) + 1
    return f"{_PREFIX}{month}-{n:03d}"


def main() -> int:
    p = argparse.ArgumentParser(
        description="Cross-branch-aware CR-id allocator (month-scoped; AIWS_Change_Request_Spec_MVP §10). "
                    "SCANNER, NOT A CLAIM: an id is only taken once its file exists on disk — two "
                    "consecutive calls return the SAME id. When drafting a batch, allocate once with "
                    "--count N, or write each CR file before allocating the next (CR-AIWS-2026-07-045 T3)."
    )
    p.add_argument("--month", default="", help="YYYY-MM (default: current UTC month)")
    p.add_argument("--count", type=int, default=1,
                   help="allocate N CONSECUTIVE ids in one call (batch drafting; default 1). "
                        "The ids are reserved only by you writing the files — see the scanner caveat.")
    ns = p.parse_args()
    root = find_ai_work_root(Path.cwd())
    month = ns.month.strip() or _month_now()
    if not re.fullmatch(r"\d{4}-\d{2}", month):
        raise SystemExit(f"error: --month must be YYYY-MM, got {month!r}")
    if ns.count < 1:
        raise SystemExit("error: --count must be >= 1")
    first = allocate(root, month)
    if ns.count == 1:
        print(first)
        return 0
    # N consecutive ids from the same scan (the allocator is a scanner — see docstring).
    stem, _, num = first.rpartition("-")
    start = int(num)
    for i in range(ns.count):
        print(f"{stem}-{start + i:03d}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
