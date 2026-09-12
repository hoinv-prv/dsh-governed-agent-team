# Customize Guidelines — Detailed Design Review Agent (blueprint)

> Mapped from: Document_Review_Agent_Blueprint/templates/CUSTOMIZE_GUIDELINES.md (template_version v0.1).
> Scope: how to adapt THIS blueprint, and when a separate blueprint vs an instance is the right move.

## 1. Blueprint vs instance
This blueprint covers Detailed Design documents in general. Module/domain variants
(e.g. Order DD review, Billing DD review) are NOT separate blueprints — create them as INSTANCES of
`aiws_detailed_design_review_agent` with project/module-specific context + memory. Make a NEW blueprint
only when the document type itself differs in review purpose, quality criteria, severity meaning,
checklist, or expected reviewer behavior.

## 2. Review purpose (fixed for this blueprint)
Prevent implementation handoff based on incomplete or inconsistent detailed design. After review the
HUMAN can decide: ready / needs fix / needs HUMAN decision / not enough information.

## 3. What to customize per instance
- `context/wiki_references.yaml`, `context/source_references.yaml` — the Wiki entries and source dirs
  the instance reads (requirements, basic design, API/DB/screen specs).
- `context/source_priority.yaml`, `context/ignored_paths.yaml` — Wiki-first ordering + what to skip.
- Mission customization (focus modules, known weak areas).
- HUMAN output preferences and known false positives (start empty; HUMAN-approved only).

## 4. What NOT to change here (shared, change once upstream)
The review process, severity tier MEANINGS, finding format, source-trace rule, lesson-capture rule,
the common checklist, and the report shape are SHARED under `../../_shared/review/`. A change to
common review behavior is made ONCE there and picked up by every review blueprint. Do not fork them
into this blueprint.

## 5. What IS blueprint-local (safe to evolve here, HUMAN-gated)
- `docs/reference_content/detailed_design_review_checklist.md` (reference seed) (document-specific checks)
- `blueprint.yaml` -> `severity_examples`, `finding_categories`, `document_specific` skills, mission.

## 6. Severity examples (detailed design)
Critical: missing/wrong business rule -> wrong data update, permission/security bug, requirement
failure. Major: missing validation/status/error handling -> implementation rework or test failure.
Minor: unclear wording, limited risk. Suggestion: readability/table/naming/links.

## 7. Finding quality (enforced)
Every finding: ID, severity, type, category, location, finding, evidence/reference, impact, suggested
action, HUMAN decision. Avoid generic findings, missing location, missing impact, or mixing open
questions with confirmed defects. Report conflicts; never resolve them silently (Wiki-first NOT
Wiki-only).

## 8. Learning capture (no auto-promotion)
After each run ask "what could improve future detailed-design reviews?" Route candidates to instance
memory / checklist update / wiki candidate / blueprint improvement per
`../../_shared/common/lesson_capture_rule.md`. All candidates `status: candidate`; promotion is
HUMAN-gated. Never auto-confirm.

## 9. Definition of done (this blueprint)
Has: target document type, mission, responsibilities/non-responsibilities, input/output contract,
review process (shared ref), document-specific checklist, severity definition (shared + examples),
finding format (shared ref), Wiki/source usage policy (shared ref), memory policy, learning candidate
policy, HUMAN gate policy.
