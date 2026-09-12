#!/usr/bin/env python3
"""Batch-build Wiki Source Metas for Python source files (LEAN + typed import edges).

COMMON library — generic for any Python project; NO project-specific extraction.
Registry-populating builder #2 (CR-AIWS-2026-07-002 H3) — closes the Stage-2 gate that was
waived for lack of a second source_type. Uses the STDLIB `ast` module (no new dependency —
unlike the java builder's optional tree-sitter): a clean AST is always available for Python.
One ARTIFACT meta per .py file (artifact-only, DP6/INV-8 — never node_kind=object).

Curation-state là của HUMAN — builder chỉ được đổi khi flag tương ứng được truyền tường minh;
rerun mặc định carry giá trị cũ từ meta hiện có (CURATION_PRESERVE_FIELDS — CR-AIWS-2026-08-058).

Import edges between project-internal modules are emitted as `## Related Sources`
`- **<sid>** — role: imports — ...` (module A imports module B → A depends on B). Two-pass:
pass 1 maps dotted-module → source_id; pass 2 resolves internal imports to sids.

Build-tool contract (SOURCE_BUILD_ROUTING_SPEC §5): stdlib-only, accepts the registry
placeholders (--root/--source-prefix/--meta-subdir), supports --dry-run, emits a FULL valid
meta (frontmatter + Summary / Knowledge Targets / Lookup Keys). refresh_mode = rerun_tool.

Usage:
  python .ai-work/tooling/build_python_wiki_metas.py \
    --root <path/to/py/pkg> --source-prefix PY-<PROJECT> --meta-subdir python \
    [--system <id> | --common] [--dry-run] [--limit N]
"""
from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (  # noqa: E402
    COMMON_ENGLISH_STOPWORDS,
    WEB_TECH_STOPWORDS,
    carry_curation_state,    # CR-AIWS-2026-08-058: rerun preserves HUMAN curation-state
    dump_frontmatter,
    find_ai_work_root,
    parse_frontmatter,
    read_text,
    source_mtime_iso,
    write_text,
)
from _common import (  # noqa: E402  CR-061 §8.5 · CR-AIWS-2026-08-128 C3
    ProjectProfileUnreadable, read_project_config as _project_config, validate_system,
)

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:  # noqa: BLE001
    pass

_CODE_STOPWORDS = COMMON_ENGLISH_STOPWORDS | WEB_TECH_STOPWORDS
_IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]{2,}")


# ── extraction (stdlib ast) ──────────────────────────────────────────────────
def extract_python_facts(src: str) -> dict:
    """Parse Python source with the stdlib `ast`. Returns module docstring, top-level classes /
    functions, decorators, and imported module names. On a SyntaxError, degrade to an empty
    fact set (the builder never hard-fails on one bad file)."""
    facts = {"docstring": "", "classes": [], "functions": [], "decorators": [],
             "imports": [], "from_modules": []}
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return facts
    facts["docstring"] = (ast.get_docstring(tree) or "").strip()
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            facts["classes"].append(node.name)
            facts["decorators"] += [_dec_name(d) for d in node.decorator_list]
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            facts["functions"].append(node.name)
            facts["decorators"] += [_dec_name(d) for d in node.decorator_list]
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                facts["imports"].append(a.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.level == 0:
                facts["imports"].append(node.module)
                facts["from_modules"].append(node.module)
            elif node.level > 0 and node.module:
                facts["from_modules"].append(node.module)  # relative import (intra-package)
    facts["decorators"] = [d for d in dict.fromkeys(facts["decorators"]) if d]
    return facts


def _dec_name(d: ast.expr) -> str:
    if isinstance(d, ast.Name):
        return d.id
    if isinstance(d, ast.Attribute):
        return d.attr
    if isinstance(d, ast.Call):
        return _dec_name(d.func)
    return ""


def _module_dotted(path: Path, root: Path) -> str:
    """Dotted module path relative to root (e.g. pkg/sub/mod.py -> pkg.sub.mod; __init__.py -> pkg.sub)."""
    try:
        rel = path.resolve().relative_to(root.resolve())
    except ValueError:
        rel = Path(path.name)
    parts = list(rel.with_suffix("").parts)
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts) if parts else path.stem


def _slug(dotted: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "-", dotted).strip("-").upper() or "MODULE"


def _lookup_keys(dotted: str, facts: dict) -> list[str]:
    """H1-style compound T1 first (module identity — Q1 spirit), then classes / functions /
    decorators, then frequency-ranked identifiers. Code-noise stopwords dropped; cap 30."""
    keys: list[str] = []
    primary = facts["classes"][0] if facts["classes"] else (
        facts["functions"][0] if facts["functions"] else dotted.split(".")[-1])
    keys.append(f"{dotted} python module {primary}".strip())     # compound discriminative T1
    for c in facts["classes"]:
        keys.append(f"{c} class {dotted.split('.')[-1]}")
    for fn in facts["functions"][:10]:
        keys.append(fn)
    for d in facts["decorators"][:6]:
        keys.append(d)
    # order-preserving dedup + stopword filter for single tokens
    out: list[str] = []
    seen: set[str] = set()
    for k in keys:
        k = k.strip()
        low = k.lower()
        if not k or low in seen:
            continue
        if " " not in k and low in _CODE_STOPWORDS:
            continue
        out.append(k)
        seen.add(low)
    return out[:30]


def build_meta_markdown(*, artifact: Path, artifact_rel: str, dotted: str, facts: dict,
                        source_id: str, edges: list[tuple[str, str]], system: str | None,
                        existing_fm: dict | None = None) -> str:
    primary_kind = "package" if artifact.name == "__init__.py" else "module"
    title = f"{dotted} ({primary_kind})"
    frontmatter = {
        "artifact_type": "wiki_source_meta", "source_id": source_id, "title": title,
        "source_type": "python_source", "artifact_locator": artifact_rel,
        "profile_id": "python_module", "status": "active",
        "updated_at": source_mtime_iso(artifact),
        "module": dotted, "python_kind": primary_kind,
    }
    if system:
        frontmatter["system"] = system
    # CR-AIWS-2026-08-058 — curation-state là của HUMAN: rerun (refresh_mode=rerun_tool) carry các
    # curation field từ meta cũ thay vì đè mất; builder chỉ đổi khi flag truyền tường minh.
    if existing_fm:
        carry_curation_state(frontmatter, existing_fm)
        if not system and str(existing_fm.get("system", "")).strip():
            frontmatter["system"] = str(existing_fm["system"]).strip()

    doc1 = facts["docstring"].splitlines()[0].strip() if facts["docstring"] else ""
    summary = (
        f"Python {primary_kind} `{dotted}`"
        + (f" — {doc1}" if doc1 else "")
        + f". {len(facts['classes'])} class(es), {len(facts['functions'])} top-level function(s),"
        + f" {len(edges)} internal import edge(s)."
    )

    lines = [f"# Wiki Source Meta — {title}", "", "## Summary", summary, "",
             "## Knowledge Targets", "- module", "- class", "- dependency", "",
             "## Lookup Keys"]
    lines += [f"- {k}" for k in _lookup_keys(dotted, facts)]

    lines += ["", "## Source Facts",
              f"- module: {dotted}",
              f"- classes ({len(facts['classes'])}): {', '.join(facts['classes'][:25]) or '(none)'}",
              f"- functions ({len(facts['functions'])}): {', '.join(facts['functions'][:25]) or '(none)'}",
              f"- decorators: {', '.join('@' + d for d in facts['decorators'][:12]) or '(none)'}"]

    lines += ["", "## Related Sources"]
    if edges:
        lines.append("<!-- Internal import edges (project-internal modules). -->")
        for sid, tgt_mod in edges:
            lines.append(f"- **{sid}** — role: imports — Module `{dotted}` imports internal "
                         f"module `{tgt_mod}`; open it to follow the dependency. [asserted]")
    else:
        lines.append("<!-- no project-internal imports detected -->")

    lines += ["", "## Cautions",
              "- Stdlib `ast` extraction; top-level classes/functions only (nested defs not surfaced).",
              "- Import edges cover project-internal modules only; dynamic imports are not detected.", ""]
    return dump_frontmatter(frontmatter) + "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser(description="Batch-build Python wiki source metas (stdlib ast; lean + import edges)")
    p.add_argument("--root", required=True, help="Directory to scan recursively for .py files")
    p.add_argument("--source-prefix", required=True, help="source_id prefix, e.g. PY-AIWS")
    p.add_argument("--meta-subdir", required=True, help="Subdir under wiki_sources/meta/ to write into")
    p.add_argument("--project-root", default=None, help="Project root for relative artifact_locator")
    p.add_argument("--system", default=None, metavar="ID",
                   help="Multi-system (CR-017/061): tag metas to system <id>. In a multi_system "
                        "project pass --system or --common.")
    p.add_argument("--common", action="store_true",
                   help="Multi-system: mark metas system-agnostic/common (no system key).")
    p.add_argument("--dry-run", action="store_true", help="Scan + report without writing metas")
    p.add_argument("--limit", type=int, default=0, help="Limit number of files (0 = no limit)")
    ns = p.parse_args()

    root = Path(ns.root).resolve()
    if not root.is_dir():
        print(f"error: root not a directory: {root}", file=sys.stderr)
        return 2

    ai_work = find_ai_work_root(root) / ".ai-work"
    project_root = Path(ns.project_root).resolve() if ns.project_root else ai_work.parent
    meta_dir = ai_work / "wiki_sources" / "meta" / ns.meta_subdir

    # Multi-system resolution (CR-AIWS-2026-06-061 §8.5) — a new meta writer must be system-aware.
    if ns.system and ns.common:
        print("error: --system and --common are mutually exclusive", file=sys.stderr)
        return 2
    try:
        cfg = _project_config(ai_work)
    except ProjectProfileUnreadable as e:                # CR-AIWS-2026-08-128 C3
        print(f"error: .ai-work/project_profile.yml exists but could not be parsed: {e}",
              file=sys.stderr)
        return 2
    system_val: str | None = None
    if ns.system:
        system_val = ns.system.strip()
        if not validate_system(system_val, cfg):
            print(f"error: --system {system_val!r} not in project systems {cfg['systems']}.", file=sys.stderr)
            return 2
    elif ns.common:
        system_val = None
    elif cfg["multi_system"]:
        print("error: multi_system project — pass --system <id> or --common.", file=sys.stderr)
        return 2

    py_files = [f for f in sorted(root.rglob("*.py")) if f.is_file()]
    if ns.limit > 0:
        py_files = py_files[: ns.limit]

    print(f"scan root       : {root}")
    print(f"meta output dir : {meta_dir}")
    print(f"python files    : {len(py_files)}")
    if ns.dry_run:
        print("(dry run — no files written)")

    # pass 1 — dotted module -> source_id
    records: list[dict] = []
    mod_to_sid: dict[str, str] = {}
    errors = 0
    for f in py_files:
        try:
            src = f.read_text(encoding="utf-8", errors="replace")
            facts = extract_python_facts(src)
            dotted = _module_dotted(f, root)
            sid = f"{ns.source_prefix}-{_slug(dotted)}"
            try:
                rel = f.resolve().relative_to(project_root).as_posix()
            except ValueError:
                rel = f.resolve().as_posix()
            records.append({"f": f, "facts": facts, "dotted": dotted, "sid": sid, "rel": rel})
            mod_to_sid[dotted] = sid
        except Exception as e:  # noqa: BLE001
            errors += 1
            print(f"  ERROR (pass1) {f}: {e}", file=sys.stderr)

    # pass 2 — resolve internal imports + write
    written = 0
    total_edges = 0
    for rec in records:
        try:
            edges: list[tuple[str, str]] = []
            seen_t: set[str] = set()
            for mod in rec["facts"]["imports"] + rec["facts"]["from_modules"]:
                # match longest internal module prefix (mod or a parent package)
                cand = mod
                while cand:
                    if cand in mod_to_sid and mod_to_sid[cand] != rec["sid"] and cand not in seen_t:
                        edges.append((mod_to_sid[cand], cand))
                        seen_t.add(cand)
                        break
                    cand = cand.rsplit(".", 1)[0] if "." in cand else ""
            total_edges += len(edges)
            # CR-AIWS-2026-08-058: read the existing meta (if any) so curated frontmatter carries over.
            _meta_path = meta_dir / f"{rec['sid']}.md"
            _existing_fm: dict = {}
            if _meta_path.exists():
                try:
                    _existing_fm, _ = parse_frontmatter(read_text(_meta_path))
                except Exception:  # noqa: BLE001 — unreadable old meta must not break the build
                    _existing_fm = {}
            md = build_meta_markdown(artifact=rec["f"], artifact_rel=rec["rel"], dotted=rec["dotted"],
                                     facts=rec["facts"], source_id=rec["sid"], edges=edges, system=system_val,
                                     existing_fm=_existing_fm)
            if not ns.dry_run:
                write_text(_meta_path, md)
            written += 1
        except Exception as e:  # noqa: BLE001
            errors += 1
            print(f"  ERROR (pass2) {rec['rel']}: {e}", file=sys.stderr)

    print(f"metas {'(would write)' if ns.dry_run else 'written'}: {written}; import edges: {total_edges}; errors: {errors}")
    print("note: rebuild index with build_wiki_source_index.py; a custom builder never writes the index.")
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
