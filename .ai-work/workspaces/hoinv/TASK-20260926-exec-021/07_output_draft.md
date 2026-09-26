# EXEC-A Output Draft — Baseline Sync and Contract Freeze

## 1. Frozen source direction
- DSH experimental GAT working tree is the behavioral baseline for current simple-mode enablement, workspace roster loading, route preflight, optional Agent route, and immediate revision-1 authorization.
- Standalone GAT is now the controlled authoring/distribution source for the synchronized behavior.
- The selected DSH baseline is not identified by commit alone because relevant files are dirty/untracked; commit `aeedf19995babaa28e35ca84624baff18a77a7d8` and exact selected file hashes are recorded in `dsh-baseline-sha256.txt`.

## 2. HUMAN-resolved merge policy
- Preserve Team-exclusive delegation after Team enablement: external `subagent`, `subagent_fork`, `workflow`, and `ralph` remain denied.
- Adopt simpleMode's approval shortcut for the current default profile, while explicitly refusing to treat it as authenticated HUMAN mission provenance.
- Retain legacy `simpleMode: false` Team-plan approval and standalone approved-plan import APIs.
- Preserve standalone atomic journal/import behavior and the exact 11-method Remote surface.

## 3. Controlled synchronization completed
- Core: `AgentOptions`, workspace enable source, immediate-authorized revision 1 plus legacy replay compatibility, mission-plan guard, and merged tests.
- Tools/profile: strict bounded YAML loader, all-route preflight, simple mode, Session-keyed installation/recovery, profile defaults/tests, and Team-exclusive policy.
- Web: standalone's internally consistent mission/import injections retained; incompatible DSH Web deletions were not copied.
- Compatibility distribution: generated payload now includes 76 source files and 85 installed files; generator emits the new tools lockfile dependencies without converting local profile links into stale package snapshots.
- Generated package libs, caches, and unrelated DSH working-tree content were not synchronized.

## 4. Frozen member-binding contract
- Normative contract: `docs/GAT_MEMBER_BINDING_CONTRACT_FREEZE.md`.
- V1 attachments are required-only with fixed binder/payload limits, RFC 8785 canonical byte semantics, and SHA-256 payload digest.
- `team/member` advances to v3 with an explicit adjacent v2 adapter.
- GAT owns prepared leases and reverse release; DSH reserves the continuable state machine and exposes persist-only inbox plus sole `activate()` wake gate.
- Effectful/wake execution requires a GAT-issued lease bound to a host-attested HUMAN mission and exactly one current `teamId + missionId + missionRevision`.
- Canonical task-board rows carry `missionId`; no mutable duplicate executable task truth is allowed.
- External-delegation denial uses capability metadata with compatibility name fallback.
- EXEC-B is fake-only orchestration; production DSH continuation integration remains EXEC-C.
- Final independent advisor review: PASS, no blocking or major findings.

## 5. Verification position
- Core isolated verification: 96 tests plus typecheck/emit/package build PASS.
- Tools isolated verification: 29 tests PASS.
- Clean supported DSH clone (`c291e796...`): installer PASS, 85 files, structural verification PASS, offline frozen-lockfile install PASS.
- Full installed package suite: 10 files / 150 tests PASS.
- Installer Node suite: 11/11 PASS.
- Full installer verifier PASS: native/unit verification, complete DSH build, built-lib Remote E2E, opt-in Team browser E2E, structural status, zero secret findings, and no paths outside the allowlist.
- The selected current DSH commit `aeedf...` remains outside the supported installer compatibility target. Its live dirty checkout was not modified; adding a tested compatibility manifest for that revision is separate follow-up work.

## 6. Capture disposition
- Seven reusable findings remain in `08_capture_inbox.jsonl` as HUMAN-review candidates only; none was silently promoted to Wiki/canonical truth.
