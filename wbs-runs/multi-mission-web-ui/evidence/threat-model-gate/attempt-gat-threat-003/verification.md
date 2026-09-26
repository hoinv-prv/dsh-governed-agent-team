# Verification — attempt-gat-threat-003

Plan: approved revision 18, SHA-256 `728c1910d910ad8ffc94e38352c437513e987d69e95f77449dbc4cce82cc0b88`. Cumulative charge: 24.

## ASC

The exact allowed STEP-06 transition was run after the revision-18 AIP edit. The first build reported stale; the exact command was repeated and the reread ASC reported AIP-EXEC-004 / STEP-06 / active / `staleness_status: fresh` before candidate edits.

## Bounded byte changes

Only `docs/conformance/gat-conservative-mvp-v1.json` changed, limited to the four approved vector objects:

1. `GAT-INJECTION-001`: `reason_code` changed from invented `ALLOW_EXPLICIT` to null.
2. `GAT-EXPIRY-001`: pins a derived active/searchable → expired/non-returnable eligibility transition, keeps persisted status active, forbids an invented expired persisted enum, and binds clock/eligibility/audit timestamp evidence.
3. `GAT-CLASS-001`: pins credential/prohibited deny + `ACTION_NOT_ALLOWED` and redactable allow + null reason, with redacted-only persistence and zero raw/unredacted bytes.
4. `GAT-DEGRADE-001`: pins optional-memory explicit degradation + `CAPABILITY_UNSUPPORTED` separately from required-security-service deny + `SECURITY_SERVICE_UNAVAILABLE`, with no silent provider substitution.

The threat-model file was not edited.

## Exact command results

`sha256sum docs/security/GAT_CONSERVATIVE_MVP_THREAT_MODEL.md docs/conformance/gat-conservative-mvp-v1.json` exited 0:

```text
f590ceec949e43a50cc6ea857c919ffbf16736e7757648d3e84c48702cad41da  docs/security/GAT_CONSERVATIVE_MVP_THREAT_MODEL.md
2250aa8bd50e08efd4e4e876e8d9ac4309d3aea8c1af424de04a817aa507b87c  docs/conformance/gat-conservative-mvp-v1.json
```

`node wbs-runs/multi-mission-web-ui/tooling/verify-gat-vector-shape.mjs` exited 0:

```json
{"total":51,"unique":51,"pinned":43,"extensions":8,"allowExplicit":[],"nonNullRequired":[],"failures":[]}
```

Independent Security review and separate HUMAN exact-hash acceptance remain pending. No package write, DSH access, accepted-baseline conformance execution, dependency/network activity, Web change, AIP close, or activation occurred.
