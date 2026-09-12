#!/usr/bin/env python3
"""Report (and optionally repair) tracked files whose WORKTREE bytes differ from their BLOB.

Run:  py .ai-work/tooling/check_eol_alignment.py            # report
      py .ai-work/tooling/check_eol_alignment.py --fix      # realign the EOL-only ones
      py .ai-work/tooling/check_eol_alignment.py --quiet    # summary line only
Exit: 0 aligned / 1 divergence found / 2 refused (real content differences). stdlib only.

WHY THIS EXISTS — `git status` structurally cannot see this class of defect.
`.gitattributes` carries `* -text` (CR-AIWS-2026-08-005), so git stores bytes verbatim and does
no EOL conversion. But the index still holds stat info (size/mtime) captured when files were
checked out under `core.autocrlf=true`, which wrote CRLF. Because the cached size matches what
is on disk, git skips the content comparison entirely and reports a CLEAN tree while thousands
of files genuinely differ from their blobs by line endings alone. Every write to one of those
files then explodes into a full-file diff.

Measured 2026-08-07 before the first realign: 2235 of 2887 tracked files diverged this way, all
EOL-only. The bleed had already cost three waves — 108 files (CR-AIWS-2026-08-016), 54 files in
the ATDB wave (42 of them carrying no content change at all), and 11 files in the duplicate_cr_id
wave. Root cause + history: capture CAP-1008-02 (AIP-EXEC-1008).

SAFETY: `--fix` refuses to write anything if ANY tracked file has a real (non-EOL) content
difference — that would be uncommitted work. It also never picks a house style: each file is
rewritten with ITS OWN blob bytes, so a deliberately-CRLF file stays CRLF.

NOTE for whoever wires this into a gate: `lint_all` rule changes are cr_required (lint-rule
freeze, CR-AIWS-2026-07-037). This tool is deliberately standalone so it can ship as `no_cr`.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path


def _walk_up_for_repo(start: Path) -> Path:
    """Walk up for the repo root.

    Start from the CWD, never from `__file__` — this tool lives inside a repo, so an
    `__file__`-anchored default would silently inspect ITS OWN repo whenever it is pointed at a
    different tree, and report that one as clean. (Caught by test_eol_alignment E2: the fixture
    diverged, the tool answered "OK" about the wrong repo. Rule 3, tooling_authoring_conventions.)
    """
    for d in [start, *start.parents]:
        if (d / ".git").exists():
            return d
    return start


def _read_blobs(root: Path, entries: list[tuple[str, str]]) -> list[bytes]:
    """Read every blob through ONE `git cat-file --batch`.

    stdin is a FILE, not a pipe: feeding ~100 KB of SHAs into a 64 KB pipe buffer before reading
    stdout deadlocks on Windows. (Learned the hard way; do not "simplify" this back to a pipe.)
    """
    sha_file = Path(tempfile.mkdtemp(prefix="eolchk-")) / "shas.txt"
    sha_file.write_bytes(("\n".join(sha for _, sha in entries) + "\n").encode())
    blobs: list[bytes] = []
    with sha_file.open("rb") as fh:
        proc = subprocess.Popen(["git", "cat-file", "--batch"], cwd=str(root),
                                stdin=fh, stdout=subprocess.PIPE)
        out = proc.stdout
        assert out is not None
        for _ in entries:
            header = out.readline()
            if not header:
                break
            parts = header.split()
            if len(parts) < 3:            # "<sha> missing"
                blobs.append(b"")
                continue
            blobs.append(out.read(int(parts[2])))
            out.read(1)                   # trailing newline
        proc.wait()
    return blobs


def main() -> int:
    p = argparse.ArgumentParser(description="Check worktree/blob byte alignment")
    # Rule 3 — never resolve the root from __file__ alone; keep the tool sandbox-pointable.
    p.add_argument("--project-root", default="", help="repo root (default: walk up)")
    p.add_argument("--fix", action="store_true", help="rewrite EOL-only divergences from the blob")
    p.add_argument("--quiet", action="store_true", help="summary line only")
    p.add_argument("--limit", type=int, default=20, help="how many paths to list (default 20)")
    ns = p.parse_args()

    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    root = (Path(ns.project_root).resolve() if ns.project_root
            else _walk_up_for_repo(Path.cwd().resolve()))

    ls = subprocess.run(["git", "ls-files", "-s", "-z"], cwd=str(root),
                        capture_output=True).stdout
    entries: list[tuple[str, str]] = []
    for rec in ls.split(b"\x00"):
        if not rec:
            continue
        meta, _, path = rec.partition(b"\t")
        cols = meta.split()
        if len(cols) >= 2:
            entries.append((path.decode("utf-8", "surrogateescape"), cols[1].decode()))
    if not entries:
        print("no tracked files (not a git repo?)", file=sys.stderr)
        return 1

    blobs = _read_blobs(root, entries)
    aligned, eol_only, real, gone = 0, [], [], 0
    for (rel, _sha), blob in zip(entries, blobs):
        f = root / rel
        if not f.is_file():
            gone += 1
            continue
        disk = f.read_bytes()
        if blob == disk:
            aligned += 1
        elif blob.replace(b"\r\n", b"\n") == disk.replace(b"\r\n", b"\n"):
            eol_only.append((rel, blob))
        else:
            real.append(rel)

    if not ns.quiet:
        print(f"tracked files       : {len(entries)}" + (f"  (missing: {gone})" if gone else ""))
        print(f"aligned with blob   : {aligned}")
        print(f"EOL-ONLY divergence : {len(eol_only)}")
        print(f"real content diff   : {len(real)}")
        for r in real[:ns.limit]:
            print(f"    [real] {r}")
        for r, _ in eol_only[:ns.limit]:
            print(f"    [eol ] {r}")
        extra = len(eol_only) - ns.limit
        if extra > 0:
            print(f"    ... +{extra} more EOL-only")

    if not ns.fix:
        if eol_only:
            print(f"DIVERGED: {len(eol_only)} file(s) differ from their blob by line endings "
                  f"only — `git status` cannot see this. Re-run with --fix.")
            return 1
        # Do NOT claim "everything matches" when real content differs — that is a false green,
        # and this tool exists to prevent exactly that. Say precisely what was and was not checked.
        if real:
            print(f"OK — no EOL divergence. ({len(real)} file(s) carry real content changes; "
                  f"those are ordinary uncommitted work, not this tool's concern.)")
        else:
            print("OK — every tracked file matches its blob.")
        return 0

    if real:
        print(f"REFUSING to fix: {len(real)} file(s) carry real content differences "
              f"(uncommitted work). Resolve those first.")
        return 2
    for rel, blob in eol_only:
        (root / rel).write_bytes(blob)
    print(f"realigned {len(eol_only)} file(s) to their blob bytes "
          f"(no content change — run `git add -A` to refresh the index stat).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
