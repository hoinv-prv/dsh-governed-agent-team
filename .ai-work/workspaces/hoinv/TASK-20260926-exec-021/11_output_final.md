# AIP-EXEC-021 Final Output — GAT Baseline Sync and Contract Freeze

## Result

EXEC-A is complete within its approved boundary. The standalone repository now carries the selected current DSH GAT behavior through a controlled merge, the member-binding/lifecycle contract is frozen for EXEC-B/EXEC-C, and the released supported installer target passes end-to-end verification. No binder, two-phase continuation implementation, Durable Agent integration, or authenticated mission-authority implementation was added.

## 1. Synchronized implementation

- Core now supports optional per-member Agent routing, workspace enable provenance, revision-1 authorized mission replay compatibility, and the mission-plan safety guard.
- Tools/profile now provide default simple mode, strict bounded `team_members.yaml`, all-route provider/model/reasoning preflight, Session-keyed installation/recovery, and the approved limits.
- HUMAN-confirmed Team exclusivity remains enforced after enable: external `subagent`, `subagent_fork`, `workflow`, and `ralph` are denied.
- `simpleMode: false` retains exact legacy Team-plan approval; approved-plan import, atomic journal behavior, prepared-state views, and the 11-method Remote surface remain intact.
- Inconsistent DSH Web deletions were not copied. Verification assets now exercise the explicit opt-in enable boundary and synchronized fallback roster.

## 2. Frozen contract readiness

`docs/GAT_MEMBER_BINDING_CONTRACT_FREEZE.md` is the normative handoff for later implementation. It freezes:

- required-only V1 attachment semantics and all numeric bounds;
- RFC 8785 canonical payload measurement plus SHA-256 digest;
- `team/member` v3 with an adjacent v2 adapter;
- GAT-owned prepare/bind/recover/reverse-release and prepared-lease cleanup;
- DSH reserved lifecycle states with persist-only quarantined inbox and sole `activate()` wake gate;
- host-attested HUMAN mission admission and exact `teamId + missionId + missionRevision` execution lease;
- canonical task-board `missionId` authority and no duplicate mutable executable task truth;
- capability-metadata external-delegation denial with compatibility name fallback;
- fake-only EXEC-B orchestration and production EXEC-C lifecycle integration.

Final independent advisor review: **PASS**, with no blocking or major findings.

## 3. Verification evidence

- Core isolated verification: **96 tests**, typecheck, emit, and package build passed.
- Tools isolated verification: **29 tests** passed.
- Installed package suite: **10 files / 150 tests** passed.
- Installer Node suite: **11/11 tests** passed.
- Clean supported DSH target `c291e7961a515f6d7af9304e7fd1d257929aef26`:
  - install: **85 files**, structural verification **PASS**;
  - offline frozen-lockfile dependency install: **PASS**;
  - full verifier: **PASS**;
  - complete DSH host/client/Web build, built-lib Remote E2E, and opt-in Team browser E2E: **PASS**;
  - secret findings: **0**; paths outside allowlist: **0**.
- Final `git diff --check`: **PASS**.

## 4. Current-DSH compatibility gap

The selected behavioral baseline is the dirty working-tree state rooted at DSH commit `aeedf19995babaa28e35ca84624baff18a77a7d8`, pinned by `dsh-baseline-sha256.txt`. That commit is outside the installer's released tested target and its live installation record/preimages do not match this installer. Therefore:

- behavioral synchronization is complete;
- supported-target installer compatibility is proven;
- compatibility for current DSH `aeedf...` remains a separate follow-up requiring a new reviewed compatibility target;
- the live DSH checkout was not modified.

## 5. Handoff artifacts

- Contract: `docs/GAT_MEMBER_BINDING_CONTRACT_FREEZE.md`
- Updated design/source map: `docs/GAT_DESIGN_AND_FEATURE_REFERENCE.md`
- Exact selected DSH evidence: `.ai-work/workspaces/hoinv/TASK-20260926-exec-021/dsh-baseline-sha256.txt`
- Normative synchronized package manifest: `.ai-work/workspaces/hoinv/TASK-20260926-exec-021/post-sync-package-sha256.txt`
- Detailed findings and verification matrix: `.ai-work/workspaces/hoinv/TASK-20260926-exec-021/04_findings.md`
- Capture inbox: seven candidates deferred for later HUMAN curation; none promoted to Wiki/canonical truth.

## Recommended next work

1. EXEC-B: implement GAT core binder orchestration and conformance fixtures against fake lifecycle handles only.
2. EXEC-C: implement DSH reserved continuable lifecycle, quarantined inbox persistence, activation gate, and production binder integration.
3. Separately authorize a compatibility-target update for DSH `aeedf...` (or a later clean current revision) before installing this distribution into that checkout.
