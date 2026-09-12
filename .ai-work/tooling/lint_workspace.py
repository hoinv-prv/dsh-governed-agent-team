#!/usr/bin/env python3
"""Lint a runtime workspace directory.

v0.9.12 alignment:
- preferred Runtime Queue file: 02_runtime_queue.jsonl
- legacy alias: 02_investigation_queue.jsonl
- supports legacy investigation queue schema and new runtime queue schema
- extended Capture Inbox enums
- lint/check is deterministic guardrail, not semantic reviewer
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (  # noqa: E402
    LintReport,
    emit_report,
    find_ai_work_root,
    parse_frontmatter,
    parse_aip_steps,
    read_jsonl,
    read_text,
    resolve_locator,
)

QUEUE_PRIMARY = "02_runtime_queue.jsonl"
QUEUE_LEGACY = "02_investigation_queue.jsonl"
CAPTURE_FILE = "08_capture_inbox.jsonl"
# CR-AIWS-2026-07-060 — optional sub↔main mailbox (present only on multi-agent AIP runs; NOT a REQUIRED_FILE)
MAILBOX_FILE = "messages.jsonl"
MAILBOX_REQUIRED = ["msg_id", "ts", "from", "to", "kind"]
MAILBOX_KIND_ENUM = {"progress", "info", "question", "blocked", "answer", "handoff_ready"}
MAILBOX_DECISION_CLASS_ENUM = {"technical", "coordination", "business_rule", "sot_conflict"}
MAILBOX_STATUS_ENUM = {"open", "answered", "closed"}

STEP_OUTPUT_META_REQUIRED = [
    "output_id", "result_type", "working_aip_ref", "step_id",
    "output_locator", "created_at", "review_status",
]
DECISION_TRACE_REQUIRED = [
    "discussion_trace_id", "related_output_id", "working_aip_ref", "step_id",
    "discussion_summary", "question_or_issue", "final_decision", "created_at",
]
STEP_RESULT_TYPES = {
    "output", "decision", "conclusion", "assumption", "clarification",
    "review_judgment", "accepted_limitation",
}
STEP_REVIEW_STATUS = {
    "draft", "ready_for_review", "reviewed", "approved_for_next_step",
    "needs_revision", "rejected", "superseded", "archived", "unknown",
}

# Required non-queue files. Queue is checked separately to support legacy alias.
REQUIRED_FILES = [
    "00_task_brief.md",
    "00b_active_aip.md",
    "00c_active_step_context.md",
    "04_findings.md",
    "05_open_questions.md",
    "07_output_draft.md",
    CAPTURE_FILE,
    "11_output_final.md",
]

LEGACY_QUEUE_HINT_FIELDS = {"kind", "target", "question", "why"}
NEW_QUEUE_HINT_FIELDS = {"title", "type", "reason", "next_action", "blocking"}

# Common validation
QUEUE_COMMON_REQUIRED = ["id", "status"]
QUEUE_COMMON_RECOMMENDED = ["priority"]

QUEUE_STATUS_ENUM = {
    # v0.9.12 canonical
    "pending", "in_progress", "resolved", "blocked", "deferred", "cancelled",
    "moved_to_capture_inbox", "moved_to_open_questions", "moved_to_backlog",
    # v0.9.2 legacy
    "queued", "done", "discarded",
}
QUEUE_PRIORITY_ENUM = {
    # v0.9.12 canonical
    "high", "medium", "low",
    # v0.9.2 legacy
    "critical", "normal", "defer",
}
QUEUE_TYPE_ENUM = {
    "source_check", "design_check", "review_followup", "output_update",
    "active_step_context_check", "step_output_check", "decision_trace_check",
    "package_update_step", "changelog_manifest_step", "feedback_fix",
    "formatting_check", "consistency_check", "source_representation_check",
    "wiki_meta_check", "working_aip_update", "workspace_cleanup",
    "close_check", "other_task_action",
}

CAPTURE_REQUIRED = ["id", "type", "title", "content", "status", "suggested_target"]
CAPTURE_TYPE_ENUM = {
    # v0.9.2 legacy
    "insight", "qa_candidate", "summary_candidate", "playbook_candidate",
    "relation_candidate", "deferred_note", "wiki_update_candidate",
    # v0.9.10+ canonical additions
    "finding_candidate", "wiki_meta_update_candidate",
    "aip_template_improvement_candidate", "run_aip_improvement_candidate",
    "guideline_improvement_candidate", "source_representation_issue",
    "future_backlog_candidate", "notebook_note_candidate",
    # v0.9.23+
    "tooling_opportunity_candidate",
    # CR-AIWS-2026-08-085 C1 — added from MEASURED use, not from guessing what might be needed.
    # `gotcha_candidate`      2 records, the only ones in an ACTIVE workspace. Nothing existing
    #                         carries "trap you must remember": `insight` is too broad, and
    #                         `tooling_opportunity_candidate` implies it is FIXABLE — a gotcha
    #                         usually is not.
    # `review_rule_candidate` 4 records, the largest off-enum group. Document review is standing
    #                         work here (4 review blueprints ship).
    # `checklist_update_candidate` 3 records. Concrete destination (a checklist file); distinct
    #                         from `guideline_improvement_candidate`.
    "gotcha_candidate", "review_rule_candidate", "checklist_update_candidate",
}

# CR-AIWS-2026-08-085 C1 (DP-084-C = a) — values with 0/573 uses, being retired in TWO PHASES.
# Phase 1 (now): `append_capture` REFUSES them, so nothing new can arrive. They stay in the enum
# above so `lint_workspace` keeps accepting any record that already carries them — 0 in this repo,
# but a downstream install was never measured, and deleting an enum value out from under existing
# data is a breaking change we cannot verify from here.
# Phase 2 (a release later): drop from CAPTURE_TYPE_ENUM entirely.
# NOT retired: `qa_candidate`. It also has 0 uses, but `.ai-work/wiki/qa_memory/` exists (README +
# confirmed_qa.jsonl) and three procedural docs reference it — that is a channel nobody has walked
# yet, not a dead value. Removing it would close a road instead of clearing rubbish.
CAPTURE_TYPE_DEPRECATED = {
    "notebook_note_candidate",      # `notebook` remains a valid suggested_target; the type is redundant
    "relation_candidate",           # duplicated by candidate_kind `artifact_relation_update`
    "source_representation_issue",  # narrow meaning, never used
}

# CR-AIWS-2026-08-085 C1 — off-enum values seen in the corpus that map onto an EXISTING value.
# The point is not to reject them: it is that the error message can say WHICH value to use, so the
# writer is not left picking a wrong-but-legal one (the failure CR-AIWS-2026-08-083 warns about).
CAPTURE_TYPE_MERGE_INTO = {
    "process_improvement_candidate": "guideline_improvement_candidate",
    "aiws_improvement_candidate": "tooling_opportunity_candidate",
    "observation": "insight",
    "decision_candidate": "finding_candidate",
    "project_issue_pattern_candidate": "finding_candidate",
}
# ---------- candidate_kind: the improvement taxonomy (CR-AIWS-2026-08-126 C1) ----------
# Fifteen values, derived from the CORPUS (709 in-repo records, 66 distinct kinds) and not from the
# playbook's 20-row trigger table: the table describes what capture is prompted, the field records what
# was actually found, and building the vocabulary from the table would drop every value the field
# invented. Thirteen of the fifteen meet the CR-AIWS-2026-08-085 add-threshold (>=3 records in >=2
# workspaces) measured IN-REPO, per the HUMAN ruling that in-repo counts decide.
#
# Two are kept rather than added, so the threshold does not apply to them:
#   `output_quality_feedback` — 2 records, and its low count is a TRIGGER-WORDING defect (C8 widens it),
#                               not evidence the class is rare.
#   `qa_candidate`            — 0 records, but a live store (.ai-work/wiki/qa_memory/) and three
#                               procedural references. "0 records is not evidence of death" — the
#                               infrastructure exists and nobody has walked the road yet.
#
# `checker_candidate` is deliberately ABSENT: 13 records in a deployed project, 0 in-repo, so under the
# same ruling it cannot enter the AIWS preset. It is the worked example for the project registry (C4).
CAPTURE_KIND_ENUM = {
    "retrieval_improvement", "process_doc_gap", "reusable_pattern", "tooling_opportunity",
    "wiki_quality_issue", "authoring_lesson", "tool_gotcha", "decision_or_convention",
    "spec_impl_drift", "review_rule", "wiki_knowledge_gap", "relation_or_object",
    "deliverable_defect", "output_quality_feedback", "qa_candidate",
}

# Default routing scope per kind, used by `append_capture` to pre-fill `improvement_scope` so the writer
# pays nothing in the common case. `None` = genuinely ambiguous, the writer must say.
CAPTURE_KIND_DEFAULT_SCOPE = {
    "retrieval_improvement": "project",
    "process_doc_gap": "aiws",
    "reusable_pattern": None,          # project | aiws
    "tooling_opportunity": "aiws",
    "wiki_quality_issue": "project",
    "authoring_lesson": None,          # project | aiws
    "tool_gotcha": "aiws",
    "decision_or_convention": "project",
    "spec_impl_drift": "aiws",
    "review_rule": None,               # project | aiws
    "wiki_knowledge_gap": "project",
    "relation_or_object": "project",
    "deliverable_defect": "project",
    "output_quality_feedback": "project",
    "qa_candidate": "project",
}

# CR-AIWS-2026-08-126 C2 — the routing key of the consumer map. Two values, not three: `both` was
# considered and rejected because the agents-pack routing rule already resolved the same ambiguity by
# requiring TWO records, one per angle, which keeps every record single-destination.
IMPROVEMENT_SCOPE_ENUM = {"aiws", "project"}

# CR-AIWS-2026-08-126 C2 - SUPERSEDED, not deprecated. `aiws_system_improvement` holds 385 records and
# 54% of the field, but its records already carry a MORE specific signal in two already-closed enums:
# `type` (167 tooling_opportunity_candidate, 109 guideline_improvement_candidate, ...) and
# `suggested_target` (155 tooling, 127 guideline, ...). Its entire remaining content - "this is an AIWS
# problem" - is what `improvement_scope: aiws` states by construction. So it was never a vocabulary gap:
# it was ONE FIELD BEING ASKED TWO QUESTIONS. Records carrying it are PROJECTED onto the new fields, not
# rewritten and not warned about: a warning nobody may act on (the CR forbids rewriting them) is noise,
# and 37 of the 56 legacy warnings on live workspaces would be exactly that.
# Legacy kinds seen in the corpus that map onto a family, mirroring CAPTURE_TYPE_MERGE_INTO above and
# for the same reason (CR-AIWS-2026-08-083): the warning must say WHICH value to use, or the writer is
# left picking a wrong-but-legal one. Every legacy value still warning on a live workspace at apply time
# is listed here - measured, not guessed.
CAPTURE_KIND_MERGE_INTO = {
    # The 20 capture_triggers/*.md fragments, each mapped to the family it produces
    # (CR-AIWS-2026-08-126 C1, measured at apply: 15 of the 20 mapped to nothing).
    "ai_output_improvement_feedback": "output_quality_feedback",
    "artifact_relation_update": "relation_or_object",
    "best_practice_anti_pattern": "reusable_pattern",
    "cross_project_knowledge_candidate": "reusable_pattern",
    "decision_candidate": "decision_or_convention",
    "digest_synthesis_candidate": "wiki_knowledge_gap",
    "glossary_candidate": "wiki_knowledge_gap",
    "human_confirmed_knowledge": "decision_or_convention",
    "missing_wiki_knowledge": "wiki_knowledge_gap",
    "new_reference_candidate": "wiki_knowledge_gap",
    "object_relation_capture": "relation_or_object",
    "onboarding_candidate": "wiki_knowledge_gap",
    "recurring_failure_defense_in_depth": "review_rule",
    "summary_layer_candidate": "wiki_knowledge_gap",
    "tooling_opportunity_candidate": "tooling_opportunity",
    "knowledge_quality_issue": "wiki_quality_issue",
    "verification_trap": "tool_gotcha",
    "process_improvement": "process_doc_gap",
    "wiki_source_refresh_needed": "wiki_quality_issue",
    "checklist_improvement": "review_rule",
    "drift_evidence": "spec_impl_drift",
    "task_pattern_candidate": "reusable_pattern",
}

CAPTURE_KIND_SUPERSEDED = {
    "aiws_system_improvement": {"improvement_scope": "aiws"},
}


def project_capture_kind(rec: dict) -> dict:
    """Fields a legacy record IMPLIES, without touching the record (CR-AIWS-2026-08-126 C2)."""
    return dict(CAPTURE_KIND_SUPERSEDED.get(str(rec.get("candidate_kind", "") or ""), {}))


def project_capture_fields(rec: dict) -> dict:
    """Routing fields a record IMPLIES — kind and scope — WITHOUT touching the record.

    AIP-EXEC-1138. Measured 2026-08-30: 171 of 179 open backlog rows carry no `improvement_scope`
    and 125 carry a superseded or invalid kind, so nothing could sort the backlog by machine — the
    promotion log reads 93 deferred against 1 promoted. The obvious answer is to rewrite those rows;
    CR-AIWS-2026-08-126 C2 already declined it and shipped the projection above instead. That
    projection had exactly one caller (a test), so this is the wiring, not a new mechanism.

    Returns {"candidate_kind", "improvement_scope", "derived"} where `derived` names the fields that
    were INFERRED. Keeping that list is the point: a derived value indistinguishable from one a human
    chose is worse than no value, because triage routes on it (the rule written into
    `triage_capture.backlog_record` at AIP-EXEC-1135).

    Three invariants, each a way to get this wrong:
      * a STATED value is never overwritten — the record wins over every table here;
      * the kinds whose CAPTURE_KIND_DEFAULT_SCOPE entry is None (reusable_pattern,
        authoring_lesson, review_rule) are ambiguous BY DESIGN and are never guessed;
      * an unknown kind with no merge hint yields nothing invented.
    """
    kind = str(rec.get("candidate_kind", "") or "").strip()
    scope = str(rec.get("improvement_scope", "") or "").strip()
    derived = []

    effective_kind = kind
    if kind and kind not in CAPTURE_KIND_ENUM:
        hint = CAPTURE_KIND_MERGE_INTO.get(kind)
        if hint:
            effective_kind = hint
            derived.append("candidate_kind")

    effective_scope = scope
    if not effective_scope:
        # Superseded kinds carry their scope explicitly; everything else falls back to the family
        # default, which is None exactly where the answer is genuinely a judgement call.
        implied = str(CAPTURE_KIND_SUPERSEDED.get(kind, {}).get("improvement_scope", "") or "")
        if not implied:
            implied = str(CAPTURE_KIND_DEFAULT_SCOPE.get(effective_kind) or "")
        if implied:
            effective_scope = implied
            derived.append("improvement_scope")

    return {"candidate_kind": effective_kind, "improvement_scope": effective_scope,
            "derived": derived}

# HUMAN corrections, classified (C8). Optional; only meaningful on `output_quality_feedback`.
CORRECTION_CLASS_ENUM = {
    "missing_section", "wrong_format", "wrong_approach", "factual_error", "scope",
}

CAPTURE_STATUS_ENUM = {
    "captured", "triaged", "promoted", "archived", "discarded",
    "deferred", "retained_local",
}
CAPTURE_TARGET_ENUM = {
    # v0.9.10+ canonical
    "knowledge_hub_curated", "knowledge_hub_reference", "wiki_meta",
    "aip_template", "run_aip", "guideline", "skill", "notebook",
    "future_backlog", "history_only", "discard", "tooling",
    # CR-AIWS-2026-08-022: đích cho bài học VẬN HÀNH (loại 2) — thứ chỉ cần nhớ để lần sau
    # làm đúng/nhanh hơn, KHÔNG cần trở thành quy tắc. Trước CR này loại đó không có đích,
    # nên trigger best_practice_anti_pattern đẩy hết về `guideline` và phần lớn không được ghi.
    "operating_memory",
    # v0.9.2 legacy aliases
    "wiki_curated", "wiki_reference", "truth", "playbook",
}


def _queue_paths(ws: Path) -> tuple[Path, Path]:
    return ws / QUEUE_PRIMARY, ws / QUEUE_LEGACY


def _select_queue_file(ws: Path, report: LintReport) -> Path | None:
    primary, legacy = _queue_paths(ws)
    if primary.exists() and legacy.exists():
        if legacy.stat().st_size > 0:
            report.warn(
                "queue_dual_files",
                f"both {QUEUE_PRIMARY} and legacy {QUEUE_LEGACY} exist; primary is used",
                path=str(ws),
            )
        else:
            report.info(
                "queue_legacy_empty",
                f"empty legacy queue alias present: {QUEUE_LEGACY}",
                path=str(ws),
            )
        return primary
    if primary.exists():
        return primary
    if legacy.exists():
        report.info(
            "queue_legacy_alias",
            f"using legacy queue alias {QUEUE_LEGACY}; consider migration to {QUEUE_PRIMARY}",
            path=str(ws),
        )
        return legacy
    return None


def _detect_queue_schema(rec: dict) -> str:
    keys = set(rec.keys())
    if keys & NEW_QUEUE_HINT_FIELDS:
        return "runtime_queue"
    if keys & LEGACY_QUEUE_HINT_FIELDS:
        return "legacy_investigation_queue"
    return "unknown"


def _lint_queue(path: Path, report: LintReport) -> None:
    try:
        records = read_jsonl(path)
    except ValueError as e:
        report.error("queue_parse", str(e), path=str(path))
        return

    seen: set[str] = set()
    for idx, rec in enumerate(records, start=1):
        loc = f"line {idx}"
        schema = _detect_queue_schema(rec)

        for f in QUEUE_COMMON_REQUIRED:
            if f not in rec or rec[f] in (None, ""):
                report.error("queue_field", f"queue missing field: {f}",
                             path=str(path), loc=loc)
        for f in QUEUE_COMMON_RECOMMENDED:
            if f not in rec or rec[f] in (None, ""):
                report.warn("queue_field_recommended",
                            f"queue recommended field missing: {f}",
                            path=str(path), loc=loc)

        rid = rec.get("id")
        if rid and rid in seen:
            report.error("queue_dup", f"duplicate queue id: {rid}",
                         path=str(path), loc=loc)
        if rid:
            seen.add(rid)

        if schema == "legacy_investigation_queue":
            report.info("queue_legacy_schema",
                        "legacy investigation queue schema detected",
                        path=str(path), loc=loc)
            if not (rec.get("question") or rec.get("target")):
                report.warn("queue_legacy_missing_context",
                            "legacy queue item should include question or target",
                            path=str(path), loc=loc)
        elif schema == "runtime_queue":
            if not rec.get("title"):
                report.error("queue_title",
                             "runtime queue item missing title",
                             path=str(path), loc=loc)
            if not rec.get("next_action"):
                report.warn("queue_next_action",
                            "runtime queue item should include next_action",
                            path=str(path), loc=loc)
        else:
            report.warn("queue_schema_unknown",
                        "queue item schema is unknown; accepted as extension but should be reviewed",
                        path=str(path), loc=loc)

        status = rec.get("status")
        if status and status not in QUEUE_STATUS_ENUM:
            report.warn("queue_status",
                        f"status '{status}' not in known values {sorted(QUEUE_STATUS_ENUM)}",
                        path=str(path), loc=loc)

        priority = rec.get("priority")
        if priority and priority not in QUEUE_PRIORITY_ENUM:
            report.warn("queue_priority",
                        f"priority '{priority}' not in known values {sorted(QUEUE_PRIORITY_ENUM)}",
                        path=str(path), loc=loc)

        qtype = rec.get("type")
        if qtype and qtype not in QUEUE_TYPE_ENUM:
            report.info("queue_type",
                        f"type '{qtype}' not in known runtime queue types; accepted as extension",
                        path=str(path), loc=loc)


def _lint_capture(path: Path, report: LintReport) -> None:
    try:
        records = read_jsonl(path)
    except ValueError as e:
        report.error("capture_parse", str(e), path=str(path))
        return

    seen: set[str] = set()
    for idx, rec in enumerate(records, start=1):
        loc = f"line {idx}"
        for f in CAPTURE_REQUIRED:
            if f not in rec or rec[f] in (None, ""):
                # suggested_target is useful, but legacy captures may omit it.
                if f == "suggested_target":
                    report.warn("capture_field", f"capture missing recommended field: {f}",
                                path=str(path), loc=loc)
                else:
                    report.error("capture_field", f"capture missing field: {f}",
                                 path=str(path), loc=loc)

        cid = rec.get("id")
        if cid and cid in seen:
            report.error("capture_dup", f"duplicate capture id: {cid}",
                         path=str(path), loc=loc)
        if cid:
            seen.add(cid)

        ctype = rec.get("type")
        if ctype and ctype not in CAPTURE_TYPE_ENUM:
            report.warn("capture_type",
                        f"type '{ctype}' not in known values {sorted(CAPTURE_TYPE_ENUM)}",
                        path=str(path), loc=loc)

        cstatus = rec.get("status")
        if cstatus and cstatus not in CAPTURE_STATUS_ENUM:
            report.warn("capture_status",
                        f"status '{cstatus}' not in known values {sorted(CAPTURE_STATUS_ENUM)}",
                        path=str(path), loc=loc)

        tgt = rec.get("suggested_target")
        if tgt and tgt not in CAPTURE_TARGET_ENUM:
            report.warn("capture_target",
                        f"suggested_target '{tgt}' not in known values {sorted(CAPTURE_TARGET_ENUM)}",
                        path=str(path), loc=loc)

        # CR-AIWS-2026-08-126 C1/C2 — BEAT 1 of the two-beat rule (CR-AIWS-2026-08-085): WARN only.
        # `append_capture` already refuses an undeclared kind for new writes, so this leg exists to
        # SHOW the legacy tail, not to fail on it. Escalates to ERROR one release later. A project may
        # declare its own kinds as `<namespace>:<id>` in project_profile.yml (C4); they are accepted
        # here by shape, because this linter must not need to read another project's config to be right.
        kind = rec.get("candidate_kind")
        if (kind and kind not in CAPTURE_KIND_ENUM and ":" not in str(kind)
                and kind not in CAPTURE_KIND_SUPERSEDED):
            hint = CAPTURE_KIND_MERGE_INTO.get(str(kind))
            report.warn("capture_kind_legacy",
                        f"candidate_kind '{kind}' is not in the closed vocabulary"
                        + (f" — use '{hint}'" if hint else
                           f" {sorted(CAPTURE_KIND_ENUM)}")
                        + " (existing records stay valid; new writes are refused by append_capture)",
                        path=str(path), loc=loc)

        scope = rec.get("improvement_scope")
        if scope and scope not in IMPROVEMENT_SCOPE_ENUM:
            report.warn("capture_scope",
                        f"improvement_scope '{scope}' not in {sorted(IMPROVEMENT_SCOPE_ENUM)}",
                        path=str(path), loc=loc)

        cclass = rec.get("correction_class")
        if cclass and cclass not in CORRECTION_CLASS_ENUM:
            report.warn("capture_correction_class",
                        f"correction_class '{cclass}' not in {sorted(CORRECTION_CLASS_ENUM)}",
                        path=str(path), loc=loc)

        # CAP-088-02 (CR-AIWS-2026-06-029): only `promoted` captures need source_refs.
        # A sanctioned `triaged` capture with a terminal disposition legitimately has none,
        # so firing on `triaged` produced a recurring post-triage warning floor.
        if cstatus == "promoted" and not rec.get("source_refs"):
            report.warn("capture_refs",
                        "promoted capture should carry source_refs",
                        path=str(path), loc=loc)

        # CR-AIWS-2026-07-008 C2: machine-readable relation block on relation captures.
        rel = rec.get("relation")
        if rel is not None:
            if not isinstance(rel, dict):
                report.error("capture_relation",
                             "relation must be an object "
                             "{from_id,to_id,role,basis_note_draft,confidence}",
                             path=str(path), loc=loc)
            else:
                for rf in ("from_id", "to_id", "role"):
                    if not rel.get(rf):
                        report.error("capture_relation",
                                     f"relation block missing field: {rf}",
                                     path=str(path), loc=loc)
                if not rel.get("basis_note_draft"):
                    report.warn("capture_relation",
                                "relation block should carry basis_note_draft "
                                "(basis-note-at-discovery doctrine)",
                                path=str(path), loc=loc)
        elif (rec.get("candidate_kind") == "artifact_relation_update"
              and cstatus == "captured"):
            report.warn("capture_relation",
                        "artifact_relation_update capture without machine-readable "
                        "relation block (CR-AIWS-2026-07-008)",
                        path=str(path), loc=loc)

        # CR-AIWS-2026-07-008 C2: qa_candidate structured fields (QA-memory feed, CR-009).
        if ctype == "qa_candidate":
            qk = rec.get("qa_kind")
            if qk and qk not in ("overview_answer", "task_info_pack",
                                 "investigation_finding"):
                report.warn("capture_qa",
                            f"qa_kind '{qk}' not in known values "
                            "['overview_answer','task_info_pack','investigation_finding']",
                            path=str(path), loc=loc)
            ab = rec.get("asked_by")
            if ab and ab not in ("human", "ai"):
                report.warn("capture_qa",
                            f"asked_by '{ab}' not in known values ['human','ai']",
                            path=str(path), loc=loc)


def _workspace_status(ws: Path) -> str:
    brief = ws / "00_task_brief.md"
    if not brief.exists():
        return ""
    text = read_text(brief)
    status_line = next(
        (l for l in text.splitlines() if l.strip().lower().startswith("current status")),
        "",
    )
    return status_line.lower()


def _aip_status_for_workspace(ws: Path) -> str:
    """The AIP's frontmatter `status` for this workspace, or "" when it cannot be resolved.

    CR-AIWS-2026-08-125 C1. The close gate used to trigger on a hand-written brief line; this reads
    MACHINE-SET state instead. Resolution order, each step a fact rather than a guess:
      1. `.current_step.json` -> `aip_path` (a portable locator) — the authoritative back-link;
      2. `.current_step.json` -> `aip_id`, or the C4 folder-name derivation, then locate the file;
      3. "" — and the caller simply does not treat the workspace as closed.
    Never raises: a lint leg that dies on one malformed pointer stops linting the whole tree.
    """
    # find_ai_work_root returns the PROJECT ROOT (the dir containing .ai-work) and raises SystemExit
    # when there is none — a lint leg must never let that kill the whole run.
    try:
        project_root = find_ai_work_root(ws)
    except SystemExit:
        return ""
    ai_work = project_root / ".ai-work"
    aip_file: "Path | None" = None
    aip_id = ""

    ptr = ws / ".current_step.json"
    if ptr.exists():
        try:
            data = json.loads(read_text(ptr))
            aip_id = str(data.get("aip_id", "") or "")
            raw = str(data.get("aip_path", "") or "")
            if raw:
                cand = resolve_locator(raw, project_root)
                if cand.exists():
                    aip_file = cand
        except Exception:
            pass

    if aip_file is None:
        if not aip_id:
            aip_id = aip_id_from_workspace_name(ws.name)
        if aip_id:
            matches = sorted((ai_work / "aip").rglob(f"{aip_id}-*.md"))
            if matches:
                aip_file = matches[0]

    if aip_file is None:
        return ""
    try:
        meta, _ = parse_frontmatter(read_text(aip_file))
    except Exception:
        return ""
    return str(meta.get("status", "") or "").strip().lower()


_WS_NAME_RE = re.compile(r"^TASK-\d{8}-([A-Za-z]+)-(\d+)$")


def aip_id_from_workspace_name(name: str) -> str:
    """`TASK-YYYYMMDD-<kind>-NNNN` -> `AIP-<KIND>-NNNN`, else "" (CR-AIWS-2026-08-125 C4).

    Same derivation as `build_aip_index.aip_id_from_workspace_name`; kept local rather than imported
    because `lint_workspace` must not depend on a builder module.
    """
    m = _WS_NAME_RE.match(name.strip())
    return f"AIP-{m.group(1).upper()}-{m.group(2)}" if m else ""


def _check_close_sanity(ws: Path, report: LintReport) -> None:
    # CR-AIWS-2026-08-125 C1 — the trigger is machine-set state, not hand-written prose.
    # Measured before the repair: 0 of 573 briefs across three projects carried a line this gate
    # could match, so the whole body below had never executed anywhere. The prose signal is kept as
    # an ADDITIONAL trigger, so a brief that does say done/closed still counts and nothing that
    # fires today stops firing.
    status_line = _workspace_status(ws)
    aip_status = _aip_status_for_workspace(ws)
    is_closed = aip_status == "done" or "done" in status_line or "closed" in status_line
    if is_closed:
        final = ws / "11_output_final.md"
        if not final.exists() or not final.read_text(encoding="utf-8").strip():
            report.error("final_missing",
                         "task marked done/closed but 11_output_final.md is empty",
                         path=str(ws))

        queue = _select_queue_file(ws, report)
        if queue and queue.exists():
            try:
                records = read_jsonl(queue)
                for idx, rec in enumerate(records, start=1):
                    blocking = rec.get("blocking")
                    if isinstance(blocking, str):
                        blocking = blocking.lower() in {"true", "yes", "1"}
                    if blocking and rec.get("status") not in {"resolved", "done", "deferred", "cancelled", "discarded"}:
                        report.error("queue_blocking_open",
                                     f"blocking queue item still open: {rec.get('id', 'line '+str(idx))}",
                                     path=str(queue), loc=f"line {idx}")
            except ValueError:
                pass

        capture = ws / CAPTURE_FILE
        if capture.exists():
            try:
                records = read_jsonl(capture)
                for idx, rec in enumerate(records, start=1):
                    rid = rec.get("id", "line " + str(idx))
                    if rec.get("status") == "captured":
                        # CR-AIWS-2026-08-125 C5: once the AIP itself says done, an untriaged row is
                        # an ERROR under its own code — distinct from the WARN below so lint_accept
                        # entries and ledger lines can address the two separately.
                        if aip_status == "done":
                            report.error("capture_untriaged_at_done",
                                         f"AIP is status:done but this capture is still untriaged: {rid}",
                                         path=str(capture), loc=f"line {idx}")
                        else:
                            report.warn("capture_untriaged",
                                        f"capture item remains untriaged at close: {rid}",
                                        path=str(capture), loc=f"line {idx}")
                    elif rec.get("status") == "deferred" and not str(rec.get("deferred_to", "") or "").strip():
                        # Mirrors the existing `capture_refs` shape for promoted + source_refs: a
                        # disposition that names no destination is a decision that cannot be acted on.
                        report.warn("capture_deferred_without_pointer",
                                    f"capture is deferred but names no backlog row (deferred_to): {rid}",
                                    path=str(capture), loc=f"line {idx}")
            except ValueError:
                pass



def _read_yamlish_meta(path: Path) -> dict:
    text = read_text(path)
    if text.lstrip().startswith("---"):
        meta, _ = parse_frontmatter(text)
        return meta
    result: dict = {}
    for line in text.splitlines():
        if ":" not in line or line.lstrip().startswith("#"):
            continue
        k, v = line.split(":", 1)
        k = k.strip()
        v = v.strip()
        # CR-AIWS-2026-08-25 Item 2a: Strip inline comment outside quotes
        if '"' not in v and "'" not in v:
            v = re.sub(r'\s*#.*$', '', v)
        v = v.strip().strip('"').strip("'")
        if k:
            result[k] = v
    return result


def _check_handoff_missing(ws: Path, step_outputs_dir: Path, report: LintReport) -> None:
    """Wave 2 Item 2: Warn if a completed step had Expected Outputs but no handoff row.

    Checks:
    1. Read pointer to get current step and AIP path
    2. Read AIP to find completed steps with Expected Outputs
    3. Check if each such step has a row in step_outputs/index.jsonl
    4. Warn if missing (OP-1113-B: only warn on steps with Expected Outputs)
    """
    pointer_file = ws / ".current_step.json"
    if not pointer_file.exists():
        return

    try:
        pointer = read_jsonl(pointer_file) if pointer_file.name.endswith('.jsonl') else None
        if not pointer:
            import json
            pointer = json.loads(pointer_file.read_text(encoding="utf-8"))
    except Exception:
        return

    current_step_id = pointer.get("step_id", "STEP-01")
    aip_path_str = pointer.get("aip_path")
    if not aip_path_str:
        return

    try:
        aip_path = Path(aip_path_str).resolve()
        if not aip_path.exists():
            return
        aip_text = read_text(aip_path)
        _, aip_body = parse_frontmatter(aip_text)
        steps = parse_aip_steps(aip_body)
    except Exception:
        return

    import re
    current_match = re.match(r'STEP-(\d+)', current_step_id)
    current_num = int(current_match.group(1)) if current_match else 1

    handoff_rows = set()
    index_file = step_outputs_dir / "index.jsonl"
    if index_file.exists():
        try:
            for row in read_jsonl(index_file):
                step_id = row.get("step_id")
                if step_id:
                    handoff_rows.add(step_id)
        except Exception:
            pass

    for step in steps:
        step_id = step.get("step_id", "")
        step_match = re.match(r'STEP-(\d+)', step_id)
        if not step_match:
            continue

        step_num = int(step_match.group(1))
        if step_num >= current_num:
            continue

        expected_outputs = step.get("Expected Outputs", "").strip()
        if not expected_outputs:
            continue

        if step_id not in handoff_rows:
            report.warn("step_handoff_missing",
                       f"Step {step_id} had Expected Outputs but no handoff row in step_outputs/index.jsonl",
                       path=f"step_outputs/index.jsonl",
                       loc=f"missing {step_id}")


def _lint_step_outputs(ws: Path, report: LintReport) -> None:
    step_outputs = ws / "step_outputs"
    decision_traces = ws / "decision_traces"

    if step_outputs.exists():
        for meta_file in sorted(step_outputs.rglob("*.meta.yml")) + sorted(step_outputs.rglob("*.meta.yaml")):
            meta = _read_yamlish_meta(meta_file)
            rel = str(meta_file)
            for k in STEP_OUTPUT_META_REQUIRED:
                if k not in meta or meta[k] in (None, "", []):
                    report.warn("step_output_meta_field",
                                f"step output meta missing field: {k}",
                                path=rel)
            result_type = meta.get("result_type")
            if result_type and result_type not in STEP_RESULT_TYPES:
                report.warn("step_output_result_type",
                            f"unknown result_type: {result_type}",
                            path=rel)
            review_status = meta.get("review_status")
            if review_status and review_status not in STEP_REVIEW_STATUS:
                report.warn("step_output_review_status",
                            f"unknown review_status: {review_status}",
                            path=rel)
            if meta.get("used_by_steps") and not review_status:
                report.warn("step_output_handoff_review",
                            "used_by_steps exists but review_status is missing",
                            path=rel)
            if meta.get("used_by_final_output") in {"true", True, "yes", "1"} and not (
                meta.get("discussion_trace_locator") or meta.get("source_refs")
            ):
                report.warn("step_output_final_trace",
                            "used_by_final_output=true should have discussion trace and/or source refs",
                            path=rel)
            # CR-AIWS-2026-08-25 Item 2b: Option 2 (backward compat) — accept both top-level key AND inline value
            if meta.get("source_refs"):
                has_key = "verification_level" in meta
                has_inline = "verification_level" in str(meta.get("source_refs", ""))
                if not (has_key or has_inline):
                    report.warn("step_output_source_verification",
                                "source_refs present but verification_level not found (as key or inline value)",
                                path=rel)

        index = step_outputs / "index.jsonl"
        if index.exists():
            try:
                rows = read_jsonl(index)
                seen = set()
                for idx, row in enumerate(rows, start=1):
                    oid = row.get("output_id")
                    if not oid:
                        report.warn("step_output_index_field", "index row missing output_id",
                                    path=str(index), loc=f"line {idx}")
                    elif oid in seen:
                        report.error("step_output_index_duplicate", f"duplicate output_id: {oid}",
                                     path=str(index), loc=f"line {idx}")
                    else:
                        seen.add(oid)
            except ValueError as e:
                report.error("step_output_index_parse", str(e), path=str(index))

        _check_handoff_missing(ws, step_outputs, report)

    if decision_traces.exists():
        for trace_file in sorted(decision_traces.rglob("*.yml")) + sorted(decision_traces.rglob("*.yaml")):
            if trace_file.name == "index.yml":
                continue
            meta = _read_yamlish_meta(trace_file)
            rel = str(trace_file)
            for k in DECISION_TRACE_REQUIRED:
                if k not in meta or meta[k] in (None, "", []):
                    report.warn("decision_trace_field",
                                f"decision trace missing field: {k}",
                                path=rel)
            if not (meta.get("options_considered") or meta.get("rationale")):
                report.info("decision_trace_rationale",
                            "important decision trace should include options_considered and rationale when available",
                            path=rel)

        index = decision_traces / "index.jsonl"
        if index.exists():
            try:
                rows = read_jsonl(index)
                seen = set()
                for idx, row in enumerate(rows, start=1):
                    tid = row.get("discussion_trace_id")
                    if not tid:
                        report.warn("decision_trace_index_field", "index row missing discussion_trace_id",
                                    path=str(index), loc=f"line {idx}")
                    elif tid in seen:
                        report.error("decision_trace_index_duplicate", f"duplicate discussion_trace_id: {tid}",
                                     path=str(index), loc=f"line {idx}")
                    else:
                        seen.add(tid)
            except ValueError as e:
                report.error("decision_trace_index_parse", str(e), path=str(index))


def _lint_mailbox(path: Path, report: LintReport) -> None:
    """CR-AIWS-2026-07-060 — validate an optional sub↔main mailbox JSONL (TW-root messages.jsonl, or a
    run-private messages_out.jsonl / messages_in.jsonl). WARN-first; the whole surface is optional."""
    try:
        records = read_jsonl(path)
    except ValueError as e:
        report.error("mailbox_parse", str(e), path=str(path))
        return
    for idx, rec in enumerate(records, start=1):
        loc = f"line {idx}"
        for f in MAILBOX_REQUIRED:
            if f not in rec or rec[f] in (None, ""):
                report.warn("mailbox_field", f"mailbox message missing field: {f}", path=str(path), loc=loc)
        k = rec.get("kind")
        if k and k not in MAILBOX_KIND_ENUM:
            report.warn("mailbox_kind", f"kind '{k}' not in {sorted(MAILBOX_KIND_ENUM)}", path=str(path), loc=loc)
        dc = rec.get("decision_class")
        if dc and dc not in MAILBOX_DECISION_CLASS_ENUM:
            report.warn("mailbox_decision_class",
                        f"decision_class '{dc}' not in {sorted(MAILBOX_DECISION_CLASS_ENUM)}", path=str(path), loc=loc)
        st = rec.get("status")
        if st and st not in MAILBOX_STATUS_ENUM:
            report.warn("mailbox_status", f"status '{st}' not in {sorted(MAILBOX_STATUS_ENUM)}", path=str(path), loc=loc)


def lint_workspace_dir(ws: Path, report: LintReport) -> None:
    if not ws.is_dir():
        report.error("not_a_dir", f"workspace not found: {ws}")
        return

    for name in REQUIRED_FILES:
        if not (ws / name).exists():
            report.error("file_missing", f"required file missing: {name}",
                         path=str(ws))

    queue = _select_queue_file(ws, report)
    if queue is None:
        report.warn("queue_missing",
                    f"Runtime Queue missing: expected {QUEUE_PRIMARY}; legacy alias {QUEUE_LEGACY} also absent",
                    path=str(ws))
    else:
        _lint_queue(queue, report)

    capture = ws / CAPTURE_FILE
    if capture.exists():
        _lint_capture(capture, report)

    # CR-AIWS-2026-07-060 — optional sub↔main mailbox (TW-root + run-private out/in); no-op when absent
    mbox = ws / MAILBOX_FILE
    if mbox.exists():
        _lint_mailbox(mbox, report)
    runs_dir = ws / "runs"
    if runs_dir.is_dir():
        for rd in sorted(runs_dir.iterdir()):
            if rd.is_dir():
                for mb in ("messages_out.jsonl", "messages_in.jsonl"):
                    if (rd / mb).exists():
                        _lint_mailbox(rd / mb, report)

    _check_close_sanity(ws, report)
    _lint_step_outputs(ws, report)

    # Active Step Context frontmatter sanity
    asc = ws / "00c_active_step_context.md"
    if asc.exists():
        meta, _ = parse_frontmatter(read_text(asc))
        if meta.get("artifact_type") and meta.get("artifact_type") != "active_step_context":
            report.error("asc_type",
                         f"active_step_context artifact_type wrong: {meta.get('artifact_type')}",
                         path=str(asc))
        if not (meta.get("active_step_id") or meta.get("step_id")):
            report.warn("asc_active_step",
                        "active step context missing active_step_id/step_id",
                        path=str(asc))
        if not meta.get("staleness_status"):
            report.info("asc_staleness",
                        "active step context missing staleness_status",
                        path=str(asc))


def main() -> int:
    p = argparse.ArgumentParser(description="Lint runtime workspace")
    p.add_argument("--workspace", required=True)
    p.add_argument("--strict", action="store_true")
    p.add_argument("--format", choices=["text", "json"], default="text")
    ns = p.parse_args()

    ws = Path(ns.workspace).resolve()
    report = LintReport(target=str(ws))
    lint_workspace_dir(ws, report)
    return emit_report(report, ns.format, ns.strict)


if __name__ == "__main__":
    raise SystemExit(main())
