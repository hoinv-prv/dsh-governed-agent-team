# Open Points — TASK-20260926-exec-013 Restore session Agent Team toggle

## OP-TASK-20260926-exec-013-01 — Define Disable semantics and activation scope

- **Status:** resolved
- **Severity:** 🔴
- **Raised at:** 2026-09-26
- **Context:** STEP-01 trace of the session activation seam.

### Question / Issue
The current project UI, TeamView type, and TeamService Remote surface do not contain the session activation contract. The supplied DSH checkout contains a reference `enable` flow that loads `team_members.yaml` and provisions teammates, but it exposes only Enable (no teardown/Disable Remote). Before implementing, confirm whether “Enable/Disable” means:

1. Restore the existing intended one-way session opt-in button: show Enable while off; after enabling show the active Team UI, with no destructive disable/teardown; or
2. Add a real Disable action and define what happens to already-provisioned teammates and durable Team state.

### Options considered
1. One-way Enable session opt-in — aligns with the available reference flow and avoids unsafe teardown.
2. Real Enable/Disable lifecycle — requires a new backend contract for teardown and persistence semantics.

### History
| Timestamp | Actor | Message |
|---|---|---|
| 2026-09-26 | AI | Found current project lacks `TeamEnableResult`, `TeamService.remoteEnable`, and session initializer; reference DSH checkout has Enable-only flow. |
| 2026-09-26 | AI | Asking HUMAN to choose semantics before inventing teardown behavior. |

### Conclusion
HUMAN selected the one-way Enable-only session opt-in. Show Enable while the session is off; after enabling, show the Agent Team UI. Do not teardown teammates or durable Team state.

**Follow-up actions:**
- [x] HUMAN confirmed one-way Enable-only semantics.
- [ ] Implement the confirmed contract and add focused tests.
