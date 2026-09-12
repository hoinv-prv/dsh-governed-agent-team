#!/usr/bin/env python3
"""Print the Operating Memory L2 digest on stdout (CR-AIWS-2026-08-029).

The second read path. The first one is `aiws-aip run start|resume|step`, which folds the same
digest into the Active Step Context — that is a TOOL, so wiring it in was easy. `aiws-aip create`
is a SKILL: a doc an AI reads and then runs commands from, with no function to hook. This CLI is
the hook.

Both paths call one helper (`_common.operating_memory_digest`). Re-implementing the display rules
— ordering, age label, budget threshold, the "not a rule" caveat — would give the project two
copies that drift, which is the failure `meta_roots()` exists to prevent.

Default slice = the four PLANNING groups (DP-029-A = a): `cost_sizing` · `required_order` ·
`where_to_look` · `rejected_option`. Those are the ones a create-time decision actually uses;
`tool_gotcha` / `verification_trap` / `recurring_shape` pay off while TYPING, and the `run` path
already carries them. `--all-groups` turns the filter off.

FAIL-SOFT, absolutely: a missing / empty / corrupt store prints what is wrong and still exits 0.
Nothing here is worth failing an AIP over — a hint store that can block work would be a worse
design than having no hint store.

Usage:
  py .ai-work/tooling/read_operating_memory.py
  py .ai-work/tooling/read_operating_memory.py --groups cost_sizing,where_to_look
  py .ai-work/tooling/read_operating_memory.py --all-groups --limit 20
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (  # noqa: E402
    OPERATING_MEMORY_PLANNING_GROUPS,
    find_ai_work_root,
    operating_memory_digest,
)


def main(argv: "list[str] | None" = None) -> int:
    ap = argparse.ArgumentParser(
        description="Print the Operating Memory L2 digest (advisory hints, never a rule).")
    ap.add_argument("--groups", default="",
                    help="comma-separated group names; default = the four planning groups")
    ap.add_argument("--all-groups", action="store_true",
                    help="no group filter — same slice the ASC builder shows")
    ap.add_argument("--limit", type=int, default=8, help="max items to print (default 8)")
    ap.add_argument("--root", default="", help="project root (default: search upward from cwd)")
    ns = ap.parse_args(argv)

    try:
        root = Path(ns.root).resolve() if ns.root else find_ai_work_root(Path.cwd())
    except SystemExit:                                  # fail-soft: no tree is not a crash
        print("- (không tìm thấy `.ai-work/` từ thư mục hiện tại — bỏ qua Operating Memory)")
        return 0

    if ns.all_groups:
        groups = None
    elif ns.groups.strip():
        groups = [g.strip() for g in ns.groups.split(",") if g.strip()]
    else:
        groups = list(OPERATING_MEMORY_PLANNING_GROUPS)

    print("## Operating Memory (L2 — bài học vận hành)")
    if groups is not None:
        print(f"- Lát cắt: nhóm {', '.join(groups)} "
              f"(`--all-groups` để xem hết; đường `run` đã phủ các nhóm còn lại).")
    try:
        for line in operating_memory_digest(root / ".ai-work", max_items=max(1, ns.limit),
                                            groups=groups):
            print(line)
    except Exception as exc:                            # noqa: BLE001 — see module docstring
        print(f"- (không đọc được Operating Memory: {exc.__class__.__name__} — bỏ qua, "
              f"không chặn việc tạo AIP)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
