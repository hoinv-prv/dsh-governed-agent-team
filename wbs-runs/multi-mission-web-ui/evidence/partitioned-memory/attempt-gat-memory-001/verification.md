# Partitioned memory verification — attempt-gat-memory-001

WBS v19; charge 31; fresh STEP-08 ASC.

Exact commands:

- `node --test packages/gat/tests/memory.test.mjs`: exit 0; 2/2 pass.
- `node --test packages/gat/tests/audit-recovery.test.mjs`: exit 0; 2/2 pass.
- `node --test packages/gat/tests/lifecycle-privacy.test.mjs`: exit 0; 2/2 pass.

Coverage claims submitted for independent review: physical tenant/ProjectScope/Desk/classification partitions; immutable versions/provenance; deterministic literal substring retrieval; idempotent exact replay and conflict; hash-chained audit, anchor-failure no internal commit, backup/restart/corruption rejection; expiry, legal hold, purge, deep-owned backup and restore isolation.

Hashes: source `c99d9f1b309104dfe2e93ddc7fbb7e24324b1c4dd08f4e00ec6def16d782e22b`; declaration `aa10bc16d100a5090ebf363a78da5efe3e576fcb27590d715abcb325aa4f2eaf`; memory test `e834446cd56fccbd67273684e55fa910f29bcb459a7d6e8e6b32d474a835a6cd`; audit test `e67733772d48fe549c8cca912abff79aa74b812a1cc437d39671b9a0cda48d9a`; lifecycle test `52e0cc1e054a54d0ff53b1a75917008ff4683b0bf0853c01c2996dd54716331f`.

No DSH/dependency/network/accepted-conformance/activation effect.
