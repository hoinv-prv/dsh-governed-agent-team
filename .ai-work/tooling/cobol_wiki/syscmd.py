"""System-command object nodes — the second `calls` population.

A control-language program invokes two very different things and the difference is invisible
in the reference graph: `CALL PGM-PGM0250` reaches another program in the same tree, while
`DLTFILE FILE-WORK1` invokes a command supplied by the operating system. Both are recorded
as `calls`. If only the first is emitted, a CL program's edge list looks complete while
being systematically short — on this corpus 2805 of 3246 `calls` edges out of one system's
CL are command invocations, so the missing population is the LARGER one.

Two properties make these nodes different from every other node the pack emits:

  * **No system.** A platform command belongs to the platform, not to a logical system, so
    one node serves callers in every system. Its id carries no system segment.
  * **No name resolution.** The extractor already established that the line's leading verb
    is a catalogued command, so the target id follows from the name by template. Running it
    through the name resolver would be wrong twice over: the catalog is system-independent
    while resolution is system-scoped, and a command name that happens to match a program
    name would resolve to the program.

Creation is evidence-gated exactly like the synthetic file nodes: the catalog lists what the
platform documents (953 commands here), and a node exists only for the ones some CL in this
tree actually invokes. A catalogue is not evidence of use.
"""
from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

from .objects import OBJECT_LOCATOR

#: `RawRef.kind` marking a command invocation. The handler sets it; the resolver reads it.
SYSCMD_KIND = "SYSCMD"

KNOWLEDGE_TARGETS = ("object_identity", "object_relations")

#: Written under this directory of the meta tree. Leading underscore keeps a name that can
#: never collide with a real library directory.
NODE_DIR = "_SYSTEM_COMMANDS"


def node_id(cfg, name: str) -> str:
    return cfg.syscmd_node_id.format(prefix=cfg.id_prefix, name=name.upper())


def collect(symbols: dict, cfg) -> dict[str, dict]:
    """Commands actually invoked, with who invokes them and how often."""
    used: dict[str, dict] = {}
    for rec in symbols["files"].values():
        for ref in rec.get("refs", []):
            if ref.get("kind") != SYSCMD_KIND:
                continue
            name = ref["name"].upper()
            entry = used.setdefault(
                name, {"calls": 0, "systems": Counter(), "callers": set()}
            )
            entry["calls"] += 1
            entry["systems"][rec["system"]] += 1
            entry["callers"].add(rec["name"])
    return used


def mark_ubiquitous(used: dict[str, dict], symbols: dict, cfg) -> set[str]:
    """Commands invoked so widely that enumerating their callers says nothing.

    Returns the set AND records `ubiquitous` + the caller count on each entry, so the node
    can state plainly how many callers it has instead of listing them. The explicit
    `ubiquitous:` config list is unioned in — a deployment may know a primitive the ratio
    has not caught yet on a small tree.
    """
    total_callers = sum(
        1 for rec in symbols["files"].values()
        if any(r.get("kind") == SYSCMD_KIND for r in rec.get("refs", []))
    )
    chosen = set(cfg.syscmd_ubiquitous)
    for name, entry in used.items():
        entry["caller_count"] = len(entry["callers"])
        if (
            cfg.syscmd_ubiquitous_ratio > 0
            and total_callers
            and entry["caller_count"] / total_callers >= cfg.syscmd_ubiquitous_ratio
        ):
            chosen.add(name)
    for name in chosen:
        if name in used:
            used[name]["ubiquitous"] = True
    return chosen


def render(cfg, name: str, entry: dict, *, updated_at: str) -> tuple[str, str]:
    sid = node_id(cfg, name)
    gloss = cfg.syscmd_gloss.get(name, {})
    english = gloss.get("english") or ""
    reading = gloss.get("reading") or ""
    category = gloss.get("category") or ""
    title = f"{name} — system command" + (f" ({english})" if english else "")
    systems = ", ".join(f"{s} {n}" for s, n in sorted(entry["systems"].items()))

    lines = [
        "---",
        "artifact_type: wiki_source_meta",
        "node_kind: object",
        f"source_id: {sid}",
        f'title: "{title}"',
        "source_type: system_command",
        f"artifact_locator: {OBJECT_LOCATOR}",
        "profile_id: knowledge_object",
        "status: active",
        f"command: {name}",
        f"cl_caller_count: {entry.get('caller_count', len(entry['callers']))}",
    ]
    if category:
        lines.append(f'command_category: "{category}"')
    lines += [f"updated_at: {updated_at}", "---", "", f"# {title}", "", "## Summary"]
    desc = " ".join(x for x in (reading, f"({english})" if english else "") if x).strip()
    lines.append(
        f"Operating-system command `{name}`"
        + (f" — {desc}" if desc else "")
        + (f"; category: {category}" if category else "")
        + f". Invoked {entry['calls']} time(s) by {len(entry['callers'])} control-language "
        f"program(s) in this tree ({systems}). The command is supplied by the platform, "
        f"so this node stands for it and has no source artifact; it belongs to no single "
        f"logical system."
    )
    if entry.get("ubiquitous"):
        lines.append(
            f"Invoked by {entry['caller_count']} of the control-language programs in this "
            f"tree — a ubiquitous primitive. Caller edges are NOT enumerated: an edge that "
            f"is present almost everywhere distinguishes nothing, and enumerating it would "
            f"add one edge per program to the graph. The count above is the fact worth "
            f"keeping."
        )
    lines += ["", "## Knowledge Targets"] + [f"- {t}" for t in KNOWLEDGE_TARGETS]
    keys = [name, "system command"] + ([english] if english else []) + (
        [category] if category else []
    )
    lines += ["", "## Lookup Keys"] + [f"- {k}" for k in keys] + [""]
    # The ONE out-edge this node carries. Caller edges are deliberately absent — the
    # caller's own meta asserts `calls`, and restating them here as `called_by` would double
    # every edge once relations are canonicalized. But an object node with no out-edge at
    # all is rejected, and the documentation reference is the honest one to keep: it says
    # where the command is DEFINED, which is exactly what this node does not contain.
    doc = gloss.get("doc_source_id") or ""
    if doc:
        lines += ["## Related Sources",
                  f"- **{doc}** — role: described_by — "
                  f"`{name}` is documented in the platform command manual [asserted]"]
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


def emit_nodes(symbols: dict, cfg, *, project_root: Path, out_root: Path, meta_subdir: str,
               updated_at: str, dry_run: bool = False, found: dict | None = None,
               resolver=None) -> dict:
    """Write one node per invoked command.

    `## Related Sources` is deliberately EMPTY here. The reverse edge is written on the
    caller's meta as `calls`; restating it as `called_by` on this node would double every
    edge in the graph once relations are canonicalized.

    A node someone WROTE BY HAND is never overwritten. Some commands are real and invoked
    but absent from the vendor manual, so a human documented them against a real artifact —
    measured here at 5 of 112. Those metas carry a genuine `artifact_locator`, whereas every
    node this builder writes carries the `__OBJECT__` sentinel, which is what the guard
    tests. Rewriting one would replace researched content with a mechanical stub.
    """
    tooling = project_root / ".ai-work" / "tooling"
    if str(tooling) not in sys.path:
        sys.path.insert(0, str(tooling.resolve()))
    import _common  # type: ignore

    from .emit import merge_preserving_unknown as _merge

    found = collect(symbols, cfg) if found is None else found
    base = Path(out_root) / (meta_subdir or cfg.source_type) / NODE_DIR
    written, preserved = 0, []
    for name, entry in sorted(found.items()):
        sid, text = render(cfg, name, entry, updated_at=updated_at)
        existing = getattr(resolver, "by_id", {}).get(sid) if resolver is not None else None
        if existing is not None and str(getattr(existing, "locator", "")) != OBJECT_LOCATOR:
            preserved.append(name)
            continue
        if not dry_run:
            path = _target_path(resolver, sid, out_root=out_root, default=base / f"{name}.syscmd.object.md")
            path.parent.mkdir(parents=True, exist_ok=True)
            text, _m = _merge(text, path, _common)
            _common.write_meta_if_changed(path, text)
        written += 1
    return {"written": written, "preserved": preserved}
