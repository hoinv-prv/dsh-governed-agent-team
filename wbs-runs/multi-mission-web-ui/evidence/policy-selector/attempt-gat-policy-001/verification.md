# Policy selector — attempt-gat-policy-001 verification

Exact command `node --test packages/gat/tests/policy-selector.test.mjs` exited 0: 5 tests passed, 0 failed.

Coverage: default deny; explicit deny precedence; immutable content-addressed fresh snapshot every call; stale evidence and revocation; full account/workspace/scope containment; exact one-selector allow path; generic fixed denial response; bounded-response callback parity; internal audited reasons; no result counts/ranking/traces; zero selector/backend work on denied paths; frozen selector/decision; no cache or post-filter.

Hashes:
- governance input: `86ba33128b2b221d1f924a04024fa6239ee99cef605808603f9707bf8785c864`
- policy source: `82043d2c931b38c59afb6c680be5ee8fb8bdbb58eff91a58f53180d16dbf2513`
- declarations: `ec0c4e9d54723c2fc4b193c4054c1ed4397a8c0f37df988d52842d9cd36e666e`
- test: `5dd7a596269fa491639e75ca73ed2905c669c56df57057db37411f4f11dd0db8`

Node built-ins only. No network/package-manager/DSH/conformance/activation effect.
