# Prerequisite source/design consistency

The approved host worktree remains based on `c291e7961a515f6d7af9304e7fd1d257929aef26`. Formal GAT design consulted: `DETAIL_DESIGN.md` §7, architecture §11, basic §12, the Durable integration prerequisite section, and frozen contract §§7–13. These describe the intended prerequisite operations; the freeze was not edited.

| Intended design | Implemented source | Observed qualification |
|---|---|---|
| DD §7 reserved lifecycle | DSH subagent reserved handle, descriptor/catalog, core Agent admission and loop | Exact generation, quarantine, persisted activation/tombstone, recovery and legacy fixtures; built public smoke |
| DD §7 prompt refresh | DSH agent-loop prepare-prompt, final synchronous Agent guards | Awaited render/retry checks, actual revocation races, built SDK prompt histories |
| DD §7 exact authority | GAT authority, mission/task/projection/journal/roster/mailbox/lifecycle; DSH authenticated control ingress | Actual HTTP receipts, canonical task associations, false/pending publication and withdrawal/recovery tests; 60-cell real dispatcher matrix |
| DD §7 nested capabilities and independent driver | DSH tools registry/executor, shipped delegators/PTC, host-only withAgentDriver; GAT tool policy | Immutable alias/descendant union and current policy checks, actual nested denial and detached live driver regressions |
| Generated-reference ownership | DSH catalog-source-files and Cordis/persistence/tool/client discovery | Explicit build replacement validation, preserved prototypes and catalog regression/freshness checks |
| Public API comments and lint reconciliation | GAT core/tools modules | Source lint clean; supported host/client builds; 270 integration tests independently repeated |

Owning DSH architecture, core/subagent/tools subsystem references, package README pairs and implemented Agent Notes describe the final caller, durability and disposal obligations. Catalogs remain generator-owned; reviewed Chinese pairs retain translated prose and match current declarations. Exact source-map validation and final documentation evidence are recorded separately in `final-mapping.md` and `verification/`.

`verification/tested-source-final-hashes.json` compares all 57 GAT source/test TypeScript files with the installed qualification tree: every pair matches. `verification/sdk-qualified-hash-comparison.json` confirms all seven built SDK runtime artifacts match the artifacts used by the completed SDK replays. SDK qualification covers actual built CLI runtime with source SDK facades; it does not claim an installed wheel or production package.

The comment pass accidentally split expressions and removed the `ATTACHMENT_LIMITS` export. Supported compilation exposed both defects. They were restored before the final compiler, built smoke and 270-test acceptance. Normalized built JavaScript matches the earlier qualified tools AST exactly. Core AST differs through local aliases, cleanup-handle capture, the private acquisition holder and equivalent validation syntax; the full difference was independently reviewed for behavior equivalence. It is not described as an exact AST match. Evidence: `verification/built-js-comparison.json`, `built-core-semantic-review.diff`, `lint-reconciliation.md` and `independent-review.md`.

Two earlier corrective edits lacked a separately written intended paragraph. Their chronology gap is retained in findings and independent review rather than retroactively claiming perfect design-before-code compliance. Later corrective deltas, including API documentation and lint reconciliation, have forward intended design paragraphs. No unresolved source/design conflict has been identified.

Dirty-work protection is independently audited. The original DSH HEAD is unchanged; 365 of 366 protected dirty files match. Its `AGENTS.md` changed outside edits issued by this workstream and remains preserved. GAT baseline files changed only within authorized source/design/workspace or parent handoff scope; the existing source snapshot, compatibility manifest and installer verifier remain unchanged. See `verification/protected-original-and-gat-audit.json`.

This qualification supplies prerequisite APIs and source. Parent production binder composition, changed-host compatibility receipt, profile/packaging/browser acceptance, deployment and canonical promotion remain separate.
