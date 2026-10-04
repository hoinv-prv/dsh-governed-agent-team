#!/usr/bin/env python3
"""Build artifact wiki metas for .ts/.tsx/.mts/.cts using stdlib lexical extraction.

Usage: python3 .ai-work/tooling/build_typescript_wiki_metas.py
  --root <src> --source-prefix TS-<PROJECT> --meta-subdir typescript [--dry-run]
Relative module dependencies only. No compiler type resolution or call graph.
Reruns preserve HUMAN curation frontmatter. Index rebuild is a separate operation.
"""
from __future__ import annotations

import argparse
import hashlib
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


# ── extraction (stdlib lexical) ──────────────────────────────────────────────────
def extract_typescript_facts(src: str) -> dict:
    """Conservative lexical extraction, not a TypeScript parser or call graph."""
    # Preserve offsets/newlines while masking comments and string/template literals.
    token = re.compile(r"//[^\n]*|/\*[\s\S]*?\*/|'(?:\\.|[^'\\])*'|\"(?:\\.|[^\"\\])*\"|`(?:\\.|[^`\\])*`")
    masked = token.sub(lambda m: re.sub(r"[^\n]", " ", m.group()), src)
    imports = []
    # Match syntax in masked code; read the literal only at that exact offset.
    literal = re.compile(r"\s*(['\"])([^'\"\n]+)\1")
    patterns = [r"\b(?:import|export)\s+(?:type\s+)?[^;]*?\bfrom\s*",
                r"\bimport\s*(?=['\"])", r"\bimport\s*\(\s*"]
    # Side-effect import uses the mask's whitespace in place of its quote.
    for pattern in [patterns[0], patterns[2], r"\bimport\s+"]:
        for m in re.finditer(pattern, masked):
            # Regex may consume masked whitespace; search from keyword end for side effects,
            # or after from/( for other forms.
            pos = m.end()
            if pattern == r"\bimport\s+":
                pos = m.start() + len('import')
            else:
                pos = len(masked[:pos].rstrip())
            lm = literal.match(src, pos)
            if lm and lm.group(2) not in imports:
                imports.append(lm.group(2))
    declarations = {kind: re.findall(r"\b" + kind + r"\s+([A-Za-z_$][\w$]*)", masked)
                    for kind in ('class', 'interface', 'type', 'enum', 'function')}
    variables = re.findall(r"\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)", masked)
    return {'docstring': '', 'classes': declarations['class'],
            'functions': declarations['function'],
            'decorators': declarations['interface'] + declarations['type'] + declarations['enum'] + variables,
            'imports': imports, 'from_modules': [], 'declarations': declarations, 'variables': variables}


def _module_dotted(path: Path, root: Path) -> str:
    # Keep the extension to distinguish foo.ts from foo.tsx.
    return path.resolve().relative_to(root.resolve()).as_posix()


def resolve_import(specifier: str, origin: Path, paths: dict[Path, str]) -> str | None:
    if not specifier.startswith('.'):
        return None  # package names / tsconfig aliases need compiler configuration
    base = origin.parent / specifier
    candidates = [base]
    if base.suffix in ('.js', '.jsx', '.mjs', '.cjs'):
        candidates.extend(base.with_suffix(ext) for ext in ('.ts', '.tsx', '.mts', '.cts'))
    elif base.suffix not in ('.ts', '.tsx', '.mts', '.cts'):
        candidates.extend(Path(str(base) + ext) for ext in ('.ts', '.tsx', '.mts', '.cts'))
        candidates.extend(base / ('index' + ext) for ext in ('.ts', '.tsx', '.mts', '.cts'))
    for candidate in candidates:
        sid = paths.get(candidate.resolve())
        if sid:
            return sid
    return None


def _slug(dotted: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "-", dotted).strip("-").upper() or "MODULE"


def _lookup_keys(dotted: str, facts: dict) -> list[str]:
    """H1-style compound T1 first (module identity — Q1 spirit), then classes / functions /
    decorators, then type / variable names. Code-noise stopwords dropped; cap 30."""
    keys: list[str] = []
    primary = facts["classes"][0] if facts["classes"] else (
        facts["functions"][0] if facts["functions"] else dotted.split(".")[-1])
    keys.append(f"{dotted} typescript module {primary}".strip())     # compound discriminative T1
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
    primary_kind = "module"
    title = f"{dotted} ({primary_kind})"
    frontmatter = {
        "artifact_type": "wiki_source_meta", "source_id": source_id, "title": title,
        "source_type": "typescript_source", "artifact_locator": artifact_rel,
        "profile_id": "typescript_module", "status": "active",
        "updated_at": source_mtime_iso(artifact),
        "module": dotted, "typescript_kind": primary_kind,
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
        f"TypeScript {primary_kind} `{dotted}`"
        + (f" — {doc1}" if doc1 else "")
        + f". {len(facts['classes'])} class(es), {len(facts['functions'])} function declaration(s),"
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
              f"- types / variables: {', '.join(d for d in facts['decorators'][:12]) or '(none)'}"]

    lines += ["", "## Related Sources"]
    if edges:
        lines.append("<!-- Internal import edges (project-internal modules). -->")
        for sid, tgt_mod in edges:
            lines.append(f"- **{sid}** — role: imports — Module `{dotted}` imports internal "
                         f"module specifier `{tgt_mod}`; changes to its exports can affect this importing module. [asserted]")
    else:
        lines.append("<!-- no project-internal imports detected -->")

    lines += ["", "## Cautions",
              "- Heuristic lexical extraction; declarations may include nested definitions; no AST/type checking.",
              "- Import edges cover relative imports/re-exports and literal dynamic imports only; aliases, packages, require() and computed imports are unresolved.", ""]
    return dump_frontmatter(frontmatter) + "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser(description="Batch-build TypeScript wiki source metas (stdlib lexical extraction; lean + import edges)")
    p.add_argument("--root", required=True, help="Directory to scan recursively for TypeScript files")
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

    project_root = Path(ns.project_root).resolve() if ns.project_root else find_ai_work_root(root)
    ai_work = project_root / ".ai-work"
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

    py_files = sorted((f for f in root.rglob('*') if f.is_file()
                       and f.suffix in ('.ts', '.tsx', '.mts', '.cts')
                       and not {'node_modules', '.git', 'dist', 'build', '.ai-work'}.intersection(f.relative_to(root).parts)),
                      key=lambda f: f.relative_to(root).as_posix())
    if ns.limit > 0:
        py_files = py_files[: ns.limit]

    print(f"scan root       : {root}")
    print(f"meta output dir : {meta_dir}")
    print(f"typescript files    : {len(py_files)}")
    if ns.dry_run:
        print("(dry run — no files written)")

    # pass 1 — dotted module -> source_id
    records: list[dict] = []
    mod_to_sid: dict[str, str] = {}
    errors = 0
    for f in py_files:
        try:
            src = f.read_text(encoding="utf-8", errors="replace")
            facts = extract_typescript_facts(src)
            dotted = _module_dotted(f, root)
            sid = f"{ns.source_prefix}-{_slug(dotted)}-{hashlib.sha256(dotted.encode()).hexdigest()[:12].upper()}"
            try:
                rel = f.resolve().relative_to(project_root).as_posix()
            except ValueError:
                raise ValueError("source must be inside --project-root for portable locators")
            records.append({"f": f, "facts": facts, "dotted": dotted, "sid": sid, "rel": rel})
            mod_to_sid[f.resolve()] = sid
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
            for mod in rec["facts"]["imports"]:
                target = resolve_import(mod, rec['f'], mod_to_sid)
                if target and target != rec['sid'] and target not in seen_t:
                    edges.append((target, mod))
                    seen_t.add(target)
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
