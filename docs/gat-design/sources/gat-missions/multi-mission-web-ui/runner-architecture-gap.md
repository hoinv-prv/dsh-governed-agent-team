# Runner architecture gap after attempt 63

Independent adversarial design analysis established that meaningful full-baseline dispatch cannot be obtained by copying `vector.expected`, generic fixture assertions, executable untrusted runtimes, or a bridge that lacks product operations.

The accepted governance functions cover identity, readiness, plan and mission bindings, but the frozen source does not expose all real state transitions needed by accepted vector families: write-once Workspace binding, explicit supersession, inactive activation gate, disabled promotion, and explicit optional-capability degradation. Runner-only simulation would not test the implementation.

Required recovery boundary:

1. Preserve accepted governance bytes; add a separately reviewed package-owned control-state module for the missing operations.
2. Runner fixtures contain setup data only and recursively reject truth/assertion/binding/evidence keys.
3. Closed handlers receive `{id, operation}` only, never expected/absence/evidence declarations.
4. Outcome reducers and symbolic predicates use append-only observations from real governance/control/policy/wrapper/memory calls.
5. Preflight requires exact handler, absence-probe and evidence-producer coverage before later baseline dispatch.
6. Stable package-relative implementation manifest binds the complete declared source closure and is rehashed after execution.

This gap invalidates continued runner mutation under WBS v29 ordering. It does not invalidate already accepted governance functions, memory, policy or wrapper bytes. Accepted baseline remains unexecuted.
