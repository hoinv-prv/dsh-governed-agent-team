#!/usr/bin/env python3
"""Build an installable package for AI Work System MVP.

Copies 10 payload sections (methodology, wiki guidelines, skills, tooling,
AIP templates, workspace template, preset knowledge, procedural,
truth templates, guidelines) from a source project rooted at `.ai-work/`
into a versioned output folder,
then generates README, MANIFEST, install_guide, the deprecated CLAUDE_SLIM_TEMPLATE, and
optional CHANGELOG (when --prev points to a previous package).

Python stdlib only. Safe to re-run (refuses to overwrite existing output).

The package version is NOT supplied on the command line — it is read from
`product/aiws_version.md` (single source of truth) so every build produces the
same version regardless of who runs it. To cut a new release, bump that file.

Usage:
    # Official build — version comes from product/aiws_version.md:
    python build_aiws_install_package.py

    # Trial/ephemeral build (quick_install only) — override the pinned version:
    python build_aiws_install_package.py --override-version trial-2026-06-05 \\
        --output /tmp/pkg --no-prev

Exit codes: 0 OK, 2 error.
"""
from __future__ import annotations

import argparse
import ast
import fnmatch
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

from _common import (PAYLOAD_DESIGN_DOCS, PAYLOAD_EXCLUDES, PAYLOAD_MAP, PAYLOAD_SINGLE_FILES,
                     RELEASE_NOTES_NAME, resolve_release_notes,  # noqa: E402  CR-121 r3
                     PAYLOAD_SRC,
                     find_ai_work_root, is_ellipsis_path, parse_frontmatter,
                     read_text, ships,                    # CR-AIWS-2026-08-115 C3
                     today, unfenced_lines, write_text)   # CR-AIWS-2026-08-078 C5


# ---------- Version pin (single source of truth) ----------
# The package version lives in product/aiws_version.md, NOT in a CLI flag, so the
# build is deterministic across people. Bumping the version is a deliberate edit
# to that file — separate from running the build.
VERSION_PIN_REL = "product/aiws_version.md"


def read_pinned_version(project_root: Path) -> tuple[str, str | None]:
    """Read (aiws_version, release_date) from product/aiws_version.md frontmatter.

    release_date is optional (None when absent/blank). Raises SystemExit with a
    clear message if the pin file is missing or has no aiws_version.
    """
    pin = project_root / VERSION_PIN_REL
    if not pin.exists():
        raise SystemExit(
            f"error: version pin file not found: {pin}\n"
            f"       create it with frontmatter:  aiws_version: v1.0"
        )
    meta, _ = parse_frontmatter(read_text(pin))
    version = str(meta.get("aiws_version", "")).strip()
    if not version:
        raise SystemExit(
            f"error: 'aiws_version' is missing or empty in {pin}"
        )
    release_date = str(meta.get("release_date", "")).strip() or None
    return version, release_date


# ---------- Payload section mapping ----------
# All source paths are relative to project root.
# Principle: everything shipped must live under product/ first.

@dataclass
class Section:
    name: str
    src_rel: str
    dst_rel: str
    description: str
    # Path (relative to src_rel) to skip during copy. CR-AIWS-2026-08-102 C2: giá trị KHÔNG còn
    # khai ở đây — nguồn sự thật là `_common.PAYLOAD_EXCLUDES`, cạnh `PAYLOAD_MAP`, vì câu hỏi
    # "path này có ship không?" phải trả lời được từ một module CÓ SHIP chứ không phải từ builder.
    # Hai field giữ nguyên tên (vòng copy union chúng lại) để hợp đồng công khai không đổi.
    exclude_subdirs: frozenset = field(default_factory=frozenset)
    exclude_files: frozenset = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        # Section KHÔNG tự khai exclusion nữa; nạp từ nguồn chung theo `name`.
        object.__setattr__(self, "exclude_subdirs",
                           frozenset(PAYLOAD_EXCLUDES.get(self.name, ())))
        object.__setattr__(self, "exclude_files", frozenset())


PAYLOAD_SECTIONS: list[Section] = [
    Section(
        "methodology",
        "product/methodology/ai_work_system",
        "payload/methodology",
        "AI Work System methodology (specs, guides — no brainstorming/design/delta-tracking)",
    ),
    Section(
        "wiki_guidelines",
        "product/wiki_guidelines",
        "payload/wiki_guidelines",
        "Wiki Guideline Package (core + install + rollout + upgrade)",
    ),
    Section(
        "skills",
        "product/skills",
        "payload/skills",
        "Claude Code user-invocable skills",
    ),
    Section(
        "commands",
        "product/commands",
        "payload/commands",
        "Claude Code slash commands (core command specs were consolidated into domain skills by "
        "CR-AIWS-2026-07-025; carries GENERATED pointer-stubs for the agents-pack verbs — "
        "CR-AIWS-2026-08-019 — written by wire_agent_pack_claude, not copied from a source dir)",
    ),
    Section(
        "tooling",
        "product/tooling",
        "payload/tooling",
        "Python stdlib tooling (no pip install)",
        # dev-only — never ship: quick-install (CR-026) is a maintenance TOOL that lives in
        # tooling but must not reach adopters. The dev regression TESTS + the wiki_corpus fixture
        # were consolidated to .ai-work/tests/ (2026-06-20) — that dir is not a build payload
        # source, so they need no exclude entry here.
    ),
    Section(
        "aip_templates",
        "product/aip_templates",
        "payload/aip_templates",
        "AIP ROOT/PLAN/EXEC/LOCAL templates",
    ),
    Section(
        "workspace_templates",
        "product/workspace_templates",
        "payload/workspace_templates",
        "Task workspace skeleton",
    ),
    Section(
        "preset_knowledge",
        "product/preset_knowledge",
        "payload/preset_knowledge",
        "Preset AIP exec templates, samples, selection guides",
    ),
    Section(
        "procedural",
        "product/procedural",
        "payload/procedural",
        "Playbooks, modes, queue/capture rules, lint policy",
    ),
    Section(
        "truth_templates",
        "product/truth_templates",
        "payload/truth_templates",
        "Starter SOP templates (SOP_MASTER, SOP_DevelopmentTasks) for target project Truth zone",
    ),
    Section(
        "guidelines",
        "product/guidelines",
        "payload/guidelines",
        "Operational guidelines (onboarding, day-to-day usage) for adopters",
    ),
    Section(
        "wiki_source_profiles",
        "product/wiki_source_profiles",
        "payload/wiki_source_profiles",
        "Canonical-tooling wiki source profiles the builders require (java_class, knowledge_object) "
        "+ README; MERGED into the project at install, never overwritten (CR-AIWS-2026-06-047)",
    ),
    Section(
        "agents",
        "product/agents",
        "payload/agents",
        "AI Agents Pack — self-contained package (blueprints, templates, tooling, tools, docs, "
        "router skill + verb commands). Ships whole to .ai-work/agents/; the pack's .claude/ surfaces "
        "(aiws-agent router skill + generated verb pointer-stubs, CR-AIWS-2026-08-019) are wired to "
        ".claude/ by wire_agent_pack_claude (CR-AIWS-2026-06-051); agent lint wired into /aiws-lint by "
        "CR-AIWS-2026-06-049. Optional section: absent product/agents/ → skipped, default build "
        "unchanged (CR-AIWS-2026-06-055).",
        # Desks + dev fixtures/process docs never ship. DEFENSIVE: product/agents/ is already
        # clean, so this guard only ever fires if a desk leaks into the canonical tree.
        # CR-AIWS-2026-08-074 C15/C16 — name BOTH generations. P2 (CR-AIWS-2026-08-006)
        # renamed agents/instances/ -> agents/task_desks/, and C1 of this same CR adds the
        # migrate step that makes the new name the only one. A guard that knows only the
        # pre-P2 name stops guarding at exactly the moment the rename completes — and a
        # guard that has stopped working does not say so. Superset, never a replacement:
        # a tree that has not migrated yet must stay covered.
    ),
    # CR-AIWS-2026-08-018 — default homes for a consuming project's request docs. Two sections, not
    # one: quick_install's PAYLOAD_MAP is dir->dir and these install to DIFFERENT destinations
    # (.ai-work/upstream_requests/ and .ai-work/change_requests/). Ships docs only; the project's own
    # IR/CR files are never touched (copy_section adds, never deletes).
    Section(
        "upstream_requests",
        "product/upstream_requests",
        "payload/upstream_requests",
        "Default home for Improvement Requests a consuming project raises TO the AIWS team: README "
        "(why never to mint a CR-AIWS-* id) + IR_TEMPLATE.md whose frontmatter already conforms to "
        "the upstream intake schema, so promoting an IR upstream is a copy, not a re-normalisation.",
    ),
    Section(
        "project_change_requests",
        "product/project_change_requests",
        "payload/project_change_requests",
        "README for the consuming project's OWN change records (.ai-work/change_requests/) — kept "
        "separate from upstream_requests/ so 'my record' and 'my request to AIWS' cannot be confused "
        "(that confusion is what produced downstream projects minting upstream CR ids).",
    ),
    # CR-AIWS-2026-08-066: the ONE source of rule-file content — core (model-agnostic) + per-tool
    # adapters + the project-identity block. `compose_aiws_rules.py` renders them into CLAUDE.local.md /
    # AGENTS.md / .github/copilot-instructions.md at install time. A `VERSION` manifest is stamped into
    # the payload copy right after this section (stamp_install_templates_version) — build is the ONLY
    # site that stamps it; every other install path just carries it.
    Section(
        "install_templates",
        "product/install_templates",
        "payload/install_templates",
        "Rule-file templates: aiws_core_rules.md (model-agnostic core) + adapter_{claude,agents,"
        "copilot}.md + project_identity.md. Rendered by compose_aiws_rules.py into each tool's rule "
        "file; replaces the former embedded CLAUDE_SLIM_TEMPLATE string.",
    ),
]

# (src_rel, dst_rel). CR-AIWS-2026-07-020: ship rename_map.json into .ai-work/tooling (installs via
# the tooling section destination) so check_aiws_upgrade is rename-aware on adopters, + a copy at
# package root for human reference.
# CR-AIWS-2026-08-105 C3: giá trị sống ở `_common.PAYLOAD_SINGLE_FILES` — cùng chỗ với PAYLOAD_MAP,
# để `ships()` trả lời được "path này có ship không" mà không phải import builder.
EXTRA_SINGLE_FILES: list[tuple[str, str]] = list(PAYLOAD_SINGLE_FILES)


def single_files_for(project_root: Path) -> "list[tuple[str, str]]":
    """`EXTRA_SINGLE_FILES` plus the release note resolved for the pinned version (CR-121 r3).

    Kept out of the module-level constant on purpose: the pair depends on the tree being built, and a
    constant that encodes one version silently ships the wrong one at the next release.
    """
    pairs = list(EXTRA_SINGLE_FILES)
    note = resolve_release_notes(project_root)
    if note:
        pairs.append(note)
        print(f"  release note      : {note[0]} -> {note[1]}")
    else:
        print(f"  release note      : NONE RESOLVED for the pinned version — the package will not "
              f"carry {RELEASE_NOTES_NAME}", file=sys.stderr)
    return pairs


# ---------- Design-doc strip-and-copy ----------
# 10_design/ files contain a mix of operational knowledge (useful for adopters) and
# AIWS-internal design rationale (explains WHY specs are what they are).
# These files are excluded from the main section copy (via exclude_subdirs) but then
# copied here with the internal sections removed.

# Per-file: top-level headings whose entire section should be removed in the package copy.
DESIGN_STRIP_HEADINGS: dict[str, list[str]] = {
    "product/methodology/ai_work_system/10_design/Architecture_Design_MVP.md": [
        "# 2. Why the architecture needs to evolve",
        "# 13. Proposed merged content summary",
        "# 14. Delta status",
    ],
    "product/methodology/ai_work_system/10_design/Basic_Design_MVP.md": [
        "# 2. Why the Basic Design needs to be refactored",
        "# 14. Impact note for canonical Basic Design refactor",
        "# 15. Proposed merged content summary",
        "# 16. Delta status",
    ],
    "product/methodology/ai_work_system/10_design/Methodology_Design_MVP.md": [
        "# 4. Design phase sequence",
        "# 5. Boundary của từng phase",
        "# 17. Deliverables của phase Methodology Design",
        "# 18. Definition of Done cho phase Methodology Design",
    ],
    # Conceptual_Design_MVP.md: no sections to strip — keep fully
}

# Files from 10_design/ to include in the package (stripped). Detail_Design is omitted.
# CR-AIWS-2026-08-105 C3: giá trị sống ở `_common.PAYLOAD_DESIGN_DOCS`. Detail_Design vẫn bị bỏ —
# danh sách bên đó là nơi duy nhất quyết định file nào của 10_design/ được copy lại.
DESIGN_DOCS_STRIP_COPY: list[str] = list(PAYLOAD_DESIGN_DOCS)


def strip_design_sections(content: str, headings_to_remove: list[str]) -> str:
    """Remove markdown sections (and their subsections) matching the given headings.

    Removes the preceding horizontal rule separator as well so the document
    stays clean. Works for any heading depth — stops skipping when a heading
    of equal or lesser depth is encountered.
    """
    if not headings_to_remove:
        return content
    lines = content.split("\n")
    result: list[str] = []
    i = 0
    while i < len(lines):
        heading = lines[i].rstrip()
        if heading in headings_to_remove:
            level = len(heading) - len(heading.lstrip("#"))
            # Drop the preceding blank lines + '---' separator
            while result and result[-1].strip() == "":
                result.pop()
            if result and result[-1].strip() == "---":
                result.pop()
            while result and result[-1].strip() == "":
                result.pop()
            # Skip this section until a heading of equal or lesser depth
            i += 1
            while i < len(lines):
                nxt = lines[i].rstrip()
                if nxt.startswith("#"):
                    curr_level = len(nxt) - len(nxt.lstrip("#"))
                    if curr_level <= level:
                        break  # hand off to outer loop without incrementing
                i += 1
        else:
            result.append(lines[i])
            i += 1
    text = "\n".join(result)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.rstrip() + "\n"


# ---------- AIWS wiki bundle (CR-AIWS-2026-06-040) ----------
# Ship the curated AIWS source metas (methodology + wiki_guidelines + preset_knowledge),
# path-rebased for the target install layout, as a dedicated `aiws` namespace. The metas
# live in .ai-work/wiki_sources/meta/ (a projection of the product docs), not under product/,
# so they are generated into the package at BUILD time (like the design-doc strip-copy), then
# the index (index.aiws.jsonl) is rebuilt from them at INSTALL time. Only artifact_locator is
# rewritten; meta_locator is not carried (the index is rebuilt locally). See CR-040.

AIWS_WIKI_META_GROUPS = ["methodology", "wiki_guidelines", "preset_knowledge"]

# Rebase: dev-repo meta artifact_locator (project-root-relative) -> target install locator.
# Ordered longest-prefix-first; mirrors PAYLOAD_SECTIONS + the install_guide payload mapping.
AIWS_WIKI_REBASE: list[tuple[str, str]] = [
    ("product/methodology/ai_work_system/", ".ai-work/truth/canonical/methodology/"),
    ("product/wiki_guidelines/", ".ai-work/truth/canonical/wiki_guidelines/"),
    ("product/preset_knowledge/", ".ai-work/preset_knowledge/"),
]


def _aiws_meta_source_shipped(locator: str) -> bool:
    """A meta is shippable only if its source artifact is actually shipped.

    The methodology payload section excludes 00_brainstorming/10_design/90_delta_tracking
    (10_design's 4 design docs are re-added stripped; Detail_Design is omitted). A shipped
    index must never point at a missing file.
    """
    if "/00_brainstorming/" in locator or "/90_delta_tracking/" in locator:
        return False
    if locator.endswith("10_design/Detail_Design_MVP_Core_Artifacts.md"):
        return False
    return True


def _aiws_rebase_locator(locator: str) -> str | None:
    """Rewrite a dev-repo artifact_locator to its target install locator, or None if it
    falls outside the three shipped groups (caller skips)."""
    for old, new in AIWS_WIKI_REBASE:
        if locator.startswith(old):
            return new + locator[len(old):]
    return None


def build_aiws_wiki_bundle(project_root: Path, output: Path,
                           file_section_map: dict[str, str]) -> int:
    """Ship the curated AIWS metas into payload/aiws_wiki/ (CR-040).

    PREFERRED source: the curated metas under `.ai-work/wiki_sources/aiws_meta/{group}/`.
    Two locator layouts are supported (CR-AIWS-2026-08-052 C7):
      - `artifact_locator: product/**` (single-index SoT repo — the current AIWS dev repo):
        the locator is REBASED product/ -> target install layout via AIWS_WIKI_REBASE at ship
        time (the original CR-040 design, now live again), and the source-shipped filter applies.
      - `artifact_locator: .ai-work/**` (legacy install-layout metas): shipped VERBATIM as before.

    FALLBACK (legacy CR-040 path, used only when `aiws_meta/` is absent): rebase the dev
    metas under `.ai-work/wiki_sources/meta/{group}/` from their product/ artifact_locator,
    dropping metas whose source isn't shipped. Returns files written.
    """
    prebuilt = project_root / ".ai-work" / "wiki_sources" / "aiws_meta"
    if prebuilt.is_dir():
        written = 0
        skipped = 0
        for group in AIWS_WIKI_META_GROUPS:
            gdir = prebuilt / group
            if not gdir.is_dir():
                print(f"  ! aiws_wiki: meta group missing ({gdir})")
                continue
            for meta in sorted(gdir.rglob("*.md")):
                # CR-AIWS-2026-08-075 C5 — a pending refresh draft is NOT a meta. Every other
                # meta-scanning tool skips it (build_relations.py:274/285,
                # build_wiki_source_index.py:232/287, …); this builder was the only one that
                # did not, so a draft left in the tree could be packaged and shipped to every
                # install as if it were a real meta.
                if meta.name.endswith(".refresh.md"):
                    continue
                raw = meta.read_text(encoding="utf-8", errors="replace")
                fm, _ = parse_frontmatter(raw)
                loc = str(fm.get("artifact_locator", "")).strip()
                if loc.startswith("product/"):
                    # CR-AIWS-2026-08-052 C7 — single-index repo: rebase-on-ship.
                    if not _aiws_meta_source_shipped(loc):
                        skipped += 1
                        continue
                    new_loc = _aiws_rebase_locator(loc)
                    if new_loc is None:
                        skipped += 1
                        continue
                    raw = raw.replace(f"artifact_locator: {loc}", f"artifact_locator: {new_loc}", 1)
                rel = meta.relative_to(prebuilt)
                dst = output / "payload" / "aiws_wiki" / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                write_text(dst, raw)
                file_section_map[dst.relative_to(output).as_posix()] = "aiws_wiki"
                written += 1
        print(f"  [aiws_wiki            ] {written} metas (from aiws_meta/; product-locators rebased "
              f"to target layout, legacy target-layout metas verbatim; skipped {skipped})")
        return written

    src_root = project_root / ".ai-work" / "wiki_sources" / "meta"
    written = 0
    skipped = 0
    for group in AIWS_WIKI_META_GROUPS:
        gdir = src_root / group
        if not gdir.is_dir():
            print(f"  ! aiws_wiki: meta group missing ({gdir})")
            continue
        for meta in sorted(gdir.rglob("*.md")):
            # CR-AIWS-2026-08-075 C5 — a pending refresh draft is NOT a meta. Every other
            # meta-scanning tool skips it (build_relations.py:274/285,
            # build_wiki_source_index.py:232/287, …); this builder was the only one that
            # did not, so a draft left in the tree could be packaged and shipped to every
            # install as if it were a real meta.
            if meta.name.endswith(".refresh.md"):
                continue
            raw = meta.read_text(encoding="utf-8", errors="replace")
            fm, _ = parse_frontmatter(raw)
            loc = str(fm.get("artifact_locator", "")).strip()
            if not loc or not _aiws_meta_source_shipped(loc):
                skipped += 1
                continue
            new_loc = _aiws_rebase_locator(loc)
            if new_loc is None:
                skipped += 1
                continue
            rebased = raw.replace(loc, new_loc)  # rewrites frontmatter + ## Artifact Reference body line
            rel = meta.relative_to(src_root)
            dst = output / "payload" / "aiws_wiki" / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            write_text(dst, rebased)
            file_section_map[dst.relative_to(output).as_posix()] = "aiws_wiki"
            written += 1
    print(f"  [aiws_wiki            ] {written} metas (rebased; {skipped} skipped — source not shipped)")
    return written


def build_aiws_wiki_index_bundle(output: Path, file_section_map: dict[str, str]) -> int:
    """CR-AIWS-2026-08-064 C5 — pre-build `payload/aiws_wiki_index/{index.aiws.jsonl,
    relations.aiws.jsonl}` from `payload/aiws_wiki/` via build_preset_wiki.py (--payload mode:
    staging tree = target layout, portable meta_locator). Generated section (no product/ mirror —
    check_dual_tree SKIP_SECTIONS). A failing pre-build FAILS the package build: never ship a
    package whose preset is silently missing. Returns files written (0 when no bundle)."""
    payload = output / "payload" / "aiws_wiki"
    if not payload.is_dir() or not any(payload.rglob("*.md")):
        print("  [aiws_wiki_index      ] skipped (no payload/aiws_wiki metas)")
        return 0
    out_dir = output / "payload" / "aiws_wiki_index"
    tool = Path(__file__).resolve().parent / "build_preset_wiki.py"
    proc = subprocess.run(
        [sys.executable, str(tool), "--payload", str(payload), "--out-dir", str(out_dir)],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        print(proc.stdout, end="")
        print(proc.stderr, end="", file=sys.stderr)
        raise SystemExit(f"error: preset wiki pre-build failed rc={proc.returncode} "
                         f"(build_preset_wiki.py --payload) — package NOT built")
    written = 0
    for name in ("index.aiws.jsonl", "relations.aiws.jsonl"):
        f = out_dir / name
        if not f.exists():
            raise SystemExit(f"error: preset pre-build produced no {name} — package NOT built")
        file_section_map[f.relative_to(output).as_posix()] = "aiws_wiki_index"
        written += 1
    n_idx = sum(1 for ln in (out_dir / "index.aiws.jsonl").read_text(encoding="utf-8").splitlines() if ln.strip())
    n_rel = sum(1 for ln in (out_dir / "relations.aiws.jsonl").read_text(encoding="utf-8").splitlines() if ln.strip())
    print(f"  [aiws_wiki_index      ] pre-built index.aiws.jsonl ({n_idx} entries) + relations.aiws.jsonl ({n_rel} edges)")
    return written


# ---------- Exclusions ----------

EXCLUDE_DIR_NAMES = {
    "__pycache__", ".DS_Store", ".pytest_cache", ".mypy_cache",
    "node_modules", ".git",
}

EXCLUDE_GLOB_PATTERNS = [
    "*.pyc", "*.pyo", "*.bak-*", "*.preview",
    "*.local.md", ".DS_Store",
]


def is_excluded(path: Path) -> bool:
    name = path.name
    if name in EXCLUDE_DIR_NAMES:
        return True
    for pat in EXCLUDE_GLOB_PATTERNS:
        if fnmatch.fnmatch(name, pat):
            return True
    return False


# ---------- Copy helper ----------

def copy_tree_filtered(
    src: Path, dst: Path, exclude_abs: frozenset | None = None
) -> tuple[int, int]:
    """Recursively copy src → dst skipping excluded names/paths. Returns (files, dirs)."""
    files_copied = 0
    dirs_created = 0
    if not src.exists():
        raise SystemExit(f"error: source not found: {src}")
    if src.is_file():
        if is_excluded(src):
            return (0, 0)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        return (1, 0)
    dst.mkdir(parents=True, exist_ok=True)
    dirs_created += 1
    for child in sorted(src.iterdir()):
        if is_excluded(child):
            continue
        if exclude_abs and child in exclude_abs:
            continue
        sub_dst = dst / child.name
        if child.is_dir():
            f, d = copy_tree_filtered(child, sub_dst, exclude_abs)
            files_copied += f
            dirs_created += d
        else:
            shutil.copy2(child, sub_dst)
            files_copied += 1
    return (files_copied, dirs_created)


# ---------- AI Agents Pack .claude wiring (CR-AIWS-2026-06-051) ----------

def wire_agent_pack_claude(project_root: Path, output: Path,
                           file_section_map: dict[str, str]) -> int:
    """Wire the AI Agents Pack's `.claude/` surfaces (CR-AIWS-2026-06-051).

    The agents package (product/agents/) ships whole to .ai-work/agents/ via the `agents`
    PAYLOAD_SECTION, but its .claude surfaces must ALSO reach the target's `.claude/`: the
    aiws-agent router skill is COPIED into payload/skills/, and one pointer-stub per verb spec is
    GENERATED into payload/commands/ (CR-AIWS-2026-08-019) so the standard payload→.claude wiring
    carries both — nothing hand-copied, nothing to miss. A smoke-check fails the build if the
    router is unwired, a verb has no stub, or a stub carries more than pointer content.

    No-op (returns 0) when product/agents/ is absent — default build unchanged.
    """
    pack = project_root / "product" / "agents"
    if not pack.is_dir():
        return 0
    written = 0
    # CR-AIWS-2026-07-031 T3 (DP-031-1 = A): verb-command BYTE-COPIES are NOT wired into
    # payload/commands/ — shipping them re-installed stale shims the repo itself had deleted
    # (demo drift ×3). CR-AIWS-2026-08-019 restores the .claude/commands surface as generated
    # POINTER-STUBS instead: a stub carries NO spec content (constant template + basename), so it
    # cannot go stale; authoritative verb specs stay pack-internal (payload/agents/commands/
    # → target .ai-work/agents/commands/). NL entry point stays the aiws-agent ROUTER SKILL below;
    # stubs add the explicit-invocation path (/aiws-agent-<verb> in the slash menu).
    # router skill(s) → payload/skills/ (→ target .claude/skills/)
    sk_src = pack / "skills"
    if sk_src.is_dir():
        sk_dst = output / "payload" / "skills"
        for skill_dir in sorted(sk_src.iterdir()):
            if skill_dir.is_dir() and not is_excluded(skill_dir):
                f, _ = copy_tree_filtered(skill_dir, sk_dst / skill_dir.name)
                written += f
                for fp in walk_files(sk_dst / skill_dir.name):
                    file_section_map[fp.relative_to(output).as_posix()] = "skills"
    # verb pointer-stubs → payload/commands/ (→ target .claude/commands/), CR-AIWS-2026-08-019.
    # Generated from the OUTPUT tree's pack commands (respects section excludes). The dash in the
    # `aiws-agent-*.md` glob excludes the router spec aiws-agent.md by construction — a router stub
    # would name-collide with the /aiws-agent skill wired above.
    stub_marker = "pointer stub (generated at build"
    stub_template = (
        "# /{stem} — pointer stub (generated at build — do not edit; CR-AIWS-2026-08-019)\n"
        "\n"
        "Read and follow the authoritative verb spec: `.ai-work/agents/commands/{name}`.\n"
        "Every gate in that spec (HUMAN confirm, aip_driven, no-auto-promotion, …) applies unchanged.\n"
        "NL alternative: the `/aiws-agent` router skill.\n"
    )
    pack_cmds_out = output / "payload" / "agents" / "commands"
    cmd_dst = output / "payload" / "commands"
    if pack_cmds_out.is_dir():
        for spec in sorted(pack_cmds_out.glob("aiws-agent-*.md")):
            cmd_dst.mkdir(parents=True, exist_ok=True)
            stub = cmd_dst / spec.name
            # CR-AIWS-2026-08-072 C2 — spec metadata first, then the pointer body. Frontmatter is
            # LIFTED from the spec (single source); absent/incomplete ⇒ the build fails above.
            write_text(stub, lift_command_frontmatter(spec)
                       + "\n" + stub_template.format(stem=spec.stem, name=spec.name))
            file_section_map[stub.relative_to(output).as_posix()] = "commands"
            written += 1
    # smoke-check (CR-AIWS-2026-08-019, supersedes the CR-031-T3 no-byte-copy assert): router skill
    # must land; payload/commands may carry ONLY pointer-stubs, 1-1 with the pack's verb specs
    # (no orphan, no missing, no router stub); a stub must stay pointer-only — spec-content
    # byte-copies remain forbidden (CR-031 T3 failure mode).
    router_ok = (output / "payload" / "skills" / "aiws-agent" / "SKILL.md").exists()
    if not router_ok:
        raise SystemExit("error: agent-pack wiring smoke-check failed — router skill aiws-agent not wired")
    expected = sorted(p.name for p in pack_cmds_out.glob("aiws-agent-*.md")) if pack_cmds_out.is_dir() else []
    present = sorted(p.name for p in cmd_dst.glob("aiws-agent*.md")) if cmd_dst.is_dir() else []
    if present != expected:
        raise SystemExit(
            f"error: agent-pack wiring smoke-check failed — stub set mismatch in payload/commands/ "
            f"(orphan/missing/router stub forbidden, CR-2026-08-019): present={present} expected={expected}")
    for name in present:
        stub_text = (cmd_dst / name).read_text(encoding="utf-8")
        # CR-AIWS-2026-08-072 C2 — the marker is now the first line of the BODY, after the lifted
        # frontmatter. Skip the frontmatter block before checking, and keep the pointer-only bound
        # on the body alone so the cap still measures what it was written to measure.
        body = stub_text
        if body.startswith("---\n"):
            _e = body.find("\n---\n", len("---\n") - 1)
            if _e < 0:
                raise SystemExit(
                    f"error: generated stub has unclosed frontmatter: {name} (CR-AIWS-2026-08-072)")
            body = body[_e + len("\n---\n"):]
        stub_lines = body.lstrip("\n").splitlines()
        if not stub_lines or stub_marker not in stub_lines[0] or len(stub_lines) > 10:
            raise SystemExit(
                f"error: agent-pack wiring smoke-check failed — {name} is not a pointer-stub "
                f"(marker on line 1 + <=10 lines; spec-content byte-copies forbidden, CR-031 T3)")
    print(f"  [agent-pack wiring     ] {written} files → .claude (router skill + {len(present)} verb "
          f"pointer-stubs; specs stay pack-internal per CR-025/CR-031-T3/CR-2026-08-019)")
    return written


# ---------- CR-AIWS-2026-08-071: payload-scope validation ----------
# WHY THIS RUNS ON THE PAYLOAD, NOT ON THE SOURCE TREE.
# lint_agents' pack_md_link_broken (C2) and dead_path_ref (C3) resolve paths against the tree they
# run on. In THIS repo `product/` and `docs/agent_pack_impl_package/` exist, so a ref into them is
# valid here and dead on every install — the defect class is invisible to any gate that runs
# upstream (IR-2026-08-15 F1/F2; AIP-EXEC-1063 FND-01). The only place it IS visible is the built
# payload. Hence: validate here, once the payload tree is complete.

_PAYLOAD_LINK_RE = re.compile(r"\]\(([^)#\s]+\.md)(?:#[^)]*)?\)")
_PAYLOAD_INREPO_RE = re.compile(r"(?:development|product)/[A-Za-z0-9_.\-/]+")
_PAYLOAD_REF_ALLOWLIST = ("source:", "precedent", "provenance", "changelog", "formerly",
                          "retired", "deleted", "lịch sử", "đã xóa", "da xoa",
                          "repo nguồn", "impl package", "canonical:")


def lift_command_frontmatter(spec: Path) -> str:
    """CR-AIWS-2026-08-072 C2 — return the verb spec's YAML frontmatter block, verbatim.

    A pointer stub carries no spec CONTENT (that is the CR-08-019 invariant that keeps it from going
    stale), but it must carry the spec's command METADATA, or the slash menu shows a stub whose
    `description` is a sentence about the build mechanism instead of what the command does — the UX
    regression CR-08-019 introduced.

    The spec is the SINGLE source: this lifts, it never composes. A table of descriptions living in
    the generator would be a second source that drifts from the specs it describes.

    Missing or malformed frontmatter FAILS THE BUILD rather than emitting a mute stub — a stub with
    no description looks identical to a stub whose description was never written, and the package
    would ship it silently.
    """
    raw = spec.read_text(encoding="utf-8").replace("\r\n", "\n")
    if not raw.startswith("---\n"):
        raise SystemExit(
            f"error: verb spec has no frontmatter — cannot build its pointer stub: {spec.name}\n"
            f"  Add `description`, `argument-hint`, `allowed-tools` at the top of the spec "
            f"(CR-AIWS-2026-08-072 C1/C2). The spec is the only source of command metadata.")
    end = raw.find("\n---\n", len("---\n") - 1)
    if end < 0:
        raise SystemExit(
            f"error: verb spec frontmatter is not closed by a `---` line: {spec.name} "
            f"(CR-AIWS-2026-08-072 C2)")
    block = raw[: end + len("\n---\n")]
    missing = [k for k in ("description:", "argument-hint:", "allowed-tools:") if k not in block]
    if missing:
        raise SystemExit(
            f"error: verb spec frontmatter is missing {missing}: {spec.name} "
            f"(CR-AIWS-2026-08-072 C1). A stub without a description shows the build marker in the "
            f"slash menu — exactly the regression this CR removes.")
    return block


def _payload_gitignore_star_dirs(payload: Path) -> "list[Path]":
    """Directories a SHIPPED .gitignore blanks out with `*` (F13)."""
    hidden = []
    for gi in sorted(payload.rglob(".gitignore")):
        pats = [ln.strip() for ln in gi.read_text(encoding="utf-8").splitlines()
                if ln.strip() and not ln.strip().startswith("#")]
        if "*" in pats:
            hidden.append(gi.parent)
    return hidden


def _install_layout(output: Path) -> "tuple[dict[Path, str], set[str]]":
    """Map every payload file to WHERE IT LANDS ON AN INSTALL, plus the set of installed paths.

    CR-AIWS-2026-08-071 r5 (AIP-EXEC-1067). The first cut of C1 asked "does this link resolve
    inside payload/?" — the wrong question. `payload/` is a STAGING tree whose shape differs from
    the installed tree, and the links inside shipped documents are authored for the INSTALL layout.
    Measured consequence: 12 skill shims (`.claude/skills/X/SKILL.md` ->
    `../../../.ai-work/procedural/skills/X/SKILL.md`) were reported broken while resolving
    perfectly on a real install — "fixing" them would have broken working files.

    The payload -> install mapping is owned by _common.PAYLOAD_MAP (dir -> dir); it is
    imported, never copied, so this gate cannot drift from the installer.
    """
    from _common import PAYLOAD_MAP, TRUTH_STUBS  # single source of the mapping (IR-2026-08-17 F1)

    payload = output / "payload"
    mapping = dict(PAYLOAD_MAP)
    placed: "dict[Path, str]" = {}
    for f in payload.rglob("*"):
        if not f.is_file():
            continue
        rel = f.relative_to(payload).as_posix()
        key = rel.split("/", 1)[0]
        if key not in mapping or "/" not in rel:
            continue  # section we do not know how to place (or a loose top-level file)
        placed[f] = mapping[key] + "/" + rel.split("/", 1)[1]

    installed = set(placed.values())
    installed.update(TRUTH_STUBS)          # written by the installer, not shipped
    # Directory prefixes count as existing targets for link purposes.
    for p in list(installed):
        parts = p.split("/")
        for i in range(1, len(parts)):
            installed.add("/".join(parts[:i]))
    return placed, installed


# CR-AIWS-2026-08-071 r7 — ROOT-ANCHORED TARGETS ARE READ FROM THE PROJECT ROOT.
# A link written ".ai-work/…" or ".claude/…" is a repo-root path, not a path relative to the file
# that carries it (that form is the existing repo convention — see CR-AIWS-2026-07-029 §3.1).
#
# HISTORY, so nobody re-adds it: r5 also carried a rule REQUIRING climbing links into a fixed root
# to be rewritten root-anchored. Investigating CR-029 showed that would flag 12 skill shims which
# resolve correctly and are governed by C4 — i.e. it enforced a convention this repo does not hold.
# Removed at r7. The off-by-one class it targeted is caught by `installed_link_broken` instead,
# which asks the only question that matters: does this resolve on an install?
_FIXED_ROOTS = (".ai-work/", ".claude/", "product/", "docs/")


def _normalize_path(parts: "list[str]") -> "str | None":
    out: "list[str]" = []
    for seg in parts:
        if seg in ("", "."):
            continue
        if seg == "..":
            if not out:
                return None       # climbed above the project root
            out.pop()
        else:
            out.append(seg)
    return "/".join(out)


def _resolve_installed(installed_file: str, target: str) -> "str | None":
    """Resolve `target` as the INSTALLED tree sees it.

    Root-anchored targets (".ai-work/…", ".claude/…") are read from the project root; everything
    else is relative to the installed location of the file that carries the link."""
    if target.startswith(_FIXED_ROOTS):
        return _normalize_path(target.split("/"))
    base = installed_file.rsplit("/", 1)[0] if "/" in installed_file else ""
    return _normalize_path((base.split("/") if base else []) + target.split("/"))


def _first_docstring_line(py: Path) -> str:
    """Dòng đầu docstring module, hoặc `(chưa có docstring)` — KHÔNG bao giờ trả rỗng.

    Một tool không có docstring vẫn phải có dòng riêng trong index (ca (d) của CR-AIWS-2026-08-115):
    im lặng bỏ qua nó là đúng hình dạng "tập duyệt rỗng" mà Rule 13 cấm.
    """
    try:
        mod = ast.parse(py.read_text(encoding="utf-8", errors="replace"))
        doc = ast.get_docstring(mod) or ""
    except Exception:  # noqa: BLE001
        doc = ""
    first = doc.strip().splitlines()[0].strip() if doc.strip() else ""
    if not first:
        return "(chưa có docstring)"
    # docstring hay mở bằng "ten_file.py — mo ta"; bỏ phần lặp lại tên cho bảng đỡ ồn
    for sep in (" — ", " - ", ": "):
        if first.startswith(py.name + sep):
            first = first[len(py.name) + len(sep):]
            break
    return first.replace("|", "\\|")


def write_tools_index(output: Path) -> int:
    """C2 (CR-AIWS-2026-08-115) — một dòng cho MỖI tool ship, sinh lúc build.

    Vì sao sinh chứ không curate tay (DP-115-A (a)): `payload/tooling/README.md` là bảng curate theo
    nhóm, và nó đã TRÔI — đo 2026-08-19 trên cut trial: nó nhắc tên 21/51 tool, tức 30 tool ship mà
    không dòng nào trong bản cài của adopter nói chúng tồn tại. Một bảng sinh tự động không trôi được.

    README **không** bị thay thế: nó vẫn là chỗ curate "tool nào dùng khi nào"; index này trả lời câu
    hẹp hơn — "package này có những tool gì".
    """
    tdir = output / "payload" / "tooling"
    if not tdir.is_dir():
        return 0
    tools = sorted(p for p in tdir.glob("*.py"))
    rows = ["# Tools shipped in this package",
            "",
            "> Sinh tự động lúc build (CR-AIWS-2026-08-115 C2) — **đừng sửa tay**, mọi sửa đổi sẽ mất ở",
            "> lần build sau. Mô tả lấy từ dòng đầu docstring của chính tool. Xem `README.md` cùng thư",
            "> mục để biết *dùng tool nào khi nào* — file này chỉ trả lời *package có tool gì*.",
            "",
            "| Tool | Purpose (dòng đầu docstring) |",
            "|---|---|"]
    for p in tools:
        rows.append(f"| `{p.name}` | {_first_docstring_line(p)} |")
    rows += ["", f"**Tổng: {len(tools)} tool.**", ""]
    write_text(tdir / "TOOLS_INDEX.md", "\n".join(rows))

    readme = tdir / "README.md"
    if readme.is_file():
        txt = readme.read_text(encoding="utf-8", errors="replace")
        marker = "TOOLS_INDEX.md"
        if marker not in txt:
            lines = txt.split("\n")
            i = 1 if lines and lines[0].startswith("#") else 0
            note = ("", "> **Danh sách ĐẦY ĐỦ mọi tool trong package: [`TOOLS_INDEX.md`](TOOLS_INDEX.md)** "
                    "(sinh tự động lúc build).", "> Bảng dưới đây là bản *curate* theo nhóm việc — nó "
                    "không hứa liệt kê hết.", "")
            # CR-059: dùng writer dùng chung (LF-stable), KHÔNG `Path.write_text` trần —
            # thiếu `newline=` là cỗ máy sinh EOL churn đã trả giá 4 lần (CAP-1008-02).
            write_text(readme, "\n".join(lines[:i + 1] + list(note) + lines[i + 1:]))
    return len(tools)


#: C4 của CR-AIWS-2026-08-115 (miễn trừ `payload_source_tree_ref` theo TÀI LIỆU thay vì theo DÒNG)
#: đã được HIỆN THỰC rồi GỠ ngay trong lượt apply, theo ruling HUMAN 2026-08-19. Lý do là số đo, ghi
#: lại ở đây để không ai hiện thực lại nó mà không biết cái giá:
#:
#:   phương án                     | doc được miễn | tree_ref | anchor | tổng
#:   không có C4 (hiện tại)        |       0       |    28    |   88   | 116
#:   thu hẹp còn 7 từ khoá lịch sử |      19       |    21    |   74   |  95
#:   C4 như CR duyệt (13 từ khoá)  |      58       |    19    |   70   |  89
#:
#: C4 sinh ra để tắt **3** cảnh báo `development/` trong **2** tài liệu đã tự khai là HISTORICAL.
#: Nhưng miễn trừ theo tài liệu là miễn CẢ FILE, và tập từ khoá của `_PAYLOAD_REF_ALLOWLIST` chứa
#: `source:` — một header provenance bình thường, một mình nó miễn 30 tài liệu. Kết quả: mua 3, mất
#: 27. Đúng rủi ro mà §7 của chính CR đã nêu; số đo tại apply xác nhận nó xảy ra thật.
#:
#: Muốn làm lại: cần một cơ chế gắn miễn trừ với ĐÚNG cây mà banner nói tới (banner khai
#: `development/` thì chỉ miễn token `development/`), chứ không phải miễn cả tài liệu — và đó là một
#: CR khác, có phép đo riêng.


def _installed_path_for_source(tok: str) -> "str | None":
    """`product/…` → path SAU KHI CÀI, hoặc None nếu token thật sự không ship (C3).

    Cách tính (CR-AIWS-2026-08-115 §Ghi chú cho người apply): tra `PAYLOAD_MAP`, tìm entry có `src`
    là tiền tố của token, thay tiền tố đó bằng `dest`. Khớp NHIỀU entry ⇒ lấy `src` **dài nhất**
    (khớp cụ thể nhất). Vẫn hoà ⇒ **không đoán**: trả None và để token rơi về mã cũ.
    """
    if not ships(tok):
        return None
    q = tok.replace("\\", "/").rstrip("/")
    # Đường ship KHÔNG-qua-section phải xét TRƯỚC (cùng lý do như `ships()` — CR-AIWS-2026-08-105 C2):
    # `product/rename_map.json` ship qua PAYLOAD_SINGLE_FILES chứ không qua bất kỳ section nào, và
    # riêng nó chiếm 28/116 hit. Bỏ qua nhánh này là để 28 token CÓ ship rơi về mã cũ.
    singles = [d for src, d in PAYLOAD_SINGLE_FILES if src == q and d.startswith("payload/")]
    if len(singles) == 1:
        return singles[0][len("payload/"):]
    if len(singles) > 1:
        return None          # nhiều đích trong payload: không đoán
    best = []
    for name, src in PAYLOAD_SRC.items():
        if q == src or q.startswith(src + "/"):
            best.append((len(src), name, src))
    if not best:
        return None
    best.sort(reverse=True)
    if len(best) > 1 and best[0][0] == best[1][0]:
        return None          # hoà: không đoán
    _, name, src = best[0]
    # PAYLOAD_MAP là LIST of (name, installed_dest) — không phải dict; `dest` đã là path SAU KHI CÀI.
    dest = next((d for n, d in PAYLOAD_MAP if n == name), "")
    if not dest:
        return None
    rest = q[len(src):].lstrip("/")
    return f"{dest}/{rest}" if rest else dest


def validate_payload_scope(output: Path) -> None:
    """C1/C2/C10 — the payload must be self-contained.

    C1  (ERROR): every relative markdown link to a .md resolves INSIDE payload/.
    C2  (WARN) : `product/…` / `development/…` are source-repo-only trees that never ship.
    C10 (ERROR): no shipped meta may point at an artifact that a SHIPPED .gitignore hides from
                 every clean checkout (F13: the index advertised 3 artifacts no clone ever had).
    """
    payload = output / "payload"
    if not payload.is_dir():
        return
    errors: "list[str]" = []
    warnings: "list[str]" = []

    placed, installed = _install_layout(output)
    md_files = sorted(payload.rglob("*.md"))
    for f in md_files:
        rel_f = f.relative_to(output).as_posix()
        try:
            lines = f.read_text(encoding="utf-8").splitlines()
        except Exception:
            continue
        here = placed.get(f)
        for i, line in unfenced_lines(lines):
            for m in _PAYLOAD_LINK_RE.finditer(line):
                target = m.group(1)
                if target.startswith(("http://", "https://", "/")):
                    continue
                # CR-AIWS-2026-08-078 C5 (iii): `core/.../SPEC.md` is an ABBREVIATION, not a path.
                # It can never resolve and was never meant to.
                if is_ellipsis_path(target):
                    continue
                if here is None:
                    continue  # unmapped section: cannot judge, do not guess
                # install_templates/*.md are RULE TEMPLATES: their body is composed into a file
                # that lives at the PROJECT ROOT (CLAUDE.md / AGENTS.md / copilot-instructions.md,
                # CR-AIWS-2026-08-066). Their paths are therefore root-relative by design, and
                # resolving them from .ai-work/install_templates/ would be wrong.
                base = "" if here.startswith(".ai-work/install_templates/") else here
                dest = _resolve_installed(base if base else "x.md", target)
                if dest is None:
                    errors.append(
                        "installed_link_escapes_project: {}:{} link '{}' climbs above the project "
                        "root once installed at '{}' (CR-AIWS-2026-08-071 C1)".format(
                            rel_f, i, target, here))
                elif dest not in installed:
                    errors.append(
                        "installed_link_broken: {}:{} link '{}' resolves to '{}' on an install, "
                        "which nothing ships or creates (CR-AIWS-2026-08-071 C1)".format(
                            rel_f, i, target, dest))
            if any(k in line.lower() for k in _PAYLOAD_REF_ALLOWLIST):
                continue
            # Same exemption as lint_agents dead_path_ref (CR-AIWS-2026-08-071 C4): a line naming
            # BOTH the canonical tree and the installed tree is EXPLAINING the anchor mapping, not
            # pointing at one. Rewriting it to a single anchor would delete the information.
            _toks = [x.group(0) for x in _PAYLOAD_INREPO_RE.finditer(line)]
            if _toks and ".ai-work/" in line:
                continue
            for m in _PAYLOAD_INREPO_RE.finditer(line):
                tok = m.group(0).rstrip(".,;:)]}\"'`")
                # '//' shorthand lists ("product//truth//wiki") are prose, not path tokens —
                # mirrors the same guard in lint_agents.
                if any(ch in tok for ch in "<>*{}$") or "//" in tok:
                    continue
                # C3 (CR-AIWS-2026-08-115): hỏi `ships()` TRƯỚC khi phát biểu. Đo trên cut
                # trial-2026-08-19: 88/116 (76%) token thuộc nội dung CÓ ship — với chúng, câu
                # "not shipped" đơn giản là SAI, và nó dẫn người đọc đi xoá tham chiếu trong khi
                # việc cần làm là đổi anchor. Hai nhóm ⇒ hai mã, vì hai HÀNH ĐỘNG khác nhau.
                dest = _installed_path_for_source(tok)
                if dest is not None:
                    warnings.append(
                        "payload_source_anchor: {}:{} references '{}' — nội dung này CÓ ship; đây là "
                        "anchor NGUỒN. Dùng path đã cài: '{}' (CR-AIWS-2026-08-115 C3)".format(
                            rel_f, i, tok, dest))
                    continue
                warnings.append(
                    "payload_source_tree_ref: {}:{} references source-only tree '{}' (not shipped; "
                    "use the .ai-work/ path, or pair both anchors, or mark the line as provenance) "
                    "(CR-AIWS-2026-08-071 C2)".format(rel_f, i, tok))

    for hidden_dir in _payload_gitignore_star_dirs(payload):
        marker = hidden_dir.name
        for meta in sorted(payload.rglob("*.md")):
            if "aiws_wiki" not in meta.as_posix():
                continue
            for ln in meta.read_text(encoding="utf-8").splitlines():
                if not ln.startswith("artifact_locator:"):
                    continue
                loc = ln.split(":", 1)[1].strip()
                if marker in loc:
                    errors.append(
                        "payload_meta_artifact_gitignored: {} points at '{}', which the shipped "
                        "{} ('*') hides from every clean checkout "
                        "(CR-AIWS-2026-08-071 C10)".format(
                            meta.relative_to(output).as_posix(), loc,
                            (hidden_dir / ".gitignore").relative_to(output).as_posix()))

    for w in warnings:
        print("  [payload-scope WARN    ] " + w)
    if errors:
        # Report a BREAKDOWN BY KIND first, then samples. A flat truncated list hides which
        # failure classes are present: while building this gate the truncation made C10 look
        # like it never fired when it had (3 errors sitting past the cutoff).
        kinds: "dict[str, list[str]]" = {}
        for e in errors:
            kinds.setdefault(e.split(":", 1)[0], []).append(e)
        summary = "\n".join(
            "    {} x {}".format(len(v), k) for k, v in sorted(kinds.items()))
        samples = "\n".join(
            "    - " + v[0] for k, v in sorted(kinds.items()))
        raise SystemExit(
            "error: payload-scope validation failed ({} error(s)) — a shipped document points "
            "outside the payload, so it is dead on every install.\n"
            "  by kind:\n{}\n  one sample each:\n{}".format(len(errors), summary, samples))
    print("  [payload-scope         ] {} md checked - 0 errors - {} warning(s) "
          "(CR-AIWS-2026-08-071 C1/C2/C10)".format(len(md_files), len(warnings)))


# ---------- Manifest / Changelog ----------

def count_lines(path: Path) -> int:
    try:
        with path.open("r", encoding="utf-8", errors="replace") as f:
            return sum(1 for _ in f)
    except Exception:
        return 0


def walk_files(root: Path) -> list[Path]:
    out: list[Path] = []
    for p in sorted(root.rglob("*")):
        if p.is_file():
            out.append(p)
    return out


def build_manifest_text(payload_root: Path, version: str, date_str: str,
                        file_section_map: dict[str, str] | None = None) -> str:
    files = walk_files(payload_root)
    lines = [
        f"# MANIFEST — AI Work System MVP Install Package",
        f"**Version:** {version}",
        f"**Build date:** {date_str}",
        f"**Total files:** {len(files)}",
        "",
        "## Intentional exclusions",
        "",
        "Các mục sau KHÔNG có trong package theo QUYẾT ĐỊNH chủ đích — đừng báo bug 'thiếu' "
        "(CR-AIWS-2026-07-031 T6):",
        "",
        "- `aiws-eval` domain (skill + procedural + commands) — excluded per rename_map "
        "`dp_resolution_025.C` (CR-AIWS-2026-07-025).",
        "- `aiws-council-review` domain (skill + procedural) — canonical trong repo AIWS nhưng "
        "CHƯA ship cho adopter: skill chưa có một lượt dogfood ĐO ĐƯỢC (CR-AIWS-2026-08-067 C9, "
        "ruling DP-1064-E). Điều kiện gỡ nằm ở §7 của CR đó (noise floor → mẫu đối chứng → mẫu số "
        "tường minh → pre-registration), và gỡ phải bằng một CR riêng.",
        "- **`tooling/council_tally.py` cũng KHÔNG còn ship** (CR-AIWS-2026-08-115 C6, HUMAN "
        "ruling 2026-08-19). Bản package trước khai ngược — rằng tool vẫn ship vì \"dùng độc lập "
        "được\". Đúng về kỹ thuật, nhưng consumer duy nhất của nó là skill ở dòng trên, và không "
        "file nào trong payload nói tool này tồn tại. **Điều kiện quay lại:** tool được đưa lại "
        "TRONG CÙNG LƯỢT mà skill ra khỏi exclusion set — hai mục, một lượt.",
        "- `tooling/switch_system_mode.py` — docstring của chính nó khai `dev-only; NOT shipped`; "
        "trước CR-AIWS-2026-08-115 nó vẫn ship. Mục exclusion bị bỏ sót, nay đã sửa.",
        "- `tooling/convert_excel_to_md.py` — hard-require `markitdown`, không fallback stdlib. "
        "Chiều ngược lại (`convert_md_to_excel.py`) VẪN ship và có trong `tooling/README.md`.",
        "- `.claude/commands/aiws-agent-*.md` byte-copies — verb specs ship PACK-INTERNAL "
        "(`payload/agents/commands/` → `.ai-work/agents/commands/`); the `aiws-agent-*.md` files "
        "in `payload/commands/` are generated POINTER-STUBS, not spec copies (CR-AIWS-2026-08-019); "
        "entry points = router skill `aiws-agent` (NL) + stubs (explicit) "
        "(CR-AIWS-2026-07-025 shim_removals + CR-AIWS-2026-07-031 T3).",
        "- `quick_install_aiws.py` (dev-only trial tool) — deliberately not shipped.",
        "",
        "| File | Section | Lines |",
        "|------|---------|------:|",
    ]
    for f in files:
        rel = f.relative_to(payload_root.parent).as_posix()
        section = (file_section_map or {}).get(rel, "—")
        n = count_lines(f) if f.suffix in {".md", ".py", ".yml", ".yaml", ".jsonl", ".txt"} else 0
        lines.append(f"| {rel} | {section} | {n if n else '-'} |")
    return "\n".join(lines) + "\n"


def parse_manifest_file_list(manifest_path: Path) -> dict[str, tuple[str, int]]:
    """Extract {path: (section, lines)} from a MANIFEST.md built by this tool.
    Handles both old 2-column format (File, Lines) and new 3-column (File, Section, Lines).
    """
    out: dict[str, tuple[str, int]] = {}
    if not manifest_path.exists():
        return out
    in_table = False
    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("| File |"):
            in_table = True
            continue
        if in_table and line.startswith("|---"):
            continue
        if in_table and line.startswith("|"):
            parts = [p.strip() for p in line.strip("|").split("|")]
            if len(parts) >= 3:
                path, section = parts[0], parts[1]
                lines_str = parts[2]
            elif len(parts) == 2:
                path, section = parts[0], "—"
                lines_str = parts[1]
            else:
                continue
            try:
                lines_n = int(lines_str) if lines_str not in ("-", "") else 0
            except ValueError:
                lines_n = 0
            out[path] = (section, lines_n)
        elif in_table and not line.strip():
            break
    return out


def _section_summary(data: dict[str, tuple[str, int]]) -> dict[str, set[str]]:
    """Group file paths by section name."""
    result: dict[str, set[str]] = {}
    for path, (section, _) in data.items():
        result.setdefault(section, set()).add(path)
    return result


def _payload_changed(prev_pkg: Path, curr_pkg: Path, rel: str) -> bool:
    """File `rel` có ĐỔI NỘI DUNG giữa hai package không? (CR-AIWS-2026-08-112)

    Trước CR-112 việc này được suy từ cột `Lines` của MANIFEST — nên MỌI thay đổi giữ nguyên số
    dòng đều VÔ HÌNH. Đo trên cut trial-2026-08-19: CHANGELOG khai `Updated 29`, diff nội dung là
    **51**, và đúng **22** file bị bỏ sót đều có số dòng không đổi (29+22=51).

    EOL được chuẩn hoá trước khi hash (DP-112-B): repo cố ý giữ EOL gốc của file authored
    (CR-059 / CR-AIWS-2026-08-016), nên không chuẩn hoá thì một lần `git checkout` trên máy có
    `core.autocrlf` khác sẽ biến TOÀN BỘ file thành "Updated" — nhiễu còn tệ hơn bỏ sót.

    **Đây là NƠI DUY NHẤT định nghĩa tiêu chí phân loại** (DP-112-D). r1 của CR-112 chỉ sửa một
    trong hai chỗ dùng nó, và điều đó sẽ làm `## Summary` và `## Section Summary` khai hai con số
    khác nhau — đúng lớp defect mà CR này sinh ra để sửa. Đừng chép logic này ra chỗ thứ hai.
    """
    # `rel` là key của MANIFEST, và key đó ĐÃ mang tiền tố `payload/` (747/747 trên cut
    # trial-2026-08-19). Ghép thêm `"payload"` nữa là đường dẫn không tồn tại — và vì
    # `is_file()` trả False cho cả hai bên nên hàm này sẽ khai `Updated: 0` cho MỌI cut,
    # im lặng và trông hợp lý. Đó chính là hình dạng defect mà CR-112 sinh ra để diệt, nên
    # đừng "tối ưu" bằng cách thêm lại tiền tố.
    a, b = prev_pkg / rel, curr_pkg / rel
    if not (a.is_file() and b.is_file()):
        # MANIFEST liệt kê file này ở CẢ HAI package (caller chỉ duyệt phần giao) nên vắng mặt
        # trên đĩa là package hỏng hoặc path sai — KÊU LÊN, đừng trả False lặng lẽ.
        missing = [str(p) for p in (a, b) if not p.is_file()]
        print(f"[changelog] WARN: MANIFEST có `{rel}` nhưng không thấy trên đĩa: {missing} "
              f"-> bỏ qua khi phân loại Updated", file=sys.stderr)
        return False
    return a.read_bytes().replace(b"\r\n", b"\n") != b.read_bytes().replace(b"\r\n", b"\n")


def build_changelog_text(prev_pkg: Path, curr_pkg: Path, version: str) -> str:
    prev_manifest = parse_manifest_file_list(prev_pkg / "MANIFEST.md")
    curr_manifest = parse_manifest_file_list(curr_pkg / "MANIFEST.md")
    prev_files = set(prev_manifest.keys())
    curr_files = set(curr_manifest.keys())
    added = sorted(curr_files - prev_files)
    removed = sorted(prev_files - curr_files)
    updated = sorted(
        f for f in (curr_files & prev_files)
        if _payload_changed(prev_pkg, curr_pkg, f)          # CR-112: nội dung, không phải số dòng
    )
    lines = [
        f"# CHANGELOG — AI Work System MVP Install Package",
        f"**New version:** {version}",
        f"**Previous package:** {prev_pkg.name}",
        "",
        f"## Summary",
        f"- Added:   {len(added)}",
        f"- Updated: {len(updated)}",
        f"- Removed: {len(removed)}",
        "",
    ]

    # Section-level summary
    prev_by_section = _section_summary(prev_manifest)
    curr_by_section = _section_summary(curr_manifest)
    all_sections = sorted(prev_by_section.keys() | curr_by_section.keys())
    if all_sections:
        lines.append("## Section Summary")
        lines.append("")
        lines.append("| Section | Added | Updated | Removed | Unchanged |")
        lines.append("|---------|------:|--------:|--------:|----------:|")
        for sec in all_sections:
            p = prev_by_section.get(sec, set())
            c = curr_by_section.get(sec, set())
            sec_added = len(c - p)
            sec_removed = len(p - c)
            sec_updated = sum(
                1 for f in (c & p)
                if _payload_changed(prev_pkg, curr_pkg, f)  # CR-112: CÙNG tiêu chí với Summary tổng
            )
            sec_unchanged = len(c & p) - sec_updated
            lines.append(f"| {sec} | {sec_added} | {sec_updated} | {sec_removed} | {sec_unchanged} |")
        lines.append("")

    if added:
        lines.append("## Added")
        for f in added:
            lines.append(f"- `{f}` ({curr_manifest[f][1]} lines)")
        lines.append("")
    if updated:
        lines.append("## Updated")
        for f in updated:
            lines.append(f"- `{f}` ({prev_manifest[f][1]} → {curr_manifest[f][1]} lines)")
        lines.append("")
    if removed:
        lines.append("## Removed")
        for f in removed:
            lines.append(f"- `{f}` (was {prev_manifest[f][1]} lines)")
        lines.append("")
    if not (added or updated or removed):
        lines.append("_No file-level changes detected vs previous package._")
    return "\n".join(lines) + "\n"


# ---------- Generated docs ----------

README_TEMPLATE = """---
name: AI Work System MVP — Installable Package
version: {version}
package_date: {date}
target: any project adopting AI Work System MVP
---

# AI Work System MVP — Installable Package ({version})

Một package "drop-in" để cài **AI Work System MVP {version}** sang một dự
án khác. Bao gồm methodology spec, wiki operational guidance, các Claude
Code skill cho AIP/Wiki, cùng tooling Python (stdlib only) và templates
cần thiết để thực thi.

## Package layout

```
AI_Work_System_MVP_{version}_{date}/
├── README.md                   # file này
├── MANIFEST.md                 # file list + line counts (base cho changelog)
├── CHANGELOG.md                # có khi build với --prev
├── install_guide.md            # hướng dẫn cho AI tool tự cài đặt (tool-neutral)
├── CLAUDE_SLIM_TEMPLATE.md     # DEPRECATED 1 release — composed từ payload/install_templates/
└── payload/
    ├── methodology/            → .ai-work/truth/canonical/methodology/
    ├── wiki_guidelines/        → .ai-work/truth/canonical/wiki_guidelines/
    ├── skills/                 → .claude/skills/
    ├── commands/               → .claude/commands/
    ├── tooling/                → .ai-work/tooling/
    ├── aip_templates/          → .ai-work/aip/templates/
    ├── workspace_templates/    → .ai-work/workspace_templates/
    ├── preset_knowledge/       → .ai-work/preset_knowledge/
    ├── procedural/             → .ai-work/procedural/
    ├── truth_templates/        → .ai-work/truth/templates/
    ├── guidelines/             → .ai-work/guidelines/
    ├── aiws_wiki/              → .ai-work/wiki_sources/aiws_meta/
    ├── aiws_wiki_index/        → .ai-work/wiki_sources/ (index.aiws.jsonl + relations.aiws.jsonl, PRE-BUILT — copy at install)
    ├── agents/                 → .ai-work/agents/ (+ .claude/ wrappers via agent-pack wiring; only if shipped)
    └── install_templates/      → .ai-work/install_templates/ (core rules + adapters + identity + VERSION;
                                  compose_aiws_rules.py renders CLAUDE*.md / AGENTS.md / copilot-instructions.md)
```

## Cách dùng

Mở AI coding tool của bạn tại dự án đích, rồi nói:

> "Hãy cài AI Work System MVP {version} vào dự án này theo
> `<đường-dẫn>/install_guide.md`."

Claude sẽ đọc `install_guide.md` và tự thực hiện các bước (pre-flight →
copy payload → init Truth placeholder → wire CLAUDE.md/CLAUDE.local.md
với slim template → smoke test → report).

## Những thứ KHÔNG nằm trong package (cố ý loại bỏ)

- `.ai-work/wiki/` — Wiki nội dung là tài sản dự án đích
- `.ai-work/wiki_sources/meta/` — Meta của artifact dự án nguồn
- `.ai-work/aip/exec|plans|local/`, `workspaces/`, `history/` — Runtime của dự án nguồn
- Truth files (SOP_MASTER / AI_WORK_CONTRACT) — Phải do dự án đích tự viết
- `releases/`, `installable_packages/` — tránh recursive bloat
- Personal `*.local.md` files, backups, caches
- `methodology/00_brainstorming/` — brainstorming internal của AIWS project
- `methodology/90_delta_tracking/` — sprint backlogs, reviews, closure records — internal only
- `methodology/10_design/Detail_Design_MVP_Core_Artifacts.md` — excluded (internal only)
- `methodology/10_design/` (4 files còn lại) — **included nhưng stripped**: sections giải thích lý do thiết kế và AIWS design phases đã được loại bỏ; chỉ giữ lại operational conceptual/methodology/component knowledge
- `aip_templates/tracking/` — internal tracking files

## Yêu cầu hệ thống ở dự án đích
- Python 3.8+ (stdlib)
- Một AI coding tool đọc được rule file: Claude Code · Codex · GitHub Copilot
  (agent mode / Chat) · hoặc bất kỳ tool nào đọc `AGENTS.md`
- Không cần internet, không cần pip

## Build info
Package này được sinh tự động bởi `build_aiws_install_package.py` từ dự
án nguồn. Xem `MANIFEST.md` cho danh sách file + line counts.
"""


INSTALL_GUIDE_TEMPLATE = """---
name: AI Work System MVP {version} — Install Guide
audience: the AI coding tool executing the install (Claude Code / Codex / Copilot agent / …)
target_layout: project root with `.ai-work/` and `.claude/skills/` + `.claude/commands/`
---

# Install Guide — AI Work System MVP {version}

> **Đọc kỹ trước khi chạy.** Đây là hướng dẫn để **bạn (AI đang chạy)** tự cài
> package này vào dự án đích — không phụ thuộc bạn là tool nào. Người dùng chỉ cần
> trỏ bạn đến file này và xác nhận target project root.

## 0. Pre-conditions

Hỏi user **đúng 3 thứ** — không hỏi thêm gì khác:

1. **Target project root** — thư mục dự án đích (sẽ chứa `.ai-work/` và `.claude/`)
2. **Project name** — tên ngắn của dự án (điền `<PROJECT_NAME>` trong `project_identity.md`)
3. **`rule_targets`** — team dùng AI tool nào? multi-select `claude` | `agents` | `copilot`
   (default `claude`). Xem bảng ở Step 5 để biết target nào phủ surface nào —
   **hỏi rõ team dùng Copilot surface nào**, đừng suy từ IDE.

**Mặc định — không hỏi user, xử lý tự động:**

| Tình huống | Hành động mặc định |
|---|---|
| `.ai-work/` hoặc `.claude/skills/` đã tồn tại | **Abort** — báo rõ path conflict, đợi user chỉ định |
| `rule_targets` | `claude` (thêm `agents`/`copilot` khi user khai dùng Codex/Copilot) |
| `claude_rule_file` | `CLAUDE.local.md` (personal, gitignored; `CLAUDE.md` nếu team muốn commit) |
| Wiki registration mode | Không hỏi — AIWS Knowledge Sources đã nằm trong core rules |

Yêu cầu môi trường:
- Python 3.8+ (kiểm tra ở Step 1)
- Quyền tạo folder trong target root

## 1. Pre-flight check

**Windows — refresh PATH trước khi check Python** (tránh false-negative sau khi mới cài Python chưa restart shell):

```powershell
$env:PATH = [System.Environment]::GetEnvironmentVariable("PATH","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH","User")
python --version
```

Nếu Python không tìm thấy → báo user cài Python 3.8+ từ python.org rồi thử lại. Không tiếp tục.

Kiểm tra project root và conflict:

```bash
pwd   # phải là target project root
ls -la .ai-work 2>/dev/null && echo "EXISTS: .ai-work"
ls -la .claude/skills 2>/dev/null && echo "EXISTS: .claude/skills"
ls -la CLAUDE.md CLAUDE.local.md AGENTS.md .github/copilot-instructions.md 2>/dev/null
```

Nếu có conflict → STOP, báo rõ, đợi user.

## 2. Payload mapping

| # | Source (trong package) | Destination (target project) |
|---|---|---|
| 1 | `payload/methodology/` | `.ai-work/truth/canonical/methodology/` |
| 2 | `payload/wiki_guidelines/` | `.ai-work/truth/canonical/wiki_guidelines/` |
| 3 | `payload/skills/` | `.claude/skills/` |
| 4 | `payload/tooling/` | `.ai-work/tooling/` |
| 5 | `payload/aip_templates/` | `.ai-work/aip/templates/` |
| 6 | `payload/workspace_templates/` | `.ai-work/workspace_templates/` |
| 7 | `payload/preset_knowledge/` | `.ai-work/preset_knowledge/` |
| 8 | `payload/procedural/` | `.ai-work/procedural/` |
| 9 | `payload/truth_templates/` | `.ai-work/truth/templates/` |
| 10 | `payload/guidelines/` | `.ai-work/guidelines/` |
| 11 | `payload/wiki_source_profiles/` | `.ai-work/wiki_sources/profiles/` **(MERGE — never overwrite project profiles; see §3 note)** |
| 12 | `payload/commands/` | `.claude/commands/` **(mang pointer-stub `/aiws-agent-<verb>` generate lúc build — CR-2026-08-019; vắng/rỗng chỉ hợp lệ khi package KHÔNG có `agents/`; spec content vẫn pack-internal per CR-025/CR-031-T3)** |
| 13 | `payload/aiws_wiki/` | `.ai-work/wiki_sources/aiws_meta/` (metas AIWS đã rebase — Step 2) |
| 13b | `payload/aiws_wiki_index/` | `.ai-work/wiki_sources/` — `index.aiws.jsonl` + `relations.aiws.jsonl` **PRE-BUILT** (copy ở Step 4; rebuild optional bằng `build_preset_wiki.py --target .` — CR-AIWS-2026-08-064) |
| 14 | `payload/agents/` | `.ai-work/agents/` **(chỉ khi package có `agents/`; router skill `.claude/skills/aiws-agent/` đã nằm sẵn trong `payload/skills`; verb specs pack-internal — `.claude/commands` chỉ nhận pointer-stub generate, KHÔNG byte-copy, CR-031 T3 + CR-2026-08-019)** |
| 15 | `payload/methodology/30_templates/task_lens_presets.default.yml` | `.ai-work/wiki/task_lens_presets/starter_lenses.yml` **(SEED-IF-ABSENT — never overwrite; dir là wiki project-local, project tự curate lens sau install — CR-AIWS-2026-07-039)** |

## 3. Install — copy payload

> **Tip:** Thay vì chạy thủ công, hãy dùng skill `/aiws-pkg install` trong package
> (`payload/skills/aiws-pkg/SKILL.md`) — skill sẽ tự động thực hiện tất cả
> các bước bên dưới và wire CLAUDE.local.md.

```bash
PKG="<absolute-path-to-this-package>"
DEST="$(pwd)"

mkdir -p "$DEST/.ai-work/truth/canonical/methodology"
mkdir -p "$DEST/.ai-work/truth/canonical/wiki_guidelines"
mkdir -p "$DEST/.ai-work/tooling"
mkdir -p "$DEST/.ai-work/aip/templates"
mkdir -p "$DEST/.ai-work/aip/plans"
mkdir -p "$DEST/.ai-work/aip/exec"
mkdir -p "$DEST/.ai-work/aip/local"
mkdir -p "$DEST/.ai-work/workspace_templates"
mkdir -p "$DEST/.ai-work/workspaces"
mkdir -p "$DEST/.ai-work/procedural"
mkdir -p "$DEST/.ai-work/preset_knowledge"
mkdir -p "$DEST/.ai-work/truth/templates"
mkdir -p "$DEST/.ai-work/guidelines"
mkdir -p "$DEST/.ai-work/wiki_sources"
mkdir -p "$DEST/.ai-work/wiki_sources/aiws_meta"
mkdir -p "$DEST/.ai-work/wiki"
mkdir -p "$DEST/.ai-work/history/trail"
mkdir -p "$DEST/.ai-work/history/evidence"
mkdir -p "$DEST/.ai-work/history/archive"
mkdir -p "$DEST/.claude/skills"
mkdir -p "$DEST/.claude/commands"
[ -d "$PKG/payload/agents" ] && mkdir -p "$DEST/.ai-work/agents"

cp -r "$PKG/payload/methodology/."          "$DEST/.ai-work/truth/canonical/methodology/"
cp -r "$PKG/payload/wiki_guidelines/."      "$DEST/.ai-work/truth/canonical/wiki_guidelines/"
cp -r "$PKG/payload/skills/."               "$DEST/.claude/skills/"
# payload/commands mang pointer-stub /aiws-agent-<verb> (generate lúc build — CR-2026-08-019; spec content vẫn pack-internal per CR-031 T3); vắng chỉ khi package không có agents/
[ -d "$PKG/payload/commands" ] && cp -r "$PKG/payload/commands/." "$DEST/.claude/commands/"
cp -r "$PKG/payload/tooling/."              "$DEST/.ai-work/tooling/"
cp -r "$PKG/payload/aip_templates/."        "$DEST/.ai-work/aip/templates/"
cp -r "$PKG/payload/workspace_templates/."  "$DEST/.ai-work/workspace_templates/"
cp -r "$PKG/payload/preset_knowledge/."     "$DEST/.ai-work/preset_knowledge/"
cp -r "$PKG/payload/procedural/."           "$DEST/.ai-work/procedural/"
cp -r "$PKG/payload/truth_templates/."      "$DEST/.ai-work/truth/templates/"
cp -r "$PKG/payload/guidelines/."           "$DEST/.ai-work/guidelines/"
cp -r "$PKG/payload/aiws_wiki/."              "$DEST/.ai-work/wiki_sources/aiws_meta/"
# Task Lens presets (CR-AIWS-2026-07-039 / R3-04): SEED-IF-ABSENT — mọi emitter (create.md, ASC,
# AIP templates, Task_Lens_Spec) trỏ .ai-work/wiki/task_lens_presets/; thiếu nó Task Lens âm thầm
# không bao giờ engage. NEVER overwrite: dir là wiki project-local, project curate sau install.
mkdir -p "$DEST/.ai-work/wiki/task_lens_presets"
[ -f "$DEST/.ai-work/wiki/task_lens_presets/starter_lenses.yml" ] || cp "$PKG/payload/methodology/30_templates/task_lens_presets.default.yml" "$DEST/.ai-work/wiki/task_lens_presets/starter_lenses.yml"
# AI Agents Pack (only if shipped) — body → .ai-work/agents/; router skill already rides
# payload/skills/ + verb pointer-stubs ride payload/commands/ above (wired at build,
# CR-2026-08-019). Verb spec CONTENT stays pack-internal (CR-025/CR-031-T3).
[ -d "$PKG/payload/agents" ] && cp -r "$PKG/payload/agents/."  "$DEST/.ai-work/agents/"

# wiki_source_profiles are PROJECT-OWNED — content-level MERGE (never overwrite); skips project_stopwords.yml (CR-AIWS-2026-06-047)
python "$DEST/.ai-work/tooling/merge_wiki_source_profiles.py" --from "$PKG/payload/wiki_source_profiles" --into "$DEST/.ai-work/wiki_sources/profiles" --apply
```

> **wiki_source_profiles are project-owned (CR-AIWS-2026-06-047).** They are **merged**, not
> `cp -r`-overwritten: a profile the project already customized keeps its values / comments /
> `extra_stopwords`; only canonical top-level keys it is **missing** are added. `project_stopwords.yml`
> is **project-authored** — neither shipped nor written by the install. The merge is done by the
> shipped `merge_wiki_source_profiles.py` (run above, after `tooling/` is copied).

## 4. Init Truth placeholders

```bash
touch "$DEST/.ai-work/truth/SOP_MASTER.md"
touch "$DEST/.ai-work/truth/AI_WORK_CONTRACT.md"

# EOL convention (CR-AIWS-2026-08-005, shipped by CR-AIWS-2026-08-073 C3) — SEED IF ABSENT.
# `check_eol_alignment.py` assumes `* -text`; hand the convention over with the tool that needs it.
# A project that already has a .gitattributes keeps it untouched.
[ -f "$DEST/.gitattributes" ] || echo '* -text' > "$DEST/.gitattributes"   # echo, not printf: no escape to survive two string layers
: > "$DEST/.ai-work/wiki_sources/index.jsonl"
echo "[]" > "$DEST/.ai-work/wiki_sources/index.local.sources.json"

# Preset AIWS wiki (searchable `aiws` namespace) = index.aiws.jsonl + relations.aiws.jsonl.
# They ship PRE-BUILT (payload/aiws_wiki_index/, CR-AIWS-2026-08-064) — just copy them:
cp "$PKG/payload/aiws_wiki_index/index.aiws.jsonl"     "$DEST/.ai-work/wiki_sources/index.aiws.jsonl"
cp "$PKG/payload/aiws_wiki_index/relations.aiws.jsonl" "$DEST/.ai-work/wiki_sources/relations.aiws.jsonl"
# Optional (or when the package has no aiws_wiki_index/): rebuild both in place from the shipped metas.
# Run from $DEST so the tools resolve the project root correctly.
( cd "$DEST" && python .ai-work/tooling/build_preset_wiki.py --target . )
```

> `index.jsonl` / `relations.jsonl` (dự án tự) để rỗng — sẽ đầy khi chạy `/aiws-wiki bootstrap`.
> `index.aiws.jsonl` + `relations.aiws.jsonl` (kiến thức AIWS) có sẵn ngay → AI tra cứu
> (`lookup_wiki_source.py`, default scope `project,aiws`) và tra quan hệ (`wiki_relations.py --relations <id>`
> đọc cả 2 namespace) được ngay sau cài. AIWS upgrade chỉ thay 2 file này + `aiws_meta/`, không đụng
> `index.jsonl`/`relations.jsonl`/`meta/` của dự án.

Hỏi user: muốn Claude draft 3 file Truth từ AIP templates trong
`.ai-work/aip/templates/` không? **KHÔNG tự bịa nội dung Truth.**

## 5. Wire rule files (per `rule_targets`)

Rule content KHÔNG còn được chép tay. Copy templates rồi để tool render — một nguồn, N file.

### 5.1. Đặt nguồn vào target

```bash
cp -r payload/install_templates "$DEST/.ai-work/install_templates"      # gồm cả VERSION (stamped at build)
cp "$DEST/.ai-work/install_templates/aiws_core_rules.md" "$DEST/.ai-work/AIWS.md"

# Project profile (CR-AIWS-2026-08-128 C5) — SEED-IF-ABSENT, không bao giờ ghi đè.
py "$DEST/.ai-work/tooling/project_profile.py" init --ai-work "$DEST/.ai-work"
py "$DEST/.ai-work/tooling/project_profile.py" check --ai-work "$DEST/.ai-work"   # rc=1 nếu chưa đủ
```

`.ai-work/AIWS.md` = core rules (model-agnostic, package-owned — upgrade ghi đè).
`.ai-work/install_templates/VERSION` = version manifest; `compose_aiws_rules.py` đọc nó và **từ chối
đoán** nếu thiếu.

`.ai-work/project_profile.yml` = **project-owned** config (ngược lại với AIWS.md: upgrade KHÔNG ghi đè).
`init` chỉ tạo khi CHƯA có. `check` in ra key còn thiếu / bất biến bị vi phạm rồi **exit non-zero** —
nó không bao giờ đoán hộ, và không dùng `input()` nên chạy được cả trong CI lẫn agent run. Muốn bổ sung
các key còn thiếu (không đụng dòng nào của bạn): `project_profile.py refresh` (dry-run) rồi `--apply`.

### 5.2. Render file rule cho từng target

```bash
( cd "$DEST" && python .ai-work/tooling/compose_aiws_rules.py     --init --tools <rule_targets> --claude-file <claude_rule_file>     --project-name "<PROJECT_NAME>" )          # dry-run: in diff, KHÔNG ghi
( cd "$DEST" && python .ai-work/tooling/compose_aiws_rules.py     --init --tools <rule_targets> --claude-file <claude_rule_file>     --project-name "<PROJECT_NAME>" --apply )  # ghi thật
```

| target | file sinh ra | git | phục vụ surface nào |
|---|---|---|---|
| `claude` | `<claude_rule_file>` (`CLAUDE.local.md` mặc định) | local: gitignore · `CLAUDE.md`: commit | Claude Code (core nạp qua `@.ai-work/AIWS.md`) |
| `agents` | `AGENTS.md` (repo root) | commit | Codex · Copilot coding agent/CLI/Chat-in-VS-Code/code-review-GitHub.com · Cursor/Zed… |
| `copilot` | `.github/copilot-instructions.md` | commit | Copilot surface **không** đọc AGENTS.md — vd **code review in VS Code**, Chat ngoài VS Code |

**File đã tồn tại** — tool tự phân loại và DỪNG với hướng xử lý, không bao giờ ghi đè im lặng:
- có sẵn rule AIWS viết tay (chuỗi `AI Work System MVP`) → `--migrate-legacy` (bọc vùng cũ vào block,
  giữ phần project-owned; backup trước khi ghi)
- file lạ không liên quan AIWS → `--init --append-existing` (append block, giữ nguyên nội dung cũ) —
  **quyết định của HUMAN**, hỏi trước
- đã có block AIWS → `--refresh` (đây là đường của upgrade, không phải install)

Mọi lượt ghi đều: backup `.bak-<ts>` → ghi → **self-verify** bytes NGOÀI block không đổi (sai thì tự
khôi phục và báo lỗi). Nội dung ngoài block là của dự án; AIWS không đụng tới.

### 5.3. Verify

```bash
( cd "$DEST" && python .ai-work/tooling/compose_aiws_rules.py --check )   # rc=0 + version khớp manifest
```

## 6. Smoke test

```bash
python .ai-work/tooling/lint_all.py --help
python .ai-work/tooling/lookup_wiki_source.py --query methodology || true
test -f .ai-work/AIWS.md && test -f .ai-work/install_templates/VERSION && echo "rules source OK"
python .ai-work/tooling/compose_aiws_rules.py --check          # mọi rule file cùng version
```

Theo từng target đã chọn:

```bash
ls .claude/skills/                                             # claude
grep -q "AIWS:BEGIN rules" AGENTS.md && echo "AGENTS.md OK"    # agents
grep -q "AIWS:BEGIN rules" .github/copilot-instructions.md && echo "copilot OK"
```

## 7. Report

```
✅ AI Work System MVP {version} installed at: <DEST>

Copied:
- methodology → .ai-work/truth/canonical/methodology/
- wiki_guidelines → .ai-work/truth/canonical/wiki_guidelines/
- skills (N) → .claude/skills/
- commands → .claude/commands/
- tooling → .ai-work/tooling/
- aip_templates → .ai-work/aip/templates/
- workspace_templates → .ai-work/workspace_templates/
- preset_knowledge → .ai-work/preset_knowledge/
- procedural → .ai-work/procedural/
- aiws_wiki → .ai-work/wiki_sources/aiws_meta/
- aiws_wiki_index → .ai-work/wiki_sources/ (index.aiws.jsonl + relations.aiws.jsonl, pre-built)

Wired (theo rule_targets):
- .ai-work/AIWS.md (core rules) + .ai-work/install_templates/ (+VERSION <version>)
- <mỗi target: CLAUDE.local.md | CLAUDE.md | AGENTS.md | .github/copilot-instructions.md> → <created | appended | migrated>

Empty placeholders (you must fill):
- .ai-work/truth/SOP_MASTER.md
- .ai-work/truth/AI_WORK_CONTRACT.md

AIWS knowledge: searchable by default (scope project,aiws; index.aiws.jsonl + relations.aiws.jsonl in place); AIWS Knowledge Sources pointer nằm trong core rules

Smoke test: <PASS | WARN: ...>

Next:
  1. Viết Truth (SOP_MASTER + AI_WORK_CONTRACT)
  2. Chạy task đầu tiên:
     - Claude Code: /aiws-aip create → /aiws-aip run → /aiws-lint
     - Codex / Copilot / tool khác: đọc .claude/skills/aiws-aip/SKILL.md rồi làm theo
       operations/create.md → operations/run.md; finalize bằng
       python .ai-work/tooling/lint_all.py
```

## 8. Rules cho install AI

- **KHÔNG ghi đè** file đã tồn tại mà chưa hỏi user
- **KHÔNG sửa** nội dung methodology hoặc wiki_guidelines khi copy
- **KHÔNG tự bịa** Truth (SOP/Contract)
- **KHÔNG copy** workspaces/, history/, wiki/ (không có sẵn, cố ý) — NGOẠI LỆ duy nhất: seed-if-absent `.ai-work/wiki/task_lens_presets/starter_lenses.yml` từ presets default (CR-AIWS-2026-07-039; never overwrite)
- **Stop và hỏi** khi gặp conflict, ambiguity, hoặc pre-flight fail
- Sau install, gợi ý user chạy `/aiws-lint` để verify
"""


START_HERE_TEMPLATE = """# START HERE — AI Work System MVP {version}

Tham khảo file này để cài đặt hoặc nâng cấp AI Work System nhanh nhất.

---

## Cài mới (fresh project)

Mở **AI coding tool của bạn** (Claude Code / Codex / Copilot agent…) tại project đích, paste prompt sau:

```
Hãy cài AI Work System MVP {version} vào dự án này.
Package nằm tại: <điền đường dẫn tuyệt đối đến folder này>
Đọc install_guide.md và làm theo từng bước.
```

## Nâng cấp (đã có AIWS)

```
Hãy nâng cấp AI Work System lên {version}.
Package mới nằm tại: <điền đường dẫn tuyệt đối đến folder này>
Dùng skill /aiws-pkg upgrade (Claude Code), hoặc đọc .claude/skills/aiws-pkg/operations/upgrade.md và làm theo.
```

---

**Files trong package:**
- `install_guide.md` — hướng dẫn chi tiết từng bước cài mới
- `payload/install_templates/` — nguồn rule file (core + adapter + identity + VERSION)
- `CLAUDE_SLIM_TEMPLATE.md` — **DEPRECATED** (1 release nữa); composed từ install_templates
- `MANIFEST.md` — danh sách đầy đủ tất cả file trong payload
- `CHANGELOG.md` — thay đổi so với bản trước (nếu có)
- `payload/` — toàn bộ nội dung cần cài

**Skills trong package:** skills/ (10 skills — xem payload/skills/; con số đã trừ các domain trong
exclusion set và đã cộng router `aiws-agent` do build tự wire vào, nên nó KHÔNG bằng số thư mục
trong `product/skills/` — đếm lại từ `payload/skills/` của một lần build thật khi con số đổi)
"""


def compose_slim_template(templates_dir: Path, version: str) -> str:
    """Compose the deprecated CLAUDE_SLIM_TEMPLATE.md from the real install_templates (CR-066).

    The template used to be a hard-coded string here, which is exactly how it drifted from the rules
    projects actually run. It is now assembled from the same files `compose_aiws_rules.py` renders, so
    the transition artifact cannot say something the source does not. Removal is scheduled for the
    release after this one — see aiws-pkg/operations/build.md.
    """
    def part(name: str) -> str:
        f = templates_dir / name
        if not f.exists():
            return ""
        return f.read_text(encoding="utf-8").replace("\r\n", "\n").strip("\n")

    identity = (part("project_identity.md")
                .replace("<RULE_FILE_TITLE>", "CLAUDE.md")
                .replace("<AIWS_VERSION>", version))
    banner = (
        "<!-- DEPRECATED (CR-AIWS-2026-08-066): kept for one transition release.\n"
        "     Do not hand-copy this file. Install/upgrade renders each tool's rule file from\n"
        "     payload/install_templates/ via:\n"
        "       python .ai-work/tooling/compose_aiws_rules.py --init --tools claude,agents,copilot --apply\n"
        "     Composed from those same templates, so it cannot drift from them. -->\n"
    )
    return (banner + "\n" + identity + "\n\n" + part("adapter_claude.md")
            + "\n\n" + part("aiws_core_rules.md") + "\n")


# ---------- Main ----------


def _release_sort_key(name: str) -> tuple:
    """Sort key for release folder names AI_Work_System_MVP_<version>_<YYYY-MM-DD>.
    Orders by SEMANTIC version, with the date as tiebreak. A plain name sort ranks
    'v0.9_...' ABOVE 'v0.9.26_...' because '_' (0x5F) > '.' (0x2E), which made
    prev auto-detect pick a stale release. Handles letter-suffixed patches (v0.9.23b)."""
    stem = name[len("AI_Work_System_MVP_"):] if name.startswith("AI_Work_System_MVP_") else name
    m = re.match(r"^v?(.+?)_(\d{4}-\d{2}-\d{2})$", stem)
    ver_str, date_str = (m.group(1), m.group(2)) if m else (stem.lstrip("v"), "")
    comps: list[tuple] = []
    for part in ver_str.split("."):
        pm = re.match(r"^(\d+)([A-Za-z]*)$", part)
        comps.append((int(pm.group(1)), pm.group(2)) if pm else (0, part))
    return (comps, date_str)


def build(version: str, output: Path, prev: Path | None, project_root: Path,
          date_str: str) -> int:
    if output.exists():
        print(f"error: output already exists: {output}", file=sys.stderr)
        return 2

    print(f"building AI Work System MVP install package")
    print(f"  version: {version}")
    print(f"  project root: {project_root}")
    print(f"  output: {output}")

    output.mkdir(parents=True)
    payload_root = output / "payload"
    payload_root.mkdir()

    # CR-096 C3: bộ đếm cộng dồn `total_files` đã gỡ — console đếm bằng walk_files(payload_root)
    section_report: list[tuple[str, int]] = []
    file_section_map: dict[str, str] = {}

    for sec in PAYLOAD_SECTIONS:
        src = project_root / sec.src_rel
        dst = output / sec.dst_rel
        if not src.exists():
            print(f"  ! skip {sec.name}: source missing ({src})")
            section_report.append((sec.name, 0))
            continue
        exclude_names = sec.exclude_subdirs | sec.exclude_files
        # Build guard (CR-AIWS-2026-07-020): in the skill-bearing sections, a dev-only skill
        # exclusion (quick-install / eval set) that matches nothing means its target was renamed
        # away from the exclude list — fail rather than silently ship it. Other sections carry
        # PRECAUTIONARY excludes that are legitimately absent, so the guard stays scoped.
        # CR-AIWS-2026-08-115 C8 nống thêm `tooling`: trước CR đó `tooling` chỉ có exclude phòng hờ,
        # từ nay nó mang BA QUYẾT ĐỊNH THẬT (xem PAYLOAD_EXCLUDES trong _common.py). Một entry stale
        # — vì tool bị rename — sẽ làm tool IM LẶNG SHIP LẠI, tức quyết định tự huỷ mà không ai biết.
        if sec.name in ("skills", "procedural", "tooling"):
            stale = sorted(nm for nm in exclude_names if not (src / nm).exists())
            if stale:
                raise SystemExit(
                    f"BUILD GUARD: section '{sec.name}' dev-only exclude entries match nothing under "
                    f"{sec.src_rel}: {stale} — update the exclude list (CR-AIWS-2026-07-020)."
                )
        exclude_abs = frozenset(src / nm for nm in exclude_names) if exclude_names else None
        files, _ = copy_tree_filtered(src, dst, exclude_abs)
        section_report.append((sec.name, files))
        print(f"  [{sec.name:22}] {files:4} files")
        # Record section for each copied file (for MANIFEST Section column)
        if dst.exists():
            for f in walk_files(dst):
                rel = f.relative_to(output).as_posix()
                file_section_map[rel] = sec.name

    # CR-AIWS-2026-08-066: stamp the rule-template VERSION manifest. BUILD IS THE ONLY SITE that
    # stamps it — install/upgrade/quick-install merely carry it with the section copy, so a target can
    # never hold a version that no build produced. compose_aiws_rules.py reads this file (tier 1) and
    # refuses to guess when it is absent (tier 2 = the source tree's own pin, then hard failure).
    templates_dst = output / "payload" / "install_templates"
    if templates_dst.is_dir():
        version_file = templates_dst / "VERSION"
        write_text(version_file,
                   "---\n"
                   f"aiws_version: {version}\n"
                   f"release_date: {date_str}\n"
                   "---\n\n"
                   "Stamped by build_aiws_install_package.py (CR-AIWS-2026-08-066). Read by\n"
                   "compose_aiws_rules.py to version the AIWS block in each rule file.\n")
        file_section_map[version_file.relative_to(output).as_posix()] = "install_templates"
        section_report = [(n, c + 1) if n == "install_templates" else (n, c)
                          for n, c in section_report]
        print(f"  [install_templates   ] +1 VERSION manifest ({version})")

    # Strip-and-copy design docs: 10_design/ is excluded from the main loop but
    # selected files are copied here with AIWS-internal sections removed.
    stripped_count = 0
    for src_rel in DESIGN_DOCS_STRIP_COPY:
        src = project_root / src_rel
        if not src.exists():
            print(f"  ! skip design strip-copy: source missing ({src_rel})")
            continue
        rel_under_methodology = Path(src_rel).relative_to(
            "product/methodology/ai_work_system"
        )
        dst = output / "payload" / "methodology" / rel_under_methodology
        dst.parent.mkdir(parents=True, exist_ok=True)
        content = src.read_text(encoding="utf-8", errors="replace")
        headings = DESIGN_STRIP_HEADINGS.get(src_rel, [])
        stripped = strip_design_sections(content, headings)
        write_text(dst, stripped)
        file_section_map[dst.relative_to(output).as_posix()] = "methodology"
        stripped_count += 1
    if stripped_count:
        print(f"  [design docs (stripped)] {stripped_count} files (internal sections removed)")

    # Ship the pre-built AIWS wiki bundle (rebased metas) as the `aiws` namespace (CR-040).
    build_aiws_wiki_bundle(project_root, output, file_section_map)
    # CR-AIWS-2026-08-064 C5: pre-build the preset projections (index.aiws.jsonl +
    # relations.aiws.jsonl) from the rebased bundle so install can COPY them (python-free Step 4).
    build_aiws_wiki_index_bundle(output, file_section_map)

    # Wire the AI Agents Pack .claude surfaces (CR-AIWS-2026-06-051) — no-op if product/agents/ absent.
    wire_agent_pack_claude(project_root, output, file_section_map)

    for src_rel, dst_rel in single_files_for(project_root):
        src = project_root / src_rel
        if src.exists():
            dst = output / dst_rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        else:
            # CR-AIWS-2026-08-121 r3: never silent. A declared single-file that is absent used to
            # vanish from the package with nothing said, which is how a release note can stop
            # shipping and no gate notice.
            print(f"warn: declared single-file payload missing, not shipped: {src_rel}",
                  file=sys.stderr)

    # CR-AIWS-2026-08-071 C1/C2/C10 — the payload tree is complete here (all sections copied,
    # agent-pack wired, extra single files in). Validate it BEFORE writing manifest/changelog:
    # a package that ships dead refs must not get a manifest describing it as shippable.
    #
    # WIRED 2026-08-17 by CR-AIWS-2026-08-078 C8 — the LAST step of that CR, deliberately after
    # C1/C3 fixed the links. History: CR-071 r3 implemented and verified this function but left the
    # call commented, because a trial build then measured 43 escaping links (CR-071 §2 had scoped 3;
    # F1 was sampling a much larger population) and turning it on would have made the repo
    # UNBUILDABLE — beyond that CR's approved scope. DP-071-E chose fix-all, and CR-078 did the
    # fixing: the widened dual-tree link rule surfaced 51 findings, 41 real, all converted to
    # repo-root-relative TEXT (CR-AIWS-2026-07-029 §3.1). Trial build immediately before wiring:
    # 0 errors, 110 advisory WARNs.
    n_tools = write_tools_index(output)
    if n_tools:
        print(f"  [tooling               ] +1 TOOLS_INDEX.md ({n_tools} tool)")

    validate_payload_scope(output)

    start_here_path = output / "START_HERE.md"
    write_text(start_here_path,
        START_HERE_TEMPLATE.format(version=version))

    readme_path = output / "README.md"
    write_text(readme_path, 
        README_TEMPLATE.format(version=version, date=date_str))

    guide_path = output / "install_guide.md"
    write_text(guide_path, 
        INSTALL_GUIDE_TEMPLATE.format(version=version))

    # CR-AIWS-2026-08-066: the slim template is no longer an embedded string — it is COMPOSED from the
    # same install_templates the installer uses, so the deprecated artifact cannot drift from the real
    # source. Kept for ONE transition release (CR-AIWS-2026-07-020 `keep_old_as_deprecation_pointer`
    # shape); the removal ledger lives in aiws-pkg/operations/build.md, not in a per-release note file.
    slim_src = output / "payload" / "install_templates"
    if slim_src.is_dir():
        slim_path = output / "CLAUDE_SLIM_TEMPLATE.md"
        write_text(slim_path, compose_slim_template(slim_src, version))

    manifest_path = output / "MANIFEST.md"
    write_text(manifest_path, 
        build_manifest_text(payload_root, version, date_str, file_section_map))

    if prev is not None:
        if not (prev / "MANIFEST.md").exists():
            print(f"  ! prev package has no MANIFEST.md, skipping changelog: {prev}")
        else:
            changelog_path = output / "CHANGELOG.md"
            write_text(changelog_path, 
                build_changelog_text(prev, output, version))
            print(f"  [changelog           ] written vs {prev.name}")

    # CR-AIWS-2026-08-096 C3: đếm bằng walk_files(payload_root) — ĐÚNG phép đếm MANIFEST dùng
    # (build_manifest_text: `files = walk_files(payload_root)` -> `**Total files:** {len(files)}`).
    # Bộ đếm cộng dồn cũ đi qua ~8 điểm `+= 1` / `+= files` nên trôi khỏi cây thật lúc nào không hay.
    print(f"\n  total payload files: {len(walk_files(payload_root))}")
    print(f"  package root:        {output}")
    print(f"  START_HERE.md, README.md, MANIFEST.md, install_guide.md, CLAUDE_SLIM_TEMPLATE.md written")

    # Guard: warn if any output file has a name that may cause unzip errors on Windows
    long_name_files = [f for f in walk_files(output) if len(f.name) > 100]
    if long_name_files:
        print(f"\n  WARNING: {len(long_name_files)} file(s) with filename > 100 chars (may cause Windows unzip errors):")
        for f in long_name_files[:5]:
            print(f"    {f.relative_to(output).as_posix()} ({len(f.name)} chars)")
        if len(long_name_files) > 5:
            print(f"    ... and {len(long_name_files) - 5} more")

    return 0


def _wiki_gate(project_root: Path, strict: bool) -> int:
    """AIP-EXEC-925 pre-package wiki-regression gate (WARN-default). Runs the aggregate runner
    (.ai-work/tests/test_wiki_all.py) and returns a DIRECTIVE: 0 = proceed with the build, 2 = refuse.
    Refuse only when `strict` AND the runner reports a REAL degrade (rc==1). rc==2 (harness/corpus
    absent — a dev-only fixture, never a build input) is a WARN-skip. A missing runner = nothing to
    gate = proceed. The gate is never reached for trial (--override-version) or --force builds."""
    import subprocess
    runner = project_root / ".ai-work" / "tests" / "test_wiki_all.py"
    if not runner.exists():
        return 0
    print("  wiki regression gate: running test_wiki_all.py (WARN-default) ...", file=sys.stderr)
    rc = subprocess.run([sys.executable, str(runner)]).returncode
    if rc == 1:
        if strict:
            print("error: wiki regression gate DEGRADE (rc=1) — refusing this official build (--strict). "
                  "Fix the wiki suite or pass --force.", file=sys.stderr)
            return 2
        print("WARNING: wiki regression gate DEGRADE (rc=1) — proceeding (WARN default; pass --strict "
              "to refuse). See .ai-work/tests/test_wiki_all.py.", file=sys.stderr)
    elif rc == 2:
        print("WARNING: wiki regression harness/corpus absent (rc=2) — gate WARN-skipped.", file=sys.stderr)
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--override-version", help="Override the pinned version — TRIAL/EPHEMERAL builds only "
                                              "(quick_install). Official builds omit this and read "
                                              "product/aiws_version.md.")
    p.add_argument("--output", help="Output folder (default: releases/AI_Work_System_MVP_<version>_<date>)")
    p.add_argument("--prev", help="Previous package folder for changelog (auto-detected from releases/ if omitted)")
    p.add_argument("--no-prev", action="store_true", help="Skip changelog even if a previous package is found")
    p.add_argument("--project-root", help="Project root (default: auto-detect ancestor with .ai-work/)")
    p.add_argument("--strict", action="store_true",
                   help="AIP-925 gate: escalate a wiki-regression DEGRADE (rc=1) on an OFFICIAL build to a "
                        "hard REFUSE (default is WARN-and-proceed).")
    p.add_argument("--force", action="store_true",
                   help="AIP-925 gate: bypass the wiki-regression gate entirely (records the skip).")
    args = p.parse_args(argv)

    start = Path(args.project_root) if args.project_root else Path.cwd()
    try:
        project_root = find_ai_work_root(start)
    except SystemExit as e:
        print(str(e), file=sys.stderr)
        return 2

    # Version is pinned in product/aiws_version.md (single source of truth) so
    # every official build is identical. --override-version is the trial-only escape.
    if args.override_version:
        version, date_str = args.override_version, today()
    else:
        try:
            version, pinned_date = read_pinned_version(project_root)
        except SystemExit as e:
            print(str(e), file=sys.stderr)
            return 2
        date_str = pinned_date or today()

    if args.output:
        output = Path(args.output)
        if not output.is_absolute():
            output = project_root / output
    else:
        output = project_root / "releases" / f"AI_Work_System_MVP_{version}_{date_str}"

    prev = None
    if args.prev:
        prev = Path(args.prev)
        if not prev.is_absolute():
            prev = project_root / prev
        if not prev.is_dir():
            print(f"error: --prev not found: {prev}", file=sys.stderr)
            return 2
    elif not args.no_prev:
        # Auto-detect: find latest AI_Work_System_MVP_* folder in releases/
        releases_dir = project_root / "releases"
        if releases_dir.is_dir():
            candidates = sorted(
                [d for d in releases_dir.iterdir()
                 if d.is_dir() and d.name.startswith("AI_Work_System_MVP_") and d != output],
                key=lambda d: _release_sort_key(d.name),
            )
            if candidates:
                prev = candidates[-1]
                print(f"  (auto-detected previous package: {prev.name})")

    # Official (pinned) build whose folder already exists = the pinned version is
    # already released. Point the user at the fix instead of a bare "already exists".
    if not args.override_version and output.exists():
        print(f"  hint: {version} ({date_str}) is already released. Bump 'aiws_version' "
              f"(and 'release_date') in {VERSION_PIN_REL} to cut a new version.",
              file=sys.stderr)

    # AIP-EXEC-925: WARN-default wiki-regression gate — OFFICIAL builds only. Trial builds
    # (--override-version) skip it; --force bypasses; --strict escalates a real degrade to REFUSE.
    if args.override_version:
        pass                                        # trial build — gate skipped (fast, uncoupled)
    elif args.force:
        print("  (wiki regression gate bypassed: --force)", file=sys.stderr)
    elif _wiki_gate(project_root, args.strict) != 0:
        return 2                                    # --strict refuse on a real degrade

    return build(version, output, prev, project_root, date_str)


if __name__ == "__main__":
    sys.exit(main())
