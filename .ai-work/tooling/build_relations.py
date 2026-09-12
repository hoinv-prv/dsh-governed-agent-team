#!/usr/bin/env python3
"""Build the Wiki Relations projection (relations.jsonl) from source metas.

Scans every source meta's `## Related Sources` section and emits a JSONL
projection of typed, directed edges carrying BOTH endpoints, so reverse /
impact queries ("who points AT X / who calls X") are answerable without
re-scanning metas or running fragile repo-wide grep.

relations.jsonl is a PROJECTION — rebuilt from metas, NEVER hand-edited (same
model as build_wiki_source_index.py). It is NOT merged into the slim index.jsonl
(Slim Index invariant). It is a ONE-HOP reverse index only — NOT a graph engine,
NOT transitive closure (Knowledge_Relationship Spec §5 "no precomputed global graph").

CR-AIWS-2026-05-022 (Wiki Relations edge-layer MVP).

Usage:
    python build_relations.py                          # project scope → wiki_sources/relations.jsonl
    python build_relations.py --meta-dir DIR --out FILE # override (testing / ad-hoc)

Each `## Related Sources` line is parsed as one OUT-edge of the declaring meta:
    - **<target_source_id>** — role: <type> — <basis note> [<confidence>]
  role:/type:  → relationship_type (registry: base roles ∪ x: extension; unknown bare = WARNING, never error)
  trailing [asserted|inferred|candidate] → relationship_confidence_note (default asserted)
  scaffold placeholders (`<SRC-id: TODO>` / `<...>`) and HTML comments are skipped.
Legacy untyped line (`- **<id>** — <note>`, no role:/type:) parses as related_to.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (  # noqa: E402
    all_index_paths,
    append_maintenance_log,
    extract_sections,
    find_ai_work_root,
    parse_frontmatter,
    portable_locator,
    meta_roots,
    read_jsonl,
    read_project_config,
    read_text,
    write_jsonl,
)

# Relationship type registry (CR-022 OP-4). Base = the 9 ## Related Sources roles
# (Knowledge_Relationship Spec v0.3 §4) ∪ lineage/lifecycle (§10.1) ∪ representation
# (CR-022 / owner F01 pair). Project extensions use the reserved `x:` prefix and are
# ALWAYS valid (no warning). Unknown BARE types are a WARNING only — never an error.
KNOWN_RELATION_TYPES = {
    # documentary / representation roles (the live 9-role enum)
    "upstream_input", "downstream_navigation", "downstream_target", "triggered_flow",
    "system_foundation", "companion_design", "companion_requirement", "output_template", "related",
    # lineage / lifecycle (§10.1)
    "upstream_of", "downstream_of", "related_to", "reflected_to",
    "superseded_by", "supersedes", "implements", "tests", "clarifies", "input_of",
    # representation register (Object <-> Artifact)
    "represents", "represented_by", "describes", "described_by",
    # domain register (code/object edges) — registered by CR-024 so the inverse-pair
    # canonical forms (calls/contains) and their members don't warn as unknown.
    "calls", "called_by", "reads", "writes", "contains", "part_of", "imports", "uses", "navigates_to",
}
CONFIDENCE_VALUES = {"asserted", "inferred", "candidate"}
DEFAULT_CONFIDENCE = "asserted"
EXTENSION_PREFIX = "x:"

# Inverse pairs (CR-AIWS-2026-05-024): relations.jsonl stores ONE canonical direction per pair.
# A non-canonical form is normalized → canonical by FLIPPING endpoints, then deduped, so
# "A calls B" + "B called_by A" collapse to a single "A calls B" (the reverse is the query
# direction on target_ref — wiki_relations --relations shows it in the `## in` section).
# Documentary roles (upstream_input / downstream_* / companion_* / triggered_flow / ...) are
# NOT inverse pairs → left untouched (their two-sidedness is an authoring-convention matter).
INVERSE_TO_CANONICAL = {
    "called_by": "calls",
    "part_of": "contains",
    "downstream_of": "upstream_of",
    "superseded_by": "supersedes",
    "represented_by": "represents",
    "described_by": "describes",
}
_CONF_RANK = {"asserted": 3, "inferred": 2, "candidate": 1}

_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
_CONF_RE = re.compile(r"\[(asserted|inferred|candidate)\]")
_TYPE_RE = re.compile(r"(?:role|type)\s*:\s*(.+)$", re.IGNORECASE)
EM_DASH = "—"


def parse_related_sources(section_text: str,
                          dropped: list[str] | None = None) -> list[dict[str, str]]:
    """Parse a `## Related Sources` section body into out-edge dicts.

    Returns [{relationship_type, target_ref, relationship_basis_note,
              relationship_confidence_note}], skipping scaffold/placeholder/comment lines.

    CR-AIWS-2026-07-032 T1(b): bullets WITHOUT a **bold** target id are NOT spec §4.3
    shape (canonical AND legacy-untyped both carry a bold id) — they are SKIPPED instead
    of projecting the raw string as a garbage target_ref. Pass `dropped` to collect them
    (build_relations surfaces each as a warning; silent drop is forbidden).
    """
    edges: list[dict[str, str]] = []
    for line in section_text.splitlines():
        s = line.strip()
        if not s.startswith("- "):
            continue
        body = s[2:].strip()
        if body.startswith("<!--") or not body:
            continue
        if body.startswith("(") and body.endswith(")"):
            continue  # placeholder, e.g. "- (none)"

        mb = _BOLD_RE.search(body)
        if not mb:
            # no bold target id → unparseable per spec §4.3; never emit a garbage edge
            if "TODO" not in body and not body.startswith("<"):
                if dropped is not None:
                    dropped.append(body)
            continue
        target = mb.group(1).strip()
        rest = body[mb.end():]
        # skip unresolved scaffold / placeholder targets
        if not target or "TODO" in target or target.startswith("<"):
            continue

        confidence = DEFAULT_CONFIDENCE
        mc = _CONF_RE.search(rest)
        if mc:
            confidence = mc.group(1)
            rest = rest.replace(mc.group(0), "")

        segs = [seg.strip() for seg in rest.split(EM_DASH)]
        segs = [seg for seg in segs if seg]
        rtype: str | None = None
        note_parts: list[str] = []
        for seg in segs:
            mt = _TYPE_RE.match(seg)
            if mt and rtype is None:
                rtype = mt.group(1).strip()
            else:
                note_parts.append(seg)
        if rtype is None:
            rtype = "related_to"  # legacy untyped → related_to (backward compatible)

        edges.append({
            "relationship_type": rtype,
            "target_ref": target,
            "relationship_basis_note": (" " + EM_DASH + " ").join(note_parts).strip(),
            "relationship_confidence_note": confidence,
        })
    return edges


def _type_is_known(rtype: str) -> bool:
    return rtype.startswith(EXTENSION_PREFIX) or rtype in KNOWN_RELATION_TYPES


def _meta_source_id(path: Path) -> tuple[str, str]:
    """Return (source_id, related_sources_section_text) for a meta file."""
    meta, body = parse_frontmatter(read_text(path))
    source_id = meta.get("source_id", path.stem)
    section = extract_sections(body).get("Related Sources", "")
    return source_id, section


def _normalize_and_dedupe(records: list[dict]) -> list[dict]:
    """Normalize inverse-pair edges to their canonical direction, then dedupe (CR-024).

    - An edge whose type is a non-canonical inverse (e.g. called_by) is rewritten to the
      canonical type with endpoints FLIPPED (B called_by A → A calls B).
    - Edges sharing (source_ref, target_ref, relationship_type) merge into one: basis notes
      UNIONED (never silently dropped), strongest confidence kept, declared_in unioned.
      status stays 'active' unless every input is 'superseded'.
    """
    norm: list[dict] = []
    for r in records:
        t = r["relationship_type"]
        if t in INVERSE_TO_CANONICAL:
            r = {
                **r,
                "relationship_type": INVERSE_TO_CANONICAL[t],
                "source_ref": r["target_ref"],
                "target_ref": r["source_ref"],
            }
        norm.append(r)

    groups: dict[tuple, dict] = {}
    order: list[tuple] = []
    for r in norm:
        k = (r["source_ref"], r["target_ref"], r["relationship_type"])
        if k not in groups:
            groups[k] = {"notes": [], "confs": [], "declared": [], "statuses": []}
            order.append(k)
        g = groups[k]
        note = r.get("relationship_basis_note", "")
        if note and note not in g["notes"]:
            g["notes"].append(note)
        g["confs"].append(r.get("relationship_confidence_note", DEFAULT_CONFIDENCE))
        d = r.get("declared_in", "")
        if d and d not in g["declared"]:
            g["declared"].append(d)
        g["statuses"].append(r.get("status", "active"))

    out: list[dict] = []
    for k in order:
        src, tgt, typ = k
        g = groups[k]
        conf = max(g["confs"], key=lambda c: _CONF_RANK.get(c, 0)) if g["confs"] else DEFAULT_CONFIDENCE
        status = "active" if any(s != "superseded" for s in g["statuses"]) else "superseded"
        out.append({
            "relationship_type": typ,
            "source_ref": src,
            "target_ref": tgt,
            "relationship_basis_note": " | ".join(g["notes"]),
            "relationship_confidence_note": conf,
            "declared_in": ",".join(g["declared"]),
            "status": status,
        })
    return out


def build_relations(meta_dir: Path, index_path: Path,
                    namespace: str = "all") -> tuple[list[dict], list[str]]:
    """Build edge records from all metas. Returns (records, warnings).

    CR-AIWS-2026-08-064 C4 — `namespace` selects WHICH meta roots are walked when `meta_dir`
    is one of the project's namespace roots: `all` (legacy CR-07-048: every root),
    `project` (only `meta/`), `aiws` (only `aiws_meta/`). An ad-hoc `--meta-dir` outside the
    namespace roots is always walked alone (namespace ignored). Target-id resolution stays
    cross-namespace via `all_index_paths` regardless of the namespace walked.

    Edges are normalized to ONE canonical direction per inverse pair and deduped (CR-024) —
    relations.jsonl never carries both A→B and its inverse B→A. Edges are NEVER silently
    dropped: a broken target (not in the index) is kept with both endpoints and surfaced as a
    [BROKEN REF] warning; unknown bare types are warned (never errored). Deterministic order.

    CR-AIWS-2026-07-048: the projection walks EVERY meta namespace — the project's `meta/` AND
    the shipped `aiws_meta/` (same blind-spot class lint had before CR-041: edges authored on an
    AIWS meta never reached relations.jsonl, so impact queries could not see them). Target ids
    resolve against BOTH indices for the same reason.
    """
    # CR-AIWS-2026-07-049: namespace resolution comes from the shared helpers (Rule 6) — an
    # explicit --meta-dir (testing / ad-hoc) is honoured as a single root.
    #
    # The membership test is the point (CAP-1027-03, AIP-EXEC-1027). This used to branch on
    # `meta_dir.name == "meta"`, which defeated the ad-hoc escape hatch for exactly the dirs most
    # likely to use it: a hermetic fixture naturally names its dir `meta`, so it took the namespace
    # branch, resolved roots from an unrelated grandparent, found none, and returned ZERO edges with
    # ZERO warnings. That silently disabled the INV-5 named-consumer test — the object-authoring gate.
    _ns_roots = [r.resolve() for r in meta_roots(meta_dir.parent.parent)]
    if meta_dir.resolve() in _ns_roots:
        # CR-AIWS-2026-08-064 C4: `--meta-dir aiws_meta` alone would STILL walk both roots here
        # (membership test above) — the namespace flag is the only way to split the walk.
        if namespace == "project":
            roots = [r for r in _ns_roots if r.name == "meta"]
        elif namespace == "aiws":
            roots = [r for r in _ns_roots if r.name == "aiws_meta"]
        else:
            roots = _ns_roots
    else:
        roots = [meta_dir]
    known_ids: set = set()
    for idx in all_index_paths(index_path.parent):
        known_ids |= {r.get("source_id", "") for r in read_jsonl(idx)}
    raw: list[dict] = []
    warnings: list[str] = []

    # Never scan nothing in silence (CAP-1027-03, AIP-EXEC-1027). An empty walk previously returned
    # `([], [])` — indistinguishable from "scanned fine, no edges declared" — so a misrouted
    # root looked like a clean run to every caller, including the gate test.
    _meta_files = sorted(f for root in roots for f in root.rglob("*.md")
                         if not f.name.endswith(".refresh.md"))
    if not roots:
        warnings.append(
            f"no meta root resolved from {meta_dir} — scanned nothing (0 edges is NOT evidence "
            f"that no edges are declared)")
    elif not _meta_files:
        warnings.append(
            f"meta roots {[str(r) for r in roots]} contain no *.md — scanned nothing "
            f"(0 edges is NOT evidence that no edges are declared)")

    for f in sorted(f for root in roots for f in root.rglob("*.md")):
        if f.name.endswith(".refresh.md"):
            continue  # pending refresh draft, not a meta (CR-AIWS-2026-07-032 T2)
        try:
            source_id, section = _meta_source_id(f)
        except Exception as e:  # noqa: BLE001
            warnings.append(f"failed to read meta {f}: {e}")
            continue
        if not section.strip():
            continue
        dropped: list[str] = []
        for edge in parse_related_sources(section, dropped=dropped):
            raw.append({
                "relationship_type": edge["relationship_type"],
                "source_ref": source_id,
                "target_ref": edge["target_ref"],
                "relationship_basis_note": edge["relationship_basis_note"],
                "relationship_confidence_note": edge["relationship_confidence_note"],
                "declared_in": source_id,
                "status": "active",
            })
        for bad in dropped:
            warnings.append(
                f"[SKIPPED] {source_id}: unparseable Related Sources bullet "
                f"(not spec §4.3 shape — no bold target id): {bad[:100]!r}")

    records = _normalize_and_dedupe(raw)
    records.sort(key=lambda r: (r["source_ref"], r["target_ref"], r["relationship_type"]))

    # Warnings computed on the FINAL (normalized + deduped) edges.
    for r in records:
        rtype, target, src = r["relationship_type"], r["target_ref"], r["source_ref"]
        if not _type_is_known(rtype):
            warnings.append(
                f"unknown relationship_type '{rtype}' in {src} → {target} "
                f"(promote via CR or namespace as x:{rtype})"
            )
        if known_ids and target not in known_ids:
            warnings.append(f"[BROKEN REF] {src} --{rtype}--> {target} (target not in index)")

    return records, warnings


def _write_relations_rebuild_log(ai_work: Path, out: Path, count: int) -> None:
    """Append a WSM maintenance-log entry for the projection rebuild.

    Projection maintenance, not approval/promotion (mirrors build_wiki_source_index.py).
    """
    from datetime import datetime, timezone

    log_path = ai_work / "wiki_sources" / "maintenance_log.jsonl"
    out_locator = portable_locator(out, ai_work.parent)
    entry = {
        "log_id": f"WSMLOG-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-RELATIONS",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "maintenance_model_version": "wsm_v1",
        "action": "relations_rebuilt",
        "source_id": "(relations-projection)",
        "target_artifact": out_locator,
        "old_locator": "",
        "new_locator": out_locator,
        "change_summary": f"Rebuilt Wiki Relations projection with {count} edges.",
        "reason": "Wiki Relations projection rebuild (CR-AIWS-2026-05-022)",
        "impact_level": "unknown",
        "review_decision": "projection_rebuilt",
        "applied_by": "tool:build_relations.py",
        "rollback_hint": "Restore previous relations.jsonl from package/git/history if needed.",
        "runtime_boundary": "relations rebuild is projection maintenance, not Knowledge Hub promotion",
    }
    append_maintenance_log(log_path, entry)


def decide_namespace(ai_work: Path) -> tuple[str, str]:
    """Default namespace rule (CR-AIWS-2026-08-064 C4) — returns (namespace, reason).

    - single-index repo (`wiki_single_index: true`, CR-052): `all` — one merged relations.jsonl,
      a stray relations.aiws.jsonl never changes that (the AIWS repo ships no preset in-repo).
    - dual-index project WITH relations.aiws.jsonl: `project` — the project rebuild must not
      swallow the shipped preset edges (they live in their own file, refreshed by AIWS upgrades).
    - dual-index project WITHOUT the preset: `all` — legacy CR-07-048 behavior, byte-identical."""
    if read_project_config(ai_work)["wiki_single_index"]:  # CR-128 C3: one reader
        return "all", "wiki_single_index=true"
    if (ai_work / "wiki_sources" / "relations.aiws.jsonl").exists():
        return "project", "relations.aiws.jsonl present — preset edges live there"
    return "all", "no relations.aiws.jsonl — legacy merged projection"


def main() -> int:
    p = argparse.ArgumentParser(description="Build the Wiki Relations projection (relations.jsonl)")
    p.add_argument("--meta-dir", help="Override meta directory (default: .ai-work/wiki_sources/meta)")
    p.add_argument("--out", help="Override output path (default: .ai-work/wiki_sources/relations.jsonl)")
    p.add_argument("--index", help="Override index.jsonl path used to resolve targets")
    p.add_argument("--namespace", choices=["project", "aiws", "all"], default=None,
                   help="CR-AIWS-2026-08-064 C4: which meta namespace to walk. aiws → aiws_meta/ only "
                        "→ relations.aiws.jsonl (the shipped preset); project → meta/ only → relations.jsonl; "
                        "all → every root → relations.jsonl (legacy). Default = decide_namespace(): "
                        "single-index repo → all; relations.aiws.jsonl present → project; else all.")
    p.add_argument("--quiet", action="store_true", help="suppress per-warning lines (still prints the count)")
    ns = p.parse_args()

    project_root = find_ai_work_root(Path.cwd())
    ai_work = project_root / ".ai-work"
    wiki_sources = ai_work / "wiki_sources"
    namespace, why = (ns.namespace, "explicit --namespace") if ns.namespace else decide_namespace(ai_work)
    if ns.meta_dir:
        meta_dir = Path(ns.meta_dir).resolve()
    else:
        meta_dir = wiki_sources / ("aiws_meta" if namespace == "aiws" else "meta")
    default_out = wiki_sources / ("relations.aiws.jsonl" if namespace == "aiws" else "relations.jsonl")
    out = Path(ns.out).resolve() if ns.out else default_out
    index_path = Path(ns.index).resolve() if ns.index else (wiki_sources / "index.jsonl")

    if not meta_dir.is_dir():
        print(f"error: meta dir not found: {meta_dir}", file=sys.stderr)
        return 2

    print(f"namespace={namespace} ({why}) → {out.name}")
    records, warnings = build_relations(meta_dir, index_path, namespace=namespace)
    write_jsonl(out, records)

    # Only log to the canonical maintenance log for a real project-scope rebuild.
    if not ns.out:
        _write_relations_rebuild_log(ai_work, out, len(records))

    if warnings and not ns.quiet:
        for w in warnings:
            print(f"  WARN  {w}", file=sys.stderr)
    broken = sum(1 for w in warnings if "[BROKEN REF]" in w)
    unknown = sum(1 for w in warnings if "unknown relationship_type" in w)
    print(f"wrote {len(records)} edges → {out}  (broken refs: {broken}, unknown types: {unknown})")
    print("note: relations.jsonl is a projection — never hand-edit; rebuild after metas change")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
