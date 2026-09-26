# Independent advisory — WBS revision 13

**Verdict:** REVISE  
**Reviewed plan SHA-256:** `96aabf505c4334f0554204adf40bdd8093a0743de00839cde5a22bbea0a8539f`  
**Authority:** advisory only; no approval or execution authority.

## Material findings

1. The reviewer initially observed a stale review hash during concurrent correction. The HUMAN approval later bound the actual `96aabf...` plan bytes, but all later edits require a new revision.
2. Conformance output drifted from proposal `.artifacts/gat-conformance/<implementation-hash>/` and omitted required vector/DSH/MCP/command/exit/timestamp/raw-output bindings.
3. Workspace-local Vitest/TypeScript/tsdown executables were absent; ambient resolution came from the DSH checkout and therefore was neither declared nor valid standalone evidence.
4. `package-surface` was accepted before later `security-conformance` mutated its conformance surface/package manifest, invalidating same-byte package review.
5. `run_aip.py close --defer-all` could write `.ai-work/capture_backlog/hoinv.jsonl` outside declared scope.

## Confirmed closures

- Threat/vector HUMAN gate was transitively before coding.
- Cumulative limits correctly included 17 historical charges plus revision-13 allocation.
- Stale `attempt-core-007` settlement was a hard first gate.
- Fixed Workspace runtime evidence and no declared DSH installation/write effects were present.

Revision 14 was created to resolve all material findings; no revision-13 task was dispatched.
