#!/usr/bin/env python3
"""Query the Wiki Relations edge layer (opt-in, one-hop).

Given a node (source_id), return its relations so AI can expand from a confirmed
source WITHOUT reopening raw artifacts or running fragile repo-wide grep:

    --relations <id>   query relations.jsonl (+ relations.aiws.jsonl preset, CR-064) → `## out` + `## in`
                       (others → id, the REVERSE / impact view). Bidirectional.
    --expand <id>      read that meta's `## Related Sources` out-edges directly
                       (authoritative), resolve each target against the index.
    --rebuild          regenerate relations.jsonl from metas (delegates to build_relations).

This is a ONE-HOP query over a rebuilt projection — NOT a graph engine, NOT
transitive closure (Knowledge_Relationship Spec §5 "no precomputed global graph").
Default invocation does NOTHING unless a relation param is given (additive; no impact
on lookup_wiki_source.py, which stays the discovery tool). CR-AIWS-2026-05-022.

Runtime flow: lookup_wiki_source.py (discovery) → open meta (confirm file + read its
`## Related Sources`) → IF the intent needs impact / what-feeds-this / neighbours:
wiki_relations.py --relations <id> for the reverse view the meta cannot provide.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_relations as br  # noqa: E402  (reuse the parser + builder; same tooling dir)
from _common import (  # noqa: E402
    all_index_paths,
    find_ai_work_root,
    locator_str,
    read_jsonl,
    read_text,
    resolve_data_file,
    resolve_locator,
    resolve_relations_paths,
    write_jsonl,
)


def _load_index(index_path: Path) -> dict[str, dict]:
    """Load the index used to resolve edge endpoints. CR-AIWS-2026-07-048: relations.jsonl carries
    edges from BOTH meta namespaces, so a lookup must read `index.aiws.jsonl` too — resolving only
    against index.jsonl made every AIWS-side endpoint print as [BROKEN REF] / 'node not in index'."""
    out: dict[str, dict] = {}
    for idx in all_index_paths(index_path.parent):
        out.update({r.get("source_id", ""): r for r in read_jsonl(idx)})
    return out


def _node_tag(idx: dict[str, dict], source_id: str) -> str:
    """[authority/status] tag for a node, or [BROKEN REF] when not in the index."""
    rec = idx.get(source_id)
    if rec is None:
        return "[BROKEN REF]"
    auth = rec.get("authority_level", "?")
    status = rec.get("status", "?")
    return f"[{auth}/{status}]"


def _title(idx: dict[str, dict], source_id: str) -> str:
    rec = idx.get(source_id)
    return rec.get("title", "") if rec else ""


def _load_edges(rel_paths: list[Path]) -> tuple[list[dict], list[str]]:
    """CR-AIWS-2026-08-064 C3 — merge every resolved relations file (project + shipped aiws
    preset), dedupe on (source_ref, target_ref, relationship_type) with first-file-wins, and
    return a per-file summary line so the reader knows WHICH namespace served the answer."""
    seen: set = set()
    edges: list[dict] = []
    parts: list[str] = []
    for rp in rel_paths:
        rows = read_jsonl(rp)
        parts.append(f"{rp.name}({len(rows)} edges)")
        for e in rows:
            k = (e.get("source_ref", ""), e.get("target_ref", ""), e.get("relationship_type", ""))
            if k in seen:
                continue
            seen.add(k)
            edges.append(e)
    return edges, parts


def cmd_relations(source_id: str, rel_paths, idx: dict[str, dict]) -> int:
    """`rel_paths` = list of relations files (dual read) — a bare Path is accepted too
    (test_object_named_consumer + external callers pass one file)."""
    if isinstance(rel_paths, (str, Path)):
        rel_paths = [Path(rel_paths)]
    rel_paths = [p for p in rel_paths if p.exists()]
    if not rel_paths:
        print("error: no relations projection found (relations.jsonl / relations.aiws.jsonl) — "
              "run: wiki_relations.py --rebuild  (or build_preset_wiki.py --target . for the AIWS preset)",
              file=sys.stderr)
        return 2
    edges, parts = _load_edges(rel_paths)
    out_edges = [e for e in edges if e.get("source_ref") == source_id]
    in_edges = [e for e in edges if e.get("target_ref") == source_id]

    title = _title(idx, source_id)
    head = f"relations for {source_id}" + (f"  ({title})" if title else "")
    if source_id not in idx:
        head += "  [NOTE: node not in index]"
    print(head)
    print(f"sources: {' + '.join(parts)}")
    print()

    print(f"## out  ({source_id} → others)")
    if not out_edges:
        print("  (none)")
    for e in out_edges:
        tgt = e.get("target_ref", "")
        conf = e.get("relationship_confidence_note", "asserted")
        note = e.get("relationship_basis_note", "")
        line = f"  - {e.get('relationship_type','')} → {tgt}  {_node_tag(idx, tgt)} ({conf})"
        if note:
            line += f"  — {note}"
        print(line)

    print()
    print(f"## in  (others → {source_id})   [reverse / impact]")
    if not in_edges:
        print("  (none)")
    for e in in_edges:
        src = e.get("source_ref", "")
        conf = e.get("relationship_confidence_note", "asserted")
        note = e.get("relationship_basis_note", "")
        line = f"  - {src} --{e.get('relationship_type','')}-->  {_node_tag(idx, src)} ({conf})"
        if note:
            line += f"  — {note}"
        print(line)
    return 0


def cmd_expand(source_id: str, idx: dict[str, dict], project_root: Path) -> int:
    rec = idx.get(source_id)
    if rec is None:
        print(f"error: {source_id} not found in index", file=sys.stderr)
        return 2
    # CR-AIWS-2026-07-064 B5 (Rule 9) — same class as wiki_meta cmd_view.
    meta_loc = locator_str(rec.get("meta_locator"))
    if not meta_loc:
        print(f"error: {source_id} has no meta_locator in index", file=sys.stderr)
        return 2
    meta_path = resolve_data_file(meta_loc, project_root)
    if meta_path is None:
        print(f"error: meta file not found or not a file: "
              f"{resolve_locator(meta_loc, project_root)}", file=sys.stderr)
        return 2

    from _common import parse_frontmatter, extract_sections
    _meta, body = parse_frontmatter(read_text(meta_path))
    section = extract_sections(body).get("Related Sources", "")
    edges = br.parse_related_sources(section)

    title = _title(idx, source_id)
    print(f"out-edges declared in {source_id} meta" + (f"  ({title})" if title else ""))
    print(f"  (authoritative; from ## Related Sources of {meta_path.name})")
    if not edges:
        print("  (none — meta has no resolved ## Related Sources entries)")
    for e in edges:
        tgt = e["target_ref"]
        line = f"  - {e['relationship_type']} → {tgt}  {_node_tag(idx, tgt)} ({e['relationship_confidence_note']})"
        if e["relationship_basis_note"]:
            line += f"  — {e['relationship_basis_note']}"
        print(line)
    return 0


def cmd_rebuild(ai_work: Path, meta_dir: Path, index_path: Path, rel_path: Path,
                namespace: str = "all", why: str = "") -> int:
    print(f"namespace={namespace}" + (f" ({why})" if why else "") + f" → {rel_path.name}")
    records, warnings = br.build_relations(meta_dir, index_path, namespace=namespace)
    write_jsonl(rel_path, records)
    br._write_relations_rebuild_log(ai_work, rel_path, len(records))
    for w in warnings:
        print(f"  WARN  {w}", file=sys.stderr)
    print(f"rebuilt {len(records)} edges → {rel_path}")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(
        description="Query the Wiki Relations edge layer (opt-in, one-hop). "
                    "Default does nothing unless a relation param is given.")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--relations", metavar="SOURCE_ID",
                   help="print out-edges + in-edges (reverse/impact) from relations.jsonl")
    g.add_argument("--expand", metavar="SOURCE_ID",
                   help="print the meta's ## Related Sources out-edges (authoritative)")
    g.add_argument("--rebuild", action="store_true", help="regenerate relations.jsonl from metas")
    p.add_argument("--relations-file", help="override relations file path (single file; disables the "
                                             "project+aiws merge for --relations)")
    p.add_argument("--index", help="override index.jsonl path")
    p.add_argument("--meta-dir", help="override meta dir (for --rebuild)")
    p.add_argument("--namespace", choices=["project", "aiws", "all"], default=None,
                   help="for --rebuild (CR-AIWS-2026-08-064 C4): aiws → aiws_meta/ → relations.aiws.jsonl; "
                        "project → meta/ → relations.jsonl; all → legacy merged. Default = build_relations rule.")
    ns = p.parse_args()

    project_root = find_ai_work_root(Path.cwd())
    ai_work = project_root / ".ai-work"
    wiki_sources = ai_work / "wiki_sources"
    index_path = Path(ns.index).resolve() if ns.index else (wiki_sources / "index.jsonl")

    if ns.rebuild:
        namespace, why = (ns.namespace, "explicit --namespace") if ns.namespace else br.decide_namespace(ai_work)
        if ns.meta_dir:
            meta_dir = Path(ns.meta_dir).resolve()
        else:
            meta_dir = wiki_sources / ("aiws_meta" if namespace == "aiws" else "meta")
        default_rel = wiki_sources / ("relations.aiws.jsonl" if namespace == "aiws" else "relations.jsonl")
        rel_path = Path(ns.relations_file).resolve() if ns.relations_file else default_rel
        return cmd_rebuild(ai_work, meta_dir, index_path, rel_path, namespace=namespace, why=why)

    idx = _load_index(index_path)
    if ns.relations:
        # CR-AIWS-2026-08-064 C3: dual read — project + shipped aiws preset via THE resolver
        # (collapse to relations.jsonl when no preset exists); an explicit file wins alone.
        rel_paths = ([Path(ns.relations_file).resolve()] if ns.relations_file
                     else resolve_relations_paths(wiki_sources, {"project", "aiws"}))
        return cmd_relations(ns.relations, rel_paths, idx)
    if ns.expand:
        return cmd_expand(ns.expand, idx, project_root)

    # additive / opt-in: no relation param → do nothing but show usage
    p.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
