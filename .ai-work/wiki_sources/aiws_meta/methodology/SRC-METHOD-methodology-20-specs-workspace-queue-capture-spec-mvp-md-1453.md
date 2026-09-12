---
artifact_type: wiki_source_meta
source_id: SRC-METHOD-methodology-20-specs-workspace-queue-capture-spec-mvp-md-1453
title: methodology / 20_specs/Workspace_Queue_Capture_Spec_MVP.md
source_type: methodology_spec
artifact_locator: .ai-work/truth/canonical/methodology/20_specs/Workspace_Queue_Capture_Spec_MVP.md
profile_id: methodology_spec
status: active
updated_at: 2026-06-25T01:39:18.953496+00:00
promotion_status: draft
source_representation_caution: Representation quality has not been reviewed.
representation_type: markdown
system: aiws
maintenance_status: active
review_required: False
review_status: approved_to_apply
---
# Wiki Source Meta — methodology / 20_specs/Workspace_Queue_Capture_Spec_MVP.md

## Summary
Minimal human/AI-readable summary of the task.

## Knowledge Targets
- reference
- domain
- pattern

## Lookup Keys
- Workspace / Queue / Capture Spec for AI Work System MVP
- for AI Work System MVP Folder placement
- for AI Work System MVP Task ID convention
- for AI Work System MVP Required files
- for AI Work System MVP Optional files
- task
- Workspace
- AIP
- capture
- Capture
- Notebook
- workspace
- Knowledge
- TASK
- Working
- Queue
- runtime
- execution
- context
- workspaces
- should
- may
- Personal
- queue
- source
- Task
- Purpose
- Findings
- Inbox
- jsonl
- findings
- working
- Hub
- file
- current
- Questions
- Placement
- addendum
- Context
- Source

## Source-Specific Hints
- heading: Workspace / Queue / Capture Spec for AI Work System MVP
- heading: 1. Mục đích
- heading: 2. Vai trò của Workspace
- heading: 3. Workspace placement and naming
- heading: 3.1. Folder placement
- heading: 3.2. Task ID convention
- heading: 4. Workspace file set
- heading: 4.1. Required files
- heading: 4.2. Optional files
- heading: 4.3. Why this split
- heading: 5. Task Brief spec
- heading: 5.1. Purpose
- heading: 5.2. Suggested sections
- heading: 5.3. Usage
- heading: 6. Active AIP reference spec
- heading: 6.1. Purpose
- heading: 6.2. Recommended content
- heading: 6.3. Why not duplicate full AIP
- heading: 7. Active Step Context spec
- heading: 7.1. Placement
- heading: 7.2. Optional pointer file
- heading: 7.3. Purpose
- heading: 7.4. Metadata
- heading: 7.5. Required sections
- heading: 7.6. Rules
- heading: 7.7. Update triggers
- heading: 8. Investigation Queue spec
- heading: 8.1. Placement
- heading: 8.2. Format
- heading: 8.3. Purpose
- heading: 8.4. Required fields
- heading: 8.5. Optional fields
- heading: 8.6. Example
- heading: 8.7. Enums
- heading: 8.8. Queue rules
- heading: 9. Findings spec
- heading: 9.1. Placement
- heading: 9.2. Purpose
- heading: 9.3. Suggested structure
- heading: 9.4. Rules
- heading: 10. Open Questions spec
- heading: 10.1. Placement
- heading: 10.2. Purpose
- heading: 10.3. Suggested sections
- heading: 10.4. Suggested per-question fields
- heading: 10.5. Rules
- heading: 11. Draft Output spec
- heading: 11.1. Placement
- heading: 11.2. Purpose
- heading: 11.3. Suggested sections
- heading: 11.4. Rule
- heading: 12. Capture Inbox spec
- heading: 12.1. Placement
- heading: 12.2. Purpose
- heading: 12.3. Format
- heading: 12.4. Required fields
- heading: 12.5. Optional fields
- heading: 12.6. Example
- heading: 12.7. Enums
- heading: 12.8. Rules
- heading: 12.9. Triage rollup (CR-AIWS-2026-06-015 F4)
- heading: 13. History log / task log spec
- heading: 13.1. Placement
- heading: 13.2. Purpose
- heading: 13.3. Typical contents
- heading: 14. Final Output spec
- heading: 14.1. Placement
- heading: 14.2. Purpose
- heading: 14.3. Rule
- heading: 15. Workspace lifecycle
- heading: 15.1. Create
- heading: 15.2. Run
- heading: 15.3. Checkpoint
- heading: 15.4. Finalize
- heading: 15.5. Archive
- heading: 16. Lint targets
- heading: 16.1. Workspace lint
- heading: 16.2. Active Step Context lint
- heading: 16.3. Queue lint
- heading: 16.4. Capture lint
- heading: 17. Boundary rules summary
- heading: Queue vs Capture
- heading: Findings vs Wiki
- heading: Open Questions vs Findings
- heading: AIP vs Active Step Context
- heading: 18. Kết luận
- heading: Knowledge-runtime sprint addendum — Workspace, notebook, and knowledge-runtime boundary
- heading: Workspace and notebook-like working context
- heading: Boundary rules
- heading: Deferred notebook work
- heading: Personal Notebook boundary addendum
- heading: Purpose
- heading: Boundary
- heading: Capture relation
- heading: Task-bound note rule
- heading: Source Understanding Artifact capture boundary addendum
- heading: Boundary
- heading: Capture path
- heading: Guardrail
- heading: Task Lens trace and capture canonical addendum
- heading: Controlled Knowledge Promotion capture addendum
- heading: v0.9.8 Wiki Meta / Index candidate capture addendum
- heading: v0.9.9 Working AIP Connection workspace addendum
- heading: v0.9.10 Workspace Boundary addendum
- heading: Runtime Queue
- heading: Capture Inbox
- heading: Queue vs Capture Inbox
- heading: Close classification

## Related Sources
- **SRC-METHOD-methodology-20-specs-workspace-boundary-spec-mvp-md-e5e3** — role: system_foundation — Defines the container that this spec's runtime file set lives in: what a Workspace is, the executor-agnostic Task Workspace at `.ai-work/workspaces/{account}/{task_id}/` (one workspace shared by AIP run / agent run / agent-via-AIP run), and the boundary against Working AIP, Knowledge Hub, Notebook and canonical docs. Coupling = workspace placement + the boundary statement this spec's addendum reproduces verbatim; a change to the Task Workspace path or to the boundary propagates into every placement path in §3–§14 here. [asserted]
- **SRC-METHOD-methodology-20-specs-workspace-runtime-guidance-mvp-md-feaa** — role: downstream_navigation — Carries the runtime flow for the artifacts this spec defines: when a Workspace is created, how the Runtime Queue and Capture Inbox are worked during execution, and the classify/close pass at task end. It consumes the file names and enums fixed here (`02_investigation_queue.jsonl` / `02_runtime_queue.jsonl`, `08_capture_inbox.jsonl`, capture status/target enums), so renaming or re-enumerating the file set here propagates to it. [asserted]
