#!/usr/bin/env python3
"""Materialize Active Step Context from an AIP step + workspace state.

Reads the AIP file, finds the target STEP, and writes a filled Active Step
Context markdown file in the workspace. The context combines step fields
(Objective, Mode, Guidelines, Skills, Inputs, Expected Outputs, Done
Condition, Notes) with pointers to relevant workspace runtime items.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (  # noqa: E402
    dump_frontmatter,
    extract_sections,
    find_ai_work_root,
    locator_str,
    operating_memory_digest,
    parse_aip_steps,
    parse_frontmatter,
    portable_locator,
    read_jsonl_lenient,
    read_text,
    resolve_locator,
    today,
    write_text,
    _h2_span,
)



def _first_existing(*paths: Path) -> Path | None:
    for p in paths:
        if p.exists():
            return p
    return None


def _bullet_refs(rows: list[dict], id_key: str = "id", max_items: int = 10) -> str:
    if not rows:
        return "- ..."
    lines = []
    for r in rows[:max_items]:
        rid = r.get(id_key) or r.get("output_id") or r.get("discussion_trace_id") or "?"
        title = r.get("title") or r.get("output_type") or r.get("final_decision") or r.get("summary") or ""
        status = r.get("status") or r.get("review_status") or r.get("handoff_status") or ""
        lines.append(f"- {rid} — {title} ({status})".rstrip())
    return "\n".join(lines)


def _format_multiline(value: str) -> str:
    """Turn a field block into markdown body lines."""
    value = (value or "").strip()
    if not value:
        return "- ..."
    return value


def _extract_selected_lens(body: str) -> str:
    """Return the AIP's selected Task Lens label (CR-AIWS-2026-05-030).

    Reads the optional `## Selected Task Lens / Mode` section and returns the value of its
    `- Lens:` bullet, or "" when the section is absent/empty (No-Lens). The lens is a HINT
    that shapes the ASC reading-surface ordering — never a hard filter; No-Lens = zero overhead.
    """
    section = extract_sections(body).get("Selected Task Lens / Mode", "")
    for line in section.splitlines():
        s = line.strip().lstrip("-").strip()
        if s.lower().startswith("lens:"):
            val = s.split(":", 1)[1].strip()
            # treat an explicit No-Lens / empty placeholder as no lens
            if not val or val.lower() in {"no-lens", "no lens", "none", "(none)", "n/a"}:
                return ""
            return val
    return ""


_STEP_HEAD_RE = re.compile(r"^#+\s*Step:\s*(STEP-\S+)", re.I)


def _step_block(body: str, step_id: str) -> str:
    """Return the raw text block of one step (heading → next step / next top-level H2).

    Used to read inline step-level flags that parse_aip_steps does not capture
    (it recognizes a fixed Field-list only). Read-only; does not touch _common.
    """
    out: list[str] = []
    capturing = False
    for line in body.splitlines():
        m = _STEP_HEAD_RE.match(line)
        if m:
            if capturing:
                break
            capturing = (m.group(1) == step_id)
            continue
        if capturing and line.startswith("## ") and not line.lstrip("#").strip().lower().startswith("step:"):
            break
        if capturing:
            out.append(line)
    return "\n".join(out)


def _allow_raw_search(body: str, step_id: str) -> str | None:
    """Read an optional inline `allow_raw_search: true|false` flag from a step block
    (CR-AIWS-2026-06-052). Returns 'true' / 'false', or None when the step does not
    declare it (the common case — no AIP-level raw-search grant)."""
    m = re.search(r"(?im)^\s*allow_raw_search\s*:\s*(true|false|yes|no|1|0)\s*$",
                  _step_block(body, step_id))
    if not m:
        return None
    return "true" if m.group(1).lower() in {"true", "yes", "1"} else "false"


def _digest_lines(text: str, max_lines: int) -> str:
    """Compact digest of an AIP-level section: first `max_lines` non-empty lines.

    Keeps the ASC an orientation surface, not a reproduction of the AIP
    (Active_Step_Context_Spec_MVP §5 — prefer pointers/compact over full content).
    """
    text = (text or "").strip()
    if not text:
        return "- ..."
    kept = [ln.rstrip() for ln in text.splitlines() if ln.strip()]
    out = kept[:max_lines]
    if len(kept) > max_lines:
        out.append("- … (digest trimmed — open the AIP for the full text)")
    return "\n".join(out)


def _indent(text: str, prefix: str = "  ") -> str:
    """Indent every line of `text` (for nesting a digest under a label)."""
    if not text:
        return prefix + "- ..."
    return "\n".join(prefix + ln for ln in text.splitlines())


def _step_map(steps: list[dict], active_step_id: str) -> tuple[str, int, int]:
    """Render the 'you are here' step map; return (1-based active index, total).

    CR-AIWS-2026-06-036: the full step list is already parsed — surface it so the
    AI knows its position without reading the whole AIP.
    """
    total = len(steps)
    idx = next((i for i, s in enumerate(steps) if s.get("step_id") == active_step_id), -1)
    lines: list[str] = []
    for i, s in enumerate(steps):
        sid = s.get("step_id", "?")
        title = s.get("title", "")
        if i == idx:
            mark = f"  ◀ ACTIVE (step {i + 1} of {total})"
        elif idx >= 0 and i < idx:
            mark = "  [upstream — done]"
        else:
            mark = "  [downstream]"
        lines.append(f"- {sid} — {title}{mark}")
    return ("\n".join(lines) if lines else "- ..."), (idx + 1 if idx >= 0 else 0), total


def _extract_guardrails(aip_sections: dict, ws: Path) -> str:
    """Extract Current Risks/Constraints and Known Open Points from AIP.

    CR-AIWS-2026-08-25 Item 2: render guardrails section with live status from
    05_open_questions.md if present (fail-soft on missing file).
    """
    lines = []

    # Current Risks / Constraints
    risks = (aip_sections.get("Current Risks / Constraints") or
             aip_sections.get("Risks") or "").strip()
    if risks:
        lines.append("- **Current Risks / Constraints:**")
        for ln in risks.splitlines()[:5]:  # cap at 5 lines
            if ln.strip():
                lines.append(f"  {ln.strip()}")

    # Known Open Points (live from 05_open_questions.md if present)
    open_points = (aip_sections.get("Known Open Points") or "").strip()
    if open_points:
        lines.append("- **Known Open Points:**")
        for ln in open_points.splitlines()[:5]:  # cap at 5 lines
            if ln.strip():
                lines.append(f"  {ln.strip()}")

    # Optional: check 05_open_questions.md for live status (fail-soft)
    try:
        op_file = ws / "05_open_questions.md"
        if op_file.exists():
            op_content = read_text(op_file)
            if "OP-" in op_content:  # sanity check for open point entries
                lines.append("- **Live open points recorded in workspace** `05_open_questions.md`")
    except Exception:
        pass

    return "\n".join(lines) if lines else "- (no risks or open points declared)"


def _extract_read_first(aip_sections: dict) -> str:
    """Extract References to Read First and Required Wiki Inputs.

    CR-AIWS-2026-08-25 Item 2: render read-first guidance per spec §5.
    """
    lines = []

    # References to Read First
    refs = (aip_sections.get("References to Read First") or "").strip()
    if refs:
        lines.append("**References to Read First:**")
        for ln in refs.splitlines()[:5]:  # cap at 5 lines
            if ln.strip():
                lines.append(ln.strip())

    # Required Wiki Inputs (hint: usually a table)
    wiki_inputs = (aip_sections.get("Required Wiki Inputs") or "").strip()
    if wiki_inputs:
        lines.append("**Required Wiki Inputs:** (see AIP for full table)")
        for ln in wiki_inputs.splitlines()[:3]:  # cap at 3 lines to preserve space
            if ln.strip():
                lines.append(ln.strip())

    return "\n".join(lines) if lines else "- (see AIP §References to Read First)"


def _extract_acceptance(step: dict, step_index_1based: int, step_total: int) -> str:
    """Extract Self-check/Review Points and Done Criteria.

    CR-AIWS-2026-08-25 Item 2: render Done Criteria when final step OR Reviewing mode.
    """
    lines = []

    # Self-check / Review Points (always)
    review_points = (step.get("Self-check / Review Points") or
                     step.get("Review Note") or "").strip()
    if review_points:
        lines.append("**Self-check / Review Points:**")
        for ln in review_points.splitlines()[:4]:  # cap at 4 lines
            if ln.strip():
                lines.append(ln.strip())
    else:
        lines.append("**Self-check / Review Points:** (from Step Output / Decision Persistence Requirements)")

    # Done Criteria (when final step OR Reviewing mode)
    done_crit = (step.get("Done Condition") or "").strip()
    is_final = step_index_1based >= step_total
    is_reviewing = "Reviewing" in (step.get("Recommended Mode") or "")

    if is_final or is_reviewing:
        lines.append("")
        if done_crit:
            lines.append("**Done Criteria (for this step):**")
            for ln in done_crit.splitlines()[:4]:  # cap at 4 lines
                if ln.strip():
                    lines.append(ln.strip())
        else:
            lines.append("**Done Criteria:** (see AIP Done Condition)")

    return "\n".join(lines) if lines else "- (no acceptance criteria)"


def _compute_staleness(pointer_step: str, requested_step: str, aip_path: Path,
                       asc_path: Path, expected_outputs: str) -> tuple[str, str]:
    """Compute staleness status: stale / possibly_stale / fresh (CR-AIWS-2026-08-25 Item 3).

    Returns (status, reason).
    """
    # Check pointer mismatch
    if pointer_step and pointer_step != requested_step:
        return "stale", f"pointer points to {pointer_step}, not {requested_step}"

    # Check AIP mtime vs ASC mtime
    try:
        aip_mtime = aip_path.stat().st_mtime
        asc_mtime = asc_path.stat().st_mtime if asc_path.exists() else 0
        if aip_mtime > asc_mtime:
            return "stale", f"AIP modified after ASC was built"
    except Exception:
        pass  # fail-soft on missing files

    # Check Expected Output paths
    try:
        for line in expected_outputs.splitlines():
            # Try to parse as path-like (skip markdown formatting)
            line = line.strip()
            if not line or line.startswith("|") or line.startswith("-") or line.startswith("#"):
                continue
            # Extract path tokens (simple heuristic: space-separated or backtick-wrapped)
            for token in line.split():
                token = token.strip("`[]().")
                if "/" in token or "\\" in token:
                    try:
                        path = Path(token)
                        if path.exists():
                            output_mtime = path.stat().st_mtime
                            if output_mtime > asc_mtime:
                                return "possibly_stale", f"output {token} modified after ASC"
                    except Exception:
                        pass  # invalid path, skip
    except Exception:
        pass

    return "fresh", ""


def _render_output_state(expected_outputs: str, ws: Path, aip_path: Path) -> str:
    """Render Output State block showing deliverable status (CR-AIWS-2026-08-25 Item 3).

    Table with Path | Exists | VCS Status | Suggested Mode columns.
    """
    lines = ["| Path | Exists | VCS Status | Suggested Mode |",
             "|---|---|---|---|"]

    # Parse Expected Outputs for paths
    found_any = False
    for line in expected_outputs.splitlines():
        line = line.strip()
        if not line or line.startswith("|") or line.startswith("-") or line.startswith("#"):
            continue

        # Extract path-like tokens
        for token in line.split():
            token = token.strip("`[]().")
            if "/" in token or "\\" in token:
                try:
                    path = Path(token)
                    path_exists = path.exists()
                    exists = "yes" if path_exists else "no"
                    vcs_status = "M" if path_exists else "?"
                    suggested = "revise-in-place" if path_exists else "create"
                    lines.append(f"| {token} | {exists} | {vcs_status} | {suggested} |")
                    found_any = True
                except Exception:
                    pass

    if not found_any:
        lines.append("| (no expected outputs declared) | — | — | — |")

    return "\n".join(lines)


#: Cap for the final step's rendered `## Expected Outputs` (CR-AIWS-2026-08-129). Measured
#: p90 = 6 lines over 397 AIPs, so 8 clears the overwhelming majority untrimmed while the
#: 17-line outlier still gets the same "digest trimmed" marker every other digest carries.
FINAL_OUTPUTS_MAX_LINES = 8


def _downstream_contract(steps: list[dict], active_idx_1based: int, aip_sections: dict) -> str:
    """What the next step needs from this step's output (forward handoff).

    CR-AIWS-2026-06-036: echo the next step's declared Inputs so the current step
    shapes its output to what successors consume.
    CR-AIWS-2026-08-25 Item 2: for final step, point to AIP Expected Outputs instead.
    CR-AIWS-2026-08-129: for final step, RENDER that section rather than naming it.

    Why the change. Every non-final step already receives CONTENT — the next step's declared Inputs,
    echoed. Only the final step received a pointer, and the final step is where the deliverable is
    produced: the one moment the ASC most needs to stand on its own. Measured over 397 AIPs in this
    repo: 391 (98 %) carry a non-empty `## Expected Outputs`, median 2 lines, p90 6, max 17 — so the
    render is cheap, and the 17-line outlier is capped by `_digest_lines` like every other digest.
    The 6 AIPs without the section keep the previous line, byte for byte.
    """
    idx = active_idx_1based - 1
    nxt = steps[idx + 1] if 0 <= idx and idx + 1 < len(steps) else None
    if not nxt:
        expected = ((aip_sections or {}).get("Expected Outputs") or "").strip()
        if not expected:
            # Fallback, unchanged from CR-08-25: nothing to render, so name the section.
            return "- (final step → see AIP's `## Expected Outputs` for output targets)"
        out = ["- Final step. This AIP's `## Expected Outputs`:"]
        for ln in _digest_lines(expected, FINAL_OUTPUTS_MAX_LINES).splitlines():
            if ln.strip():
                out.append(f"  {ln.strip()}")
        out.append("- Shape this step's output to satisfy the above.")
        return "\n".join(out)
    lines = [f"- Next step ({nxt.get('step_id', '?')} — {nxt.get('title', '')}) needs as Inputs:"]
    nxt_inputs = (nxt.get("Inputs") or "").strip()
    if nxt_inputs:
        for ln in nxt_inputs.splitlines():
            if ln.strip():
                lines.append(f"  {ln.strip()}")
    else:
        lines.append("  - (next step declares no explicit Inputs)")
    lines.append("- Shape this step's output to satisfy the above + the AIP final outcome "
                 "(see AIP Goal & Outcome).")
    return "\n".join(lines)


def _compute_coverage(rendered_asc: str) -> str:
    """Compute coverage: what ASC cannot carry or is complete (CR-AIWS-2026-08-25 Item 5).

    Scans rendered ASC for missing items:
    - Trimmed sections (collapsed to pointers)
    - Unresolved inputs (contains "{{" or "(?:" patterns)
    - Missing handoff rows (table without data rows)
    """
    gaps = []

    # Check for trimmed sections (they're now pointers)
    if "→ See `AIP_Detail_Spec_MVP.md`" in rendered_asc:
        gaps.append("Step Output / Decision Persistence Requirements (trimmed → spec §7.2)")
    if "→ See `Active_Step_Context_Spec_MVP.md`" in rendered_asc:
        gaps.append("Source Verification Requirements (trimmed → spec §5)")

    # Check for unresolved template inputs
    if "{{" in rendered_asc or "{{" in rendered_asc:  # template placeholders
        gaps.append("Unresolved template variables present")

    # Check for missing Inputs (placeholder text)
    if "(see AIP §References" in rendered_asc or "(see AIP §" in rendered_asc:
        gaps.append("Unresolved AIP references (guidance pointers only)")

    # Check for minimal/empty coverage indicators
    if "(no expected outputs declared)" in rendered_asc:
        gaps.append("No expected outputs declared (inherited from AIP)")

    if gaps:
        return "**Coverage Gaps:**\n" + "\n".join([f"- {gap}" for gap in gaps])
    else:
        return "✓ Complete — ASC carries all surfaced guardrails and guidance"


def _resolve_aip_path(aip_ref: str, ai_work: Path) -> Path:
    """Resolve AIP id or path to a file under .ai-work/aip/.

    Accepts a portable `__PROJECT_ROOT__/…` locator (CR-AIWS-2026-07-022) — resolved
    against the project root, NOT the CWD — as well as a plain/absolute path or an id.
    """
    p = resolve_locator(aip_ref, ai_work.parent)
    if p.is_file():
        return p.resolve()
    # id-ish — search plans/exec/local for matching artifact_id
    for sub in ("plans", "exec", "local"):
        for f in (ai_work / "aip" / sub).glob("*.md"):
            meta, _ = parse_frontmatter(read_text(f))
            if meta.get("artifact_id") == aip_ref:
                return f.resolve()
    raise SystemExit(f"error: cannot resolve AIP '{aip_ref}'")


# CR-AIWS-2026-08-127 C2 — step `Kind:` tags → Operating Memory groups. The CR-AIWS-2026-08-25 Item 3 mapping was a
# two-layer no-op: its keys ("Document Review" …) matched none of the 10 real Kind tags (AIP_Detail_Spec §Kind /
# lint_aip enum), and its target groups (code_impl …) did not exist in the store, so `.get()` returned None and
# nothing was ever filtered while the spec claimed it was. Groups here are the seven of operating_memory.md §3
# (`_common.OPERATING_MEMORY_GROUPS`). Comma-separated tags → union; no known tag → all groups.
KIND_TO_MEMORY_GROUPS: dict[str, tuple[str, ...]] = {
    "code": ("tool_gotcha", "required_order", "recurring_shape"),
    "patch_proposal": ("tool_gotcha", "required_order", "recurring_shape"),
    "sql": ("tool_gotcha", "required_order", "recurring_shape"),
    "canonical_edit": ("tool_gotcha", "required_order", "recurring_shape"),
    "review": ("verification_trap", "recurring_shape", "where_to_look"),
    "triage": ("verification_trap", "recurring_shape", "where_to_look"),
    "research": ("cost_sizing", "where_to_look", "rejected_option", "required_order"),
    "plan": ("cost_sizing", "where_to_look", "rejected_option", "required_order"),
    "organize": ("required_order", "tool_gotcha", "verification_trap"),
    "test_design": ("required_order", "tool_gotcha", "verification_trap"),
}


def _memory_groups_for_kind(kind: str) -> "tuple[list[str] | None, list[str]]":
    """(groups or None, recognised tags). None = every group (no Kind, or no tag in the table)."""
    tags = [t.strip().lower() for t in (kind or "").split(",") if t.strip()]
    groups: list[str] = []
    known: list[str] = []
    for t in tags:
        if t in KIND_TO_MEMORY_GROUPS:
            known.append(t)
            for g in KIND_TO_MEMORY_GROUPS[t]:
                if g not in groups:
                    groups.append(g)
    return (groups or None), known


def _memory_slice_line(kind: str, groups: "list[str] | None", known: list[str]) -> str:
    """The one-line 'Lát cắt' the reader sees before the digest (CR-127 C2; mirrors read_operating_memory.py)."""
    if groups:
        return (f"- Lát cắt: Kind={', '.join(known)} → nhóm {', '.join(groups)} "
                f"(mục ngoài lát cắt được đánh dấu *bù* — DP-127-C)")
    if (kind or "").strip():
        return f"- Lát cắt: mọi nhóm (Kind `{kind.strip()}` không có trong bảng KIND_TO_MEMORY_GROUPS)"
    return "- Lát cắt: mọi nhóm (step không khai Kind)"


def main() -> int:
    p = argparse.ArgumentParser(description="Build Active Step Context")
    p.add_argument("--workspace", required=True)
    p.add_argument("--aip", help="AIP id or path (omit to read pointer)")
    p.add_argument("--step-id", help="Step id (omit to read pointer)")
    p.add_argument("--pointer-file",
                   help="Alternate pointer file (default <workspace>/.current_step.json)")
    p.add_argument("--output",
                   help="Override output path (default 00c_active_step_context.md)")
    p.add_argument("--digest-lines", type=int, default=8,
                   help="Max lines for the AIP Goal/Outcome orientation digest (default 8)")
    p.add_argument("--scope-lines", type=int, default=5,
                   help="Max lines for the AIP Scope orientation digest (default 5)")
    ns = p.parse_args()

    ws = Path(ns.workspace).resolve()
    if not ws.is_dir():
        print(f"error: workspace not found: {ws}", file=sys.stderr)
        return 2

    aip_ref, step_id = ns.aip, ns.step_id
    if not (aip_ref and step_id):
        pointer_path = Path(ns.pointer_file) if ns.pointer_file else ws / ".current_step.json"
        if not pointer_path.exists():
            print(
                "error: no --aip/--step-id and no pointer file; "
                "run set_current_step.py first",
                file=sys.stderr,
            )
            return 2
        ptr = json.loads(read_text(pointer_path))
        # CR-AIWS-2026-07-064 D2 (Rule 9): the pointer file is DATA — a non-string aip_path/aip_id
        # crashed inside resolve_locator (s.startswith) with a raw traceback.
        aip_ref = (locator_str(aip_ref) or locator_str(ptr.get("aip_path"))
                   or locator_str(ptr.get("aip_id")))
        step_id = step_id or ptr.get("step_id")

    ai_work = find_ai_work_root(ws) / ".ai-work"
    aip_path = _resolve_aip_path(aip_ref, ai_work)
    meta, body = parse_frontmatter(read_text(aip_path))
    steps = parse_aip_steps(body)
    selected_lens = _extract_selected_lens(body)  # CR-030: Task Lens hint for the reading surface
    allow_raw_search = _allow_raw_search(body, step_id)  # CR-052: optional AIP-level raw-search grant
    step = next((s for s in steps if s["step_id"] == step_id), None)
    if step is None:
        print(
            f"error: step {step_id} not found in {aip_path}",
            file=sys.stderr,
        )
        return 2

    # CR-AIWS-2026-06-036: per-step orientation derived from the already-parsed AIP body + step list.
    aip_sections = extract_sections(body)
    step_map, step_index, step_total = _step_map(steps, step_id)
    downstream = _downstream_contract(steps, step_index, aip_sections)  # CR-2026-08-25: pass aip_sections
    goal_digest = _digest_lines(aip_sections.get("Objective", ""), ns.digest_lines)
    outcome_digest = _digest_lines(aip_sections.get("Expected Outputs", ""), ns.digest_lines)
    # CR-AIWS-2026-08-25 Item 1: explicit union of In Scope + Out of Scope (fixes parser-level
    # bug where or-chain dropped Out of Scope when Execution Scope was an H2 with H3+ children)
    in_scope = aip_sections.get("In Scope", "")
    out_of_scope = aip_sections.get("Out of Scope", "")
    scope_text = (in_scope + "\n\n**Out of Scope:**\n" + out_of_scope).strip() if out_of_scope else in_scope
    scope_digest = _digest_lines(scope_text, ns.scope_lines)

    task_id = ws.name
    queue_path = _first_existing(ws / "02_runtime_queue.jsonl", ws / "02_investigation_queue.jsonl")
    queue_rows = read_jsonl_lenient(queue_path) if queue_path else []
    blocking_queue = [
        r for r in queue_rows
        if str(r.get("blocking", "")).lower() in {"true", "1", "yes"} or r.get("status") == "blocked"
    ]
    capture_rows = read_jsonl_lenient(ws / "08_capture_inbox.jsonl")
    output_index = read_jsonl_lenient(ws / "step_outputs" / "index.jsonl")
    decision_index = read_jsonl_lenient(ws / "decision_traces" / "index.jsonl")

    # CR-AIWS-2026-08-25 Item 3: Compute staleness instead of hard-coded "fresh"
    pointer_path = ws / ".current_step.json"
    pointer_step = ""
    if pointer_path.exists():
        try:
            ptr_data = json.loads(read_text(pointer_path))
            pointer_step = ptr_data.get("step_id", "")
        except Exception:
            pass

    # Compute staleness: stale / possibly_stale / fresh
    asc_output_path = Path(ns.output) if ns.output else ws / "00c_active_step_context.md"
    staleness_status, staleness_reason = _compute_staleness(
        pointer_step, step_id, aip_path, asc_output_path,
        step.get("Expected Outputs", "")
    )

    asc_meta = {
        "artifact_type": "active_step_context",
        "artifact_id": f"ASC-{task_id}-{step_id}",
        "task_id": task_id,
        "working_aip_ref": meta.get("artifact_id", ""),
        "working_aip_path": portable_locator(aip_path, ai_work.parent),
        "active_step_id": step_id,
        "active_step_title": step.get("title", ""),
        "source_aip": meta.get("artifact_id", ""),
        "source_aip_path": portable_locator(aip_path, ai_work.parent),
        "step_id": step_id,
        "step_index": step_index,
        "step_total": step_total,
        "status": "active",
        "active_task_lens": selected_lens,
        "staleness_status": staleness_status,
        "staleness_reason": staleness_reason,
        "updated_at": today(),
    }

    # Extract new Item 2 content
    guardrails = _extract_guardrails(aip_sections, ws)
    read_first = _extract_read_first(aip_sections)
    acceptance = _extract_acceptance(step, step_index, step_total)
    workspace_actions = (step.get("Workspace Actions") or "").strip()

    out_lines: list[str] = [
        dump_frontmatter(asc_meta),
        f"# Active Step Context — {step.get('title', '')}",
        "",
        "## AIP Goal & Outcome",
        "- Goal (AIP-level objective):",
        _indent(goal_digest),
        "- Final outcome (AIP Expected Outputs):",
        _indent(outcome_digest),
        "- Scope:",
        _indent(scope_digest),
        "",
        "## Step Map — You Are Here",
        step_map,
        "",
        "## Downstream / Output Contract",
        downstream,
        "",
        # CR-AIWS-2026-08-25 Item 2: new guardrails + actions + acceptance sections
        "## Guardrails (from AIP)",
        guardrails,
        "",
        "## Read First",
        read_first,
        "",
    ]

    # Workspace Actions (optional, render only if present)
    if workspace_actions:
        out_lines += [
            "## Workspace Actions",
            workspace_actions,
            "",
        ]

    # Acceptance Criteria
    out_lines += [
        "## Acceptance Criteria",
        acceptance,
        "",
        "## Active Task Lens",
        (f"- {selected_lens}" if selected_lens
         else "- No explicit lens (No-Lens) — read from intent (zero forced overhead)"),
        "- Reading-surface hint (CR-030): when a lens is set, prioritise its preset "
        "`relevant_source_types` + `register_priority`/`expansion_priority` "
        "(`.ai-work/wiki/task_lens_presets/`) when ordering what to read — a HINT, not a hard "
        "filter; expand or verify raw/source when correctness needs it.",
        "",
        # Operating Memory digest moved after "## Notes / Constraints" (CR-AIWS-2026-08-127 C3, DP-127-E):
        # the step speaks first, hints after. See the block right before Coverage.
        "## Step Objective",
        _format_multiline(step.get("Objective", "")),
        "",
        "## Recommended Mode",
        _format_multiline(step.get("Recommended Mode", "")),
        "",
    ]
    # CR-AIWS-2026-08-25 Item 6: optional Procedure and Acceptance fields
    _proc = (step.get("Procedure") or "").strip()
    if _proc:  # optional (CR-AIWS-2026-08-25 Item 6) — omit when absent (lean surface)
        out_lines += [
            "## Procedure",
            _proc,
            "",
        ]
    _acc = (step.get("Acceptance") or "").strip()
    if _acc:  # optional (CR-AIWS-2026-08-25 Item 6) — omit when absent (lean surface)
        out_lines += [
            "## Acceptance",
            _acc,
            "",
        ]
    _aa = (step.get("Assigned Agent") or "").strip()
    if _aa:  # optional field (CR-AIWS-2026-07-018) — omit when absent (lean surface)
        out_lines += [
            "## Assigned Agent",
            _aa + "   (execute via: py .ai-work/agents/tooling/run_agent.py start <instance> --aip <this AIP> --task \"<step objective>\")",
            "",
        ]
    _ex = (step.get("Executor") or "").strip()
    if _ex:  # optional field (CR-AIWS-2026-08-044 C4) — plan-time executor; omit when absent
        out_lines += [
            "## Executor",
            _ex + "   (plan-time choice — pass as `--executor` on the dispatch; desk default when absent)",
            "",
        ]
    _diff = (step.get("Difficulty") or "").strip()
    _kind = (step.get("Kind") or "").strip()
    if _diff or _kind:  # optional fields (CR-AIWS-2026-07-059) — omit when absent (lean surface)
        out_lines += [
            "## Difficulty / Kind",
            (("Difficulty: " + _diff if _diff else "") + ("   Kind: " + _kind if _kind else "")).strip(),
            "",
        ]
    out_lines += [
        "## Applicable Guidelines",
        _format_multiline(step.get("Applicable Guidelines", "")),
        "",
        "## Recommended Skills",
        _format_multiline(step.get("Recommended Skills", "")),
        "",
        "## Inputs",
        _format_multiline(step.get("Inputs", "")),
        "",
        "## Expected Outputs",
        _format_multiline(step.get("Expected Outputs", "")),
        "",
        "## Step Output / Decision Persistence Requirements",
        "→ See `AIP_Detail_Spec_MVP.md` §7.2",
        "",
        "## Source Verification Requirements",
        "→ See `Active_Step_Context_Spec_MVP.md` §5",
        "",
        "## Done Condition",
        _format_multiline(step.get("Done Condition", "")),
        "",
        # CR-AIWS-2026-08-25 Item 3: Add Output State block
        "## Output State",
        _render_output_state(step.get("Expected Outputs", ""), ws, aip_path),
        "",
        "## Notes / Constraints",
        _format_multiline(step.get("Notes / Constraints", "")),
        "",
    ]

    # CR-AIWS-2026-08-127 C2/C3 (revises CR-AIWS-2026-08-25 Item 3): Operating Memory digest, scoped by the
    # step's Kind tags via KIND_TO_MEMORY_GROUPS, capped at 3, topped up with newest entries of other groups
    # when the slice is short (DP-127-C), rendered AFTER Notes / Constraints (DP-127-E). Digest render itself
    # (one line per entry, ` → ref` suffix, one-line caveat) lives in _common.operating_memory_digest (C1).
    _om_kind = (step.get("Kind") or "").strip()
    _om_groups, _om_known = _memory_groups_for_kind(_om_kind)
    out_lines += [
        "## Operating Memory (L2 — bài học vận hành)",
        _memory_slice_line(_om_kind, _om_groups, _om_known),
        *operating_memory_digest(ai_work, max_items=3, groups=_om_groups, top_up=_om_groups is not None),
        "",
    ]

    # CR-AIWS-2026-08-25 Item 5: Add Coverage section (measured from rendered ASC)
    rendered_so_far = "\n".join(out_lines)
    coverage = _compute_coverage(rendered_so_far)
    out_lines.extend([
        "## Coverage",
        coverage,
        "",
    ])

    # CR-AIWS-2026-06-052: surface an explicit AIP-level raw-search grant ONLY when the step declares
    # it (lean — the common no-grant case adds no section; the default is governed by the lookup tool
    # + the CLAUDE.md raw-search-authorization rule).
    if allow_raw_search == "true":
        out_lines.extend([
            "## Raw Search Authorization",
            "- This step GRANTS raw (un-registered) search (`allow_raw_search: true`). When a "
            "registered lookup misses, you MAY run `lookup_wiki_source.py --authorized aip "
            "--include-raw on-empty --lookup-mode object`. Raw hits are un-registered — open directly "
            "and register via /aiws-wiki build-meta if reused. (CR-AIWS-2026-06-052)",
            "",
        ])
    elif allow_raw_search == "false":
        out_lines.extend([
            "## Raw Search Authorization",
            "- This step explicitly does NOT grant raw search (`allow_raw_search: false`). Raw / "
            "beyond-default-scope search needs HUMAN authorization — halt and ask. (CR-AIWS-2026-06-052)",
            "",
        ])

    # CR-AIWS-2026-06-036 (full-lean): runtime-pointer sections render ONLY when they carry data —
    # empty "- ..." placeholders are dropped. Dead Finding/Open-Question-ID slots were removed
    # entirely (findings live in 04_findings.md, open questions in 05_open_questions.md). Pure
    # duplicates (Step ID/Title, Source AIP, Active References) dropped — covered by frontmatter,
    # the H1, the Step Map, and ## Inputs respectively.
    def _append_if(title: str, rows: list[dict], **kw) -> None:
        if rows:
            out_lines.extend([title, _bullet_refs(rows, **kw), ""])

    _append_if("## Runtime Queue Blockers", blocking_queue)
    _append_if("## Relevant Queue Item IDs", queue_rows)
    _append_if("## Previous Step Results / Handoff Inputs", output_index)
    _append_if("## Decision Discussion Trace References", decision_index,
               id_key="discussion_trace_id")
    _append_if("## Capture Inbox References", capture_rows)

    out_path = Path(ns.output) if ns.output else ws / "00c_active_step_context.md"
    write_text(out_path, "\n".join(out_lines))
    print(f"active step context written: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
