# aiws-wiki — operation: refresh-pattern

> Operation of the `aiws-wiki` domain skill (consolidated by CR-AIWS-2026-07-025; former standalone skill — see `product/rename_map.json`). Content preserved verbatim; every gate herein stays binding.


## Purpose

Update an existing PMP when:
- Upstream artifact format has drifted from what PMP was built for
- New canonical slots are needed that PMP doesn't cover
- `reuse_confidence` should be downgraded due to observed failures

## Inputs
- Existing PMP file: `.ai-work/wiki_sources/profiles/pmp_<profile_id>.yml`  (CR-AIWS-2026-06-021 — the path the tool reads; NOT `mapping_patterns/PMP-<id>.yml`)
- Evidence of drift: new artifact samples that didn't map correctly with current PMP
- (Optional) Updated canonical slots from `/aiws-wiki build-meta` failure log

## Flow

1. Read existing PMP
2. Identify drift signals:
   - Sections in new artifacts not matching `format_signature`
   - New sections that should map to canonical slots but don't
   - `common_source_to_slot_mapping` entries that failed on recent artifacts
3. Propose updated PMP fields:
   - Updated `format_signature` (added/removed patterns)
   - Updated `canonical_slots_used`
   - Updated `common_source_to_slot_mapping`
   - New `project_customized_meta_fields` if needed
   - Downgraded `reuse_confidence` if major drift
   - Updated `exceptions` list
4. Show diff to user (old vs new PMP fields)
5. User confirms
6. Save updated PMP, bump `last_validated: <today>`
7. Report: "PMP refreshed. Next build with this format will use updated mapping."

## Drift severity classification

| Drift type | Impact | Suggested action |
|---|---|---|
| Minor (1-2 field changes) | Cosmetic | Update + keep confidence |
| Moderate (new section, slot added) | Medium | Update + confirm new slots |
| Major (format restructured) | High | Downgrade confidence + Sample-First on next batch |
| Breaking (format fundamentally different) | Breaking | Create new PMP, retire old |

## Rules

- `last_validated` must be updated on every refresh
- If `reuse_confidence: low` → suggest Sample-First mode before next mass build
- If breaking drift → do NOT patch existing PMP; create new PMP with new `mapping_pattern_id`
- Retired PMPs: add `deprecated: true` + `superseded_by: PMP-<new-id>`, do NOT delete
