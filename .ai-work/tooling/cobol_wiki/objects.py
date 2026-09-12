"""Object nodes: the endpoints structural edges point at.

`part_of` needs somewhere to land. Its targets are not artifacts — they are nodes standing
for a library and for a system, carrying the sentinel `artifact_locator: __OBJECT__`
instead of a path. Emitting the artifact metas without these produces a `[BROKEN REF]` for
every single `part_of`, so the two must ship together.

Membership is fully mechanical: a file belongs to its library, a library to its system. No
classifier and no judgement is involved, which is why `part_of` is gated on a structural
invariant rather than on agreement with a reference (whose coverage is partial: 953 edges
in one system against 112 in the other, on corpora of comparable size).
"""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path

#: Object nodes carry this instead of a path. Anything indexing metas by locator must skip
#: them, or they all collapse onto one entry.
OBJECT_LOCATOR = "__OBJECT__"

KNOWLEDGE_TARGETS = ("object_identity", "object_relations")


def module_id(cfg, system: str, library: str) -> str:
    return cfg.module_id_template.format(
        prefix=cfg.id_prefix, system=system.upper(), library=library.upper()
    )


def system_id(cfg, system: str) -> str:
    return cfg.system_id_template.format(prefix=cfg.id_prefix, system=system.upper())


def collect(symbols: dict, cfg) -> dict:
    """Derive the node set and the library-to-library dependency edges.

    A dependency between libraries is asserted only when a real reference crosses them —
    it is a projection of edges that already exist, never an independent guess.
    """
    libs: dict[tuple[str, str], int] = defaultdict(int)
    name_home: dict[tuple[str, str], str] = {}
    for rec in symbols["files"].values():
        if not rec["library"]:
            continue
        libs[(rec["system"], rec["library"])] += 1
        name_home[(rec["system"], rec["name"])] = rec["library"]

    depends: dict[tuple[str, str], set[str]] = defaultdict(set)
    for rec in symbols["files"].values():
        src_lib = rec["library"]
        if not src_lib:
            continue
        for ref in rec.get("refs", []):
            home = name_home.get((rec["system"], ref["name"].upper()))
            if home and home != src_lib:
                depends[(rec["system"], src_lib)].add(home)

    return {
        "libraries": dict(libs),
        "systems": sorted({s for s, _ in libs}),
        "depends": {k: sorted(v) for k, v in depends.items()},
    }


def render_module(cfg, system: str, library: str, file_count: int, depends: list[str],
                  *, updated_at: str) -> tuple[str, str]:
    sid = module_id(cfg, system, library)
    title = f"{library} — {system} (library/module)"
    lines = [
        "---",
        "artifact_type: wiki_source_meta",
        "node_kind: object",
        f"source_id: {sid}",
        f'title: "{title}"',
        f"source_type: {cfg.module_source_type}",
        f"artifact_locator: {OBJECT_LOCATOR}",
        "profile_id: knowledge_object",
        "status: active",
        f"system: {system}",
        f"library: {library}",
        f"updated_at: {updated_at}",
        "---",
        "",
        f"# {title}",
        "",
        "## Summary",
        f"Library **{library}** of the **{system}** system; {file_count} source artifact(s).",
        "",
        "## Knowledge Targets",
    ]
    lines += [f"- {t}" for t in KNOWLEDGE_TARGETS]
    lines += ["", "## Lookup Keys", f"- {library}", f"- {system}", "- library", "- module", ""]
    lines += ["## Related Sources",
              f"- **{system_id(cfg, system)}** — role: part_of — "
              f"library {library} is part of {system} system [asserted]"]
    for dep in depends:
        lines.append(
            f"- **{module_id(cfg, system, dep)}** — role: x:depends_on — "
            f"library {library} depends on {dep} [asserted]"
        )
    return sid, "\n".join(lines).rstrip() + "\n"


def render_system(cfg, system: str, library_count: int, *, updated_at: str) -> tuple[str, str]:
    sid = system_id(cfg, system)
    title = f"{system} — logical system"
    lines = [
        "---",
        "artifact_type: wiki_source_meta",
        "node_kind: object",
        f"source_id: {sid}",
        f'title: "{title}"',
        f"source_type: {cfg.system_source_type}",
        f"artifact_locator: {OBJECT_LOCATOR}",
        "profile_id: knowledge_object",
        "status: active",
        f"system: {system}",
        f"updated_at: {updated_at}",
        "---",
        "",
        f"# {title}",
        "",
        "## Summary",
        f"Logical system **{system}**; {library_count} library/module node(s). Systems are "
        f"independent — a reference is never resolved across them.",
        "",
        "## Knowledge Targets",
    ]
    lines += [f"- {t}" for t in KNOWLEDGE_TARGETS]
    lines += ["", "## Lookup Keys", f"- {system}", "- system", ""]
    # A system is the top of what this pack derives, but an object node with NO out-edge is
    # rejected outright (lint INV-4), so the hierarchy has to continue upward by one step.
    # The project node is authored outside this pack; here we only point at it.
    if cfg.project_id:
        lines += ["## Related Sources",
                  f"- **{cfg.project_id}** — role: part_of — "
                  f"{system} system is part of the project [asserted]"]
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


def emit_nodes(symbols: dict, cfg, *, project_root, out_root, meta_subdir: str,
               updated_at: str, dry_run: bool = False, resolver=None) -> dict:
    """Write module and system nodes. Returns counts."""
    import sys

    tooling = project_root / ".ai-work" / "tooling"
    if str(tooling) not in sys.path:
        sys.path.insert(0, str(tooling.resolve()))
    import _common  # type: ignore

    from .emit import merge_preserving_unknown as _merge

    info = collect(symbols, cfg)
    base = Path(out_root) / (meta_subdir or cfg.source_type)
    written = {"module": 0, "system": 0}

    per_system_libs: dict[str, int] = defaultdict(int)
    for (system, library), count in sorted(info["libraries"].items()):
        per_system_libs[system] += 1
        sid, text = render_module(
            cfg, system, library, count, info["depends"].get((system, library), []),
            updated_at=updated_at,
        )
        if not dry_run:
            path = _target_path(resolver, sid, out_root=out_root, default=
                                base / system / library / f"{library}.module.object.md")
            path.parent.mkdir(parents=True, exist_ok=True)
            text, _m = _merge(text, path, _common)
            _common.write_meta_if_changed(path, text)
        written["module"] += 1

    for system in info["systems"]:
        sid, text = render_system(cfg, system, per_system_libs[system], updated_at=updated_at)
        if not dry_run:
            path = _target_path(resolver, sid, out_root=out_root, default=base / system / f"{system}.system.object.md")
            path.parent.mkdir(parents=True, exist_ok=True)
            text, _m = _merge(text, path, _common)
            _common.write_meta_if_changed(path, text)
        written["system"] += 1

    return written
