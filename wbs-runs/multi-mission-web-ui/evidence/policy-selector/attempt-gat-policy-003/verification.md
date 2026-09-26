# Policy selector — attempt-gat-policy-003

Exact command `node --test packages/gat/tests/policy-selector.test.mjs`: PASS, 6/6, exit 0.

Final corrections: signed selector binds exact one requested/matched classification, resource id, action, correlation id, decision id and issued time; logical requested paths must be normalized and contained under logical Workspace root in addition to authoritative canonical resolved-path/case/account checks; deficient padding, evaluation overrun and slow audit callback deny before selector emission; selector callback overrun cannot return public allow. All prior deep snapshot, Team/Mission/account/classification, HMAC, generic denial, revocation, no-cache/no-backend/no-post-filter behavior remains.

Hashes: source `038782af3fc8671f8e8e3ede1a8fddecb898840288ac1cb2e7d1c2bf65d871fb`; declarations `3ab29993702a4a00f02f67c544fe5eab131e72ad7432c269c5ce24746057d55f`; test `72ff6e66f201c361e17bd2a00ae49543690b80d8e31ec193aeb493d56ec88ed8`.
