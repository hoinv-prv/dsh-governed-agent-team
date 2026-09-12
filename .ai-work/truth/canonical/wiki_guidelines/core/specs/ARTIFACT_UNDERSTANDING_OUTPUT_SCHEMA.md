# ARTIFACT_UNDERSTANDING_OUTPUT_SCHEMA_v0_1

## 1. Purpose
This schema defines the minimal structure for artifact understanding outputs in the Wiki sprint.

## 2. Base schema

```yaml
artifact_understanding_id: AU-<id>
artifact_ref: <artifact ref or file ref>
artifact_type_candidate: <raw_requirement_list | qa_list | requirement_definition | basic_design | detail_design | it_testcase | meeting_minutes | weekly_report | supplemental_other>
artifact_family: <requirement_side | main_project_artifact | supplemental_artifact>

artifact_identity:
  title_or_name: <string>
  source_location: <string or ref>
  version_or_revision: <optional>
  language_notes: <optional>

artifact_role_understanding:
  role_summary: <string>
  likely_phase_position: <string>
  likely_upstream_artifacts:
    - <ref>
  likely_downstream_artifacts:
    - <ref>

structure_template_understanding:
  template_shape_summary: <string>
  major_sections:
    - section_name: <string>
      section_purpose: <string>
  section_mapping_notes:
    - <string>

key_objects_and_terms:
  objects:
    - object_name: <string>
      object_type: <function | screen | batch | api | table | field | rule | other>
      notes: <string>
  alias_candidates:
    - canonical_candidate: <string>
      alias: <string>
      confidence_note: <string>

related_artifacts_and_links:
  explicit_refs:
    - <artifact ref>
  inferred_related_refs:
    - <artifact ref>
  traceability_hints:
    - <string>

confirmed_from_artifact:
  - item: <string>
    evidence_note: <string>

ai_inference:
  - item: <string>
    inference_basis: <string>

unresolved_or_needs_confirmation:
  - item: <string>
    why_unresolved: <string>

suggested_followup_actions:
  - <string>
```

## 3. Requirement-side extension

### 3.1. Use for
- raw requirement list
- Q&A list
- requirement definition document

### 3.2. Additional fields
```yaml
requirement_chain_position:
  layer_type: <raw_requirement | qa_clarification | refined_requirement_definition>
  relationship_to_other_requirement_layers:
    upstream_refs:
      - <ref>
    downstream_refs:
      - <ref>

requirement_refinement_notes:
  apparent_refinement_state: <string>
  possible_refinement_gaps:
    - <string>
```

### 3.3. Rule
These three layers should not be collapsed too early into one generic requirement object.
```

## 4. Supplemental artifact extension

### 4.1. Use for
- Q&A
- findings
- open points
- clarification notes
- review comments summary
- pending decisions
- similar supplemental artifacts

### 4.2. Additional fields
```yaml
supplemental_status_understanding:
  current_status: <open | answered_unapplied | resolved_unapplied | partially_reflected | reflected | superseded | dropped | unknown>
  status_basis_note: <string>

reflection_status_understanding:
  reflection_status: <not_reflected | partially_reflected | reflected | unknown>
  reflected_to:
    - <artifact ref>
  reflected_at: <optional date/time/version note>
  superseded_by:
    - <artifact ref or item ref>
  reflection_note: <string>

future_usage_note:
  direct_consultation_still_needed_by_default: <yes | no | maybe>
  reason: <string>
```

### 4.3. Rule
If a supplemental artifact appears to have already been reflected into a main artifact, this should be surfaced explicitly.
```

## 5. Minimal review/revise fields
```yaml
review_state:
  reviewed_by_brse: <yes | no | partial>
  review_note: <string>
  revision_round: <integer>
```

## 6. Notes
- This schema is intentionally minimal for this sprint.
- Fields may be extended later in BL-02, BL-03, BL-04, and BL-05.
- The understanding output should remain grounded and reviewable.
