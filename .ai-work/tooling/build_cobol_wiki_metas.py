#!/usr/bin/env python3
"""Build wiki source metas from a COBOL/CL/ASP source tree.

The single entrypoint the build-route registry invokes. Three passes:

  PASS 1  scan the WHOLE tree -> symbol sidecar
  PASS 2  emit metas for --root only
  PASS 3  print the standard AIWS follow-up commands; this tool never writes the index

Pass 1 deliberately covers more than pass 2: edges resolve against a system-wide symbol
table, so scanning only the emit scope would turn every call leaving that library into an
unresolved reference.

Writing into the live meta tree requires `--write-live`. Without it output goes to a
temporary directory, so an accidental run cannot overwrite curated metas.

stdlib-only; UTF-8 (cp932-safe).
"""
from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
except Exception:  # noqa: BLE001
    pass

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cobol_wiki import config as cfgmod  # noqa: E402
from cobol_wiki import emit as emitmod  # noqa: E402
from cobol_wiki import filenodes as filenodesmod  # noqa: E402
from cobol_wiki import ids as idsmod  # noqa: E402
from cobol_wiki import objects as objmod  # noqa: E402
from cobol_wiki import scan as scanmod  # noqa: E402
from cobol_wiki import syscmd as syscmdmod  # noqa: E402
from cobol_wiki.resolve import Resolver, load_candidates  # noqa: E402


def find_project_root(override: str = "") -> Path:
    """Explicit flag first, then walk up. A tool that can only derive its root from
    `__file__` cannot be pointed at a sandbox — `tooling_authoring_conventions` R3."""
    if override:
        return Path(override).resolve()
    here = Path(__file__).resolve()
    for parent in [Path.cwd(), *Path.cwd().parents, *here.parents]:
        if (parent / ".ai-work").is_dir():
            return parent
    raise SystemExit("cannot locate project root (no .ai-work/ found)")


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--root", required=True, help="emit scope, e.g. src/system_a/LIB1")
    ap.add_argument("--source-prefix", default="", help="override source_id prefix")
    ap.add_argument("--meta-subdir", default="", help="path under the meta namespace")
    ap.add_argument("--config", default="", help="default: .ai-work/cobol_wiki.config.yml")
    ap.add_argument("--project-root", default="")
    ap.add_argument("--scan-root", default="", help="PASS 1 scope; default: whole source_root")
    ap.add_argument("--out-root", default="", help="meta namespace; default: a temp dir")
    ap.add_argument(
        "--write-live",
        action="store_true",
        help="write into .ai-work/wiki_sources/meta — required, never the default",
    )
    ap.add_argument("--symbols", default="", help="symbol sidecar path")
    ap.add_argument("--rescan", action="store_true", help="ignore an existing sidecar")
    ap.add_argument("--emit-partial", action="store_true",
                    help="mark metas `needs_completion` for a downstream LLM pass")
    ap.add_argument("--updated-at", default="",
                    help="date stamp for the metas: YYYY-MM-DD, or the literal `today`")
    ap.add_argument("--no-preserve-unknown", action="store_true",
                    help="rewrite each meta from scratch, DISCARDING any field or section "
                         "this builder does not own. Off by default: on this project's own "
                         "corpus a from-scratch rewrite of 8857 metas would have dropped "
                         "~15000 real values written by other tools.")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    root = find_project_root(args.project_root)
    cfg = cfgmod.load(Path(args.config) if args.config else root / ".ai-work" / "cobol_wiki.config.yml")
    if args.source_prefix:
        cfg.id_prefix = args.source_prefix
    idsmod.load_overrides_file(cfg, root)
    cfg.load_syscmd_catalog(root)

    if args.write_live:
        out_root = root / ".ai-work" / "wiki_sources" / "meta"
    elif args.out_root:
        out_root = Path(args.out_root)
    else:
        out_root = Path(tempfile.mkdtemp(prefix="cobol_wiki_metas_"))

    sidecar = Path(args.symbols) if args.symbols else root / ".ai-work" / "wiki_sources" / "_cobol_symbols.json"
    symbols = None if args.rescan else scanmod.read_sidecar(sidecar)
    if symbols is None:
        scan_root = Path(args.scan_root) if args.scan_root else root / cfg.source_root
        print(f"PASS 1  scanning {scan_root} …", flush=True)
        symbols = scanmod.scan(root, cfg, scan_root=scan_root, limit=args.limit)
        if not args.dry_run:
            scanmod.write_sidecar(symbols, sidecar)
        print(f"        {len(symbols['files'])} files | {symbols['counts']}")
    else:
        print(f"PASS 1  reusing {sidecar} ({len(symbols['files'])} files) — --rescan to redo")

    resolver = Resolver(load_candidates(root), cfg)

    if not args.updated_at:
        raise SystemExit(
            "--updated-at is required: the date is stamped into every meta, and deriving "
            "it from the clock would make two runs of the same input differ. Pass an "
            "explicit YYYY-MM-DD, or the literal `today` when that is what you mean — a "
            "registered build route uses `today` because pinning a literal date in the "
            "registry would stamp that same day into every meta forever."
        )
    if args.updated_at == "today":
        from datetime import date

        args.updated_at = date.today().isoformat()

    # Synthetic file nodes are derived from references that resolve to nothing, so they
    # must be created AND registered before PASS 2 — otherwise the very edges that
    # justified creating them still fail to resolve and land in Cautions instead.
    file_nodes = {"written": 0}
    if cfg.emit_file_nodes:
        from cobol_wiki.resolve import Candidate  # noqa: E402

        pending = filenodesmod.collect(symbols, cfg, resolver)
        for (system, name), _entry in pending.items():
            resolver.add(
                Candidate(
                    source_id=filenodesmod.file_id(cfg, system, name),
                    system=system, library="", name=name, file_type="",
                    locator=objmod.OBJECT_LOCATOR,
                )
            )
        file_nodes = filenodesmod.emit(
            symbols, cfg, resolver, project_root=root, out_root=out_root,
            meta_subdir=args.meta_subdir, updated_at=args.updated_at, dry_run=args.dry_run,
            found=pending,   # already collected AND registered above — never re-collect
        )
        print(f"        file nodes: {file_nodes['written']} {file_nodes.get('by_system', {})}")

    # Which commands are ubiquitous is a property of THIS tree, so it is measured after
    # the scan and before PASS 2 — emit consults the result to suppress those edges.
    syscmd_used = syscmdmod.collect(symbols, cfg)
    cfg.syscmd_ubiquitous_resolved = syscmdmod.mark_ubiquitous(syscmd_used, symbols, cfg)
    if cfg.syscmd_ubiquitous_resolved:
        print(f"        syscmd ubiquitous (edges suppressed): "
              f"{', '.join(sorted(cfg.syscmd_ubiquitous_resolved))}")

    print(f"PASS 2  emitting under {args.root} -> {out_root}")
    result = emitmod.emit_all(
        symbols, cfg, resolver,
        project_root=root, out_root=out_root, meta_subdir=args.meta_subdir,
        updated_at=args.updated_at, only_under=args.root,
        emit_partial=args.emit_partial, dry_run=args.dry_run,
        preserve_unknown=not args.no_preserve_unknown,
    )
    # Object nodes must exist for the part_of edges the metas just asserted; emitting the
    # artifacts without them leaves every part_of dangling.
    nodes = objmod.emit_nodes(
        symbols, cfg, project_root=root, out_root=out_root, meta_subdir=args.meta_subdir,
        updated_at=args.updated_at, dry_run=args.dry_run, resolver=resolver,
    )
    # Command nodes: the caller metas emitted above already assert `calls` edges pointing
    # at them, so writing the artifacts without these leaves every one of those dangling.
    cmd_nodes = syscmdmod.emit_nodes(
        symbols, cfg, project_root=root, out_root=out_root, meta_subdir=args.meta_subdir,
        updated_at=args.updated_at, dry_run=args.dry_run, found=syscmd_used,
        resolver=resolver,
    ) if cfg.syscmd_emit_caller_edges else {"written": 0, "preserved": []}
    print(f"        metas: {result['written']}{' (dry-run)' if args.dry_run else ''}"
          f" | object nodes: {nodes['module']} module + {nodes['system']} system"
          f" + {cmd_nodes['written']} syscmd")
    if cmd_nodes.get("preserved"):
        print(f"        syscmd hand-authored, NOT overwritten: "
              f"{', '.join(cmd_nodes['preserved'])}")
    print(f"        resolution: {result['resolution']}")
    if result.get("merge"):
        m = result["merge"]
        print(f"        preserved from existing metas: {m.get('fields_preserved', 0)} field(s)"
              f" + {m.get('sections_preserved', 0)} section(s)"
              f" across {m.get('metas_merged', 0)} meta(s)")
    if not args.write_live:
        print("        NOT written to the live meta tree (pass --write-live for that)")

    print("\nPASS 3  follow-up (this tool never writes the index — SOURCE_BUILD_ROUTING_SPEC §3):")
    print("        py .ai-work/tooling/build_wiki_source_index.py")
    print("        py .ai-work/tooling/build_relations.py")
    print("        py .ai-work/tooling/lint_wiki.py --sources-only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
