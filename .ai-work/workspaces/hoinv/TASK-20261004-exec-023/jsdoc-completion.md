# Public API JSDoc completion — intended documentation delta

## Scope

Add concise JSDoc to the exported GAT core APIs identified by `verification/doc-sync-final-02.log` and to `packages/experimental/gat-tools/src/team-config.ts`. Copy the same comment-only source changes into the matching isolated DSH packages. Complete the existing generated English `docs/event-producer-consumer.md` Chinese counterpart by synchronizing only the generated table blocks while retaining its Chinese-owned prose.

## API documentation contract

Document current implementation behavior at each reported declaration. Summaries name the value, operation, or ownership exposed; function-like exports document every parameter and non-void return. Do not infer new guarantees from the frozen member-binding contract or alter runtime behavior, signatures, types, control flow, or existing decisions. Keep descriptions aligned with the implementation and local contracts in the frozen member-binding design (especially §§4–9) and GAT DD-07 / DD-16 as applicable. Formal intended delta: `docs/gat-design/DETAIL_DESIGN.md` §7, “Prerequisite public API documentation completion.”

## Files

The affected GAT core files are `approved-plan-import.ts`, `attachments.ts`, `authority.ts`, `binding-deadline.ts`, `journal.ts`, `member-binders.ts`, `member-binding.ts`, `mission-board.ts`, `mission-plan.ts`, `projection.ts`, `roster.ts`, `task-board.ts`, and `types.ts`. The affected tools file is `team-config.ts`. The DSH documentation pair is `docs/event-producer-consumer.md` and its existing Chinese counterpart.

## Verification

Run the assigned direct `verify-export-jsdoc.ts` command from the isolated DSH root and retain its final output in this workspace. Changes remain comments and generated-doc table synchronization only; no behavior tests are in scope.
