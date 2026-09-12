# aiws-wiki — operation: build-pattern

> Operation of the `aiws-wiki` domain skill (consolidated by CR-AIWS-2026-07-025; former standalone skill — see `product/rename_map.json`). Content preserved verbatim; every gate herein stays binding.


## Purpose

Record a confirmed, reusable format mapping pattern so future artifact builds of the same
format can reuse it instead of re-inferring. A Project Mapping Pattern (PMP) is an
**active template** — applied at build time to derive canonical slots, not stored as memory.

## Schema reference

`product/wiki_guidelines/core/guidelines/WIKI_PROFILE_GENERATION_CUSTOMIZATION_GUIDELINE.md §19`

## Inputs
- Confirmed artifact_type (from `Artifact_Type_Taxonomy_Spec_MVP` enum)
- N sample artifact metas (built via `/aiws-wiki build-meta`) showing the stable pattern
- Human-confirmed `format_signature` (textual pattern list that identifies this format)
- `canonical_slots_used` (the slots actually found in this format)
- `common_source_to_slot_mapping` (section/heading → slot mappings)

## Output

Saved alongside the profile as `pmp_<profile_id>.yml` (CR-AIWS-2026-06-021 — the path the tool reads):
```
.ai-work/wiki_sources/profiles/pmp_<profile_id>.yml
```

## YAML Schema

```yaml
mapping_pattern_id: PMP-<PROJECT>-<FORMAT>-<VERSION>
artifact_type: <artifact_type enum>
project_format_label: <human-readable label, e.g. dd_split_fe_api_be_v1>
format_signature:
  - "<textual signature 1>"   # pattern that identifies this format
  - "<textual signature 2>"
canonical_slots_used:
  - <slot_name>
common_source_to_slot_mapping:
  - source_pattern: "<section/heading pattern>"
    canonical_slots:
      - <slot_name>
project_customized_meta_fields:
  - field: <field_name>
    description: <description>
    example: <example_value>
reuse_confidence: high | medium | low
exceptions:
  - "<exception note>"
created_at: <YYYY-MM-DD>
confirmed_by: <human_id>
last_validated: <YYYY-MM-DD>
```

## Flow

1. Collect N sample metas from same format (already built via `/aiws-wiki build-meta`)
2. AI analyze metas — extract common: format_signature, canonical_slots_used, source_to_slot_mapping
3. Propose PMP YAML to user
4. User confirms/corrects:
   - format_signature correct?
   - canonical_slots_used complete?
   - source_to_slot_mapping correct?
   - reuse_confidence assessment?
5. Set `confirmed_by: <user>`, `created_at: <today>`, `reuse_confidence: high|medium|low`
6. Save PMP file
7. Report: "PMP saved as `pmp_<profile_id>.yml`. Auto-loaded by `/aiws-wiki build-meta` for matching format." (the tool reads it via `_load_pmp`; there is no `--mode mass` — modes are `create|refresh`.)

## Rules

- PMP must be human-confirmed before save (reuse_confidence = high/medium requires explicit confirm)
- `format_signature` must be generic enough for project reuse (not hardcode single artifact ID)
- `mapping_pattern_id` follows convention: `PMP-<PROJECT_PREFIX>-<FORMAT_LABEL>-<VERSION>`
- Prefer ≥2 samples showing a consistent pattern; a single-sample draft is allowed at `reuse_confidence: low` per guideline §19.4a (do not hard-block a single-sample draft)
