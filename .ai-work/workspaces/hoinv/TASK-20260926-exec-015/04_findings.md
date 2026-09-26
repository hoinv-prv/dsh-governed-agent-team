# Findings

## STEP-00 — Scope confirmation

The HUMAN confirmed that Durable Agent has a close architectural relationship with GAT and requested that the GAT design reference incorporate it. The update must cover relationship, shared concepts, boundaries, persistence/recovery mapping, integration assumptions, gaps, and roadmap without representing Durable Agent features as already integrated into GAT.

Evidence: current-session HUMAN confirmation on 2026-09-26.

## STEP-01 — Durable Agent ↔ GAT architecture mapping

### Relationship

GAT and Durable Agent are complementary, not interchangeable:

- GAT owns Team orchestration: root Session authority, child Session lifecycle, roster, mailbox, tasks, missions, work status, readiness, recovery, and Web/tools.
- Durable Agent owns stable member definition and file-backed member context: immutable profile, SOUL, bounded memory catalog/items, and member working files.
- Durable Agent explicitly does not spawn agents, schedule concurrent work, retry tasks, discover routes, or manage runtime lifecycle. GAT must remain the runtime lifecycle owner.
- Durable Agent files must not become a second authority for GAT roster/task/mailbox/runtime state.

### Identity mapping

The same `name` is used at different scopes:

- GAT name identifies a teammate inside one root Team/Session.
- Durable Agent name identifies a storage directory under one workspace or the user's global home.

Two GAT Sessions in the same workspace using the same member name would therefore share workspace-local Durable Agent storage even though their Team logs and child Sessions are distinct. Global scope broadens storage sharing further but does not merge GAT Team membership or child Sessions.

### Manifest compatibility

The common fields are `version`, `members`, `name`, `description`, `prompt`, `context`, `provider`, `model`, and optional `reasoning_effort`.

Current incompatibilities:

- Durable Agent accepts optional `storage_scope: workspace|global`, defaulting to `workspace`; GAT's strict member-key set rejects `storage_scope` and then falls back to the built-in roster.
- Durable Agent requires `context`; GAT permits omission and defaults it to `fresh`.
- GAT adds member count, trim, and string-length limits not specified by the Durable Agent document.
- Thus there is only a narrow portable subset today; sharing the same filename does not mean the schemas are unified.

### Context and persistence mapping

- `profile.json`: immutable durable identity/route/scope; conflicts fail closed.
- `SOUL.md`: persistent behavioral guidance loaded for every task.
- `memory/index.json` plus selected Markdown items: bounded hint-driven member memory, not vector/semantic retrieval.
- `working/`: member-owned task documents, not GAT task-board authority.
- GAT root Session events remain canonical for Team coordination and lifecycle.

### Required target integration sequence (proposed, not implemented)

1. Parse one canonical manifest snapshot instead of running two drifting parsers.
2. Validate all routes and storage bindings before side effects.
3. Ensure each durable profile/storage before the member's first task.
4. Let GAT record provisioning, start the continuable child, and record active/failed.
5. For every task/turn, inject host/GAT governance first, then SOUL at the required durable-context position, then member/task context; precedence must be explicit.
6. Load the bounded memory index and only relevant items.
7. Persist Team events only to the root Session log; persist persona/memory/working artifacts only to Durable Agent storage.
8. On restart, reconcile the GAT child first, then revalidate the durable profile binding.
9. Treat name/route/scope changes as explicit migration or new identity, never silent rewrite/copy.

### Major integration risks

- Mid-session manifest drift: GAT freezes roster at Enable while Durable Agent reloads the manifest on every storage access.
- Policy precedence: mutable SOUL must not override host/GAT governance or HUMAN boundaries.
- Concurrent access: multiple Sessions may share one workspace/global durable identity, but no locking/CAS contract is specified for memory files.
- GAT fallback: an invalid file including `storage_scope` silently changes the roster to built-ins; those fallback members have no defined Durable Agent authorization/storage policy.
- Partial provisioning: storage may exist without an active child, and earlier members may remain active after a later failure; storage is evidence, not proof of runtime activation.
- Durable Agent memory and the proposed GAT MCP/reference-memory system are separate layers and must not be conflated.

## STEP-02 — GAT reference update and review

Updated `docs/GAT_DESIGN_AND_FEATURE_REFERENCE.md` with:

- Durable Agent in the architecture and package map;
- exact schema compatibility matrix and portable subset;
- GAT control-plane versus Durable Agent persistence-plane boundary;
- identity/storage-scope semantics and cross-Session sharing caveats;
- SOUL/profile/memory/working file responsibilities;
- proposed integration sequence and fail-closed rules;
- distinction between Durable Agent operational memory and proposed GAT reference memory;
- current implementation status, source path, limitations, and maintenance triggers.

Independent review identified and the document corrected these nuances:

- roster fallback applies only to file/YAML/schema loading; route preflight failure aborts Enable;
- the portable subset must also meet `teamMembersMaxBytes`;
- manifest authorizes route/scope, profile detects binding conflicts, and GAT/DSH owns effective runtime route;
- authority precedence is distinct from unresolved literal SOUL/GAT prompt ordering;
- Durable context is required per task, not automatically every turn;
- a canonical snapshot requires snapshot-aware or atomic digest-verification APIs because Durable Agent currently reloads the live manifest;
- durable binding must be revalidated before the first resumed task is admitted;
- shared storage is conditional on compatible authorization/profile, not name alone;
- member-owned files are logically owned but not filesystem-isolated.

A second focused review found no remaining material discrepancy in the updated sections.

## STEP-03 — Verification

- `docs/GAT_DESIGN_AND_FEATURE_REFERENCE.md` contains AIP-EXEC-015 attribution and a dedicated §7 Durable Agent relationship.
- External Durable Agent source path and `storage_scope` contract are present in the reference.
- Independent evidence review and focused correction re-review completed.
- `git diff --check` passed for the updated document and task artifacts.
- AIWS scoped task lint passed with 0 errors and 0 warnings.
- CAP-001 was deferred to backlog BL-015-CAP-001 for separate HUMAN curation; no Wiki or Truth was changed.
- No unresolved open point remains.
