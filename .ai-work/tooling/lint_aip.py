#!/usr/bin/env python3
"""Lint AIP files (PLAN / EXEC / LOCAL).

Enforces AIP_Detail_Spec_MVP_v0_1 §5–§12 (aip_root retired — CR-AIWS-2026-07-026):
- metadata: artifact_type, artifact_id, status enum, plan_source
- full required sections per AIP type (§6.2–§6.4)
- full step structure per §7.1 (id, title, objective, mode, guidelines,
  inputs, expected outputs, done condition, notes / constraints)
- reference lint: guideline / skill paths (warn if missing on disk)
- live-working-file guard: warn when AIP is being used as a runtime tracker
  (Done Criteria with [x], runtime metrics inline)

Usage:
  lint_aip.py --path <file-or-dir> [--strict] [--format text|json]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (  # noqa: E402
    LintReport,
    apply_lint_accept,
    emit_report,
    extract_sections,
    find_ai_work_root,
    has_section,
    parse_aip_steps,
    parse_frontmatter,
    read_text,
)

STATUS_ENUM = {"draft", "active", "done", "archived"}
TYPE_ENUM = {"aip_plan", "aip_exec", "aip_local"}

# Required sections per AIP_Detail_Spec §6. Some entries accept alternative
# section names ("A | B") so templates that split sections still pass.
REQUIRED_SECTIONS = {
    "aip_plan": [
        "Objective",
        "Background / Context",
        "Scope",
        "Expected Outputs",
        "References to Read First",
        "Assumptions / Constraints",
        "Open Questions | Open Questions / Risks",
        "Risks / Constraints | Risks",
        "Execution Steps",
        "Done Criteria",
        "Review Points",
    ],
    "aip_exec": [
        "Objective",
        "Execution Scope",
        "Expected Outputs",
        "References to Read First",
        "Execution Steps",
        "Current Risks / Constraints",
        "Done Criteria",
        "Review / Finalization Notes | Self-check / Review Points | Finalization Notes",
        # CR-AIWS-2026-08-055 (DP-1025-B): §6.3 8→10 — spec đuổi theo AIP_EXEC_TEMPLATE thực tế.
        # done/ AIPs nằm ngoài lint walk (CAP-015) nên grandfather list = rỗng tại apply.
        "Re-plan Rule",
        "Re-plan Log",
    ],
    "aip_local": [
        "Objective", "Notes",
        "Personal Constraints / Reminders",
        "Local Execution Notes",
    ],
}

# Required step fields per §7.1 (Step ID + Title come from the header regex).
REQUIRED_STEP_FIELDS = [
    "Objective",
    "Recommended Mode",
    "Applicable Guidelines",
    "Inputs",
    "Expected Outputs",
    "Done Condition",
    "Notes / Constraints",
]

# Heuristics for the "live working file" guard.
RUNTIME_METRIC_RE = re.compile(
    r"\(\s*\d{2,}\s+(metas|entries|chapters|files|items|records|companions|docs)\b",
    re.IGNORECASE,
)

# Heuristics for the "wiki-first preflight at HARD GATE" rule.
# See product/procedural/skills/aiws-aip/operations/run.md §"Wiki-first preflight at HARD GATE".
HARD_GATE_RE = re.compile(r"\bHARD\s+GATE\b", re.IGNORECASE)
# CR-AIWS-2026-08-097 C1 — namespace theo TẬP NGUỒN WIKI THẬT, không theo một thư mục.
# Trước đây rule chỉ nhận `product/wiki_guidelines/` + `.ai-work/wiki/`, nên một AIP trích ĐÚNG
# authority (vd `product/methodology/.../AIWS_Change_Request_Spec_MVP.md` — có đăng ký wiki source)
# vẫn bị WARN. Người viết AIP khi đó hoặc đổi sang trích một guideline KHÔNG liên quan, hoặc khai
# `wiki:none` sai sự thật — cả hai đều làm hỏng chính thứ rule này định bảo vệ.
WIKI_REF_RE = re.compile(
    r"(\bwiki:[^\s/]"
    r"|product/wiki_guidelines/"
    r"|\.ai-work/wiki/"
    r"|product/methodology/"          # methodology_spec / methodology_guide (đã register)
    r"|\.ai-work/truth/canonical/"    # bản mirror của methodology trong Truth
    r"|\.ai-work/procedural/"         # process_guideline đã register (playbook, conventions, skills)
    r")",
    re.IGNORECASE,
)
WIKI_NONE_RE = re.compile(r"\bwiki:none\b", re.IGNORECASE)


_CR_ID_RE = re.compile(r"CR-AIWS-\d{4}-\d{2}-\d{3}")
_CR_SUBDIRS = ("", "applied", "rejected", "drafts", "intake")


def _cr_ref_resolves(project_root: Path, candidate: str) -> bool:
    """True iff `candidate` names a CR that exists SOMEWHERE in the CR pipeline (CR-AIWS-2026-07-042
    T2). A CR's file MOVES between `change_requests/` and its lifecycle subfolders (`applied/` …),
    so the reference must resolve by **cr_id**, not by the path frozen into the AIP at write time.
    Returns False for a CR id that exists in no folder — a genuinely dead ref still warns."""
    m = _CR_ID_RE.search(candidate)
    if not m:
        return False
    cr_id = m.group(0)
    base = project_root / "product" / "change_requests"
    if not base.is_dir():
        return False
    for sub in _CR_SUBDIRS:
        d = base / sub if sub else base
        if not d.is_dir():
            continue
        if any(f.name.startswith(cr_id) for f in d.glob("*.md")):
            return True
    return False


#: Thư mục vòng đời của AIP dưới `<account>/<kind>/` (CR-AIWS-2026-08-103 C3).
_AIP_SUBDIRS = ("", "done", "archived")
_AIP_ID_RE = re.compile(r"\bAIP-(?:EXEC|PLAN|LOCAL)-\d+\b", re.IGNORECASE)


def _intake_ref_consumed(candidate: str) -> bool:
    """CR-AIWS-2026-08-106 C0 — candidate có trỏ vào thư mục intake (vật tư tiêu hao) không?

    Chỉ nhận đúng thư mục intake của change_requests, ở cả hai cây; KHÔNG nhận
    `change_requests/` nói chung (CR applied vẫn phải resolve qua `_cr_ref_resolves`).
    """
    q = candidate.replace("\\", "/").strip()
    if q.startswith("./"):
        q = q[2:]
    return "change_requests/intake/" in q


def _aip_ref_resolves(ai_work: Path, candidate: str) -> bool:
    """True iff `candidate` nêu một AIP tồn tại ở ĐÂU ĐÓ trong cây AIP (CR-AIWS-2026-08-103 C3).

    Cùng lý lẽ với `_cr_ref_resolves` ngay trên: file AIP **di chuyển** theo vòng đời
    (`<kind>/` → `<kind>/done/` → `<kind>/archived/`), nên ref phải resolve theo **artifact_id**,
    không theo path đóng băng trong AIP lúc viết. Sửa AIP mỗi lần một AIP khác đóng là cách sai —
    AIP là stable control doc, và mọi AIP đóng trong tương lai sẽ tái tạo đúng lỗi này.
    Trả False cho một AIP-id không tồn tại ở bất kỳ thư mục nào — ref chết thật thì VẪN cảnh báo.
    """
    m = _AIP_ID_RE.search(candidate)
    if not m:
        return False
    aip_id = m.group(0).upper()
    base = ai_work / "aip"
    if not base.is_dir():
        return False
    for account in base.iterdir():          # mọi account, không hardcode tên
        if not account.is_dir():
            continue
        for kind in account.iterdir():
            if not kind.is_dir():
                continue
            for sub in _AIP_SUBDIRS:
                d = kind / sub if sub else kind
                if not d.is_dir():
                    continue
                if any(f.name.upper().startswith(aip_id) for f in d.glob("*.md")):
                    return True
    return False


def _check_wiki_first_preflight(step: dict, rel: str, sid: str, report: LintReport) -> None:
    """Warn when a HARD GATE step lacks a wiki cross-reference in Applicable Guidelines.

    Detection: step is HARD GATE if "HARD GATE" appears in the step TITLE only
    (CR-AIWS-2026-06-007 Change 1). Objective / Notes are intentionally excluded —
    they commonly quote or mention "HARD GATE" as data, not as gate intent, which
    produced false-positives (e.g. an apply-AIP for a CR about the preflight rule).
    Convention marks a real HARD GATE in the step title, e.g. "(HARD GATE)".
    Pass if Applicable Guidelines cites a REGISTERED wiki-source namespace
    (product/wiki_guidelines/ · .ai-work/wiki/ · product/methodology/ ·
    .ai-work/truth/canonical/ · .ai-work/procedural/) or the explicit opt-out
    "wiki:none" (CR-AIWS-2026-08-097 C1).
    """
    title = step.get("title", "") or ""
    if not HARD_GATE_RE.search(title):
        return
    guidelines = step.get("Applicable Guidelines", "") or ""
    if WIKI_NONE_RE.search(guidelines):
        return
    if WIKI_REF_RE.search(guidelines):
        return
    report.warn(
        "wiki_first_preflight_at_hard_gate",
        f"HARD GATE step {sid} lacks a Wiki cross-reference in 'Applicable Guidelines'. "
        f"Per aiws-aip run SKILL.md §'Wiki-first preflight at HARD GATE', consult Wiki via "
        f"lookup_wiki_source.py before posing the clarifying question and cite the relevant "
        f"wiki path (or add 'wiki:none' as a bullet to confirm explicit opt-out).",
        path=rel, loc=sid,
    )


# CR-AIWS-2026-08-127 C7 — ONE vague-input vocabulary for both step-Inputs rules, matched on WORDS after the
# locator tokens are removed. Before this, the last pattern was the bare substring `findings`, so a concrete,
# correct Input such as `04_findings.md#STEP-01` fired the rule: measured 2026-08-27 on 13 live AIPs, 14 WARN
# of which 9 were exactly that false positive (AIP-1121 STEP-01_count_findings_warn.py). Locator tokens =
# anything in backticks, path-like tokens ending .md/.jsonl/.py/.yml, and `#anchor` fragments.
_VAGUE_INPUT_PATTERNS = (
    r"all\s+step\s+evidence",
    r"all\s+prior\s+outputs",
    r"previous\s+results?",
    r"\bfindings\b",
)
_LOCATOR_TOKEN_RE = re.compile(r"`[^`]*`|[\w./#-]*\.(?:md|jsonl|py|yml)\b|#[\w-]+", re.IGNORECASE)


def _strip_locator_tokens(text: str) -> str:
    """Remove backtick spans, path-like tokens and #anchors so a word match cannot hit inside a locator."""
    return _LOCATOR_TOKEN_RE.sub(" ", text)


def _inputs_look_vague(inputs: str) -> bool:
    stripped = _strip_locator_tokens(inputs)
    return any(re.search(p, stripped, re.IGNORECASE) for p in _VAGUE_INPUT_PATTERNS)


def _check_step_inputs_unresolvable(step: dict, rel: str, sid: str, report: LintReport) -> None:
    """Warn when step Inputs field contains vague patterns or unresolved step references.

    Triggers when the Inputs field — with locator tokens (backtick spans, `x.md`, `#anchor`)
    removed first — matches the vague set: "All step evidence", "all prior outputs",
    "previous results", the bare WORD "findings" (case-insensitive, word-boundary); OR names a
    step without locator: "STEP-05" (no file path, no # anchor).
    Severity: WARN (guardrail — author can justify if needed).
    Per CR-AIWS-2026-08-25 Item 1; precision fix CR-AIWS-2026-08-127 C7 (`04_findings.md` is a
    locator, not a vague reference).
    """
    inputs = step.get("Inputs", "").strip()
    if not inputs:
        return

    if _inputs_look_vague(inputs):
        report.warn("step_inputs_unresolvable",
                   f"step {sid} Inputs field contains vague reference (e.g. 'All step evidence', "
                   f"'previous results', 'findings'); consider specifying exact file paths or step locators",
                   path=rel, loc=sid)
        return

    # Check for STEP-NN without locator (file path or # anchor)
    step_refs = re.findall(r'STEP-\d+\b', inputs)
    if step_refs and not re.search(r'[./:#]', inputs):  # no path/file/anchor in inputs
        report.warn("step_inputs_unresolvable",
                   f"step {sid} Inputs field references step(s) ({', '.join(set(step_refs))}) "
                   f"without file path or anchor; add locators (e.g. 'STEP-03 from 02_findings.md#section')",
                   path=rel, loc=sid)


def _check_closing_step_inputs_vague(step: dict, step_index: int, total_steps: int, rel: str, report: LintReport) -> None:
    """Warn when closing step (final step) has vague Inputs field.

    Applies only to the last step in the AIP (step_index == total_steps - 1).
    Same vocabulary and locator-stripping as _check_step_inputs_unresolvable
    (`_inputs_look_vague` — one implementation, CR-AIWS-2026-08-127 C7).
    Severity: WARN (guardrail — author can justify via Done Condition if needed).
    Per CR-AIWS-2026-08-25 Item 1b.
    """
    if step_index != total_steps - 1:
        return

    sid = step.get("step_id", f"step-{step_index + 1}")
    inputs = step.get("Inputs", "").strip()
    if not inputs:
        return

    if _inputs_look_vague(inputs):
        report.warn("closing_step_inputs_vague",
                   f"closing step {sid} Inputs field contains vague reference (e.g. 'All step evidence'); "
                   f"final step should declare specific evidence or refer to Done Condition for closure",
                   path=rel, loc=sid)


# CR-AIWS-2026-07-033 T3: markdown .md links in an AIP/template body (spaces allowed in path —
# same hardening as lint_wiki._SKILL_MD_LINK_RE, M-05).
_BODY_MD_LINK_RE = re.compile(r"\]\(([^)#]+?\.md)(?:#[^)]*)?\)")


def _lint_file(path: Path, ai_work: Path | None, report: LintReport) -> None:
    rel = str(path)
    text = read_text(path)
    meta, body = parse_frontmatter(text)

    if not meta:
        report.error("meta_missing", "no YAML frontmatter", path=rel)
        return

    atype = meta.get("artifact_type", "")
    if atype not in TYPE_ENUM:
        report.error("meta_type", f"artifact_type '{atype}' not in {sorted(TYPE_ENUM)}", path=rel)
        return

    if not meta.get("artifact_id"):
        report.error("meta_id", "artifact_id missing", path=rel)

    # S-04: title presence (per AIP_REVIEW_CHECKLIST_v0_3 §A.1)
    if not meta.get("title"):
        report.error("meta_title", "title missing or empty", path=rel)

    # S-06: project presence (per AIP_REVIEW_CHECKLIST_v0_3 §A.1)
    if not meta.get("project"):
        report.error("meta_project", "project missing or empty", path=rel)

    # S-07: updated_at presence + YYYY-MM-DD format (per AIP_REVIEW_CHECKLIST_v0_3 §A.1)
    # CR-AIWS-2026-06-007 Change 2 (Option A): template files under aip(_)templates/
    # intentionally ship the literal `YYYY-MM-DD` placeholder. Downgrade THAT to info
    # (not error) so the template floor does not pollute lint_all. Non-template files,
    # and template files with a real/malformed date, still error as before.
    _is_template = "/aip/templates/" in path.as_posix() or "/aip_templates/" in path.as_posix()
    updated_at = meta.get("updated_at", "")
    if _is_template and str(updated_at) == "YYYY-MM-DD":
        report.info("meta_updated_at",
                    "template placeholder updated_at (YYYY-MM-DD) — expected for template files",
                    path=rel)
    elif not updated_at:
        report.error("meta_updated_at", "updated_at missing", path=rel)
    elif not re.match(r"^\d{4}-\d{2}-\d{2}$", str(updated_at)):
        report.error("meta_updated_at",
                     f"updated_at format invalid (expected YYYY-MM-DD): {updated_at}",
                     path=rel)

    status = meta.get("status", "")

    def _status_hint(value: str) -> str:
        # Common drift: humans/AI write 'completed' (or variants) instead of 'done'.
        # Per AIP_Detail_Spec §5.6 the only finished-state value is 'done'.
        aliases = {
            "completed": "done",
            "complete": "done",
            "candidate-completed": "done",
            "finished": "done",
            "closed": "done",
            "in_progress": "active",
            "in-progress": "active",
            "open": "active",
            "todo": "draft",
            "wip": "active",
        }
        suggestion = aliases.get(value.strip().lower())
        return f" (did you mean '{suggestion}'?)" if suggestion else ""

    if status not in STATUS_ENUM:
        report.error("meta_status",
                     f"status '{status}' not in {sorted(STATUS_ENUM)}{_status_hint(status)}",
                     path=rel)

    if atype == "aip_exec" and not meta.get("plan_source"):
        report.warn("meta_plan_source",
                    "plan_source not declared (direct execution allowed but should be explicit)",
                    path=rel)

    for sec in REQUIRED_SECTIONS.get(atype, []):
        # Accept "A | B | C" meaning at least one of A/B/C must be present
        alternatives = [s.strip() for s in sec.split("|")]
        if not any(has_section(body, alt) for alt in alternatives):
            label = " or ".join(alternatives) if len(alternatives) > 1 else alternatives[0]
            report.error("section_missing", f"required section missing: {label}", path=rel)

    # ---- Live-working-file guard (§2.3 + §10.2) ----
    if atype in ("aip_plan", "aip_exec"):
        sections = extract_sections(body)
        done_body = sections.get("Done Criteria", "")
        for line in done_body.splitlines():
            stripped = line.strip()
            if stripped.startswith("- [x]") or stripped.startswith("- [X]"):
                report.warn(
                    "live_working_file",
                    "Done Criteria contains '[x]' — AIP must stay stable; "
                    "progress tracking belongs in the workspace "
                    "(07_output_draft.md / active step context)",
                    path=rel, loc="Done Criteria",
                )
                break
        for sec_name, sec_body in sections.items():
            for line in sec_body.splitlines():
                if RUNTIME_METRIC_RE.search(line):
                    report.warn(
                        "runtime_metric_in_aip",
                        f"runtime metric inline ('{line.strip()[:60]}…') — "
                        "move concrete counts/findings to workspace "
                        "04_findings.md",
                        path=rel, loc=sec_name,
                    )
                    break

    if atype in ("aip_plan", "aip_exec"):
        steps = parse_aip_steps(body)
        if not steps:
            report.error("steps_empty", "no Execution Steps found", path=rel)
        seen_ids: set[str] = set()
        # CR-AIWS-2026-08-048 C1 — P2 dual-read (task_desks primary, instances legacy fallback):
        # the old single `instances/` path went permanently is_dir()==False after the P2 rename,
        # leaving `assigned_agent_unresolved` silently inert (CAP-1043-01).
        # CR-AIWS-2026-08-101 C1 — `ai_work` được phép là None (main: `except SystemExit ->
        # ai_work = None` khi file không nằm dưới cây .ai-work/ nào; chữ ký hàm này cũng khai
        # `Path | None`). Trước đây khối dưới deref thẳng => TypeError + traceback + 0 finding,
        # và một harness kiểm theo tên rule đọc traceback đó thành "không có warning" (CAP-1082-01).
        # Skip CÓ THÔNG BÁO chứ không im lặng: im lặng thì không phân biệt được "không có vấn đề"
        # với "phép đo không chạy" (DP-101-A = a).
        _inst_root = None
        _dispatch_off = False
        if ai_work is None:
            report.info("project_root_absent",
                        "không tìm thấy cây .ai-work/ từ file này — bỏ qua các rule cần project "
                        "root (assigned_agent_unresolved, dispatch toggle, ref_missing); các rule "
                        "cấp file vẫn chạy", path=rel)
        else:
            _inst_root = ai_work / "agents" / "agents" / "task_desks"
            if not _inst_root.is_dir():
                _inst_root = ai_work / "agents" / "agents" / "instances"
            # CR-AIWS-2026-08-044 C0 — project-level dispatch toggle (pack_config.yaml is OPTIONAL;
            # absent file/key = ON). Only an explicit false/no/off arms the WARN below.
            _pc = ai_work / "agents" / "pack_config.yaml"
            _m = re.search(r"(?m)^dispatch_enabled:[ \t]*([^#\n]*?)[ \t]*(?:#.*)?$",
                           _pc.read_text(encoding="utf-8") if _pc.is_file() else "")
            _dispatch_off = bool(_m) and _m.group(1).strip().lower() in ("false", "no", "off")
        _dispatch_off_warned = False
        for step in steps:
            sid = step["step_id"]
            loc = sid
            # CR-AIWS-2026-07-018 (optional field, WARN-only): Assigned Agent should resolve to an
            # installed instance dir; silently skipped when the agents pack has no instances dir.
            _aa = (step.get("Assigned Agent") or "").strip()
            if _aa and _aa.lower() != "auto" and _inst_root.is_dir() and not (_inst_root / _aa).is_dir():
                report.warn("assigned_agent_unresolved",
                               f"Assigned Agent '{_aa}' has no task desk under {_inst_root.as_posix()}/",
                               path=rel, loc=loc)
            # CR-AIWS-2026-08-044 C0 (WARN-only, once per AIP): assignment declared while the
            # project's dispatch toggle is OFF — run_agent.py will refuse these starts; surface
            # the drift at lint time instead of at dispatch time.
            if _aa and _dispatch_off and not _dispatch_off_warned:
                report.warn("dispatch_disabled_assignment_present",
                            "AIP declares `Assigned Agent:` step(s) but the agents pack "
                            "pack_config.yaml sets dispatch_enabled: false — dispatch will be "
                            "refused (CR-AIWS-2026-08-044 C0)",
                            path=rel, loc=loc)
                _dispatch_off_warned = True
            # CR-AIWS-2026-07-059 (optional fields, WARN-only): Difficulty/Kind value shape.
            _diff = (step.get("Difficulty") or "").strip().lower()
            if _diff and _diff not in ("low", "medium", "high"):
                report.warn("step_difficulty_value",
                            f"Difficulty '{_diff}' not in low|medium|high", path=rel, loc=loc)
            _kind = (step.get("Kind") or "").strip()
            if _kind:
                _kvocab = {"triage", "plan", "code", "patch_proposal", "sql",
                           "test_design", "review", "research", "organize", "canonical_edit"}
                _bad = [k.strip() for k in _kind.replace(";", ",").split(",")
                        if k.strip() and k.strip() not in _kvocab]
                if _bad:
                    report.warn("step_kind_value",
                                f"Kind tag(s) {_bad} not in the controlled vocab", path=rel, loc=loc)
            if sid in seen_ids:
                report.error("step_dup", f"duplicate step id: {sid}", path=rel, loc=loc)
            seen_ids.add(sid)
            for f in REQUIRED_STEP_FIELDS:
                if not step.get(f):
                    # CAP-088-03 (CR-AIWS-2026-06-029): distinguish "present but indented"
                    # from truly missing. An indented field label (e.g. 2 spaces, rendering as a
                    # bullet-list continuation) is not recognised as a column-0 field, so it is
                    # absorbed into another field's value. Detect it there and emit a precise
                    # message; it stays an error (markdown is malformed).
                    _label_re = re.compile(r"(?m)^[ \t]+" + re.escape(f) + r"[ \t]*:[ \t]*$")
                    if any(isinstance(v, str) and _label_re.search(v) for v in step.values()):
                        report.error("step_field_indented",
                                     f"step {sid} field '{f}' present but indented; move its "
                                     f"label to column 0 (lint anchors required step fields "
                                     f"at column 0)", path=rel, loc=loc)
                    else:
                        report.error("step_field_missing",
                                     f"step {sid} missing field: {f}", path=rel, loc=loc)

            # Wiki-first preflight rule — warn-level
            _check_wiki_first_preflight(step, rel, sid, report)

            # CR-AIWS-2026-08-25 Item 1: Lint rules for step Inputs
            _check_step_inputs_unresolvable(step, rel, sid, report)
            _check_closing_step_inputs_vague(step, step_index=len(seen_ids) - 1, total_steps=len(steps),
                                              rel=rel, report=report)

            if ai_work is not None:
                for field_name in ("Applicable Guidelines", "Recommended Skills"):
                    raw = step.get(field_name, "")
                    for line in raw.splitlines():
                        line = line.strip().lstrip("-").strip()
                        if not line or line == "...":
                            continue
                        # CR-AIWS-2026-08-101 C2 — quét MỌI token của dòng, không chỉ token đầu.
                        # `line.split()[0]` bỏ sót mọi path đứng sau token đầu: dòng
                        # `- aiws-council-review · references/x.md` cho candidate = tên skill
                        # (không có "/") nên nhánh kiểm path không hề chạy (CAP-1082-02). Carve-out
                        # giữ nguyên từng cái một, kiểm ngay trong vòng lặp.
                        _toks = [t.strip("`,;()[]*·").strip("`") for t in line.split()]
                        for _i, candidate in enumerate(_toks):
                            if not candidate or "/" not in candidate:
                                continue
                            # Token ĐẦU: predicate cũ (chỉ cần có "/") — giữ nguyên, không hồi quy.
                            # Token SAU: chỉ kiểm khi TRÔNG NHƯ path. Đo khi apply CR-101: predicate
                            # "mọi token có /" cho 0 -> 65 hit và 65/65 là NHIỄU — toàn tham chiếu mục
                            # dùng "/" làm dấu phân cách (`§4.1/§5`, `INTAKE-05/06`, `#7/#8`).
                            # DP-101-B đã lường: số liệu quyết định. Path-shape = có phần mở rộng
                            # hoặc bắt đầu bằng một gốc đã biết.
                            if "`" in candidate:
                                # còn backtick GIỮA token => đây là cụm nhiều tên ghép bằng "/"
                                # (`lint_wiki.py`/`lint_all.py`), không phải một path
                                continue
                            if candidate[0] in "§#":
                                # tham chiếu MỤC (`§4.1/§5`, `#7/#8`) dùng "/" làm dấu phân cách,
                                # không phải path — và đuôi ".4"/".12" của nó khớp cả regex phần mở rộng
                                continue
                            if _i and not (re.search(r"\.[A-Za-z0-9]{1,6}$", candidate)
                                           or candidate.startswith((".ai-work/", "product/", "docs/",
                                                                    ".claude/", "references/",
                                                                    "operations/", "assets/"))):
                                continue
                            if candidate.startswith(("http://", "https://")):
                                continue
                            if re.match(r"^/[a-z][a-z0-9-]*$", candidate):
                                # slash-router invocation (`/aiws-<domain> <verb>`) — the documented
                                # skill-call syntax, not a file path (CR-AIWS-2026-07-033 T2 / L-01)
                                continue
                            if candidate.endswith(":"):
                                continue
                            search = [
                                ai_work / candidate,
                                ai_work / "procedural" / candidate,
                                ai_work.parent / candidate,
                            ]
                            # CR-AIWS-2026-08-097 C2 — path NỘI BỘ của một skill package.
                            # SKILL.md dạy trỏ `references/<x>.md` / `operations/<verb>.md`, nhưng
                            # linter resolve từ project root nên báo ref_missing cho path viết ĐÚNG
                            # theo doc. Chỉ mở khi ngữ cảnh cho phép: cùng field có nêu tên skill,
                            # HOẶC candidate mang đúng hình dạng thư mục con của skill package.
                            if candidate.startswith(("references/", "operations/", "assets/")):
                                skills_root = ai_work / "procedural" / "skills"
                                for _sk in re.findall(r"\baiws-[a-z0-9-]+\b", raw):
                                    search.append(skills_root / _sk / candidate)
                            if any(c.exists() for c in search):
                                continue
                            # CR-AIWS-2026-07-042 T2: a CR reference resolves by cr_id, NOT by the
                            # path it had when the AIP was written — an applied CR is MOVED to
                            # change_requests/applied/ (lifecycle §16), which killed the path and
                            # produced 38 false ref_missing across done AIPs. AIPs are stable
                            # control docs; rewriting them on every CR move is the wrong fix
                            # (CR-AIWS-2026-07-036: a systematic false positive is a BUG of the rule).
                            if _cr_ref_resolves(ai_work.parent, candidate):
                                continue
                            # CR-AIWS-2026-08-103 C3 — cùng lớp với dòng trên, cho AIP
                            if _aip_ref_resolves(ai_work, candidate):
                                continue
                            # CR-AIWS-2026-08-106 C0 — thành viên THỨ BA của cùng họ, nhưng cho vật tư
                            # BỊ TIÊU THỤ chứ không phải BỊ DỜI. Một IR/intake tồn tại để dựng nên một
                            # CR; xong việc thì nó XOÁ ĐƯỢC — ruling PO 2026-08-19. Vì file đã biến mất
                            # hẳn, không có gì để resolve-by-id như hai dòng trên; cách duy nhất là
                            # coi ref tới `change_requests/intake/` là ref tới vật tư đã tiêu thụ,
                            # không phải ref chết. Giá phải trả: một path intake gõ sai cũng lọt —
                            # chấp nhận, vì ref intake luôn là INPUT LỊCH SỬ, không phải hợp đồng
                            # đang sống. Carve-out KHÔNG được nới ra ngoài `intake/` (test ca (f)).
                            if _intake_ref_consumed(candidate):
                                continue
                            report.warn(
                                "ref_missing",
                                f"{field_name} path not found: {candidate}",
                                path=rel, loc=sid,
                            )

        # CR-AIWS-2026-07-033 T3 (aip_body_link_broken, WARN — DP-033-1): every relative .md
        # MARKDOWN link in the body must resolve from the file's location. Repo-root TEXT paths
        # (the C4 doctrine for cross-depth/cross-tree targets) are NOT markdown links and are
        # never flagged. WARN (not ERROR): template placeholder links can be intentional.
        for _link in _BODY_MD_LINK_RE.findall(text):
            if _link.startswith(("http://", "https://", "/")):
                continue
            try:
                _tgt = (path.parent / _link).resolve()
            except OSError:
                _tgt = None
            if _tgt is None or not _tgt.exists():
                report.warn(
                    "aip_body_link_broken",
                    f"body markdown link does not resolve from this file: ({_link}) — fix the "
                    f"relative path or use a repo-root TEXT path (CR-AIWS-2026-07-033 T3)",
                    path=rel,
                )

        # Sequential step numbering check — warn on gaps (e.g. STEP-04 → STEP-06)
        _step_nums: list[int] = []
        for _s in steps:
            _m = re.search(r"(\d+)$", _s["step_id"])
            if _m:
                _step_nums.append(int(_m.group(1)))
        for _i in range(1, len(_step_nums)):
            if _step_nums[_i] != _step_nums[_i - 1] + 1:
                report.warn(
                    "step_numbering_gap",
                    f"step numbering gap: STEP-{_step_nums[_i-1]:02d} → "
                    f"STEP-{_step_nums[_i]:02d}",
                    path=rel,
                )


def _collect(root: Path) -> list[Path]:
    if root.is_file():
        return [root]
    return sorted(p for p in root.rglob("*.md") if "/aip/" in p.as_posix())


def main() -> int:
    p = argparse.ArgumentParser(description="Lint AIP files")
    p.add_argument("--path", required=True, help="File or directory to lint")
    p.add_argument("--strict", action="store_true")
    p.add_argument("--format", choices=["text", "json"], default="text")
    p.add_argument("--show-accepted", action="store_true",
                   help="list lint_accept-muted findings instead of just tallying them")
    ns = p.parse_args()

    target = Path(ns.path).resolve()
    if not target.exists():
        print(f"error: path not found: {target}", file=sys.stderr)
        return 2

    try:
        ai_work = find_ai_work_root(target) / ".ai-work"
    except SystemExit:
        ai_work = None

    files = _collect(target)
    report = LintReport(target=str(target))
    if not files:
        report.warn("no_files", "no AIP files found")
    for f in files:
        _lint_file(f, ai_work, report)

    if ai_work is not None:
        apply_lint_accept(report, ai_work)
    return emit_report(report, ns.format, ns.strict, ns.show_accepted)


if __name__ == "__main__":
    raise SystemExit(main())
