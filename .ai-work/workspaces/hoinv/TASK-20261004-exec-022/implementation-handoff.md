# Implementation handoff — AIP-EXEC-022 (active)

Foundation and separate WK adapter implemented under HUMAN-approved P01–08/direct-continuable selection. Intended design was added before source; Current sections now distinguish delivered foundation from gated production integration.

Source evidence: 235 passing source tests, independent substantive review, public WK provider in temporary storage. Host/client typechecks and bundles, Web build, actual core/adapter built-export smoke, 11 installer CLI tests and default install/status/rollback passed in disposable compatibility checkout c291e7961a515f6d7af9304e7fd1d257929aef26. Browser replay: 2 passed / 1 failed, model golden mismatch against unchanged defaults. See verification/README.md and acceptance-matrix.md. Strict task lint is clean (0 errors / 0 warnings). Whole-tree strict lint has 0 errors / 37 existing warnings and exits 1. No live activation is authorized or claimed.

## Required owner work before production wiring

1. DSH owner: qualify a revision exposing reserved child materialize / persist-only initial item / activation / cold recovery gate with exact generation ownership, and a request hook that refreshes/replaces prompt before rendering and dispatch. Existing startContinuable and agent/request do not meet these contracts (dependency-qualification.md).
2. Mission/executor owner: supply approved exact authenticated HUMAN team/mission/revision leases and canonical task association, plus immutable nested tool capability enforcement at every dispatch boundary. Existing simpleMode and tool-name guards do not qualify.
3. Deployment owner: pin the selected DSH + WK package build and trusted serviceBindingKey, attest dedicated provider / single-host workspace exclusivity, then qualify opt-in profile and actual registered child lifecycle.

These require separately approved external source work or owner-supplied evidence. Current core rejects required attachments before member rows and excludes attached records from legacy wakes/readiness. The new adapter is excluded from the default profile/installer; no compatibility bypass, downgrade attachment stripping, isolated migration or official Consumer substitution is performed.

STEP04/STEP07 gate status OPEN; browser verification mismatch RQ-022-03 also remains open; full AIP remains active. The current ASC is STEP07 with all blocker references. Per-step generated contexts are archived in step_contexts/ and actual states in step-status.md. STEP08 review/handoff is provisional until the production prerequisites and all applicable full-delivery checks pass.

## Authorized prerequisite workstream

On 2026-10-04 HUMAN explicitly authorized the previously requested external prerequisite scope. AIP-EXEC-023 now owns approved host worktree /home/hoinv/work/dsh-binding-prerequisites from c291e7961a515f6d7af9304e7fd1d257929aef26 plus GAT authority/capability bridges. Parent consumes exact qualified evidence only after prerequisite verification; current open dependency gates do not become PASS from authorization alone. Deployment remains separate.

## Qualified prerequisite receipt — AIP-EXEC-023

The prerequisite source/artifact workstream now has independent PASS. This supersedes the missing-API/authority/capability observations above for the exact qualified patch; it does not qualify the parent production adapter/profile or supported release. Read ../TASK-20261004-exec-023/prerequisite-handoff.md, qualification-receipt.json and source-design-consistency.md before parent source changes.

Host worktree: /home/hoinv/work/dsh-binding-prerequisites, branch gat-binding-prerequisites, approved baseline c291e7961a515f6d7af9304e7fd1d257929aef26. Reviewable 244-path source patch: ../TASK-20261004-exec-023/verification/DSH-prerequisites.patch, SHA-256 d532cc1e8d110c9db891219c89f20b4fd94d0836aa1e8c7d6d3494dddfb8cbf0. The changed bytes are uncommitted and require an exact changed-host compatibility receipt; unchanged baseline HEAD alone is insufficient.

Reserved materialize/persist/activate/recover APIs, awaited pre-render hook, exact authenticated mission/task authority and immutable nested executor classification are qualified. Final integration has 270 passing tests independently repeated, 60 actual authorization cases, supported builds/public imports, SDK histories and 34 documentation gates. Design-before-code chronology limitations and dirty-work audit limits remain disclosed in the prerequisite handoff.

Parent next: design and implement production binder composition against these exact APIs, then qualify generation/attachment recovery, selected profile/packaging/browser behavior and changed-host compatibility. Existing parent browser finding remains open; parent AIP remains active. Deployment approval stays separate. Do not reinstall over the isolated host source changes or automatically edit Truth/wiki/freeze/compatibility controls from this receipt.

## Local commit handoff — 2026-10-04

The isolated DSH prerequisite work is committed locally as `5c02ce9f3e44dfce3f87498f65cf684194ad4572`, with parent `c291e7961a515f6d7af9304e7fd1d257929aef26`. `../TASK-20261004-exec-023/commit-receipt.json` binds all 244 committed paths to the checked bytes and preserves the earlier patch receipt as history. Eleven commit-check corrections match the preceding normalized emitted JavaScript exactly; 18 GAT files / 271 tests and 22 Connection/Gateway files / 451 tests pass. Documentation checks pass 34/34; client types and public built imports pass; seven SDK runtime hashes remain unchanged; 57 root/host source pairs match. Source maps and current hashes were refreshed.

Required staged lint passes with 21 warnings and enabled commit hooks. Supplemental type-aware lint remains RED with 172 diagnostics traced to pre-correction lines. This is not a full lint qualification; parent RQ-022-05 requires disposition. Parent production composition, changed-host release/profile/package qualification and browser mismatch remain open. No deployment or external publication was performed. Earlier uncommitted-patch instructions and results above describe their historical inspection.
