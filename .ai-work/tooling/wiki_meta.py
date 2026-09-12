#!/usr/bin/env python3
"""Meta value-add reader — output a Wiki Source Meta's ORIENTATION info for AI WITHOUT
repeating what index.jsonl already carries (CR-AIWS-2026-05-024).

Design tenet: a meta is an AI ORIENTATION surface — read it (after lookup) to understand the
artifact + decide the next action, NOT to re-read discovery fields already seen at lookup time.

PRINT (sections NOT projected to the index — the orientation value-add):
  Summary (full) · Source-Specific Hints (how to use) · Cautions (trust) ·
  Change Impact Hints · Related Sources SIGNAL (out-edge count + relationship_type breakdown
  + a wiki_relations.py --relations pointer; the full out-edges are NOT printed — out-only,
  CR-AIWS-2026-06-054) · any CUSTOM section.
SKIP (already in the index, or a frontmatter mirror):
  Lookup Keys · Knowledge Targets · Profile Mapping · routing frontmatter.
A one-line header carries the trust flag (authority_level / intended_ai_use / status).

Usage:
    python wiki_meta.py --view <source_id>
    python wiki_meta.py --view <source_id> --index <path>   # cross-index (root derived from --index)

Additive: does not change lookup_wiki_source.py (discovery) — this is the META-FIRST companion.
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_relations as br  # noqa: E402  (reuse parse_related_sources — same parser as wiki_relations)
from _common import (  # noqa: E402
    all_index_paths,
    extract_sections,  # noqa: F401  (kept for parity / potential reuse)
    find_ai_work_root,
    locator_str,
    parse_frontmatter,
    read_jsonl,
    read_text,
    resolve_data_file,
    resolve_locator,
)

# Sections the index already carries, or that mirror a frontmatter scalar → skip on meta-read.
SKIP_SECTIONS = {"lookup keys", "knowledge targets", "profile mapping"}
_HEAD_RE = re.compile(r"^(#{2,6})\s+(.+?)\s*$")


def _ordered_sections(body: str) -> list[tuple[str, str]]:
    """Return [(heading, section_text)] in document order for ##..###### headings.

    Content before the first such heading (e.g. the H1 title) is ignored.
    """
    out: list[tuple[str, str]] = []
    cur: str | None = None
    buf: list[str] = []
    for line in body.splitlines():
        m = _HEAD_RE.match(line)
        if m:
            if cur is not None:
                out.append((cur, "\n".join(buf).strip()))
            cur = m.group(2).strip()
            buf = []
        elif cur is not None:
            buf.append(line)
    if cur is not None:
        out.append((cur, "\n".join(buf).strip()))
    return out


def _related_sources_signal(section_text: str, source_id: str) -> str:
    """Render the out-edge SIGNAL for the `## Related Sources` section (CR-AIWS-2026-06-054).

    `--view` shows a FORWARD-ONLY signal — out-edge count + relationship_type breakdown + a
    wiki_relations pointer — NOT the full out-edges. The meta's `## Related Sources` stays the
    authoritative out-edge source; reverse/impact (`## in`) lives ONLY in wiki_relations.py
    --relations. out-count==0 does NOT mean "no relations" (in-edges may exist) — the signal is
    never a gate; the decision to query reverse/impact follows task intent. Reuses the SAME parser
    as wiki_relations.py --expand so the count/types match the relations layer exactly.
    """
    edges = br.parse_related_sources(section_text)
    if not edges:
        return (
            "## Related Sources (out-edges only)\n"
            f"  none declared. in-edges (reverse/impact) unknown here → "
            f"wiki_relations.py --relations {source_id}"
        )
    counts = Counter(e["relationship_type"] for e in edges)
    breakdown = ", ".join(f"{t}×{n}" for t, n in counts.most_common())
    return (
        "## Related Sources (out-edges only — reverse/impact NOT shown here)\n"
        f"  {len(edges)} out-edges: {breakdown}\n"
        f"  → full out+in (with basis notes): wiki_relations.py --relations {source_id}"
        "   (in/reverse-impact lives only there)"
    )


def cmd_view(source_id: str, index_paths: list, project_root: Path) -> int:
    # CR-AIWS-2026-07-051 T2 (Rule 6): resolve across EVERY namespace index, not just index.jsonl —
    # `--view` used to fail with "not found in index" for all 187 AIWS sources.
    idx: dict = {}
    for ip in index_paths:
        idx.update({r.get("source_id", ""): r for r in read_jsonl(ip)})
    rec = idx.get(source_id)
    if rec is None:
        joined = ", ".join(p.name for p in index_paths) or "(none)"
        print(f"error: {source_id} not found in index ({joined})", file=sys.stderr)
        return 2
    # CR-AIWS-2026-07-064 B4 (Rule 9): normalize the index value first (a non-string crashed
    # inside resolve_locator, before any guard), and require a real FILE — exists() is true for a
    # directory, which then blew up read_text() with a traceback instead of this rc=2 diagnostic.
    meta_loc = locator_str(rec.get("meta_locator"))
    if not meta_loc:
        print(f"error: {source_id} has no meta_locator in index", file=sys.stderr)
        return 2
    meta_path = resolve_data_file(meta_loc, project_root)
    if meta_path is None:
        print(f"error: meta file not found or not a file: "
              f"{resolve_locator(meta_loc, project_root)}", file=sys.stderr)
        return 2

    meta, body = parse_frontmatter(read_text(meta_path))
    title = meta.get("title", source_id)
    flags = [f"{k}={meta[k]}" for k in ("authority_level", "intended_ai_use", "status") if meta.get(k)]
    print(f"{source_id} — {title}")
    if flags:
        print("  [" + " · ".join(flags) + "]")
    print()

    skipped: list[str] = []
    for heading, text in _ordered_sections(body):
        h = heading.strip().lower()
        if h in SKIP_SECTIONS:
            skipped.append(heading)
            continue
        if h == "related sources":  # CR-AIWS-2026-06-054 — print the out-edge signal, not the full edges
            print(_related_sources_signal(text, source_id))
            print()
            continue
        print(f"## {heading}")
        if text:
            print(text)
        print()

    if skipped:
        print(f"(skipped — already in index / frontmatter: {', '.join(skipped)})")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(
        description="Meta value-add reader (orientation info; skips index-duplicated sections)")
    p.add_argument("--view", metavar="SOURCE_ID", required=True, help="source_id of the meta to view")
    p.add_argument("--index", help="override index.jsonl path (project root derived from it)")
    ns = p.parse_args()

    if ns.index:
        index_path = Path(ns.index).resolve()
        # <root>/.ai-work/wiki_sources/index.jsonl → derive root for __PROJECT_ROOT__ resolution
        project_root = index_path.parent.parent.parent
        index_paths = [index_path]          # explicit override wins (tests / sandboxes)
    else:
        project_root = find_ai_work_root(Path.cwd())
        index_paths = all_index_paths(project_root / ".ai-work" / "wiki_sources")

    return cmd_view(ns.view, index_paths, project_root)


if __name__ == "__main__":
    raise SystemExit(main())
