"""Derive reserved.py from BOTH manuals' reserved-word tables.

Authorities:
  G  付表 E.1  — SRC-ASP-04-asp-cobol-g-v13-0a47-ph-l-c-e-e578
                 (manuals/asp_manuals/ASP COBOL G 文法書 V13～/MD/Phụ_Lục_E_予約語表.md)
                 a word is reserved in G iff its COBOL G column (2nd cell) carries ○
  E  表 2.2   — ASP JIS COBOL E 文法書 §2.9, column A ("A欄に○印が付いている語を
                 予約語として扱う"), transcribed in AIP-EXEC-048 STEP-06 and kept in
                 tools/manual_audit/e_reserved_table.json

Why both. The corpus is mixed-dialect and measurably so: 139 files write NOMINAL
KEY and 9 write ACTUAL KEY, neither of which exists in G. The parser's word table
came from G alone, so 120 words that E reserves were read as ordinary user words.
That is not cosmetic — `Sentence.kind` asks `head.reserved`, so a sentence whose
first word was one of them was filed `raw`, i.e. counted as a construct the parser
does not handle, while the splitter was parsing it correctly all along. Measured
over the whole corpus: 114 sentences in 50 files (UNLOCK 89, EXAMINE 23,
EXHIBIT 2) moved raw -> statements, and NOTHING moved the other way.

The union is deliberate but it is not free, so the cost was measured too: 9 data
entries in 9 files are NAMED by a word only E reserves (RETURN-CODE 5, DIRECT 3,
ID 1). None change how they parse — in the data division a level number decides
the sentence kind before `reserved` is consulted — but the risk is real for a
different corpus, which is why the two sets stay separately named below rather
than being flattened into one anonymous blob.

Both inputs are gitignored (the manuals deliberately so); the OUTPUT is committed.
This script therefore cannot be re-run in a fresh checkout, which has been true
since it was written.

Run from project root:
    py packages/cobol_parser/src/tooling/cobol_parser/_derive_reserved.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

SOURCE_G = "SRC-ASP-04-asp-cobol-g-v13-0a47-ph-l-c-e-e578"
MANUAL_G = Path("manuals/asp_manuals/ASP COBOL G 文法書 V13～/MD/Phụ_Lục_E_予約語表.md")
TABLE_E = Path("tools/manual_audit/e_reserved_table.json")
OUT = Path(__file__).with_name("reserved.py")

WORD_RE = re.compile(r"^[A-Z0-9][A-Z0-9-]*$")


def parse_words(text: str) -> list[str]:
    words = set()
    for line in text.splitlines():
        if not line.startswith("│"):
            continue
        cells = line.split("│")
        if len(cells) < 3:
            continue
        word = cells[1].strip().strip("　").strip()
        if not WORD_RE.match(word):
            continue
        if "○" in cells[2]:
            words.add(word)
    return sorted(words)


def e_words() -> list[str]:
    table = json.loads(TABLE_E.read_text(encoding="utf-8"))
    return sorted(w for w in table["A_FACOM_JIS_COBOL_E"] if WORD_RE.match(w))


def _block(words: list[str]) -> str:
    return ",\n    ".join(f'"{w}"' for w in words)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    g = parse_words(MANUAL_G.read_text(encoding="utf-8"))
    e = e_words()
    OUT.write_text(
        '"""Reserved words of the two ASP COBOL dialects — GENERATED, do not hand-edit.\n'
        "\n"
        f"COBOL G: 付表 E.1 ({SOURCE_G}), a word is included iff its COBOL G column\n"
        "carries ○.\n"
        "\n"
        "JIS COBOL E: 表2.2 of §2.9, column A — 「このコンパイラでは，A欄に○印が付いて\n"
        "いる語を予約語として扱う」.\n"
        "\n"
        "`RESERVED_WORDS` is the UNION, because the corpus is mixed-dialect: 139 files\n"
        "write NOMINAL KEY and 9 write ACTUAL KEY, which exist only in E. Keeping the\n"
        "sets separately named keeps the question 'which dialect reserves this?'\n"
        "answerable — the union alone cannot answer it.\n"
        "\n"
        "Regenerate with _derive_reserved.py.\n"
        '"""\n'
        "\n"
        f"RESERVED_WORDS_G = frozenset((\n    {_block(g)},\n))\n"
        "\n"
        f"RESERVED_WORDS_E = frozenset((\n    {_block(e)},\n))\n"
        "\n"
        "#: What the lexer marks. See the module docstring for why it is the union.\n"
        "RESERVED_WORDS = RESERVED_WORDS_G | RESERVED_WORDS_E\n",
        encoding="utf-8",
    )
    print(f"G {len(g)} · E {len(e)} · union {len(set(g) | set(e))} -> {OUT}")


if __name__ == "__main__":
    main()
