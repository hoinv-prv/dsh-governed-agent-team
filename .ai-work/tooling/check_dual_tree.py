#!/usr/bin/env python3
"""Dual-tree drift check (CR-AIWS-2026-07-030 change B).

AIWS's dual-tree invariant: every shippable surface exists twice — `product/**` (the
packaged source) and its installed twin (`.ai-work/**` / `.claude/**`; methodology
mirrors under `.ai-work/truth/canonical/`). This module compares every pair and reports:

- ``dual_tree_drift``       — pair content differs (EOL-INSENSITIVE per DP-1; EOL-only
                              differences are NOT drift and normalize gradually on touch)
- ``dual_tree_only_in_one`` — a file exists on one side only and is not a classified
                              by-design exception

Severity is decided by the caller (lint_all reports WARN per DP-3; an apply-CR AIP must
reach 0 findings on its own footprint before flipping `applied` — CR Spec §13).

The pair map DERIVES from quick_install's ``PAYLOAD_MAP`` (single source of what ships
twice) — do not duplicate the table by hand. On an installed project (no `product/`
tree), :func:`check` returns [] (nothing to compare — the source tree is absent).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import PAYLOAD_MAP  # noqa: E402  (single source of the section map; _common IS shipped
                                 #  — quick_install_aiws is not: IR-2026-08-17 F1)

# product-side source subdirs where the payload key is not literally product/<key>
PROD_SRC = {"methodology": "product/methodology/ai_work_system"}

# ---- Classified by-design exceptions (keep in sync with CR-AIWS-2026-07-030 §2-A0) ----
# only-in-PRODUCT paths that are install-excluded on purpose (never mirrored):
ONLY_OK_PREFIXES: dict[str, tuple[str, ...]] = {
    "methodology": (
        "00_brainstorming/",
        "90_delta_tracking/",
        "10_design/Detail_Design_MVP_Core_Artifacts.md",
    ),
}
# sections whose INSTALLED side may legitimately carry extra files:
#   wiki_source_profiles — install is a MERGE (CR-047 NEVER_WRITE): project-local profiles are valid
ONLY_OK_SECTIONS = {"wiki_source_profiles"}
# sections that are NOT dual-tree pairs at all (no product/<key> mirror by design):
#   aiws_wiki — the aiws_meta bundle is GENERATED (registered metas of product docs); the build
#   ships it verbatim FROM .ai-work/wiki_sources/aiws_meta/ (CR-040), there is no product-side
#   copy to drift against. Added with the PAYLOAD_MAP aiws_wiki entry (CR-AIWS-2026-07-031 T4).
#   commands   — `product/commands/` was retired by CR-AIWS-2026-07-025 (core command specs
#                consolidated into domain skills); the agents pack keeps its verb specs
#                pack-internal (payload/agents/commands/ → .ai-work/agents/commands/) and the
#                build actively FORBIDS byte-copies landing in payload/commands/ (CR-031 T3
#                smoke-check). The PAYLOAD_MAP slot stays reserved for install wiring, but there
#                is no product-side mirror to drift against.
#   aiws_wiki_index — index.aiws.jsonl + relations.aiws.jsonl PRE-BUILT from payload/aiws_wiki at
#                build time (build_preset_wiki.py --payload, CR-AIWS-2026-08-064 C5); generated
#                projection, no product-side copy.
SKIP_SECTIONS = {"aiws_wiki", "aiws_wiki_index", "commands"}
# individual only-in-one files that are by-design:
ONLY_OK_FILES = {
    ("skills", "aiws-agent/SKILL.md"),  # build-wired from product/agents (wire_agent_pack_claude, CR-051)
    # CR-AIWS-2026-08-066: install_templates IS a real mirror pair (product/install_templates <->
    # .ai-work/install_templates, both committed) — only VERSION is one-sided: it is GENERATED at
    # package build into payload/, so it exists on an installed side but never under product/.
    ("install_templates", "VERSION"),
}
# ---- Project-local zones INSIDE a shipped section (CR-AIWS-2026-08-091 C1) ----
# A shipped section is not always a pure pair. `agents` installs as ONE tree, but the desk root
# inside it (`agents/task_desks/`, legacy `agents/instances/`) is PROJECT RUNTIME — memory/,
# run_index.jsonl, training/, workspace/completed_runs/** — and has no product-side twin at all.
# Applying pair-semantics there produced 122 `dual_tree_only_in_one` WARNs on the source repo
# and, downstream, `dualtree_link_broken` ERRORs on closed run reports that could be neither
# fixed (history) nor `lint_accept`-ed (agents/ is outside the accept scope) — IR-2026-08-17 G1.
# The list lives HERE, once; `lint_wiki` imports it (a second hand-kept copy would drift from the
# thing it claims to mirror — the exact defect CR-078 C1 closed). Prefixes are relative to the
# section root, POSIX form. DP-091-A(b) — installed-side project-authored files under
# `upstream_requests/` / `change_requests/` — is NOT declared here yet: it stays a PO decision.
PROJECT_LOCAL_PREFIXES: dict[str, tuple[str, ...]] = {
    "agents": ("agents/task_desks/", "agents/instances/"),
}


def project_local_prefixes(section: str) -> tuple[str, ...]:
    """Section-relative POSIX prefixes that are project-local (not part of the pair)."""
    return PROJECT_LOCAL_PREFIXES.get(section, ())


def is_project_local(section: str, rel_posix: str) -> bool:
    """True when `rel_posix` (relative to the section root) lies inside a project-local zone."""
    return any(rel_posix == p.rstrip("/") or rel_posix.startswith(p)
               for p in project_local_prefixes(section))


# pairs whose CONTENT divergence is an accepted, documented exception:
CONTENT_OK = {
    # G-a ruling 2026-07-14 (AIP-EXEC-939): human README diverged on both sides
    # (.ai-work = CR-043/044 wording, product = merge-tool wording) — reconcile via its own
    # doc pass, not a blind overwrite. Remove this entry when that pass lands.
    ("wiki_source_profiles", "README.md"),
}


def iter_pairs(project_root: Path):
    """Yield (section_key, product_side_dir, installed_side_dir) for every shipped pair."""
    for key, dest in PAYLOAD_MAP:
        if key in SKIP_SECTIONS:
            continue
        prod = project_root / PROD_SRC.get(key, "product/" + key)
        yield key, prod, project_root / dest


def _walk(base: Path) -> dict[str, Path]:
    if not base.is_dir():
        return {}
    return {p.relative_to(base).as_posix(): p
            for p in base.rglob("*")
            if p.is_file() and "__pycache__" not in p.parts}


def _norm(data: bytes) -> bytes:
    """CRLF-insensitive view of a file's bytes.

    Kept, NOT removed (CR-AIWS-2026-08-080 §6): it was added deliberately so the gate behaves the
    same on a Windows checkout as on a Linux one. What CR-080 changes is that a pair which differs
    ONLY under this normalisation stops being invisible — see `check()`.
    """
    return data.replace(b"\r\n", b"\n")


def check(project_root: Path) -> list[tuple[str, str, str]]:
    """Compare every dual-tree pair. Returns [(code, message, path), ...]."""
    findings: list[tuple[str, str, str]] = []
    project_root = Path(project_root)
    if not (project_root / "product").is_dir():
        return findings  # installed project — no source tree to compare against

    # CR-AIWS-2026-07-034 T3 (DP-034-1): a NEW PAYLOAD_MAP key must declare what kind of pair it
    # is. Un-declared + no product mirror = a PHANTOM pair: every installed file reads as
    # only-in-one (adding `aiws_wiki` produced 188 such warnings in AIP-945 before it was
    # classified). Warn ONCE per section instead, naming the three ways to classify it.
    for key, dest in PAYLOAD_MAP:
        if key in SKIP_SECTIONS or key in ONLY_OK_SECTIONS:
            continue
        prod = project_root / PROD_SRC.get(key, "product/" + key)
        if not prod.is_dir():
            findings.append((
                "dual_tree_unclassified_section",
                f"PAYLOAD_MAP section '{key}' has no product-side mirror ({prod.name}/) and is not "
                f"classified — declare it: PROD_SRC (mirror lives elsewhere) / ONLY_OK_SECTIONS "
                f"(install-side MERGE) / SKIP_SECTIONS (generated bundle, no product copy). "
                f"Un-classified sections turn every installed file into a phantom only-in-one "
                f"(CR-AIWS-2026-07-034 T3)",
                str(prod)))

    for key, prod, dst in iter_pairs(project_root):
        pf, df = _walk(prod), _walk(dst)
        if not pf and not df:
            continue  # vacated section (e.g. commands post-CR-025) — empty/empty = OK

        for rel in sorted(set(pf) & set(df)):
            if (key, rel) in CONTENT_OK:
                continue
            a = pf[rel].read_bytes()
            b = df[rel].read_bytes()
            if a != b and _norm(a) == _norm(b):
                # CR-AIWS-2026-08-080 C1 (DP-080-A = a) — SAME TEXT, DIFFERENT LINE ENDINGS.
                # Two gates used to disagree about what "drift" means: most CR guardrails say
                # "byte-identical; diff -q before every cp", while this check compares AFTER
                # CRLF normalisation. A pair in this state therefore passed lint while failing the
                # guardrail the CR was closed against — and the AUTOMATED one is the gate people
                # actually trust. Own class, so the message names the one fix that applies (copy
                # the bytes, do not re-save through an editor) instead of sending someone hunting
                # for a content difference that is not there.
                # Measured before wiring (DP-080-B): 0 such pairs out of 552 — this is a gate
                # blind spot being closed, not an incident being cleaned up.
                findings.append((
                    "dual_tree_eol_drift",
                    f"dual-tree pair has identical TEXT but different line endings: section "
                    f"'{key}', file '{rel}' (product CRLF={a.count(bytes([13, 10]))}, installed "
                    f"CRLF={b.count(bytes([13, 10]))}) — `diff -q`/`cmp` calls this a difference "
                    f"and most CR guardrails require byte-identity, so mirror by COPYING BYTES "
                    f"(CR-AIWS-2026-08-080 C1; EOL policy itself is unchanged — CR-AIWS-2026-08-059: "
                    f"authored files keep their original EOL, generated files are LF)",
                    str(df[rel])))
                continue
            if a != b and _norm(a) != _norm(b):
                findings.append((
                    "dual_tree_drift",
                    f"dual-tree pair content differs (EOL-insensitive): section '{key}', "
                    f"file '{rel}' — sync per CR-AIWS-2026-07-030 §2-A (direction: the side "
                    f"carrying the latest applied-CR content wins; ambiguous → PO)",
                    str(dst.joinpath(rel))))

        if key in ONLY_OK_SECTIONS:
            continue
        ok_prefixes = ONLY_OK_PREFIXES.get(key, ())
        for rel in sorted(set(pf) - set(df)):
            if any(rel == p or rel.startswith(p) for p in ok_prefixes):
                continue
            if (key, rel) in ONLY_OK_FILES:
                continue
            findings.append((
                "dual_tree_only_in_one",
                f"section '{key}': product-only file '{rel}' (not a classified exception) — "
                f"mirror it, remove it, or classify it by-design (CR-AIWS-2026-07-030 §2-A0)",
                str(prod.joinpath(rel))))
        for rel in sorted(set(df) - set(pf)):
            if (key, rel) in ONLY_OK_FILES:
                continue
            if is_project_local(key, rel):
                continue  # CR-AIWS-2026-08-091 C1 — desk state etc. is not part of the pair
            findings.append((
                "dual_tree_only_in_one",
                f"section '{key}': installed-only file '{rel}' (not a classified exception) — "
                f"promote it to product/, remove it, or classify it by-design "
                f"(CR-AIWS-2026-07-030 §2-A0)",
                str(dst.joinpath(rel))))
    return findings


def main() -> int:
    root = Path.cwd()
    findings = check(root)
    for code, msg, path in findings:
        print(f"[{code}] {msg}  @ {path}")
    print(f"total: {len(findings)}")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
