#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""lint_standard_pack.py — contract lint for a Standard Pack.

Spec: `Standard_Pack_Contract_Spec_MVP` §11 (the eleven codes below), with the conditions
defined in §2 (layout + `pack.yml`), §3 (asset frontmatter), §4 (classification), §5 (AIP
law / D024), §6 (task catalog schema + roles) and §7.3 (`skills[]`).

    py .ai-work/tooling/lint_standard_pack.py --pack <dir> [--format text|json]

Exit code: 0 when clean, 2 when ANY error is reported (every code here is an ERROR).

Two laws for this lint itself (§11):
  1. It checks the CONTRACT, never the CONTENT. It never judges whether a checklist is
     missing an item — that belongs to the pack owner.
  2. Every finding names the place to fix it: a file path or a `task_id`. A finding that
     points at neither is a broken finding.

The eleven codes:
    pack_yml_missing_key · asset_frontmatter_missing · asset_id_dup · task_asset_unknown ·
    task_asset_kind_mismatch · aip_template_kind · mandatory_no_tailoring_note ·
    aiws_min_version_exceeds · deliverable_task_no_aip · task_skill_unknown · task_role_unknown

Python 3.8+, stdlib only. The YAML reader below is a deliberate SUBSET parser (no PyYAML —
`.ai-work/AIWS.md` §6 forbids non-stdlib deps): block mappings, block sequences (scalar items
and mapping items), flow lists/mappings, folded/literal block scalars, comments. That is
everything `pack.yml`, an asset frontmatter, `task_catalog.yml` and `common/roles.yml` use.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _common import (  # noqa: E402  (also forces UTF-8 stdout)
    LintReport,
    emit_report,
    find_ai_work_root,
)

# ---------------------------------------------------------------- contract constants

#: §2.1 — keys `pack.yml` MUST carry.
PACK_REQUIRED_KEYS = ("pack_id", "pack_version", "title", "owner", "aiws_min_version", "areas")

#: §3 — frontmatter fields every asset MUST carry.
ASSET_REQUIRED_FIELDS = ("artifact_type", "asset_id", "pack_id", "area", "kind", "title",
                         "classification", "owner", "status")

ARTIFACT_TYPE = "standard_asset"

#: §3.2 — the seven kinds and their `<KIND3>` code used inside `asset_id` (§3.1).
KIND3 = {
    "process": "PRC",
    "template": "TPL",
    "checklist": "CHK",
    "guideline": "GDL",
    "rule": "RUL",
    "aip_template": "AIP",
    "skill": "SKL",
}
KINDS = frozenset(KIND3)

#: §2 — kind directory inside an area -> the `kind` its assets must declare.
KIND_DIRS = {
    "templates": "template",
    "checklists": "checklist",
    "guidelines": "guideline",
    "rules": "rule",
    "aip_templates": "aip_template",
}

#: §6.3 — list-valued bind groups in `assets:` and the kind each one requires.
ASSET_LIST_BINDS = (
    ("templates", "template"),
    ("checklists", "checklist"),
    ("guidelines", "guideline"),
    ("rules", "rule"),
)

CLASSIFICATIONS = frozenset({"mandatory", "default", "tailorable", "reference"})   # §4
STATUSES = frozenset({"draft", "active", "retired"})                               # §3
ARCHETYPES = frozenset({"plan", "understand", "generate_artifact",                 # §6.2
                        "review_artifact", "update_artifact", "verify_execute"})
#: §5 / §6.2 — the two archetypes that create a deliverable and therefore REQUIRE an AIP.
DELIVERABLE_ARCHETYPES = frozenset({"generate_artifact", "update_artifact"})

#: Files that are never assets even when they sit inside an area (§2: an area with no
#: documents carries only a README saying what is missing).
NON_ASSET_NAMES = frozenset({"README.md", "CHANGELOG.md", "CONVERSION_LOG.md", "PACK_SOURCE.md"})

ASSET_ID_RE = re.compile(r"^(?P<area>[A-Z0-9]+)-(?P<kind3>PRC|TPL|CHK|GDL|RUL|AIP|SKL)-"
                         r"(?P<slug>[a-z0-9-]+)$")


# ---------------------------------------------------------------- YAML subset parser

class YamlSubsetError(Exception):
    """Raised when the input is not something this subset parser can read at all."""


def _ind(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _skip(lines, i: int) -> int:
    """Index of the next line that carries content (blank / comment / document markers skipped)."""
    while i < len(lines):
        s = lines[i].strip()
        if s and not s.startswith("#") and s not in ("---", "..."):
            return i
        i += 1
    return i


def _top_colon(s: str) -> int:
    """Index of the top-level `: ` separator in a scalar line, or -1.

    Top-level = not inside quotes and not inside a flow collection, so
    `roles: {title: Developer}` splits once and `- [a, b]` does not split at all.
    """
    quote = ""
    depth = 0
    for idx, ch in enumerate(s):
        if quote:
            if ch == quote:
                quote = ""
            continue
        if ch in ('"', "'"):
            quote = ch
        elif ch in "[{":
            depth += 1
        elif ch in "]}":
            depth = max(0, depth - 1)
        elif ch == ":" and depth == 0:
            if idx + 1 >= len(s) or s[idx + 1] in " \t":
                return idx
    return -1


def _strip_comment(s: str) -> str:
    """Drop a YAML inline comment (` #…`) from an UNQUOTED value. A `#` with no preceding
    whitespace (`BD#12`, `#fff`) is part of the value, never a comment."""
    h = 1
    while True:
        h = s.find("#", h)
        if h < 1:
            break
        if s[h - 1] in (" ", "\t"):
            return s[:h].strip()
        h += 1
    return s.strip()


_INT_RE = re.compile(r"^-?\d+$")


def _scalar(v: str):
    """Coerce ONE plain scalar. Quoted -> literal string. `true/false` -> bool, `null/~`/empty
    -> None, a pure integer -> int. Everything else stays a string: version strings (`0.1.0`),
    ids and dates must not be mangled."""
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in ("'", '"'):
        return v[1:-1]
    low = v.lower()
    if low in ("true", "false"):
        return low == "true"
    if low in ("null", "~", ""):
        return None
    if _INT_RE.match(v):
        return int(v)
    return v


def _ws(s: str, i: int) -> int:
    while i < len(s) and s[i] in " \t":
        i += 1
    return i


def _parse_flow(s: str, i: int, stops: str = ",]}"):
    """Parse one flow-style value starting at s[i]. Returns (value, next_index)."""
    i = _ws(s, i)
    if i >= len(s):
        return None, i
    ch = s[i]
    if ch == "[":
        items = []
        i += 1
        while True:
            i = _ws(s, i)
            if i >= len(s):
                break
            if s[i] == "]":
                i += 1
                break
            before = i
            val, i = _parse_flow(s, i)
            items.append(val)
            i = _ws(s, i)
            if i < len(s) and s[i] == ",":
                i += 1
                continue
            if i < len(s) and s[i] == "]":
                i += 1
                break
            if i <= before:                      # no progress — malformed, stop rather than spin
                break
        return items, i
    if ch == "{":
        out = {}
        i += 1
        while True:
            i = _ws(s, i)
            if i >= len(s):
                break
            if s[i] == "}":
                i += 1
                break
            before = i
            key, i = _parse_flow(s, i, stops=",]}:")
            i = _ws(s, i)
            if i < len(s) and s[i] == ":":
                i += 1
                val, i = _parse_flow(s, i)
            else:
                val = None
            if key is not None:
                out[str(key)] = val
            i = _ws(s, i)
            if i < len(s) and s[i] == ",":
                i += 1
                continue
            if i < len(s) and s[i] == "}":
                i += 1
                break
            if i <= before:
                break
        return out, i
    if ch in ('"', "'"):
        j = i + 1
        buf = []
        while j < len(s) and s[j] != ch:
            buf.append(s[j])
            j += 1
        return "".join(buf), j + 1
    j = i
    while j < len(s) and s[j] not in stops:
        j += 1
    return _scalar(s[i:j]), j


def _parse_value(raw: str):
    """Parse the right-hand side of `key:` written on the same line."""
    raw = raw.strip()
    if raw[:1] in ("[", "{"):
        val, _ = _parse_flow(raw, 0)
        return val
    if raw[:1] in ('"', "'"):
        quote = raw[0]
        end = raw.find(quote, 1)
        if end != -1:
            return raw[1:end]
        return raw
    return _scalar(_strip_comment(raw))


def _block_scalar(lines, i: int, key_indent: int, indicator: str):
    """Read the continuation lines of a `|` / `>` block scalar. Returns (text, next_index)."""
    body = []
    block_indent = None
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            body.append("")
            i += 1
            continue
        ind = _ind(line)
        if ind <= key_indent:
            break
        if block_indent is None:
            block_indent = ind
        body.append(line[block_indent:] if ind >= block_indent else line.lstrip())
        i += 1
    while body and body[-1] == "":
        body.pop()
    text = "\n".join(body)
    if indicator.startswith(">"):
        text = " ".join(seg.strip() for seg in text.split("\n") if seg.strip())
    return text, i


BLOCK_INDICATORS = ("|", ">", "|-", ">-", "|+", ">+")


def _parse_map(lines, i: int, ind: int):
    out = {}
    while True:
        i = _skip(lines, i)
        if i >= len(lines) or _ind(lines[i]) != ind:
            break
        s = lines[i].strip()
        if s == "-" or s.startswith("- "):
            break
        col = _top_colon(s)
        if col < 0:
            i += 1
            continue
        key = str(_scalar(s[:col]))
        raw = s[col + 1:].strip()
        i += 1
        if raw in BLOCK_INDICATORS:
            out[key], i = _block_scalar(lines, i, ind, raw)
        elif raw == "" or _strip_comment(raw) == "":
            child, i = _parse_node(lines, i, ind + 1)
            out[key] = child
        else:
            out[key] = _parse_value(raw)
    return out, i


def _parse_seq(lines, i: int, ind: int):
    items = []
    while True:
        i = _skip(lines, i)
        if i >= len(lines) or _ind(lines[i]) != ind:
            break
        s = lines[i].strip()
        if s == "-":
            i += 1
            child, i = _parse_node(lines, i, ind + 1)
            items.append(child)
            continue
        if not s.startswith("- "):
            break
        dash = lines[i].index("-", ind)
        rest = lines[i][dash + 1:]
        body = rest.strip()
        if _top_colon(body) >= 0:
            # Mapping item. Blank the dash so the first `key: value` sits at the same column as
            # the item's other keys, then read the whole item as an ordinary block mapping.
            content_ind = dash + 1 + (len(rest) - len(rest.lstrip(" ")))
            lines[i] = " " * (dash + 1) + rest
            child, i = _parse_map(lines, i, content_ind)
            items.append(child)
        else:
            items.append(_parse_value(body))
            i += 1
    return items, i


def _parse_node(lines, i: int, min_indent: int):
    """Parse whatever collection starts at/after line i, provided it is indented at least
    `min_indent`. Returns (value, next_index) — `(None, i)` when there is nothing there, which
    is how `key:` with an empty value reads."""
    i = _skip(lines, i)
    if i >= len(lines):
        return None, i
    ind = _ind(lines[i])
    if ind < min_indent:
        return None, i
    s = lines[i].strip()
    if s == "-" or s.startswith("- "):
        return _parse_seq(lines, i, ind)
    return _parse_map(lines, i, ind)


def parse_yaml(text: str) -> dict:
    """Parse a YAML-subset document into a dict. Raises YamlSubsetError when the top level is
    not a mapping (the only shape any pack file uses)."""
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    value, _ = _parse_node(lines, 0, 0)
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise YamlSubsetError("top level is not a mapping")
    return value


FRONTMATTER_RE = re.compile(r"^﻿?---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|$)", re.S)


def split_frontmatter(text: str):
    """(meta, ok). `ok` is False when the file has no frontmatter block at all."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, False
    try:
        return parse_yaml(m.group(1)), True
    except YamlSubsetError:
        return {}, False


# ---------------------------------------------------------------- helpers

def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def as_list(value):
    """Normalise a bind slot into a list of non-empty values (absent -> [], scalar -> [scalar])."""
    if value is None:
        return []
    if isinstance(value, list):
        return [v for v in value if v not in (None, "")]
    if isinstance(value, dict):
        return []
    return [value]


def _txt(value) -> str:
    return "" if value is None else str(value).strip()


_VER_PART_RE = re.compile(r"^\d+")


def version_tuple(raw):
    """`v1.2.1` / `1.2` -> (1, 2, 1) / (1, 2, 0). None when it is not a version at all."""
    s = _txt(raw).lstrip("vV")
    if not s:
        return None
    parts = s.split(".")[:3]
    out = []
    for p in parts:
        m = _VER_PART_RE.match(p.strip())
        if not m:
            return None
        out.append(int(m.group(0)))
    while len(out) < 3:
        out.append(0)
    return tuple(out)


def detect_aiws_version(project_root: Path) -> str:
    """Version of the AIWS running this lint, resolved the same two tiers as
    `compose_aiws_rules.py:resolve_version`: the stamped install marker first, then the
    source-tree pin. Returns "" when neither exists — the caller then SKIPS the comparison
    rather than guessing (a guessed version would fire `aiws_min_version_exceeds` on nothing).

    Both tiers are FRONTMATTER documents carrying `aiws_version`. `install_templates/VERSION` is
    stamped by `build_aiws_install_package.py` and its first line is `---`, so reading "the first
    line" yields `---`, `version_tuple` yields None, and §9.3 goes silent on exactly the trees it
    guards — every tree that has AIWS installed. The raw-first-line branch survives only as a
    fallback for a marker written without frontmatter.
    """
    stamped = project_root / ".ai-work" / "install_templates" / "VERSION"
    try:
        if stamped.is_file():
            raw = _read(stamped)
            meta, ok = split_frontmatter(raw)
            if ok:
                if _txt(meta.get("aiws_version")):
                    return _txt(meta.get("aiws_version"))
            else:
                first = raw.strip().splitlines()
                if first and _txt(first[0]):
                    return _txt(first[0])
    except OSError:
        pass
    pin = project_root / "product" / "aiws_version.md"
    try:
        if pin.is_file():
            meta, ok = split_frontmatter(_read(pin))
            if ok and _txt(meta.get("aiws_version")):
                return _txt(meta.get("aiws_version"))
    except OSError:
        pass
    return ""


def known_aiws_skills(project_root: Path):
    """Names of real AIWS skills in this tree (§7.3: a `skills[]` entry may be one)."""
    out = set()
    skills_dir = project_root / ".claude" / "skills"
    try:
        if skills_dir.is_dir():
            for child in sorted(skills_dir.iterdir(), key=lambda p: p.name):
                if child.is_dir() and (child / "SKILL.md").is_file():
                    out.add(child.name)
    except OSError:
        pass
    return out


def iter_asset_files(pack: Path):
    """Every file that IS an asset per §2, with the (area, kind) its PATH implies.

    A path-implied value of None means the path carries no opinion (a `common/` asset), so the
    frontmatter is accepted as-is for that field.
    """
    found = []
    common = pack / "common"
    if common.is_dir():
        for p in sorted(common.rglob("*.md"), key=lambda x: x.name):
            if p.is_file() and p.name not in NON_ASSET_NAMES:
                found.append((p, "COMMON", None))
    areas = pack / "areas"
    if areas.is_dir():
        for area_dir in sorted([d for d in areas.iterdir() if d.is_dir()], key=lambda p: p.name):
            area = area_dir.name
            proc = area_dir / "process.md"
            if proc.is_file():
                found.append((proc, area, "process"))
            for dir_name, kind in sorted(KIND_DIRS.items()):
                sub = area_dir / dir_name
                if not sub.is_dir():
                    continue
                for p in sorted(sub.rglob("*.md"), key=lambda x: x.as_posix()):
                    if p.is_file() and p.name not in NON_ASSET_NAMES:
                        found.append((p, area, kind))
            skills = area_dir / "skills"
            if skills.is_dir():
                for sd in sorted([d for d in skills.iterdir() if d.is_dir()], key=lambda p: p.name):
                    sk = sd / "SKILL.md"
                    if sk.is_file():
                        found.append((sk, area, "skill"))
    # Rule 12 (tooling_authoring_conventions): explicit sort key — the default ordering of
    # Path objects is case-folded on Windows and case-sensitive on POSIX, and this list decides
    # which of two duplicate asset_ids is reported first.
    found.sort(key=lambda t: t[0].as_posix())
    return found


def rel_of(path: Path, pack: Path) -> str:
    try:
        return path.resolve().relative_to(pack.resolve()).as_posix()
    except (ValueError, OSError):
        return path.as_posix()


# ---------------------------------------------------------------- checks

def check_pack_yml(pack: Path, report: LintReport) -> dict:
    """§2.1 -> `pack_yml_missing_key`. Returns the parsed mapping ({} when unusable)."""
    path = pack / "pack.yml"
    if not path.is_file():
        report.error("pack_yml_missing_key",
                     "pack.yml not found at pack root — every required key is missing: "
                     + ", ".join(PACK_REQUIRED_KEYS),
                     path="pack.yml")
        return {}
    try:
        data = parse_yaml(_read(path))
    except (YamlSubsetError, OSError) as exc:
        report.error("pack_yml_missing_key",
                     f"pack.yml is not parseable ({exc}) — cannot read required keys: "
                     + ", ".join(PACK_REQUIRED_KEYS),
                     path="pack.yml")
        return {}
    for key in PACK_REQUIRED_KEYS:
        if key not in data or data.get(key) in (None, "", [], {}):
            report.error("pack_yml_missing_key",
                         f"pack.yml is missing required key '{key}' (§2.1)", path="pack.yml")
        elif key == "areas" and not isinstance(data.get("areas"), list):
            report.error("pack_yml_missing_key",
                         "pack.yml key 'areas' must be a list of area ids (§2.1)",
                         path="pack.yml")
    return data


def check_aiws_min_version(pack_meta: dict, aiws_version: str, report: LintReport) -> None:
    """§9.3 -> `aiws_min_version_exceeds`."""
    declared = _txt(pack_meta.get("aiws_min_version"))
    if not declared or not aiws_version:
        return                      # missing key already reported; unknown current version = skip
    want, have = version_tuple(declared), version_tuple(aiws_version)
    if want is None or have is None:
        return
    if want > have:
        report.error("aiws_min_version_exceeds",
                     f"pack.yml requires AIWS aiws_min_version={declared} but the AIWS running "
                     f"this lint is {aiws_version}",
                     path="pack.yml")


def check_assets(pack: Path, pack_meta: dict, report: LintReport) -> dict:
    """§3 / §3.1 / §3.2 / §4 -> `asset_frontmatter_missing`, `asset_id_dup`,
    `mandatory_no_tailoring_note`. Returns {asset_id: {"kind":…, "path":…}}."""
    declared_areas = {str(a) for a in as_list(pack_meta.get("areas"))}
    declared_areas.add("COMMON")
    pack_id = _txt(pack_meta.get("pack_id"))

    index: dict = {}
    for path, path_area, path_kind in iter_asset_files(pack):
        rel = rel_of(path, pack)
        meta, ok = split_frontmatter(_read(path))
        if not ok:
            report.error("asset_frontmatter_missing",
                         f"{rel}: no YAML frontmatter — an asset must open with the §3 block "
                         f"(missing: {', '.join(ASSET_REQUIRED_FIELDS)})", path=rel)
            continue

        for field in ASSET_REQUIRED_FIELDS:
            if _txt(meta.get(field)) == "":
                report.error("asset_frontmatter_missing",
                             f"{rel}: missing required frontmatter field '{field}' (§3)",
                             path=rel)

        artifact_type = _txt(meta.get("artifact_type"))
        if artifact_type and artifact_type != ARTIFACT_TYPE:
            report.error("asset_frontmatter_missing",
                         f"{rel}: field 'artifact_type' is '{artifact_type}', must be the "
                         f"constant '{ARTIFACT_TYPE}' (§3)", path=rel)

        kind = _txt(meta.get("kind"))
        if kind and kind not in KINDS:
            report.error("asset_frontmatter_missing",
                         f"{rel}: field 'kind' is '{kind}', not one of the seven kinds "
                         f"({', '.join(sorted(KINDS))}) (§3.2)", path=rel)
            kind = ""
        elif kind and path_kind and kind != path_kind:
            report.error("asset_frontmatter_missing",
                         f"{rel}: field 'kind' is '{kind}' but its path implies "
                         f"'{path_kind}' (§2 layout)", path=rel)

        area = _txt(meta.get("area"))
        if area:
            if path_area and area != path_area:
                report.error("asset_frontmatter_missing",
                             f"{rel}: field 'area' is '{area}' but its path implies "
                             f"'{path_area}' (§2 layout)", path=rel)
            elif area not in declared_areas:
                report.error("asset_frontmatter_missing",
                             f"{rel}: field 'area' is '{area}', which is neither COMMON nor an "
                             f"area declared in pack.yml (§3)", path=rel)

        asset_pack = _txt(meta.get("pack_id"))
        if asset_pack and pack_id and asset_pack != pack_id:
            report.error("asset_frontmatter_missing",
                         f"{rel}: field 'pack_id' is '{asset_pack}' but pack.yml declares "
                         f"'{pack_id}' (§3)", path=rel)

        classification = _txt(meta.get("classification"))
        if classification and classification not in CLASSIFICATIONS:
            report.error("asset_frontmatter_missing",
                         f"{rel}: field 'classification' is '{classification}', not one of "
                         f"{', '.join(sorted(CLASSIFICATIONS))} (§4)", path=rel)

        status = _txt(meta.get("status"))
        if status and status not in STATUSES:
            report.error("asset_frontmatter_missing",
                         f"{rel}: field 'status' is '{status}', not one of "
                         f"{', '.join(sorted(STATUSES))} (§3)", path=rel)

        asset_id = _txt(meta.get("asset_id"))
        if asset_id:
            m = ASSET_ID_RE.match(asset_id)
            if not m:
                report.error("asset_frontmatter_missing",
                             f"{rel}: field 'asset_id' is '{asset_id}', which is not "
                             f"<AREA>-<KIND3>-<slug> (§3.1)", path=rel)
            else:
                if area and m.group("area") != area.upper():
                    report.error("asset_frontmatter_missing",
                                 f"{rel}: field 'asset_id' ('{asset_id}') carries area "
                                 f"'{m.group('area')}' but 'area' is '{area}' (§3.1)", path=rel)
                if kind and m.group("kind3") != KIND3[kind]:
                    report.error("asset_frontmatter_missing",
                                 f"{rel}: field 'asset_id' ('{asset_id}') carries kind code "
                                 f"'{m.group('kind3')}' but 'kind' is '{kind}' "
                                 f"(expected '{KIND3[kind]}') (§3.1)", path=rel)

            if asset_id in index:
                first = index[asset_id]["path"]
                report.error("asset_id_dup",
                             f"asset_id '{asset_id}' is declared twice: {first} and {rel} — "
                             f"asset_id must be unique across the pack (§3.1)", path=rel)
            else:
                index[asset_id] = {"kind": kind, "path": rel}

        # §4 / §11 — a mandatory asset without a note leaves the project no way to know WHY.
        if classification == "mandatory" and _txt(meta.get("tailoring_note")) == "":
            report.error("mandatory_no_tailoring_note",
                         f"{rel}: classification is 'mandatory' but 'tailoring_note' is missing "
                         f"or blank (§4)", path=rel)
    return index


def load_roles(pack: Path, report: LintReport):
    """§6.4 — role labels declared in `common/roles.yml` (empty set when the file is absent,
    which is legal only for a pack whose tasks declare no roles)."""
    path = pack / "common" / "roles.yml"
    if not path.is_file():
        return set()
    try:
        data = parse_yaml(_read(path))
    except (YamlSubsetError, OSError):
        return set()
    roles = data.get("roles")
    if isinstance(roles, dict):
        return {str(k) for k in roles}
    return {str(r) for r in as_list(roles)}


def _bind(report: LintReport, index: dict, task_id: str, slot: str, value, want_kind: str,
          rel: str) -> None:
    """One `asset_id` bind -> `task_asset_unknown` / `task_asset_kind_mismatch`."""
    asset_id = _txt(value)
    if not asset_id:
        return
    entry = index.get(asset_id)
    if entry is None:
        report.error("task_asset_unknown",
                     f"task '{task_id}': {slot} binds asset_id '{asset_id}', which does not "
                     f"exist in this pack (§6.3)", path=rel, loc=task_id)
        return
    got = entry.get("kind") or "<unknown>"
    if got != want_kind:
        report.error("task_asset_kind_mismatch",
                     f"task '{task_id}': {slot} expects kind '{want_kind}' but asset_id "
                     f"'{asset_id}' is kind '{got}' ({entry['path']}) (§3.2)",
                     path=rel, loc=task_id)


def check_task_catalogs(pack: Path, index: dict, roles: set, aiws_skills: set,
                        report: LintReport) -> None:
    """§5 / §6 / §7.3 — everything keyed on a `task_id`."""
    areas = pack / "areas"
    if not areas.is_dir():
        return
    for area_dir in sorted([d for d in areas.iterdir() if d.is_dir()], key=lambda p: p.name):
        catalog = area_dir / "task_catalog.yml"
        if not catalog.is_file():
            continue                      # an area with no documents is legal (§2)
        rel = rel_of(catalog, pack)
        try:
            data = parse_yaml(_read(catalog))
        except (YamlSubsetError, OSError):
            continue
        tasks = data.get("tasks")
        if not isinstance(tasks, list):
            continue
        for pos, task in enumerate(tasks, start=1):
            if not isinstance(task, dict):
                continue
            task_id = _txt(task.get("task_id")) or f"<task #{pos} in {rel} has no task_id>"
            archetype = _txt(task.get("archetype"))

            assets = task.get("assets") if isinstance(task.get("assets"), dict) else {}
            _bind(report, index, task_id, "assets.process", assets.get("process"),
                  "process", rel)
            for slot, want_kind in ASSET_LIST_BINDS:
                for value in as_list(assets.get(slot)):
                    _bind(report, index, task_id, f"assets.{slot}", value, want_kind, rel)

            # ---- §5 — AIP
            aip = task.get("aip") if isinstance(task.get("aip"), dict) else {}
            mode = _txt(aip.get("mode"))
            template = _txt(aip.get("template"))
            if template:
                entry = index.get(template)
                if entry is None:
                    report.error("task_asset_unknown",
                                 f"task '{task_id}': aip.template binds asset_id '{template}', "
                                 f"which does not exist in this pack (§6.3)",
                                 path=rel, loc=task_id)
                elif (entry.get("kind") or "") != "aip_template":
                    report.error("aip_template_kind",
                                 f"task '{task_id}': aip.template '{template}' is kind "
                                 f"'{entry.get('kind') or '<unknown>'}' ({entry['path']}), "
                                 f"expected kind 'aip_template' (§3.2)", path=rel, loc=task_id)
            if archetype in DELIVERABLE_ARCHETYPES and (mode != "mandatory" or not template):
                report.error("deliverable_task_no_aip",
                             f"task '{task_id}' (archetype '{archetype}') creates a deliverable "
                             f"and must bind aip.template with aip.mode: mandatory (§5, D024) — "
                             f"got mode='{mode or '<missing>'}', "
                             f"template='{template or '<missing>'}'", path=rel, loc=task_id)

            # ---- §7.3 — skills
            for value in as_list(task.get("skills")):
                name = _txt(value)
                if not name:
                    continue
                entry = index.get(name)
                if entry is not None:
                    if (entry.get("kind") or "") != "skill":
                        report.error("task_asset_kind_mismatch",
                                     f"task '{task_id}': skills[] expects kind 'skill' but "
                                     f"asset_id '{name}' is kind "
                                     f"'{entry.get('kind') or '<unknown>'}' ({entry['path']}) "
                                     f"(§7.3)", path=rel, loc=task_id)
                elif name not in aiws_skills:
                    report.error("task_skill_unknown",
                                 f"task '{task_id}': skills[] entry '{name}' resolves to neither "
                                 f"a skill asset of this pack nor a real AIWS skill (§7.3)",
                                 path=rel, loc=task_id)

            # ---- §6.4 / §6.5 — roles
            declared = task.get("roles") if isinstance(task.get("roles"), dict) else {}
            for slot, value in sorted(declared.items()):
                for role in as_list(value):
                    if _txt(role) and _txt(role) not in roles:
                        report.error("task_role_unknown",
                                     f"task '{task_id}': role '{_txt(role)}' (roles.{slot}) is "
                                     f"not declared in common/roles.yml (§6.4)",
                                     path=rel, loc=task_id)
            gate = task.get("human_gate") if isinstance(task.get("human_gate"), dict) else {}
            checker = _txt(gate.get("checker"))
            if checker and checker not in roles:
                report.error("task_role_unknown",
                             f"task '{task_id}': role '{checker}' (human_gate.checker) is not "
                             f"declared in common/roles.yml (§6.4)", path=rel, loc=task_id)


def lint_pack(pack: Path, project_root: Path, aiws_version: str) -> LintReport:
    report = LintReport(target=pack.as_posix())
    pack_meta = check_pack_yml(pack, report)
    check_aiws_min_version(pack_meta, aiws_version, report)
    index = check_assets(pack, pack_meta, report)
    roles = load_roles(pack, report)
    check_task_catalogs(pack, index, roles, known_aiws_skills(project_root), report)
    return report


# ---------------------------------------------------------------- CLI

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Lint a Standard Pack against Standard_Pack_Contract_Spec_MVP §11.")
    ap.add_argument("--pack", required=True, help="path to the pack root (the dir holding pack.yml)")
    ap.add_argument("--format", choices=("text", "json"), default="text", help="output format")
    ap.add_argument("--project-root", default="",
                    help="AIWS project root (default: walk up from cwd) — used to resolve the "
                         "running AIWS version and the set of real AIWS skills")
    ap.add_argument("--aiws-version", default="",
                    help="override the AIWS version used by aiws_min_version_exceeds")
    ns = ap.parse_args(argv)

    if ns.project_root:
        project_root = Path(ns.project_root).resolve()
    else:
        try:
            project_root = find_ai_work_root(Path.cwd())
        except SystemExit:
            project_root = Path.cwd()

    pack = Path(ns.pack)
    report = LintReport(target=pack.as_posix())
    if not pack.is_dir():
        report.error("pack_yml_missing_key",
                     f"--pack {pack} is not a directory — pack.yml and every required key of "
                     f"§2.1 are unreachable", path=str(pack))
        return emit_report(report, ns.format, False)

    aiws_version = _txt(ns.aiws_version) or detect_aiws_version(project_root)
    report = lint_pack(pack, project_root, aiws_version)
    return emit_report(report, ns.format, False)


if __name__ == "__main__":
    raise SystemExit(main())
