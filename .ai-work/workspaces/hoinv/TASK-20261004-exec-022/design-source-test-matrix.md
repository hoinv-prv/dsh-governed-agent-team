# Intended design → source → verification

All changes below follow the 2026-10-04 HUMAN selection in approved-decisions.md. Formal intended delta was added before source to Detail Design §5, Architecture §9, Basic Design §10 and Durable integration approved WK baseline.

| Requirement | Prior design | Source ownership | Evidence / dependency |
|---|---|---|---|
| Normalized initializer + full preflight | DD §5 DD01/16; freeze §4 | root core index; Luna tools default initializer | core/team and tools regressions; malformed roster tests |
| Bounded digest, member v3 and strict v2 | DD §5 DD03/16; freeze §5 | root attachments/types/projection/roster | Luna member-attachments; projection replay tests |
| Registry/ownership/prepare-all | DD §5 DD02/16; freeze §6 | root member-binders/deadline | attachment suite + lifecycle barriers |
| Reserved lifecycle and recovery | DD §5 DD07/08/16; freeze §§7–9 | root member-binding, strict legacy wake refusal | deterministic ports; actual DSH reserved API qualification held |
| WK payload / strict declaration | DD §5 DD09/15/16; proposal §§4–5 | Luna initializer; root binder/ownership | real temporary public provider + strict YAML tests |
| Scoped executable tools / refresh | DD §5 WK adapter; proposal §6 | Luna tools; root binder | effect/read pre/post checks; host request hook still required |
| Mission/executor production admission | DD §5 DD17; freeze §§10–11 | external owning workstreams | exact authenticated lease + canonical task + nested capability union required |
| Packaging/profile and source/build | DD §5 DD10/11; proposal §9 | root opt-in adapter export/build and installer qualification | no production activation before qualified host |

Direct-continuable target: T17–T21 and isolated-only parts of T16/T22/T23 are not applicable. Strict denial and static Team presentation remain applicable. No official isolated Consumer or host-created hook substitutes for reserved-child admission.

## Final production corroboration

The intended deltas above are retained as chronology. Official DD sections7–8, AD/BD/integration production sections and their prospective corrective refinements govern the delivered connected implementation. Current source/test/fixture hashes and138 mapped files,184 symbols and80 test locators are in docs/gat-design/source-code-map.json and source-baseline.json, validated by verification/production-mapping-validation.json. Actual executed source, built/profile/SDK/browser and artifact evidence is in verification/production-qualification-receipt.json and acceptance-matrix.md, with independent review separately recorded. Macro criteria are declarative; runtime acceptance is not encoded by ticking them.
