#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_wiki_page_base.py — deterministic base for /aiws-wiki build-pages (CR-AIWS-2026-07-023).

Subcommands (NO LLM — deterministic only):
  indices         Gate 0 inventory: registered index files + entry counts per system
                  (local index HIDDEN unless --authorized — DP-024-B / rule #11)
  survey          inventory + dir-map (rollup) + gap checklist (profile-driven) +
                  wiki-zone scan + data-quality report  -> SURVEY_<sys>.md + survey_<sys>.json
  skeleton        --page <KIND>: frontmatter + deterministic tables + source digest table
                  + NARRATIVE markers  -> SKELETON_<KIND>_<sys>.md (LLM fills markers later)
  check-grounding staleness: grounding source updated_at > page last_verified_at (rc 3 if stale)

stdlib-only; UTF-8 stdout (cp932-safe). Multi-system: HARD-REQUIRE --system/--all-systems
when project_profile.multi_system: true (rc=2 if missing) — rule #12.
Index scope (CR-AIWS-2026-07-024): two INDEPENDENT axes — `--system` filters records
(horizontal, rule #12); `--scope` picks WHICH registered index files to read (vertical,
rule #13). survey/skeleton/check-grounding HARD-REQUIRE --scope (NO default — DP-024-A:
run `indices`, confirm the index set with the HUMAN [Gate 0], then pass the chosen scope).
Scope beyond project,aiws requires --authorized (rule #11 / CR-052) — same gate as lookup.
"""
import argparse, io, json, os, re, sys
from datetime import datetime, date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (  # noqa: E402
    ProjectProfileUnreadable, parse_scope, read_project_config, resolve_index_paths,
    scope_needs_authorization, index_inventory, locator_str,
    write_text,
)

# --- cp932-safe UTF-8 stdout (Windows) ---
try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
except Exception:  # noqa: BLE001
    pass

# Grounding exclusions (§6.6): routing pages + templates are never evidence.
EXCLUDED_GROUNDING_TYPES = {"overview_page", "wiki_page"}
TEMPLATE_TYPE_RE = re.compile(r"template", re.I)

PAGE_KINDS = [
    "SYSTEM_OVERVIEW", "SYSTEM_ARCHITECTURE", "FUNCTION_LIST", "SCREEN_LIST",
    "TABLE_LIST", "BUSINESS_FLOW", "DIRECTORY_MAP", "INTENT_NAVIGATION",
    "READ_FIRST", "GLOSSARY",
]
CUSTOM_KIND_RE = re.compile(r"^CUSTOM_[A-Z0-9_]+$")

# KIND_NA (CR-AIWS-2026-07-046): a page kind that does NOT APPLY to this flavor (a methodology
# corpus has no screens and no tables). Distinct from `None`, which already means "deterministic —
# grounded by all locators". Without this sentinel an inapplicable kind would masquerade as
# PROPOSE (None) or as NO_GROUNDING (empty set) — both wrong.
KIND_NA = "__NOT_APPLICABLE__"

# KIND_RULES v1 — grounding source_type classes per flavor (DATA constant).
KIND_RULES = {
    "docs": {
        "SYSTEM_OVERVIEW": {"requirement_definition", "basic_design", "customer_requirement", "canonical_doc"},
        "SYSTEM_ARCHITECTURE": {"basic_design", "detail_design"},
        "FUNCTION_LIST": {"basic_design", "detail_design", "requirement_definition"},
        "SCREEN_LIST": {"basic_design", "screen_mockup"},
        "TABLE_LIST": {"detail_design", "db_schema"},
        "BUSINESS_FLOW": {"requirement_definition", "basic_design"},
        "DIRECTORY_MAP": None,       # deterministic — all locators
        "INTENT_NAVIGATION": None,
        "READ_FIRST": None,
        "GLOSSARY": {"requirement_definition", "basic_design", "canonical_doc"},
    },
    "cobol": {
        "SYSTEM_OVERVIEW": {"cobol_source", "legacy_design", "basic_design"},
        "SYSTEM_ARCHITECTURE": {"cobol_source", "module"},
        "FUNCTION_LIST": {"cobol_source", "module"},
        "SCREEN_LIST": {"screen_mockup"},
        "TABLE_LIST": {"db_schema", "detail_design"},
        "BUSINESS_FLOW": {"legacy_design", "basic_design"},
        "DIRECTORY_MAP": None,
        "INTENT_NAVIGATION": None,
        "READ_FIRST": None,
        "GLOSSARY": None,
    },
    # CR-AIWS-2026-07-046: a methodology corpus (AIWS itself: 110 methodology_spec + 84
    # wiki_guideline) matched NO grounding class of the `docs` flavor, so 7/10 kinds came back
    # NO_GROUNDING and pages for system `aiws` could not be built at all (blocked AIP-EXEC-931).
    # SCREEN_LIST / TABLE_LIST are N/A here BY DESIGN (a methodology has no screens or tables) —
    # they are `None` (skipped), which is NOT the same as "no grounding found".
    "methodology": {
        "SYSTEM_OVERVIEW": {"methodology_spec", "wiki_guideline", "canonical_doc"},
        "SYSTEM_ARCHITECTURE": {"methodology_spec", "wiki_guideline"},
        "FUNCTION_LIST": {"methodology_spec"},
        "SCREEN_LIST": KIND_NA,     # not applicable to a methodology corpus
        "TABLE_LIST": KIND_NA,      # not applicable to a methodology corpus
        "BUSINESS_FLOW": {"methodology_spec", "wiki_guideline", "process_guideline", "sop"},
        "DIRECTORY_MAP": None,
        "INTENT_NAVIGATION": None,
        "READ_FIRST": None,
        "GLOSSARY": {"methodology_spec", "wiki_guideline"},
    },
}

# Source types whose presence (in the majority) marks a corpus as a methodology corpus.
METHODOLOGY_TYPES = {"methodology_spec", "wiki_guideline", "process_guideline", "sop",
                     "process_template"}


def find_project_root(start=None):
    p = Path(start or os.getcwd()).resolve()
    for cand in [p, *p.parents]:
        if (cand / ".ai-work").is_dir():
            return cand
    return p


# `load_yaml_lite` lived here until CR-AIWS-2026-08-128 C3 — a THIRD hand-rolled parser for
# project_profile.yml, with exactly one caller (measured). Beyond the duplication it conflated two
# different facts: it returned {} for a MISSING file and for an UNPARSEABLE one, so a damaged profile
# read as "no keys" and multi-system scoping quietly switched off. `read_project_config` distinguishes
# them and raises on the second.


def parse_frontmatter(text):
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end < 0:
        return {}, text
    fm_raw = text[3:end].strip("\n")
    body = text[end + 4:]
    meta, key = {}, None
    for raw in fm_raw.splitlines():
        if re.match(r"^\s*-\s+", raw) and key:
            meta.setdefault(key, [])
            if isinstance(meta[key], list):
                meta[key].append(raw.split("-", 1)[1].strip())
            continue
        m = re.match(r"^([A-Za-z0-9_]+):\s*(.*)$", raw)
        if m:
            key = m.group(1)
            v = m.group(2).strip()
            meta[key] = v if v != "" else None
    return meta, body


def load_index(proot, scope_set):
    """Read ALL registered indices selected by scope_set (CR-AIWS-2026-07-024 —
    shared resolver from _common; this tool must NOT re-implement index selection).
    Returns (records, indices_read) where indices_read carries provenance
    [{path, records}] for the survey json / PAGE_PLAN audit trail."""
    ws = proot / ".ai-work" / "wiki_sources"
    recs, indices_read = [], []
    for idx in resolve_index_paths(ws, scope_set):
        n0 = len(recs)
        for line in idx.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                try:
                    recs.append(json.loads(line))
                except Exception:  # noqa: BLE001
                    pass
        try:
            rel = str(idx.relative_to(proot)).replace("\\", "/")
        except ValueError:
            rel = str(idx)
        indices_read.append({"path": rel, "records": len(recs) - n0})
    return recs, indices_read


def resolve_locator(proot, loc):
    if not loc:
        return None
    loc = loc.split("#")[0].strip()
    if loc.startswith("__PROJECT_ROOT__"):
        return proot / loc[len("__PROJECT_ROOT__"):].replace("\\", "/").lstrip("/")
    if (len(loc) >= 2 and loc[1] == ":") or loc.startswith("/"):
        return Path(loc)
    return proot / loc.replace("\\", "/").lstrip("/")


def detect_flavor(recs):
    types = {r.get("source_type", "") for r in recs}
    if any("cobol" in t for t in types):
        return "cobol"
    # CR-AIWS-2026-07-046: a corpus whose MAJORITY is methodology/guideline material is a
    # methodology corpus — the `docs` fallback (requirement_definition / basic_design / …) has no
    # grounding class that such a corpus can satisfy.
    counted = [r.get("source_type", "") for r in recs]
    if counted and sum(1 for t in counted if t in METHODOLOGY_TYPES) > len(counted) / 2:
        return "methodology"
    return "docs"


def is_grounding_eligible(r):
    st = r.get("source_type") or ""
    if st in EXCLUDED_GROUNDING_TYPES:
        return False
    if TEMPLATE_TYPE_RE.search(st):
        return False
    return True


def build_dir_map(recs):
    """dir -> {count, types, sources}; rollup siblings same prefix+single type."""
    dm = {}
    for r in recs:
        loc = r.get("artifact_locator")
        if loc == "__OBJECT__":
            bucket = "(objects)"
        elif not loc:
            bucket = "(no-locator)"
        else:
            bucket = str(Path(loc.replace("\\", "/")).parent)
        d = dm.setdefault(bucket, {"count": 0, "types": set(), "sources": []})
        d["count"] += 1
        d["types"].add(r.get("source_type") or "unknown")
        d["sources"].append(r.get("source_id"))
    # rollup: parent-prefix groups where every child dir has a single identical type
    rolled, consumed = {}, set()
    by_parent = {}
    for dpath in dm:
        if dpath in ("(objects)", "(no-locator)"):
            continue
        by_parent.setdefault(str(Path(dpath).parent), []).append(dpath)
    for parent, children in by_parent.items():
        if len(children) >= 3:
            child_types = set()
            for c in children:
                child_types |= dm[c]["types"]
            if len(child_types) == 1:
                total = sum(dm[c]["count"] for c in children)
                rolled[f"{parent}/* ({len(children)} dirs)"] = {
                    "count": total, "types": sorted(child_types),
                    "sources": [s for c in children for s in dm[c]["sources"]],
                }
                consumed.update(children)
    out = {}
    for dpath, d in dm.items():
        if dpath in consumed:
            continue
        out[dpath] = {"count": d["count"], "types": sorted(d["types"]), "sources": d["sources"]}
    out.update(rolled)
    return out


def scan_wiki_zone(proot, system):
    """Existing curated pages under .ai-work/wiki/pages/ for this system."""
    pages_dir = proot / ".ai-work" / "wiki" / "pages"
    existing = []
    if pages_dir.is_dir():
        for f in sorted(pages_dir.glob("*.md")):
            meta, _ = parse_frontmatter(f.read_text(encoding="utf-8"))
            if meta.get("artifact_type") == "wiki_page":
                if not system or meta.get("system") == system:
                    existing.append({"page_kind": meta.get("page_kind"),
                                     "system": meta.get("system"),
                                     "status": meta.get("status"),
                                     "path": str(f.relative_to(proot))})
    return existing


def data_quality(recs):
    missing_st, broken_sum, unknown_sys = [], [], []
    for r in recs:
        if not r.get("source_type"):
            missing_st.append(r.get("source_id"))
        s = (r.get("summary_short") or "").strip()
        if not s or s in ("...", "-") or len(s) < 15:
            broken_sum.append(r.get("source_id"))
    return {"missing_source_type": missing_st, "broken_summary": broken_sum,
            "boilerplate_object_meta": [], "unknown_system": unknown_sys}


# CR-AIWS-2026-07-067 T1 — per-kind relevance keyword bags (bilingual VN+EN). After the KIND_RULES
# source_type filter, grounding is RANKED by how many of the kind's keywords appear in a source's
# lookup_keys/summary/title, THEN cut — so the kept N are the most relevant N, not the first N in
# index order (which used to send everything past the front region to /dev/null; see CAP-003).
KIND_KEYWORDS = {
    "SYSTEM_OVERVIEW":     ["overview", "system", "concept", "model", "architecture",
                            "tổng quan", "khái niệm", "kiến trúc"],
    "SYSTEM_ARCHITECTURE": ["architecture", "component", "layer", "actor", "design",
                            "kiến trúc", "thành phần", "tầng"],
    "FUNCTION_LIST":       ["function", "skill", "verb", "command", "tool", "capability",
                            "chức năng", "lệnh", "công cụ"],
    "BUSINESS_FLOW":       ["flow", "process", "lifecycle", "step", "gate",
                            "luồng", "quy trình", "bước", "cổng"],
    "DIRECTORY_MAP":       ["directory", "path", "structure", "layout", "folder", "tree",
                            "thư mục", "cấu trúc", "đường dẫn"],
    "INTENT_NAVIGATION":   ["intent", "navigation", "route", "lookup", "find",
                            "ý định", "điều hướng", "tra cứu"],
    "READ_FIRST":          ["onboarding", "start", "first", "introduction", "guide",
                            "bắt đầu", "giới thiệu", "đọc trước"],
    "GLOSSARY":            ["glossary", "term", "definition", "terminology", "vocabulary",
                            "thuật ngữ", "định nghĩa"],
}
GROUNDING_LIMIT_DEFAULT = 100                        # CR-AIWS-2026-07-067 (was hardcoded 40)


def _rank_grounding(kind, gset):
    """Stable-rank a grounding set by relevance to `kind`, keeping index order as the tiebreak.

    Deterministic (no LLM): score = number of the kind's keywords found (substring, lowercased) in
    the record's title + summary_short + lookup_keys. A kind with no keyword bag (e.g. CUSTOM_*)
    is returned unchanged — never a regression. CR-AIWS-2026-07-067 T1.
    """
    kws = KIND_KEYWORDS.get(kind)
    if not kws:
        return gset
    def score(r):
        hay = " ".join([str(r.get("title", "")), str(r.get("summary_short", "")),
                        " ".join(r.get("lookup_keys") or [])]).lower()
        return sum(1 for k in kws if k in hay)
    # enumerate() supplies the original index as a stable tiebreak → reproducible ordering
    return [r for _, r in sorted(enumerate(gset), key=lambda t: (-score(t[1]), t[0]))]


def build_gap_checklist(recs, flavor, existing_pages, limit=GROUNDING_LIMIT_DEFAULT):
    rules = KIND_RULES.get(flavor, KIND_RULES["docs"])
    ground_pool = [r for r in recs if is_grounding_eligible(r)]
    exist_kinds = {p["page_kind"] for p in existing_pages}
    checklist = []
    for kind in PAGE_KINDS:
        allowed = rules.get(kind, None)
        if allowed == KIND_NA:                      # CR-046: kind does not apply to this flavor
            checklist.append({
                "kind": kind, "verdict": "N_A", "grounding_count": 0, "grounding": [],
                "zone_evidence": [p["path"] for p in existing_pages if p["page_kind"] == kind],
            })
            continue
        if allowed is None:
            gset = ground_pool                      # deterministic / all-locators
        else:
            gset = [r for r in ground_pool if r.get("source_type") in allowed]
        gcount = len(gset)
        if kind in exist_kinds:
            verdict = "PAGE_EXISTS"
        elif allowed is not None and gcount == 0:
            verdict = "NO_GROUNDING"
        else:
            verdict = "PROPOSE"
        ranked = _rank_grounding(kind, gset)        # CR-AIWS-2026-07-067 T1: rank BEFORE the cut
        checklist.append({
            "kind": kind, "verdict": verdict, "grounding_count": gcount,
            "grounding": [r.get("source_id") for r in ranked[:limit]],   # T2: limit (default 100)
            "zone_evidence": [p["path"] for p in existing_pages if p["page_kind"] == kind],
        })
    return checklist


def cmd_survey(args, proot):
    all_recs, indices_read = load_index(proot, args._scope_set)
    recs = [r for r in all_recs
            if (args.all_systems or r.get("system") == args.system)]
    for ir in indices_read:
        print(f"index read: {ir['path']} ({ir['records']} records)")
    flavor = args.flavor if args.flavor and args.flavor != "auto" else detect_flavor(recs)
    system_label = "ALL" if args.all_systems else args.system
    inventory = {}
    for r in recs:
        inventory.setdefault(r.get("source_type") or "unknown", []).append(r.get("source_id"))
    existing = scan_wiki_zone(proot, None if args.all_systems else args.system)
    survey = {
        "system": system_label, "flavor": flavor, "total_sources": len(recs),
        "scope": sorted(args._scope_set), "indices_read": indices_read,
        "inventory": {k: sorted(v) for k, v in sorted(inventory.items())},
        "dir_map": build_dir_map(recs),
        "gap_checklist": build_gap_checklist(recs, flavor, existing,
                                             limit=getattr(args, "grounding_limit",
                                                           GROUNDING_LIMIT_DEFAULT)),
        "data_quality": data_quality(recs),
        "existing_wiki_pages": existing,
    }
    outdir = Path(args.out); outdir.mkdir(parents=True, exist_ok=True)
    write_text((outdir / f"survey_{system_label}.json"), 
        json.dumps(survey, ensure_ascii=False, indent=2))
    # human-readable SURVEY md
    lines = [f"# SURVEY — system `{system_label}` (flavor: {flavor})",
             f"\nTotal registered sources: **{len(recs)}**",
             f"\nIndex scope: `{','.join(sorted(args._scope_set))}` — read: "
             + "; ".join(f"`{ir['path']}` ({ir['records']})" for ir in indices_read) + "\n",
             "## Inventory (by source_type)\n"]
    for st, ids in survey["inventory"].items():
        lines.append(f"- `{st}` — {len(ids)}")
    lines.append("\n## Directory map (registered sources)\n")
    for d, info in sorted(survey["dir_map"].items()):
        lines.append(f"- `{d}` — {info['count']} ({', '.join(info['types'])})")
    lines.append("\n## Page gap checklist (không trang nào auto-build — HUMAN chọn ở Gate 1)\n")
    lines.append("| Page kind | Verdict | Grounding # |")
    lines.append("|---|---|---|")
    for c in survey["gap_checklist"]:
        lines.append(f"| {c['kind']} | {c['verdict']} | {c['grounding_count']} |")
    dq = survey["data_quality"]
    lines.append("\n## Data-quality report\n")
    lines.append(f"- missing source_type: {len(dq['missing_source_type'])}")
    lines.append(f"- weak/boilerplate summary: {len(dq['broken_summary'])}")
    lines.append(f"\n## Existing curated pages\n- {len(existing)} found")
    write_text((outdir / f"SURVEY_{system_label}.md"), "\n".join(lines) + "\n")
    print(f"survey OK: {len(recs)} sources, flavor={flavor} -> {outdir}/survey_{system_label}.json")
    return 0


def cmd_skeleton(args, proot):
    survey = json.loads(Path(args.survey).read_text(encoding="utf-8"))
    kind = args.page
    if kind not in PAGE_KINDS and not CUSTOM_KIND_RE.match(kind):
        print(f"WARN: page_kind '{kind}' outside enum + CUSTOM_ pattern", file=sys.stderr)
    entry = next((c for c in survey["gap_checklist"] if c["kind"] == kind), None)
    grounding_ids = entry["grounding"] if entry else []
    # CR-AIWS-2026-07-067 T3: the grounding was ranked-then-cut at survey time. Surface "shown N/total"
    # so the writer KNOWS the page is grounded on a subset and must say so in Coverage & Limits —
    # the old code printed only the cut list and hid the total (CAP-003).
    ground_total = entry.get("grounding_count", len(grounding_ids)) if entry else 0
    ground_shown = len(grounding_ids)
    recs = {r.get("source_id"): r for r in load_index(proot, args._scope_set)[0]}
    today = args.today or date.today().isoformat()
    fm = [
        "---", "artifact_type: wiki_page", f"page_kind: {kind}",
        f"system: {args.system}", f'title: "{kind.replace("_", " ").title()} — {args.system}"',
        "status: draft", "audience: human+ai",
        f'generated_by: "/aiws-wiki build-pages ({args.aip or "AIP-EXEC-NNN"})"',
        f"generated_at: {today}", "last_verified_at:", "---", "",
    ]
    body = [f"# {kind.replace('_', ' ').title()} — {args.system}", ""]
    if ground_shown < ground_total:                 # CR-AIWS-2026-07-067 T3
        body += [f"> ⚠️ grounding: hiển thị {ground_shown}/{ground_total} nguồn "
                 "(đã rank theo độ liên quan; raise bằng `--grounding-limit` khi survey nếu cần "
                 "phủ rộng hơn). Ghi giới hạn này vào `## Coverage & Limits`.", ""]
    body += ["<!-- NARRATIVE:BEGIN — LLM viết theo page contract v0.1; giữ marker -->", "",
             "(narrative pass sẽ điền — mọi claim cần citation [S#])", "",
             "<!-- NARRATIVE:END -->", "",
             "## Source digest (deterministic — nguồn khả dụng)", "",
             "| Alias | source_id | Artifact path | Summary |", "|---|---|---|---|"]
    for i, sid in enumerate(grounding_ids, 1):
        r = recs.get(sid, {})
        summ = (r.get("summary_short") or "").replace("|", "/")[:80]
        body.append(f"| [S{i}] | {sid} | {r.get('artifact_locator', '')} | {summ} |")
    body += ["", "## Coverage & Limits", "", "(LLM điền — grounding không phủ gì; coverage tính từ grounding)",
             "", "## Sources", "", "| Alias | source_id | Artifact path | Đã lấy gì |", "|---|---|---|---|"]
    for i, sid in enumerate(grounding_ids, 1):
        r = recs.get(sid, {})
        body.append(f"| [S{i}] | {sid} | {r.get('artifact_locator', '')} | (LLM điền) |")
    outdir = Path(args.out); outdir.mkdir(parents=True, exist_ok=True)
    outp = outdir / f"SKELETON_{kind}_{args.system}.md"
    write_text(outp, "\n".join(fm + body) + "\n")
    print(f"skeleton OK: {kind} ({len(grounding_ids)} grounding) -> {outp}")
    return 0


def _parse_ts(s):
    if not s:
        return None
    s = str(s).strip()
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt)
        except Exception:  # noqa: BLE001
            continue
    m = re.match(r"(\d{4}-\d{2}-\d{2})", s)
    if m:
        try:
            return datetime.strptime(m.group(1), "%Y-%m-%d")
        except Exception:  # noqa: BLE001
            return None
    return None


def _src_updated_at(rec, proot):
    if rec.get("updated_at"):
        return rec["updated_at"]
    # CR-AIWS-2026-07-064 B6 (Rule 9): index records are DATA. A non-string meta_locator crashed
    # in the local resolver, and a fragment-only ('#x') or bare '__PROJECT_ROOT__' locator resolved
    # to the project ROOT DIRECTORY, passed exists(), then killed the whole check-grounding run on
    # read_text(). Normalize, require a real file, and degrade per-citation.
    ml = resolve_locator(proot, locator_str(rec.get("meta_locator")))
    if ml is not None and ml.is_file():
        try:
            mm, _ = parse_frontmatter(ml.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            return None
        return mm.get("updated_at")
    return None


def cmd_check_grounding(args, proot):
    pages_dir = Path(args.pages_dir)
    recs = {r.get("source_id"): r for r in load_index(proot, args._scope_set)[0]}
    stale = []
    for f in sorted(pages_dir.glob("*.md")):
        meta, body = parse_frontmatter(f.read_text(encoding="utf-8"))
        if meta.get("artifact_type") != "wiki_page":
            continue
        if not (args.all_systems or meta.get("system") == args.system):
            continue
        if meta.get("status") != "active":
            continue
        lv = _parse_ts(meta.get("last_verified_at"))
        src_ids = re.findall(r"\|\s*\[S\d+\]\s*\|\s*([A-Za-z0-9_\-]+)\s*\|", body)
        for sid in src_ids:
            r = recs.get(sid)
            if r is None:
                stale.append((f.name, sid, "deregistered"))
                continue
            su = _parse_ts(_src_updated_at(r, proot))
            if lv and su and su.date() > lv.date():
                stale.append((f.name, sid, f"src {su.date()} > verified {lv.date()}"))
    for page, sid, why in stale:
        print(f"STALE: {page} <- {sid} ({why})")
    if not stale:
        print("check-grounding: all fresh")
        return 0
    return 3


def cmd_indices(args, proot):
    """Gate 0 inventory (CR-AIWS-2026-07-024 D3): deterministic list of registered
    indices + per-system counts so the HUMAN can choose --scope. DP-024-B: local
    index hidden entirely (not even metadata) unless --authorized."""
    ws = proot / ".ai-work" / "wiki_sources"
    inv = index_inventory(ws, include_local=bool(args.authorized))
    print("INDICES — registered wiki source indexes (Gate 0 inventory)")
    for e in inv:
        by = ", ".join(f"{k}={v}" for k, v in sorted(e["by_system"].items()))
        try:
            rel = str(Path(e["path"]).relative_to(proot)).replace("\\", "/")
        except ValueError:
            rel = e["path"]
        status = f"entries={e['entries']}" + (f"  by_system: {by}" if by else "") \
            if e["exists"] else "(absent)"
        print(f"- scope={e['scope']:<8} path={rel}  {status}")
    if not args.authorized:
        print("(local index hidden — rule #11 / DP-024-B; pass --authorized "
              "{human|aip|agent-rule} to include its metadata)")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Deterministic base for /aiws-wiki build-pages")
    sub = ap.add_subparsers(dest="cmd", required=True)
    def add_sys(p):
        p.add_argument("--system"); p.add_argument("--all-systems", action="store_true")
        # CR-AIWS-2026-07-024 DP-024-A: NO default — hard-require, checked in main()
        p.add_argument("--scope", default=None, metavar="LIST",
                       help="Comma-list of registered indices to read: project,local,aiws. "
                            "REQUIRED (no default — DP-024-A): run `indices` first and confirm "
                            "the index set with the HUMAN (Gate 0). 'local' requires --authorized "
                            "(rule #11).")
        p.add_argument("--authorized", choices=["human", "aip", "agent-rule"], default=None,
                       help="Authorization source for a scope beyond project,aiws "
                            "(CR-AIWS-2026-06-052 / rule #11).")
    p1 = sub.add_parser("survey"); add_sys(p1)
    p1.add_argument("--out", required=True); p1.add_argument("--flavor", default="auto",
                    choices=["docs", "cobol", "methodology", "auto"])
    p1.add_argument("--grounding-limit", type=int, default=GROUNDING_LIMIT_DEFAULT,
                    help="max grounding sources per page (ranked by relevance; default "
                         f"{GROUNDING_LIMIT_DEFAULT}). CR-AIWS-2026-07-067.")
    p2 = sub.add_parser("skeleton"); add_sys(p2)
    p2.add_argument("--page", required=True); p2.add_argument("--survey", required=True)
    p2.add_argument("--out", required=True); p2.add_argument("--aip"); p2.add_argument("--today")
    p3 = sub.add_parser("check-grounding"); add_sys(p3)
    p3.add_argument("--pages-dir", required=True)
    p4 = sub.add_parser("indices")
    p4.add_argument("--authorized", choices=["human", "aip", "agent-rule"], default=None)
    args = ap.parse_args()

    proot = find_project_root()
    if args.cmd == "indices":
        return cmd_indices(args, proot)

    # CR-AIWS-2026-08-128 C3: the single reader. A damaged profile now raises instead of reading as
    # single-system, so the rule #12 gate below cannot be disarmed by a file nobody noticed was broken.
    try:
        multi = read_project_config(proot / ".ai-work")["multi_system"]
    except ProjectProfileUnreadable as e:
        print(f"ERROR: .ai-work/project_profile.yml exists but could not be parsed: {e}",
              file=sys.stderr)
        return 2
    if multi and not args.all_systems and not getattr(args, "system", None):
        print("ERROR: project is multi_system — pass --system <id> or --all-systems (rule #12)",
              file=sys.stderr)
        return 2
    # CR-AIWS-2026-07-024 DP-024-A (PO override): --scope is HARD-REQUIRED, no default.
    if not args.scope:
        print("ERROR: --scope is required (no default — CR-AIWS-2026-07-024 DP-A). "
              "Run `build_wiki_page_base.py indices` first, confirm the index set with the "
              "HUMAN (Gate 0 — Index Confirm), then pass --scope <chosen> (e.g. project,aiws).",
              file=sys.stderr)
        return 2
    try:
        scope_set = parse_scope(args.scope)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    if scope_needs_authorization(scope_set) and not args.authorized:
        print("error: --scope includes " + str(sorted(set(scope_set) - {"project", "aiws"}))
              + " requires --authorized {human|aip|agent-rule}. "
              "Raw / beyond-default-scope search is never silent — name the authorization source "
              "(HUMAN in conversation, the active AIP's allow_raw_search, or a standing agent rule) "
              "or STOP and ask HUMAN.", file=sys.stderr)
        return 2
    args._scope_set = scope_set
    return {"survey": cmd_survey, "skeleton": cmd_skeleton,
            "check-grounding": cmd_check_grounding}[args.cmd](args, proot)


if __name__ == "__main__":
    sys.exit(main())
