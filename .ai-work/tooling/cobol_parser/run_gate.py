"""Corpus round-trip gate runner (AIP-EXEC-048 STEP-01).

One system per invocation — systems are independent and their numbers must not
be merged (AIP-EXEC-013 rule). COBOL selection mirrors the cobol-wiki config:
COB/CB/CBL by extension, PRC/TXT by content sniff.

    py packages/cobol_parser/src/tooling/cobol_parser/run_gate.py \
        --root src/honsha --libs DBSRCLIB,COPYLIB --out <report.jsonl>
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
if True:  # noqa: E402 — path bootstrap before package import
    from cobol_parser.gate import check_file

_COBOL_EXT = {"COB", "CB", "CBL"}
_SNIFF_EXT = {"PRC", "TXT"}
_SNIFF = re.compile(r"^\s*(IDENTIFICATION\s+DIVISION|PROGRAM-ID\.)", re.IGNORECASE | re.MULTILINE)


def is_cobol(path: Path, data: bytes) -> bool:
    ext = path.suffix.lstrip(".").upper()
    if ext in _COBOL_EXT:
        return True
    if ext in _SNIFF_EXT:
        head = data[:4000].decode("cp932", errors="replace")
        return bool(_SNIFF.search(head))
    return False


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, help="system root, e.g. src/honsha")
    ap.add_argument("--libs", required=True, help="comma-separated library dirs")
    ap.add_argument("--out", required=True, help="JSONL report path")
    args = ap.parse_args()

    rows = []
    for lib in args.libs.split(","):
        base = Path(args.root) / lib
        for path in sorted(p for p in base.rglob("*") if p.is_file()):
            data = path.read_bytes()
            if not is_cobol(path, data):
                continue
            row = {"path": path.as_posix(), "lib": lib}
            row.update(check_file(data))
            rows.append(row)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    total = len(rows)
    by = lambda s: sum(1 for r in rows if r["status"] == s)  # noqa: E731
    cautioned = sum(1 for r in rows if r.get("caution_count"))
    print(f"root={args.root} files={total} pass={by('pass')} fail={by('fail')} "
          f"unreadable={by('unreadable')} files_with_cautions={cautioned}")
    for r in rows:
        if r["status"] == "fail":
            print(f"  FAIL {r['path']}: {r['violations'][:2]}")


if __name__ == "__main__":
    main()
