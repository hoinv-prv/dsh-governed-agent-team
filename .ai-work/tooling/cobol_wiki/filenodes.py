"""Synthetic nodes for files that are accessed but never defined.

A program can assign a file that has no definition artifact anywhere in the tree — work
files, print devices, tape units, files owned by another system. Without a node for those,
every access edge pointing at one is simply lost: the resolver reports `not_found`, the
reference goes to `## Cautions`, and the relation disappears from the graph. In the
reference corpus these nodes carry 7104 of the 9379 `x:accesses` edges, so they are the
majority of that role rather than an edge case.

The node is deliberately thin. It asserts only what the references themselves prove: the
file was accessed, by which libraries, and under which category. It does NOT claim a
location, a format, or a definition — that is exactly the information missing, and
inventing it would turn an honest placeholder into a false record.

Creation is evidence-gated: a node exists only where at least one real reference could not
resolve to a defined artifact. Nothing is pre-created from a catalogue.
"""
from __future__ import annotations

import sys
from collections import Counter, defaultdict
from pathlib import Path

from .objects import KNOWLEDGE_TARGETS, OBJECT_LOCATOR, system_id

#: Roles whose unresolved targets are files rather than programs or copybooks.
FILE_ROLES = ("reads", "x:accesses", "writes")


def file_id(cfg, system: str, name: str) -> str:
    return cfg.file_id_template.format(
        prefix=cfg.id_prefix, system=system.upper(), name=name.upper()
    )


def collect(symbols: dict, cfg, resolver) -> dict:
    """Find file references that resolve to nothing, grouped by (system, name).

    Only unresolved ones. A reference that already lands on a defined artifact must NOT
    also mint a synthetic node — that would split one file across two identities and
    silently halve every count taken over it.
    """
    seen: dict[tuple[str, str], dict] = {}
    for rec in symbols["files"].values():
        for ref in rec.get("refs", []):
            if ref["role"] not in FILE_ROLES:
                continue
            res = resolver.resolve(
                ref["name"], system=rec["system"], role=ref["role"],
                library_hint=ref.get("lib_hint", ""),
            )
            # Only a name that resolves to NOTHING earns a node. An AMBIGUOUS name already
            # has real candidates; minting a synthetic identity for it adds a third one,
            # makes the ambiguity permanent, and splits the file across two ids.
            if res.ok or res.reason != "not_found":
                continue
            key = (rec["system"], ref["name"].upper())
            entry = seen.setdefault(
                key, {"libraries": set(), "categories": Counter(), "refs": 0}
            )
            entry["refs"] += 1
            if rec["library"]:
                entry["libraries"].add(rec["library"])
            kind = ref.get("kind", "")
            if "/" in kind:
                entry["categories"][kind.split("/", 1)[1].split("->")[-1]] += 1
    return seen


def render(cfg, system: str, name: str, entry: dict, *, updated_at: str) -> tuple[str, str]:
    sid = file_id(cfg, system, name)
    category = entry["categories"].most_common(1)[0][0] if entry["categories"] else "unknown"
    libs = ", ".join(sorted(entry["libraries"])) or "(unknown)"
    title = f"{name} — {system} (physical file)"
    lines = [
        "---",
        "artifact_type: wiki_source_meta",
        "node_kind: object",
        f"source_id: {sid}",
        f'title: "{title}"',
        f"source_type: {cfg.file_node_source_type}",
        f"artifact_locator: {OBJECT_LOCATOR}",
        "profile_id: knowledge_object",
        "status: active",
        f"system: {system}",
        f"file_category: {category}",
        f"updated_at: {updated_at}",
        "---",
        "",
        f"# {title}",
        "",
        "## Summary",
        f"Physical file `{name}` ({category}) accessed by programs in the **{system}** "
        f"system; seen in library/libraries: {libs}. No definition artifact for it exists "
        f"in the scanned tree — this node stands for the file so its access edges are not "
        f"lost, and asserts nothing beyond what those {entry['refs']} reference(s) show.",
        "",
        "## Knowledge Targets",
    ]
    lines += [f"- {t}" for t in KNOWLEDGE_TARGETS]
    lines += ["", "## Lookup Keys", f"- {name}", f"- {system}", f"- {category}", ""]
    lines += [
        "## Related Sources",
        f"- **{system_id(cfg, system)}** — role: part_of — "
        f"physical file {name} belongs to {system} system [asserted]",
    ]
    return sid, "\n".join(lines).rstrip() + "\n"



def _target_path(resolver, sid: str, default: "Path", *, out_root=None) -> "Path":
    """Where to write an object node: its existing meta if one exists, else our own name.

    A project that already carries this node under a different file name must not end up
    with two files claiming one `source_id` — the index counts that as a duplicate and the
    graph gains a phantom node.

    Confinement fix, adopted with the preset (CR-AIWS-2026-08-026): the redirect is confined to `out_root`.
    Without that bound, a build aimed at a temp out-root wrote into the LIVE tree —
    silently, because the caller had every reason to believe `--out-root` meant what it
    says. That defeats the candidate-then-review pattern this project uses for wiki
    content. Inside the same tree the redirect still applies, because the duplicate-id
    problem it solves is real.
    """
    cand = getattr(resolver, "by_id", {}).get(sid) if resolver is not None else None
    existing = getattr(cand, "meta_path", "") if cand is not None else ""
    if not existing:
        return default
    if out_root is not None:
        try:
            Path(existing).resolve().relative_to(Path(out_root).resolve())
        except ValueError:
            return default          # the existing meta lives outside this build's tree
    return Path(existing)


def emit(symbols: dict, cfg, resolver, *, project_root: Path, out_root: Path,
         meta_subdir: str, updated_at: str, dry_run: bool = False,
         found: dict | None = None) -> dict:
    """Write the nodes. `found` MUST be passed when the caller already registered them.

    Re-collecting here after the caller registered the nodes with the resolver would find
    almost nothing: the references that justified each node now resolve — to that very
    node. Measured on this corpus, that self-cancelling second pass wrote 36 nodes where
    175 were due.
    """
    tooling = project_root / ".ai-work" / "tooling"
    if str(tooling) not in sys.path:
        sys.path.insert(0, str(tooling.resolve()))
    import _common  # type: ignore

    from .emit import merge_preserving_unknown as _merge

    found = collect(symbols, cfg, resolver) if found is None else found
    base = Path(out_root) / (meta_subdir or cfg.source_type)
    by_system: dict[str, int] = defaultdict(int)
    for (system, name), entry in sorted(found.items()):
        sid, text = render(cfg, system, name, entry, updated_at=updated_at)
        if not dry_run:
            path = _target_path(resolver, sid, out_root=out_root, default=
                                base / system / cfg.file_node_dir / f"{name}.file.object.md")
            path.parent.mkdir(parents=True, exist_ok=True)
            text, _m = _merge(text, path, _common)
            _common.write_meta_if_changed(path, text)
        by_system[system] += 1
    return {"written": sum(by_system.values()), "by_system": dict(by_system)}
