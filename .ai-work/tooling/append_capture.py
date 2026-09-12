#!/usr/bin/env python3
"""Append ONE capture record to a Task Workspace's `08_capture_inbox.jsonl` — safely.

CR-AIWS-2026-07-045 T4. Appending a capture by hand (shell heredoc / echo) is how malformed JSONL
gets into an inbox: a Windows path in `content` carries backslashes that the shell turns into
invalid JSON escapes, and the damage only surfaces at finalize lint (`capture_parse`). It happened
twice inside a single task (AIP-EXEC-913). This tool builds the record in Python, serializes with
`json.dumps`, RE-PARSES it to prove it is valid, and only then appends.

Usage:
    py .ai-work/tooling/append_capture.py \
        --workspace .ai-work/workspaces/<account>/<TASK-ID> \
        --id CAP-001 --type tooling_opportunity_candidate \
        --title "..." --content "..." \
        [--candidate-kind aiws_system_improvement] [--knowledge-value high|medium|low] \
        [--suggested-target tooling] [--step STEP-02] [--source-ref path ...] [--reusable]

`--content` may contain anything (Windows paths, quotes, newlines) — it is never shell-escaped
into JSON by hand. Exit 0 on append, 2 on validation error (nothing is written).

Python stdlib only.
"""
from __future__ import annotations

import argparse
import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import find_ai_work_root, today  # noqa: E402  (also forces UTF-8 stdout)
# CR-AIWS-2026-08-083 C2 — enum IMPORTED from the linter that enforces them, never copied.
# Two hand-kept copies drift, and then the writer blocks one set while lint blocks another —
# worse than today, where at least one of them is authoritative.
from lint_workspace import (CAPTURE_KIND_DEFAULT_SCOPE,  # noqa: E402  CR-AIWS-2026-08-126
                            CAPTURE_KIND_ENUM, CAPTURE_KIND_MERGE_INTO,
                            CORRECTION_CLASS_ENUM, IMPROVEMENT_SCOPE_ENUM,
                            CAPTURE_STATUS_ENUM, CAPTURE_TARGET_ENUM,
                            CAPTURE_TYPE_DEPRECATED, CAPTURE_TYPE_ENUM,
                            CAPTURE_TYPE_MERGE_INTO)

# CR-AIWS-2026-08-083 C2 — STATUS_ENUM used to be a HAND COPY here with a
# "keep in sync" comment. That is exactly the duplication this CR removes for `type`
# and `suggested_target`, so it goes too: one source, imported. (Measured at apply:
# the copy had NOT drifted — the point is that nothing would have said so if it had.)
STATUS_ENUM = CAPTURE_STATUS_ENUM


# CR-AIWS-2026-08-083 C3 — the seven Operating Memory groups (operating_memory.md §3). They are a
# DIFFERENT vocabulary from CAPTURE_TYPE_ENUM: §3 classifies what a lesson IS ABOUT, the capture enum
# classifies WHERE it goes in triage. Naming them here is not a second enum — it exists only so the
# error message can recognise the exact confusion that happened (AIP-EXEC-1067 sweep wrote 11 records
# with §3 group names as `type`, and nothing stopped it).
_OM_GROUPS = {"verification_trap", "tool_gotcha", "required_order", "recurring_shape",
              "cost_sizing", "where_to_look", "rejected_option"}

_VOCAB_FALLBACK = (
    "  If NO listed value fits: pick the closest one AND record what you meant in `candidate_kind`, "
    "then raise a CR to extend the enum. Do not pick a wrong-but-legal value silently — an off-enum "
    "value at least stays visible as a lint WARNING, while a wrong legal one disappears from every "
    "count. (Measured 2026-08-17: 8 off-enum `type` values are in use across the corpus and none of "
    "them is a typo — they are vocabulary this enum does not cover; CR-AIWS-2026-08-083 DP-083-A.)")


def _validate_vocab(cap_type: str, suggested_target: str) -> None:
    """CR-AIWS-2026-08-083 C1 — fail at the WRITE, not at the next lint run.

    `type` and `suggested_target` always had enums, but they lived in `lint_workspace`, so a bad
    value travelled into the JSONL and only surfaced whenever someone next ran lint. Real case: the
    Final Capture Sweep of AIP-EXEC-1067 wrote 11 records with Operating Memory §3 group names as
    `type` and file PATHS as `suggested_target`; lint reported +16 warnings AFTER the AIP had already
    been closed. The same fact had been written down during the CR-076 investigation and never became
    a check.
    """
    # CR-AIWS-2026-08-085 C1 (DP-084-C = a, phase 1): the value is still in the enum so lint keeps
    # accepting records that already carry it, but nothing NEW may be written with it.
    if cap_type in CAPTURE_TYPE_DEPRECATED:
        raise ValueError(
            f"type {cap_type!r} is RETIRED (0 uses across the corpus; CR-AIWS-2026-08-085). It is "
            f"still accepted by lint so existing records stay valid, but no new record may use it. "
            f"Choose from {sorted(CAPTURE_TYPE_ENUM - CAPTURE_TYPE_DEPRECATED)}")
    if cap_type in CAPTURE_TYPE_MERGE_INTO:
        # Off-enum, but we know exactly what it means — say so instead of making the writer guess.
        raise ValueError(
            f"type {cap_type!r} is not a capture type; use "
            f"{CAPTURE_TYPE_MERGE_INTO[cap_type]!r} instead (CR-AIWS-2026-08-085 mapped it: the two "
            f"could not be told apart in practice). Keep the original wording in `candidate_kind` "
            f"if it matters.")
    if cap_type not in CAPTURE_TYPE_ENUM:
        hint = ""
        if cap_type in _OM_GROUPS:
            hint = (f"\n  `{cap_type}` is an Operating Memory §3 GROUP, not a capture type — two "
                    f"different vocabularies. Put the group in `candidate_kind` and choose a `type` "
                    f"from the list above (a lesson usually lands as `insight`).")
        raise ValueError(f"type {cap_type!r} not in {sorted(CAPTURE_TYPE_ENUM)}{hint}\n"
                         + _VOCAB_FALLBACK)
    if suggested_target and suggested_target not in CAPTURE_TARGET_ENUM:
        hint = ""
        if "/" in suggested_target or suggested_target.endswith(".md"):
            hint = ("\n  This looks like a FILE PATH. `suggested_target` takes a destination TOKEN "
                    "(e.g. `operating_memory`, `guideline`, `tooling`), not the path of the file you "
                    "expect it to land in.")
        raise ValueError(f"suggested_target {suggested_target!r} not in "
                         f"{sorted(CAPTURE_TARGET_ENUM)}{hint}\n" + _VOCAB_FALLBACK)


# ---------- candidate_kind: preset + project-declared (CR-AIWS-2026-08-126 C1/C4) ----------

def project_kind_ids(ai_work=None) -> "dict[str, dict]":
    """Kinds this project declares in `project_profile.yml`, keyed `<namespace>:<id>`.

    Generalises the mechanism the agents-pack routing rule already ships for the desk producer: a
    vocabulary bridge with a CLOSED boundary, plus a preserved original label. A project may add a
    **kind**; it may not add a `type` or a `suggested_target`, because those are the pipelines lint and
    routing understand. Project-specific destinations go in `target_artifact`, which is what it is for.

    The namespace is not decoration: a deployed project independently invented `design_defect`,
    `artifact_gap` and `review_pattern` — all names AIWS could plausibly choose later. Namespacing makes
    that collision structurally impossible instead of merely unlikely.

    Returns {} on any failure. A project that declares nothing is the normal case (measured: both real
    installs have no profile at all), and the preset works alone.
    """
    try:
        from _common import read_project_config, find_ai_work_root
    except Exception:
        return {}
    try:
        if ai_work is None:
            ai_work = find_ai_work_root(Path.cwd()) / ".ai-work"
        cfg = read_project_config(Path(ai_work))
    except Exception:
        return {}
    block = cfg.get("capture_kinds") or {}
    if not isinstance(block, dict):
        return {}
    ns = str(block.get("namespace", "") or "").strip()
    out: "dict[str, dict]" = {}
    if not ns:
        return out
    for row in block.get("kinds") or []:
        if isinstance(row, dict) and str(row.get("id", "") or "").strip():
            out[f"{ns}:{str(row['id']).strip()}"] = row
    return out


def effective_kinds(ai_work=None) -> "set[str]":
    """AIWS preset UNION the project's declared kinds. Nothing else is accepted for a NEW write."""
    return set(CAPTURE_KIND_ENUM) | set(project_kind_ids(ai_work))


def resolve_improvement_scope(candidate_kind: str, given: str = "", ai_work=None) -> str:
    """`given`, else the project's declared default, else the family default, else "".

    Pre-filling is what lets the field be required without taxing the writer: 12 of the 15 families have
    an unambiguous scope, so the common case costs nothing and the ambiguous three are exactly the ones
    worth a decision.
    """
    if given:
        return given
    declared = project_kind_ids(ai_work).get(candidate_kind) or {}
    if declared.get("improvement_scope"):
        return str(declared["improvement_scope"]).strip()
    return CAPTURE_KIND_DEFAULT_SCOPE.get(candidate_kind) or ""


def _validate_kind_and_scope(candidate_kind: str, improvement_scope: str,
                             correction_class: str, ai_work=None) -> None:
    """Refuse an undeclared kind for a NEW write. Existing records are never touched (two-beat rule)."""
    if candidate_kind:
        allowed = effective_kinds(ai_work)
        if candidate_kind not in allowed:
            hint = CAPTURE_KIND_MERGE_INTO.get(candidate_kind)
            msg = (f"candidate_kind {candidate_kind!r} is not declared. "
                   + (f"Use {hint!r}." if hint else f"AIWS preset: {sorted(CAPTURE_KIND_ENUM)}."))
            declared = sorted(k for k in allowed if ":" in k)
            msg += (f" This project also declares: {declared}." if declared else
                    " A project may declare its own kinds under a namespace in "
                    "`.ai-work/project_profile.yml` (`capture_kinds:`) - it may add a KIND, not a "
                    "`type` and not a `suggested_target`.")
            raise ValueError(msg + "\n" + _VOCAB_FALLBACK)
    if improvement_scope and improvement_scope not in IMPROVEMENT_SCOPE_ENUM:
        raise ValueError(f"improvement_scope {improvement_scope!r} not in "
                         f"{sorted(IMPROVEMENT_SCOPE_ENUM)}")
    if correction_class and correction_class not in CORRECTION_CLASS_ENUM:
        raise ValueError(f"correction_class {correction_class!r} not in "
                         f"{sorted(CORRECTION_CLASS_ENUM)}")


# ---------- C7: the playbook's enum block is GENERATED from this code ----------

PLAYBOOK_ENUM_BEGIN = "<!-- AIWS:BEGIN generated-capture-enums -->"
PLAYBOOK_ENUM_END = "<!-- AIWS:END generated-capture-enums -->"


def render_enum_block() -> str:
    """The playbook's enum section, rendered FROM the enums the linter and this writer enforce.

    Measured drift before this existed: `type` doc 16 vs code 22, `suggested_target` doc 12 vs code 17,
    and the doc still presented three values `append_capture` refuses. A one-off correction would drift
    again - it already did, which is how writers learned to invent values.
    """
    def fmt(vals):
        return " · ".join(f"`{v}`" for v in sorted(vals))

    live_types = sorted(set(CAPTURE_TYPE_ENUM) - set(CAPTURE_TYPE_DEPRECATED))
    return "\n".join([
        PLAYBOOK_ENUM_BEGIN,
        "<!-- GENERATED from lint_workspace.py by "
        "`py .ai-work/tooling/append_capture.py --sync-playbook-enums --apply`. Do not hand-edit: this "
        "block drifted from the code once already (CR-AIWS-2026-08-126 C7). -->",
        "**Enum hợp lệ (generated — doc == code):**",
        "",
        f"- `candidate_kind` ({len(CAPTURE_KIND_ENUM)}): {fmt(CAPTURE_KIND_ENUM)}",
        "  - Một dự án có thể khai thêm kind riêng trong "
        "`.ai-work/project_profile.yml` (`capture_kinds:`); tập hiệu lực = preset ∪ "
        "`<namespace>:<id>`. Thêm **kind** thì được, thêm `type` / "
        "`suggested_target` thì không.",
        f"- `improvement_scope` (**bắt buộc với record mới**): "
        f"{fmt(IMPROVEMENT_SCOPE_ENUM)}",
        "- `target_artifact` (tùy chọn): repo-relative path hoặc stable id. Chỉ "
        "validate **shape**, không bao giờ kiểm tra tồn tại — một "
        "capture có quyền trỏ tới thứ chưa có.",
        f"- `type` ({len(live_types)}): {fmt(live_types)}",
        f"  - từ chối cho record mới (deprecated): {fmt(CAPTURE_TYPE_DEPRECATED)}",
        f"- `suggested_target` ({len(CAPTURE_TARGET_ENUM)}): {fmt(CAPTURE_TARGET_ENUM)}",
        f"- `status` ({len(CAPTURE_STATUS_ENUM)}): {fmt(CAPTURE_STATUS_ENUM)}",
        f"- `correction_class` (tùy chọn, cho `output_quality_feedback`): "
        f"{fmt(CORRECTION_CLASS_ENUM)}",
        PLAYBOOK_ENUM_END,
    ])


def sync_playbook_enums(ai_work: Path, *, apply: bool = False) -> "list[Path]":
    """Render the block into the playbook in BOTH trees. Returns the paths whose content would change."""
    block = render_enum_block()
    targets = [Path(ai_work) / "procedural" / "wiki_candidate_capture_playbook.md",
               Path(ai_work).parent / "product" / "procedural" / "wiki_candidate_capture_playbook.md"]
    changed: "list[Path]" = []
    for p in targets:
        if not p.exists():
            continue
        raw = p.read_bytes()
        eol = "\r\n" if b"\r\n" in raw else "\n"
        flat = raw.decode("utf-8").replace("\r\n", "\n")
        if PLAYBOOK_ENUM_BEGIN not in flat or PLAYBOOK_ENUM_END not in flat:
            raise ValueError(f"{p}: no generated-enum markers - refusing to guess where the block goes")
        i = flat.index(PLAYBOOK_ENUM_BEGIN)
        j = flat.index(PLAYBOOK_ENUM_END) + len(PLAYBOOK_ENUM_END)
        out = flat[:i] + block + flat[j:]
        if out != flat:
            changed.append(p)
            if apply:
                p.write_bytes(out.replace("\n", eol).encode("utf-8"))
    return changed


def build_capture_record(cap_id: str, cap_type: str, title: str, content: str,
                         status: str = "captured", *, candidate_kind: str = "",
                         knowledge_value: str = "", suggested_target: str = "", step: str = "",
                         desk_type: str = "", desk_id: str = "", run_id: str = "",
                         desk_candidate_ref: str = "",
                         improvement_scope: str = "", target_artifact: str = "",
                         correction_class: str = "",
                         reusable: bool = False, source_refs=None, ai_work=None) -> dict:
    """Build one inbox record + prove it round-trips through JSON. Raises ValueError on bad input.

    CR-AIWS-2026-07-056 T2a: extracted from main() so run_aip.py's pending-capture sweep writes
    records through the SAME builder (Rule 2 — no second inbox-writer to drift)."""
    if status not in STATUS_ENUM:
        raise ValueError(f"status {status!r} not in {sorted(STATUS_ENUM)}")
    _validate_vocab(cap_type, suggested_target)
    _validate_kind_and_scope(candidate_kind, improvement_scope, correction_class, ai_work)
    # Pre-fill from the family default (CR-AIWS-2026-08-126 C2): a required field the writer must
    # always type is a field half the corpus will lack.
    improvement_scope = resolve_improvement_scope(candidate_kind, improvement_scope, ai_work)
    rec = {"id": cap_id, "type": cap_type, "title": title, "content": content,
           "status": status, "discovered_at": today()}
    # Desk→TW tier-up provenance (AIP-EXEC-999, friction of the CR-AIWS-2026-08-011 bridge):
    # `desk_type` keeps the ORIGINAL desk-side candidate type after `type` is translated into the
    # Task-Workspace enum. Optional and omitted when empty — existing records keep their exact shape.
    for key, val in (("candidate_kind", candidate_kind), ("knowledge_value", knowledge_value),
                     ("suggested_target", suggested_target), ("step", step),
                     ("desk_type", desk_type), ("desk_id", desk_id), ("run_id", run_id),
                     ("desk_candidate_ref", desk_candidate_ref),
                     ("improvement_scope", improvement_scope),
                     ("target_artifact", target_artifact),
                     ("correction_class", correction_class)):
        if val:
            rec[key] = val
    if reusable:
        rec["reusable"] = True
    if source_refs:
        rec["source_refs"] = [s.replace("\\", "/") for s in source_refs]
    try:
        json.loads(json.dumps(rec, ensure_ascii=False))  # prove valid BEFORE anyone writes it
    except (TypeError, ValueError) as e:
        raise ValueError(f"record does not serialize to valid JSON: {e}") from e
    return rec


def inbox_has_id(inbox: Path, cap_id: str) -> bool:
    """True if a capture with this id already exists (dup guard; idempotent sweeps depend on it)."""
    if not inbox.exists():
        return False
    for line in io.open(inbox, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        try:
            if json.loads(line).get("id") == cap_id:
                return True
        except json.JSONDecodeError:
            continue
    return False


def append_record(inbox: Path, rec: dict) -> None:
    """Append a validated record, newline-safe. Caller checks inbox_has_id() for dup control."""
    line = json.dumps(rec, ensure_ascii=False)
    json.loads(line)  # defensive re-parse
    with io.open(inbox, "a", encoding="utf-8", newline="\n") as f:
        f.write(line + "\n")


def main() -> int:
    # CR-AIWS-2026-08-126 C7 - handled BEFORE the parser is built: every capture argument
    # below is `required=True`, and this verb takes none of them. Branching here keeps the
    # existing CLI contract exactly as it was rather than loosening five requirements.
    if "--sync-playbook-enums" in sys.argv:
        apply = "--apply" in sys.argv
        try:
            ai_work = find_ai_work_root(Path.cwd()) / ".ai-work"
        except SystemExit:
            print("error: no .ai-work/ found", file=sys.stderr)
            return 2
        try:
            changed = sync_playbook_enums(ai_work, apply=apply)
        except ValueError as e:
            print(f"error: {e}", file=sys.stderr)
            return 2
        if not changed:
            print("playbook enum block is already in sync with the code.")
            return 0
        for c in changed:
            print(f"  {'rewrote' if apply else 'WOULD rewrite'}  {c}")
        if not apply:
            print("DRY RUN - nothing written. Re-run with --apply.")
        return 0
    p = argparse.ArgumentParser(description="Append a validated capture record to a workspace inbox")
    p.add_argument("--workspace", required=True, help="Task Workspace dir (holds 08_capture_inbox.jsonl)")
    p.add_argument("--id", required=True, help="capture id, e.g. CAP-001 (unique within the inbox)")
    p.add_argument("--type", required=True, help="capture type, e.g. tooling_opportunity_candidate")
    p.add_argument("--title", required=True)
    p.add_argument("--content", required=True, help="free text — Windows paths / quotes / newlines are safe here")
    p.add_argument("--status", default="captured", help=f"one of {sorted(STATUS_ENUM)}")
    p.add_argument("--candidate-kind", default="")
    p.add_argument("--knowledge-value", default="", choices=["", "high", "medium", "low"])
    p.add_argument("--suggested-target", default="")
    p.add_argument("--step", default="")
    # Desk→TW tier-up provenance (bridge CR-AIWS-2026-08-011): `--desk-type` keeps the ORIGINAL
    # desk-side candidate type after `--type` is translated to the TW enum. All optional.
    p.add_argument("--desk-type", default="", help="original desk-side candidate type (bridge tier-up)")
    p.add_argument("--desk-id", default="", help="agent task desk id that raised the capture")
    p.add_argument("--run-id", default="", help="agent run id that raised the capture")
    p.add_argument("--desk-candidate-ref", default="", help="desk-side learning_candidates id (e.g. LC-001)")
    p.add_argument("--source-ref", action="append", default=[], help="repeatable")
    p.add_argument("--reusable", action="store_true")
    # CR-AIWS-2026-08-126 C2/C8
    p.add_argument("--improvement-scope", default="",
                   help="aiws|project - the routing key of the consumer map; pre-filled "
                        "from the family default when omitted")
    p.add_argument("--target-artifact", default="",
                   help="repo-relative path or stable id; shape only, existence NOT checked")
    p.add_argument("--correction-class", default="",
                   help="missing_section|wrong_format|wrong_approach|factual_error|scope")
    ns = p.parse_args()

    ws = Path(ns.workspace)
    if not ws.is_dir():
        print(f"error: workspace not found: {ws}", file=sys.stderr)
        return 2
    inbox = ws / "08_capture_inbox.jsonl"
    if ns.status not in STATUS_ENUM:
        print(f"error: --status {ns.status!r} not in {sorted(STATUS_ENUM)}", file=sys.stderr)
        return 2

    if inbox_has_id(inbox, ns.id):
        print(f"error: capture id {ns.id!r} already exists in {inbox}", file=sys.stderr)
        return 2

    try:
        rec = build_capture_record(
            ns.id, ns.type, ns.title, ns.content, ns.status,
            candidate_kind=ns.candidate_kind, knowledge_value=ns.knowledge_value,
            suggested_target=ns.suggested_target, step=ns.step,
            desk_type=ns.desk_type, desk_id=ns.desk_id, run_id=ns.run_id,
            desk_candidate_ref=ns.desk_candidate_ref,
            improvement_scope=ns.improvement_scope,
            target_artifact=ns.target_artifact,
            correction_class=ns.correction_class,
            reusable=ns.reusable, source_refs=ns.source_ref)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    append_record(inbox, rec)
    print(f"appended {ns.id} -> {inbox}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
