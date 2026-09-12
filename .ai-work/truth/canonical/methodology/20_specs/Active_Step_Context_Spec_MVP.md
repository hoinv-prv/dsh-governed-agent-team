# Active Step Context Spec MVP

Status: Canonical MVP spec  
Version: v0.9.16  
Date: 2026-04-26  
Source sprint: Active Step Context Minimal Spec Sprint

---

## 1. Purpose

This spec defines minimal Active Step Context behavior for AIWS MVP.

The goal is to help AI execute the current Working AIP step using only step-relevant runtime context, while preserving authority and traceability boundaries.

---

## 2. Central stance

```text
ASC gives AI the current-step runtime view,
while Workspace persists outputs/decisions/discussion traces
and Working AIP remains task authority.
```

---

## 3. Core rules

### 3.1. ASC is temporary step-local runtime view

```text
Active Step Context is a temporary, step-local runtime view.
It helps AI focus on the current step.
It does not replace Working AIP, Workspace, Wiki, or source verification.
```

### 3.2. Working AIP remains authority

```text
ASC is derived from Working AIP current step.
It may expose execution context, but Working AIP remains the task/step authority.
```

### 3.3. Workspace persists context

```text
Workspace persists task context.
ASC displays the current-step slice of that context.
Runtime Queue blocks current work; Capture Inbox captures future-value candidates.
```

### 3.4. Source pointers are not verification

```text
ASC can carry source routes and verification requirements,
but verified evidence still requires reading AIWS-readable source representation.
```

### 3.5. Output/decision/discussion trace must persist when reused

```text
Important step outputs, HUMAN–AI interaction-derived decisions/conclusions,
and the key discussion process that led to them
must be persisted in Workspace with trace metadata.
```

---

## 4. Minimal Active Step Context model

Recommended fields:

```yaml
asc_id:
task_id:
working_aip_ref:
working_aip_version:
active_step_id:
active_step_title:
step_index:        # CR-036: 1-based position of the active step in the AIP
step_total:        # CR-036: total number of steps in the AIP
step_objective:
step_guardrails:
step_inputs:
step_outputs_expected:
required_previous_outputs:
previous_step_results:
runtime_queue_blockers:
capture_inbox_refs:
wiki_lookup_refs:
source_verification_requirements:
known_limitations:
staleness_status:
staleness_reason:
last_refreshed_at:
```

---

## 5. Allowed ASC content

ASC may include:
- current step id/title/objective
- step-specific guardrails
- step input/output pointers
- required previous step output refs
- decision discussion trace refs
- Runtime Queue blockers
- Capture Inbox refs relevant to current step
- Wiki/source pointers
- source verification requirements
- known limitations/caveats
- staleness metadata
- a COMPACT digest of the Working AIP's overall goal / expected outcome / scope (CR-036)
- a step-position map — the active step within the AIP step sequence, "k of n" (CR-036)
- a downstream output contract — what the next step's Inputs / the AIP's Expected Outputs require of this step's output (CR-036)

ASC should prefer pointers over full content; the goal/scope/contract items above are CAPPED digests (orientation), never a full reproduction of the AIP.

---

## 6. Restricted content

ASC should not include:
- full source documents
- full Wiki dumps
- full Workspace history
- unreviewed candidates as truth
- hidden scratchpad reasoning
- automatic new task instructions
- raw binary/non-text content
- full discussion transcript unless explicitly needed
- redundant restatements of frontmatter — step id/title and source AIP path are already in the ASC frontmatter (CR-036)
- never-populated placeholder sections — finding/open-question id slots live in `04_findings.md` / `05_open_questions.md`, not the ASC (CR-036)
- empty runtime-pointer sections — render Queue / Previous-Step-Results / Decision-Trace / Capture sections ONLY when they carry data (CR-036)

Operating Memory digest (§L2 section) is scoped by mapping the step's `Kind:` tags (controlled set, AIP_Detail_Spec §Kind) to Operating Memory groups (`KIND_TO_MEMORY_GROUPS` in `build_active_step_context.py`; union over comma-separated tags; no Kind or no known tag ⇒ all groups), capped at 3 entries, topped up with the newest entries of other groups when the slice is short (each marked *bù*), and preceded by a one-line "Lát cắt" stating the slice; an empty store shows a placeholder line; a slice filtered to empty says so explicitly. Each entry renders as one head line (title · group · age · ` → ref` when the entry carries a `ref`) plus its body, bodies longer than `OPERATING_MEMORY_BODY_MAX` truncated to their first sentence. The section is rendered after `## Notes / Constraints`, before `## Coverage` (CR-AIWS-2026-08-25 Item 3, corrected and extended by CR-AIWS-2026-08-127 C1–C3).

---

## 7. Build / Refresh / Staleness

ASC is built from:
- Working AIP
- current step
- selected Workspace context
- Runtime Queue blockers
- relevant source/Wiki pointers
- previous step outputs/decisions

ASC should refresh when:
- active step changes
- Working AIP changes
- Runtime Queue blockers change
- source representation status changes
- previous step output changes
- HUMAN decision changes
- output expectation changes

Recommended staleness values:

```text
fresh
possibly_stale
stale
unknown
```

---

## 8. Step Output / Decision Trace integration

ASC may reference:

```yaml
previous_step_results:
  - output_id:
    result_type:
    output_locator:
    discussion_trace_locator:
    review_status:
    reason_for_use:
```

ASC does not store these artifacts. Workspace stores them.

---

## 9. Working AIP relation

Working AIP defines:
- task scope
- step flow
- expected outputs
- branch conditions
- done conditions

ASC prepares only the active slice of the Working AIP.

If ASC conflicts with Working AIP, Working AIP wins.

---

## 10. Workspace relation

Workspace stores:
- step outputs
- decision discussion traces
- runtime queue
- capture inbox
- task-local notes
- draft/final outputs
- logs/traces

ASC displays current-step relevant subset.

---

## 11. Wiki / Source Verification relation

Wiki lookup result in ASC is route/context only.

To claim source verification:
- AI must read AIWS-readable source representation
- verification level must support the claim
- limitations must be handled
- Step Output Meta should record source_refs and verification_level

---

## 12. Non-goals

This spec does not define:
- full task execution framework
- full runtime orchestration engine
- semantic context optimizer
- token scoring/telemetry
- automatic AIP rewriting
- full memory/cache system
- UI/form

---

## 13. Conclusion

Active Step Context is the current-step runtime view. It supports focused execution while keeping Working AIP as authority, Workspace as persistence layer, and source representation as evidence boundary.
