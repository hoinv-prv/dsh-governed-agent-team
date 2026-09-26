# Threat-model gate — attempt-gat-threat-001

## Candidate artifacts

- `docs/security/GAT_CONSERVATIVE_MVP_THREAT_MODEL.md`
- `docs/conformance/gat-conservative-mvp-v1.json`
- Proposal binding: Revision 3, SHA-256 `dc47dc96949ea0c83d779d3dec11e30fbefb0bd738c4fb4898e6367313bd60ee`, inactive.

## Coverage

- Threat model covers assets, actors, authority boundaries, trust boundaries, tenant/principal/account/ProjectScope/Workspace confusion, physical selector/path isolation, raw MCP bypass, stale authorization, response side channels, prompt injection, record classification/retention, lifecycle/hold/purge/backup/restore, audit integrity/sinks/atomic recovery, DSH topology drift, evidence and activation.
- Baseline contains every 43 unique proposal §18.1 ID plus clearly marked threat-model extension vectors for filesystem containment, prompt injection, classification/redaction, retention policy, audit-read isolation, and reference-memory degradation.
- The evidence contract includes proposal/vector/implementation, policy/membership/rules, execution/readiness/native approvals, selector/capability/topology, DSH/MCP integration status, environment, expected/actual/side effects/audit, exact command/exit/timestamps/raw stdout/stderr/run/reviewer bindings.
- Candidate status is HOLD/pending independent Security review and exact HUMAN acceptance. Full baseline execution, implementation conformance, DSH integration, and activation remain unclaimed.

## Review state

Independent read-only Security reviewer: subagent `fecd8a65-edd7-43d0-a20c-8cab1acaa212`.

Review 1 returned REVISE on its exact bytes for reason fidelity, missing extension-to-threat mappings, and absent expiry/backup-restore vectors. All three findings were corrected without dispatching product work. A fresh read-only Security reviewer, subagent `00a7cef4-ac0f-4585-995c-efbb0e49edb8`, is reviewing the newly frozen bytes. No hash or verdict may be relied upon until that reviewer returns a final exact-byte disposition.
