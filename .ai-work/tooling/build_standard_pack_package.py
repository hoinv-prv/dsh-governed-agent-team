#!/usr/bin/env python3
"""Build an installable package for ONE Standard Pack (Standard_Pack_Contract_Spec_MVP §2/§9/§12).

A Standard Pack package is NOT the AIWS package and never becomes part of it: the AIWS installer
ships methodology + tooling; this one ships an organisation's *content* (process · template ·
checklist · guideline · rule · aip_template · skill) on top of a project that already has AIWS.
`build_aiws_install_package.py` enumerates its payload sections explicitly and none of them names
`product/standard_pack`, so a pack can never leak into an AIWS package by accident — that
separation is an invariant the tests of this tool assert, not a convention.

Payload (three sections, mapped to the INSTALL layout by `INSTALL_MAP`):

    payload/standard_pack/                     -> .ai-work/standard_pack/            (the whole pack tree)
    payload/standard_pack_wiki/                -> .ai-work/wiki_sources/aiws_meta/standard_pack/
    payload/wiki_source_profiles/standard_asset.yml
                                               -> .ai-work/wiki_sources/profiles/    (MERGE, never overwrite)

WHY THE PROFILE IS MANDATORY (not "nice to have"): `lint_wiki._allowed_source_types()` unions the
`source_type` keys it reads from the profiles directory OF THE CONSUMING PROJECT. The pack's metas
declare `source_type: standard_asset`. A package that does not carry `standard_asset.yml` therefore
makes every project that installs the pack warn `meta_source_type_unknown` on every pack meta. So the
profile ships, and `install_guide.md` says where it must land.

Metas are built by delegating to `build_standard_pack_metas.py` (§12) — this tool writes no meta
itself, exactly as that tool writes no meta itself (one meta writer, `build_wiki_source_meta.py`).
Consequence of that delegation, surfaced up front instead of at rc=2: the meta builder resolves the
project root from the ASSET path, so the pack root must sit under a tree with an ancestor `.ai-work/`.
Run it on a pack outside such a tree and it fails with an off-topic message blaming whichever asset
file happened to be processed first. This tool checks the premise itself and refuses with a message
that names the real cause.

Version: read from `pack.yml > pack_version` (§9, the pack layer). Never a CLI flag — the pack owner
bumps the file, and two people building the same pack get the same version.

Run:
    py .ai-work/tooling/build_standard_pack_package.py --pack product/standard_pack
    py .ai-work/tooling/build_standard_pack_package.py --pack product/standard_pack \\
        --output /tmp/pkg --system aiws

Refuses (rc=2, nothing written) when the output directory already exists. There is deliberately no
`--force`: a release folder is an artifact someone may already have shipped, and "rebuild over it"
must be a human deleting a directory, not a flag.

Exit codes: 0 OK, 2 error.
"""
from __future__ import annotations

import argparse
import fnmatch
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import find_ai_work_root, read_text, today, write_text  # noqa: E402
# The pack.yml parser lives in the lint tool (Rule 2 — do not re-implement): one YAML reader for
# `pack.yml`, so "what the package believes the pack declares" cannot drift from "what lint checks".
from lint_standard_pack import PACK_REQUIRED_KEYS, as_list, parse_yaml  # noqa: E402

#: payload top-level dir -> where it lands in the consuming project (§12 / §7.2).
#: Single source for the install_guide table, the MANIFEST `Install destination` column and the
#: tests. Rule 14: the rationale for each destination lives with the value.
INSTALL_MAP: "list[tuple[str, str, str]]" = [
    ("standard_pack", ".ai-work/standard_pack",
     "the whole pack tree; this path IS the `artifact_locator` prefix every meta carries (§12), "
     "so changing it invalidates the metas"),
    ("standard_pack_wiki", ".ai-work/wiki_sources/aiws_meta/standard_pack",
     "meta group in the `aiws` namespace, beside methodology / wiki_guidelines / preset_knowledge (§12)"),
    ("wiki_source_profiles", ".ai-work/wiki_sources/profiles",
     "MERGE, never overwrite — without `standard_asset.yml` the consuming project lints every pack "
     "meta as `meta_source_type_unknown` (lint_wiki._allowed_source_types reads the CONSUMER's "
     "profiles dir)"),
]

PROFILE_REL = "wiki_sources/profiles/standard_asset.yml"
LOCATOR_PREFIX = ".ai-work/standard_pack"      # §12 — the INSTALLED layout, not the build layout
TEMPLATE_REL = "templates/standard_pack_install_guide.template.md"

EXCLUDE_DIR_NAMES = {"__pycache__", ".git", ".pytest_cache", ".mypy_cache", "node_modules"}
EXCLUDE_GLOBS = ["*.pyc", "*.pyo", "*.bak-*", "*.preview", ".DS_Store"]


# ---------- helpers ----------

def is_excluded(path: Path) -> bool:
    if path.name in EXCLUDE_DIR_NAMES:
        return True
    return any(fnmatch.fnmatch(path.name, pat) for pat in EXCLUDE_GLOBS)


def copy_tree_filtered(src: Path, dst: Path) -> int:
    """Recursive copy skipping build/VCS noise. Returns files copied."""
    copied = 0
    dst.mkdir(parents=True, exist_ok=True)
    # Rule 12 — order by POSIX relative path, never by raw Path sort (OS-dependent).
    for child in sorted(src.iterdir(), key=lambda p: p.name):
        if is_excluded(child):
            continue
        if child.is_dir():
            copied += copy_tree_filtered(child, dst / child.name)
        else:
            dst.mkdir(parents=True, exist_ok=True)
            shutil.copy2(child, dst / child.name)
            copied += 1
    return copied


def walk_files(root: Path) -> "list[Path]":
    """Every file under root, ordered by POSIX relative path (Rule 12)."""
    if not root.is_dir():
        return []
    return sorted((p for p in root.rglob("*") if p.is_file()),
                  key=lambda p: p.relative_to(root).as_posix())


def count_lines(path: Path) -> int:
    try:
        with path.open("r", encoding="utf-8", errors="replace") as f:
            return sum(1 for _ in f)
    except Exception:  # noqa: BLE001 — a binary asset simply has no line count
        return 0


def has_ai_work_ancestor(pack_root: Path) -> bool:
    """The premise of `build_standard_pack_metas.py` (via build_wiki_source_meta -> find_ai_work_root).

    Checked HERE so the refusal names the real cause. The meta builder's own failure mode is a rc=2
    that blames an arbitrary asset file, which sends the reader looking at frontmatter that is fine.
    """
    return any((p / ".ai-work").is_dir() for p in [pack_root, *pack_root.parents])


def read_pack_yml(pack_root: Path) -> dict:
    """Parse + validate `pack.yml` (§2.1). Raises SystemExit(2)-shaped errors via return None path."""
    data = parse_yaml(read_text(pack_root / "pack.yml"))
    if not isinstance(data, dict):
        raise ValueError("pack.yml did not parse to a mapping")
    missing = [k for k in PACK_REQUIRED_KEYS if not str(data.get(k, "") or "").strip()
               and not (k == "areas" and as_list(data.get("areas")))]
    if missing:
        raise ValueError("pack.yml is missing required key(s): " + ", ".join(missing) + " (§2.1)")
    return data


# ---------- generated package files ----------

def build_pack_version_text(meta: dict, date_str: str, pack_files: int, asset_count: int) -> str:
    """`PACK_VERSION.md` — the pack layer of §9, verbatim from `pack.yml`."""
    areas = ", ".join(str(a) for a in as_list(meta.get("areas"))) or "—"
    lines = [
        f"# PACK_VERSION — {meta.get('title')}",
        "",
        f"**pack_id:** {meta.get('pack_id')}",
        f"**pack_version:** {meta.get('pack_version')}",
        f"**title:** {meta.get('title')}",
        f"**owner:** {meta.get('owner')}",
        f"**aiws_min_version:** {meta.get('aiws_min_version')}",
        f"**areas:** {areas}",
        f"**build_date:** {date_str}",
        # Two different numbers on purpose: a pack tree carries non-asset files too (README,
        # pack.yml, task_catalog.yml, roles.yml). `assets` = files with `artifact_type:
        # standard_asset` = metas built (§3/§12), and it is the number a reader means by "how big
        # is this pack".
        f"**pack files:** {pack_files}",
        f"**assets (= metas built):** {asset_count}",
        "",
        "Ba lớp version (Standard_Pack_Contract_Spec_MVP §9): **AIWS** (`product/aiws_version.md` →",
        "bản cài) · **Pack** (`pack.yml > pack_version` → chính file này) · **Pin của dự án**",
        "(`.ai-work/project_profile.yml`, khối `AIWS:BEGIN`, khoá `standard_pack`).",
        "",
        f"`aiws_min_version` là hợp đồng một chiều: pack cần AIWS **từ {meta.get('aiws_min_version')}**",
        "trở lên. Tool cài từ chối khi bản AIWS của dự án thấp hơn (§9.3) — từ chối *trước* khi chép",
        "byte nào. Pack không bao giờ khai \"AIWS tối đa\".",
        "",
        "Nâng cấp pack luôn là hành động tường minh của người (§9.1): không có đường nào để một bản",
        "cài tự kéo pack mới về.",
        "",
    ]
    if str(meta.get("description", "") or "").strip():
        lines += ["## Description", "", str(meta["description"]).strip(), ""]
    return "\n".join(lines)


def payload_table(output: Path) -> str:
    """The payload -> install mapping, as a markdown table, with the REAL per-section file counts."""
    rows = ["| # | Source (trong package) | Destination (dự án đích) | Files | Ghi chú |",
            "|---|---|---|------:|---|"]
    for i, (name, dest, note) in enumerate(INSTALL_MAP, 1):
        n = len(walk_files(output / "payload" / name))
        rows.append(f"| {i} | `payload/{name}/` | `{dest}/` | {n} | {note} |")
    return "\n".join(rows)


def build_install_guide_text(template: Path, output: Path, meta: dict, date_str: str,
                             asset_count: int, meta_count: int) -> str:
    """Render the install guide from its template.

    A template file, not a string constant in this module, because the guide is prose a human edits
    and reviews; `{{TOKEN}}` substitution (not `str.format`) so the guide can contain braces, YAML
    and code fences without escaping.
    """
    text = read_text(template)
    total = len(walk_files(output / "payload"))
    subs = {
        "PACK_ID": str(meta.get("pack_id", "")),
        "PACK_TITLE": str(meta.get("title", "")),
        "PACK_VERSION": str(meta.get("pack_version", "")),
        "OWNER": str(meta.get("owner", "")),
        "AIWS_MIN_VERSION": str(meta.get("aiws_min_version", "")),
        "AREAS": ", ".join(str(a) for a in as_list(meta.get("areas"))) or "—",
        "BUILD_DATE": date_str,
        "PAYLOAD_TABLE": payload_table(output),
        "TOTAL_FILES": str(total),
        "ASSET_COUNT": str(asset_count),
        "META_COUNT": str(meta_count),
    }
    for key, val in subs.items():
        text = text.replace("{{" + key + "}}", val)
    left = [t for t in ("{{",) if t in text]
    if left:
        # A token the builder does not know about would ship to adopters verbatim.
        raise ValueError(f"install guide template has unsubstituted {{{{…}}}} tokens: {template}")
    return text


def build_manifest_text(output: Path, meta: dict, date_str: str) -> str:
    """`MANIFEST.md` — counted from the REAL payload tree, after everything has been written.

    Never from the intended file list: a section that failed to copy, a meta the builder skipped or a
    file an exclusion swallowed would all still be "counted" by a plan-derived number, and the
    manifest would state a total the package does not have.
    """
    payload_root = output / "payload"
    files = walk_files(payload_root)
    dest_of = {name: dest for name, dest, _ in INSTALL_MAP}
    lines = [
        f"# MANIFEST — Standard Pack `{meta.get('pack_id')}` {meta.get('pack_version')}",
        f"**Pack:** {meta.get('title')} (owner: {meta.get('owner')})",
        f"**pack_version:** {meta.get('pack_version')}",
        f"**aiws_min_version:** {meta.get('aiws_min_version')}",
        f"**Build date:** {date_str}",
        f"**Total files:** {len(files)}",
        "",
        "Con số trên đếm **cây `payload/` thật** sau khi build ghi xong, không đếm danh sách dự định.",
        "`PACK_VERSION.md`, `MANIFEST.md`, `install_guide.md` nằm ở gốc package, ngoài `payload/`, nên",
        "không nằm trong tổng này.",
        "",
        "## Intentional exclusions",
        "",
        "- **Không có gì của AIWS trong package này.** Pack cài lên trên một dự án đã có AIWS; package",
        "  AIWS là một package khác (`build_aiws_install_package.py`) và không section nào của nó trỏ",
        "  vào `product/standard_pack` — hai cây không bao giờ trộn vào nhau.",
        "- `__pycache__/`, `*.pyc`, `.git/`, `*.bak-*`, `*.preview` — rác build, không bao giờ ship.",
        "",
        "| File | Section | Install destination | Lines |",
        "|------|---------|---------------------|------:|",
    ]
    for f in files:
        rel = f.relative_to(payload_root).as_posix()
        section = rel.split("/", 1)[0]
        dest = dest_of.get(section, "—")
        rest = rel.split("/", 1)[1] if "/" in rel else ""
        installed = f"{dest}/{rest}" if rest and dest != "—" else dest
        n = count_lines(f) if f.suffix in {".md", ".py", ".yml", ".yaml", ".jsonl", ".txt"} else 0
        lines.append(f"| payload/{rel} | {section} | {installed} | {n if n else '-'} |")
    return "\n".join(lines) + "\n"


# ---------- build ----------

def build(pack_root: Path, output: Path, profile: Path, template: Path,
          system: "str | None", common: bool, date_str: str) -> int:
    meta = read_pack_yml(pack_root)
    pack_id = str(meta["pack_id"]).strip()
    pack_version = str(meta["pack_version"]).strip()

    # Refuse BEFORE creating anything (§9.3 discipline: a half-written package is worse than none).
    if output.exists():
        print(f"error: output already exists: {output}\n"
              f"       there is no --force: delete the directory yourself, or pass a different "
              f"--output. A release folder may already have been shipped.", file=sys.stderr)
        return 2

    print(f"building Standard Pack package")
    print(f"  pack:    {pack_id} {pack_version} ({meta.get('title')})")
    print(f"  source:  {pack_root}")
    print(f"  output:  {output}")

    output.mkdir(parents=True)
    payload_root = output / "payload"

    # 1) the pack tree, verbatim
    n_pack = copy_tree_filtered(pack_root, payload_root / "standard_pack")
    print(f"  [standard_pack       ] {n_pack} files")

    # 2) metas — DELEGATED (§12). Built from the SOURCE pack (which satisfies the ancestor-`.ai-work/`
    #    premise), never from the payload copy, whose location the caller chose with --output and
    #    which may well sit outside any AIWS tree.
    metas_out = payload_root / "standard_pack_wiki"
    cmd = [sys.executable, str(Path(__file__).resolve().parent / "build_standard_pack_metas.py"),
           "--pack", str(pack_root), "--out", str(metas_out),
           "--locator-prefix", LOCATOR_PREFIX, "--profile", str(profile), "--mode", "create"]
    if system:
        cmd += ["--system", system]
    elif common:
        cmd.append("--common")
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        print(r.stdout, end="")
        print(r.stderr, end="", file=sys.stderr)
        print(f"error: meta build failed rc={r.returncode} — package NOT complete; remove the "
              f"partial output before re-running: {output}", file=sys.stderr)
        return 2
    n_meta = len(list(metas_out.glob("*.md")))
    print(f"  [standard_pack_wiki  ] {n_meta} metas (build_standard_pack_metas.py, "
          f"locator prefix {LOCATOR_PREFIX})")

    # 3) the profile — MANDATORY, see the module docstring.
    prof_dst = payload_root / "wiki_source_profiles" / profile.name
    prof_dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(profile, prof_dst)
    print(f"  [wiki_source_profiles] 1 file ({profile.name}) — without it every consuming project "
          f"warns meta_source_type_unknown")

    # 4) generated package-root files. install_guide + MANIFEST are written LAST, so both read a
    #    payload tree that is already complete.
    write_text(output / "PACK_VERSION.md",
               build_pack_version_text(meta, date_str, n_pack, n_meta))
    write_text(output / "install_guide.md",
               build_install_guide_text(template, output, meta, date_str, n_meta, n_meta))
    write_text(output / "MANIFEST.md", build_manifest_text(output, meta, date_str))

    total = len(walk_files(payload_root))
    print(f"\n  total payload files: {total}")
    print(f"  package: {output}")
    return 0


def main(argv: "list[str] | None" = None) -> int:
    p = argparse.ArgumentParser(
        description="Build an installable package for one Standard Pack (§2/§9/§12)")
    p.add_argument("--pack", required=True, help="pack root directory (the one holding pack.yml)")
    p.add_argument("--output", default="", metavar="DIR",
                   help="output directory (default: releases/<pack_id>_<pack_version>_<date>)")
    p.add_argument("--project-root", default="", metavar="DIR",
                   help="project root (default: walk up from cwd) — used for the default --output "
                        "and the default --profile")
    p.add_argument("--profile", default="", metavar="FILE",
                   help=f"Source Interpretation Profile to SHIP (default: <project-root>/.ai-work/"
                        f"{PROFILE_REL})")
    p.add_argument("--template", default="", metavar="FILE",
                   help=f"install guide template (default: <tooling>/{TEMPLATE_REL})")
    p.add_argument("--system", default=None, metavar="ID",
                   help="tag the metas to system <id> (passed through to build_standard_pack_metas)")
    p.add_argument("--common", action="store_true",
                   help="mark the metas system-agnostic (default when neither flag is given: a pack "
                        "is process content, not one system's knowledge)")
    p.add_argument("--date", default="", help="build date (default: today, ISO)")
    ns = p.parse_args(argv)

    if ns.system and ns.common:
        print("error: --system and --common are mutually exclusive", file=sys.stderr)
        return 2

    pack_root = Path(ns.pack).resolve()
    if not pack_root.is_dir():
        print(f"error: pack root not found: {pack_root}", file=sys.stderr)
        return 2
    if not (pack_root / "pack.yml").exists():
        print(f"error: not a standard pack (no pack.yml): {pack_root}", file=sys.stderr)
        return 2
    if not has_ai_work_ancestor(pack_root):
        print(f"error: the pack root has no ancestor directory containing `.ai-work/`: {pack_root}\n"
              f"       build_standard_pack_metas.py resolves the project root from the ASSET path, so "
              f"it cannot build metas for a pack outside an AIWS tree (its own failure message blames "
              f"an arbitrary asset file instead). Move/copy the pack inside a project that has "
              f"`.ai-work/` and build from there.", file=sys.stderr)
        return 2

    project_root = Path(ns.project_root).resolve() if ns.project_root \
        else find_ai_work_root(Path.cwd())

    profile = Path(ns.profile).resolve() if ns.profile \
        else (project_root / ".ai-work" / PROFILE_REL)
    if not profile.is_file():
        print(f"error: profile not found: {profile}\n"
              f"       it is NOT optional — the package must carry it, or every project that "
              f"installs this pack warns `meta_source_type_unknown` on every pack meta.",
              file=sys.stderr)
        return 2

    template = Path(ns.template).resolve() if ns.template \
        else (Path(__file__).resolve().parent / TEMPLATE_REL)
    if not template.is_file():
        print(f"error: install guide template not found: {template}", file=sys.stderr)
        return 2

    try:
        meta = read_pack_yml(pack_root)
    except Exception as exc:  # noqa: BLE001 — an unreadable pack.yml is a refusal, with the reason
        print(f"error: {exc} ({pack_root / 'pack.yml'})", file=sys.stderr)
        return 2

    date_str = ns.date.strip() or today()
    if ns.output:
        output = Path(ns.output).resolve()
    else:
        output = (project_root / "releases" /
                  f"{str(meta['pack_id']).strip()}_{str(meta['pack_version']).strip()}_{date_str}")

    try:
        return build(pack_root, output, profile, template,
                     ns.system, ns.common or not ns.system, date_str)
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
