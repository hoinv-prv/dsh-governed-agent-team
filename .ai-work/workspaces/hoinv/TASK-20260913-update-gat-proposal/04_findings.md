# Findings

## Task Understanding and Gate U1 Evidence
- HUMAN selected shared task `task-1` and explicitly instructed: “Tôi đã mô tả rõ trong task-1. Hãy thực hiện task-1 nhé.”
- Deliverable: revise `docs/GAT_AGENT_TEAM_MCP_MEMORY_ARCHITECTURE_PROPOSAL.md` against `/home/hoinv/work/advisor_workspace/TASK-1_COUNCIL_REVIEW_REPORT.md`.
- Scope excludes implementation, approval, activation, merge, and deployment.
- Done means F1–F11 have traceable dispositions, the revision has a new hash and verification evidence, and the proposal remains pending fresh review/HUMAN activation.

## Confirmed Findings
- Council verdict on the input revision is `BLOCKED`; F1–F5 are activation blockers and F6–F11 require revision.
- Canonical Workspace is the task/session-bound Task Workspace at `.ai-work/workspaces/{account}/{task_id}/`, not a durable project/repository container.
- Canonical architecture requires a Working AIP before meaningful execution.
- Canonical Task Lens is optional/lightweight runtime retrieval context; it is not an authorization boundary or mandatory persisted object.
- Controlled promotion requires Knowledge Value plus Source/Authority/Target checks and a separate promotion decision.
- The proposal's SoT/reference separation, access-before-retrieval direction, immutable request scope, and concurrency guardrails should be preserved.

## Inferred Findings
- The safest bounded MVP is a security vertical slice with deny-by-default authorization, no cross-scope promotion, shipped substring retrieval as baseline, and explicit future capability gates.
- Applying that profile would close the council ambiguities without inventing a third-party provider or granting new authority, but it is still a product decision reserved for HUMAN.

## HUMAN Decision
- On 2026-09-13, HUMAN selected **Conservative MVP (Recommended)**. This authorizes drafting with the safe/current-capability profile; it does not approve or activate the proposal.

## F1–F11 Change Matrix
| Finding | Approved disposition |
|---|---|
| F1 | Rename durable project/repository boundary to `ProjectScope`; reserve `Task Workspace` for canonical per-task runtime; key Desk by `(principal_id, project_scope_id, agent_id)`. |
| F2 | Require one Working AIP and one canonical Task Workspace per non-trivial Task execution; AgentRuns reuse them; no GAT MVP bypass. |
| F3 | Add deny-by-default subject/resource/action decision contract, deny precedence, revision binding, reason codes, immediate revocation, and per-operation reauthorization. |
| F4 | Prohibit Task/Desk→Agent and cross-scope promotion in MVP; only same-scope controlled candidate flows with HUMAN decision and source/authority/target checks. |
| F5 | Baseline shipped DSH substring retrieval; semantic retrieval is future/provider-gated with no silent fallback or third-party transfer. |
| F6 | Make tenant/principal, scope, origin, source refs, status, and run attribution required or explicitly conditional; define namespace uniqueness. |
| F7 | Expand audit for full auth reconstruction; append-only hash-chained/tamper-evident records, controlled readers, configurable retention/redaction. |
| F8 | Add classification/redaction, configurable retention/TTL, tombstone-first deletion, immediate active-index/cache revocation, backup purge policy, and lifecycle audit. |
| F9 | Add current DSH mapping/capability matrix; adapt to current runtime and label per-agent provider/model/preset routing future-only. |
| F10 | Add pinned package-owned executable conformance vectors and persisted verifier evidence with absence-of-side-effect assertions. |
| F11 | Add authority matrix; HUMAN exclusively owns acceptance, deviation, activation, and high-risk decisions; propagate decision routing fields. |

## To-Verify Findings
- Exact current DSH entity/tool mapping and capability evidence in the proposal.
- No stale claim treats semantic retrieval, cross-scope promotion, AIP bypass, or per-member routing as MVP behavior.

## Verification Evidence
- Final stable proposal SHA-256: `c682b65579ea9962ff8bfd819255c31c180bf3ac52df3ddcf7ae690ebf999652`.
- `git diff --check` on proposal/AIP/workspace changes: exit `0`, no output.
- Task-scoped AIWS lint after fixes: `errors=0 warnings=0 info=0`.
- Conflict sweep confirmed every occurrence of semantic/vector retrieval and cross-scope promotion is a prohibition, negative test, or explicitly future-only item.
- Working AIP/Task Workspace and HUMAN acceptance/activation references are consistently normative.

## Notes
- AIWS AIP lint passed with `errors=0 warnings=0 info=0` before start.
- Wiki lookup resolved Workspace Boundary Spec as `SRC-METHOD-methodology-20-specs-workspace-boundary-spec-mvp-md-e5e3`.
- Proposal lookup returned no project-specific match; retrieval gap imported as `CAP-006-01`.
- First fresh independent review returned `REVISE`: F1/F2/F4/F5/F6/F11 closed; F3/F7/F9/F10 partial; F8 closed with precision gaps.
- Applied all reported fixes: physical namespace prefilter, atomic revision/cache validation, complete audit failure behavior, deterministic anchored chain, legal-hold/purge evidence, pinned DSH mapping and workspace path binding, added conformance vectors, execution identity, immutable record history, and threat-model gate.
- Two stale-hash reviews correctly refused or requested revision while the proposal was still changing; their substantive gaps were fixed before final attestation.
- Exact-hash independent delta re-review returned **PASS** for `c682b65579ea9962ff8bfd819255c31c180bf3ac52df3ddcf7ae690ebf999652`; F1–F11 all PASS with no residual issue requiring revision.
- Review is advisory only. Proposal remains inactive and is not HUMAN-approved, accepted, or activated.
- Non-blocking implementation follow-up: pin the GENESIS signature algorithm and key-rotation format in the future implementation schema/vector package.

## Final Capture Sweep
- Reviewed the proposal diff, F1–F11 matrix, independent-review iterations, open points, and final output.
- New Knowledge Value captures found during final sweep: `0`.
- Capture Inbox total: `1` (`CAP-006-01`, proposal wiki-meta retrieval gap).
- Relation candidates pending: `0`.
- `CAP-006-01` must be triaged/deferred before AIP close; no direct Wiki promotion is authorized.
