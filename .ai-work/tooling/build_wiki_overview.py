#!/usr/bin/env python3
"""build_wiki_overview.py — Wiki overview synthesis pages (CR-AIWS-2026-07-010).

Deterministic PROJECTION of index.jsonl (+ index.aiws.jsonl) + relations.jsonl into
category overview pages under .ai-work/wiki/overview/ — so AI (and HUMAN) can see WHAT
the wiki contains and HOW to search it, without drifting hand-maintained lists.

Default-on pages (DP-912-6c): contents (#1) · search (#3) · health (#5).
Opt-in page (CR-AIWS-2026-09-003 C1): `nav` — pass `--pages nav`. It is deliberately not
default-on so an existing install does not silently gain a page on its next refresh.
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
    py .ai-work/tooling/build_wiki_overview.py --system aiws --pages nav     # navigation page (opt-in)
"""
from __future__ import annotations

import argparse
import collections
import datetime
import json
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
    # CR-AIWS-2026-09-003 C1. OPT-IN (DP-003-A): deliberately NOT in PAGES_DEFAULT, so an
    # existing install does not start emitting + registering a new page on its next refresh.
    "nav": "WIKI_NAV",
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


# ============================================================================
# Page kind `nav` (CR-AIWS-2026-09-003 C1) — the navigation page.
#
# WHY it exists: a "find me the reference docs for task X" run cost 11.3 LLM turns measured over
# 16 clean subagent contexts (AIP-EXEC-1156). Roughly half of those turns were spent LOCATING
# things, not reading them. A page that names every registered source with its path, and that
# states its own coverage, lets the agent answer "where is it / is it there at all" in ONE read.
# Measured: demo 11.0 -> 4.9 turns; aiws 12.0 -> 7.8 with the 2-level tree.
#
# WHY three shapes: one shape does not fit three corpora. The shape is picked from the corpus, and
# the thresholds are constants HERE (never inline) so tuning them needs no code archaeology.
# ============================================================================

# Shape thresholds (CR-AIWS-2026-09-003 §6: constants at the top, not scattered in the code).
NAV_RICH_MAX = 80          # RICH needs an F-code convention AND a corpus this small
NAV_FLAT_MAX = 60          # <= this, with no F-code convention -> one flat page
NAV_SPLIT_OVER = 40        # a tree branch holding more than this is a split candidate
NAV_BRANCH_CHAR_BUDGET = 8000   # ... and so is one estimated wider than this

_NAV_NOTE = ("Trang này là **FALLBACK**, không phải bước đầu: `lookup_wiki_source.py` vẫn đi "
             "TRƯỚC. Chỉ dùng trang này khi lookup ra 0 kết quả / kết quả không khớp / match "
             "fragile — hoặc khi câu hỏi cần LIỆT KÊ ĐỦ. Khi dùng thì **`grep` trang, đừng `cat`** "
             "(grep rẻ hơn ~75%). Path lấy từ wiki index — KHÔNG cần `ls` kiểm tra tồn tại. Trang "
             "là ĐỊNH TUYẾN, không phải bằng chứng — mở artifact khi cần nội dung thật, và đọc "
             "ĐOẠN chứ đừng `cat` cả file.")

_FCODE_RE = re.compile(
    r'^(F\d{2,3})\s+(.+?)\s+(requirement definition|basic design|detail design)\s*$', re.I)
_DOC_COLS = [("requirement_definition", "RD"), ("basic_design", "BD"), ("detail_design", "DD")]
_STANDARD_TYPES = ("process_template", "process_guideline")


class NavCoverageError(RuntimeError):
    """A nav page failed to place every source of its system.

    This is fatal ON PURPOSE and is NOT an `assert` (asserts vanish under `python -O`). The page
    tells its reader "a document that is not named here is NOT in the registered wiki", and
    `operations/lookup.md` lets an agent STOP on that answer instead of escalating to a raw search.
    A page that silently dropped entries would make that sentence a lie, which is worse than no
    page at all.
    """


def _nav_tops(recs: list[dict]) -> list[dict]:
    """The entries a nav page lists: real documents only.

    Chunk children are excerpts of a parent that is listed already (37 duplicate rows for ONE spec
    in the first PoC run), and overview pages are the navigation layer itself.
    """
    return [r for r in recs
            if not _is_chunk_child(r) and r.get("source_type") != OVERVIEW_SOURCE_TYPE]


def _nav_short(t: str | None, n: int) -> str:
    t = re.sub(r"\s+", " ", t or "").strip()
    return t if len(t) <= n else t[: n - 1].rstrip() + "…"


def _nav_fcode(r: dict) -> tuple[str, str] | None:
    for k in r.get("lookup_keys") or []:
        m = _FCODE_RE.match(k)
        if m:
            return m.group(1).upper(), m.group(2)
    return None


def _nav_detect_fcode(tops: list[dict]) -> bool:
    """RICH (function × doc-type) is worth it only when the corpus really follows an F-code naming
    convention across several functions and doc types. Hard-coding that shape for every corpus did
    not generalize — it was measured on three corpora and fit exactly one."""
    rows: dict[str, set] = {}
    for r in tops:
        if r.get("source_type") in dict(_DOC_COLS):
            fk = _nav_fcode(r)
            if fk:
                rows.setdefault(fk[0], set()).add(r["source_type"])
    return len(rows) >= 3 and sum(1 for v in rows.values() if len(v) >= 2) >= 2


def _nav_relations(relations_raw: str) -> list[dict]:
    edges = []
    for line in relations_raw.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            edges.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return edges


def _nav_segs(r: dict) -> list[str]:
    """Directory segments used to group an entry. Object nodes carry no real path."""
    loc = r.get("artifact_locator") or ""
    if loc.startswith("__"):
        return ["(object nodes)", r.get("source_type", "")]
    return loc.split("/")[:-1] or ["(project root)"]


def _nav_est_chars(items: list[dict]) -> int:
    """Estimated rendered width of a branch. Splitting by ENTRY COUNT alone was measured to leave
    branches at 11.1k and 19.8k chars, because path+summary length varies wildly."""
    return sum(len(r.get("source_id", "")) + len(r.get("artifact_locator", ""))
               + len(r.get("summary_short") or "") + 20 for r in items)


def _nav_coverage(recs: list[dict], tops: list[dict], sys_label: str) -> str:
    """The coverage sentence. `operations/lookup.md` lets an agent conclude "not on this page =
    not in the registered wiki" and stop there, so the page has to state precisely what N/N counts.
    Saying "227/227 registered
    sources" while the index holds 266 entries for that system would be false: 36 of them are
    chunk EXCERPTS of documents listed here, and 3 are overview pages (this navigation layer).
    Both are folded on purpose; the sentence says so rather than hiding the arithmetic.
    """
    chunks = sum(1 for r in recs if _is_chunk_child(r))
    pages = sum(1 for r in recs if r.get("source_type") == OVERVIEW_SOURCE_TYPE)
    folded = []
    if chunks:
        folded.append(f"{chunks} chunk con đã gộp về tài liệu mẹ")
    if pages:
        folded.append(f"{pages} trang overview/nav")
    tail = (" (" + "; ".join(folded) + " — không liệt kê riêng)") if folded else ""
    return (f"Phủ **{len(tops)}/{len(tops)}** tài liệu đã đăng ký của system {sys_label}"
            f"{tail}. Một tài liệu không có tên ở trang này = **KHÔNG có trong wiki đã đăng ký**.")


def _page_nav_rich(recs: list[dict], tops: list[dict], sys_label: str,
                   relations_raw: str, fp: str) -> str:
    """Small corpus WITH an F-code convention: function × doc-type table + foundation docs +
    reference standards + a relation-type graph summary + the coverage gaps."""
    rows: dict[str, dict] = {}
    fname: dict[str, str] = {}
    found: dict[str, list] = {}
    used: set = set()
    for r in tops:
        st = r.get("source_type")
        fk = _nav_fcode(r) if st in dict(_DOC_COLS) else None
        if fk:
            rows.setdefault(fk[0], {})[st] = r
            fname[fk[0]] = fk[1]
            used.add(r["source_id"])
        else:
            found.setdefault(st, []).append(r)

    def common_dir(st):
        ds = {r["artifact_locator"].rsplit("/", 1)[0]
              for row in rows.values() for t, r in row.items()
              if t == st and not r["artifact_locator"].startswith("__")}
        return ds.pop() + "/" if len(ds) == 1 else ""
    dirs = {st: common_dir(st) for st, _ in _DOC_COLS}

    def cell(r, st):
        if not r:
            return "— (chưa có)"
        p = r["artifact_locator"]
        if p.startswith("__"):
            return f"`{r['source_id']}`"
        d = dirs[st]
        return f"`{r['source_id']}` · {p[len(d):] if d and p.startswith(d) else p}"

    L = [f"# Wiki Navigation — {sys_label}", "", f"> {_NAV_NOTE}", ""]
    L.append("## 1. Tree — function × loại tài liệu")
    dirline = " · ".join(f"{lab} = `{dirs[st]}`" for st, lab in _DOC_COLS if dirs[st])
    if dirline:
        L += [dirline, ""]
    L.append("| F | Function | " + " | ".join(lab for _, lab in _DOC_COLS) + " |")
    L.append("|---|---|" + "---|" * len(_DOC_COLS))
    for f in sorted(rows):
        L.append(f"| {f} | {fname[f]} | "
                 + " | ".join(cell(rows[f].get(st), st) for st, _ in _DOC_COLS) + " |")
    L.append("")

    L.append("## 2. Tài liệu nền — dùng chung, không gắn một function cụ thể")
    for st, _ in _DOC_COLS:
        for r in found.pop(st, []):
            used.add(r["source_id"])
            L.append(f"- **{r['source_type']}** `{r['source_id']}` · {r['artifact_locator']} — "
                     f"{_nav_short(r.get('summary_short'), 110)}")
    L.append("")

    L.append("## 3. Chuẩn tham chiếu — template · guideline · checklist")
    for st in _STANDARD_TYPES:
        for r in sorted(found.pop(st, []), key=lambda r: r["source_id"]):
            used.add(r["source_id"])
            L.append(f"- `{r['source_id']}` ({r['source_type']}) · {r['artifact_locator']} — "
                     f"{_nav_short(r.get('summary_short'), 120)}")
    L.append("")

    L.append("## 4. Graph — loại quan hệ đã khai trong wiki (giữa các tài liệu ở mục 1)")
    id_to_fdoc = {r["source_id"]: (f, st) for f, row in rows.items() for st, r in row.items()}
    pat: dict = {}
    cross = 0
    for e in _nav_relations(relations_raw):
        s_, t_ = e.get("source_ref"), e.get("target_ref")
        if s_ not in id_to_fdoc or t_ not in id_to_fdoc:
            continue
        fs, ss = id_to_fdoc[s_]
        ft, st_ = id_to_fdoc[t_]
        if fs != ft:
            cross += 1
        key = (dict(_DOC_COLS)[ss], e.get("relationship_type"), dict(_DOC_COLS)[st_])
        pat[key] = pat.get(key, 0) + 1
    for (a, rel, b), n in sorted(pat.items(), key=lambda kv: -kv[1]):
        L.append(f"- {a} —`{rel}`→ {b}  ×{n}")
    L.append(f"- **Edge chéo giữa hai function khác nhau: {cross}.**"
             + (" Wiki KHÔNG khai quan hệ giữa các function khác nhau — quan hệ đó (nếu có) chỉ "
                "nằm trong thân tài liệu." if cross == 0 else ""))
    L.append("")

    L.append("## 5. Còn lại trong wiki (chưa xếp vào mục 1–3, KHÔNG phải mọi thứ đều liên quan)")
    rest = sorted((r for st, lst in found.items() for r in lst), key=lambda r: r["source_id"])
    for r in rest[:60]:
        L.append(f"- `{r['source_id']}` ({r['source_type']}) · {r['artifact_locator']} — "
                 f"{_nav_short(r.get('summary_short'), 90)}")
    if len(rest) > 60:
        L.append(f"- … +{len(rest) - 60} nguồn khác (loại: "
                 + ", ".join(sorted({r['source_type'] for r in rest[60:]})) + ")")
    for r in rest:
        used.add(r["source_id"])
    L.append("")

    missing_f = {st: [f for f in sorted(rows) if st not in rows[f]] for st, _ in _DOC_COLS}
    L.append("## 6. KHÔNG có trong wiki")
    for st, lab in _DOC_COLS:
        if missing_f[st]:
            L.append(f"- {lab} chưa có cho: {', '.join(missing_f[st])}.")
    left = [r["source_id"] for r in tops if r["source_id"] not in used]
    if left:
        raise NavCoverageError("nav(rich): entries not placed: " + ", ".join(left))
    L.append("- " + _nav_coverage(recs, tops, sys_label)
             + " Mục 1, 2, 3 và 5 cộng lại là toàn bộ danh sách đó.")
    L.append("")
    return _finish_page(L, fp)


def _page_nav_flat(recs: list[dict], tops: list[dict], sys_label: str, fp: str) -> str:
    """Small/medium corpus WITHOUT an F-code convention: group by directory (or object-node type),
    one section per group, a path on every line."""
    groups: dict[str, list] = {}
    for r in tops:
        groups.setdefault("/".join(_nav_segs(r)), []).append(r)
    L = [f"# Wiki Navigation — {sys_label}", "", f"> {_NAV_NOTE}", "",
         _nav_coverage(recs, tops, sys_label), ""]
    placed = 0
    for key in sorted(groups):
        items = sorted(groups[key], key=lambda r: (r["artifact_locator"], r["source_id"]))
        types = ", ".join(f"{t}×{n}" for t, n in
                          collections.Counter(r["source_type"] for r in items).most_common())
        L.append(f"## `{key}` — {len(items)} source ({types})")
        for r in items:
            L.append(f"- `{r['source_id']}` · {r['artifact_locator']} — "
                     f"{_nav_short(r.get('summary_short'), 130)}")
        L.append("")
        placed += len(items)
    if placed != len(tops):
        raise NavCoverageError(f"nav(flat): placed {placed} of {len(tops)}")
    return _finish_page(L, fp)


def _page_nav_tree(recs: list[dict], tops: list[dict], sys_label: str,
                   suffix: str, fp: str) -> list[tuple[str, str]]:
    """Large corpus: a 2-level tree — root sitemap (names only, per branch) + one branch page per
    group. Branch size is capped by an ESTIMATED CHAR BUDGET, not by entry count."""

    def group(items, depth):
        g = collections.defaultdict(list)
        for r in items:
            g["/".join(_nav_segs(r)[:depth])].append(r)
        return g

    branches: dict[str, list] = {}

    def place(items, depth):
        for key, its in group(items, depth).items():
            deeper = any(len(_nav_segs(r)) > depth for r in its)
            over = len(its) > NAV_SPLIT_OVER or _nav_est_chars(its) > NAV_BRANCH_CHAR_BUDGET
            if over and deeper and depth < 6:
                place(its, depth + 1)
            else:
                branches.setdefault(key, []).extend(its)
    place(tops, 2)

    # Fold the tiny branches together so the root sitemap does not become a list of 1-item pages.
    small = [k for k, v in branches.items() if len(v) < 5]
    merged: dict[str, list] = collections.defaultdict(list)
    for k in small:
        merged[k.split("/")[0] + "/(nhánh nhỏ gộp)"].extend(branches.pop(k))
    for k in [k for k, v in merged.items() if len(v) < 5]:
        merged["(khác)/(nhánh nhỏ gộp)"].extend(merged.pop(k))
    branches.update(merged)

    def sub_chunks(items):
        """A directory-FLAT branch (61 specs in one folder) cannot be split further by depth —
        every entry has the same prefix. Fall back to alphabetical slices sized to the budget."""
        if _nav_est_chars(items) <= NAV_BRANCH_CHAR_BUDGET or len(items) <= 5:
            return [items]
        per = max(5, int(len(items) * NAV_BRANCH_CHAR_BUDGET / max(1, _nav_est_chars(items))))
        return [items[j:j + per] for j in range(0, len(items), per)]

    nav_name = PAGE_TITLES["nav"]
    out: list[tuple[str, str]] = []
    R = [f"# Wiki Navigation Tree — {sys_label} (ROOT)", "", f"> {_NAV_NOTE}",
         f"> Cây 2 tầng. {_nav_coverage(recs, tops, sys_label)}", ""]
    total = 0
    for i, (key, items) in enumerate(sorted(branches.items()), 1):
        items = sorted(items, key=lambda r: (r["artifact_locator"], r["source_id"]))
        chunks = sub_chunks(items)
        fns = [f"{nav_name}{suffix}_{i:02d}{chr(97 + c) if len(chunks) > 1 else ''}.md"
               for c in range(len(chunks))]
        types = ", ".join(f"{t}×{n}" for t, n in
                          collections.Counter(r["source_type"] for r in items).most_common())
        links = (", ".join(f"[{c + 1}]({fn})" for c, fn in enumerate(fns))
                 if len(chunks) > 1 else f"[{fns[0]}]({fns[0]})")
        R.append(f"## {i:02d}. `{key}` — {len(items)} source → {links}")
        R.append(f"_{types}_" + (f" — chia {len(chunks)} trang vì vượt ngân sách ký tự một trang"
                                 if len(chunks) > 1 else ""))
        names = (r["title"] if r["artifact_locator"].startswith("__")
                 else r["artifact_locator"].rsplit("/", 1)[-1].removesuffix(".md") for r in items)
        R.append(" · ".join(names))
        R.append("")
        for c, (chunk, fn) in enumerate(zip(chunks, fns)):
            part = f" (phần {c + 1}/{len(chunks)})" if len(chunks) > 1 else ""
            B = [f"# Wiki Navigation — {sys_label} · nhánh {i:02d}{part}: `{key}` "
                 f"({len(chunk)}/{len(items)} source)", "",
                 f"> Trang nhánh của [{nav_name}{suffix}.md]({nav_name}{suffix}.md). {_NAV_NOTE}", ""]
            for r in chunk:
                B.append(f"- `{r['source_id']}` · {r['artifact_locator']} — "
                         f"{_nav_short(r.get('summary_short'), 140)}")
            out.append((fn, _finish_page(B, fp)))
        total += len(items)
    if total != len(tops):
        raise NavCoverageError(f"nav(tree): placed {total} of {len(tops)}")
    out.insert(0, (f"{nav_name}{suffix}.md", _finish_page(R, fp)))
    return out


def _page_nav(recs: list[dict], sys_label: str, relations_raw: str,
              suffix: str, fp: str) -> list[tuple[str, str]]:
    """Pick a shape for this system's corpus. Returns [(filename, text), ...]; index 0 is ALWAYS
    the entry page (the one that gets registered — CR-AIWS-2026-09-003 DP-003-B = root only)."""
    nav_name = PAGE_TITLES["nav"]
    tops = _nav_tops(recs)
    if not tops:
        return [(f"{nav_name}{suffix}.md", _finish_page(
            [f"# Wiki Navigation — {sys_label}", "", f"> {_NAV_NOTE}", "",
             "(no sources registered)"], fp))]
    if _nav_detect_fcode(tops) and len(tops) <= NAV_RICH_MAX:
        return [(f"{nav_name}{suffix}.md",
                 _page_nav_rich(recs, tops, sys_label, relations_raw, fp))]
    if len(tops) <= NAV_FLAT_MAX:
        return [(f"{nav_name}{suffix}.md", _page_nav_flat(recs, tops, sys_label, fp))]
    return _page_nav_tree(recs, tops, sys_label, suffix, fp)


def main() -> int:
    p = argparse.ArgumentParser(description="Build wiki overview pages (CR-AIWS-2026-07-010)")
    p.add_argument("--pages", default=PAGES_DEFAULT,
                   help=f"Comma-list: contents,search,health,nav (default: {PAGES_DEFAULT}). "
                        "`nav` is OPT-IN (CR-AIWS-2026-09-003): a navigation page that names every "
                        "registered source with its path and states its own coverage. It picks its "
                        "shape from the corpus and may emit a ROOT page plus branch pages.")
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
            # A page kind yields [(filename, text), ...]. Only `nav` uses more than one file, and
            # for it index 0 is the ROOT (see _page_nav) — the entry the reader starts from.
            if page == "contents":
                files = [(f"{PAGE_TITLES[page]}{suffix}.md", _page_contents(recs, sys_label, fp))]
            elif page == "search":
                files = [(f"{PAGE_TITLES[page]}{suffix}.md",
                          _page_search(recs, sys_label, sflag, lenses, fp))]
            elif page == "health":
                files = [(f"{PAGE_TITLES[page]}{suffix}.md",
                          _page_health(recs, relations_raw, sys_label, fp))]
            elif page == "nav":
                files = _page_nav(recs, sys_label, relations_raw, suffix, fp)
            else:
                print(f"warn: unknown page '{page}' — skipped "
                      "(narrative pages are HUMAN-gated, not emitted here)", file=sys.stderr)
                continue
            for n, (fname, text) in enumerate(files):
                fpath = out_dir / fname
                write_text(fpath, text)
                # DP-003-B = (a): register the ROOT only. Registering every branch would add ~19
                # entries to a 262-entry index (+7.3%) — inflating the very thing this CR shrinks
                # — and `sid` below is unique per (page, system), so N branches would collide on
                # ONE source_id and overwrite each other. Accepted debt: branch pages are outside
                # `_lint_overview_page`, which only walks REGISTERED metas (CAP-1157-01).
                if n == 0:
                    emitted.append((fpath, page, system))
                print(f"overview page: {fpath}" + ("" if n == 0 else "   (branch, not registered)"))

    if ns.register and emitted:
        meta_dir = wiki_sources / "meta" / "overview"
        meta_dir.mkdir(parents=True, exist_ok=True)
        for fpath, page, system in emitted:
            sid = f"SRC-OVERVIEW-{page.upper()}" + (f"-{system.upper()}" if system else "")
            # CR-AIWS-2026-09-003: the nav ROOT of a tree-shaped corpus is a sitemap, so the
            # auto-extractor's "first prose line" lands on a branch's type tally ("_process_
            # guideline×2_") and lint fires `meta_summary_degenerate` the moment the page is
            # registered. State what the page IS instead of letting a heuristic guess.
            nav_summary = (
                f"Trang điều hướng wiki của system {system or 'project'}: liệt kê mọi tài liệu đã "
                "đăng ký kèm artifact path và tự khai độ phủ. Dùng làm FALLBACK khi "
                "lookup_wiki_source.py không đủ, không phải bước đầu tiên "
                "(aiws-wiki/operations/lookup.md, CR-AIWS-2026-09-004); khi dùng thì grep trang "
                "chứ đừng cat. Một tài liệu không có tên ở đây = không có trong wiki đã đăng ký "
                "của system đó — kết luận hợp lệ, dừng lại. Corpus lớn thì đây là trang GỐC, các "
                "trang nhánh WIKI_NAV*_NN*.md link từ đây và KHÔNG được đăng ký riêng."
            ) if page == "nav" else ""
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
            if nav_summary:
                cmd += ["--summary", nav_summary]
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
