# Open Points — TASK-20260913-triage-gat-rereview-v3

## Metadata
| Field | Value |
|---|---|
| Task ID | `TASK-20260913-triage-gat-rereview-v3` |
| AIP | `AIP-EXEC-007` |
| Date | 2026-09-13 |

## Index
No open, pending, or blocking points.

## Resolved by bounded design choice
- R3 topology: adapter-owned partitioned GAT MCP server; no upstream reference-server backend in MVP.
- R4 atomicity: one transactional adapter store plus fenced anchor/publish recovery; invariant is zero committed/visible domain mutation.
- R6 cache: decision/result cache removed from MVP.
- R7 shared scope: `mission-shared` deferred rather than inventing MissionMembership.

These are proposal decisions only and do not activate implementation.
