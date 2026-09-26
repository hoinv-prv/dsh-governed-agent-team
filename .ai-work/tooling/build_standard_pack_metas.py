#!/usr/bin/env python3
"""Build Wiki Source Metas for a Standard Pack (Standard_Pack_Contract_Spec_MVP §12).

One meta per pack ASSET — a `.md` whose frontmatter carries `artifact_type: standard_asset`
(§3). Non-asset files in the pack tree (README, CHANGELOG, `pack.yml`, `task_catalog.yml`,
`common/roles.yml`) are skipped, not guessed at.

Projection contract (§12):

    source_id           SRC-STDPACK-<asset_id>
    source_type         standard_asset   (profile_id: standard_asset)
    artifact_locator    <locator-prefix>/<path relative to the pack root>
                        default prefix `.ai-work/standard_pack` = the INSTALLED layout,
                        so a meta built at packaging time is already correct once the
                        pack is copied into a project.
    meta group          whatever --out points at; the shipped group is
                        `.ai-work/wiki_sources/aiws_meta/standard_pack/` (namespace `aiws`,
                        beside methodology / wiki_guidelines / preset_knowledge).

This tool writes NO meta itself: every file is written by `build_wiki_source_meta.py`
(the one meta writer — same delegation as `build_canonical_package_metas.py`), so the
frontmatter shape, the curation-state preserve rules (CR-AIWS-2026-08-058) and the
multi-system gate all stay in one place.

Run:
    py .ai-work/tooling/build_standard_pack_metas.py \
        --pack product/standard_pack \
        --out .ai-work/wiki_sources/aiws_meta/standard_pack \
        --system aiws

`--out` is REQUIRED and never defaulted: which meta group a pack lands in is a decision of
the caller (packaging vs. install vs. a test tempdir), not of this tool.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import parse_frontmatter, read_text  # noqa: E402

ASSET_ARTIFACT_TYPE = "standard_asset"
SOURCE_TYPE = "standard_asset"
ID_PREFIX = "SRC-STDPACK"
DEFAULT_LOCATOR_PREFIX = ".ai-work/standard_pack"
DEFAULT_PROFILE_REL = "wiki_sources/profiles/standard_asset.yml"


def iter_assets(pack_root: Path) -> "list[tuple[Path, dict]]":
    """Every `.md` under the pack root whose frontmatter declares a standard asset."""
    found: list[tuple[Path, dict]] = []
    for md in sorted(pack_root.rglob("*.md"), key=lambda p: p.relative_to(pack_root).as_posix()):
        try:
            meta, _ = parse_frontmatter(read_text(md))
        except Exception as exc:  # noqa: BLE001 — an unreadable file is reported, not skipped silently
            print(f"warning: cannot parse frontmatter of {md}: {exc}", file=sys.stderr)
            continue
        if (meta or {}).get("artifact_type") == ASSET_ARTIFACT_TYPE:
            found.append((md, meta))
    return found


def _first_prose(body: str, limit: int = 240) -> str:
    """First prose paragraph of the asset body: no heading, table, list or fence."""
    para: list[str] = []
    for raw in body.splitlines():
        line = raw.strip()
        if not line:
            if para:
                break
            continue
        if line.startswith(("#", "|", "-", "*", ">", "```", "<!--")):
            if para:
                break
            continue
        para.append(line)
    text = " ".join(para).strip()
    return text[:limit].rstrip() if text else ""


def asset_summary(meta: dict, body: str) -> str:
    """Factual, frontmatter-derived summary (§3 fields) + the asset's own opening prose.

    Deterministic on purpose: the builder never invents semantics — every clause is a field
    the asset itself declares. A human/LLM completion pass may write a better one later.
    """
    head = (f"{meta.get('title') or meta.get('asset_id')} — standard pack asset "
            f"(kind: {meta.get('kind', '?')}, area: {meta.get('area', '?')}, "
            f"classification: {meta.get('classification', '?')}, "
            f"pack: {meta.get('pack_id', '?')}, asset_id: {meta.get('asset_id', '?')}).")
    prose = _first_prose(body)
    return f"{head} {prose}".strip() if prose else head


def asset_lookup_keys(meta: dict) -> "list[str]":
    """Pinned keys along the three axes a reader searches an asset by: kind · area · classification."""
    area = str(meta.get("area", "") or "")
    kind = str(meta.get("kind", "") or "")
    keys = [
        str(meta.get("title", "") or ""),
        str(meta.get("asset_id", "") or ""),
        f"{area} {kind}".strip(),
        f"{kind} {meta.get('classification', '')}".strip(),
        str(meta.get("pack_id", "") or ""),
        kind,
        area,
        str(meta.get("classification", "") or ""),
    ]
    out: list[str] = []
    seen: set[str] = set()
    for k in keys:
        k = k.strip()
        if k and k.lower() not in seen:
            seen.add(k.lower())
            out.append(k)
    return out


def main() -> int:
    p = argparse.ArgumentParser(
        description="Build Wiki Source Metas for a Standard Pack (one meta per asset)")
    p.add_argument("--pack", required=True, help="pack root directory (the one holding pack.yml)")
    p.add_argument("--out", required=True, metavar="DIR",
                   help="meta output directory (e.g. .ai-work/wiki_sources/aiws_meta/standard_pack)")
    p.add_argument("--locator-prefix", default=DEFAULT_LOCATOR_PREFIX,
                   help=f"artifact_locator prefix, i.e. where the pack lives once installed "
                        f"(default: {DEFAULT_LOCATOR_PREFIX})")
    p.add_argument("--profile", default=None,
                   help="Source Interpretation Profile (default: <ai-work>/" + DEFAULT_PROFILE_REL + ")")
    p.add_argument("--mode", choices=["create", "refresh"], default="refresh",
                   help="passed through to build_wiki_source_meta (default: refresh — idempotent, "
                        "preserves HUMAN curation-state)")
    p.add_argument("--authority-level", default=None,
                   help="optional curation-state passthrough; omitted by default (HUMAN owns it)")
    # Multi-system passthrough (CR-AIWS-2026-06-061 §8.5): a multi_system project HARD-REQUIRES one.
    p.add_argument("--system", default=None, metavar="ID",
                   help="tag each meta to system <id> (passed to build_wiki_source_meta)")
    p.add_argument("--common", action="store_true",
                   help="mark metas system-agnostic/common (mutually exclusive with --system)")
    ns = p.parse_args()

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

    tooling = Path(__file__).resolve().parent
    if ns.profile:
        profile = Path(ns.profile).resolve()
    else:
        profile = tooling.parent / DEFAULT_PROFILE_REL
    if not profile.exists():
        print(f"error: profile not found: {profile}", file=sys.stderr)
        return 2

    out_dir = Path(ns.out).resolve()
    prefix = ns.locator_prefix.replace("\\", "/").rstrip("/")

    assets = iter_assets(pack_root)
    if not assets:
        print(f"error: no `artifact_type: {ASSET_ARTIFACT_TYPE}` file under {pack_root}",
              file=sys.stderr)
        return 2
    print(f"assets found: {len(assets)} under {pack_root}")

    # Validate the WHOLE pack before writing anything: a half-written meta group is worse than
    # a refusal, and the id rules (§3/§3.1) are pack-wide, not per-file.
    seen_ids: dict[str, str] = {}
    plan: list[tuple[Path, dict, str, str]] = []          # (file, frontmatter, rel, source_id)
    for md_file, meta in assets:
        rel = md_file.relative_to(pack_root).as_posix()
        asset_id = str(meta.get("asset_id", "") or "").strip()
        if not asset_id:
            print(f"error: asset without `asset_id`: {rel} (§3 — asset_id is REQUIRED)",
                  file=sys.stderr)
            return 2
        sid = f"{ID_PREFIX}-{asset_id}"
        if sid in seen_ids:
            print(f"error: duplicate asset_id '{asset_id}' — {rel} collides with "
                  f"{seen_ids[sid]} (§3.1: asset_id is unique across the pack)", file=sys.stderr)
            return 2
        seen_ids[sid] = rel
        plan.append((md_file, meta, rel, sid))

    out_dir.mkdir(parents=True, exist_ok=True)      # only after the pack validates
    builder = tooling / "build_wiki_source_meta.py"
    count = 0
    for md_file, meta, rel, sid in plan:
        asset_id = str(meta.get("asset_id", "")).strip()
        _, body = parse_frontmatter(read_text(md_file))
        cmd = [
            sys.executable, str(builder),
            "--artifact", str(md_file),
            "--source-id", sid,
            "--source-type", SOURCE_TYPE,
            "--profile", str(profile),
            "--title", str(meta.get("title") or asset_id),
            "--out", str(out_dir / f"{sid}.md"),
            "--mode", ns.mode,
            # §12: the locator describes where the asset lives once INSTALLED, not where this
            # build read it from. build_wiki_source_meta stores --representation-locator as the
            # meta's artifact_locator, which is exactly the rebase this needs.
            "--representation-locator", f"{prefix}/{rel}",
            "--summary", asset_summary(meta, body),
            "--lookup-keys", ",".join(asset_lookup_keys(meta)),
            # small, hand-authored assets: one meta each, never chunked; and no Related Sources
            # TODO scaffold (bulk registration stays lint-clean — CAP-091-01).
            "--no-chunk",
            "--no-related-sources",
        ]
        if ns.authority_level:
            cmd += ["--authority-level", ns.authority_level]
        if ns.system:
            cmd += ["--system", ns.system]
        elif ns.common:
            cmd.append("--common")
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode != 0:
            print(f"error on {rel}: {r.stderr or r.stdout}", file=sys.stderr)
            return 2
        count += 1

    print(f"metas written: {count}")
    print(f"output dir:    {out_dir}")
    print(f"locator prefix: {prefix}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
