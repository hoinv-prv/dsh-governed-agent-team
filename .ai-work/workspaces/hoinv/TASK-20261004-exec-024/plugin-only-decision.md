# HUMAN decisions — active task/intent memory policy

Date: 2026-10-04. AIP-EXEC-024 re-plan authority, not an independent review verdict.

1. HUMAN said “theo huong chi sua plugin”: retain plugin-only scope and unchanged DSH core/loop.
2. HUMAN then clarified “memory duoc dung by task/intent nen se khong dua vao system prompt”: memory is retrieved for the current task/intent through guarded tools. Do not inject memory body, catalog, provider guidance or provenance into system prompt. This latest clarification supersedes the intermediate per-step memory prompt policy.

Active interpretation follows the existing proposal's explicit assignment selection: `brief.inputs` contains exact `durable-memory:<id>` references. The plugin binds the stable Durable identity, guards those reads with current GAT execution authority, and returns the selected item only as a bounded task Session tool result. No inferred semantic search, eager member memory load or all-memory permission is added. A task without selected refs cannot read memory.

WK Detail DD-03 says only Host policy decides placement/tooling/authority; `Consumer.readMemory` is independent of `modelContribution`. Accordingly ordinary binding/model requests make no openTaskContext/modelContribution calls. Prompt-refresh qualification and the proposed DSH prerequisite are historical/superseded for this entry, not active blockers. Preserve existing direct composition behavior and all previous evidence.

Review remains an explicit evidence-only task mode with no memory tools. Packet inputs must come from actual trusted Host derivation and current assignment/candidate binding; no invented receipts or generic reviewer fallback. Independent qualification/design and implementation review requirements remain in the AIP.
