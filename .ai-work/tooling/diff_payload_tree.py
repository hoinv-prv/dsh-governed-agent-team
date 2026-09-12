#!/usr/bin/env python3
"""Per-file ADD / UPDATE / UNCHANGED / REMOVED between a package payload and an installed tree.

`aiws-pkg upgrade` step 4 asks for exactly this list, and step 5 copies the ADD/UPDATE half of it.
Until CR-AIWS-2026-08-088 nothing produced it: `ls .ai-work/tooling/ | grep -iE "diff|delta"` came
back empty, so every adopter wrote the script again.

**The package CHANGELOG cannot answer this question.** Its counts are package-vs-package — the
delta between the previous release and this one. A project that skipped a release, or edited a
file after installing, has a different delta into ITS tree. Measured case (IR-2026-08-15 F8):
CHANGELOG said 119 new / 78 updated / 55 removed; the real delta into the target was **147 ADD /
173 UPDATE** — off by more than 2x, in the direction that makes you copy too little.

READ-ONLY by contract (DP-088-B = a). It never writes into the target, never makes a temp dir,
never touches `.aiws-version`. Steps 5/6/7 already own the write path, with temp-first and a HUMAN
confirm in front of it; a second way in would be a way around that gate.

Section pairs are IMPORTED from `_common.PAYLOAD_MAP`, never copied — a second list is a list that
drifts from the one that actually installs. The map lives in `_common` and not in
`quick_install_aiws` because that installer is deliberately NOT shipped, so importing it here
killed this tool on every install (IR-2026-08-17 F1).

Usage:
  py .ai-work/tooling/diff_payload_tree.py --package <pkg-dir>
  py .ai-work/tooling/diff_payload_tree.py --package <pkg> --sections tooling,procedural
  py .ai-work/tooling/diff_payload_tree.py --package <pkg> --status ADD,UPDATE --format jsonl
  py .ai-work/tooling/diff_payload_tree.py --package <pkg> --strict-eol      # byte comparison
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import PAYLOAD_MAP  # noqa: E402  (see module docstring: _common ships, quick_install_aiws does not)

#: Sections the upgrade flow does NOT copy-overwrite. Reported anyway (DP-088-C = a) — omitting
#: them would read as "this section did not change", which is a different and false statement —
#: but flagged, because acting on their ADD/UPDATE rows with a copy would destroy project content.
MERGE_ONLY = {
    "wiki_source_profiles": "MERGE only (CR-AIWS-2026-06-047) — run merge_wiki_source_profiles.py; "
                            "NEVER copy-overwrite",
}

#: Payload dirs that exist in a package but are not in PAYLOAD_MAP because a dedicated step owns
#: them. Named here so a reader is told they were skipped rather than left to assume 0 changes.
NOT_IN_PAYLOAD_MAP = {
    "aiws_wiki_index": "handled by upgrade step 7b (copied into .ai-work/wiki_sources/)",
}

STATUSES = ("ADD", "UPDATE", "UNCHANGED", "REMOVED")


def _walk(base: Path) -> "dict[str, Path]":
    if not base.is_dir():
        return {}
    return {p.relative_to(base).as_posix(): p
            for p in base.rglob("*")
            if p.is_file() and "__pycache__" not in p.parts}


def _same(a: Path, b: Path, strict_eol: bool) -> bool:
    da, db = a.read_bytes(), b.read_bytes()
    if strict_eol:
        return da == db
    return da.replace(b"\r\n", b"\n") == db.replace(b"\r\n", b"\n")


def compare(package: Path, target: Path, sections: "list[str] | None" = None,
            strict_eol: bool = False) -> "list[dict]":
    """Return one row per file: {section, path, status, dest}. Pure read."""
    rows: list[dict] = []
    wanted = set(sections) if sections else None
    for key, dest_rel in PAYLOAD_MAP:
        if wanted is not None and key not in wanted:
            continue
        src = package / "payload" / key
        dest = target / dest_rel
        have_src, have_dest = _walk(src), _walk(dest)
        for rel in sorted(set(have_src) | set(have_dest)):
            if rel not in have_dest:
                status = "ADD"
            elif rel not in have_src:
                status = "REMOVED"
            elif _same(have_src[rel], have_dest[rel], strict_eol):
                status = "UNCHANGED"
            else:
                status = "UPDATE"
            rows.append({"section": key, "path": rel, "status": status,
                         "dest": (Path(dest_rel) / rel).as_posix()})
    return rows


def main(argv: "list[str] | None" = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--package", required=True, help="package root (the dir holding payload/)")
    ap.add_argument("--target", default=".", help="installed tree root (default: cwd)")
    ap.add_argument("--sections", default="", help="comma-separated section keys; default = all")
    ap.add_argument("--status", default="", help=f"filter, comma-separated from {','.join(STATUSES)}")
    ap.add_argument("--strict-eol", action="store_true",
                    help="compare bytes; default treats a CRLF/LF-only difference as UNCHANGED")
    ap.add_argument("--format", choices=("table", "jsonl"), default="table")
    ns = ap.parse_args(argv)

    package, target = Path(ns.package).resolve(), Path(ns.target).resolve()
    if not (package / "payload").is_dir():
        print(f"error: no payload/ under {package} — point --package at the package ROOT",
              file=sys.stderr)
        return 2

    keys = [k for k, _ in PAYLOAD_MAP]
    sections = [s.strip() for s in ns.sections.split(",") if s.strip()] or None
    if sections:
        unknown = [s for s in sections if s not in keys]
        if unknown:
            print(f"error: unknown section(s) {unknown}; known: {keys}", file=sys.stderr)
            return 2

    want_status = {s.strip().upper() for s in ns.status.split(",") if s.strip()} or set(STATUSES)
    bad = want_status - set(STATUSES)
    if bad:
        print(f"error: unknown status {sorted(bad)}; known: {list(STATUSES)}", file=sys.stderr)
        return 2

    rows = compare(package, target, sections, ns.strict_eol)
    shown = [r for r in rows if r["status"] in want_status]

    if ns.format == "jsonl":
        for r in shown:
            print(json.dumps(r, ensure_ascii=False))
    else:
        print(f"payload: {package / 'payload'}")
        print(f"target : {target}")
        print(f"compare: {'BYTE (--strict-eol)' if ns.strict_eol else 'EOL-insensitive (default)'}")
        print()
        for key, dest_rel in PAYLOAD_MAP:
            if sections is not None and key not in sections:
                continue
            sec = [r for r in rows if r["section"] == key]
            if not sec:
                continue
            tally = {s: sum(1 for r in sec if r["status"] == s) for s in STATUSES}
            note = MERGE_ONLY.get(key)
            print(f"## {key} -> {dest_rel}"
                  f"   ADD {tally['ADD']} · UPDATE {tally['UPDATE']} · "
                  f"UNCHANGED {tally['UNCHANGED']} · REMOVED {tally['REMOVED']}")
            if note:
                print(f"   !! {note}")
            for r in sec:
                if r["status"] in want_status and r["status"] != "UNCHANGED":
                    print(f"   {r['status']:9} {r['path']}")
            print()

    total = {s: sum(1 for r in rows if r["status"] == s) for s in STATUSES}
    print(f"TOTAL: ADD {total['ADD']} · UPDATE {total['UPDATE']} · "
          f"UNCHANGED {total['UNCHANGED']} · REMOVED {total['REMOVED']}"
          f"   (apply-list = ADD + UPDATE = {total['ADD'] + total['UPDATE']})")
    print("NOTE: REMOVED = present in the tree, absent from the package. It may be project-local; "
          "upgrade never deletes it for you — step 8 asks a HUMAN to review the list.")
    for key, why in NOT_IN_PAYLOAD_MAP.items():
        if (package / "payload" / key).is_dir():
            print(f"NOTE: payload/{key} not compared — {why}.")
    print("NOTE: the package CHANGELOG counts are package-vs-package, NOT the delta into this "
          "tree. Use the numbers above.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
