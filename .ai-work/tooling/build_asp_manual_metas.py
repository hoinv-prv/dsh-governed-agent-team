#!/usr/bin/env python3
"""One-shot driver: build Wiki Source Metas for the ASP vendor manual set.

Layout assumed (one entry per MD chapter):

    references/vendor/asp_manuals/<category>/<manual>/MD/<stem>.md
    references/vendor/asp_manuals/<category>/<manual>/PDF/<stem>.pdf    (companion)
    references/vendor/asp_manuals/<category>/<manual>/Word/<stem>.docx  (companion)

For each MD chapter the driver writes a **primary** Wiki Source Meta.
For each matching PDF/DOCX it writes a **companion** Wiki Source Meta
that carries a `companion_of` reference to the primary source_id and a
`do_not_read_content: true` flag so LLMs read the paired MD instead.

Primary metas are built by calling `build_wiki_source_meta.py` in the
same tooling folder. Companion metas are written directly (no content
read) and share the primary's lookup keys + knowledge targets.

Usage:
    python .ai-work/tooling/build_asp_manual_metas.py \
        --root references/vendor/asp_manuals \
        --profile .ai-work/wiki_sources/profiles/asp_manual.yml
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (  # noqa: E402
    dump_frontmatter,
    extract_sections,
    find_ai_work_root,
    parse_frontmatter,
    read_text,
    today,
    write_text,
)

SLUG_RE = re.compile(r"[^A-Za-z0-9]+")


def slugify(text: str, fallback: str = "x") -> str:
    s = SLUG_RE.sub("-", text).strip("-").lower()
    return s or fallback


def short_hash(text: str, length: int = 6) -> str:
    import hashlib
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:length]


def build_source_id(category: str, manual: str, stem: str) -> str:
    cat = slugify(category) or short_hash(category)
    man_slug = slugify(manual) or short_hash(manual)
    chap = slugify(stem) or short_hash(stem)
    # Always attach short hashes of the original names so IDs are unique
    # even when slugs collapse (Vietnamese / CJK characters strip to same form).
    man_h = short_hash(manual, 4)
    chap_h = short_hash(stem, 4)
    return f"SRC-ASP-{cat}-{man_slug}-{man_h}-{chap}-{chap_h}"[:140]


def run_primary_builder(artifact: Path, source_id: str, title: str,
                        profile: Path, out_dir: Path) -> Path:
    out_path = out_dir / f"{source_id}.md"
    cmd = [
        sys.executable,
        str(Path(__file__).resolve().parent / "build_wiki_source_meta.py"),
        "--artifact", str(artifact),
        "--source-id", source_id,
        "--source-type", "asp_vendor_manual",
        "--profile", str(profile),
        "--title", title,
        "--out", str(out_path),
        "--mode", "refresh",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        raise SystemExit(
            f"primary build failed for {artifact}:\n{r.stderr or r.stdout}"
        )
    return out_path


def _list_items(section_text: str) -> list[str]:
    out: list[str] = []
    for line in section_text.splitlines():
        s = line.strip()
        if s.startswith("- "):
            out.append(s[2:].strip())
    return out


def write_companion_meta(
    *,
    out_dir: Path,
    binary_path: Path,
    primary_meta_path: Path,
    primary_source_id: str,
    category: str,
    manual: str,
    stem: str,
    fmt: str,
    profile: Path,
) -> Path:
    """Write a companion meta pointing at the primary MD meta. Never reads binary."""
    companion_sid = f"{primary_source_id}-{fmt}"
    out_path = out_dir / f"{companion_sid}.md"

    # Inherit lookup keys + knowledge targets from primary projection
    primary_meta, primary_body = parse_frontmatter(read_text(primary_meta_path))
    sections = extract_sections(primary_body)
    lookup_keys = _list_items(sections.get("Lookup Keys", ""))
    knowledge_targets = _list_items(sections.get("Knowledge Targets", ""))
    title = f"{primary_meta.get('title', stem)} ({fmt.upper()} companion)"

    meta = {
        "artifact_type": "wiki_source_meta",
        "source_id": companion_sid,
        "title": title,
        "source_type": "asp_vendor_manual_companion",
        "artifact_locator": str(binary_path),
        "profile_id": "asp_manual",
        "status": "active",
        "format": fmt,
        "is_companion": "true",
        "do_not_read_content": "true",
        "companion_of": primary_source_id,
        "companion_primary_meta": str(primary_meta_path),
        "updated_at": today(),
    }

    body: list[str] = [
        f"# Wiki Source Meta — {title}",
        "",
        "> ⚠️ **DO NOT READ THIS BINARY.** This is a companion of a Markdown",
        "> chapter; the full textual content lives in the paired MD file.",
        "> LLMs and humans should open the primary MD meta instead.",
        "",
        "## Summary",
        (f"Binary companion ({fmt.upper()}) of the MD chapter `{stem}` from "
         f"the ASP vendor manual `{manual}`. Content is NOT to be read from "
         f"this file — read the paired MD chapter instead."),
        "",
        "## Knowledge Targets",
    ]
    for kt in knowledge_targets or ["reference"]:
        body.append(f"- {kt}")
    body += [
        "",
        "## Lookup Keys",
    ]
    for k in lookup_keys:
        body.append(f"- {k}")
    body += [
        "",
        "## Profile Mapping",
        f"- profile_id: asp_manual",
        f"- profile_path: {profile}",
        "",
        "## Artifact Reference",
        f"- artifact_locator: {binary_path}",
        f"- format: {fmt}",
        "",
        "## Companion Of",
        f"- primary_source_id: {primary_source_id}",
        f"- primary_meta: {primary_meta_path}",
        f"- relation: same-content-different-format",
        "",
        "## Read Rules",
        "- **Do NOT read this binary artifact.**",
        "- To consume the content, open the primary MD meta and then the",
        "  paired `MD/` chapter file.",
        "- This meta exists so lookups find the binary file and redirect",
        "  the reader to the MD equivalent.",
        "",
        "## Cautions",
        "- vendor reference material; not project truth",
        "- binary format (PDF/DOCX) is provided for archival fidelity only",
        "",
    ]

    write_text(out_path, dump_frontmatter(meta) + "\n".join(body))
    return out_path


def _normalize_stem(stem: str) -> str:
    """Lowercase and collapse separators; drops trailing numeric/word noise minimally."""
    return SLUG_RE.sub("-", stem).strip("-").lower()


def find_pair(stem: str, md_files: list[Path]) -> Path | None:
    """Match a binary stem to an MD file. Exact match, then prefix/contains match."""
    norm = _normalize_stem(stem)
    # exact
    for md in md_files:
        if md.stem == stem:
            return md
    # normalized exact
    for md in md_files:
        if _normalize_stem(md.stem) == norm:
            return md
    # normalized prefix: binary "Chương 1" → MD "Chương_1_..."
    prefix = norm + "-"
    for md in md_files:
        if _normalize_stem(md.stem).startswith(prefix):
            return md
    # token intersection fallback (first token)
    bin_tokens = norm.split("-")
    if not bin_tokens:
        return None
    first = bin_tokens[0]
    candidates = [md for md in md_files
                  if _normalize_stem(md.stem).startswith(first + "-")
                  or _normalize_stem(md.stem) == first]
    if len(candidates) == 1:
        return candidates[0]
    return None


def discover_manuals(root: Path) -> list[tuple[str, str, Path]]:
    """Yield (category, manual, manual_dir) for every manual with an MD/ folder."""
    manuals: list[tuple[str, str, Path]] = []
    for category_dir in sorted(root.iterdir()):
        if not category_dir.is_dir():
            continue
        for manual_dir in sorted(category_dir.iterdir()):
            if manual_dir.is_dir() and (manual_dir / "MD").is_dir():
                manuals.append((category_dir.name, manual_dir.name, manual_dir))
    return manuals


def main() -> int:
    p = argparse.ArgumentParser(description="Build ASP manual metas (primary + companions)")
    p.add_argument("--root", required=True, help="references/vendor/asp_manuals root")
    p.add_argument("--profile", required=True, help="asp_manual.yml profile")
    p.add_argument("--meta-dir", help="Override meta output dir")
    p.add_argument("--dry-run", action="store_true")
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
    meta_dir = Path(ns.meta_dir).resolve() if ns.meta_dir else (
        ai_work / "wiki_sources" / "meta" / "asp_manuals")
    meta_dir.mkdir(parents=True, exist_ok=True)

    manuals = discover_manuals(root)
    print(f"found {len(manuals)} manuals with MD/ subfolder")

    total_primary = 0
    total_pdf = 0
    total_docx = 0
    skipped_no_md = 0

    orphans: list[str] = []

    for category, manual, manual_dir in manuals:
        md_dir = manual_dir / "MD"
        pdf_dir = manual_dir / "PDF"
        docx_dir = manual_dir / "Word"
        md_files = sorted(md_dir.glob("*.md"))

        # Primary metas (from MD)
        primary_meta_by_md: dict[Path, Path] = {}
        primary_sid_by_md: dict[Path, str] = {}
        for md_file in md_files:
            stem = md_file.stem
            source_id = build_source_id(category, manual, stem)
            title = f"{manual} — {stem}"
            if ns.dry_run:
                print(f"[primary] {source_id}  ← {md_file}")
                total_primary += 1
                continue
            primary_meta_path = run_primary_builder(
                md_file, source_id, title, profile, meta_dir,
            )
            primary_meta_by_md[md_file] = primary_meta_path
            primary_sid_by_md[md_file] = source_id
            total_primary += 1

        if ns.dry_run:
            continue

        # Companion metas (from PDF + DOCX) — match to MD via find_pair
        for sub, ext, fmt in (
            ("PDF", ".pdf", "pdf"),
            ("Word", ".docx", "docx"),
        ):
            d = manual_dir / sub
            if not d.is_dir():
                continue
            for binary_file in sorted(d.glob(f"*{ext}")):
                paired_md = find_pair(binary_file.stem, md_files)
                if paired_md is None:
                    orphans.append(str(binary_file))
                    continue
                write_companion_meta(
                    out_dir=meta_dir,
                    binary_path=binary_file,
                    primary_meta_path=primary_meta_by_md[paired_md],
                    primary_source_id=primary_sid_by_md[paired_md],
                    category=category,
                    manual=manual,
                    stem=binary_file.stem,
                    fmt=fmt,
                    profile=profile,
                )
                if fmt == "pdf":
                    total_pdf += 1
                else:
                    total_docx += 1

    # Manuals without any MD (pure binary) — reported separately
    for category_dir in sorted(root.iterdir()):
        if not category_dir.is_dir():
            continue
        for manual_dir in sorted(category_dir.iterdir()):
            if manual_dir.is_dir() and not (manual_dir / "MD").is_dir():
                skipped_no_md += 1

    print()
    print(f"primary metas:     {total_primary}")
    print(f"pdf companions:    {total_pdf}")
    print(f"docx companions:   {total_docx}")
    print(f"manuals w/o MD:    {skipped_no_md}  (binary-only; not covered)")
    print(f"orphan binaries:   {len(orphans)}")
    if orphans[:5]:
        for o in orphans[:5]:
            print(f"  - {o}")
        if len(orphans) > 5:
            print(f"  ... ({len(orphans) - 5} more)")
    print(f"output dir:        {meta_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
