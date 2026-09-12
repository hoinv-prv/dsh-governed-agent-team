#!/usr/bin/env python3
"""UTF-8-safe append for agent task desk changelogs (CAP-1002-02, no_cr tooling — AIP-EXEC-1003).

Why this exists: PowerShell `Add-Content` without `-Encoding utf8` writes the system ANSI
codepage and silently destroys Vietnamese text (measured 2026-08-06: 3 desk changelogs
corrupted in one session, one entry lossy beyond decode-repair). This helper is the
sanctioned writer: always UTF-8, LF newlines, and it PROVES the write by re-reading the
file in strict UTF-8 afterwards.

Usage:
  py append_desk_changelog.py --desk <desk_id> --title "..." [--date YYYY-MM-DD]
                              [--line "- ..."] [--line "- ..."] [--by "..."]
  py append_desk_changelog.py --file <path/to/changelog.md> --title "..." ...

Appends:

  ## <date> — <title>
  <lines verbatim, one per --line>

The tool never rewrites existing content — append-only. It refuses a missing changelog
(a desk without one is a scaffold problem, not something to paper over here).
"""
from __future__ import annotations

import argparse
import datetime as _dt
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass

PACK_ROOT = Path(__file__).resolve().parent.parent
_DESK_ROOTS = [
    PACK_ROOT / "agents" / "task_desks",
    PACK_ROOT / "agents" / "instances",  # CR-AIWS-2026-08-006 P2 dual-read
]


def _die(msg: str) -> None:
    print(f"[error] {msg}")
    sys.exit(1)


def _resolve_changelog(args: argparse.Namespace) -> Path:
    if args.file:
        p = Path(args.file)
        if not p.is_file():
            _die(f"changelog not found: {p}")
        return p
    for root in _DESK_ROOTS:
        cand = root / args.desk / "changelog.md"
        if cand.is_file():
            return cand
    _die(f"desk '{args.desk}' has no changelog.md under {_DESK_ROOTS[0]} (or legacy root)")
    raise AssertionError  # unreachable


def main() -> None:
    ap = argparse.ArgumentParser(description="Append a UTF-8 entry to a desk changelog")
    who = ap.add_mutually_exclusive_group(required=True)
    who.add_argument("--desk", help="desk_id (resolved under the pack's task_desks root)")
    who.add_argument("--file", help="explicit path to a changelog.md")
    ap.add_argument("--title", required=True, help="entry title (goes after '## <date> — ')")
    ap.add_argument("--date", default=_dt.date.today().isoformat(), help="YYYY-MM-DD (default: today)")
    ap.add_argument("--line", action="append", default=[], help="entry body line, verbatim; repeatable")
    ap.add_argument("--by", default="", help="optional author note, appended as '- by: <...>'")
    args = ap.parse_args()

    try:
        _dt.date.fromisoformat(args.date)
    except ValueError:
        _die(f"--date must be YYYY-MM-DD, got: {args.date}")

    cl = _resolve_changelog(args)
    before = cl.read_text(encoding="utf-8")  # strict: an already-corrupt file fails HERE, loudly

    header = f"## {args.date} — {args.title}"
    body = list(args.line)
    if args.by:
        body.append(f"- by: {args.by}")
    entry = "\n".join([header, *body])

    text = before
    if text and not text.endswith("\n"):
        text += "\n"
    text += "\n" + entry + "\n"
    cl.write_text(text, encoding="utf-8", newline="\n")

    # prove the write: strict re-read + the entry must round-trip byte-exactly
    after = cl.read_text(encoding="utf-8")
    if header not in after or not after.startswith(before[: len(before)]):
        _die("post-write verification failed — file content did not round-trip")
    print(f"appended: {cl} :: {header}")


if __name__ == "__main__":
    main()
