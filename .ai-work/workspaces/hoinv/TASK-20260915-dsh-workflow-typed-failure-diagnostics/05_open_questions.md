# Open Points — TASK-20260915-dsh-workflow-typed-failure-diagnostics

## Metadata

| Field | Value |
|---|---|
| Task ID | `TASK-20260915-dsh-workflow-typed-failure-diagnostics` |
| AIP source | `.ai-work/aip/hoinv/exec/AIP-EXEC-010-dsh-workflow-typed-failure-diagnostics.md` |
| Maintainer | AI + HUMAN (`hoinv`) |
| Created | 2026-09-16 |
| Last updated | 2026-09-16 |

## Index

| ID | Status | Severity | Raised at | Summary |
|---|---|---|---|---|
| OP-TASK-20260915-dsh-workflow-typed-failure-diagnostics-01 | open | 🔴 Blocker | STEP-03 | Activate patched workflow tool in a fresh Harness process |

## OP-TASK-20260915-dsh-workflow-typed-failure-diagnostics-01 — Active-runtime restart required

- **Status:** open
- **Severity:** 🔴 Blocker
- **Raised at:** STEP-03
- **Context:** running DSH Web process at `127.0.0.1:3080`

### Question / Issue

The earlier host-build blocker was removed with the minimal Typert-required parameter rename. `build:lib:host` now passes, and all affected workflow suites pass (107 tests total). The current Web process (`pnpm dsh web`) was started before the patch and there is no `pnpm run dev:web` watcher, so plain-package changes are not hot-reloaded. Restarting that process from inside this live session would terminate/disrupt the GUI that owns the session.

### Assumption in use

Keep the source patch built and verified, but do not claim the current workflow tool exposes `agentFailures`. Do not run another council review through the old loaded transport.

### Conclusion

A fresh/restarted Harness Web process is required before the schema-enforced council retry. This restart must occur outside the current live session or through an operator-controlled maintenance window.
