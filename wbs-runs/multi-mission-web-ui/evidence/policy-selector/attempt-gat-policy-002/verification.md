# Policy selector — attempt-gat-policy-002 verification

Exact command `node --test packages/gat/tests/policy-selector.test.mjs`: PASS, 6 tests, 0 failures, exit 0.

Attempt-1 gaps closed:
- authoritative account mapping contains logical/canonical paths, registry id, revision/hash, and collision-free case-fold keys; symlink-resolved outside paths, case collisions, and account/workspace mismatches deny;
- deeply validated snapshot/rules bind execution/readiness/current Team approval/conditional native Mission/account mapping/classification policy/membership/capability;
- unknown scope, arbitrary classification, malformed rule/snapshot, stale hashes, and mutable aliases fail closed without uncaught errors;
- configured timing envelope is mandatory, pads under-minimum responses, and converts over-maximum evaluation to generic denial before selector emission;
- decisions contain decision id, correlation id and timestamp; exact typed selector is SHA-256 content addressed and HMAC authenticated;
- test uses selector sink as the only downstream handoff; denied requests emit zero selectors. Policy code owns no backend/cache/post-filter capability.

Hashes: source `7f58ac2d75bbea5d3aede18a823842d39de42f26a40dbed151113b640e9535ab`; declarations `3ab29993702a4a00f02f67c544fe5eab131e72ad7432c269c5ce24746057d55f`; test `5e7021983f60d77bed2e33d56a9071fd3288c8ff15b9327a2769bb2b20a986fc`.

Node built-ins only; no DSH/network/package-manager/conformance/activation effect.
