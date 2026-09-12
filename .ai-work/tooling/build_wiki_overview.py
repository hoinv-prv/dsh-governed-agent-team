#!/usr/bin/env python3
"""build_wiki_overview.py — Wiki overview synthesis pages (CR-AIWS-2026-07-010).

Deterministic PROJECTION of index.jsonl (+ index.aiws.jsonl) + relations.jsonl into
category overview pages under .ai-work/wiki/overview/ — so AI (and HUMAN) can see WHAT
the wiki contains and HOW to search it, without drifting hand-maintained lists.

Default-on pages (DP-912-6c): contents (#1) · search (#3) · health (#5).
Every page carries a GENERATED footer (fingerprint + body-hash + timestamp):
  - hand-editing a generated page  → lint ERROR  `overview_hand_edit`
  - index changed but page not regenerated → lint WARN `overview_fingerprint_stale`
Two-clause rule (DP-912-6a): regeneration of THESE deterministic pages is CR-free
maintenance (review happened at the input layer — metas/index are governance-gated);
any LLM-authored narrative page stays HUMAN-gated content and is NOT emitted here.

Multi-system (rule #12): in a multi_system project you MUST pass --system <id> or
--all-systems; default-on pages emit PER SYSTEM (no cross-system aggregate bleed).

Registration: each page is registered as a wiki source (source_type overview_page,
knowledge_targets navigation) via build_wiki_source_meta + a FINAL index rebuild —
the refresh-hook contract (Appendix G step: rebuild index/relations → regenerate
overview → final index rebuild).

Usage:
    py .ai-work/tooling/build_wiki_overview.py --system aiws
    py .ai-work/tooling/build_wiki_overview.py --all-systems          # every system + common
    py .ai-work/tooling/build_wiki_overview.py --system demo --pages contents,health
    py .ai-work/tooling/build_wiki_overview.py --system aiws --no-register   # emit only
"""
from __future__ import annotations

import argparse
import datetime
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (  # noqa: E402
    OVERVIEW_SOURCE_TYPE,
    all_index_paths,
    find_ai_work_root,
    in_system,
    overview_body_hash,
    overview_fingerprint,
    read_jsonl,
    read_project_config,
    read_text,
    resolve_relations_paths,
    write_text,
)

PAGES_DEFAULT = "contents,search,health"
PAGE_TITLES = {
    "contents": "WIKI_CONTENTS_OVERVIEW",
    "search": "WIKI_SEARCH_GUIDE",
    "health": "WIKI_HEALTH",
}


def _load_records(wiki_sources: Path) -> list[dict]:
    records: list[dict] = []
    for p in all_index_paths(wiki_sources):   # CR-051 T3 (Rule 6): one source of truth, not a 4th copy
        records.extend(read_jsonl(p))
    return records


def _is_chunk_child(r: dict) -> bool:
    return bool(str(r.get("section_lines", "")).strip())


def _children_counts(records: list[dict]) -> dict[str, int]:
    out: dict[str, int] = {}
    for r in records:
        if _is_chunk_child(r):
            pid = r.get("source_id", "").rsplit("-SEC-", 1)[0]
            out[pid] = out.get(pid, 0) + 1
    return out


def _lens_presets(ai_work: Path) -> list[dict]:
    """Minimal stdlib parse of task_lens_presets/starter_lenses.yml → [{lens_id, intent,
    relevant_source_types}] (enough for the search-guide table; tolerant of absence)."""
    p = ai_work / "wiki" / "task_lens_presets" / "starter_lenses.yml"
    if not p.exists():
        return []
    out: list[dict] = []
    cur: dict = {}
    for line in read_text(p).splitlines():
        s = line.strip()
        if s.startswith("- lens_id:"):
            if cur.get("lens_id"):
                out.append(cur)
            cur = {"lens_id": s.split(":", 1)[1].strip()}
        elif s.startswith("intent:") and cur:
            cur["intent"] = s.split(":", 1)[1].strip()
        elif s.startswith("relevant_source_types:") and cur:
            inline = s.split(":", 1)[1].strip()
            if inline.startswith("[") and inline.endswith("]"):
                cur["types"] = [v.strip() for v in inline[1:-1].split(",") if v.strip()]
    if cur.get("lens_id"):
        out.append(cur)
    return out


def _footer(fp: str, body_hash_placeholder: str = "@BODYHASH@") -> list[str]:
    now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    return [
        "",
        "<!-- GENERATED page — do not hand-edit; regenerate via "
        "`py .ai-work/tooling/build_wiki_overview.py` (/aiws-wiki build-overview). "
        "CR-AIWS-2026-07-010; hand-edit = lint ERROR overview_hand_edit. -->",
        f"<!-- GENERATED-FINGERPRINT: {fp} -->",
        f"<!-- GENERATED-BODY-HASH: {body_hash_placeholder} -->",
        f"<!-- GENERATED-AT: {now} -->",
        "",
    ]


def _finish_page(lines: list[str], fp: str) -> str:
    text = "\n".join(lines + _footer(fp))
    return text.replace("@BODYHASH@", overview_body_hash(text))


def _page_contents(recs: list[dict], sys_label: str, fp: str) -> str:
    kids = _children_counts(recs)
    tops = [r for r in recs if not _is_chunk_child(r)
            and r.get("source_type") != OVERVIEW_SOURCE_TYPE]
    lines = [f"# Wiki Contents Overview — {sys_label}", "",
             f"Registered sources: **{len(tops)}** (+{sum(kids.values())} chunked section metas). "
             "Đây là PROJECTION của wiki index — trang này trả lời \"wiki chứa gì\"; cách tìm → "
             "WIKI_SEARCH_GUIDE. Mở meta: `lookup_wiki_source.py --mode id <source_id>`.", ""]
    by_type: dict[str, list[dict]] = {}
    for r in tops:
        by_type.setdefault(r.get("source_type", "(none)"), []).append(r)
    for st in sorted(by_type):
        group = sorted(by_type[st], key=lambda r: r.get("source_id", ""))
        lines.append(f"## {st} ({len(group)})")
        for r in group:
            summ = (r.get("summary_short", "") or "").replace("\n", " ").strip()[:100]
            kid = kids.get(r.get("source_id", ""), 0)
            kid_tag = f" *(+{kid} sections)*" if kid else ""
            lines.append(f"- **{r.get('source_id','')}**{kid_tag} — {r.get('title','')}"
                         + (f" — {summ}" if summ else ""))
        lines.append("")
    return _finish_page(lines, fp)


def _page_search(recs: list[dict], sys_label: str, system_flag: str,
                 lenses: list[dict], fp: str) -> str:
    tops = [r for r in recs if not _is_chunk_child(r)
            and r.get("source_type") != OVERVIEW_SOURCE_TYPE]
    type_counts: dict[str, int] = {}
    for r in tops:
        type_counts[r.get("source_type", "")] = type_counts.get(r.get("source_type", ""), 0) + 1
    lines = [f"# Wiki Search Guide — {sys_label}", "",
             "## Cách tìm (escalation chain)",
             f"1. `lookup_wiki_source.py --query <kw> {system_flag} --limit 5` (lexical mặc định)",
             "2. Miss/yếu → `--mode tokens` (per-token, fold dấu VI, aliases tự expand)",
             "3. Concept khác từ vựng / top score <15 → `--mode catalog` (đọc-chọn slim catalog)",
             "4. Vẫn miss → raw search (CR-052 gated — cần authorization; xem "
             "document_search_guidelines)",
             "",
             "Budget (E4): plan 3–5 queries, ~1 call/input; vượt ~2× inputs → BẮT BUỘC capture "
             "`retrieval_improvement` (MP1–MP7). Doc-set theo task: `build_reading_kit.py "
             f"--query \"<task>\" {system_flag}`.",
             "",
             "## By task type (từ Task Lens presets × types hiện có)",
             "| Lens | Intent | Source types có trong wiki này |",
             "|---|---|---|"]
    for ln in lenses:
        avail = [f"{t} ({type_counts[t]})" for t in ln.get("types", []) if type_counts.get(t)]
        if not avail:
            continue
        intent = (ln.get("intent", "") or "")[:90]
        lines.append(f"| {ln.get('lens_id','')} | {intent} | {', '.join(avail)} |")
    lines += ["",
              "## Types & counts",
              "| source_type | entries |", "|---|---|"]
    for st in sorted(type_counts):
        lines.append(f"| {st} | {type_counts[st]} |")
    lines.append("")
    return _finish_page(lines, fp)


def _page_health(recs: list[dict], relations_raw: str, sys_label: str, fp: str) -> str:
    tops = [r for r in recs if not _is_chunk_child(r)
            and r.get("source_type") != OVERVIEW_SOURCE_TYPE]
    kids = _children_counts(recs)
    n = len(tops)
    by = lambda f: sorted(  # noqa: E731
        {(r.get(f) or "(unset)") for r in tops},
        key=lambda v: -sum(1 for r in tops if (r.get(f) or "(unset)") == v))
    cnt = lambda f, v: sum(1 for r in tops if (r.get(f) or "(unset)") == v)  # noqa: E731
    edge_ids: set = set()
    for ln in relations_raw.splitlines():
        for m in re.finditer(r'"(?:from|to|source_id|target_id)"\s*:\s*"([^"]+)"', ln):
            edge_ids.add(m.group(1))
    with_rel = sum(1 for r in tops if r.get("source_id") in edge_ids)
    lines = [f"# Wiki Health — {sys_label}", "",
             f"- Entries: **{n}** top-level (+{sum(kids.values())} section metas, "
             f"{len(kids)} chunked parents)",
             f"- Relations coverage: **{with_rel}/{n}** top-level entries có ≥1 typed edge "
             f"({(100 * with_rel // n) if n else 0}%) — ưu tiên enrich (Relations Enrichment CR)",
             ""]
    for field, label in (("status", "Status"),
                         ("source_representation_status", "Representation"),
                         ("freshness_status", "Freshness")):
        vals = ", ".join(f"{v}={cnt(field, v)}" for v in by(field))
        lines.append(f"- {label}: {vals}")
    lines += ["",
              "Regenerate sau mỗi index/relations rebuild — fingerprint mismatch = lint WARN "
              "`overview_fingerprint_stale`.", ""]
    return _finish_page(lines, fp)


def main() -> int:
    p = argparse.ArgumentParser(description="Build wiki overview pages (CR-AIWS-2026-07-010)")
    p.add_argument("--pages", default=PAGES_DEFAULT,
                   help=f"Comma-list: contents,search,health (default: {PAGES_DEFAULT})")
    p.add_argument("--system", default=None, metavar="ID")
    p.add_argument("--all-systems", dest="all_systems", action="store_true", default=False)
    p.add_argument("--out-dir", default=None)
    p.add_argument("--no-register", dest="register", action="store_false", default=True,
                   help="Emit pages only (skip meta registration + final index rebuild).")
    ns = p.parse_args()

    project_root = find_ai_work_root(Path.cwd())
    ai_work = project_root / ".ai-work"
    wiki_sources = ai_work / "wiki_sources"
    out_dir = Path(ns.out_dir).resolve() if ns.out_dir else ai_work / "wiki" / "overview"
    out_dir.mkdir(parents=True, exist_ok=True)

    cfg = read_project_config(ai_work)
    systems: list[str | None]
    if cfg.get("multi_system"):
        if ns.all_systems:
            systems = list(cfg.get("systems") or []) or [None]
        elif ns.system:
            if cfg.get("systems") and ns.system not in cfg["systems"]:
                print(f"error: --system {ns.system!r} not in {cfg['systems']}", file=sys.stderr)
                return 2
            systems = [ns.system]
        else:
            print("error: multi_system project — pass --system <id> or --all-systems "
                  "(per-system pages; no cross-system aggregate — rule #12).", file=sys.stderr)
            return 2
    else:
        systems = [None]

    all_records = _load_records(wiki_sources)
    relations_raw = ""
    # CR-AIWS-2026-08-064 C8: project + shipped aiws preset (THE resolver; collapse when absent)
    for rel_path in resolve_relations_paths(wiki_sources, {"project", "aiws"}):
        relations_raw += read_text(rel_path)
    lenses = _lens_presets(ai_work)
    pages = [x.strip() for x in ns.pages.split(",") if x.strip()]
    builder = Path(__file__).resolve().parent / "build_wiki_source_meta.py"
    emitted: list[tuple[Path, str, str | None]] = []

    for system in systems:
        recs = [r for r in all_records if in_system(r, system)] if system else all_records
        fp = overview_fingerprint(recs, relations_raw)
        sys_label = system or ("all systems" if not cfg.get("multi_system") else "common")
        suffix = f"_{system}" if system else ""
        sflag = f"--system {system}" if system else ""
        for page in pages:
            if page == "contents":
                text = _page_contents(recs, sys_label, fp)
            elif page == "search":
                text = _page_search(recs, sys_label, sflag, lenses, fp)
            elif page == "health":
                text = _page_health(recs, relations_raw, sys_label, fp)
            else:
                print(f"warn: unknown page '{page}' — skipped "
                      "(narrative pages are HUMAN-gated, not emitted here)", file=sys.stderr)
                continue
            fpath = out_dir / f"{PAGE_TITLES[page]}{suffix}.md"
            write_text(fpath, text)
            emitted.append((fpath, page, system))
            print(f"overview page: {fpath}")

    if ns.register and emitted:
        meta_dir = wiki_sources / "meta" / "overview"
        meta_dir.mkdir(parents=True, exist_ok=True)
        for fpath, page, system in emitted:
            sid = f"SRC-OVERVIEW-{page.upper()}" + (f"-{system.upper()}" if system else "")
            cmd = [sys.executable, str(builder),
                   "--artifact", str(fpath), "--source-id", sid,
                   "--source-type", OVERVIEW_SOURCE_TYPE,
                   "--profile", str(wiki_sources / "profiles" / "overview_pages.yml"),
                   "--title", f"Overview — {PAGE_TITLES[page]}" + (f" ({system})" if system else ""),
                   "--out", str(meta_dir / f"{sid}.md"),
                   "--mode", "refresh", "--no-related-sources", "--no-chunk",
                   "--knowledge-targets", "navigation",
                   # CR-AIWS-2026-08-100: trang overview do MÁY sinh, không có curation để
                   # người duyệt — staleness của nó đã có `overview_fingerprint_stale` canh.
                   # Không khai cờ này thì rơi vào default `needs_review` của build_wiki_source_meta
                   # và lint_wiki cảnh báo mỗi lần regenerate, mà sửa tay thì lần sau bị ghi đè.
                   "--maintenance-status", "active",
                   # Pin THREE distinct discriminative compounds (self-test gates the first 3 keys):
                   # key #1 case-collides with the page H1 title and is deduped, so 2 pins alone left a
                   # generic body-frequency single word ('wiki') at position 3. The 3rd pin keeps the
                   # top-3 all discriminative so the HEALTH/CONTENTS/SEARCH page self-surfaces.
                   "--lookup-keys",
                   f"{PAGE_TITLES[page].replace('_', ' ').lower()}"
                   + (f" {system}" if system else "")
                   + f",wiki overview {page}" + (f" {system}" if system else "")
                   + f",{PAGE_TITLES[page].replace('_', ' ').lower()} overview page"
                   + (f" {system}" if system else ""),
                   ]
            if system:
                cmd += ["--system", system]
            elif cfg.get("multi_system"):
                cmd += ["--common"]
            r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
            if r.returncode != 0:
                print(f"error registering {sid}: {r.stderr or r.stdout}", file=sys.stderr)
                return 2
            print(f"registered: {sid}")
        # Final index rebuild — the refresh-hook contract (pages join the index AFTER emission;
        # their records are EXCLUDED from the fingerprint, so this does not self-invalidate).
        r = subprocess.run([sys.executable,
                            str(Path(__file__).resolve().parent / "build_wiki_source_index.py"),
                            "--scope", "project"],
                           capture_output=True, text=True, encoding="utf-8")
        print((r.stdout or "").strip().splitlines()[0] if r.stdout else "index rebuilt")
        if r.returncode != 0:
            print(f"error: final index rebuild failed: {r.stderr}", file=sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
