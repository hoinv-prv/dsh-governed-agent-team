# Scope decision proposal — OP-024-03

Date: 2026-10-04. Status: superseded by HUMAN plugin-only/task-intent memory decision; historical proposal only. AIP-EXEC-024 remains active at qualification; production implementation has not started.

## Demonstrated obstacle

On selected Host `c1157f7ed448b40c463c1a43fa595b12294fd50d`, real GAT assignment/admission and real WK service/Consumer through Loader produce two execution model requests but one prompt assembly. After a public confirmed-memory commit between attempts, the new catalog is visible to the Consumer while the retry still contains the previous catalog. The freshness contract test fails; the characterization test passes. Receipts and exact observed revisions are in `verification/qualification-attempt-08.*` and `qualification-observation.json`.

The loop captures `decision.assembly` and renders it before its retry loop (`packages/core/agent-loop/src/agent.ts`, `step`). Each attempt runs route preparation and projects that captured rendered value; `agent/request-error` retry continues without another assembly. Existing `system-prompt-admission.spec.ts` intentionally asserts one assembly and retained prompt during compaction retries. Its focused baseline passes. This is a current Host contract, not a WK provider malfunction.

GAT `DETAIL_DESIGN.md` §7 defines a per-actual-request extension in the separately qualified prerequisite Host. §9 now records experimental qualification of this current Host without inheriting that capability. WK Detail DD-04/DD-06 defines per-call context; its public Consumer cannot replace a Host-owned rendered/logged prompt.

## Recommended bounded extension

Authorize a separate additive **opt-in per-request contribution refresh** prerequisite on this current Host. It runs an awaited owner-scoped refresh before rendering/reconciling every actual admitted request, including retries. Only opted-in owned contributions refresh; ordinary sections, accepted user admission and pre-step decisions keep their existing retry semantics. Deny dispatch on refresh failure, lost execution authority, cancellation or owner disposal. Keep the actual refreshed prompt reconstructable from persisted Session events and prevent duplicate owned sections. Tool/schema refresh must be explicitly designed and bounded; no dynamic schema mutation during assembly or unqualified re-admission.

Proposed source owners, subject to design review before edits:

- DSH `packages/core/system-prompt/src/index.ts`: reversible owner-scoped refresh contract and participation semantics.
- DSH `packages/core/agent-loop/src/agent.ts`: await the opted-in refresh before per-attempt rendering/projection and final request derivation.
- Their focused tests and package READMEs: default unchanged retry behavior, opted-in freshness/logging, failure and cancellation negatives, effect disposal and nonrecursive assembly.
- GAT `docs/gat-design/DETAIL_DESIGN.md` plus Basic/Integration/source map: attributed current-Host prerequisite and adapter contract, preserving §§5/7/8 history and the existing direct path.
- AIP-EXEC-024: a dated re-plan before widening its explicit DSH core/loop exclusion, with prerequisite design/qualification ahead of adapter implementation. Retain the same isolated worktree and exact input/effect manifests.

Keep WK service/provider/storage, Team persistence schema and dispatch lifecycle unchanged. Retain independent review requirements. No broad older Host patchset, default profile activation or deployment is proposed. Exact public event/API shape must be reviewed against the current owner contracts before source edits; this proposal is permission for that bounded prerequisite design/implementation, not a fabricated final API approval.

## Alternatives and tradeoffs

1. **Recommended: authorize the bounded current-Host prerequisite.** Meets the original freshness requirement while preserving default retry behavior and current isolated GAT assignment semantics. Adds DSH-owned design/code/tests to scope.
2. **Keep adapter-only scope.** Leave qualification blocked at STEP-02 until a compatible Host exposes the required public operation. No production adapter can be accepted under the current contract.
3. Select another Host only after separately qualifying its current isolated GAT assignment, public exports and cleanup/recovery. The older direct-continuable qualification alone does not establish these semantics, so it is not an immediate equivalent substitution.

Reject post-log transport rewriting, full default prompt reassembly on retry, silently disabling retries, or weakening freshness to once per step. They change the requested contract or the current Host contract without the explicit decision.
