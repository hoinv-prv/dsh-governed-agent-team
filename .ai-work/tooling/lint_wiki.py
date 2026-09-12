#!/usr/bin/env python3
"""Lint wiki knowledge artifacts and wiki source-side artifacts.

Three target groups:
  1. Official wiki entries  (.ai-work/wiki/<type>/*.md)
  2. Wiki source metas      (.ai-work/wiki_sources/meta/*.md or *.yml)
  3. Wiki source index      (.ai-work/wiki_sources/index.jsonl)

Each has its own required-metadata + section checks, per
Wiki_Truth_History_Spec_MVP_v0_1.md and Lint_and_Tooling_Spec_MVP_v0_2.md.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from functools import lru_cache
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (  # noqa: E402
    all_index_paths as _all_index_paths,
    is_ellipsis_path,          # CR-AIWS-2026-08-078 C5 — illustration spans, one definition
    unfenced_lines,            # CR-AIWS-2026-08-078 C5
    meta_roots as _meta_roots,
    resolve_relations_paths as _resolve_relations_paths,
    DATA_FLOW_TYPES,
    NODE_KIND_ARTIFACT,
    NODE_KIND_OBJECT,
    OBJECT_LOCATOR_SENTINEL,
    OVERVIEW_SOURCE_TYPE,
    in_system,
    overview_body_hash,
    overview_fingerprint,
    WSM_REQUIRED_LOG_FIELDS,
    SEV_ERROR,
    LintReport,
    apply_lint_accept,
    emit_report,
    extract_sections,
    find_ai_work_root,
    has_section,
    locator_str,
    parse_frontmatter,
    read_jsonl,
    read_project_config,
    read_text,
    resolve_data_file,
    resolve_locator,
)

# Source Build Routing registry (CR-AIWS-2026-05-019 Stage 2).
# Keep in sync with route_build_tool.KNOWN_PLACEHOLDERS / REFRESH_MODES.
_BUILD_ROUTING_PLACEHOLDERS = {"root", "prefix", "subdir", "artifact"}
_BUILD_ROUTING_REFRESH_MODES = {"rerun_tool", "reconvert_then_rerun"}  # H2 (CR-AIWS-2026-07-002)

# CR-AIWS-2026-06-024: wiki-meta updated_at / last_verified_at accept BOTH a legacy date
# (YYYY-MM-DD) AND a UTC ISO 8601 timestamp — permanently. Legacy date metas MUST stay valid
# (no forced migration), so a value matching either form is OK; only a malformed value is flagged.
_TS_OR_DATE_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}$"                                                 # legacy date
    r"|^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?([+-]\d{2}:\d{2}|Z)?$"  # UTC ISO 8601 timestamp
)


def _valid_ts_or_date(v) -> bool:
    """True if v is a YYYY-MM-DD date or an ISO-8601 timestamp (or empty — presence is checked elsewhere)."""
    return bool(_TS_OR_DATE_RE.match(str(v).strip())) if v else True


ENTRY_REQUIRED_META = [
    "artifact_type", "entry_type", "artifact_id", "title",
    "knowledge_class", "use_rule", "status",
    "canonical_references", "last_verified_at", "updated_at",
]
ENTRY_SECTIONS = ["Purpose", "Scope", "Canonical References", "Recommended Next Reads"]

ENTRY_TYPE_ENUM = {"domain", "function", "module", "data", "pattern", "reference"}
KNOWLEDGE_CLASS_ENUM = {"source_of_truth", "curated", "reference", "history"}
USE_RULE_ENUM = {"authoritative", "verify_when_decision_matters",
                 "verify_before_use", "historical_only"}
ENTRY_STATUS_ENUM = {"active", "needs_review", "superseded"}

META_REQUIRED = [
    "source_id", "title", "source_type", "artifact_locator", "profile_id", "status",
]
META_SECTIONS = ["Summary", "Knowledge Targets", "Lookup Keys"]  # Profile Mapping dropped (CR-024): mirrored frontmatter profile_id
# CR-AIWS-2026-07-037 T2 (DP-037-1=A): soft budget for ## Lookup Keys — emitter-aligned with
# build_wiki_source_meta max_keys=40. Hygiene signal only (index projects keys LOSSLESSLY).
LOOKUP_KEYS_SOFT_BUDGET = 40

# CR-AIWS-2026-08-107 C1 — nhãn PHIÊN BẢN / TRẠNG THÁI trong lookup key.
# `score_lexical` khớp NGUYÊN CỤM, nên vị trí của nhãn quyết định thiệt hại:
#   "AIP v0.3 Conformance Checklist"    -> KHÔNG khớp "AIP Conformance Checklist"      = 0
#   "AIP Conformance Checklist (v0.3)"  -> substring                                   = +4
#   "AIP Conformance Checklist"         -> trùng khít                                  = +12
# Nhãn ở CUỐI chỉ tụt một bậc (−8) và thường là cố ý ⇒ KHÔNG bắt (DP-107-B).
# Nhãn ở GIỮA làm đứt chuỗi ⇒ key mất SẠCH điểm cho người gõ tên ⇒ bắt.
# Từ vựng CỐ Ý không có `MVP`/`proposal`/`candidate`: ở repo này chúng là QUY ƯỚC ĐẶT TÊN
# (`AIWS_Change_Request_Spec_MVP.md`), không phải nhãn trạng thái (DP-107-A).
_LK_MARKER_TOKEN_RE = re.compile(
    r"^\(?(v\d+[._]\d+([._]\d+)?|draft|WIP|superseded|deprecated|retired|obsolete)\)?[,;:]?$",
    re.I)


def _lookup_key_marker_midname(key: str) -> str:
    """Trả về token nhãn nếu nó đứng RIÊNG và có token không-nhãn ở CẢ HAI phía; else ''.

    Đứng riêng = là một token phân tách bằng khoảng trắng. Nhãn nằm BÊN TRONG một token
    (`CHANGELOG_v0_5_0`) không tính: đó là tên file thật, không phải nhãn chèn vào tên.

    "Cả hai phía" phải là token KHÔNG-nhãn, không phải chỉ là "có token nào đó". Nhãn có thể
    dài hơn một token — `... Checklist (draft v0.1)` tách thành `(draft` + `v0.1)` — và nếu chỉ
    xét VỊ TRÍ thì `(draft` trông như "có chữ ở cả hai phía" trong khi thứ đứng sau nó cũng là
    nhãn. Đó vẫn là nhãn Ở CUỐI (chỉ mất 1 bậc) nên KHÔNG được bắt (DP-107-B).
    """
    toks = key.split()
    marks = [bool(_LK_MARKER_TOKEN_RE.match(t)) for t in toks]
    for i, t in enumerate(toks):
        if not marks[i]:
            continue
        if any(not m for m in marks[:i]) and any(not m for m in marks[i + 1:]):
            return t
    return ""

INDEX_REQUIRED = [
    "source_id", "title", "source_type", "artifact_locator",
    "profile_id", "summary_short", "knowledge_targets", "status",
]

WTA_OPTIONAL_META_FIELDS = [
    "authority_level",
    "freshness_status",
    "source_representation_status",
    "knowledge_value",
    "intended_ai_use",
    "promotion_status",
]

SRI_OPTIONAL_META_FIELDS = [
    "original_source_locator",
    # CR-AIWS-2026-07-021 (IR-C): representation_locator removed from the info-recommend set — the
    # spec (WIKI_META_INDEX_SPEC) OMITS it when it equals artifact_locator, so an unconditional
    # "recommended SRI field missing: representation_locator" is a false recommendation on every
    # converted source whose AIWS-readable artifact_locator already IS the representation.
    "representation_type",
    "conversion_method",
    "conversion_date",
    "converted_by",
    "conversion_limitations",
    "representation_scope",
]
AIWS_READABLE_EXTS = {".md", ".txt", ".json", ".jsonl", ".csv", ".yml", ".yaml"}
RAW_NON_TEXT_EXTS = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tif", ".tiff", ".webp", ".bin"}

AUTHORITY_LEVEL_ENUM = {
    "source_of_truth", "curated_reference", "working_reference",
    "history_reference", "candidate", "unknown",
}
SOURCE_REPRESENTATION_STATUS_ENUM = {
    "complete", "partial", "needs_review", "failed", "unknown", "not_applicable",
}
PROMOTION_STATUS_ENUM = {
    "approved", "candidate", "draft", "needs_review", "archived",
}
SOURCE_TYPE_VOCAB = {
    "requirement_definition", "basic_design", "detail_design",
    "customer_requirement", "process_guideline", "process_template",
    "sop", "canonical_doc", "test_spec", "methodology_spec",
    "meeting_note", "legacy_design", "screen_mockup", "api_manual",
    "db_schema", "unit_test_spec", "wiki_guideline",  # wiki_guideline: CR-AIWS-2026-05-034 (also profile-declared)
}
UNSAFE_RECOMMENDATIONS = {
    "approve_update", "auto_promote", "auto_apply",
}

# WSM_REQUIRED_LOG_FIELDS lives in _common (single source of truth, shared with
# append_maintenance_log) — imported above so writer and linter cannot drift.
WSM_ACTION_ENUM = {
    "refresh_draft_created", "meta_applied", "index_rebuilt", "candidate_created",
    "candidate_deferred", "source_representation_issue_recorded", "meta_archived",
    "meta_restored", "no_action_recorded", "source_deregistered", "aiws_package_apply",
    "relations_rebuilt",
}

# CR-AIWS-2026-06-020: stray tool-call / markup artifacts that can survive into a meta
# body via a botched Write (e.g. </invoke>). They parse-harmlessly, so extract_sections
# folds them into the last section and the rest of the linter never sees them.
_TRAILING_JUNK_RE = re.compile(
    r"</?(?:invoke|antml:parameter|function_calls|parameter|content)\b", re.IGNORECASE
)


@lru_cache(maxsize=8)
def _ms_config(ai_work_str: str) -> tuple:
    """(multi_system: bool, systems: frozenset, synthetic: frozenset) from project_profile.yml
    (CR-06-017 + CR-AIWS-2026-07-028). Absent → off. Reads via the centralized
    _common.read_project_config (CR-AIWS-2026-06-061 §8.5) so the config parser cannot drift
    from lookup / build_meta; re-shaped to a cached tuple here."""
    cfg = read_project_config(Path(ai_work_str))
    return (cfg["multi_system"], frozenset(cfg["systems"]), frozenset(cfg["synthetic_systems"]))



def _looks_raw_non_text(locator: str) -> bool:
    if not locator:
        return False
    suffix = Path(str(locator).split("#")[0]).suffix.lower()
    return suffix in RAW_NON_TEXT_EXTS


def _looks_aiws_readable(locator: str) -> bool:
    if not locator:
        return False
    suffix = Path(str(locator).split("#")[0]).suffix.lower()
    return suffix in AIWS_READABLE_EXTS


def _lint_wiki_entry(path: Path, report: LintReport) -> None:
    rel = str(path)
    meta, body = parse_frontmatter(read_text(path))
    if meta.get("artifact_type") != "wiki_entry":
        return  # not an entry (might be a README, glossary, etc.)

    for k in ENTRY_REQUIRED_META:
        if k not in meta or meta[k] in (None, "", []):
            report.error("entry_meta", f"missing metadata: {k}", path=rel)

    # CR-AIWS-2026-06-024: accept date OR UTC ISO 8601 timestamp; flag only malformed values.
    for ts_field in ("updated_at", "last_verified_at"):
        val = meta.get(ts_field)
        if val and not _valid_ts_or_date(val):
            report.warn("entry_ts_format",
                        f"{ts_field} should be a date (YYYY-MM-DD) or UTC ISO 8601 timestamp: {val}",
                        path=rel)

    et = meta.get("entry_type")
    if et and et not in ENTRY_TYPE_ENUM:
        report.error("entry_type", f"entry_type '{et}' invalid", path=rel)
    kc = meta.get("knowledge_class")
    if kc and kc not in KNOWLEDGE_CLASS_ENUM:
        report.error("knowledge_class", f"knowledge_class '{kc}' invalid", path=rel)
    ur = meta.get("use_rule")
    if ur and ur not in USE_RULE_ENUM:
        report.error("use_rule", f"use_rule '{ur}' invalid", path=rel)
    st = meta.get("status")
    if st and st not in ENTRY_STATUS_ENUM:
        report.error("entry_status", f"status '{st}' invalid", path=rel)

    for sec in ENTRY_SECTIONS:
        if not has_section(body, sec):
            report.error("entry_section", f"missing section: {sec}", path=rel)

    if kc == "source_of_truth":
        refs = meta.get("canonical_references") or []
        if not refs:
            report.warn("sot_weak_ref",
                        "source_of_truth entry has no canonical_references",
                        path=rel)

    if st == "needs_review":
        report.warn("needs_review", "entry is marked needs_review", path=rel)


@lru_cache(maxsize=None)
def _allowed_source_types(profiles_dir_str: str) -> frozenset:
    """Valid source_types = canonical base vocab ∪ source_type declared by each shipped
    profile (CR-AIWS-2026-05-008 / IR-04). A project adds a type by declaring it on a
    profile — no hardcoded edit needed, and lint stays in sync with shipped profiles.
    """
    allowed = set(SOURCE_TYPE_VOCAB)
    pdir = Path(profiles_dir_str)
    if pdir.is_dir():
        for f in pdir.glob("*.yml"):
            lines = read_text(f).splitlines()
            for i, line in enumerate(lines):
                s = line.strip()
                # singular form: `source_type: X` (one value)
                if s.startswith("source_type:"):
                    val = s.split(":", 1)[1].strip().strip("\"'")
                    if val:
                        allowed.add(val)
                # plural form: `source_types: [a, b]` OR a `- item` block list
                # (CR-AIWS-2026-06-004 C3 — a profile may declare many source_types,
                # e.g. knowledge_object.yml carries the object kinds per DP2/DP3).
                elif s.startswith("source_types:"):
                    inline = s.split(":", 1)[1].strip()
                    if inline.startswith("[") and inline.endswith("]"):
                        for v in inline[1:-1].split(","):
                            v = v.strip().strip("\"'")
                            if v:
                                allowed.add(v)
                    else:
                        for nxt in lines[i + 1:]:
                            t = nxt.strip()
                            if t.startswith("- "):
                                # CR-AIWS-2026-08-028 T3 (DP-028-B = a): cat inline comment.
                                # Truoc do `- x  # note` dang ky nguyen chuoi KEM comment, nen `x`
                                # khong bao gio vao vocab — khong loi parse, trieu chung noi len o
                                # noi khac duoi ten `meta_source_type_unknown`. Chi cat khi truoc
                                # `#` co KHOANG TRANG, nen mot gia tri chua hash lien ky tu
                                # (vd `asp#weird`) khong bi dung toi.
                                v = re.split(r"\s+#", t[2:], maxsplit=1)[0]
                                v = v.strip().strip("\"'")
                                if v:
                                    allowed.add(v)
                            elif t and not t.startswith("#"):
                                break
    return frozenset(allowed)


def _ai_work_for(path: Path) -> "Path | None":
    for parent in path.parents:
        if parent.name == ".ai-work":
            return parent
    return None


def _orphan_artifact_check(meta_path: Path, artifact_locator: str,
                           report: LintReport, rel: str) -> None:
    """Warn when a source meta's artifact_locator resolves to a nonexistent file.

    Checks existence regardless of locator style — __PROJECT_ROOT__ placeholder,
    project-relative, OR absolute path. (Portability of absolute paths is a separate
    concern flagged by meta_absolute_locator; existence is independent.)
    URLs / external locators (with '://') are skipped.
    """
    # node_kind=object metas have NO backing file — the __OBJECT__ sentinel is not a path
    # and must never be flagged as an orphan (CR-AIWS-2026-05-023 DP7/INV-9).
    if artifact_locator == OBJECT_LOCATOR_SENTINEL:
        return
    if not artifact_locator or "://" in artifact_locator:
        return
    loc = str(artifact_locator).split("#")[0].strip()
    if not loc:
        return
    # derive project root from the meta path (.ai-work/wiki_sources/meta/...)
    project_root = None
    for parent in meta_path.parents:
        if parent.name == ".ai-work":
            project_root = parent.parent
            break
    if project_root is None:
        return  # cannot resolve (e.g. external/local meta) — skip
    if loc.startswith("__PROJECT_ROOT__"):
        resolved = project_root / loc[len("__PROJECT_ROOT__"):].replace("\\", "/").lstrip("/")
    elif (len(loc) >= 2 and loc[1] == ":") or loc.startswith("/"):
        resolved = Path(loc)  # absolute — STILL existence-check (orphan detection)
    else:
        resolved = project_root / loc.replace("\\", "/").lstrip("/")
    if not resolved.exists():
        report.warn("meta_orphan_artifact",
                    f"artifact_locator points to a nonexistent file: {artifact_locator}",
                    path=rel, loc="artifact_locator")


def _lint_qa_store(store: Path, index_ids: set, report: LintReport) -> None:
    """CR-AIWS-2026-07-009 T5 (lint rules, cr_required per CR-037): QA Memory store —
    schema/id/status/confirmed_by checks + source_refs-resolve WARN. Store rỗng = hợp lệ."""
    rel = str(store)
    try:
        rows = read_jsonl(store)
    except Exception as e:  # noqa: BLE001
        report.error("qa_store_parse", str(e), path=rel)
        return
    seen: set = set()
    for idx, rec in enumerate(rows, start=1):
        loc = f"line {idx}"
        for f in ("id", "question", "answer", "qa_kind", "asked_by", "status"):
            if not rec.get(f):
                report.error("qa_store_field", f"QA record missing field: {f}", path=rel, loc=loc)
        rid = rec.get("id", "")
        if rid in seen:
            report.error("qa_store_dup", f"duplicate QA id: {rid}", path=rel, loc=loc)
        seen.add(rid)
        if rec.get("qa_kind") not in ("overview_answer", "task_info_pack", "investigation_finding"):
            report.warn("qa_store_kind", f"qa_kind '{rec.get('qa_kind')}' not in taxonomy", path=rel, loc=loc)
        if rec.get("asked_by") not in ("human", "ai"):
            report.warn("qa_store_kind", f"asked_by '{rec.get('asked_by')}' not in ['human','ai']", path=rel, loc=loc)
        st = rec.get("status")
        if st not in ("confirmed", "needs_review", "deprecated"):
            report.error("qa_store_status", f"status '{st}' not in enum", path=rel, loc=loc)
        if st == "confirmed" and rec.get("confirmed_by") != "HUMAN":
            report.error("qa_store_confirm", "confirmed record must carry confirmed_by: HUMAN (rule #7)",
                         path=rel, loc=loc)
        for ref in rec.get("source_refs", []) or []:
            if isinstance(ref, str) and ref.startswith("SRC-") and index_ids and ref not in index_ids:
                report.warn("qa_store_ref_stale",
                            f"source_refs id '{ref}' not found in index — QA may be stale (flip needs_review)",
                            path=rel, loc=loc)


_OVERVIEW_FP_CACHE: dict = {}


def _overview_fp_now(project_root: Path, system: str) -> str:
    """Current-inputs fingerprint for overview pages of <system> (cached per run) — must match
    build_wiki_overview's computation (shared _common.overview_fingerprint)."""
    key = (str(project_root), system or "")
    if key in _OVERVIEW_FP_CACHE:
        return _OVERVIEW_FP_CACHE[key]
    ws = project_root / ".ai-work" / "wiki_sources"
    records: list = []
    for name in ("index.jsonl", "index.aiws.jsonl"):
        p = ws / name
        if p.exists():
            try:
                records.extend(read_jsonl(p))
            except Exception:  # noqa: BLE001
                pass
    if system:
        records = [r for r in records if in_system(r, system)]
    rel_raw = ""
    # CR-AIWS-2026-08-064 C7: the fingerprint spans every relations namespace the overview
    # projects (project + shipped aiws preset) — via THE resolver, stable order.
    for rp in _resolve_relations_paths(ws, {"project", "aiws"}):
        try:
            rel_raw += read_text(rp)
        except Exception:  # noqa: BLE001
            pass
    fp = overview_fingerprint(records, rel_raw)
    _OVERVIEW_FP_CACHE[key] = fp
    return fp


def _lint_overview_page(meta: dict, path: Path, report: LintReport, rel: str) -> None:
    """CR-AIWS-2026-07-010 (lint rules, cr_required per CR-037): a GENERATED overview page must
    (a) not be hand-edited (body-hash mismatch = ERROR overview_hand_edit — fix by editing the
    SOURCE metas/index or the generator, then regenerate) and (b) be regenerated after its inputs
    change (fingerprint mismatch = WARN overview_fingerprint_stale)."""
    al = str(meta.get("artifact_locator", ""))
    if not al or al == OBJECT_LOCATOR_SENTINEL or "://" in al:
        return
    proot = None
    for parent in path.parents:
        if parent.name == ".ai-work":
            proot = parent.parent
            break
    if proot is None:
        return
    loc = al.split("#")[0].strip()
    if loc.startswith("__PROJECT_ROOT__"):
        art = proot / loc[len("__PROJECT_ROOT__"):].replace("\\", "/").lstrip("/")
    elif (len(loc) >= 2 and loc[1] == ":") or loc.startswith("/"):
        art = Path(loc)
    else:
        art = proot / loc.replace("\\", "/").lstrip("/")
    if not art.exists():
        return  # orphan check's concern
    try:
        text = read_text(art)
    except Exception:  # noqa: BLE001
        return
    m_bh = re.search(r"GENERATED-BODY-HASH:\s*([0-9a-f]+)", text)
    m_fp = re.search(r"GENERATED-FINGERPRINT:\s*([0-9a-f]+)", text)
    if not (m_bh and m_fp):
        report.error("overview_hand_edit",
                     "generated overview page missing GENERATED footer markers — regenerate via "
                     "build_wiki_overview.py", path=rel)
        return
    if overview_body_hash(text) != m_bh.group(1):
        report.error("overview_hand_edit",
                     "generated overview page body differs from its recorded body-hash — "
                     "hand-edited; edit the SOURCE metas/index (or the generator) and regenerate",
                     path=rel)
    fp_now = _overview_fp_now(proot, str(meta.get("system") or ""))
    if fp_now and fp_now != m_fp.group(1):
        report.warn("overview_fingerprint_stale",
                    "index/relations changed since this overview page was generated — "
                    "regenerate via build_wiki_overview.py", path=rel)



# CR-AIWS-2026-07-023: curated synthesis pages (source_type: wiki_page). Two rules:
#   page_sources_missing (ERROR) — a REGISTERED page must be grounding-traceable:
#     page has a non-empty `## Sources` table AND meta carries >=1 `x:synthesized_from` edge.
#   page_grounding_stale (WARN) — for an `active` page, a grounding source whose updated_at is
#     newer than the page `last_verified_at`, or a grounding source that is no longer in the index.
WIKI_PAGE_SOURCE_TYPE = "wiki_page"


@lru_cache(maxsize=8)
def _wiki_page_index(proot_str: str) -> dict:
    # CR-AIWS-2026-07-068 (Rule 6): resolve grounding ids across EVERY registered index via the shared
    # helper, not just index.jsonl. Reading only index.jsonl reported every grounding source registered
    # in index.aiws.jsonl as "deregistered" (27 false page_grounding_stale on the aiws pages). Same
    # aiws_meta blind-spot the sibling relations check already fixed with _all_index_paths (CR-049).
    ws = Path(proot_str) / ".ai-work" / "wiki_sources"
    out: dict = {}
    for idx in _all_index_paths(ws):
        for line in idx.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
                out[r.get("source_id")] = r
            except Exception:  # noqa: BLE001
                pass
    return out


def _wp_parse_date(v):
    if not v:
        return None
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", str(v).strip())
    if m:
        try:
            return tuple(int(x) for x in m.groups())
        except Exception:  # noqa: BLE001
            return None
    return None


def _wp_src_updated(rec, proot):
    if rec.get("updated_at"):
        return rec["updated_at"]
    # CR-AIWS-2026-07-064 A2 (Rule 9): index records are DATA — a non-string meta_locator crashed
    # resolve_locator, and an exists()-only guard let a directory reach read_text().
    mp = resolve_data_file(rec.get("meta_locator"), proot)
    if mp is not None:
        try:
            mm, _ = parse_frontmatter(read_text(mp))
        except Exception:  # noqa: BLE001
            return None
        return mm.get("updated_at")
    return None


def _lint_wiki_page(meta: dict, path: Path, report: LintReport, rel: str) -> None:
    proot = None
    for parent in path.resolve().parents:
        if (parent / ".ai-work").is_dir():
            proot = parent
            break
    if proot is None:
        proot = path.resolve().parent
    # CR-AIWS-2026-07-064 A1 (Rule 9): normalize the frontmatter value before it becomes a path.
    art = resolve_data_file(meta.get("artifact_locator"), proot)
    if art is None:
        return  # orphan check's concern
    try:
        ptext = read_text(art)
    except Exception:  # noqa: BLE001
        return
    pmeta, pbody = parse_frontmatter(ptext)
    psecs = extract_sections(pbody)
    sources_body = psecs.get("Sources", "")
    src_ids = re.findall(r"^\s*\|\s*\[S\d+\]\s*\|\s*([A-Za-z0-9_\-]+)\s*\|", sources_body, re.M)
    _, mbody = parse_frontmatter(read_text(path))
    rel_body = extract_sections(mbody).get("Related Sources", "")
    edge_ids = re.findall(r"-\s*\*\*([A-Za-z0-9_\-]+)\*\*", rel_body)
    has_synth_edge = "x:synthesized_from" in rel_body

    if ("Sources" not in psecs) or (not src_ids) or (not has_synth_edge):
        report.error("page_sources_missing",
                     "registered wiki page not grounding-traceable — needs a non-empty `## Sources` "
                     "table AND a meta `x:synthesized_from` Related Sources edge", path=rel)

    if pmeta.get("status") == "active":
        lv = _wp_parse_date(pmeta.get("last_verified_at"))
        idx = _wiki_page_index(str(proot))
        for gid in dict.fromkeys(list(src_ids) + list(edge_ids)):
            rec = idx.get(gid)
            if rec is None:
                report.warn("page_grounding_stale",
                            f"grounding source '{gid}' not in index (deregistered) — re-synthesis review",
                            path=rel)
                continue
            su = _wp_parse_date(_wp_src_updated(rec, proot))
            if lv and su and su > lv:
                report.warn("page_grounding_stale",
                            f"grounding '{gid}' updated {su[0]:04d}-{su[1]:02d}-{su[2]:02d} > verified "
                            f"{lv[0]:04d}-{lv[1]:02d}-{lv[2]:02d} — re-synthesis review", path=rel)


def _lint_source_meta(path: Path, report: LintReport) -> None:
    rel = str(path)
    text = read_text(path)
    meta, body = parse_frontmatter(text)
    if not meta:
        report.error("meta_missing", "no frontmatter on source meta", path=rel)
        return
    if meta.get("artifact_type") != "wiki_source_meta":
        report.warn("meta_type",
                    f"artifact_type != wiki_source_meta (got {meta.get('artifact_type')})",
                    path=rel)
    # Two-kind node model (CR-AIWS-2026-05-023): node_kind is meta-only, default 'artifact'
    # (DP2 — zero migration). is_object drives the object-scoped INV guards below.
    node_kind = meta.get("node_kind") or NODE_KIND_ARTIFACT
    is_object = node_kind == NODE_KIND_OBJECT
    # profile_id is REQUIRED for ALL metas incl. node_kind=object — object metas carry
    # profile_id: knowledge_object (CR-AIWS-2026-06-004 C1; supersedes CR-035 OP-2 omit-exemption).
    # EXCEPT binary-by-design stubs (CR-AIWS-2026-06-066): not_meta_applicable metas have no text
    # body → profile_id is intentionally absent (scoped exemption from CR-004 C1). Identity fields stay required.
    not_applicable = meta.get("not_meta_applicable") is True
    # H6 (CR-AIWS-2026-07-002): chunked section metas. `section_lines` must be "start-end" with
    # start<=end; `section_heading` requires `section_lines`. The retired-KO field name `source_anchor`
    # stays forbidden (INV-3) — H6 uses `section_lines`, never `source_anchor`.
    if "source_anchor" in meta:
        report.error("meta_source_anchor", "forbidden field `source_anchor` (INV-3); use section_lines", path=rel)
    _sl = meta.get("section_lines")
    if _sl is not None and str(_sl).strip():
        _m = re.fullmatch(r"(\d+)-(\d+)", str(_sl).strip())
        if not _m:
            report.error("meta_section_lines", f"section_lines '{_sl}' must be 'start-end' (integers)", path=rel)
        elif int(_m.group(1)) > int(_m.group(2)):
            report.error("meta_section_lines", f"section_lines '{_sl}' has start > end", path=rel)
    if meta.get("section_heading") and not (_sl and str(_sl).strip()):
        report.warn("meta_section_heading", "section_heading without section_lines (range unknown)", path=rel)
    # CR-AIWS-2026-07-006 T6 (lint rule, cr_required per CR-037): range-vs-heading — a chunked
    # child's section_lines must still point at ITS heading in the live artifact; a drifted range
    # silently serves the WRONG lines, so mismatch = ERROR (re-chunk the source: refresh mode now
    # rebuilds children — CR-006 A1).
    if (meta.get("section_heading") and _sl and str(_sl).strip()
            and re.fullmatch(r"(\d+)-(\d+)", str(_sl).strip())):
        _start = int(str(_sl).split("-")[0])
        _al = str(meta.get("artifact_locator", ""))
        if _al and _al != OBJECT_LOCATOR_SENTINEL and "://" not in _al:
            _proot = None
            for _parent in path.parents:
                if _parent.name == ".ai-work":
                    _proot = _parent.parent
                    break
            if _proot is not None:
                _loc = _al.split("#")[0].strip()
                if _loc.startswith("__PROJECT_ROOT__"):
                    _art = _proot / _loc[len("__PROJECT_ROOT__"):].replace("\\", "/").lstrip("/")
                elif (len(_loc) >= 2 and _loc[1] == ":") or _loc.startswith("/"):
                    _art = Path(_loc)
                else:
                    _art = _proot / _loc.replace("\\", "/").lstrip("/")
                if _art.exists():
                    try:
                        _art_lines = read_text(_art).splitlines()
                        _head_line = _art_lines[_start - 1].strip() if _start - 1 < len(_art_lines) else ""
                        if _head_line != f"## {meta.get('section_heading')}".strip():
                            report.error(
                                "chunk_range_vs_heading",
                                f"section_lines '{_sl}' does not start at heading "
                                f"'## {meta.get('section_heading')}' in the artifact (found: "
                                f"{_head_line[:60]!r}) — source drifted; re-chunk via refresh",
                                path=rel)
                    except Exception:  # noqa: BLE001
                        pass  # unreadable artifact is the orphan check's concern, not this rule's
    # CR-AIWS-2026-07-010: generated overview pages — hand-edit (ERROR) + staleness (WARN).
    if meta.get("source_type") == OVERVIEW_SOURCE_TYPE:
        _lint_overview_page(meta, path, report, rel)
    if meta.get("source_type") == WIKI_PAGE_SOURCE_TYPE:
        _lint_wiki_page(meta, path, report, rel)
    # H1 (CR-AIWS-2026-07-002) completion-layer guard: a meta still flagged needs_completion is NOT a
    # finished meta — the completion step (LLM fills summary/lookup_keys/related_sources) must clear it
    # before it is treated as index-ready/done.
    _nc = meta.get("needs_completion")
    if _nc:
        report.error("meta_needs_completion",
                     f"partial meta (needs_completion={_nc}) — run the completion step before index/done",
                     path=rel)
    # H5 (CR-AIWS-2026-07-002): diagrams recorded but the representation is not marked partial → the
    # diagram content would be silently treated as fully captured.
    _cl = meta.get("conversion_limitations") or []
    if any(str(x).startswith("diagrams_present:") for x in _cl):
        if meta.get("source_representation_status") not in ("partial", "needs_review", "failed"):
            report.warn("meta_diagram_partial",
                        "diagrams_present recorded but source_representation_status is not partial/needs_review",
                        path=rel)
    required_fields = ([k for k in META_REQUIRED if k != "profile_id"]
                       if not_applicable else META_REQUIRED)
    for k in required_fields:
        if k not in meta or meta[k] in (None, "", []):
            report.error("meta_field", f"missing field: {k}", path=rel)
    # CR-AIWS-2026-06-024: updated_at (optional on source metas) accepts date OR UTC ISO 8601 timestamp.
    ua = meta.get("updated_at")
    if ua and not _valid_ts_or_date(ua):
        report.warn("meta_ts_format",
                    f"updated_at should be a date (YYYY-MM-DD) or UTC ISO 8601 timestamp: {ua}",
                    path=rel)
    # not_meta_applicable stubs intentionally omit Summary/Knowledge Targets/Lookup Keys (CR-066).
    if not not_applicable:
        for sec in META_SECTIONS:
            if not has_section(body, sec):
                report.error("meta_section", f"missing section: {sec}", path=rel)
    # IR-14: flag degenerate/placeholder Summary. WARN for artifact metas; promoted to
    # ERROR for node_kind=object metas (CR-AIWS-2026-05-023 INV-4: an object is never empty).
    if has_section(body, "Summary"):
        summary_text = (extract_sections(body).get("Summary", "") or "").strip()
        if (not summary_text
                or summary_text.startswith("(no semantic summary")
                or len(summary_text) < 40):
            if is_object:
                report.error("meta_summary_degenerate",
                             "Summary is empty/placeholder or too short; a node_kind=object meta "
                             "must carry a real summary (CR-023 INV-4: objects are never empty)",
                             path=rel)
            else:
                report.warn("meta_summary_degenerate",
                            "Summary is empty/placeholder or too short to be useful; "
                            "rebuild with --summary for a quality meta",
                            path=rel)
    # CR-AIWS-2026-07-037 T2 (WARN — DP-037-1=A): lookup-keys soft budget. The index projects
    # keys LOSSLESSLY (no positional cap since CR-037) — key-count hygiene lives HERE, meta layer.
    if has_section(body, "Lookup Keys"):
        _lk_bullets = [ln for ln in (extract_sections(body).get("Lookup Keys", "") or "").splitlines()
                       if ln.strip().startswith("- ")
                       and not (ln.strip()[2:].strip().startswith("(") and ln.strip().endswith(")"))]
        if len(_lk_bullets) > LOOKUP_KEYS_SOFT_BUDGET:
            report.warn("meta_lookup_keys_over_budget",
                        f"meta declares {len(_lk_bullets)} lookup keys (> budget {LOOKUP_KEYS_SOFT_BUDGET}) — "
                        "curate: merge near-duplicates, drop generic terms, keep one best discriminator per "
                        "concept (Buildup Guideline Appendix C); keys are still indexed IN FULL (lossless) — "
                        "hygiene signal, not a truncation",
                        path=rel)
        # CR-AIWS-2026-08-107 C1 (WARN) — rule ANH EM của over_budget: cái trên đếm SỐ LƯỢNG
        # key, cái này xét HÌNH DẠNG của từng key. Cả hai đều là hygiene ở tầng meta.
        for _ln in _lk_bullets:
            _key = _ln.strip()[2:].strip()
            _mark = _lookup_key_marker_midname(_key)
            if _mark:
                report.warn("meta_lookup_key_marker_midname",
                            f"lookup key {_key!r} có nhãn {_mark!r} chèn GIỮA tên — matching là "
                            "NGUYÊN CỤM nên key này ăn 0 điểm cho người gõ tên tài liệu mà không "
                            "kèm phiên bản. Sửa: gỡ nhãn khỏi key tên; nếu THẬT SỰ có nhiều bản "
                            "cùng active thì THÊM một key riêng mang phiên bản, đừng sửa key tên. "
                            "Bản cũ thì dùng `status: superseded` (đã có phạt điểm) thay vì ghi "
                            "trạng thái vào chữ của key — Lookup_Key_Strategy_Spec §7.4",
                            path=rel)

    # CR-AIWS-2026-08-092 C3 — curator marker: `related_sources: none_by_design` means "no
    # relationships, on purpose". A meta carrying it must NOT also carry a `## Related Sources`
    # section (one of the two is wrong); without the section it is simply exempt from the TODO
    # warning below (and builder/refresh do not re-scaffold it).
    _rs_marker = str(meta.get("related_sources", "") or "").strip() == "none_by_design"
    if _rs_marker and has_section(body, "Related Sources"):
        report.warn("meta_related_sources_marker_conflict",
                    "frontmatter says `related_sources: none_by_design` but the body still has a "
                    "`## Related Sources` section — drop the section or drop the marker "
                    "(CR-AIWS-2026-08-092)",
                    path=rel)
    # CR-017: warn on unresolved Related Sources scaffold (left-over TODO markers)
    if has_section(body, "Related Sources"):
        rs_text = extract_sections(body).get("Related Sources", "") or ""
        if ("<SRC-id: TODO>" in rs_text) or ("TODO: fill real source_ids" in rs_text):
            report.warn("meta_related_sources_todo",
                        "Related Sources scaffold left unresolved (contains <SRC-id: TODO>); "
                        "fill real source_ids, or set frontmatter `related_sources: none_by_design` "
                        "and drop the section if this source has no relationships "
                        "(CR-AIWS-2026-08-092)",
                        path=rel)
        # CR-AIWS-2026-06-002: warn (never error) a data-flow edge left with a blank basis note.
        # Conservative — detects ABSENCE of a note only; cannot judge whether a note is meaningful.
        try:
            import build_relations as _br
            for _edge in _br.parse_related_sources(rs_text):
                if (_edge.get("relationship_type") in DATA_FLOW_TYPES
                        and not (_edge.get("relationship_basis_note") or "").strip()):
                    report.warn("relations_thin_basis",
                                f"data-flow edge → {_edge.get('target_ref','?')} "
                                f"(role: {_edge.get('relationship_type')}) has no basis note; add objective "
                                f"stakes/coupling per Knowledge_Expansion_Link_Spec §4.4",
                                path=rel)
        except Exception:  # noqa: BLE001
            pass
        # CR-AIWS-2026-07-032 T1 (ERROR — DP-032-2=A): shape/resolution INTEGRITY of every
        # Related Sources bullet, at meta level (the projection-side relations_broken_ref WARN
        # stays as backstop). Shape = spec §4.3: canonical typed AND legacy-untyped both carry
        # a **bold** target id; a bullet without one projects a garbage target_ref. Resolution:
        # the bold target must be a known source_id (meta set + sibling indexes). This ERROR
        # class scopes only shape/resolution — relation-TYPE semantics stay warn-not-error
        # per spec §4.1 (type registry).
        _lint_related_sources_integrity(path, rs_text, report, rel)
        # CR-AIWS-2026-07-038 T4 (ERROR — DP-038-3=A): representation-direction invariant.
        # Representation flows artifact → object: after inverse-normalization the source_ref
        # of a represents/describes edge must NEVER be a node_kind=object meta. One wrong word
        # (`represents` vs `represented_by`) silently inverts the edge (round-3 R3-02) —
        # build_relations normalizes+accepts it and no other rule reads direction.
        # Both authoring paths are caught: (a) object meta declares the forward role;
        # (b) artifact meta declares the inverse role targeting an object node.
        import build_relations as _brd
        _rep_inv = {"represented_by": "represents", "described_by": "describes"}
        _mr = next((p for p in path.parents if p.name in ("meta", "aiws_meta")), None)
        _obj_ids = _known_object_ids(_mr) if _mr is not None else set()
        _sid = str(meta.get("source_id") or path.stem)
        for _edge in _brd.parse_related_sources(rs_text):
            _t = _edge.get("relationship_type", "")
            _tgt = _edge.get("target_ref", "")
            if _t in ("represents", "describes") and is_object:
                _fix = "represented_by" if _t == "represents" else "described_by"
                report.error("representation_edge_inverted",
                             f"node_kind=object meta declares `role: {_t}` — edge "
                             f"'{_sid} --{_t}--> {_tgt}' puts the OBJECT as source_ref; "
                             f"representation flows artifact → object: declare `role: {_fix}` "
                             f"on the object side instead (CR-AIWS-2026-07-038 T4)",
                             path=rel)
            elif _t in _rep_inv and _tgt in _obj_ids:
                report.error("representation_edge_inverted",
                             f"`role: {_t}` targeting object node '{_tgt}' normalizes to "
                             f"'{_tgt} --{_rep_inv[_t]}--> {_sid}' — an OBJECT as source_ref; "
                             f"representation flows artifact → object: declare `role: {_t}` "
                             f"FROM the object '{_tgt}' pointing at '{_sid}' instead "
                             f"(CR-AIWS-2026-07-038 T4)",
                             path=rel)
    for k in WTA_OPTIONAL_META_FIELDS:
        if k not in meta or meta[k] in (None, "", []):
            report.info("meta_wta_field",
                        f"recommended WTA field missing: {k}",
                        path=rel)

    for k in SRI_OPTIONAL_META_FIELDS:
        if k not in meta or meta[k] in (None, "", []):
            report.info("meta_sri_field",
                        f"recommended SRI field missing: {k}",
                        path=rel)

    source_type = meta.get("source_type", "")
    ai_work = _ai_work_for(path)
    allowed_types = (_allowed_source_types(str(ai_work / "wiki_sources" / "profiles"))
                     if ai_work else frozenset(SOURCE_TYPE_VOCAB))
    if source_type and source_type not in allowed_types:
        report.warn("meta_source_type_unknown",
                    f"unrecognized source_type '{source_type}'; use a canonical base value "
                    f"or declare it via a profile's source_type (wiki_sources/profiles/)",
                    path=rel)

    authority = meta.get("authority_level")
    if authority and authority not in AUTHORITY_LEVEL_ENUM:
        report.warn("meta_authority",
                    f"unknown authority_level: {authority}",
                    path=rel)

    # CR-AIWS-2026-07-064 A3 (Rule 9): normalize ONCE — these three feed .startswith()/slicing
    # below, and a flow-list value ([...]) used to abort the whole lint run with AttributeError.
    artifact_locator = locator_str(meta.get("artifact_locator"))
    original_locator = locator_str(meta.get("original_source_locator"))
    representation_locator = locator_str(meta.get("representation_locator"))

    # ── Two-kind node model invariants (CR-AIWS-2026-05-023) ──────────────────
    # INV-2: the retired 3-layer Knowledge-Object record fields must never reappear as a
    # frontmatter KEY in ANY meta (object OR artifact) — ERROR. (Body text / lookup_keys that
    # merely mention these terms — e.g. a spec describing their removal — is fine; only a
    # real frontmatter key is forbidden.)
    for forbidden in ("object_id", "expansion_links", "canonical_object_refs", "source_anchor"):
        if forbidden in meta:
            report.error("meta_forbidden_ko_field",
                         f"forbidden frontmatter field '{forbidden}' — retired Knowledge-Object "
                         f"record field (CR-023 INV-2)",
                         path=rel)
    # INV-9: the __OBJECT__ sentinel and node_kind=object must agree (both directions).
    if artifact_locator == OBJECT_LOCATOR_SENTINEL and not is_object:
        report.error("meta_object_sentinel_misuse",
                     f"artifact_locator={OBJECT_LOCATOR_SENTINEL} is reserved for node_kind=object "
                     f"metas (CR-023 INV-9)",
                     path=rel)
    if is_object and artifact_locator != OBJECT_LOCATOR_SENTINEL:
        report.error("meta_object_locator",
                     f"node_kind=object meta must set artifact_locator: {OBJECT_LOCATOR_SENTINEL} "
                     f"(CR-023 INV-9)",
                     path=rel)
    if is_object:
        # INV-4: an object is never empty — it must declare >=1 ## Related Sources out-edge.
        rs_text = extract_sections(body).get("Related Sources", "")
        try:
            import build_relations as _br
            n_out = len(_br.parse_related_sources(rs_text))
        except Exception:  # noqa: BLE001
            n_out = 1 if rs_text.strip() else 0
        if n_out == 0:
            report.error("meta_object_no_outedge",
                         "node_kind=object meta declares no ## Related Sources out-edge "
                         "(CR-023 INV-4: an object must never be empty — needs >=1 out-edge)",
                         path=rel)
        # INV-3 / DP5: an object is a POINTER, never a container/aggregator.
        if re.search(r"(?im)^#{1,3}\s*(Contents|Aggregated|Synthesized|Child Sources)\b", body):
            report.error("meta_object_aggregation_heading",
                         "node_kind=object meta carries an aggregation heading "
                         "(Contents/Aggregated/Synthesized/Child Sources) — objects are pointers, "
                         "not containers (CR-023 DP5/INV-3)",
                         path=rel)
        if "wiki_sources/objects" in text:
            report.error("meta_object_store_ref",
                         "node_kind=object meta references a wiki_sources/objects/ store — the "
                         "retired Knowledge-Object store is forbidden (CR-023 INV-1/INV-3)",
                         path=rel)
    # ──────────────────────────────────────────────────────────────────────────

    if _looks_raw_non_text(artifact_locator):
        report.warn("meta_artifact_raw_non_text",
                    "artifact_locator appears to point to raw/non-text file; runtime artifact_locator should point to AIWS-readable representation",
                    path=rel)
    # DESIGN-04: flag absolute paths — meta files should store project-relative paths
    if artifact_locator and (
        (len(artifact_locator) >= 2 and artifact_locator[1] == ":")
        or artifact_locator.startswith("/")
    ):
        report.error("meta_absolute_locator",
                     "artifact_locator contains an absolute path; use a project-relative path for portability",
                     path=rel)
    # CR-AIWS-2026-05-007: orphan doctor check — meta points to a nonexistent artifact.
    # Complements the index→meta stale check (build_wiki_source_index.py). Warn-level so
    # intentional external/remote placeholders don't break CI.
    _orphan_artifact_check(path, artifact_locator, report, rel)
    # CR-AIWS-2026-07-021 (IR-C): representation_locator is legitimately OMITTED when it equals
    # artifact_locator (WIKI_META_INDEX_SPEC omit-when-equal), and the AIWS-readable artifact_locator
    # then serves as the representation. Only warn when there is NO effective AIWS-readable
    # representation at all (i.e. the artifact_locator is itself a raw binary) — the genuine-missing case.
    effective_rep = representation_locator or (
        artifact_locator if _looks_aiws_readable(artifact_locator) else "")
    if original_locator and not effective_rep:
        report.warn("meta_missing_representation_locator",
                    "original_source_locator exists but there is no AIWS-readable representation "
                    "(neither representation_locator nor an AIWS-readable artifact_locator)",
                    path=rel)
    if representation_locator and not _looks_aiws_readable(representation_locator):
        report.warn("meta_representation_locator_not_text",
                    "representation_locator does not appear to be markdown/text/structured AI-readable format",
                    path=rel)

    rep_status = meta.get("source_representation_status")
    if rep_status and rep_status not in SOURCE_REPRESENTATION_STATUS_ENUM:
        report.warn("meta_representation_status",
                    f"unknown source_representation_status: {rep_status}",
                    path=rel)
    if rep_status in {"partial", "needs_review", "failed"} and not meta.get("source_representation_caution"):
        report.warn("meta_representation_caution",
                    "source representation status requires caution text",
                    path=rel)
    if meta.get("source_representation_quality_issue") is True and not (
        meta.get("source_representation_caution") or meta.get("review_required")
    ):
        report.warn("meta_representation_issue",
                    "source_representation_quality_issue=true should include caution/review_required",
                    path=rel)

    promotion = meta.get("promotion_status")
    if promotion and promotion not in PROMOTION_STATUS_ENUM:
        report.warn("meta_promotion_status",
                    f"unknown promotion_status: {promotion}",
                    path=rel)
    if promotion == "approved" and not (
        meta.get("review_status") or meta.get("last_reviewed_at") or meta.get("change_summary")
    ):
        report.warn("meta_promotion_trace",
                    "promotion_status=approved should have review trace/change summary",
                    path=rel)

    if meta.get("review_required") is True and not (
        meta.get("next_action") or meta.get("source_representation_caution") or meta.get("review_status")
    ):
        report.warn("meta_review_required",
                    "review_required=true should have next_action/caution/review_status",
                    path=rel)

    if meta.get("maintenance_status") in {"needs_review", "stale"}:
        report.warn("meta_maintenance_status",
                    f"maintenance_status indicates review: {meta.get('maintenance_status')}",
                    path=rel)

    if len(text) > 8_000:
        report.warn("meta_heavy",
                    f"source meta is large ({len(text)} bytes) — may be too heavy",
                    path=rel)

    # CR-AIWS-2026-06-020: flag stray tool-call/markup artifacts in the meta body.
    # Raw line-walk (NOT extract_sections, which folds the tail into the last section and
    # hides the junk). WARN-level so the sec_lint_negative error-only/rc==2 contract is
    # preserved; surfaced by --strict.
    for ln in body.splitlines():
        if _TRAILING_JUNK_RE.search(ln):
            report.warn("meta_trailing_junk",
                        f"stray tool-call/markup artifact in meta body: {ln.strip()[:60]!r}",
                        path=rel)
            break

    # CR-AIWS-2026-06-017: optional `system` scope axis. NOT required (absent = common).
    # When the project is multi_system, a non-empty `system` must be a declared project system.
    ai_work_dir = next((par for par in path.parents if par.name == ".ai-work"), None)
    if ai_work_dir is not None:
        ms, systems, synthetic = _ms_config(str(ai_work_dir))
        sysval = str(meta.get("system", "")).strip()
        if ms and sysval and systems and sysval not in systems:
            report.warn("meta_system",
                        f"system {sysval!r} not in project systems {sorted(systems)} "
                        f"(project_profile.yml)", path=rel)
        # CR-AIWS-2026-07-028: fixture-namespace guardrail. A fixture artifact registered under
        # a REAL system poisons every wiki page grounded on that system (incident OP-931-03:
        # 3 fictional RDs under `aiws` were the system's ONLY requirement_definitions). Active
        # only when the project declares synthetic_systems (absent → no-op, backward compat).
        _loc = str(meta.get("artifact_locator", "")).replace("\\", "/")
        if (ms and synthetic and sysval and sysval not in synthetic
                and ("/tests/fixtures/" in _loc or "/fixtures/" in _loc)):
            report.error(
                "fixture_under_real_system",
                f"fixture artifact registered under REAL system {sysval!r} — dùng một system "
                f"tổng hợp (synthetic_systems: {sorted(synthetic)}); tài liệu hư cấu trong "
                f"namespace của system thật sẽ đầu độc mọi trang wiki grounded trên system đó "
                f"(sự cố OP-931-03, CR-AIWS-2026-07-028)", path=rel)


def _lint_source_index(path: Path, report: LintReport) -> None:
    rel = str(path)
    try:
        records = read_jsonl(path)
    except ValueError as e:
        report.error("index_parse", str(e), path=rel)
        return
    seen_ids: set[str] = set()
    for idx, rec in enumerate(records, start=1):
        loc = f"line {idx}"
        # Binary-by-design stubs (CR-066): index projects not_meta_applicable:true; exempt the
        # text-meta fields such stubs intentionally lack.
        idx_exempt = ({"profile_id", "summary_short", "knowledge_targets"}
                      if rec.get("not_meta_applicable") is True else set())
        for k in INDEX_REQUIRED:
            if k in idx_exempt:
                continue
            if k not in rec or rec[k] in (None, "", []):
                report.error("index_field", f"missing field: {k}", path=rel, loc=loc)
        sid = rec.get("source_id")
        if sid and sid in seen_ids:
            report.error("index_dup", f"duplicate source_id: {sid}", path=rel, loc=loc)
        if sid:
            seen_ids.add(sid)
        if "meta_locator" not in rec and "meta_id" not in rec:
            report.error("index_no_meta_ref",
                         "entry has neither meta_locator nor meta_id", path=rel, loc=loc)
        if not rec.get("lookup_keys"):
            report.warn("index_weak_lookup",
                        "entry has no lookup_keys surface", path=rel, loc=loc)
        for k in ("authority_level", "freshness_status", "source_representation_status", "promotion_status"):
            if k not in rec:
                report.info("index_wta_field",
                            f"recommended WTA projection field missing: {k}",
                            path=rel, loc=loc)

        rep_status = rec.get("source_representation_status")
        if rep_status and rep_status not in SOURCE_REPRESENTATION_STATUS_ENUM:
            report.warn("index_representation_status",
                        f"unknown source_representation_status: {rep_status}",
                        path=rel, loc=loc)

        promotion = rec.get("promotion_status")
        if promotion and promotion not in PROMOTION_STATUS_ENUM:
            report.warn("index_promotion_status",
                        f"unknown promotion_status: {promotion}",
                        path=rel, loc=loc)

        recommendation = rec.get("recommendation")
        if recommendation and recommendation in UNSAFE_RECOMMENDATIONS:
            report.error("index_unsafe_recommendation",
                         f"unsafe recommendation: {recommendation}",
                         path=rel, loc=loc)

        summary = rec.get("summary_short") or ""
        if len(summary) > 500:
            report.warn("index_heavy_summary",
                        f"summary_short too long ({len(summary)} chars)",
                        path=rel, loc=loc)
        # projection guard: index entry should not embed fat bodies
        for fat_key in ("full_meta", "body", "raw", "full_source", "source_body", "meta_body"):
            if fat_key in rec:
                report.error("index_projection",
                             f"entry contains fat field '{fat_key}' (violates projection rule)",
                             path=rel, loc=loc)



def _lint_maintenance_log(path: Path, report: LintReport) -> None:
    rel = str(path)
    # Per-line tolerant parse (IR-09): a single corrupt line must record one
    # parse error but must NOT suppress checks on every other record / mask
    # aggregate counts. Mirrors read_jsonl's BOM + null handling.
    records: list[dict] = []
    if path.exists():
        for i, raw in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), start=1):
            raw = raw.strip().strip("\x00")
            if not raw:
                continue
            try:
                records.append(json.loads(raw))
            except json.JSONDecodeError as e:
                report.error("maintenance_log_parse", f"line {i}: {e}",
                             path=rel, loc=f"line {i}")

    seen: set[str] = set()
    for idx, rec in enumerate(records, start=1):
        loc = f"line {idx}"
        for k in WSM_REQUIRED_LOG_FIELDS:
            if k not in rec or rec[k] in (None, "", []):
                report.warn("maintenance_log_field",
                            f"maintenance log missing field: {k}",
                            path=rel, loc=loc)
        log_id = rec.get("log_id")
        if log_id and log_id in seen:
            report.error("maintenance_log_dup",
                         f"duplicate maintenance log_id: {log_id}",
                         path=rel, loc=loc)
        if log_id:
            seen.add(log_id)

        action = rec.get("action")
        if action and action not in WSM_ACTION_ENUM:
            report.info("maintenance_log_action",
                        f"unknown maintenance action: {action}",
                        path=rel, loc=loc)

        recommendation = rec.get("recommendation")
        if recommendation and recommendation in UNSAFE_RECOMMENDATIONS:
            report.error("maintenance_log_unsafe_recommendation",
                         f"unsafe recommendation: {recommendation}",
                         path=rel, loc=loc)

        if action in {"meta_applied", "index_rebuilt"} and not rec.get("rollback_hint"):
            report.warn("maintenance_log_rollback",
                        "applied/rebuild action should have rollback_hint",
                        path=rel, loc=loc)


def _lint_relations(path: Path, index_path: Path, meta_dir: Path, report: LintReport) -> None:
    """Lint the relations.jsonl projection (CR-AIWS-2026-05-022).

    Warn-not-error, skip-if-absent: relations.jsonl is an OPTIONAL projection.
    Checks: malformed edge (missing core fields), broken target/source ref (not
    resolvable in the index), unknown BARE relationship_type, and a staleness
    rebuild HINT (a non-empty projection older than the newest meta). All findings
    are warnings (never errors) except a hard parse failure. Object-scoped lints
    (non-aggregation, degenerate-summary→error, etc.) are DEFERRED to CR-023.
    """
    rel = str(path)
    if not path.exists():
        return
    try:
        edges = read_jsonl(path)
    except ValueError as e:
        report.error("relations_parse", str(e), path=rel)
        return

    # CR-AIWS-2026-07-048: relations.jsonl now carries edges authored on BOTH meta namespaces
    # (project `meta/` + shipped `aiws_meta/`), so a target must resolve against BOTH indices —
    # resolving only against index.jsonl reported every AIWS-side edge as a broken ref.
    known_ids: set = set()
    for _idx in _all_index_paths(index_path.parent):
        try:
            known_ids |= {r.get("source_id", "") for r in read_jsonl(_idx)}
        except ValueError:
            pass

    try:
        import build_relations as _br
        known_types, ext_prefix = _br.KNOWN_RELATION_TYPES, _br.EXTENSION_PREFIX
    except Exception:  # noqa: BLE001
        known_types, ext_prefix = set(), "x:"

    for i, e in enumerate(edges, start=1):
        loc = f"line {i}"
        for k in ("relationship_type", "source_ref", "target_ref"):
            if not e.get(k):
                report.warn("relations_field", f"edge missing field: {k}", path=rel, loc=loc)
        src, tgt, rtype = e.get("source_ref", ""), e.get("target_ref", ""), e.get("relationship_type", "")
        if known_ids:
            if tgt and tgt not in known_ids:
                report.warn("relations_broken_ref",
                            f"target_ref not in index: {src} --{rtype}--> {tgt}", path=rel, loc=loc)
            if src and src not in known_ids:
                report.warn("relations_orphan_source",
                            f"source_ref not in index: {src}", path=rel, loc=loc)
        if rtype and not (rtype.startswith(ext_prefix) or rtype in known_types):
            report.warn("relations_unknown_type",
                        f"unknown relationship_type '{rtype}' (promote via CR or namespace as x:)",
                        path=rel, loc=loc)

    # staleness HINT: a non-empty projection older than the newest meta → rebuild
    if edges and meta_dir.is_dir():
        try:
            # CR-AIWS-2026-07-010: overview metas are projections-of-projections regenerated
            # AFTER relations in the maintenance chain (relations → overview → index) and never
            # carry edges — excluding them avoids a permanent false relations_stale.
            newest_meta = max((f.stat().st_mtime for f in meta_dir.rglob("*.md")
                               if f.parent.name != "overview"), default=0.0)
            if path.stat().st_mtime < newest_meta:
                report.warn("relations_stale",
                            "relations.jsonl is older than the newest meta — rebuild with build_relations.py",
                            path=rel)
        except OSError:
            pass


def _lint_object_node_invariants(ai_work: Path, report: LintReport) -> None:
    """Repo-structure anti-KO guards for the two-kind node model (CR-AIWS-2026-05-023).

    ERROR-grade CI guards so a node_kind=object meta can never drift back into the retired
    3-layer Knowledge-Object record:
      INV-8: hand-authored only — no _pending_object_refresh.jsonl refresh queue, and
             build_relations.py must not write into wiki_sources/meta/.
      INV-8: no functional build-/refresh-knowledge-object skill — any such SKILL.md must stay a
             retired tombstone (status: retired, not user-invocable) in every skill tree.
      INV-1: one store / no separate object store (wiki_sources/objects/).

    SCOPE — read this before trusting a green run (CR-AIWS-2026-08-030):
    "hand-authored only" is NO LONGER absolute. Knowledge_Object_Model_Spec_MVP §3bis.5(7) (v0.4+;
    the retired-shape list itself lives in that spec's §8 since v0.5)
    carves out an exception: a PO-approved deterministic build route MAY instantiate object metas
    when it (1) writes only its own sentinel-marked nodes and never overwrites a node carrying a
    real artifact_locator, and (2) derives node content deterministically from a catalog/source.
    CR-AIWS-2026-08-026 (ASP COBOL preset) is the first such route. AI auto-creating an object
    meta by judgment is STILL forbidden — that is what INV-8 exists to stop.

    Consequently these checks do NOT verify the general proposition. Each one guards a specific
    LEGACY KO shape (one named queue file, one named tool, two named skills); a new builder can
    emit object metas without tripping any of them, and CR-026's does. The overwrite hazard is
    covered elsewhere (F10 of ASP_COBOL_SOURCE_BUILD_GUIDE), not here. If you need a guard that
    catches arbitrary builders, it does not exist yet — do not read a green run as proof.

    The INV-8 "no build/refresh-knowledge-object skill" clause was deferred by AIP-049 to ship
    WITH the skill removal (the skills were CR-gated — CAP-049-01). It landed in AIP-055 (CR-035
    Change 10) AFTER the Change-9 tombstones, so CI does not go red on a pre-existing leak.

    Called from this module's main() AND from lint_all.main() (the CI driver), mirroring
    _check_duplicate_artifact_ids — so the guard runs in every full lint.
    """
    wiki_sources = ai_work / "wiki_sources"

    # INV-1 — one store / one index: no separate Knowledge-Object store. wiki_sources/objects/
    # was the retired Layer-2 store (CR-005/CR-020 removed the layer; this is the remaining
    # CR-022 cleanup CI assertion). Object metas live in wiki_sources/meta/ like any artifact.
    objects_dir = wiki_sources / "objects"
    if objects_dir.exists():
        report.error("object_store_present",
                     "wiki_sources/objects/ exists — the retired Knowledge-Object store is "
                     "forbidden; object metas live in wiki_sources/meta/ (CR-023 INV-1)",
                     path=str(objects_dir))

    # INV-8 — no tool-driven object refresh queue (the retired KO had one).
    for q in (wiki_sources / "_pending_object_refresh.jsonl",
              ai_work / "_pending_object_refresh.jsonl"):
        if q.exists():
            report.error("object_refresh_queue_present",
                         "_pending_object_refresh.jsonl exists — objects are hand-authored only; "
                         "no tool refresh queue (CR-023 INV-8)",
                         path=str(q))

    # INV-8 — build_relations.py must only project relations.jsonl, never write object metas
    # into wiki_sources/meta/. Heuristic source guard: flag a write_jsonl/write_text call whose
    # argument list mentions a meta path (build_relations legitimately READS meta_dir, but must
    # never WRITE there).
    br_path = Path(__file__).resolve().parent / "build_relations.py"
    if br_path.exists():
        try:
            br_src = read_text(br_path)
        except OSError:
            br_src = ""
        if re.search(r"write_(?:jsonl|text)\s*\([^)]*\bmeta\b", br_src):
            report.error("build_relations_writes_meta",
                         "build_relations.py appears to write into a meta path — it must only "
                         "project relations.jsonl; object metas are hand-authored (CR-023 INV-8)",
                         path=str(br_path))

    # INV-8 — no functional KO skill may reappear in any skill tree (CR-035 Change 10, deferred
    # from AIP-049). A build-/refresh-knowledge-object SKILL.md is allowed ONLY as a retired
    # tombstone: status: retired AND not user-invocable. Tombstone-safe (the Change-9 tombstones
    # keep status: retired). Scans all 4 live skill trees (2 FULL canonical + 2 short-pointer).
    root = ai_work.parent
    skill_trees = (
        ai_work / "procedural" / "skills",
        root / "product" / "procedural" / "skills",
        root / ".claude" / "skills",
        root / "product" / "skills",
    )
    for tree in skill_trees:
        for ko_name in ("build-knowledge-object", "refresh-knowledge-object"):
            sk = tree / ko_name / "SKILL.md"
            if not sk.exists():
                continue
            try:
                fm, _ = parse_frontmatter(read_text(sk))
            except OSError:
                continue
            status = str(fm.get("status", "")).strip().strip("\"'").lower()
            inv = fm.get("user-invocable")
            inv_true = (inv is True) or (str(inv).strip().strip("\"'").lower() == "true")
            if status != "retired" or inv_true:
                report.error("ko_skill_reappeared",
                             f"{ko_name} SKILL.md must be a retired tombstone (status: retired, "
                             "not user-invocable) — a functional Knowledge-Object skill must not "
                             "reappear; objects are hand-authored via node_kind=object "
                             "(CR-023 INV-8 / CR-035 Change 9)",
                             path=str(sk))


def _lint_rename_invariants(ai_work: Path, report: LintReport) -> None:
    """CR-AIWS-2026-07-020 rename gates (no-op if rename_map.json is absent — pre-migration installs):
      (1) skill folder name == frontmatter `name:` in every tree (Claude Code loads by folder==name);
      (2) a .claude/skills short-pointer's procedural target must resolve;
      (3) old skill/command names (rename_map) must not reappear in the skill/command surface —
          except a folder/command intentionally KEPT as a deprecation pointer (rename_map special)."""
    root = ai_work.parent
    skill_trees = (
        ai_work / "procedural" / "skills",
        root / "product" / "procedural" / "skills",
        root / ".claude" / "skills",
        root / "product" / "skills",
    )
    # (1) folder == frontmatter name
    for tree in skill_trees:
        if not tree.is_dir():
            continue
        for d in sorted(p for p in tree.iterdir() if p.is_dir()):
            sk = d / "SKILL.md"
            if not sk.exists():
                continue
            try:
                fm, _ = parse_frontmatter(read_text(sk))
            except OSError:
                continue
            name = str(fm.get("name", "")).strip().strip("\"'")
            if name and name != d.name:
                report.error("skill_folder_frontmatter_mismatch",
                             f"skill folder '{d.name}' != frontmatter name '{name}' — Claude Code "
                             "loads a skill only when they match (CR-AIWS-2026-07-020)",
                             path=str(sk))
    # (2) .claude short-pointer target resolves
    claude_skills = root / ".claude" / "skills"
    if claude_skills.is_dir():
        for d in sorted(p for p in claude_skills.iterdir() if p.is_dir()):
            sk = d / "SKILL.md"
            if not sk.exists():
                continue
            try:
                body = read_text(sk)
            except OSError:
                continue
            for tgt in re.findall(r"procedural/skills/([A-Za-z0-9_-]+)/SKILL\.md", body):
                if not (ai_work / "procedural" / "skills" / tgt / "SKILL.md").exists():
                    report.error("skill_pointer_dangling",
                                 f".claude/skills/{d.name} points at procedural/skills/{tgt}/SKILL.md "
                                 "which does not exist (CR-AIWS-2026-07-020)",
                                 path=str(sk))
    # (3) old-name denylist over the skill + command surface
    olds: list[str] = []
    kept: set[str] = set()
    verb_tokens: set[str] = set()
    for rp in (root / "product" / "rename_map.json", ai_work / "rename_map.json"):
        try:
            doc = json.loads(read_text(rp))
        except OSError:
            continue
        olds = [e["old"] for e in doc.get("renames", []) if e.get("old")]
        kept = {e["old"] for e in doc.get("renames", []) if e.get("special")}
        # CR-AIWS-2026-07-034 T1 — VERB-AWARE: after the CR-025 domain merge, many OLD names
        # survive as legitimate VERBS of a domain router (`init-workspace`, `point-step`, …).
        # A verb token inside its own domain surface is CORRECT usage, not a rename relapse —
        # flagging it produced 16 false ERRORs. Only a token that is nobody's verb (a truly
        # retired standalone skill, e.g. `update-aiws-package`) still errors.
        # Exempt ONLY when the old name IS the verb name it became (`init-workspace` →
        # verb `init-workspace` of aiws-aip). An entry whose old name maps to a DIFFERENT verb
        # (`update-aiws-package` → verb `upgrade`) is a real retirement and still errors.
        verb_tokens = {e["old"] for e in doc.get("renames", [])
                       if e.get("old") and e.get("skill") and e.get("verb") == e.get("old")}
        break
    if olds:
        pats = [(o, re.compile(r"(?<![\w-])" + re.escape(o) + r"(?![\w-])"))
                for o in sorted(olds, key=len, reverse=True)
                if o not in verb_tokens]
        # A token is ALSO a legitimate verb when the tree actually carries
        # <skill>/operations/<token>.md (belt-and-braces: works even if rename_map is stale).
        op_verbs: set[str] = set()
        for tree in skill_trees:
            if not tree.is_dir():
                continue
            for d in tree.iterdir():
                ops = d / "operations"
                if ops.is_dir():
                    op_verbs.update(p.stem for p in ops.glob("*.md"))
        pats = [(o, pat) for o, pat in pats if o not in op_verbs]

        def _scan(f: Path) -> None:
            if f.suffix.lower() not in (".md", ".txt"):
                return
            try:
                txt = read_text(f)
            except OSError:
                return
            hit = next((o for o, pat in pats if pat.search(txt)), None)
            if hit:
                report.error("old_skill_name_reappeared",
                             f"old name '{hit}' appears in a skill/command surface after rename — "
                             "use the new aiws-* name (CR-AIWS-2026-07-020; verb tokens of a merged "
                             "domain are exempt — CR-AIWS-2026-07-034 T1)",
                             path=str(f.relative_to(root)))

        for tree in skill_trees:
            if not tree.is_dir():
                continue
            for d in sorted(p for p in tree.iterdir() if p.is_dir()):
                if d.name in kept:        # deprecation pointer — allowed to keep its old name
                    continue
                for f in d.rglob("*"):
                    if f.is_file():
                        _scan(f)
        for base in (root / ".claude" / "commands", root / "product" / "commands"):
            if base.is_dir():
                for f in base.glob("*.md"):
                    if f.stem not in kept:
                        _scan(f)
        # CR-AIWS-2026-08-093 C3 — the Agents Pack is a shipped surface an agent READS AT RUN
        # TIME (verb specs, blueprint process docs); an old skill/command name there makes the agent
        # believe a shipped skill does not exist (IR-2026-08-15 F17 / IR-2026-08-17 F17-r:
        # `create-runtime-review-checklist` survived CR-071 because this scan never looked here).
        # Desk state (`agents/task_desks/`, legacy `agents/instances/`) is project-local history —
        # excluded via the same single source the dual-tree rules use (CR-091 C1). Measured before
        # widening: exactly 4 files / 3 old names in agents/, 0 noise; widening to EVERY shipped
        # root would hit 158 files (historical `90_delta_tracking/`, prose) — so the scope is
        # `agents/` only, deliberately.
        try:
            from check_dual_tree import project_local_prefixes as _plp
            _agents_skip = _plp("agents")
        except Exception:  # pragma: no cover
            _agents_skip = ("agents/task_desks/", "agents/instances/")
        for base in (root / "product" / "agents", ai_work / "agents"):
            if not base.is_dir():
                continue
            for f in base.rglob("*"):
                if not f.is_file():
                    continue
                rel = f.relative_to(base).as_posix()
                if any(rel.startswith(p) for p in _agents_skip):
                    continue
                _scan(f)


def _lint_object_golden_fixtures(ai_work: Path, report: LintReport) -> None:
    """Assert golden source-meta fixtures stay lint-clean (regression guard).

    Lints each fixture meta in the golden dirs below into a throwaway report; if any produces an
    ERROR, surface ONE error here so a future propagation gap (e.g. the profile_id requirement,
    the object-kind whitelist, or an enum regressing) fails CI. Called from this module's main()
    AND lint_all.main(), mirroring _lint_object_node_invariants.

      • tooling/fixtures/object_nodes/          object-node golden fixture (CR-AIWS-2026-06-004 C5)
      • tests/fixtures/wiki_corpus/metas_good/  wiki regression-suite spec-correct corpus metas
        (test_wiki_regression.py — consolidated to .ai-work/tests/ 2026-06-20). metas_broken/ is
        deliberately NOT scanned — those must fail. Both dirs are skipped if absent (slim install).
    """
    golden_dirs = (
        ai_work / "tooling" / "fixtures" / "object_nodes",
        ai_work / "tests" / "fixtures" / "wiki_corpus" / "metas_good",
    )
    for fixtures_dir in golden_dirs:
        if not fixtures_dir.is_dir():
            continue
        for fx in sorted(fixtures_dir.glob("*.md")):
            sub = LintReport(target=str(fx))
            try:
                _lint_source_meta(fx, sub)
            except Exception as exc:  # noqa: BLE001
                report.error("object_fixture_lint_crash",
                             f"golden fixture {fx.name} raised {exc!r} during lint "
                             "(CR-AIWS-2026-06-004 C5)", path=str(fx))
                continue
            codes = sorted({f.code for f in sub.findings if f.severity == SEV_ERROR})
            if codes:
                report.error("object_fixture_regressed",
                             f"golden fixture {fx.name} no longer lints clean "
                             f"(errors: {', '.join(codes)}) — a spec-correct meta must stay "
                             "lint-clean (CR-AIWS-2026-06-004 C5)", path=str(fx))


def _lint_build_routing(path: Path, ai_work: Path, report: LintReport) -> None:
    """Validate the Source Build Routing registry `_build_routing.json` (CR-AIWS-2026-05-019 Stage 2).

    Absence is valid (handled by the caller). Checks: JSON parses; default_route present; each route has
    required keys (tool, args); tool path resolves on disk (WARN); args use only known placeholders (WARN);
    refresh_mode known; profile_id (if set) resolves to a profiles/<id>.yml back-reference (WARN).
    """
    rel = str(path)
    try:
        data = json.loads(read_text(path))
    except json.JSONDecodeError as e:  # noqa: BLE001
        report.error("build_routing_json", f"_build_routing.json is not valid JSON: {e}", path=rel)
        return
    if not isinstance(data, dict):
        report.error("build_routing_shape", "_build_routing.json must be a JSON object", path=rel)
        return
    if not data.get("default_route"):
        report.warn("build_routing_default", "missing default_route (expected e.g. 'generic')", path=rel)
    routes = data.get("routes", {})
    if not isinstance(routes, dict):
        report.error("build_routing_routes", "'routes' must be an object", path=rel)
        return
    project_root = ai_work.parent
    profiles_dir = ai_work / "wiki_sources" / "profiles"
    for st, route in routes.items():
        if not isinstance(route, dict):
            report.error("build_routing_route", f"route '{st}' must be an object", path=rel)
            continue
        for k in ("tool", "args"):
            if k not in route:
                report.error("build_routing_field", f"route '{st}' missing required key '{k}'", path=rel)
        # CR-AIWS-2026-07-064 A4 (Rule 9): the registry is hand-editable DATA — a non-string tool
        # crashed resolve_locator, and exists() silently accepted a directory-valued tool.
        tool = locator_str(route.get("tool"))
        if tool and resolve_data_file(tool, project_root) is None:
            report.warn("build_routing_tool_missing",
                        f"route '{st}' tool not on disk: {resolve_locator(tool, project_root)}", path=rel)
        args = route.get("args", [])
        if not isinstance(args, list):
            report.error("build_routing_args", f"route '{st}' args must be a list", path=rel)
        else:
            bad: set[str] = set()
            for a in args:
                bad.update(re.findall(r"\{(\w+)\}", str(a)))
            bad -= _BUILD_ROUTING_PLACEHOLDERS
            if bad:
                report.warn("build_routing_placeholder",
                            f"route '{st}' uses unknown placeholders {sorted(bad)} "
                            f"(known: {sorted(_BUILD_ROUTING_PLACEHOLDERS)})", path=rel)
        rmode = route.get("refresh_mode", "")
        if rmode and rmode not in _BUILD_ROUTING_REFRESH_MODES:
            report.warn("build_routing_refresh_mode",
                        f"route '{st}' unknown refresh_mode '{rmode}' "
                        f"(known: {sorted(_BUILD_ROUTING_REFRESH_MODES)})", path=rel)
        pid = route.get("profile_id", "")
        if pid and not (profiles_dir / f"{pid}.yml").exists():
            report.warn("build_routing_profile",
                        f"route '{st}' profile_id '{pid}' has no profiles/{pid}.yml back-reference", path=rel)
        # H2 (CR-AIWS-2026-07-002): conversion-aware route fields.
        pc = route.get("pre_convert")
        if pc is not None:
            if not isinstance(pc, dict) or "tool" not in pc:
                report.error("build_routing_pre_convert",
                             f"route '{st}' pre_convert must be an object with a 'tool'", path=rel)
            elif locator_str(pc.get("tool")) and resolve_data_file(pc.get("tool"), project_root) is None:
                # CR-AIWS-2026-07-064 A5 (Rule 9) — same class as the route tool above.
                report.warn("build_routing_pre_convert",
                            f"route '{st}' pre_convert tool not on disk: "
                            f"{resolve_locator(locator_str(pc.get('tool')), project_root)}", path=rel)
        if "companion" in route and not isinstance(route["companion"], bool):
            report.error("build_routing_companion", f"route '{st}' companion must be true/false", path=rel)


_CITED_SRC_RE = re.compile(r"SRC-[A-Za-z0-9]+(?:-[A-Za-z0-9]+){2,}")


def _lint_curated_citations(ai_work: Path, report: LintReport) -> None:
    """Q4 (CR-AIWS-2026-07-001): a curated reading guide under wiki/reference/ that cites a
    source_id absent from every index has DRIFTED — re-registering a source changes its hash/prefix
    (CAP-902-003: 5/5 cited ids were stale). WARN so the digest is fixed before it routes an AI to a
    dead id. Warn-not-error; skip-if-absent. Only ids with >=3 segments are checked (avoid matching
    'SRC-' fragments in prose)."""
    ref_dir = ai_work / "wiki" / "reference"
    if not ref_dir.is_dir():
        return
    known: set[str] = set()
    for idx_name in ("index.jsonl", "index.aiws.jsonl", "index.local.jsonl"):
        idx = ai_work / "wiki_sources" / idx_name
        if idx.exists():
            try:
                known |= {r.get("source_id", "") for r in read_jsonl(idx)}
            except ValueError:
                pass
    if not known:
        return
    for f in sorted(ref_dir.rglob("*.md")):
        try:
            text = f.read_text(encoding="utf-8")
        except OSError:
            continue
        rel = str(f)
        seen: set[str] = set()
        for sid in _CITED_SRC_RE.findall(text):
            if sid in seen:
                continue
            seen.add(sid)
            if sid not in known:
                report.warn("curated_citation_stale",
                            f"cited source_id '{sid}' not in any index — the curated reading guide "
                            f"has drifted (re-register changes the hash/prefix); update to the live id",
                            path=rel)


# CR-AIWS-2026-07-033 T1(b)/M-05: the capture group allows SPACES inside the path —
# rename-created space-paths (e.g. `aiws-aip run/SKILL.md`) were invisible to the old
# `[^)#\s]+` class and survived CR-029 unseen.
_SKILL_MD_LINK_RE = re.compile(r"\]\(([^)#]+?\.md)(?:#[^)]*)?\)")

# ---- CR-AIWS-2026-07-032 T1: Related Sources shape/resolution integrity ----

_RS_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
_KNOWN_SOURCE_IDS_CACHE: dict[str, set] = {}
_KNOWN_OBJECT_IDS_CACHE: dict[str, set] = {}


def _known_object_ids(meta_root: Path) -> set:
    """source_ids that are node_kind=object (CR-AIWS-2026-07-038 T4): metas under meta_root
    with node_kind=object / __OBJECT__ locator + sibling index entries whose artifact_locator
    is the __OBJECT__ sentinel (node_kind itself is meta-only — CR-023 DP7, so the index side
    is resolved via the sentinel). Cached per meta_root."""
    key = str(meta_root.resolve())
    cached = _KNOWN_OBJECT_IDS_CACHE.get(key)
    if cached is not None:
        return cached
    ids: set = set()
    for p in meta_root.rglob("*.md"):
        if p.name.endswith(".refresh.md"):
            continue
        try:
            m, _ = parse_frontmatter(read_text(p))
        except Exception:  # noqa: BLE001
            continue
        if (str(m.get("node_kind", "")) == "object"
                or str(m.get("artifact_locator", "")) == OBJECT_LOCATOR_SENTINEL):
            ids.add(str(m.get("source_id") or p.stem))
    ws = meta_root.parent
    for idx_name in ("index.jsonl", "index.aiws.jsonl", "index.local.jsonl"):
        ip = ws / idx_name
        if not ip.exists():
            continue
        for line in read_text(ip).splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except Exception:  # noqa: BLE001
                continue
            if (str(rec.get("artifact_locator", "")) == OBJECT_LOCATOR_SENTINEL
                    and rec.get("source_id")):
                ids.add(str(rec["source_id"]))
    _KNOWN_OBJECT_IDS_CACHE[key] = ids
    return ids


def _known_source_ids(meta_root: Path) -> set:
    """All resolvable source_ids: every meta under meta/ (drafts excluded) + sibling indexes
    (index.jsonl / index.aiws.jsonl / index.local.jsonl). Cached per meta_root."""
    key = str(meta_root.resolve())
    cached = _KNOWN_SOURCE_IDS_CACHE.get(key)
    if cached is not None:
        return cached
    ids: set = set()
    for p in meta_root.rglob("*.md"):
        if p.name.endswith(".refresh.md"):
            continue
        try:
            m, _ = parse_frontmatter(read_text(p))
        except Exception:  # noqa: BLE001
            continue
        ids.add(str(m.get("source_id") or p.stem))
    ws = meta_root.parent
    for idx_name in ("index.jsonl", "index.aiws.jsonl", "index.local.jsonl"):
        ip = ws / idx_name
        if not ip.exists():
            continue
        for line in read_text(ip).splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                sid = json.loads(line).get("source_id")
            except Exception:  # noqa: BLE001
                continue
            if sid:
                ids.add(str(sid))
    _KNOWN_SOURCE_IDS_CACHE[key] = ids
    return ids


def _lint_related_sources_integrity(path: Path, rs_text: str, report: LintReport, rel: str) -> None:
    """ERROR `relations_edge_unresolvable` (CR-AIWS-2026-07-032 T1a) — see call site."""
    meta_root = next((p for p in path.parents if p.name == "meta"), None)
    known = _known_source_ids(meta_root) if meta_root is not None else set()
    for line in rs_text.splitlines():
        s = line.strip()
        if not s.startswith("- "):
            continue
        b = s[2:].strip()
        if (not b or b.startswith("<!--") or b.startswith("<") or "TODO" in b
                or (b.startswith("(") and b.endswith(")"))):
            continue  # comment / scaffold (CR-017 warn) / placeholder like "- (none)"
        mb = _RS_BOLD_RE.search(b)
        if not mb:
            report.error(
                "relations_edge_unresolvable",
                f"Related Sources bullet is not spec-§4.3 shape "
                f"(`- **<target_source_id>** — role: <type> — <note> [conf]`; legacy-untyped "
                f"still needs the **bold id**) — would project a garbage edge: {b[:90]!r}",
                path=rel)
            continue
        target = mb.group(1).strip()
        if known and target not in known:
            report.error(
                "relations_edge_unresolvable",
                f"Related Sources target '{target}' does not resolve to any known source_id "
                f"(meta set + indexes) — dead edge",
                path=rel)


_INTAKE_STATUS_ENUM = {"open", "staged", "processed", "promoted", "rejected"}
_INTAKE_DISPOSITION_ENUM = {"under_consideration", "promoted_to_cr", "applied", "rejected",
                            "idea_reference_only"}


def _lint_intake_frontmatter(ai_work: Path, report: LintReport) -> None:
    """WARN `intake_frontmatter_offvocab` (CR-AIWS-2026-07-043 T5) — `intake_status` /
    `disposition` in product/change_requests/intake/*.md must use the closed vocabulary declared
    by that folder's README. 7 off-vocab values had drifted across 18 files with nothing linting."""
    intake = ai_work.parent / "product" / "change_requests" / "intake"
    if not intake.is_dir():
        return  # installed project: no CR pipeline
    for f in sorted(intake.glob("*.md")):
        if f.name.lower() == "readme.md":
            continue
        try:
            meta, _ = parse_frontmatter(read_text(f))
        except Exception:  # noqa: BLE001
            continue
        for field, enum in (("intake_status", _INTAKE_STATUS_ENUM),
                            ("disposition", _INTAKE_DISPOSITION_ENUM)):
            v = str(meta.get(field, "")).strip()
            if v and v not in enum:
                report.warn("intake_frontmatter_offvocab",
                            f"{field} '{v}' not in the closed vocabulary {sorted(enum)} "
                            f"(product/change_requests/intake/README.md)",
                            path=str(f))


# Canonical sections that SHIP to a target project (PAYLOAD_MAP) and whose docs must be reachable
# via wiki lookup. Scope is deliberately the *reference documents* an agent must FIND by query —
# NOT skill bodies (`procedural/skills/**` have their own discovery surface: the skill router) and
# not `docs/` (advisory, never shipped).
# Scanned NON-recursively: a top-level doc is what an agent must find by query. Sub-documents
# (`procedural/capture_triggers/*`, `procedural/modes/*`) are reached FROM their parent doc, and
# skill bodies (`procedural/skills/**`) have their own discovery surface (the skill router).
_SHIPPED_CANONICAL_DIRS = (".ai-work/guidelines", ".ai-work/procedural")


def _lint_canonical_doc_registered(ai_work: Path, report: LintReport) -> None:
    """WARN `canonical_doc_unregistered` (CR-AIWS-2026-07-043 T5 + §7 rule) — a canonical doc that
    SHIPS to target projects but has no Wiki Source Meta is invisible to `lookup_wiki_source`, so
    every later wave has to hand-point its path. Scans the shipped canonical sections and checks
    each .md is referenced by some meta's artifact_locator (either index). Mute per-file with
    lint_accept when a doc is deliberately unregistered."""
    proj = ai_work.parent
    if not (proj / "product").is_dir():
        return  # dev-repo-only check (an installed project cannot register AIWS-owned docs)
    registered: set = set()
    # CR-AIWS-2026-08-052 C8 — twin-aware: a doc whose PRODUCT twin is registered counts as
    # registered (single-index repos register the product/ SoT path; the .ai-work copy is the
    # working mirror — no more false-nag on e.g. .ai-work/guidelines/AGENT_USAGE_GUIDE.md).
    _TWIN = ((".ai-work/guidelines/", "product/guidelines/"),
             (".ai-work/procedural/", "product/procedural/"))
    for name in ("index.jsonl", "index.aiws.jsonl"):
        ip = ai_work / "wiki_sources" / name
        if not ip.exists():
            continue
        for r in read_jsonl(ip):
            loc = str(r.get("artifact_locator", "")).replace("\\", "/")
            if loc:
                loc = loc.split("__PROJECT_ROOT__/")[-1]
                if loc.startswith("./"):        # NOT lstrip("./") — that would eat the dot of `.ai-work`
                    loc = loc[2:]
                registered.add(loc)
    for dest in _SHIPPED_CANONICAL_DIRS:
        d = proj / dest
        if not d.is_dir():
            continue
        for f in sorted(d.glob("*.md")):  # top-level only — see _SHIPPED_CANONICAL_DIRS note
            if f.name.lower() in ("readme.md", "index.md"):
                continue
            rel = f.relative_to(proj).as_posix()
            _twin_registered = any(
                rel.startswith(a) and (b + rel[len(a):]) in registered for a, b in _TWIN)
            if rel not in registered and not _twin_registered:
                report.warn("canonical_doc_unregistered",
                            "canonical doc ships to target projects but has no Wiki Source Meta — "
                            "invisible to lookup_wiki_source; register it (/aiws-wiki register) or "
                            "accept with a reason (CR-AIWS-2026-07-043 §7)",
                            path=str(f))


def _lint_duplicate_artifact(ai_work: Path, report: LintReport) -> None:
    """WARN `meta_duplicate_artifact` (CR-AIWS-2026-07-050 T2) — two SEPARATE metas describing the
    SAME artifact. It happens when one artifact is registered twice (e.g. by hand and by the
    package builder, with different path forms producing different id hashes — the OS-hash bug
    CR-041 T2 fixed); one of the two then becomes an orphan on the next rebuild.

    A parent + its H6 chunk children (CR-AIWS-2026-07-006) legitimately SHARE `artifact_locator`
    — a child carries `section_lines` and its id is `<parent_id>-SEC-…`. Those are excluded; without
    the carve-out this rule would fire on 4 valid groups (3 ASP fixtures + WIKI_META_INDEX_SPEC).
    Merging/deleting a meta is a Promotion trigger (refresh.md Promotion Gate) → the message says so.
    """
    by_artifact: dict = {}
    for root in _meta_roots(ai_work):
        for f in sorted(root.rglob("*.md")):
            if f.name.endswith(".refresh.md"):
                continue
            try:
                meta, _ = parse_frontmatter(read_text(f))
            except Exception:  # noqa: BLE001
                continue
            loc = str(meta.get("artifact_locator", "")).replace("\\", "/")
            if not loc or loc == OBJECT_LOCATOR_SENTINEL:
                continue
            sid = str(meta.get("source_id") or f.stem)
            chunked = bool(str(meta.get("section_lines", "")).strip()) or "-SEC-" in sid
            by_artifact.setdefault(loc, []).append((sid, str(f), chunked))
    for loc, entries in sorted(by_artifact.items()):
        parents = [(sid, path) for sid, path, chunked in entries if not chunked]
        if len(parents) < 2:
            continue  # single parent (+ any number of chunk children) = valid
        ids = ", ".join(sid for sid, _ in parents)
        for sid, path in parents:
            report.warn("meta_duplicate_artifact",
                        f"artifact '{loc}' is described by {len(parents)} separate metas ({ids}) — "
                        f"one will be orphaned on the next rebuild; merge them (keep the id the "
                        f"builder reproduces) via a CR — merging/deleting a meta is a Promotion "
                        f"trigger (Wiki-Manager approval required)",
                        path=path)


def _lint_skill_keep_surface(ai_work: Path, report: LintReport) -> None:
    """WARN `skill_keep_without_surface` (CR-AIWS-2026-07-044 T3) — every skill listed in
    rename_map.json `keep[]` must have at least ONE invocable surface (`.claude/skills/<n>/` or
    `product/skills/<n>/`), otherwise a downstream install receives a keep[] name it can never
    call. Opt out per entry with `procedural_only: true` (skills only AI-internal flows read)."""
    proj = ai_work.parent
    rm = proj / "product" / "rename_map.json"
    if not rm.exists():
        return
    try:
        data = json.loads(read_text(rm))
    except Exception:  # noqa: BLE001
        return
    keep = data.get("keep") or []
    procedural_only = set(data.get("procedural_only") or [])
    for name in keep:
        if not isinstance(name, str) or name in procedural_only:
            continue
        surfaces = [proj / ".claude" / "skills" / name / "SKILL.md",
                    proj / "product" / "skills" / name / "SKILL.md"]
        if not any(s.exists() for s in surfaces):
            report.warn("skill_keep_without_surface",
                        f"skill '{name}' is in rename_map keep[] but has NO invocable surface "
                        f"(.claude/skills/{name}/ or product/skills/{name}/) — a downstream install "
                        f"cannot call it; ship a shim or declare it in `procedural_only`",
                        path=str(rm))


#: Markers that make a `description` answer "when do I use this skill?" (CR-AIWS-2026-08-108 C3).
#: TWO families, deliberately. A skill meant for HUMANS answers with TRIGGERS; a skill meant to be
#: called by another step answers with an INVOCATION CONTRACT. Both are valid answers to the same
#: question, so both count — this is why the rule needs no per-name allowlist (DP-108-C = (a) kept
#: `aiws-review-plan` / `aiws-runtime-review-checklist` unedited, and an allowlist was refused).
_SKILL_DESC_TRIGGER_MARKERS = (
    "trigger", "use this skill", "use when", "when the user", "khi nào", "khi user",
)
_SKILL_DESC_CONTRACT_MARKERS = (
    "not directly user-invocable", "called by", "not for ad-hoc", "user-invocable: false",
)
#: Length floors. Two of them, because the two signal families need different amounts of room.
#: A human-invocable skill must fit WHAT + a usable VN/EN trigger set, which does not compress
#: below ~200 chars. A caller-only skill only has to state WHAT + name its caller — the invocation
#: contract is already the complete answer to "when", so holding it to the trigger-sized floor
#: would contradict SKILL_AUTHORING_CONVENTIONS §4.2, which tells such a skill it needs no trigger
#: list. Length ALONE is never the test (DP-108-B = (b)): no signal fails at any length.
_SKILL_DESC_MIN_LEN = 200
_SKILL_DESC_MIN_LEN_CONTRACT = 80


def _skill_description_signal(desc: str) -> "str | None":
    """Which kind of "when do I use this?" answer `desc` carries — or None.

    `"trigger"` — quoted user words (`"tạo AIP"`, `"run lint"`) or an explicit trigger marker. The
    strongest form, because it is literally what the user types.
    `"contract"` — the skill declares it is invoked by another step, not by a human. A complete
    answer for skills like `aiws-review-plan` (DP-108-C = (a) left their text untouched, and a
    per-name allowlist was refused — so the criterion has to be about CONTENT, not identity).
    """
    if re.search(r'"[^"]{3,60}"', desc):
        return "trigger"
    low = desc.lower()
    if any(m in low for m in _SKILL_DESC_CONTRACT_MARKERS):
        return "contract"
    if any(m in low for m in _SKILL_DESC_TRIGGER_MARKERS):
        return "trigger"
    return None


def _lint_skill_description(ai_work: Path, report: LintReport) -> None:
    """`description` is the ONLY thing an AI reads when deciding whether to invoke a skill — the
    body is loaded only AFTER the skill is chosen. So a missing or contentless description does not
    degrade gracefully: the skill is either never selected or selected for the wrong request, and
    both fail silently. CR-AIWS-2026-08-108 C3.

    Why this rule has to exist at all: the COMMAND surface already has the equivalent gate —
    `build_aiws_install_package.lift_command_frontmatter` fails the build when a verb spec has no
    `description`. The SKILL surface had nothing, so deleting one shipped straight through.

    ERROR `skill_description_missing` — key absent, or empty after the block scalar is parsed.
    WARN  `skill_description_thin`    — present but carries no selection signal (too short, or no
                                        trigger/contract marker). WARN, never ERROR: "thin" is a
                                        heuristic about prose and must not gate a build.

    MUST parse via `parse_frontmatter`. A hand-rolled `^description:` regex re-commits the exact
    bug CR-AIWS-2026-08-063 fixed: it returns the folded-scalar indicator `>` and reports a healthy
    description as empty. That failure mode is what made a HUMAN report "all descriptions are
    blank" in the first place, so the rule that checks for blankness must not reproduce it.
    """
    root = ai_work.parent
    skill_trees = (
        ai_work / "procedural" / "skills",
        root / "product" / "procedural" / "skills",
        root / ".claude" / "skills",
        root / "product" / "skills",
        ai_work / "agents" / "skills",
        root / "product" / "agents" / "skills",
    )
    for tree in skill_trees:
        if not tree.is_dir():
            continue
        for d in sorted(p for p in tree.iterdir() if p.is_dir()):
            sk = d / "SKILL.md"
            if not sk.exists():
                continue
            try:
                fm, _ = parse_frontmatter(read_text(sk))
            except OSError:
                continue
            desc = str(fm.get("description", "") or "").strip()
            if not desc:
                report.error("skill_description_missing",
                             f"skill '{d.name}' has no usable `description` — it is the only text an "
                             f"AI reads when choosing a skill, so this one is unselectable. Add a "
                             f"`description` stating WHAT it does and WHEN to use it "
                             f"(CR-AIWS-2026-08-108)",
                             path=str(sk))
                continue
            signal = _skill_description_signal(desc)
            floor = _SKILL_DESC_MIN_LEN_CONTRACT if signal == "contract" else _SKILL_DESC_MIN_LEN
            if signal is None or len(desc) < floor:
                report.warn("skill_description_thin",
                            f"skill '{d.name}' has a `description` ({len(desc)} chars) with no "
                            f"selection signal — an AI cannot tell when to pick it over a "
                            f"neighbouring skill. Add NL triggers (quote the user's words, VN + EN) "
                            f"or, for a skill only another step calls, say so explicitly "
                            f"(\"NOT directly user-invocable — CALLED by …\") (CR-AIWS-2026-08-108)",
                            path=str(sk))


def _dualtree_link_roots(ai_work: Path) -> "list[tuple[Path, bool, tuple[str, ...]]]":
    """Every root the dual-tree link rule scans, DERIVED from the shipped section map.

    CR-AIWS-2026-08-078 C1. Before this the rule carried a hand-written list of four roots, so the
    C4 convention (cross-tree targets are repo-root-relative TEXT, not markdown links) was
    self-enforcing only inside `procedural/skills/**` and the two shim trees. Everywhere else the
    same dual-tree constraint applied but nothing checked it — measured consequence: 11 broken
    links survived silently in `truth_templates/` and `aip_templates/`, each resolving on the
    product side and dead on the installed side.

    The pairs come from `check_dual_tree.iter_pairs()`, which derives from quick_install's
    `PAYLOAD_MAP` — the same single source. A second hand-kept list here would drift from the
    thing it claims to mirror, which is the defect this CR is closing.

    The `aiws_owned_only` flag survives for the `skills` section only: `.claude/skills/` is a
    namespace SHARED with project-local skills that AIWS must not gate on (M-10, CR-07-033 T1b).

    CR-AIWS-2026-08-091 C2: each root also carries the section's PROJECT-LOCAL prefixes
    (`check_dual_tree.project_local_prefixes`) — zones inside a shipped section that are not part
    of the pair (desk state under `agents/task_desks/`, legacy `agents/instances/`). A relative
    link in a closed run report there is history, not a dual-tree defect: it can be neither fixed
    nor `lint_accept`-ed (agents/ is outside the accept scope), so scanning it only manufactures
    an ERROR nobody can close (IR-2026-08-17 G1). Imported, not copied — same single source.
    """
    roots: "list[tuple[Path, bool, tuple[str, ...]]]" = []
    seen: "set[Path]" = set()
    try:
        from check_dual_tree import iter_pairs, project_local_prefixes
    except Exception:  # pragma: no cover - defensive; the tool ships beside this one
        iter_pairs = None
        project_local_prefixes = None
    if iter_pairs is not None:
        for key, prod, inst in iter_pairs(ai_work.parent):
            owned = (key == "skills")
            skip = project_local_prefixes(key) if project_local_prefixes else ()
            for r in (prod, inst):
                if r not in seen:
                    seen.add(r)
                    roots.append((r, owned, skip))
    # `.claude/skills` is the INSTALL destination of the `skills` section, so it already arrives
    # above on a real install. Kept explicit because this repo is a SOURCE tree: it wires
    # .claude/skills/ by hand and would otherwise go unscanned.
    for r in (ai_work.parent / ".claude" / "skills",):
        if r not in seen:
            seen.add(r)
            roots.append((r, True, ()))
    return roots


def _lint_skill_links(ai_work: Path, report: LintReport) -> None:
    """CR-AIWS-2026-07-029 C4: every relative .md markdown link inside a DUAL-TREE pair must
    resolve ON THE TREE BEING LINTED. Cross-tree targets (methodology specs, product/aiws_version.md)
    cannot be one relative string that is correct in BOTH copies of a byte-identical pair — write
    those as repo-root-relative TEXT paths, not markdown links. The convention is unchanged by
    CR-AIWS-2026-08-078; only the area where it enforces itself got wider (see `_dualtree_link_roots`).

    Finding code is `dualtree_link_broken`. The former name `skill_link_broken` is an ALIAS —
    resolved at the `lint_accept` layer (`_common.LINT_ACCEPT_CODE_ALIASES`, one release —
    CR-AIWS-2026-08-091 C3), NOT emitted as a second finding. CR-078 C2 had emitted it twice; that
    doubled `errors` and still did not rescue an accept keyed on either name, because
    `apply_lint_accept` matches the code string exactly (IR-2026-08-17 G2).

    Illustration spans (fenced blocks, ❌ counter-examples, `/.../` abbreviations) are skipped via
    the shared helper in `_common` — CR-AIWS-2026-08-078 C5.
    """
    for root, aiws_owned_only, skip_prefixes in _dualtree_link_roots(ai_work):
        if not root.is_dir():
            continue
        if aiws_owned_only:
            files = sorted(f for d in root.iterdir()
                           if d.is_dir() and d.name.startswith("aiws-")
                           for f in d.rglob("*.md"))
        else:
            files = sorted(root.rglob("*.md"))
        if skip_prefixes:
            # CR-AIWS-2026-08-091 C2 — project-local zones inside the section are not the pair.
            files = [f for f in files
                     if not any(f.relative_to(root).as_posix().startswith(p) for p in skip_prefixes)]
        # CR-AIWS-2026-08-078 C1b — install_templates/*.md are RULE TEMPLATES: their body is
        # composed into a file that lives at the PROJECT ROOT (CLAUDE.md / AGENTS.md /
        # copilot-instructions.md, CR-AIWS-2026-08-066), so their paths are root-relative BY
        # DESIGN and resolving them from install_templates/ is the wrong base. validate_payload_scope
        # already carries this exact exception (CR-AIWS-2026-08-071 C1); applying the same one here
        # rather than inventing a second rule. Measured: without it the widened scan reports 10
        # false errors, one of them a line CR-AIWS-2026-08-077 C4 had just added correctly.
        root_relative_base = root.name == "install_templates"
        for f in files:
            lines = read_text(f).splitlines()
            for i, line in unfenced_lines(lines):
                for link in _SKILL_MD_LINK_RE.findall(line):
                    if link.startswith(("http://", "https://", "/")):
                        continue
                    if is_ellipsis_path(link):
                        continue
                    base = (ai_work.parent if root_relative_base else f.parent)
                    try:
                        target = (base / link).resolve()
                    except OSError:
                        target = None
                    if target is not None and target.exists():
                        continue
                    msg = (f"relative link does not resolve on this tree: ({link}) at line {i} — "
                           f"fix the relative path, or use a repo-root-relative TEXT path for "
                           f"cross-tree targets (CR-AIWS-2026-07-029 C4)")
                    # ONE finding. The old code `skill_link_broken` is honoured as an ACCEPT alias
                    # (`_common.LINT_ACCEPT_CODE_ALIASES`), not re-emitted — CR-AIWS-2026-08-091 C3.
                    report.error("dualtree_link_broken", msg, path=str(f))


def run_wiki_source_lints(ai_work: Path, report: LintReport, *,
                          entries: bool = True,
                          sources: bool = True,
                          meta_files: "list[Path] | None" = None) -> None:
    """THE single rule list for the wiki/wiki-sources lint surface (CR-AIWS-2026-07-034 T2).

    Both `lint_wiki.main()` and `lint_all._lint_wiki_all` call THIS — neither owns a copy of the
    list. Before this driver the leg re-implemented a hand-picked subset, so a rule added to
    main() was INVISIBLE to the whole-tree gate (`skill_link_broken` was missing from CR-029
    until AIP-945; `_lint_rename_invariants`, `_lint_maintenance_log`, `_lint_build_routing`,
    `_lint_curated_citations`, `_lint_qa_store` were missing entirely until this CR).

    entries/sources mirror main()'s --entries-only / --sources-only. `meta_files` overrides which
    metas are linted (main()'s --paths); default = every meta under wiki_sources/meta.
    """
    if entries:
        wiki_root = ai_work / "wiki"
        if wiki_root.is_dir():
            for f in sorted(wiki_root.rglob("*.md")):
                if f.name.lower() == "readme.md":
                    continue
                _lint_wiki_entry(f, report)

    if not sources:
        return

    # CR-AIWS-2026-07-041 T1: meta-scan covers EVERY meta namespace — `meta/` (project) AND
    # `aiws_meta/` (the 188 shipped AIWS metas). Before this, aiws_meta/ + index.aiws.jsonl were
    # never fed to _lint_source_meta/_lint_source_index, so 32 metas with an empty ## Summary
    # sat in the corpus while lint reported errors=0 (and CR-037's declared WARN delta silently
    # evaporated). Index BUILD scope is unchanged (meta/→index.jsonl, aiws_meta/→index.aiws.jsonl).
    #
    # DP-041-1: `aiws_meta/` is a READ-ONLY namespace shipped by AIWS — an installed project
    # cannot fix findings in it. In the dev repo (product/ present) findings are emitted at their
    # natural severity and gate; in an installed project they are DOWNGRADED to warnings and never
    # gate, so an upstream defect can never block a downstream task's finalize lint.
    aiws_downgrade = not (ai_work.parent / "product").is_dir()
    # CR-AIWS-2026-07-049 (Rule 6): namespace roots come from the shared helper, never hand-picked.
    roots = (_meta_roots(ai_work) if meta_files is None
             else [ai_work / "wiki_sources" / "meta"])  # --paths scoping stays project-meta only
    for meta_root in roots:
        if not meta_root.is_dir():
            continue
        is_aiws_ns = meta_root.name == "aiws_meta"
        files = (meta_files if (meta_files is not None and not is_aiws_ns)
                 else sorted(meta_root.rglob("*.md")))
        for f in files:
            if f.name.endswith(".refresh.md"):
                continue  # pending refresh draft, not a meta (CR-AIWS-2026-07-032 T2)
            if is_aiws_ns and aiws_downgrade:
                sub = LintReport(target=str(f))
                _lint_source_meta(f, sub)
                for fnd in sub.findings:
                    if fnd.severity == "error":
                        fnd.severity = "warning"
                report.findings.extend(sub.findings)
            else:
                _lint_source_meta(f, report)

    for idx_name in ("index.jsonl", "index.local.jsonl", "index.aiws.jsonl"):
        index_path = ai_work / "wiki_sources" / idx_name
        if not index_path.exists():
            continue
        if idx_name == "index.aiws.jsonl" and aiws_downgrade:
            sub = LintReport(target=str(index_path))
            _lint_source_index(index_path, sub)
            for fnd in sub.findings:
                if fnd.severity == "error":
                    fnd.severity = "warning"
            report.findings.extend(sub.findings)
        else:
            _lint_source_index(index_path, report)

    # CR-AIWS-2026-08-064 C7: relations.aiws.jsonl (shipped preset) ↔ index.aiws.jsonl ↔ aiws_meta/.
    # Same warn-not-error / skip-if-absent contract; a single-index repo has no such file.
    _rel_pairs = (
        ("relations.jsonl", "index.jsonl", "meta"),
        ("relations.local.jsonl", "index.local.jsonl", "meta"),
        ("relations.aiws.jsonl", "index.aiws.jsonl", "aiws_meta"),
    )
    for rel_name, idx_name, meta_name in _rel_pairs:
        rel_path = ai_work / "wiki_sources" / rel_name
        if rel_path.exists():
            idx_for = ai_work / "wiki_sources" / idx_name
            if not idx_for.exists():
                idx_for = ai_work / "wiki_sources" / "index.jsonl"  # single-index collapse (CR-052)
            _lint_relations(rel_path, idx_for, ai_work / "wiki_sources" / meta_name, report)
            # note: the staleness hint walks meta/ only — an aiws_meta-only edit is covered by the
            # index rebuild check; keeping one root here avoids a false 'stale' on every AIWS ship.

    maintenance_log = ai_work / "wiki_sources" / "maintenance_log.jsonl"
    if maintenance_log.exists():
        _lint_maintenance_log(maintenance_log, report)

    build_routing = ai_work / "wiki_sources" / "_build_routing.json"
    if build_routing.exists():
        _lint_build_routing(build_routing, ai_work, report)

    # Q4 (CR-AIWS-2026-07-001): curated reading-guide citations must resolve in an index.
    _lint_curated_citations(ai_work, report)
    # Repo-structure anti-KO guards (two-kind node model, CR-023 INV-1/INV-8)
    _lint_object_node_invariants(ai_work, report)
    # Object-node golden-fixture regression guard (CR-AIWS-2026-06-004 C5)
    _lint_object_golden_fixtures(ai_work, report)
    # Skill/command rename gates (CR-AIWS-2026-07-020; verb-aware per CR-AIWS-2026-07-034 T1)
    _lint_rename_invariants(ai_work, report)
    # Relative-link integrity in skill surfaces (CR-AIWS-2026-07-029 C4; CR-AIWS-2026-07-033 T1b)
    _lint_skill_links(ai_work, report)
    # Intake frontmatter vocabulary (CR-AIWS-2026-07-043 T5)
    _lint_intake_frontmatter(ai_work, report)
    # Shipped canonical docs must be registered in the wiki (CR-AIWS-2026-07-043 T5/§7)
    _lint_canonical_doc_registered(ai_work, report)
    # keep[] skills must have an invocable surface (CR-AIWS-2026-07-044 T3)
    _lint_skill_keep_surface(ai_work, report)
    # `description` = the only skill-selection signal an AI sees (CR-AIWS-2026-08-108 C3)
    _lint_skill_description(ai_work, report)
    # two metas describing the same artifact (CR-AIWS-2026-07-050 T2)
    _lint_duplicate_artifact(ai_work, report)
    # QA Memory store (CR-AIWS-2026-07-009 T5)
    qa_store = ai_work / "wiki" / "qa_memory" / "confirmed_qa.jsonl"
    if qa_store.exists():
        idx_ids: set = set()
        for name in ("index.jsonl", "index.aiws.jsonl"):
            ip = ai_work / "wiki_sources" / name
            if ip.exists():
                try:
                    idx_ids.update(r.get("source_id", "") for r in read_jsonl(ip))
                except Exception:  # noqa: BLE001
                    pass
        _lint_qa_store(qa_store, idx_ids, report)


def main() -> int:
    p = argparse.ArgumentParser(description="Lint wiki + wiki sources")
    p.add_argument("--path",
                   help="Override path to scan; default = <ai-work>/wiki + wiki_sources")
    p.add_argument("--paths", nargs="+", metavar="GLOB_OR_FILE",
                   help="Restrict meta lint to specific files or glob patterns (e.g. 'meta/SRC-*.md'). "
                        "Applied relative to <ai-work>/wiki_sources/meta/. Use to scope batch results.")
    p.add_argument("--entries-only", action="store_true")
    p.add_argument("--sources-only", action="store_true")
    p.add_argument("--strict", action="store_true")
    p.add_argument("--format", choices=["text", "json"], default="text")
    p.add_argument("--show-accepted", action="store_true",
                   help="list lint_accept-muted findings instead of just tallying them")
    ns = p.parse_args()

    start = Path(ns.path).resolve() if ns.path else Path.cwd()
    try:
        ai_work = find_ai_work_root(start) / ".ai-work"
    except SystemExit as e:
        print(e, file=sys.stderr)
        return 2

    report = LintReport(target=str(ai_work))

    # --paths → explicit meta selection (glob/stem), else the driver's default (every meta).
    meta_files: "list[Path] | None" = None
    meta_root = ai_work / "wiki_sources" / "meta"
    if ns.paths and meta_root.is_dir():
        import glob as _glob
        picked: list[Path] = []
        for pat in ns.paths:
            base = meta_root if not Path(pat).is_absolute() else Path(".")
            matched = [Path(p) for p in _glob.glob(str(base / pat), recursive=True)]
            if not matched:
                direct = meta_root / pat            # try direct stem match
                if direct.exists():
                    matched = [direct]
            picked.extend(matched)
        meta_files = sorted(set(picked))

    # ONE rule list, shared with lint_all's wiki leg (CR-AIWS-2026-07-034 T2).
    run_wiki_source_lints(ai_work, report,
                          entries=not ns.sources_only,
                          sources=not ns.entries_only,
                          meta_files=meta_files)

    apply_lint_accept(report, ai_work)
    return emit_report(report, ns.format, ns.strict, ns.show_accepted)


if __name__ == "__main__":
    raise SystemExit(main())
