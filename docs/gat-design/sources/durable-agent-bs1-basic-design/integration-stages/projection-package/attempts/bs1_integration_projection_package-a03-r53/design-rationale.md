# BS1 Design Rationale

> Deterministic source map for the canonical design facts.

## identity
- input-lock/semantic-inputs.json#/semantic_source_set_id

## source_bindings
- input-lock/semantic-inputs.json#/sources

## ownership_interfaces
- component-ownership-dag.json#/outputs/owners
- component-ownership-dag.json#/outputs/interfaces
- effect-boundary.json#/outputs/component_ownership

## dag
- component-ownership-dag.json#/outputs/dependency_dag

## flows
- component-flow-closure.json#/outputs/normal_flows
- component-flow-closure.json#/outputs/terminal_flows
- component-flow-closure.json#/outputs/restart_routes
- component-flow-closure.json#/outputs/persistence_and_result_closure
- component-flow-closure.json#/outputs/downstream_manifests

## tests
- test-sizing-gate.json#/outputs/test_layers
- test-sizing-gate.json#/outputs/compatibility_tests
- test-sizing-gate.json#/outputs/invariant_matrix
- test-sizing-gate.json#/outputs/artifact_negative_vectors

## sizing
- test-sizing-gate.json#/outputs/df_sizing
- test-sizing-gate.json#/outputs/implementation_gate
- component-flow-closure.json#/outputs/sizing_gates

## limitations
- component-ownership-dag.json#/outputs/limitations
- effect-boundary.json#/outputs/provenance_and_limitations
- component-flow-closure.json#/outputs/negative_vectors_and_authority

## governance
- input-lock/semantic-policy.json#/

## authority
- dto-plan-boundary.json#/outputs/authority_and_zero_model
- effect-boundary.json#/outputs/effect_scope
- state-handoff-boundary.json#/outputs/evidence_limits_and_authority

