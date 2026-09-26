#!/usr/bin/env python3
"""Resolve the EFFECTIVE binding of one standard-pack task (Standard_Pack_Contract_Spec_MVP §6/§7.3/§8).

A task in `task_catalog.yml` binds only **asset_id**s (§6.3). Nobody can act on an asset_id: a
person needs the file that is actually in force *in this project*, and the two trees of §8.1 make
"actually in force" a computation, not a lookup:

    .ai-work/standard_pack/     — owned by the pack, replaced wholesale on every install/upgrade
    .ai-work/project_process/   — owned by the project, never touched by pack tooling

§8.3 fixes the order `project > pack`, and the reason the resolver **always prints the source** is
that the two trees answer with the same asset_id: a reader who cannot see `pack` vs `project` cannot
tell a tailored checklist from the default one, which is exactly the thing a review argument turns on.

The project also edits the *catalog* (not just the assets) through
`.ai-work/project_process/task_catalog.override.yml` — flat, one level per task_id, with exactly two
operations (§8.4): **replace** (a bare value) and **add** (`+[...]` before a list). There is no deep
merge on purpose; see `apply_override` for what that costs and why it is still the right trade.

What this tool does NOT do:
  - it does not validate the pack (that is `lint_standard_pack.py`);
  - it does not create or refresh a tailored copy (that is a tailoring skill, later);
  - it does not install anything.

Exit codes
  0  resolved
  1  usage / unreadable input (no pack root, no catalog, bad --format)
  2  task_id not in any area catalog
  3  task disabled by the project override (`enabled: false`) — a DIFFERENT failure from "unknown":
     the task exists in the pack, this project deliberately dropped it.

Warnings (stderr, one line each; also carried in `--format json` under `warnings`) never change the
exit code. They exist because the failures they name are the SILENT ones: `lint_standard_pack.py`
lints the pack only, so nothing else in AIWS ever looks at `.ai-work/project_process/`. A resolver
that quietly does the reasonable thing there is the last place a project would find out.

Usage
  py .ai-work/tooling/resolve_task.py DD-CREATE
  py .ai-work/tooling/resolve_task.py DD-CREATE --format json
  py .ai-work/tooling/resolve_task.py DD-CREATE --pack-root <dir> --project-root <dir>
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:                                                    # tool must run from a sandbox too (Rule 3)
    from _common import find_ai_work_root               # noqa: E402
except Exception:                                       # pragma: no cover - _common always present
    find_ai_work_root = None                            # type: ignore[assignment]

# ONE reader for the pack format, shared with the linter (same directory, no `product/` touch).
# `_common._parse_block_mapping_list` cannot be used: it is flat by design (`- k: v` siblings only)
# and a task item nests `assets`/`aip`/`human_gate` three levels down. Writing a SECOND subset
# parser here was the other option and it cost immediately: it returned `step` as the string "1"
# where `lint_standard_pack.parse_yaml` returned int 1 on the very same file, so two tools of one
# mission disagreed about §6's `step: int >= 1` — and sorting steps as strings puts "10" before "2".
from lint_standard_pack import (                        # noqa: E402
    YamlSubsetError,
    parse_yaml as parse_yaml_text,
    split_frontmatter,
)

# Windows cp932-safe (§Environment). `_common` already reconfigures both streams; this is the
# fallback for the sandbox case where it could not be imported. RECONFIGURE, never rebind: swapping
# in a new TextIOWrapper over `sys.stdout.buffer` leaves the old wrapper unreferenced, and when it
# is collected it CLOSES that shared buffer — every later print in the importing process then dies
# with "I/O operation on closed file". Harmless in a CLI, fatal when a test imports this module.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")   # type: ignore[attr-defined]

PACK_SUBDIR = (".ai-work", "standard_pack")
PROJECT_SUBDIR = (".ai-work", "project_process")
OVERRIDE_NAME = "task_catalog.override.yml"
ASSET_GROUPS = ("process", "templates", "checklists", "guidelines", "rules")
SINGLE_GROUPS = ("process",)                            # groups whose value is one asset_id, not a list


# ---------------------------------------------------------------- YAML subset

class AddOp:
    """`+[a, b]` from §8.4 — 'append to whatever the pack said', kept distinct from the list `[a, b]`
    ('replace it'). Parsing it into a plain list would erase the only difference between the two
    operations the override language has."""

    __slots__ = ("items",)

    def __init__(self, items: list) -> None:
        self.items = items

    def __repr__(self) -> str:                          # pragma: no cover - debugging aid
        return f"AddOp({self.items!r})"


class YamlError(Exception):
    """Unreadable or unparsable pack file. Wraps `lint_standard_pack.YamlSubsetError` so a caller
    of this module has one exception type to catch, whoever did the parsing."""


def load_yaml(path: Path) -> dict:
    """Read one pack/override file with the LINTER's parser (see the import note at the top)."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise YamlError(f"cannot read {path}: {exc}") from exc
    try:
        doc = parse_yaml_text(text)
    except YamlSubsetError as exc:
        raise YamlError(f"cannot parse {path}: {exc}") from exc
    return doc if isinstance(doc, dict) else {}


#: §8.4 `+[a, b]`. This is the one piece of syntax the linter's parser does not need to know about
#: (it never reads an override), so it comes back as the plain string "+[a, b]". Re-reading it here
#: as `<key>: [a, b]` keeps the parsing in ONE place instead of forking the reader for one prefix.
_ADD_RE = re.compile(r"^\+\s*\[.*\]$", re.S)


def _wrap_add_ops(node):
    if isinstance(node, dict):
        return {k: _wrap_add_ops(v) for k, v in node.items()}
    if isinstance(node, list):
        return [_wrap_add_ops(v) for v in node]
    if isinstance(node, str) and _ADD_RE.match(node.strip()):
        try:
            items = parse_yaml_text("__add__: " + node.strip()[1:]).get("__add__")
        except YamlSubsetError:                          # pragma: no cover - flow list, cannot fail
            return node
        if isinstance(items, list):
            return AddOp(items)
    return node


# ---------------------------------------------------------------- asset index

def parse_frontmatter_fields(path: Path) -> dict:
    """Read the asset frontmatter (§3) with the linter's `split_frontmatter`. A file without
    frontmatter yields {} and is simply not an asset."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return {}
    meta, ok = split_frontmatter(text)
    return meta if ok and isinstance(meta, dict) else {}


def index_assets(root: Path) -> dict:
    """`by_id`: asset_id -> {path, kind, classification, title, name, status}, indexing both
    `asset_id` and `tailored_from` so a tailored copy answers for the pack asset it descends
    from (§8.2).

    `nameless`: basename -> [paths] for files in this tree that declare NEITHER `asset_id` NOR
    `tailored_from`. They are not assets and can never win a resolution; they are indexed only so
    `resolve_asset` can say out loud that one of them looks like it was meant to (see there)."""
    by_id: dict = {}
    nameless: dict = {}
    if not root.is_dir():
        return {"by_id": by_id, "nameless": nameless}
    for path in sorted(root.rglob("*.md"), key=lambda p: p.as_posix()):
        meta = parse_frontmatter_fields(path)
        rec = {
            "path": path,
            "kind": str(meta.get("kind") or ""),
            "classification": str(meta.get("classification") or ""),
            "title": str(meta.get("title") or ""),
            "name": str(meta.get("name") or ""),
            "status": str(meta.get("status") or ""),
        }
        keys = [k.strip() for k in (meta.get("asset_id"), meta.get("tailored_from"))
                if isinstance(k, str) and k.strip()]
        for key in keys:
            by_id.setdefault(key, rec)
        if not keys:
            nameless.setdefault(path.name, []).append(path)
    return {"by_id": by_id, "nameless": nameless}


def resolve_asset(asset_id: str, pack_idx: dict, proj_idx: dict, warn=None) -> dict:
    """§8.3 `project > pack`, and always report which one answered.

    The project tree answers on ONE piece of evidence: a file whose frontmatter carries this
    `asset_id`, or `tailored_from: <asset_id>` (§8.2). Otherwise the pack answers, or nobody does
    (`unresolved` — a lint finding, not a crash: an asset_id an override invented with no file
    behind it must stay visible instead of being swallowed).

    There is deliberately NO "same file name" fallback. §2 fixes exactly one `areas/<A>/process.md`
    per area, so in a real pack the basename `process.md` repeats in every area: matching on it
    would let a tailored copy of BD answer for DD's process asset and still print `source: project`
    — a confident wrong answer. Worse, a file that wins on its name need not have frontmatter at
    all, so the win would route around §8.2 (`tailored_from` / `_sha256` / `deviation_ref` are
    MANDATORY) and around §4 (a mandatory asset needs a `deviation_ref` to be tailored) — and
    `lint_standard_pack.py` lints the pack only, so no second tool would ever catch it. Legalising
    tailoring-without-provenance is a change to §8.2, i.e. a CR, not a resolver convenience. What
    the resolver owes the project instead is to not be silent: it warns and keeps the pack copy.
    """
    hit = proj_idx["by_id"].get(asset_id)
    if hit:
        return dict(hit, source="project", asset_id=asset_id, resolved=True)
    pack_rec = pack_idx["by_id"].get(asset_id)
    if pack_rec:
        if warn is not None:
            for path in proj_idx["nameless"].get(pack_rec["path"].name, []):
                warn(path, asset_id)                    # message built in `resolve` (has the root)
        return dict(pack_rec, source="pack", asset_id=asset_id, resolved=True)
    return {"asset_id": asset_id, "path": None, "kind": "", "classification": "",
            "title": "", "name": "", "status": "", "source": "unresolved", "resolved": False}


# ---------------------------------------------------------------- catalog + override

def load_catalog(pack_root: Path) -> dict:
    """task_id -> (area, task dict). §6.1 makes task_id unique pack-wide, so one flat map is right;
    a duplicate is reported rather than silently won by the last area read."""
    tasks: dict = {}
    dupes: list = []
    areas_dir = pack_root / "areas"
    for cat in sorted(areas_dir.glob("*/task_catalog.yml"), key=lambda p: p.as_posix()):
        doc = load_yaml(cat)
        area = str(doc.get("area") or cat.parent.name)
        for task in doc.get("tasks") or []:
            if not isinstance(task, dict):
                continue
            tid = str(task.get("task_id") or "").strip()
            if not tid:
                continue
            if tid in tasks:
                dupes.append(tid)
            tasks[tid] = {"area": area, "catalog": cat, "task": task}
    return {"tasks": tasks, "duplicates": sorted(set(dupes))}


def load_override(project_root: Path) -> dict:
    path = project_root.joinpath(*PROJECT_SUBDIR) / OVERRIDE_NAME
    if not path.is_file():
        return {"path": path, "present": False, "tasks": {}}
    doc = _wrap_add_ops(load_yaml(path))
    raw = doc.get("tasks") or {}
    return {"path": path, "present": True,
            "tasks": raw if isinstance(raw, dict) else {}}


def _as_list(value) -> list:
    if value is None:
        return []
    if isinstance(value, list):
        return list(value)
    return [value]


def apply_override(task: dict, ov: dict) -> "tuple[dict, list]":
    """Two operations, one level deep (§8.4).

    `replace` = a bare value; `add` = `+[...]`. A nested mapping in the override (`assets:`,
    `human_gate:`) is walked ONE level so the op lands on the leaf list/scalar the project meant —
    that is still not a deep merge: below that leaf the override value wins whole. Deep merge was
    rejected in the spec because the result of `assets.checklists` decides *who must review what*,
    and a reader must be able to predict it from the two files without simulating a merge algorithm.
    """
    out = json_safe_copy(task)
    trace: list = []
    for key, value in (ov or {}).items():
        if key == "enabled":
            continue
        base = out.get(key)
        if isinstance(value, dict) and isinstance(base, dict):
            for sub, sval in value.items():
                new, how = _apply_one(base.get(sub), sval)
                base[sub] = new
                trace.append(f"{key}.{sub}: {how}")
            out[key] = base
        else:
            new, how = _apply_one(base, value)
            out[key] = new
            trace.append(f"{key}: {how}")
    return out, trace


def _apply_one(base, value) -> "tuple[object, str]":
    if isinstance(value, AddOp):
        merged = _as_list(base)
        added = [it for it in value.items if it not in merged]
        return merged + added, f"add {value.items}"
    return json_safe_copy(value), f"replace -> {value}"


def json_safe_copy(obj):
    if isinstance(obj, dict):
        return {k: json_safe_copy(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [json_safe_copy(v) for v in obj]
    if isinstance(obj, AddOp):                          # `+[...]` inside a catalog is meaningless
        return list(obj.items)
    return obj


# ---------------------------------------------------------------- resolution

def resolve(task_id: str, pack_root: Path, project_root: Path) -> dict:
    warnings: list = []

    def warn(msg: str) -> None:
        if msg not in warnings:                          # one asset can be bound by two groups
            warnings.append(msg)

    def warn_name_collision(path: Path, asset_id: str) -> None:
        # See `resolve_asset`: a name match is NOT a resolution, and staying quiet about it is how
        # a project ends up editing a file nothing reads.
        warn(f"{rel(path, project_root)} has the file name of pack asset {asset_id} but declares "
             f"no asset_id/tailored_from (§8.2) — NOT used; the pack copy is in force")

    pack_yml = load_yaml(pack_root / "pack.yml") if (pack_root / "pack.yml").is_file() else {}
    catalog = load_catalog(pack_root)
    for dup in catalog["duplicates"]:
        warn(f"task_id '{dup}' is declared in more than one area catalog (§6.1: unique pack-wide) "
             f"— the last area read wins, which is not a decision anyone made")

    ov_doc = load_override(project_root)
    for tid in ov_doc["tasks"]:
        # §8.4 overrides a task the pack HAS; it cannot add one. Skipping an unmatched entry in
        # silence means a typo'd task_id looks exactly like a working override.
        if tid not in catalog["tasks"]:
            warn(f"override entry '{tid}' in {rel(ov_doc['path'], project_root)} matches no "
                 f"task_id in the pack catalog — the entry is IGNORED (§8.4 overrides an existing "
                 f"task; it cannot add one)")

    entry = catalog["tasks"].get(task_id)
    if entry is None:
        return {"ok": False, "code": 2, "task_id": task_id,
                "error": f"task_id '{task_id}' not found in any area catalog under {pack_root}",
                "known_tasks": sorted(catalog["tasks"]), "warnings": warnings}

    ov_task = ov_doc["tasks"].get(task_id) or {}
    if not isinstance(ov_task, dict):
        ov_task = {}
    enabled = ov_task.get("enabled", True)
    task, trace = apply_override(entry["task"], ov_task)

    proj_dir = project_root.joinpath(*PROJECT_SUBDIR)
    pack_idx = index_assets(pack_root)
    proj_idx = index_assets(proj_dir)
    roles_doc = load_yaml(pack_root / "common" / "roles.yml") if (
        pack_root / "common" / "roles.yml").is_file() else {}
    role_titles = {}
    for rid, rec in (roles_doc.get("roles") or {}).items():
        role_titles[str(rid)] = str(rec.get("title") or "") if isinstance(rec, dict) else str(rec or "")

    assets_raw = task.get("assets") if isinstance(task.get("assets"), dict) else {}
    assets: dict = {}
    for group in ASSET_GROUPS:
        ids = _as_list(assets_raw.get(group))
        assets[group] = [resolve_asset(str(a), pack_idx, proj_idx, warn_name_collision)
                         for a in ids if str(a).strip()]

    aip_raw = task.get("aip") if isinstance(task.get("aip"), dict) else {}
    aip_mode = str(aip_raw.get("mode") or "none")
    aip_template = str(aip_raw.get("template") or "").strip()
    aip = {"mode": aip_mode,
           "template": (resolve_asset(aip_template, pack_idx, proj_idx, warn_name_collision)
                        if aip_template else None)}

    skills = [resolve_skill(str(s), pack_idx, proj_idx, project_root)
              for s in _as_list(task.get("skills")) if str(s).strip()]

    hg_raw = task.get("human_gate") if isinstance(task.get("human_gate"), dict) else {}
    human_gate = {"required": bool(hg_raw.get("required")),
                  "checker": str(hg_raw.get("checker") or "") or None}
    human_gate["checker_title"] = role_titles.get(human_gate["checker"] or "", "")

    roles_raw = task.get("roles") if isinstance(task.get("roles"), dict) else {}
    roles = {k: _as_list(v) for k, v in roles_raw.items()}

    unresolved = [a["asset_id"] for group in assets.values() for a in group if not a["resolved"]]
    if aip["template"] and not aip["template"]["resolved"]:
        unresolved.append(aip["template"]["asset_id"])
    unresolved += [s["ref"] for s in skills if s["source"] == "unresolved"]

    return {
        "ok": bool(enabled), "code": 0 if enabled else 3,
        "task_id": task_id, "enabled": bool(enabled),
        "title": str(task.get("title") or ""), "area": entry["area"],
        "step": task.get("step"), "archetype": str(task.get("archetype") or ""),
        "pack": {"pack_id": str(pack_yml.get("pack_id") or ""),
                 "pack_version": str(pack_yml.get("pack_version") or ""),
                 "root": pack_root},
        "override": {"present": ov_doc["present"], "path": ov_doc["path"],
                     "applies": bool(ov_task), "trace": trace},
        "inputs": _as_list(task.get("inputs")), "outputs": _as_list(task.get("outputs")),
        "assets": assets, "aip": aip, "skills": skills, "roles": roles,
        "role_titles": role_titles, "human_gate": human_gate,
        "machine_verification": _as_list(task.get("machine_verification")),
        "downstream": _as_list(task.get("downstream")),
        "unresolved": unresolved,
        "duplicate_task_ids": catalog["duplicates"],
        "warnings": warnings,
    }


def resolve_skill(ref: str, pack_idx: dict, proj_idx: dict, project_root: Path) -> dict:
    """§7.3: an element is either a pack skill asset_id (`<AREA>-SKL-<slug>`) or the NAME of a real
    AIWS skill. Print the source so a reader knows whether the pack ships it or the project already
    had it."""
    for source, idx in (("project", proj_idx), ("pack", pack_idx)):
        rec = idx["by_id"].get(ref)
        if rec and (rec["kind"] == "skill" or rec["path"].name == "SKILL.md"):
            return {"ref": ref, "source": source, "name": rec["name"] or rec["path"].parent.name,
                    "path": rec["path"], "classification": rec["classification"],
                    "title": rec["title"]}
    installed = project_root / ".claude" / "skills" / ref / "SKILL.md"
    if installed.is_file():
        meta = parse_frontmatter_fields(installed)
        return {"ref": ref, "source": "aiws", "name": str(meta.get("name") or ref),
                "path": installed, "classification": str(meta.get("classification") or ""),
                "title": str(meta.get("title") or "")}
    return {"ref": ref, "source": "unresolved", "name": ref, "path": None,
            "classification": "", "title": ""}


# ---------------------------------------------------------------- rendering

def rel(path, project_root: Path) -> str:
    if path is None:
        return "(not found)"
    p = Path(path)
    try:
        return p.resolve().relative_to(project_root.resolve()).as_posix()
    except (ValueError, OSError):
        return p.as_posix()


def render_text(res: dict, project_root: Path) -> str:
    out: list = []
    pack = res["pack"]
    head = f"task: {res['task_id']} — {res['title']}" if res["title"] else f"task: {res['task_id']}"
    out.append(head)
    out.append(f"pack: {pack['pack_id']}@{pack['pack_version']}  area: {res['area']}  "
               f"step: {res['step']}  archetype: {res['archetype']}")
    ov = res["override"]
    if not ov["present"]:
        out.append("override: none (no .ai-work/project_process/task_catalog.override.yml)")
    elif not ov["applies"]:
        out.append(f"override: file present, no entry for {res['task_id']}")
    else:
        out.append(f"override: applied ({rel(ov['path'], project_root)})")
        for line in ov["trace"]:
            out.append(f"  - {line}")
    if not res["enabled"]:
        out.append("ENABLED: false — task disabled by project override")
    out.append("")
    out.append("assets:")
    any_asset = False
    for group in ASSET_GROUPS:
        for a in res["assets"][group]:
            any_asset = True
            cls = f"[{a['classification'] or '-'}]"
            out.append(f"  {group:<11} {a['asset_id']:<24} {cls:<13} {a['source']:<10} "
                       f"{rel(a['path'], project_root)}")
    if not any_asset:
        out.append("  (none)")
    out.append("")
    aip = res["aip"]
    out.append("aip:")
    out.append(f"  mode: {aip['mode']}")
    if aip["template"]:
        t = aip["template"]
        out.append(f"  template: {t['asset_id']} [{t['classification'] or '-'}]"
                   f"  {t['source']}  {rel(t['path'], project_root)}")
    else:
        out.append("  template: (none)")
    out.append("")
    out.append("skills:")
    for s in res["skills"] or []:
        out.append(f"  {s['ref']:<32} {s['source']:<10} {s['name']:<24} {rel(s['path'], project_root)}")
    if not res["skills"]:
        out.append("  (none)")
    out.append("")
    out.append("roles:")
    for key, vals in (res["roles"] or {}).items():
        pretty = ", ".join(f"{v} ({res['role_titles'][v]})" if res["role_titles"].get(v) else str(v)
                           for v in vals)
        out.append(f"  {key}: {pretty or '(none)'}")
    if not res["roles"]:
        out.append("  (none)")
    out.append("")
    hg = res["human_gate"]
    checker = hg["checker"] or "(none)"
    if hg["checker_title"]:
        checker = f"{hg['checker']} ({hg['checker_title']})"
    out.append(f"human_gate: required={str(hg['required']).lower()}  checker: {checker}")
    if res["inputs"] or res["outputs"]:
        out.append(f"inputs: {', '.join(map(str, res['inputs'])) or '(none)'}   "
                   f"outputs: {', '.join(map(str, res['outputs'])) or '(none)'}")
    if res["downstream"]:
        out.append(f"downstream: {', '.join(map(str, res['downstream']))}")
    if res["unresolved"]:
        out.append("")
        out.append("UNRESOLVED (lint_standard_pack territory): " + ", ".join(res["unresolved"]))
    # Warnings are NOT rendered here: `main` prints them on stderr for every format, so a caller
    # that pipes stdout to a file (the json consumers of §12/T19 do) still sees them.
    return "\n".join(out)


def to_json(res: dict, project_root: Path) -> dict:
    def asset(a):
        if a is None:
            return None
        return {"asset_id": a["asset_id"], "path": rel(a["path"], project_root) if a["path"] else None,
                "source": a["source"], "classification": a["classification"],
                "kind": a["kind"], "title": a["title"], "resolved": a["resolved"]}

    return {
        "task_id": res["task_id"], "title": res["title"], "area": res["area"],
        "step": res["step"], "archetype": res["archetype"], "enabled": res["enabled"],
        "pack": {"pack_id": res["pack"]["pack_id"], "pack_version": res["pack"]["pack_version"],
                 "root": rel(res["pack"]["root"], project_root)},
        "override": {"present": res["override"]["present"],
                     "applies": res["override"]["applies"],
                     "path": rel(res["override"]["path"], project_root),
                     "trace": res["override"]["trace"]},
        "assets": {g: [asset(a) for a in res["assets"][g]] for g in ASSET_GROUPS},
        "aip": {"mode": res["aip"]["mode"], "template": asset(res["aip"]["template"])},
        "skills": [{"ref": s["ref"], "source": s["source"], "name": s["name"],
                    "path": rel(s["path"], project_root) if s["path"] else None,
                    "classification": s["classification"]} for s in res["skills"]],
        "roles": res["roles"], "human_gate": res["human_gate"],
        "inputs": res["inputs"], "outputs": res["outputs"],
        "machine_verification": res["machine_verification"], "downstream": res["downstream"],
        "unresolved": res["unresolved"], "duplicate_task_ids": res["duplicate_task_ids"],
        "warnings": res["warnings"],
    }


# ---------------------------------------------------------------- CLI

def main(argv: "list[str] | None" = None) -> int:
    ap = argparse.ArgumentParser(
        description="Resolve the effective binding of a standard-pack task (assets, AIP, skills, "
                    "roles, human gate) with project overrides applied.")
    ap.add_argument("task_id", help="task_id from a pack task_catalog.yml (e.g. DD-CREATE)")
    ap.add_argument("--pack-root", default="",
                    help="installed pack root (default: <project-root>/.ai-work/standard_pack)")
    ap.add_argument("--project-root", default="", help="project root (default: walk up from cwd)")
    ap.add_argument("--format", default="text", choices=("text", "json"), dest="fmt")
    ns = ap.parse_args(argv)

    if ns.project_root:
        project_root = Path(ns.project_root).resolve()
    elif find_ai_work_root is not None:
        try:
            project_root = find_ai_work_root(Path.cwd())
        except SystemExit:
            print("error: not inside an AIWS project; pass --project-root", file=sys.stderr)
            return 1
    else:                                               # pragma: no cover
        project_root = Path.cwd().resolve()

    pack_root = Path(ns.pack_root).resolve() if ns.pack_root else project_root.joinpath(*PACK_SUBDIR)
    if not pack_root.is_dir():
        print(f"error: pack root not found: {pack_root}\n"
              f"       install a Standard Pack first (install_standard_pack.py) or pass --pack-root",
              file=sys.stderr)
        return 1
    if not (pack_root / "areas").is_dir():
        print(f"error: no areas/ under pack root: {pack_root}", file=sys.stderr)
        return 1

    try:
        res = resolve(ns.task_id, pack_root, project_root)
    except YamlError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    for line in res.get("warnings") or []:
        print(f"WARNING: {line}", file=sys.stderr)

    if res.get("code") == 2:
        if ns.fmt == "json":
            print(json.dumps({"task_id": ns.task_id, "error": res["error"],
                              "known_tasks": res["known_tasks"],
                              "warnings": res.get("warnings") or []},
                             ensure_ascii=False, indent=2))
        else:
            print(f"error: {res['error']}", file=sys.stderr)
            print("known task_id: " + (", ".join(res["known_tasks"]) or "(none)"), file=sys.stderr)
        return 2

    if ns.fmt == "json":
        print(json.dumps(to_json(res, project_root), ensure_ascii=False, indent=2))
    else:
        print(render_text(res, project_root))
    return int(res["code"])


if __name__ == "__main__":
    raise SystemExit(main())
