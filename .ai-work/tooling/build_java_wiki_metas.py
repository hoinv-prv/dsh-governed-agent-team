#!/usr/bin/env python3
"""Batch-build Wiki Source Metas for Java source files (LEAN + typed edges + endpoints).

COMMON library — generic for any Java project; NO project-specific extraction.

Phase 1 (CR-AIWS-2026-06-045): pragmatic regex-based extraction (stdlib-only). One ARTIFACT
meta per .java file (artifact-only, DP6/INV-8 — never node_kind=object).

Dependency edges between project-internal files use the STRONGEST evidence per
(source,target) pair: calls > uses > imports (related fallback). Inheritance is a
separate axis: x:extends / x:implements.

Also extracts REST endpoints (@RequestMapping base + @{Get,Post,Put,Delete,Patch}Mapping)
into a `## Endpoints` section, so a cross-layer matcher can link FE calls -> BE controllers.

(Phase 2, CR-AIWS-2026-06-046, swaps the regex engine for tree-sitter-java with a regex fallback.)

Curation-state là của HUMAN — builder chỉ được đổi khi flag tương ứng được truyền tường minh;
rerun mặc định carry giá trị cũ từ meta hiện có (CURATION_PRESERVE_FIELDS — CR-AIWS-2026-08-058).

Usage:
  python .ai-work/tooling/build_java_wiki_metas.py \
    --root <path/to/java/src> --source-prefix JAVA-<PROJECT> --meta-subdir java [--dry-run] [--limit N]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (  # noqa: E402
    apply_enrich,            # CR-AIWS-2026-06-048: shared Step-2 enrich engine (project-owned enrich)
    carry_curation_state,    # CR-AIWS-2026-08-058: rerun preserves HUMAN curation-state
    dump_frontmatter,
    find_ai_work_root,
    parse_frontmatter,
    read_text,
    source_mtime_iso,
    write_text,
    # CR-AIWS-2026-06-043 Change A: code-key stopwords (built-in COMMON_ENGLISH ∪ WEB_TECH; EXCLUDES
    # PROJECT_DESIGN so code words event/state/message/status + identifiers are preserved).
    COMMON_ENGLISH_STOPWORDS,
    WEB_TECH_STOPWORDS,
)

# CR-AIWS-2026-06-046 (Phase 2): OPTIONAL tree-sitter-java AST engine — the one sanctioned exception
# to stdlib-only (CLAUDE.md §6), scoped to THIS common builder. Used when installed; ALWAYS falls back
# to the stdlib regex extractor below when absent or on any AST error, so the builder never hard-fails.
try:
    from tree_sitter import Language as _TSLanguage, Parser as _TSParser  # noqa: E402
    import tree_sitter_java as _tsjava  # noqa: E402
    _TS_LANGUAGE = _TSLanguage(_tsjava.language())
    _HAVE_TS = True
except Exception:  # noqa: BLE001 — any import/build failure → regex fallback
    _HAVE_TS = False

_TS_TYPE_DECL_KINDS = {
    "class_declaration": "class",
    "interface_declaration": "interface",
    "enum_declaration": "enum",
    "record_declaration": "record",
    "annotation_type_declaration": "@interface",
}
_TS_MAPPING_HTTP = {
    "GetMapping": "GET", "PostMapping": "POST", "PutMapping": "PUT",
    "DeleteMapping": "DELETE", "PatchMapping": "PATCH",
}
_CAP_RE = re.compile(r"\b([A-Z][A-Za-z0-9_]*)\b")


def _strip_comments_and_strings(src: str) -> str:
    out: list[str] = []
    i = 0
    n = len(src)
    while i < n:
        c = src[i]
        nxt = src[i + 1] if i + 1 < n else ""
        if c == "/" and nxt == "/":
            j = src.find("\n", i)
            if j == -1:
                break
            out.append(" " * (j - i)); i = j; continue
        if c == "/" and nxt == "*":
            j = src.find("*/", i + 2)
            if j == -1:
                out.append(" " * (n - i)); break
            span = src[i:j + 2]
            out.append("".join(ch if ch == "\n" else " " for ch in span)); i = j + 2; continue
        if c == '"':
            out.append('""'); j = i + 1
            while j < n:
                if src[j] == "\\" and j + 1 < n:
                    j += 2; continue
                if src[j] == '"' or src[j] == "\n":
                    break
                j += 1
            i = j + 1 if j < n and src[j] == '"' else j; continue
        if c == "'":
            out.append("''"); j = i + 1
            while j < n:
                if src[j] == "\\" and j + 1 < n:
                    j += 2; continue
                if src[j] == "'" or src[j] == "\n":
                    break
                j += 1
            i = j + 1 if j < n and src[j] == "'" else j; continue
        out.append(c); i += 1
    return "".join(out)


PACKAGE_RE = re.compile(r"^\s*package\s+([\w\.]+)\s*;", re.MULTILINE)
IMPORT_RE = re.compile(r"^\s*import\s+(static\s+)?([\w\.\*]+)\s*;", re.MULTILINE)
TYPE_DECL_RE = re.compile(
    r"(?P<mods>(?:\b(?:public|private|protected|abstract|final|static|sealed|non-sealed|strictfp)\b\s+)*)"
    r"(?P<kind>class|interface|enum|record|@interface)\s+(?P<name>[A-Za-z_][\w]*)"
    r"(?:\s*<[^{]*?>)?(?:\s*\([^)]*\))?"
    r"(?:\s+extends\s+(?P<ext>[\w\.<>,\s]+?))?"
    r"(?:\s+implements\s+(?P<impl>[\w\.<>,\s]+?))?\s*\{",
    re.DOTALL,
)
ANNOTATION_RE = re.compile(r"@([A-Za-z_][\w\.]*)\s*(?:\([^)]*\))?")
METHOD_RE = re.compile(
    r"(?P<anno>(?:@[A-Za-z_][\w\.]*\s*(?:\([^)]*\))?\s*)*)"
    r"(?P<mods>(?:\b(?:public|private|protected|static|final|abstract|synchronized|native|default|strictfp)\b\s+)*)"
    r"(?:<[^>]{0,200}>\s+)?(?P<ret>[\w\.$<>\[\],\s?]+?)\s+(?P<name>[A-Za-z_][\w]*)\s*"
    r"\((?P<params>[^)]*)\)\s*(?:throws\s+[\w\.,\s]+)?\s*(?:\{|;)",
)
METHOD_SKIP_NAMES = {
    "if", "for", "while", "switch", "catch", "return", "new", "throw",
    "else", "do", "try", "synchronized", "case", "break", "continue", "assert", "yield",
}
NEW_RE = re.compile(r"\bnew\s+([A-Za-z_][\w\.]*)\s*[\(<]")
# NOTE: no project-specific function-tag regex — the builder is a COMMON library (CR-045 guardrail).

# evidence for edge precedence
DECL_RE = re.compile(r"\b([A-Z][A-Za-z0-9_]*)(?:<[^>{};()]*>)?(?:\[\])?\s+([a-z_][A-Za-z0-9_]*)\s*[;=,)]")
INSTANCE_CALL_RE = re.compile(r"\b([a-z_][A-Za-z0-9_]*)\s*\.\s*[A-Za-z_]\w*\s*\(")
STATIC_CALL_RE = re.compile(r"\b([A-Z][A-Za-z0-9_]*)\s*\.\s*[A-Za-z_]\w*\s*\(")
CAP_TOKEN_RE = re.compile(r"\b([A-Z][A-Za-z0-9_]*)\b")

# endpoints
BASE_MAPPING_RE = re.compile(r"@RequestMapping\s*\(\s*(?:value\s*=\s*)?\"([^\"]*)\"")
METHOD_MAPPING_RE = re.compile(
    r"@(Get|Post|Put|Delete|Patch)Mapping\s*(?:\(\s*(?:value\s*=\s*|path\s*=\s*)?\"([^\"]*)\")?")


def _class_level_annotations(pre_text: str) -> list[str]:
    annos: list[str] = []
    for line in reversed(pre_text.splitlines()):
        s = line.strip()
        if not s:
            continue
        if s.startswith("@"):
            m = ANNOTATION_RE.match(s)
            if m:
                annos.append(m.group(1))
            continue
        break
    return list(reversed(annos))


def _split_commalist(s: str) -> list[str]:
    out: list[str] = []; depth = 0; buf: list[str] = []
    for ch in s:
        if ch == "<":
            depth += 1; buf.append(ch)
        elif ch == ">":
            depth = max(0, depth - 1); buf.append(ch)
        elif ch == "," and depth == 0:
            out.append("".join(buf).strip()); buf = []
        else:
            buf.append(ch)
    if buf:
        t = "".join(buf).strip()
        if t:
            out.append(t)
    return [x for x in out if x]


def _norm_path(base: str, sub: str) -> str:
    full = "/" + "/".join(p for p in (base + "/" + sub).split("/") if p)
    return full or "/"


def _extract_facts_regex(src: str) -> dict:
    """Structured facts about a Java source file (regex/stdlib — Phase-1 engine + Phase-2 fallback)."""
    stripped = _strip_comments_and_strings(src)
    pkg_m = PACKAGE_RE.search(stripped)
    package = pkg_m.group(1) if pkg_m else ""
    imports = [m.group(2) for m in IMPORT_RE.finditer(stripped)]

    types: list[dict] = []
    for m in TYPE_DECL_RE.finditer(stripped):
        annos = _class_level_annotations(stripped[: m.start()])
        ext = (m.group("ext") or "").strip(); impl = (m.group("impl") or "").strip()
        types.append({
            "kind": m.group("kind"), "name": m.group("name"),
            "modifiers": (m.group("mods") or "").split(),
            "extends": ext, "implements": _split_commalist(impl) if impl else [],
            "annotations": annos,
        })

    methods: list[dict] = []
    used_short: set[str] = set()
    for m in METHOD_RE.finditer(stripped):
        name = m.group("name")
        if name in METHOD_SKIP_NAMES:
            continue
        ret = (m.group("ret") or "").strip()
        if not ret or ret.endswith("=") or ret.split()[0] in METHOD_SKIP_NAMES:
            continue
        if any(tok in {"new", "throw", "return"} for tok in ret.split()):
            continue
        params = (m.group("params") or "").strip()
        methods.append({"name": name, "return_type": ret,
                        "modifiers": (m.group("mods") or "").split(),
                        "annotations": ANNOTATION_RE.findall(m.group("anno") or ""), "params": params})
        # DTO/types referenced as return/param types → "uses"
        used_short.update(CAP_TOKEN_RE.findall(ret))
        used_short.update(CAP_TOKEN_RE.findall(params))

    # edge-precedence evidence
    var_type: dict[str, str] = {}
    for m in DECL_RE.finditer(stripped):
        var_type[m.group(2)] = m.group(1)
    called_short: set[str] = set()
    for m in INSTANCE_CALL_RE.finditer(stripped):
        recv = m.group(1)
        if recv in var_type:
            called_short.add(var_type[recv])
    for m in STATIC_CALL_RE.finditer(stripped):
        called_short.add(m.group(1))
    new_short: set[str] = {t.split("<")[0].strip().rsplit(".", 1)[-1] for t in
                           (mm.group(1) for mm in NEW_RE.finditer(stripped))}
    used_short.update(new_short)
    used_short.update(var_type.values())
    # generic args in extends/implements (e.g. JpaRepository<Member, Long> → Member) count as "uses"
    for t in types:
        used_short.update(CAP_TOKEN_RE.findall(t["extends"]))
        for _impl in t["implements"]:
            used_short.update(CAP_TOKEN_RE.findall(_impl))

    # endpoints (controllers) — read from RAW src: path strings are blanked in `stripped`
    base = ""
    bm = BASE_MAPPING_RE.search(src)
    if bm:
        base = bm.group(1)
    endpoints: list[tuple[str, str]] = []
    for m in METHOD_MAPPING_RE.finditer(src):
        http = m.group(1).upper()
        sub = m.group(2) or ""
        endpoints.append((http, _norm_path(base, sub)))

    return {
        "package": package, "imports": imports, "types": types, "methods": methods,
        "called_short": called_short, "used_short": used_short, "endpoints": endpoints,
    }


def _extract_facts_treesitter(src: str) -> dict:
    """Structured facts via tree-sitter-java AST (CR-AIWS-2026-06-046). SAME dict shape as
    `_extract_facts_regex` so everything downstream is engine-agnostic. Raises on parser/grammar
    trouble → the caller (`extract_java_facts`) falls back to regex."""
    data = src.encode("utf-8")
    root = _TSParser(_TS_LANGUAGE).parse(data).root_node

    def txt(n) -> str:
        return data[n.start_byte:n.end_byte].decode("utf-8", "replace")

    def first_cap(s: str) -> str:
        m = _CAP_RE.search(s)
        return m.group(1) if m else ""

    def modifiers_of(n):
        for c in n.children:
            if c.type == "modifiers":
                return c
        return None

    def anno_names(mods) -> list:
        out: list[str] = []
        if mods is None:
            return out
        for c in mods.children:
            if c.type in ("marker_annotation", "annotation"):
                nm = c.child_by_field_name("name")
                if nm is not None:
                    out.append(txt(nm).rsplit(".", 1)[-1])
        return out

    def mod_keywords(mods) -> list:
        if mods is None:
            return []
        return [w for w in txt(mods).split() if not w.startswith("@")]

    def first_string_arg(anno) -> str:
        args = anno.child_by_field_name("arguments")
        if args is None:
            return ""
        for c in args.children:
            if c.type == "string_literal":
                return txt(c).strip('"').strip("'")
            if c.type == "element_value_pair":
                for cc in c.children:
                    if cc.type == "string_literal":
                        return txt(cc).strip('"').strip("'")
        return ""

    state = {"package": ""}
    imports: list[str] = []
    types: list[dict] = []
    methods: list[dict] = []
    used_short: set[str] = set()
    var_type: dict[str, str] = {}
    inst_objs: list[str] = []
    static_objs: set[str] = set()
    endpoints: list[tuple[str, str]] = []
    base = {"path": ""}

    def walk(n):
        t = n.type
        if t == "package_declaration":
            for c in n.named_children:
                if c.type in ("scoped_identifier", "identifier"):
                    state["package"] = txt(c)
                    break
            return
        if t == "import_declaration":
            for c in n.named_children:
                if c.type in ("scoped_identifier", "identifier"):
                    imports.append(txt(c))
                    break
            return
        if t in _TS_TYPE_DECL_KINDS:
            mods = modifiers_of(n)
            nm = n.child_by_field_name("name")
            ext = ""
            sup = n.child_by_field_name("superclass")
            if sup is not None:
                for c in sup.named_children:
                    if c.type in ("type_identifier", "scoped_type_identifier", "generic_type"):
                        ext = txt(c)
                        break
            impl: list[str] = []
            ifc = n.child_by_field_name("interfaces")
            if ifc is not None:
                for tl in ifc.children:
                    if tl.type == "type_list":
                        impl.extend(txt(it) for it in tl.named_children)
            types.append({
                "kind": _TS_TYPE_DECL_KINDS[t],
                "name": txt(nm) if nm is not None else "",
                "modifiers": mod_keywords(mods),
                "extends": ext,
                "implements": impl,
                "annotations": anno_names(mods),
            })
            used_short.update(_CAP_RE.findall(ext))
            for it in impl:
                used_short.update(_CAP_RE.findall(it))
            if mods is not None:
                for c in mods.children:
                    if c.type == "annotation":
                        anm = c.child_by_field_name("name")
                        if anm is not None and txt(anm).rsplit(".", 1)[-1] == "RequestMapping":
                            base["path"] = first_string_arg(c)
            for c in n.children:
                walk(c)
            return
        if t == "method_declaration":
            mods = modifiers_of(n)
            nm = n.child_by_field_name("name")
            rt = n.child_by_field_name("type")
            params = n.child_by_field_name("parameters")
            ret_txt = txt(rt) if rt is not None else ""
            par_txt = txt(params)[1:-1].strip() if params is not None else ""
            methods.append({
                "name": txt(nm) if nm is not None else "",
                "return_type": ret_txt,
                "modifiers": mod_keywords(mods),
                "annotations": anno_names(mods),
                "params": par_txt,
            })
            used_short.update(_CAP_RE.findall(ret_txt))
            used_short.update(_CAP_RE.findall(par_txt))
            if mods is not None:
                for c in mods.children:
                    if c.type in ("annotation", "marker_annotation"):
                        anm = c.child_by_field_name("name")
                        if anm is None:
                            continue
                        short = txt(anm).rsplit(".", 1)[-1]
                        if short in _TS_MAPPING_HTTP:
                            sub = first_string_arg(c) if c.type == "annotation" else ""
                            endpoints.append((_TS_MAPPING_HTTP[short], _norm_path(base["path"], sub)))
            for c in n.children:
                walk(c)
            return
        if t == "formal_parameter":
            ty = n.child_by_field_name("type")
            nm = n.child_by_field_name("name")
            if ty is not None and nm is not None:
                cap = first_cap(txt(ty))
                if cap:
                    var_type[txt(nm)] = cap
            for c in n.children:
                walk(c)
            return
        if t in ("field_declaration", "local_variable_declaration"):
            ty = n.child_by_field_name("type")
            ty_short = first_cap(txt(ty)) if ty is not None else ""
            for c in n.children:
                if c.type == "variable_declarator":
                    vn = c.child_by_field_name("name")
                    if vn is not None and ty_short:
                        var_type[txt(vn)] = ty_short
            if ty is not None:
                used_short.update(_CAP_RE.findall(txt(ty)))
            for c in n.children:
                walk(c)
            return
        if t == "method_invocation":
            obj = n.child_by_field_name("object")
            if obj is not None and obj.type == "identifier":
                ot = txt(obj)
                if ot[:1].islower():
                    inst_objs.append(ot)
                elif ot[:1].isupper():
                    static_objs.add(ot)
            for c in n.children:
                walk(c)
            return
        if t == "object_creation_expression":
            ty = n.child_by_field_name("type")
            if ty is not None:
                cap = first_cap(txt(ty))
                if cap:
                    used_short.add(cap)
            for c in n.children:
                walk(c)
            return
        for c in n.children:
            walk(c)

    walk(root)
    called_short = {var_type[o] for o in inst_objs if o in var_type} | static_objs
    used_short.update(var_type.values())
    return {
        "package": state["package"], "imports": imports, "types": types, "methods": methods,
        "called_short": called_short, "used_short": used_short, "endpoints": endpoints,
    }


def extract_java_facts(src: str) -> dict:
    """Engine-agnostic facts: tree-sitter-java AST when available (CR-046), else stdlib regex (CR-045).
    Per-file fallback — any AST error degrades to regex so this COMMON builder never hard-fails."""
    if _HAVE_TS:
        try:
            return _extract_facts_treesitter(src)
        except Exception:  # noqa: BLE001
            return _extract_facts_regex(src)
    return _extract_facts_regex(src)


def _slug_fqcn(fqcn: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "-", fqcn).strip("-")


def _java_concept_keys(facts: dict) -> list[str]:
    """English concept/synonym terms so English design/coding queries surface this file."""
    annos = {a for t in facts["types"] for a in t["annotations"]}
    name = facts["types"][0]["name"] if facts["types"] else ""
    kind = facts["types"][0]["kind"] if facts["types"] else ""
    pkg = "." + facts["package"] + "."
    c: list[str] = []
    if "RestController" in annos or "Controller" in annos or name.endswith("Controller") or ".web." in pkg:
        c += ["REST controller", "API endpoint", "HTTP endpoint", "web layer"]
    if "Service" in annos or name.endswith("Service") or ".service." in pkg:
        c += ["service layer", "business logic"]
    if "Repository" in annos or name.endswith("Repository") or ".repo." in pkg:
        c += ["JPA repository", "data access", "repository"]
    if "Entity" in annos or ".domain." in pkg:
        c += ["JPA entity", "domain model", "entity"]
    if ".dto." in pkg or kind == "record":
        c += ["DTO", "request response model"]
    if "Configuration" in annos or name.endswith("Config"):
        c += ["configuration"]
    if name.endswith("Test") or name.endswith("Tests"):
        c += ["unit test", "test"]
    # NOTE: no universal "Java/Spring Boot/backend" — non-discriminative (every file) + dilutes those queries.
    return c


def _lookup_keys(facts: dict, fqcn: str, enrich: dict | None = None) -> list[str]:
    keys: list[str] = []
    if facts["package"]:
        keys.append(facts["package"])
    keys.append(fqcn)
    for t in facts["types"]:
        keys.append(t["name"])
        keys.extend(t["annotations"])
        if t["extends"]:
            keys.append(t["extends"].split("<")[0].strip())
        for impl in t["implements"]:
            keys.append(impl.split("<")[0].strip())
    keys.extend(_java_concept_keys(facts))   # English concepts — kept high for the 30-key index cap
    if enrich:   # CR-AIWS-2026-06-048: project Step-2 enrich augmentations (high priority; already stopword-filtered)
        keys.extend(enrich.get("extra_concepts", []))
        keys.extend(enrich.get("extra_lookup_keys", []))
    keys.extend(f"{h} {p}" for h, p in facts.get("endpoints", [])[:12])
    for m in facts["methods"][:20]:
        keys.append(m["name"])
    seen: set[str] = set(); out: list[str] = []
    for k in keys:
        k = k.strip()
        if k and k not in seen:
            seen.add(k); out.append(k)
    # CR-AIWS-2026-06-043 Change A: drop single-token common-English/web-tech noise; keep multi-word keys
    # (e.g. "GET /orders") and identifiers/class names. No profile path at this call site → built-in code
    # set only (functionally = code_key_stopwords with empty config).
    code_stop = COMMON_ENGLISH_STOPWORDS | WEB_TECH_STOPWORDS
    out = [k for k in out if (" " in k) or (k.lower() not in code_stop)]
    return out[:50]


def resolve_edges(facts: dict, fqcn_to_sid: dict, self_sid: str) -> list[tuple[str, str, str]]:
    """Internal dependency edges, strongest type per target: calls > uses > imports.
    Inheritance on its own axis: x:extends / x:implements. External deps → no edge.
    """
    short_to_fqcn = {imp.rsplit(".", 1)[-1]: imp for imp in facts["imports"]}

    def resolve(fqcn: str):
        parts = fqcn.split(".")
        while parts:
            cand = ".".join(parts)
            if cand in fqcn_to_sid:
                return fqcn_to_sid[cand]
            parts = parts[:-1]
        return None

    edges: list[tuple[str, str, str]] = []
    seen: set[str] = set()

    # inheritance (own structural axis) FIRST — claim target so the dep loop won't double-emit
    primary = facts["types"][0] if facts["types"] else None
    if primary and primary["extends"]:
        base = primary["extends"].split("<")[0].strip().rsplit(".", 1)[-1]
        sid = resolve(short_to_fqcn.get(base, base))
        if sid and sid != self_sid:
            seen.add(sid); edges.append(("x:extends", sid, f"extends `{base}`"))
    if primary:
        for impl in primary["implements"]:
            base = impl.split("<")[0].strip().rsplit(".", 1)[-1]
            sid = resolve(short_to_fqcn.get(base, base))
            if sid and sid != self_sid and sid not in seen:
                seen.add(sid); edges.append(("x:implements", sid, f"implements `{base}`"))

    # dependency edges from imports, typed by strongest evidence: calls > uses > imports
    for imp in facts["imports"]:
        short = imp.rsplit(".", 1)[-1]
        if short == "*":
            continue
        sid = resolve(imp)
        if not sid or sid == self_sid or sid in seen:
            continue
        if short in facts["called_short"]:
            rtype, basis = "x:calls", f"calls `{short}`"
        elif short in facts["used_short"]:
            rtype, basis = "x:uses", f"uses type `{short}`"
        else:
            rtype, basis = "x:imports", f"imports `{imp}`"
        seen.add(sid)
        edges.append((rtype, sid, basis))
    return edges


def build_meta_markdown(*, artifact: Path, artifact_rel: str, facts: dict,
                        source_id: str, edges: list[tuple[str, str, str]],
                        enrich: dict | None = None,
                        existing_fm: dict | None = None) -> str:
    primary = facts["types"][0] if facts["types"] else None
    primary_name = primary["name"] if primary else artifact.stem
    kind = primary["kind"] if primary else "java"
    fqcn = f"{facts['package']}.{primary_name}" if facts["package"] else primary_name
    eps = facts.get("endpoints", [])
    title = f"{primary_name} ({kind})"

    frontmatter = {
        "artifact_type": "wiki_source_meta", "source_id": source_id, "title": title,
        "source_type": "java_source", "artifact_locator": artifact_rel,
        "profile_id": "java_class", "status": "active",
        "updated_at": source_mtime_iso(artifact),  # CR-AIWS-2026-06-024: source-backed = source file mtime
        "package": facts["package"], "fqcn": fqcn, "java_kind": kind,
    }
    # CR-AIWS-2026-08-058 — curation-state là của HUMAN: rerun (refresh_mode=rerun_tool) carry các
    # curation field từ meta cũ thay vì đè mất; builder chỉ đổi khi flag truyền tường minh.
    if existing_fm:
        carry_curation_state(frontmatter, existing_fm)

    summary = (
        f"{kind} `{fqcn}`"
        + (f" extends `{primary['extends']}`" if primary and primary["extends"] else "")
        + (f" implements {', '.join('`' + i + '`' for i in primary['implements'])}"
           if primary and primary["implements"] else "")
        + f". {len(facts['methods'])} method(s); {len(edges)} dep edge(s)"
        + (f"; {len(eps)} endpoint(s)" if eps else "")
        + "."
    )

    lines = [f"# Wiki Source Meta — {title}", "", "## Summary", summary, "",
             "## Knowledge Targets", "- java_type", "- method", "- dependency"]
    if eps:
        lines.append("- endpoint")
    lines += ["", "## Lookup Keys"]
    lines += [f"- {k}" for k in _lookup_keys(facts, fqcn, enrich)]

    annos: list[str] = []
    for t in facts["types"]:
        for a in t["annotations"]:
            if a not in annos:
                annos.append(a)
    method_names = [m["name"] for m in facts["methods"]][:25]
    lines += ["", "## Source Facts",
              f"- package: {facts['package'] or '(default)'}",
              f"- fqcn: {fqcn}", f"- kind: {kind} {primary_name}",
              f"- annotations: {', '.join('@' + a for a in annos) if annos else '(none)'}",
              f"- methods ({len(facts['methods'])}): {', '.join(method_names) if method_names else '(none detected)'}"
              + (" …" if len(facts["methods"]) > 25 else "")]

    if eps:
        lines += ["", "## Endpoints"]
        for http, path in eps:
            lines.append(f"- {http} {path}")

    lines += ["", "## Related Sources"]
    if edges:
        lines.append("<!-- Dependency edges (project-internal); type = strongest evidence calls>uses>imports. -->")
        for rtype, sid, basis in edges:
            lines.append(f"- **{sid}** — role: {rtype} — {basis} [asserted]")
    else:
        lines.append("<!-- no project-internal dependencies detected -->")
    # CR-AIWS-2026-06-048: project Step-2 enrich extra edges (from the optional code-hook). Empty → unchanged.
    for e in (enrich or {}).get("extra_edges", []):
        if isinstance(e, dict):
            tgt = e.get("target") or e.get("sid") or ""
            role = e.get("role") or e.get("rtype") or "x:related"
            basis = e.get("basis") or "project enrich"
            lines.append(f"- **{tgt}** — role: {role} — {basis} [asserted]")
        elif str(e).strip():
            lines.append(f"- {str(e).strip()}")

    # CR-AIWS-2026-06-048: project Step-2 enrich extra sections (from the optional code-hook). Each a full block.
    for sec in (enrich or {}).get("extra_sections", []):
        block = str(sec).strip()
        if block:
            lines += ["", block]

    lines += ["", "## Cautions",
              "- Regex-based extraction (stdlib); verify against the .java artifact.",
              "- Dep edges cover project-internal types only; edge type is a heuristic (calls/uses/imports).", ""]
    return dump_frontmatter(frontmatter) + "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser(description="Batch-build Java wiki source metas (lean + typed edges + endpoints)")
    p.add_argument("--root", required=True,
                   help="Directory to scan recursively for .java files")
    p.add_argument("--source-prefix", required=True,
                   help="source_id prefix, e.g. JAVA-YPO")
    p.add_argument("--meta-subdir", required=True,
                   help="Subdirectory under wiki_sources/meta/ to write metas into")
    p.add_argument("--project-root", default=None,
                   help="Project root for relative artifact_locator (default: .ai-work parent)")
    p.add_argument("--dry-run", action="store_true",
                   help="Scan + report without writing metas")
    p.add_argument("--limit", type=int, default=0,
                   help="Limit number of files (0 = no limit)")
    ns = p.parse_args()

    root = Path(ns.root).resolve()
    if not root.is_dir():
        print(f"error: root not a directory: {root}", file=sys.stderr); return 2

    ai_work = find_ai_work_root(root) / ".ai-work"
    project_root = Path(ns.project_root).resolve() if ns.project_root else ai_work.parent
    meta_dir = ai_work / "wiki_sources" / "meta" / ns.meta_subdir
    # CR-AIWS-2026-06-048: Step-2 enrich reads the PROJECT's java_class profile (project-owned `enrich:`
    # block + optional code-hook). Absent / no enrich: → apply_enrich returns empty → Step-1 output unchanged.
    profile_path = ai_work / "wiki_sources" / "profiles" / "java_class.yml"
    java_files = sorted(root.rglob("*.java"))
    if ns.limit > 0:
        java_files = java_files[: ns.limit]

    print(f"scan root       : {root}")
    print(f"meta output dir : {meta_dir}")
    print(f"java files      : {len(java_files)}")
    if ns.dry_run:
        print("(dry run — no files written)")

    records: list[dict] = []
    fqcn_to_sid: dict[str, str] = {}
    errors = 0
    for f in java_files:
        try:
            src = f.read_text(encoding="utf-8", errors="replace")
            facts = extract_java_facts(src)
            primary = facts["types"][0] if facts["types"] else None
            primary_name = primary["name"] if primary else f.stem
            fqcn = f"{facts['package']}.{primary_name}" if facts["package"] else primary_name
            sid = f"{ns.source_prefix}-{_slug_fqcn(fqcn)}"
            try:
                rel = f.resolve().relative_to(project_root).as_posix()
            except ValueError:
                rel = f.resolve().as_posix()
            records.append({"f": f, "facts": facts, "sid": sid, "rel": rel})
            fqcn_to_sid[fqcn] = sid
        except Exception as e:  # noqa: BLE001
            errors += 1; print(f"  ERROR (pass1) {f}: {e}", file=sys.stderr)

    written = 0; total_edges = 0; total_eps = 0
    type_counts: dict[str, int] = {}
    for rec in records:
        try:
            edges = resolve_edges(rec["facts"], fqcn_to_sid, rec["sid"])
            total_edges += len(edges); total_eps += len(rec["facts"]["endpoints"])
            for rt, _, _ in edges:
                type_counts[rt] = type_counts.get(rt, 0) + 1
            # CR-AIWS-2026-06-048: Step-2 project enrich (declarative profile `enrich:` + optional hook).
            # Engine-agnostic, graceful — any trouble degrades to empty (byte-identical Step-1 output).
            try:
                enrich = apply_enrich(rec["facts"], profile_path,
                                      rec["f"].read_text(encoding="utf-8", errors="replace"))
            except Exception as e:  # noqa: BLE001 — never let enrich break the build
                enrich = None
                print(f"  WARN enrich skipped {rec['rel']}: {e}", file=sys.stderr)
            # CR-AIWS-2026-08-058: read the existing meta (if any) so curated frontmatter carries over.
            _meta_path = meta_dir / f"{rec['sid']}.md"
            _existing_fm: dict = {}
            if _meta_path.exists():
                try:
                    _existing_fm, _ = parse_frontmatter(read_text(_meta_path))
                except Exception:  # noqa: BLE001 — unreadable old meta must not break the build
                    _existing_fm = {}
            md = build_meta_markdown(artifact=rec["f"], artifact_rel=rec["rel"],
                                     facts=rec["facts"], source_id=rec["sid"], edges=edges, enrich=enrich,
                                     existing_fm=_existing_fm)
            if not ns.dry_run:
                write_text(_meta_path, md)
            written += 1
        except Exception as e:  # noqa: BLE001
            errors += 1; print(f"  ERROR (pass2) {rec['rel']}: {e}", file=sys.stderr)

    print(f"done: written={written} edges={total_edges} endpoints={total_eps} errors={errors}")
    print(f"edge types: {dict(sorted(type_counts.items()))}")
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
