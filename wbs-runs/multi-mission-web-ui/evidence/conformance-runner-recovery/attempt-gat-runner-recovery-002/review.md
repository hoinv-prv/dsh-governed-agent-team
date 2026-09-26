# Independent conformance-runner review — WBS v28 attempt 58

Verdict: CHANGES REQUIRED. Reviewer: `team-message-a09810c0-6d99-4e01-8428-805847dda2bd`.

Passing source semantics: nonempty/count/hash-pinned vectors; runner-owned core hashes and exact command; deep expected/actual and counter-absence checks; structured required-evidence entries; runtime entry bytes hashed before import; accepted baseline unexecuted.

Material gaps:

1. `types/conformance/index.d.ts` does not declare required handler evidence, typed expected bindings/I/O/dispatch, runtime loader result/config or CLI `main` seam.
2. Only runtime entry bytes are hashed; mutable transitive imports are not bound. Runtime literal/canonical path is discarded from CLI/raw evidence.
3. Environment hash and outer command are asserted via ambient variables rather than bound to a pinned execution packet.
4. CLI test injects the loader rather than exercising real loader→main→raw-evidence end to end; absent runtime reason is masked by config validation.

Exact synthetic suite recorded 4/4 PASS but is insufficient for acceptance. No DSH, network, package-manager or accepted-baseline execution occurred.
