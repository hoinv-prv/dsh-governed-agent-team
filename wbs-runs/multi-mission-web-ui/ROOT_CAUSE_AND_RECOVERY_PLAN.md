# Root-cause analysis and WBS recovery proposal

## Pause state

The mission is paused at selected/HUMAN-approved WBS v29, cumulative charge 63/80, with no active worker or background job. Candidate v30 passed planning review but was never HUMAN-approved or selected. No accepted conformance baseline, DSH, network, npm/pnpm, installation, activation or proposal activation was executed.

## Why accepted progress did not move

The dashboard stayed at 7/10 accepted because attempts 57, 58 and 60–63 all targeted conformance recovery but none passed independent acceptance. They improved mechanics, yet did not produce a valid conformance boundary. Attempt count increased while accepted-task count did not.

## Root causes

### RC1 — Wrong decomposition boundary

The WBS treated conformance as a runner/CLI problem. Static analysis later proved that the accepted package did not expose all real state transitions needed by accepted vector families: Workspace write-once binding, supersession, activation denial, promotion denial and explicit degradation. The runner was therefore pushed to simulate missing product behavior.

### RC2 — Self-fulfilling oracle design

Early handlers received the complete vector or fixture-provided assertions and could reproduce `vector.expected`. Synthetic tests proved dispatch mechanics but did not prove that disposition, reason and symbolic result were derived from real implementation observations.

### RC3 — Trust and runtime architecture was selected too late

Successive attempts moved from missing handlers, to ambient runtime modules, to hashed executable files, to VM execution, then to declarative fixtures. Independent review correctly found, in sequence, missing evidence enforcement, self-attested hashes, transitive imports, TOCTOU/cache ambiguity, VM escape/hang risk and finally simulation-only semantics.

### RC4 — Incomplete provenance model

Implementation hashing was designed before the complete executable closure was defined. It used absolute paths or incomplete source subsets instead of a stable package-relative manifest covering the reviewed implementation and checking pre/post-run drift.

### RC5 — Review gate was after implementation rather than before architecture

Each attempt combined architecture, implementation, testing and acceptance. The independent reviewer first saw the full trust model only after code existed, so each review exposed the next architectural class of defect. There was no accepted 51-vector contract matrix before runner mutation.

### RC6 — Progress metric mismatch

The report counts accepted WBS tasks, not lines changed or tests passed. Multiple 5/5 synthetic suites were real local improvements but could not change the accepted denominator because the task-level independent gate still failed.

## Recommended recovery: WBS v31 split gates

Do not execute monolithic candidate v30. Use v31 with the remaining 17 attempts:

1. Selection — 1 attempt.
2. Conformance contract matrix — up to 2 attempts.
3. Control-state reconciliation — up to 3 attempts.
4. Closed handlers/probes/reducers — up to 5 attempts.
5. Runner assembly — up to 2 attempts.
6. Integration/build/smoke — up to 2 attempts.
7. Deterministic freeze/handoff — up to 2 attempts.

Total: 63 + 17 = 80.

### Gate A — Contract matrix before code

Statically enumerate all 51 accepted IDs without dispatching them. For each vector pin exactly one real API/control prerequisite, handler, observation reducer, symbolic predicate, absence probe and evidence producer. Missing API or producer blocks downstream work immediately.

### Gate B — Real missing control operations

Add a separately reviewed package-owned control module instead of modifying accepted governance/policy/memory/wrapper bytes or faking outcomes in the runner.

### Gate C — Strict trust separation

Fixtures contain setup data only and recursively reject expected/actual/disposition/reason/result/assertion/binding/evidence/counter fields. Handlers receive only `{id, operation}`. Only the terminal comparator sees expected and required declarations.

### Gate D — Observation-derived conformance

Closed handlers invoke actual package APIs. Append-only probes capture policy/admission/selector/MCP/backend/partition/audit/lifecycle/control behavior. Reducer-owned predicates produce symbolic labels from raw observations; mutation tests must prove unrelated successful work cannot PASS.

### Gate E — Stable freeze provenance

Use sorted package-relative POSIX paths, complete declared source closure, exact leaf hashes and a domain-separated root. Reject missing/extra/alias/symlink/case-collision inputs and rehash after execution. Literal caller paths remain diagnostic evidence only.

## HUMAN decision needed

The mission must remain paused until exact reviewed v31 bytes are presented and explicitly approved. Approval of v29 or the unselected v30 does not authorize v31. No DSH or accepted-baseline decision is needed for this recovery phase.
