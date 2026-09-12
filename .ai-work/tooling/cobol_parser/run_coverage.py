"""Coverage harness (AIP-EXEC-048 STEP-02) — the P3 steering instrument.

Per file: status (structured | partial | unreadable), statement counts, and the
verb histogram. "Recognized" means the statement leads with a known verb
(shallow); P3 types each verb against its 付録F 書き方. RawStatements' leading
words are histogrammed separately — that list IS the P3 work queue.

One system per invocation (numbers stay separate):

    py packages/cobol_parser/src/tooling/cobol_parser/run_coverage.py \
        --root src/honsha --libs DBSRCLIB,COPYLIB --out <report.jsonl>
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
if True:  # noqa: E402
    from cobol_parser.decode import sniff_encoding
    from cobol_parser.lexer import lex
    from cobol_parser.reader import read_lines
    from cobol_parser.structure import parse_program

_COBOL_EXT = {"COB", "CB", "CBL"}
_SNIFF_EXT = {"PRC", "TXT"}
_SNIFF = re.compile(r"^\s*(IDENTIFICATION\s+DIVISION|PROGRAM-ID\.)", re.IGNORECASE | re.MULTILINE)


def is_cobol(path: Path, data: bytes) -> bool:
    ext = path.suffix.lstrip(".").upper()
    if ext in _COBOL_EXT:
        return True
    if ext in _SNIFF_EXT:
        return bool(_SNIFF.search(data[:4000].decode("cp932", errors="replace")))
    return False


def check_file(data: bytes) -> dict:
    enc = sniff_encoding(data)
    if enc in ("binary", "undecodable"):
        return {"status": "unreadable", "encoding": enc}
    lines = read_lines(data)
    cautions: list[str] = [c for ln in lines for c in ln.cautions]
    tokens = lex(lines, encoding=enc, cautions=cautions)
    prog = parse_program(lines, tokens)

    verb_hist: Counter = Counter()
    raw_hist: Counter = Counter()
    kind_hist: Counter = Counter()
    n_recognized = n_raw = n_raw_debug = 0
    for div in prog.divisions:
        for sent in div.sentences():
            kind_hist[sent.kind] += 1
        # Procedural statements plus the compiler-directing ones that live inside
        # data entries — both are "statements the parser had to recognize".
        # Debug-line statements are counted separately: they are real code (they
        # can call real programs) but a raw fragment on a `D` line is not the
        # same coverage gap as one in production code.
        for st in list(div.statements(("statements", "raw"))) + list(div.compiler_directing("COPY")):
            if st.verb:
                n_recognized += 1
                verb_hist[st.verb] += 1
            else:
                n_raw += 1
                head = st.tokens[0]
                raw_hist[head.text.upper()[:20] if head.type == "WORD" else head.type] += 1
        for st in div.statements(("debug",)):
            if st.verb:
                n_recognized += 1
                verb_hist[st.verb] += 1
            else:
                n_raw_debug += 1

    total = n_recognized + n_raw + n_raw_debug
    status = "structured" if (n_raw == 0 and n_raw_debug == 0 and not cautions) else "partial"
    return {
        "status": status,
        "encoding": enc,
        "statements": total,
        "recognized": n_recognized,
        "raw": n_raw,
        "raw_debug": n_raw_debug,
        "caution_count": len(cautions),
        "verbs": dict(verb_hist),
        "raw_heads": dict(raw_hist),
        "sentence_kinds": dict(kind_hist),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--libs", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    rows = []
    for lib in args.libs.split(","):
        for path in sorted(p for p in (Path(args.root) / lib).rglob("*") if p.is_file()):
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

    n = len(rows)
    by = Counter(r["status"] for r in rows)
    stmts = sum(r.get("statements", 0) for r in rows)
    rec = sum(r.get("recognized", 0) for r in rows)
    raw = sum(r.get("raw", 0) for r in rows)
    raw_dbg = sum(r.get("raw_debug", 0) for r in rows)
    verbs: Counter = Counter()
    raws: Counter = Counter()
    for r in rows:
        verbs.update(r.get("verbs", {}))
        raws.update(r.get("raw_heads", {}))
    pct = (100.0 * rec / stmts) if stmts else 0.0
    print(f"root={args.root} files={n} structured={by['structured']} partial={by['partial']} "
          f"unreadable={by['unreadable']}")
    print(f"statements={stmts} recognized={rec} ({pct:.2f}%) raw={raw} raw_on_debug_lines={raw_dbg}")
    print("top verbs:", verbs.most_common(12))
    print("top raw heads:", raws.most_common(12))


if __name__ == "__main__":
    main()
