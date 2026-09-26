# Open Points — TASK-20260913-update-gat-proposal

## Metadata

| Field | Value |
|---|---|
| Task ID | `TASK-20260913-update-gat-proposal` |
| Workspace | `.ai-work/workspaces/hoinv/TASK-20260913-update-gat-proposal/` |
| AIP source | `.ai-work/aip/hoinv/exec/AIP-EXEC-006-update-gat-proposal.md` |
| Maintainer | AI + HUMAN requester |
| Created | 2026-09-13 |
| Last updated | 2026-09-13 |

## Index

| ID | Status | Severity | Raised at | Summary |
|---|---|---|---|---|
| OP-TASK-20260913-update-gat-proposal-01 | resolved | 🔴 Blocker | 2026-09-13 | Select the product-policy profile for the revision |

## OP-TASK-20260913-update-gat-proposal-01 — Product-policy profile

- **Status:** resolved
- **Severity:** 🔴 Blocker
- **Raised at:** 2026-09-13
- **Context:** AIP-EXEC-006 STEP-01; council F1–F11

### Question / Issue
The council requires decisions that the report does not authoritatively supply: durable scope/Desk key, AIP cardinality/bypass, authorization owner and revocation, promotion, retrieval provider, tenancy, retention/audit, DSH compatibility, test ownership, and HUMAN authority boundaries. Choosing these silently would change the product architecture.

### Options considered
1. **Conservative MVP (recommended):** `ProjectScope` as durable container; `AgentDesk=(principal_id, project_scope_id, agent_id)`; one Working AIP and one canonical Task Workspace per non-trivial task/run; no bypass inside GAT MVP; deny-by-default per-operation authorization with deny precedence and immediate revocation; no Task/Desk→Agent promotion in MVP; shipped DSH substring retrieval only; tenant-scoped IDs; tombstone-first deletion with configurable retention; append-only/tamper-evident audit; adapt to current DSH and label per-agent routing future-only; package-owned conformance gates; HUMAN exclusively owns acceptance/deviation/activation; security vertical slice gates WebUI.
2. **Expanded MVP:** include a pinned semantic provider, controlled cross-scope promotion, per-agent routing/core DSH changes, and broader WebUI after separate provider/data-governance decisions.
3. **Custom:** HUMAN supplies deviations from the conservative profile.

### History

| Timestamp | Actor | Message |
|---|---|---|
| 2026-09-13 | AI | Raised consolidated blocker and recommended least-authority/current-capability MVP profile. |
| 2026-09-13 | HUMAN | Selected `Conservative MVP (Recommended)`. |

### Conclusion
Resolved by HUMAN: use the Conservative MVP profile exactly as summarized in Option 1. This authorizes proposal drafting only; it does not approve or activate the proposal.

**Follow-up actions:**
- [x] HUMAN selected the Conservative MVP profile.
- [x] AI recorded F1–F11 dispositions, revised the proposal, and obtained exact-hash advisory PASS.
