# Independent advisory — WBS revision 14

**Verdict:** REVISE  
**Reviewed plan SHA-256:** `187186a10b622159d9568023fa0a185d6257a3bde4bb6a5fc9c5a7c48878b60e`  
**Authority:** advisory only.

## Material findings

1. The conformance command still passed only `.artifacts/gat-conformance` while proposal §18 pins `--evidence .artifacts/gat-conformance/<implementation-hash>/`; deriving the child inside the runner changed the exact CLI/path contract without a reviewed proposal revision.
2. Ambient `pnpm` provenance remained unpinned. The external pnpm store could not be expressed as a workspace-relative WBS read path, and offline mode alone did not prove the executable/store avoided DSH bytes.

## Confirmed closures

Revision 14 correctly closed exact-hash review identity, content-addressed child-output intent, raw evidence fields, package scaffold/build ordering, plain AIWS close, cumulative limits, stale-work gate, dependency closure, and absence of DSH install/build/Web commands.

## Revision-15 response

Revision 15 narrows the executable objective to standalone dependency-free JavaScript coding, Node tests, package build/smoke, and an implementation freeze. It removes pnpm/TypeScript/Vitest/tsdown and does not claim or run the unresolved proposal-pinned conformance CLI. The exact frozen implementation hash becomes input to a separately reviewed follow-up WBS before conformance; DSH installation remains later still.
