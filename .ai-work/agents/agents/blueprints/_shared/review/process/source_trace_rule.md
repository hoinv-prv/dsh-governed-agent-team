# Source Trace Rule (shared)

> Shared across all Document Review Agent blueprints.
> Mapped from: REVIEW_AGENT_BLUEPRINT_TEMPLATE.md §10 (Source/Wiki Usage Policy) + §7 (Review
> Principles) (v0.1).
> Document-type-agnostic.

---

## 1. Wiki-first, NOT Wiki-only

> ⚖ **governance_invariant** `wiki_first` — read Wiki first but verify important findings against source; never Wiki-only.

The agent reads relevant Wiki entries FIRST to understand project context, terminology, design
decisions, cautions, and source-navigation hints. Wiki is the starting point for grounding — it is
NOT the sole authority. For findings that matter, the agent verifies against the underlying
source / reference documents.

## 2. Evidence requirement for important findings

> ⚖ **governance_invariant** `evidence` — important findings cite source/reference; an inference is marked assumption / open question, never presented as confirmed fact.

For each important finding, identify the supporting source / reference when available and record it
in the Evidence / Reference column (see `finding_format.md`):
- cite the specific Wiki entry, source document, section, or line.
- if the finding is based only on inference, mark it `possible_issue` or `open_question` and state
  that it is an assumption — do NOT present an inference as a confirmed fact.

## 3. Conflict policy

> ⚖ **governance_invariant** `conflict_report` — report conflicts as findings; never silently resolve or pick a side.

If the target document conflicts with Wiki / source / reference documents:
- REPORT the conflict as a `conflict`-type finding.
- do NOT silently resolve it or silently pick a side.
- when Wiki and source disagree, surface both and request a HUMAN decision if it affects the
  review outcome.

## 4. Staleness / uncertainty

When a Wiki entry is stale or unverified, prefer the source and note the staleness. Source
verification is required when:
- the Wiki entry is stale or unverified,
- a source / code conflict is detected,
- the output will feed an official deliverable.

## 5. Trace recorded in references_used

All Wiki entries and source documents actually used are listed in `references_used.md` (shared
output template) with what each was used for — so a reader can audit the grounding of the review.

## 6. Source-of-Truth layering (SoT layers) — CR-AIWS-2026-07-012

Every conclusion must be anchored to the CORRECT layer. Classify each reference before using it
(instances may pre-classify via `sot_layer` in `context/source_references.yaml`):

| Layer | Authority over | Examples | Rule |
|---|---|---|---|
| **SoT-1** — "what is correct" | behavior / original semantics | requirement spec, standard, vendor manual, embedded normative spec | Highest authority on *behavior*. Suspected transcription error → verify against the original |
| **SoT-2** — "actual usage / empirical" | usage counts, logs, real callers | object metas, usage inventories, sample sources | Numbers in the reviewed artifact reconcile against here; samples illustrate, enumeration decides |
| **Target-direction** | intended target/category direction | architecture policy, migration policy | Authoritative for DIRECTION only — it does NOT override SoT-1 on "what X does". Divergence = a decision point, not automatically "wrong" |
| **REFERENCE-ONLY** | cross-check | per-item conventions, derived summaries, prior drafts | Never grounds a pass/fail conclusion. Divergence from a reference = a point to raise, not an error |

## 7. Two golden rules — CR-AIWS-2026-07-012

> ⚖ **governance_invariant** `artifact_no_self_proof` — the content under review never proves itself; explanations written inside the reviewed artifact are the SUBJECT of review, not evidence for it. Trace to an independent SoT layer.

> ⚖ **governance_invariant** `reference_not_sot` — a REFERENCE-ONLY or target-direction layer is never elevated into SoT; divergence from them is reported as a decision point.
