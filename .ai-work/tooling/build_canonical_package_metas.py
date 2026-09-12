#!/usr/bin/env python3
"""One-shot driver: build Wiki Source Metas for any adopted canonical package.

Walks every *.md under a package root directory and creates a primary
Wiki Source Meta per file. Source ids are stable:

    <prefix>-<version>-<relative-slug>-<short-hash>

Default `--source-type` is `methodology_spec` and default `--id-prefix`
is `SRC-METHOD` so that legacy invocations for the methodology tree
keep working unchanged. Pass `--source-type` / `--id-prefix` to target
a different canonical package (e.g. wiki_guideline / SRC-WIKIGUIDE).

Run (methodology example — single-index repo dùng PRODUCT root, CR-AIWS-2026-08-052):
    python .ai-work/tooling/build_canonical_package_metas.py \
        --root product/methodology/ai_work_system \
        --profile .ai-work/wiki_sources/profiles/methodology_spec.yml

Run (wiki guideline example):
    python .ai-work/tooling/build_canonical_package_metas.py \
        --root product/wiki_guidelines \
        --profile .ai-work/wiki_sources/profiles/wiki_guideline.yml \
        --meta-dir .ai-work/wiki_sources/meta/wiki_guidelines \
        --source-type wiki_guideline \
        --id-prefix SRC-WIKIGUIDE

Curation-state là của HUMAN — builder chỉ được đổi khi flag tương ứng được truyền tường minh;
refresh mặc định carry giá trị cũ. Tool này delegate toàn bộ write qua
`build_wiki_source_meta.py --mode refresh` nên hưởng luật preserve ở đó
(CURATION_PRESERVE_FIELDS trong _common.py — CR-AIWS-2026-08-058).

NOTE (CR-AIWS-2026-08-052 C6): trong repo khai `wiki_single_index: true` (project_profile.yml),
artifact_locator phải trỏ cây PRODUCT (SoT) — tool TỪ CHỐI một --root nằm dưới
.ai-work/truth/canonical/ hoặc .ai-work/preset_knowledge/ để refresh không re-point ngược.
Downstream installs (không set key) build từ .ai-work như cũ.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import find_ai_work_root, read_text  # noqa: E402

SLUG_RE = re.compile(r"[^A-Za-z0-9]+")


def slugify(text: str, fallback: str = "x") -> str:
    s = SLUG_RE.sub("-", text).strip("-").lower()
    return s or fallback


def short_hash(text: str, length: int = 4) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:length]


# CR-AIWS-2026-07-041 T2: the id hash MUST be computed from a CANONICAL path form, or the same file
# gets a different source_id per OS — sha1('a/b.md') != sha1('a\\b.md') — and a rebuild on POSIX
# would mint fresh ids for every NESTED meta, orphaning a corpus that now ships verbatim (CR-06-041).
#
# The canonical form is the BACKSLASH form, not POSIX. That is deliberate: the shipped 188-meta
# corpus was built on Windows, so backslash-canonicalization is BOTH os-stable AND byte-compatible
# with every id already in `aiws_meta/`, `index.aiws.jsonl`, the generated overview page, the golden
# lookup cases and ~185 other referencing files. Canonicalizing on POSIX would be equally correct in
# theory but would re-key all 188 ids — see the Apply Outcome of CR-041 (DP-041-2 deviation) and the
# open point left for the PO. The hash input is an opaque internal string; only its determinism matters.
_ID_HASH_SEP = "\\"


def build_source_id(version: str, rel_path: Path, prefix: str = "SRC-METHOD") -> str:
    rel_str = str(rel_path).replace("\\", "/")          # normalize first (OS-independent)
    slug = slugify(rel_str)
    h = short_hash(rel_str.replace("/", _ID_HASH_SEP))  # then canonicalize to the corpus form
    ver = slugify(version)
    return f"{prefix}-{ver}-{slug}-{h}"[:150]


def main() -> int:
    p = argparse.ArgumentParser(
        description="Build Wiki Source Metas for a methodology-like tree "
                    "(methodology spec, wiki guideline package, etc.)"
    )
    p.add_argument("--root", required=True, help="package root directory")
    p.add_argument("--profile", required=True)
    p.add_argument("--meta-dir", help="Override meta output dir")
    p.add_argument("--source-type", default="methodology_spec",
                   help="Source type to record in each meta (default: methodology_spec)")
    p.add_argument("--id-prefix", default="SRC-METHOD",
                   help="Source id prefix (default: SRC-METHOD)")
    p.add_argument("--with-related-sources", action="store_true",
                   help="Emit the '## Related Sources' scaffold per meta (opt-in). "
                        "Default: suppressed, so bulk reference-doc registration is "
                        "lint-clean (no meta_related_sources_todo warnings) without a "
                        "post-build strip (CAP-091-01).")
    # CR-AIWS-2026-06-061 §8.5: this meta writer must be system-aware. Pass --system/--common
    # through to build_wiki_source_meta (required in a multi_system project when building NEW metas;
    # in-place refresh of existing metas preserves their system even without it).
    p.add_argument("--system", default=None, metavar="ID",
                   help="Multi-system: tag each meta to system <id> (passed to build_wiki_source_meta).")
    p.add_argument("--common", action="store_true",
                   help="Multi-system: mark metas system-agnostic/common (mutually exclusive with --system).")
    # H6: keep large canonical specs as a single meta (no chunking) unless explicitly requested.
    p.add_argument("--chunk", action="store_true",
                   help="H6: allow chunking large sources into parent+section metas (default: --no-chunk).")
    ns = p.parse_args()

    root = Path(ns.root).resolve()
    profile = Path(ns.profile).resolve()
    if not root.is_dir():
        print(f"error: root not found: {root}", file=sys.stderr)
        return 2
    if not profile.exists():
        print(f"error: profile not found: {profile}", file=sys.stderr)
        return 2

    ai_work = find_ai_work_root(profile) / ".ai-work"
    # CR-AIWS-2026-08-052 C6 — single-index repo: artifact_locator = product/ SoT. Refuse a
    # working-copy root so a habitual refresh cannot re-point the metas back at .ai-work.
    # CR-AIWS-2026-08-128 C3: one reader. The regex `wiki_single_index()` is gone; the key
    # comes from the same parse everything else uses, so a damaged profile raises here too.
    from _common import read_project_config  # local import: keep module import surface unchanged
    if read_project_config(ai_work)["wiki_single_index"]:
        try:
            _rel_root = root.relative_to(ai_work.parent).as_posix()
        except ValueError:
            _rel_root = root.as_posix()
        if _rel_root.startswith((".ai-work/truth/canonical", ".ai-work/preset_knowledge")):
            print("error: wiki_single_index=true — build canonical metas from the PRODUCT root "
                  f"(SoT), not the working copy '{_rel_root}' (CR-AIWS-2026-08-052 C6). "
                  "Example: --root product/methodology/ai_work_system", file=sys.stderr)
            return 2
    version = root.name
    meta_dir = (
        Path(ns.meta_dir).resolve()
        if ns.meta_dir
        else ai_work / "wiki_sources" / "meta" / "methodology"
    )
    meta_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(root.rglob("*.md"))
    print(f"found {len(files)} md files under {root}")

    # CR-AIWS-2026-07-006 A4: per-profile chunk opt-in (`chunk_enabled: true` in the profile YAML).
    _profile_chunk_enabled = bool(
        re.search(r"^\s*chunk_enabled\s*:\s*true\s*$", read_text(profile), re.MULTILINE))
    if _profile_chunk_enabled and not ns.chunk:
        print("profile chunk_enabled: true → chunking large sources (CR-AIWS-2026-07-006 A4)")

    builder = Path(__file__).resolve().parent / "build_wiki_source_meta.py"
    count = 0
    for md_file in files:
        rel = md_file.relative_to(root)
        sid = build_source_id(version, rel, prefix=ns.id_prefix)
        title = f"{version} / {rel.as_posix()}"
        out_path = meta_dir / f"{sid}.md"
        cmd = [
            sys.executable, str(builder),
            "--artifact", str(md_file),
            "--source-id", sid,
            "--source-type", ns.source_type,
            "--profile", str(profile),
            "--title", title,
            "--out", str(out_path),
            "--mode", "refresh",
        ]
        # CR-061 §8.5: system passthrough. Refresh of an existing meta preserves its system when
        # neither flag is given, but pass it explicitly so NEW metas in a multi_system project build.
        if ns.system:
            cmd += ["--system", ns.system]
        elif ns.common:
            cmd.append("--common")
        # H6: default to no chunking for canonical packages UNLESS the profile opts in via
        # `chunk_enabled: true` (CR-AIWS-2026-07-006 A4 — per-profile dogfood knob, DP-912-1 nhịp 1;
        # nhịp 2 = flip this default once dogfood metrics land). CLI --chunk still forces on.
        if not ns.chunk and not _profile_chunk_enabled:
            cmd.append("--no-chunk")
        # CAP-091-01: suppress the '## Related Sources' TODO scaffold by default so bulk
        # reference-doc registration is lint-clean; pass --with-related-sources to opt back in.
        if not ns.with_related_sources:
            cmd.append("--no-related-sources")
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        if r.returncode != 0:
            print(f"error on {md_file}: {r.stderr or r.stdout}", file=sys.stderr)
            return 2
        count += 1

    print(f"primary metas: {count}")
    print(f"output dir:    {meta_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
