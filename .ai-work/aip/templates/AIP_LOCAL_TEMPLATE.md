---
artifact_type: aip_local
artifact_id: AIP-LOCAL-001
title: "`<title>`"
status: draft
# status: (auto) — `aiws-aip run start` flips draft → active (CR-AIWS-2026-07-040); close sets done by hand (draft|active → done).
project: "`<project-name>`"
owner: "`<optional>`"
updated_at: YYYY-MM-DD
---

# AIP_LOCAL — `<title>`

## Objective
- ...

## Selected Task Lens / Mode
<!-- OPTIONAL (CR-AIWS-2026-05-030 / -032; Task_Lens_Spec_MVP). An ADDITIVE, non-exhaustive HINT for which source_types/
reference_types to reference + reading order; consult presets in `.ai-work/wiki/task_lens_presets/`. aiws-aip create front-
loads (Resolved references); aiws-aip run resolves only Deferred lookups. No-Lens is valid — leave empty or set No-Lens with
a reason. -->
- Lens: `<preset lens_id, a custom/runtime lens, or No-Lens>`
- Reason: `<why this lens (or why No-Lens)>`
- Search/execution effect: `<source_types/reference_types it prioritises>`
- Resolved references: `<subject + reference standards already filled at create time — AI inference ∪ lens>`
- Deferred lookups: `<doc still to find + which lens — aiws-aip run resolves; empty if all resolved>`
- Expansion allowed: `<yes/no>`
> Note: the lens is an **ADDITIVE** hint (also-consider), not the input spec — AI inference is **primary**; inputs = inference ∪ lens (`Task_Lens_Spec_MVP` §F).

## Notes
- ...

## Personal Constraints / Reminders
- ...

## Local Execution Notes
- ...

## Rule
AIP_LOCAL là tùy chọn. Không dùng thay cho AIP shared/official trong workflow chính.
