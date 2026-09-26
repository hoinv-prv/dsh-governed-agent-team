# Governed Agent Team Conservative MVP — Threat Model

Status: candidate for independent Security review and HUMAN acceptance  
Proposal binding: `docs/GAT_AGENT_TEAM_MCP_MEMORY_ARCHITECTURE_PROPOSAL.md`, Revision 3, SHA-256 `dc47dc96949ea0c83d779d3dec11e30fbefb0bd738c4fb4898e6367313bd60ee`  
Vector binding: `docs/conformance/gat-conservative-mvp-v1.json` (hash is recorded only after this candidate is frozen)  
Authority: this document is a pre-code security gate, not proposal approval, implementation conformance, DSH integration, or activation evidence.

## 1. Security objective

The Conservative MVP must preserve tenant, principal, ProjectScope, Task/AIP/Workspace, AgentDesk, physical memory partition, lifecycle, and audit boundaries even when Agent/LLM input is malicious, stale, ambiguous, or replayed. Missing, stale, contradictory, unsupported, or unverifiable state fails closed. Unauthorized exposure and mutation thresholds are zero.

## 2. Assets

1. Tenant/principal identity and authenticated runtime context.
2. ProjectScope, AgentDesk, Mission, Task, Working AIP, fixed Task Workspace, Team plan, conditional native Mission, and AgentRun identities/revisions.
3. Policy, membership, readiness, approval, lifecycle, selector, capability, and topology snapshots/hashes.
4. Memory record content, history, source references, classifications, indexes, materializations, tombstones, holds, purge manifests, backups, and idempotency dispositions.
5. Package-private MCP capability and physical partition handles.
6. Append-only audit events, epochs, sequence/head anchors, emergency sink, operator alerts, and reconstruction evidence.
7. Conformance vectors, implementation bytes/hash, raw verifier output, and Activation Manifest.

## 3. Actors and authority

| Actor | Trusted authority | Explicitly not trusted/authorized |
|---|---|---|
| HUMAN decision owner | High-risk direction, threat/vector acceptance, lifecycle authorization, final acceptance, proposal approval, activation, merge/deploy | No implicit decision from silence or an earlier unrelated approval |
| Authenticated principal | Operations explicitly allowed by current policy within its bound scopes | Cannot claim another tenant/principal/ProjectScope/Workspace |
| Agent/Leader | Bounded execution and wrapper-tool input | Cannot grant lifecycle authority, choose selectors, call raw MCP, promote/share, approve itself, or activate |
| LLM/tool arguments | Operation data only | Identity, scope, ownership, policy, selector, capability, approvals, or trusted instructions |
| GAT package/PDP/adapter | Build immutable context, authorize, select one partition, enforce wrapper admission, normalize results | Cannot invent package readiness, native approvals, HUMAN decisions, or DSH capabilities |
| Partitioned backend | Execute only one trusted package-selected partition and transactional protocol | Cannot accept Agent-selected partition keys or broad-read/post-filter |
| Audit/anchor/emergency sinks | Integrity and availability evidence | Failure cannot be treated as success or permit content/mutation |
| Independent reviewer | Advisory verification bound to exact bytes/evidence | Cannot replace HUMAN acceptance/activation |
| DSH bridge/native Team | Future pinned integration surface | Not integrated in this standalone phase; no current capability claim |

## 4. Trust boundaries and data flows

1. **HUMAN/session → governance records:** exact decision, revision, artifact hash, and source reference cross into immutable execution evidence.
2. **LLM → wrapper schema:** only operation data crosses. Identity/selector/capability fields are rejected or ignored; raw MCP prefixes are denied before PDP/MCP/backend.
3. **Authoritative stores → PDP:** one fresh consistent snapshot binds execution tuple, readiness, Team approval, conditional Mission approval, policy, membership, lifecycle, capability, and hashes. No decision/result cache.
4. **PDP → adapter/backend:** a complete typed selector chooses exactly one physical partition; broader retrieval and post-filtering are forbidden.
5. **Mutation → audit/anchor/publish:** prepare, local audit append, synchronous anchor, publish, and response are ordered so audit/anchor failure yields zero committed/visible domain mutation.
6. **Backend → Agent:** records are untrusted reference data with provenance/freshness labels and instruction delimiters; unauthorized/nonexistent resources are externally indistinguishable.
7. **Backup/restore/purge:** tombstones, holds, authorizations, manifests, and backup inventory cross a lifecycle authority boundary and must reconcile without resurrection.
8. **Implementation → conformance/activation:** exact proposal/vector/implementation/environment hashes and raw evidence precede any activation; standalone status uses explicit not-integrated markers for DSH and MCP bridge.

## 5. Threat register and required controls

| ID | Threat / abuse case | Required controls | Required vectors | Residual risk and owner | Activation disposition |
|---|---|---|---|---|---|
| T01 | LLM forges tenant, principal, ProjectScope, Task/AIP/Workspace, or AgentDesk identity | Authenticated out-of-band immutable context; write-once execution tuple; principal-bound Desk; resource containment; deny before namespace lookup | GAT-AUTH-003A/B, GAT-WS-001, GAT-EXEC-002/004, GAT-TENANT-001, GAT-DESK-001, GAT-PATH-001 | Runtime authenticator correctness; package owner + HUMAN | Block until zero-leak vectors pass on pinned runtime |
| T02 | Missing/contradictory allow state becomes implicit access | Explicit-deny wins; absence of allow denies; reason codes and immutable decision evidence | GAT-AUTH-001/002/004/005 | Policy authoring errors; policy owner | Block on any unauthorized byte/change |
| T03 | Reuse of stale policy, membership, readiness, approval, or session decision after revoke | Fresh authoritative consistent snapshot per operation; no decision/result cache; stale request denial | GAT-REV-001, GAT-EXEC-004, GAT-AIP-002/003, GAT-PLAN-002, GAT-MISSION-001 | Source-store availability; package/policy owners | Block unless revocation is effective before next operation |
| T04 | Non-trivial execution bypasses Working AIP/readiness or creates/replaces Workspace | Package-owned readiness oracle; exactly one Working AIP/Workspace; new Task for replacement with provenance | GAT-AIP-001/002/003, GAT-WS-001, GAT-EXEC-001/002/003/004 | Oracle semantics drift; package owner + HUMAN | Block on missing readiness evidence or identity alias |
| T05 | Native Team executes unapproved/stale plan; mapped native Mission is misrepresented | Exact current Team planApproval gate; conditional Mission binding only when mapped; no claim for unmapped Mission | GAT-PLAN-001/002, GAT-MISSION-001 | DSH API drift; integration owner | Standalone remains not integrated; later pinned PoC required |
| T06 | Broad backend read followed by application filter exposes other tenant/principal/Task data | PDP emits complete selector; one physical partition handle; zero non-selected reads; typed capability | GAT-PREFILTER-001/002/003, GAT-TENANT-001, GAT-DESK-001 | Backend instrumentation coverage; storage owner | Block until selector non-bypass traces pass |
| T07 | Agent discovers or directly invokes raw MCP tools, supplying its own partition | Raw tool absent from schema; execution prefix guard before PDP/MCP/backend; package-private capability | GAT-MCP-RAW-001 | Host tool-discovery drift; adapter/integration owners | Block if raw prefix visible or callable |
| T08 | Cross-scope copy/promotion creates uncontrolled durable knowledge | No share/promote operations; target-scope write requires independent authorization; source unchanged on denial | GAT-PROMO-001 | Manual out-of-band copying; HUMAN/governance owner | Feature disabled in MVP |
| T09 | Semantic fallback/provider substitution transfers or leaks data | Literal substring only; deterministic normalization/order; unsupported semantic request fails closed; no third party | GAT-SEARCH-001/002 | Unicode normalization edge cases; package owner | Block until deterministic fixtures repeat |
| T10 | ID probing, counts, ranking, timing, traces, logs, or errors disclose existence | Same external status class/shape and bounded timing; no unauthorized counts/content; redacted audit reason | GAT-GET-001, GAT-AUTH-003A/B, GAT-TENANT-001, GAT-DESK-001, GAT-AUDIT-READ-001 | Deployment timing variance; security owner + HUMAN approves measured bound | Block until deployment-specific timing policy is measured later |
| T11 | Duplicate/replayed/concurrent mutation creates extra or lost revisions | Idempotency ledger; optimistic expected revision; one durable disposition; deterministic retry | GAT-WRITE-001, GAT-REVISION-001, GAT-TXN-001 | Local storage faults; storage owner | Block on duplicate logical mutation |
| T12 | Tombstoned/expired/held/purged data remains searchable or is resurrected by restore | Tombstone-first removal; clock-bound expiry exclusion before matching/get; HUMAN lifecycle authority; current fenced purge authorization; manifest and backup-inventory reconciliation; restore non-resurrection | GAT-DELETE-001/002, GAT-LIFECYCLE-001/002, GAT-RESTART-001, GAT-RETENTION-001, GAT-EXPIRY-001, GAT-BACKUP-001 | Backup provider guarantees; lifecycle/HUMAN owner | Block until inventory reconciliation passes; holds always win |
| T13 | Secret/prohibited data is stored or retrieved as instruction | Required classification; reject/deterministic redact; provenance/source refs; reference-only delimited results | GAT-AUDIT-001, GAT-SEARCH-001, GAT-INJECTION-001, GAT-CLASS-001, GAT-RETENTION-001, wrapper tests bound by GAT-MCP-RAW-001 | Classifier/redaction false negatives; tenant policy owner | Block absent versioned retention/classification policy |
| T14 | Audit can be forged, reordered, truncated, omitted, or failure can expose/mutate data | Canonical event bytes/hash chain, monotonic sequence, signed checkpoints/heads, audit.read auth, primary/emergency sink rules, operator alert | GAT-AUDIT-001/002/003/004/005, GAT-AUDIT-READ-001 | Signing-key/sink compromise; security/operator owner | Block on any unverifiable segment or unavailable required sink behavior |
| T15 | Crash between prepare/audit/anchor/publish/response exposes partial state | Single-store transaction/outbox; anchor-before-publish; fenced recovery/abort; prepared/aborted invisible; idempotent response recovery | GAT-TXN-001/002, GAT-RESTART-001 | Filesystem durability assumptions; storage owner | Block until every crash boundary passes repeatedly |
| T16 | Tests/build are treated as permission to activate incomplete/stale bytes | Content-addressed proposal/vector/implementation/evidence; independent reviews; complete Activation Manifest; separate HUMAN activation | GAT-ACT-001 and every vector's evidence binding | HUMAN procedural error; coordinator + HUMAN | Implementation remains inactive until separate manifest-bound activation |
| T17 | DSH/MCP/backend topology drift invalidates standalone evidence | Evidence records pinned DSH design-source hash, explicit DSH-runtime-not-integrated and MCP-bridge-not-integrated states, backend topology/capability revisions; later compatibility WBS | GAT-PLAN-001/002, GAT-MISSION-001, GAT-MCP-RAW-001, GAT-ACT-001 | Future DSH change; integration owner | No DSH readiness claim from standalone run |
| T18 | Optional reference-memory outage is treated as task state or causes fabricated remembered facts | Task/Mission state and SoT remain authoritative outside memory; explicit degraded or security-unavailable disposition; never fabricate results or silently substitute a provider | GAT-DEGRADE-001, GAT-SEARCH-002 | Agent may hallucinate when reference context is absent; runtime/prompt owner + HUMAN | Block any integrity fallback; availability degradation needs explicit product disposition |

## 6. Required security invariants

- Unauthorized content exposure: zero records and zero bytes.
- Unauthorized mutation: zero record, revision, index, materialization, tombstone, hold, purge, or backup-state changes.
- Denied/raw requests: zero backend/MCP calls; raw requests also stop before PDP except one permitted denial audit disposition.
- One operation uses one current consistent authorization snapshot and at most one complete physical partition selector.
- Audit reconstruction maps each tested allow/deny to one decision and one valid event without raw secret material.
- Prepared or aborted mutations never become visible; after restart there is exactly one published revision or the prior revision.
- Tombstones are never normally readable; holds prevent physical purge but never restore searchability.
- All evidence and approvals bind exact bytes/hashes; missing evidence is not PASS.

## 7. Evidence and conformance obligations

Every executed vector must bind: proposal hash; vector-file hash; complete implementation hash; policy and membership revisions, snapshot hashes and matched rule IDs; Task/AIP/Workspace binding and readiness evidence; Team-plan and conditional Mission approvals; DSH design-source version/hash plus explicit runtime integration status; MCP bridge status/revision; partitioned backend topology, selector and capability revisions; environment/fixtures; operation/input; expected and actual disposition/reason/result; observable side-effect counters; audit event/chain/anchor/sink results; exact command, exit code, start/end timestamps, raw stdout/stderr, run ID and independent reviewer.

For the current standalone phase, `dsh_runtime_status` and `mcp_bridge_status` must be `not_integrated`; these are evidence values, not waivers. The later full conformance WBS must use the literal frozen implementation hash in `.artifacts/gat-conformance/<implementation-hash>/` and the exact proposal-pinned package command.

## 8. Residual risk decisions requiring HUMAN authority

1. Accept or reject this exact threat-model hash and the exact vector-file hash before code.
2. Later accept deployment-specific bounded timing targets; this proposal does not invent them.
3. Later approve the complete standalone conformance report.
4. Later approve a pinned DSH compatibility/integration plan.
5. Separately approve the proposal and an exact Activation Manifest; neither follows from this gate.

## 9. Gate outcome

Default: **HOLD**. Coding is forbidden until independent Security review returns no material change and the HUMAN explicitly accepts exact hashes for this file and `docs/conformance/gat-conservative-mvp-v1.json`. Any later byte change invalidates that acceptance and dependent readiness.
