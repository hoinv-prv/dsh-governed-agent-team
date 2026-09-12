#!/usr/bin/env python3
"""Reading-kit / digest generator (CR-AIWS-2026-07-003 E2).

For a task-shape (review / author a function or object), assemble in ONE call the set of docs to
read — instead of N per-doc lookups. Seeds from the index (semantic scoring, shared with the real
lookup via `_common`), then expands ONE hop over the relations projection (RD↔BD↔DD chains,
→OVERALL, part_of/contains for chunked sections). When the corpus has no edges yet, falls back to a
NAMING-CONVENTION grouping (docs sharing a function code like F02 across doc-types).

stdlib-only. Default = on-demand (print to stdout, 0 staleness — reads the live index). `--materialize
<dir>` writes a reading-kit .md (cited by path + source_id together, so it survives id drift — the
staleness guard Q4's curated_citation_stale lint then covers it).

Usage:
  python .ai-work/tooling/build_reading_kit.py --query "search room detail design" --system demo
  python .ai-work/tooling/build_reading_kit.py --function F02 --system demo
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import all_index_paths, find_ai_work_root, read_jsonl, resolve_relations_paths, score_semantic, wiki_tokens, write_text  # noqa: E402
from _common import read_project_config as _project_config, in_system as _in_system  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:  # noqa: BLE001
    pass


def _load_relations(paths):
    """Return (out, inn): out[src] = [(role, tgt)], inn[tgt] = [(role, src)].

    CR-AIWS-2026-08-064 C8: `paths` = every relations file the resolver returns (project +
    shipped aiws preset) — one-hop expansion sees AIWS edges too. A single Path still works."""
    out: dict = {}
    inn: dict = {}
    if isinstance(paths, Path):
        paths = [paths]
    try:
        for path in paths:
            if not path.exists():
                continue
            for e in read_jsonl(path):
                s, t, r = e.get("source_ref"), e.get("target_ref"), e.get("relationship_type", "related")
                if s and t:
                    out.setdefault(s, []).append((r, t))
                    inn.setdefault(t, []).append((r, s))
    except ValueError:
        pass
    return out, inn


def main() -> int:
    p = argparse.ArgumentParser(description="Reading-kit / digest generator (E2)")
    p.add_argument("--query", default="", help="task keyword (e.g. 'search room detail design')")
    p.add_argument("--function", default="", help="function code to group by (e.g. F02) — naming-convention seed")
    p.add_argument("--system", default=None, help="multi-system scope (id) or omit")
    p.add_argument("--all-systems", action="store_true")
    p.add_argument("--index", default=None, help="comma-separated index paths (default project+aiws)")
    p.add_argument("--top-seeds", type=int, default=4, help="how many seed docs before expansion")
    p.add_argument("--materialize", default=None, metavar="DIR",
                   help="write a reading-kit .md into DIR instead of printing")
    # E3 (CR-AIWS-2026-07-003): second output format of THIS generator (OP-902-03) — a per-corpus
    # cheat-sheet (function-code → source_ids) instead of a per-task reading kit.
    p.add_argument("--cheat-sheet", action="store_true",
                   help="E3: emit a per-corpus cheat-sheet (function code → source_ids) for the scope, "
                        "not a per-task reading kit. Materialize into .ai-work/wiki/reference/ so Q4's "
                        "curated_citation_stale lint keeps it fresh.")
    ns = p.parse_args()

    project_root = find_ai_work_root(Path.cwd())
    ai_work = project_root / ".ai-work"
    ws = ai_work / "wiki_sources"

    if ns.index:
        idx_paths = [Path(x) for x in ns.index.split(",")]
    else:
        idx_paths = all_index_paths(ws)   # CR-051 T3 (Rule 6): one source of truth, not a 3rd copy
    records: list = []
    for ip in idx_paths:
        if ip.exists():
            records.extend(read_jsonl(ip))
    by_id = {r.get("source_id"): r for r in records}

    # multi-system scope
    cfg = _project_config(ai_work)
    active = None
    if cfg["multi_system"] and not ns.all_systems:
        active = ns.system
        if not active:
            print("error: multi_system project — pass --system <id> or --all-systems", file=sys.stderr)
            return 2
    scoped = [r for r in records if (active is None or _in_system(r, active))]

    # ── E3 (CR-AIWS-2026-07-003): per-corpus cheat-sheet (function-code → source_ids) ──
    if ns.cheat_sheet:
        fcode_re = re.compile(r"\b([A-Z]{1,3}\d{2,})\b")
        groups: dict = {}
        for r in scoped:
            hay = r.get("source_id", "") + " " + " ".join(r.get("lookup_keys", []) or []) + " " + r.get("title", "")
            codes = sorted(set(fcode_re.findall(hay)))
            key = codes[0] if codes else "(no code)"
            groups.setdefault(key, []).append(r)
        scope_lbl = active or "all"
        lines = [f"# Cheat-sheet — {scope_lbl}", "",
                 "Function/entity code → registered source_ids (cite BOTH the id and the path so this "
                 "survives id drift; `lint_wiki curated_citation_stale` keeps it fresh).", ""]
        for code in sorted(groups):
            lines.append(f"## {code}")
            for r in sorted(groups[code], key=lambda x: x.get("source_type", "")):
                loc = r.get("artifact_locator", "")
                if r.get("section_lines"):
                    loc += f" (lines {r['section_lines']})"
                lines.append(f"- `{r.get('source_id','')}` — {r.get('source_type','')} — {loc}")
            lines.append("")
        cheat_md = "\n".join(lines)
        if ns.materialize:
            d = Path(ns.materialize)
            d.mkdir(parents=True, exist_ok=True)
            outp = d / f"cheat_sheet_{re.sub(r'[^A-Za-z0-9]+','-',scope_lbl).lower()}.md"
            write_text(outp, cheat_md + "\n")
            print(f"cheat-sheet written: {outp}")
        else:
            print(cheat_md)
        return 0

    # ── seed ──
    seeds: list = []
    seed_reason: dict = {}
    if ns.query:
        qtok = {t.lower() for t in wiki_tokens(ns.query)}
        ranked = sorted(((score_semantic(r, qtok, ns.query), r) for r in scoped),
                        key=lambda sr: -sr[0])
        seeds = [r for s, r in ranked[:ns.top_seeds] if s > 0]
        for r in seeds:
            seed_reason[r["source_id"]] = "seed:query"
    if ns.function:
        fcode = ns.function.upper()
        fre = re.compile(rf"\b{re.escape(fcode)}\b", re.IGNORECASE)
        for r in scoped:
            hay = r.get("source_id", "") + " " + " ".join(r.get("lookup_keys", []) or []) + " " + r.get("title", "")
            if fre.search(hay) and r["source_id"] not in seed_reason:
                seeds.append(r)
                seed_reason[r["source_id"]] = f"seed:{fcode}"
    if not seeds:
        print("(no seed docs — refine --query/--function)", file=sys.stderr)
        return 1

    # ── expand one hop over relations (edges) ──
    out_e, in_e = _load_relations(resolve_relations_paths(ws, {"project", "aiws"}))
    kit: dict = {}  # source_id -> role
    for r in seeds:
        kit[r["source_id"]] = seed_reason.get(r["source_id"], "seed")
    for sid in list(kit):
        for role, tgt in out_e.get(sid, []):
            if tgt in by_id and tgt not in kit:
                kit[tgt] = role
        for role, src in in_e.get(sid, []):
            if src in by_id and src not in kit:
                kit[src] = f"in:{role}"

    used_edges = len(kit) > len(seeds)
    # ── fallback: naming-convention F-code grouping if edges added nothing ──
    if not used_edges and ns.function:
        fcode = ns.function.upper()
        fre = re.compile(rf"\b{re.escape(fcode)}\b", re.IGNORECASE)
        for r in scoped:
            hay = r.get("source_id", "") + " " + " ".join(r.get("lookup_keys", []) or [])
            if fre.search(hay) and r["source_id"] not in kit:
                kit[r["source_id"]] = f"naming:{fcode}"

    # ── render ──
    rows = []
    for sid, role in kit.items():
        r = by_id.get(sid, {})
        loc = r.get("artifact_locator", "")
        sec = r.get("section_lines", "")
        if sec:
            loc = f"{loc} (lines {sec})"
        rows.append((role, r.get("source_type", ""), sid, r.get("title", ""), loc))
    rows.sort(key=lambda x: (0 if x[0].startswith("seed") else 1, x[1], x[2]))

    header = f"# Reading kit — {ns.query or ns.function} " + (f"[system:{active}]" if active else "")
    lines = [header, "",
             f"{len(rows)} doc(s) — {len(seeds)} seed + expansion via "
             + ("relations edges" if used_edges else "naming-convention fallback (no edges)") + ".", "",
             "| role | type | source_id | title | open |",
             "|---|---|---|---|---|"]
    for role, st, sid, title, loc in rows:
        lines.append(f"| {role} | {st} | `{sid}` | {title} | {loc} |")
    kit_md = "\n".join(lines) + "\n"

    if ns.materialize:
        d = Path(ns.materialize)
        d.mkdir(parents=True, exist_ok=True)
        slug = re.sub(r"[^A-Za-z0-9]+", "-", (ns.function or ns.query)).strip("-").lower() or "kit"
        outp = d / f"reading_kit_{slug}.md"
        write_text(outp, kit_md)
        print(f"reading kit written: {outp}")
    else:
        print(kit_md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
