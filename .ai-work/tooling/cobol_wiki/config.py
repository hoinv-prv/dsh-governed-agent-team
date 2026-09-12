"""Config loading + validation for the cobol-wiki pack.

Everything project-specific lives in one YAML file; the builder code stays generic.
This module is the ONLY place that knows the config file's shape — it validates up
front so a bad declaration fails before a single source file is scanned, rather than
producing thousands of wrong metas.

## Why the schema looks the way it does

The project is stdlib-only (no PyYAML). Config is parsed with the AIWS YAML-subset
parser (`_common.parse_frontmatter`), which was measured on 2026-08-07 to have hard
limits that the schema is designed around:

  WORKS   nested block mappings; flow lists `[a, b]` at top level or inside a plain
          nested mapping; block-list items whose fields are all scalars; `true`/`false`
          coercion; regex kept verbatim (so patterns use SINGLE backslashes).

  BROKEN  flow mappings `{k: v}` anywhere -> come back as a plain string.
          flow lists inside a block-list item -> come back as a plain string.
          block lists inside a block-list item -> SILENTLY CORRUPT the outer list
          (the child's `- ` lines are absorbed as siblings, yielding empty `{}` items).

The last one is why `_check_parser_corruption` exists: the parser does not raise, so a
malformed config would otherwise run to completion on garbage. Inside a list item, a
multi-value field is therefore declared as a comma-separated STRING and split here
(`_as_list`), which round-trips safely through the subset parser.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any


class ConfigError(Exception):
    """Raised when the config is missing, unparsable, or internally inconsistent."""


# Fields that hold a list but live inside a block-list item, so they are authored as
# comma-separated scalars (see module docstring).
_CSV_FIELDS = ("when_ext", "skip_prefixes")

# A stringified flow LIST: `[a, b]`.
_FLOW_LIST_RE = re.compile(r"^\s*\[.*\]\s*$", re.DOTALL)
# A stringified flow MAPPING: `{k: v, ...}`. The `:` is what separates a mangled mapping
# from a legitimate template string like `{prefix}-{system}-{name}`, whose braces are
# placeholders and never contain a colon.
_FLOW_MAP_RE = re.compile(r"^\s*\{[^{}]*:[^{}]*\}\s*$", re.DOTALL)


def _looks_mangled(text: str) -> bool:
    """True when a scalar is really a collection the subset parser failed to build."""
    return bool(_FLOW_LIST_RE.match(text) or _FLOW_MAP_RE.match(text))


def _load_yaml(path: Path) -> dict:
    """Parse a plain .yml (no `---` fence) via the AIWS subset parser."""
    try:
        import sys

        # Walk up from the config AND from cwd looking for the AIWS tooling dir. A fixed
        # `parents[N]` offset breaks the moment the config is addressed relatively — the
        # same class of defect `tooling_authoring_conventions` R3 is about.
        seen: list[Path] = []
        for start in (path.resolve(), Path.cwd()):
            for parent in [start, *start.parents]:
                cand = parent / ".ai-work" / "tooling"
                if (cand / "_common.py").is_file():
                    seen.append(cand)
                    break
        for cand in seen:
            if str(cand) not in sys.path:
                sys.path.insert(0, str(cand))
        from _common import parse_frontmatter, read_text  # type: ignore
    except Exception as exc:  # noqa: BLE001
        raise ConfigError(
            "cannot import .ai-work/tooling/_common.py — the pack requires an AIWS "
            f"installation (>= v1.1.x) in the target project ({exc})"
        ) from exc

    if not path.is_file():
        raise ConfigError(f"config not found: {path}")
    meta, _ = parse_frontmatter("---\n" + read_text(path).strip("\n") + "\n---\n")
    if not isinstance(meta, dict) or not meta:
        raise ConfigError(f"config parsed empty: {path}")
    return meta


def _check_parser_corruption(node: Any, where: str, problems: list[str]) -> None:
    """Detect the subset parser's silent-corruption signature.

    A collection nested inside a block-list item makes the parser emit empty `{}` items
    and truncated scalars into the OUTER list instead of failing. Catch that here so the
    operator gets a pointed message instead of a builder that quietly does the wrong thing.
    """
    if isinstance(node, list):
        # A flow list written across several lines is truncated to its FIRST line, with the
        # opening bracket left stuck to item 0 and every continuation line dropped. Nothing
        # raises; the list is simply short. Keep flow lists on one line, or use block style.
        if node and isinstance(node[0], str) and node[0].lstrip().startswith("["):
            problems.append(
                f"{where}[0] = {node[0]!r} still carries its opening bracket — a flow list "
                f"spanning MULTIPLE LINES was truncated to its first line and the rest was "
                f"silently dropped. Put it on one line, or use a block list."
            )
        for i, item in enumerate(node):
            if isinstance(item, dict) and not item:
                problems.append(
                    f"{where}[{i}]: empty item — almost certainly a nested list/mapping "
                    f"inside a list item, which this parser cannot represent. Use a "
                    f"comma-separated string for multi-value fields."
                )
            else:
                _check_parser_corruption(item, f"{where}[{i}]", problems)
    elif isinstance(node, dict):
        for k, v in node.items():
            if str(k).lstrip().startswith("- "):
                # A comment line indented to ITEM depth between a key and its first `- `
                # makes the parser fold the whole list into a mapping, swallowing the dash
                # into the first key. Nothing raises; the caller just gets a mapping where
                # it expected a list. Put such comments at KEY depth instead.
                problems.append(
                    f"{where}.{k}: a list was flattened into a mapping (the `- ` ended up "
                    f"inside the key). This happens when a comment sits between the key "
                    f"and its first item at item indentation — move it above the key."
                )
                continue
            if isinstance(v, str) and _looks_mangled(v):
                problems.append(
                    f"{where}.{k}: value came back as the STRING {v!r}. Flow "
                    f"collections do not survive this parser in that position — use a "
                    f"block mapping, or a comma-separated string inside a list item."
                )
            else:
                _check_parser_corruption(v, f"{where}.{k}", problems)


# Role names in this corpus contain a colon (`x:uses`, `x:accesses`), but the subset
# parser splits every line on its FIRST colon — quoting does not help, so a colon can
# never appear in a config KEY. Roles are therefore written with an underscore and
# canonicalized here.
_ROLE_KEY_ALIASES = {
    "x_uses": "x:uses",
    "x_accesses": "x:accesses",
    "x_depends_on": "x:depends_on",
}


def _canonical_role(key: str) -> str:
    """Map a colon-free config key back to the canonical role name."""
    return _ROLE_KEY_ALIASES.get(key.strip().lower(), key.strip())


def _as_list(value: Any) -> list[str]:
    """Normalize a multi-value field to a list of trimmed strings.

    Accepts a real list (top-level flow/block list) or a comma-separated string (the
    only form that survives inside a block-list item).
    """
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    text = str(value).strip()
    if _FLOW_LIST_RE.match(text):
        text = text[1:-1]
    return [part.strip() for part in text.split(",") if part.strip()]


def _as_int(value: Any, field: str, default: int) -> int:
    """The subset parser does not coerce ints — every scalar arrives as a string."""
    if value is None:
        return default
    try:
        return int(str(value).strip())
    except ValueError as exc:
        raise ConfigError(f"{field}: expected an integer, got {value!r}") from exc


def _as_bool(value: Any, default: bool) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in ("true", "yes", "1", "on")


class Config:
    """Validated, normalized view of the pack config.

    Attribute access is deliberate: every consumer reads typed fields, so a schema
    change surfaces here rather than as a KeyError deep inside a handler.
    """

    def __init__(self, raw: dict, path: Path) -> None:
        self.path = path
        self.raw = raw

        problems: list[str] = []
        _check_parser_corruption(raw, "config", problems)
        if problems:
            raise ConfigError(
                f"{path}: the YAML subset parser mangled this file —\n  "
                + "\n  ".join(problems)
            )

        self.source_root: str = str(raw.get("source_root") or "src")
        self.systems: list[str] = _as_list(raw.get("systems"))
        self.source_type: str = str(raw.get("source_type") or "cobol_source")
        self.profile_id: str = str(raw.get("profile_id") or self.source_type)

        sid = raw.get("source_id") or {}
        if not isinstance(sid, dict):
            raise ConfigError("source_id: expected a mapping")
        self.id_prefix: str = str(sid.get("prefix") or "SRC-PRJ")
        self.id_template: str = str(
            sid.get("template") or "{prefix}-{system}-{library}-{name}"
        )
        self.id_overrides: list[dict] = [
            o for o in (sid.get("overrides") or []) if isinstance(o, dict)
        ]
        #: Optional CSV of `system,library,file_type,template` rows. A corpus with dozens
        #: of drifted libraries would otherwise bury the config under near-identical rules.
        self.id_overrides_file: str = str(sid.get("overrides_file") or "")

        # Object-node ids. `part_of` targets these, so they must exist before the artifact
        # metas that point at them — otherwise every part_of becomes a broken reference.
        obj = raw.get("objects") or {}
        self.module_id_template: str = str(obj.get("module_id") or "SRC-MODULE-{system}-{library}")
        self.system_id_template: str = str(obj.get("system_id") or "SRC-SYSTEM-{system}")
        self.emit_part_of: bool = _as_bool(obj.get("emit_part_of"), True)
        # Synthetic nodes for accessed-but-undefined files. In the reference corpus these
        # carry the MAJORITY of access edges, so omitting them loses most of that role.
        self.file_id_template: str = str(obj.get("file_id") or "SRC-FILE-{system}-{name}")
        self.file_node_source_type: str = str(obj.get("file_node_source_type") or "prj_file")
        self.file_node_dir: str = str(obj.get("file_node_dir") or "_FILES")
        # `source_type` must be a value the lint recognizes or one a profile declares.
        # `module` is canonical; a system node has no canonical type of its own, so it
        # is a `concept` — which is what the reference corpus calls it too.
        self.module_source_type: str = str(obj.get("module_source_type") or "module")
        self.system_source_type: str = str(obj.get("system_source_type") or "concept")
        # The system node's own parent. A logical system belongs to a project, and without
        # that edge the node has NO out-edge at all — which `lint_wiki` rejects (INV-4: an
        # object node must never be empty). The project node itself is authored outside
        # this pack; here we only point at it.
        self.project_id: str = str(obj.get("project_id") or "")
        self.emit_file_nodes: bool = _as_bool(obj.get("emit_file_nodes"), True)

        ft = raw.get("file_type") or {}
        if not isinstance(ft, dict):
            raise ConfigError("file_type: expected a mapping")
        by_ext = ft.get("by_extension") or {}
        if not isinstance(by_ext, dict):
            raise ConfigError(
                "file_type.by_extension: expected a block mapping (flow `{...}` does "
                "not survive the subset parser)"
            )
        self.by_extension: dict[str, str] = {
            str(k).upper().lstrip("."): str(v) for k, v in by_ext.items()
        }
        self.sniff: list[dict] = []
        for rule in ft.get("sniff") or []:
            if not isinstance(rule, dict):
                continue
            pattern = str(rule.get("pattern") or "")
            if not pattern:
                raise ConfigError("file_type.sniff: a rule is missing `pattern`")
            try:
                compiled = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
            except re.error as exc:
                raise ConfigError(f"file_type.sniff pattern {pattern!r}: {exc}") from exc
            self.sniff.append(
                {
                    "when_ext": [e.upper().lstrip(".") for e in _as_list(rule.get("when_ext"))],
                    "re": compiled,
                    "type": str(rule.get("type") or ""),
                }
            )
        # Path rules sit between the extension table and the per-file map: they express
        # "every X under this directory is a Y", which is true for converted definition
        # markdown but NOT for formats that share an extension across kinds.
        self.path_overrides: list[dict] = []
        for rule in ft.get("path_overrides") or []:
            if not isinstance(rule, dict):
                continue
            glob = str(rule.get("glob") or "")
            if not glob:
                raise ConfigError("file_type.path_overrides: a rule is missing `glob`")
            self.path_overrides.append({"glob": glob, "type": str(rule.get("type") or "")})

        self.explicit_map_file: str = str(ft.get("explicit_map_file") or "")
        #: locator -> file_type, loaded lazily by `load_explicit_map`.
        self.explicit_map: dict[str, str] = {}

        # The subset parser keeps quote characters inside a key, so `"*": mod` arrives as
        # the key `"*"` and a fallback lookup silently misses. Strip them, and accept the
        # plain word `default` so a config need not rely on punctuation surviving at all.
        self.handlers: dict[str, str] = {}
        for k, v in (raw.get("handlers") or {}).items():
            key = str(k).strip().strip("\"'")
            if key.lower() == "default":
                key = "*"
            self.handlers[key] = str(v)

        enc = raw.get("encoding") or {}
        self.encoding_try_order: list[str] = _as_list(enc.get("try_order")) or [
            "utf-8",
            "shift_jis",
        ]
        self.binary_nul_window: int = _as_int(
            enc.get("binary_if_nul_in_first"), "encoding.binary_if_nul_in_first", 4096
        )

        ex = raw.get("extract") or {}
        self.include_commented_statements: bool = _as_bool(
            ex.get("include_commented_statements"), False
        )
        self.business_name_rules: list[dict] = []
        for rule in ex.get("business_name") or []:
            if not isinstance(rule, dict):
                continue
            kind = str(rule.get("kind") or "regex")
            entry: dict = {"kind": kind}
            if kind == "regex":
                pattern = str(rule.get("pattern") or "")
                if not pattern:
                    raise ConfigError("extract.business_name: regex rule missing `pattern`")
                try:
                    entry["re"] = re.compile(pattern, re.IGNORECASE)
                except re.error as exc:
                    raise ConfigError(
                        f"extract.business_name pattern {pattern!r}: {exc}"
                    ) from exc
            else:
                entry["within_lines"] = _as_int(
                    rule.get("within_lines"), "extract.business_name.within_lines", 14
                )
                entry["skip_banner"] = _as_bool(rule.get("skip_banner"), True)
                entry["skip_prefixes"] = [
                    p.upper() for p in _as_list(rule.get("skip_prefixes"))
                ]
            self.business_name_rules.append(entry)

        self.file_assign_rules: list[dict] = []
        for rule in ex.get("file_assign") or []:
            if not isinstance(rule, dict):
                continue
            pattern = str(rule.get("pattern") or "")
            if not pattern:
                raise ConfigError("extract.file_assign: a rule is missing `pattern`")
            try:
                compiled = re.compile(pattern, re.IGNORECASE)
            except re.error as exc:
                raise ConfigError(f"extract.file_assign pattern {pattern!r}: {exc}") from exc
            self.file_assign_rules.append(
                {
                    "re": compiled,
                    "name": str(rule.get("name") or r"\1"),
                    "kind": str(rule.get("kind") or "disk"),
                }
            )

        # Category -> role. The category comes from the ASSIGN device prefix; the role is
        # what the edge is finally called. Measured: `data` accounts for 7893 of 7930
        # `reads`, and every other category lands on the generic access role.
        fr = raw.get("file_roles") or {}
        self.file_roles: dict[str, str] = {
            str(k): _canonical_role(str(v)) for k, v in fr.items() if str(k) != "default"
        }
        self.file_role_default: str = _canonical_role(str(fr.get("default") or "x:accesses"))

        self.file_commands: list[str] = [v.upper() for v in _as_list(raw.get("file_commands"))]

        sc = raw.get("system_commands") or {}
        self.syscmd_catalog: list[str] = [c.upper() for c in _as_list(sc.get("catalog"))]
        # The catalog is VENDOR data, not pack logic: this platform documents 953 commands.
        # Inline `catalog` stays for small or experimental lists; a real deployment points
        # at a file whose provenance is the vendor manual.
        self.syscmd_catalog_file: str = str(sc.get("catalog_file") or "")
        self.syscmd_gloss: dict[str, dict] = {}
        self.syscmd_node_id: str = str(sc.get("node_id") or "{prefix}-SYSCMD-{name}")
        self.syscmd_emit_caller_edges: bool = _as_bool(sc.get("emit_caller_edges"), True)
        # A handful of commands are invoked by nearly EVERY control-language program. Each
        # one would contribute an edge per caller — measured here at 1920, 1793, 1755 and
        # 1133 callers against 1934 CL programs — and an edge present almost everywhere
        # discriminates nothing while dominating the graph. Those get a node carrying the
        # caller COUNT and no enumerated edges. The cut is a ratio so it travels: the next
        # command down this corpus sits at 40%, so any threshold in (0.41, 0.58) separates
        # the same four. Set to 0 to enumerate everything.
        self.syscmd_ubiquitous_ratio: float = float(sc.get("ubiquitous_ratio") or 0.5)
        self.syscmd_ubiquitous: set[str] = {
            c.upper() for c in _as_list(sc.get("ubiquitous"))
        }

        rs = raw.get("resolve") or {}
        scope = str(rs.get("scope") or "system")
        if scope != "system":
            raise ConfigError(
                "resolve.scope must be 'system' — cross-system resolution is never valid "
                "on a multi-system corpus (two systems are independent)"
            )
        self.resolve_scope = scope
        self.library_hint: str = str(rs.get("library_hint") or "object_library")
        self.type_constraints: dict[str, list[str]] = {
            _canonical_role(str(k)): _as_list(v)
            for k, v in (rs.get("type_constraints") or {}).items()
        }
        self.exclude_self: bool = _as_bool(rs.get("exclude_self"), True)
        self.library_priority: list[str] = [
            lib.upper() for lib in _as_list(rs.get("library_priority"))
        ]
        self.on_ambiguous: str = str(rs.get("on_ambiguous") or "cautions")
        self.on_unresolved: str = str(rs.get("on_unresolved") or "cautions")

        self._validate()

    def _validate(self) -> None:
        if not self.by_extension:
            raise ConfigError("file_type.by_extension is empty — nothing would be scanned")
        for rule in self.sniff:
            if not rule["type"]:
                raise ConfigError("file_type.sniff: a rule is missing `type`")
        for choice, field in ((self.on_ambiguous, "on_ambiguous"), (self.on_unresolved, "on_unresolved")):
            if choice not in ("cautions", "skip"):
                raise ConfigError(f"resolve.{field}: expected 'cautions' or 'skip', got {choice!r}")
        if self.library_hint not in ("object_library", "source_library"):
            raise ConfigError(
                "resolve.library_hint: expected 'object_library' or 'source_library'"
            )

    #: A file_type of this value means "known about, deliberately not built".
    SKIP = "skip"

    def load_explicit_map(self, project_root: Path) -> None:
        """Load the per-file `locator,file_type` CSV, if one is declared.

        Needed where neither the extension nor the content can separate kinds — measured
        on 140 printout PDFs of three different definition kinds sharing one directory,
        whose text extracts as mojibake. Guessing there would be inventing data, so the
        mapping is declared by a human and the builder simply obeys it.
        """
        if not self.explicit_map_file:
            return
        path = Path(self.explicit_map_file)
        if not path.is_absolute():
            path = project_root / path
        if not path.is_file():
            return
        import csv

        with path.open(encoding="utf-8", newline="") as fh:
            for row in csv.reader(fh):
                if not row or row[0].startswith("#") or len(row) < 2:
                    continue
                if row[0].strip().lower() in ("locator", "path"):
                    continue  # header
                self.explicit_map[row[0].strip().replace("\\", "/")] = row[1].strip()

    def load_syscmd_catalog(self, project_root: Path) -> None:
        """Load `command[,reading,english,category]` rows, if a catalog file is declared.

        Appends to whatever `catalog:` already listed rather than replacing it, so a
        deployment can pin one extra command without restating the vendor list.
        """
        if not self.syscmd_catalog_file:
            return
        path = Path(self.syscmd_catalog_file)
        if not path.is_absolute():
            path = project_root / path
        if not path.is_file():
            raise ConfigError(
                f"system_commands.catalog_file: {path} does not exist. A missing catalog "
                f"silently yields ZERO system-command edges instead of an error, so it is "
                f"refused here rather than reported as an empty result later."
            )
        import csv

        known = set(self.syscmd_catalog)
        with path.open(encoding="utf-8", newline="") as fh:
            for row in csv.reader(fh):
                if not row or not row[0].strip() or row[0].lstrip().startswith("#"):
                    continue
                name = row[0].strip().upper()
                if name in ("COMMAND", "CMD", "NAME"):
                    continue  # header
                if name not in known:
                    known.add(name)
                    self.syscmd_catalog.append(name)
                self.syscmd_gloss[name] = {
                    "reading": (row[1].strip() if len(row) > 1 else ""),
                    "english": (row[2].strip() if len(row) > 2 else ""),
                    "category": (row[3].strip() if len(row) > 3 else ""),
                    # Optional 5th column: the source_id of the documentation that
                    # describes this command. It gives the node its one required out-edge
                    # (`described_by`), which an object node cannot legally be without.
                    "doc_source_id": (row[4].strip() if len(row) > 4 else ""),
                }

    def classify_assign(self, token: str) -> tuple[str, str, str]:
        """`ASSIGN` token -> (file name, category, edge role).

        The device prefix carries the category and the category picks the role, so this
        one table decides both what the file IS and how the edge is labelled. A token that
        matches no rule keeps its own name and falls to the default role — unknown is a
        real category in this corpus, not an error.
        """
        token = token.strip().rstrip(".").upper()
        for rule in self.file_assign_rules:
            m = rule["re"].match(token)
            if not m:
                continue
            template = rule["name"]
            # RAW strings: `"\0"` is the NUL character, not the two-character escape the
            # config actually contains. Writing it unraw silently made every whole-match
            # rule produce a NUL-byte file name.
            name = token if template in (r"\0", r"\g<0>") else m.expand(template)
            kind = rule["kind"]
            return name.upper(), kind, self.file_roles.get(kind, self.file_role_default)
        return token, "unknown", self.file_role_default

    def file_type_for(self, ext: str, text: str, locator: str = "") -> str:
        """Resolve file_type, most specific declaration first.

        explicit per-file map -> content sniff -> path rule -> extension table.

        The sniff outranks the path rule and the extension because extensions lie in real
        corpora: every `.PRC` file in the reference corpus is COBOL while the table says
        CL. The per-file map outranks even the sniff, because it exists precisely for
        formats where nothing readable distinguishes the kinds.
        """
        ext = ext.upper().lstrip(".")
        loc = locator.replace("\\", "/")
        if loc and loc in self.explicit_map:
            return self.explicit_map[loc]
        for rule in self.sniff:
            if rule["when_ext"] and ext not in rule["when_ext"]:
                continue
            if rule["re"].search(text):
                return rule["type"]
        if loc:
            # `fnmatch` folds case according to the HOST os, so the same config would
            # behave differently on Windows and Linux. Compare case-insensitively and
            # explicitly instead, so a rule means the same thing everywhere.
            from fnmatch import fnmatchcase

            low = loc.lower()
            for rule in self.path_overrides:
                if fnmatchcase(low, rule["glob"].lower()):
                    return rule["type"]
        return self.by_extension.get(ext, "")

    def __repr__(self) -> str:  # pragma: no cover - diagnostics only
        return (
            f"<Config {self.path.name} systems={self.systems} "
            f"exts={len(self.by_extension)} sniff={len(self.sniff)} "
            f"bn_rules={len(self.business_name_rules)}>"
        )


def load(path: str | Path) -> Config:
    """Load and validate a pack config. Raises ConfigError with an actionable message."""
    p = Path(path)
    return Config(_load_yaml(p), p)
