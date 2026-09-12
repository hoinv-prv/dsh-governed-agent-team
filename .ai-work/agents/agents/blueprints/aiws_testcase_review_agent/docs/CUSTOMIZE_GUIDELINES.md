# Customize Guidelines — Test Case Review Agent (blueprint)

> Mapped from: Document_Review_Agent_Blueprint/templates/CUSTOMIZE_GUIDELINES.md (template_version v0.1).
> Scope: how to adapt THIS blueprint, and when a separate blueprint vs an instance is the right move.

## 1. Blueprint vs instance
This blueprint covers Test Case documents in general. Project/module/feature variants
(e.g. Order test-case review, Billing test-case review) are NOT separate blueprints — create them as
INSTANCES of `aiws_testcase_review_agent` with project/module-specific context + memory. Make a NEW
blueprint only when the document type itself differs in review purpose, coverage criteria, severity
meaning, checklist, or expected reviewer behavior.

## 2. Review purpose (fixed for this blueprint)
Prevent shipping test cases that leave requirements unverified or coverage thin. After review the
HUMAN can decide: ready / needs more coverage / needs HUMAN decision / not enough information.

## 3. What to customize per instance
- `context/wiki_references.yaml`, `context/source_references.yaml` — the Wiki entries and source dirs
  the instance reads (requirements, design, feature/API/screen specs the cases must trace back to).
- `context/source_priority.yaml`, `context/ignored_paths.yaml` — Wiki-first ordering + what to skip.
- Mission customization (focus features, coverage axes in focus, known regression-prone areas).
- HUMAN output preferences and known false positives (start empty; HUMAN-approved only).

## 4. What NOT to change here (shared, change once upstream)
The review process, severity tier MEANINGS, finding format, source-trace rule, lesson-capture rule,
the common checklist, and the report shape are SHARED under `../../_shared/review/`. A change to
common review behavior is made ONCE there and picked up by every review blueprint. Do not fork them
into this blueprint.

## 5. What IS blueprint-local (safe to evolve here, HUMAN-gated)
- `docs/reference_content/testcase_review_checklist.md` (reference seed) (test-case coverage / alignment / readiness checks)
- `blueprint.yaml` -> `severity_examples`, `finding_categories`, `skills`, mission.

## 6. Severity examples (test-case coverage lens)
Critical: a major requirement has NO coverage at all, or a security/authorization path is untested.
Major: missing abnormal/boundary/status-transition cases, an unverifiable expected result, or a
regression-prone hot path left unprotected. Minor: incomplete precondition/test-data wording or hard-
to-read grouping while the coverage still exists. Suggestion: case naming, grouping, or trace-format
readability.

## 7. Finding quality (enforced)
Every finding: ID, severity, type, category, location, finding, evidence/reference, impact, suggested
action, HUMAN decision. State each coverage gap with the SPECIFIC requirement/axis it misses. Avoid
generic findings, missing location, missing impact, or mixing open questions with confirmed gaps.
Report conflicts (requirement vs Wiki vs cases); never resolve them silently (Wiki-first NOT
Wiki-only). Judge coverage against the requirement/design + Wiki, not against the cases that already
exist.

## 8. Learning capture (no auto-promotion)
After each run ask "what could improve future test-case reviews?" Route candidates to instance
memory / checklist update / wiki candidate / blueprint improvement per
`../../_shared/common/lesson_capture_rule.md`. All candidates `status: candidate`; promotion is
HUMAN-gated. Never auto-confirm.

## 9. Definition of done (this blueprint)
Has: target document type, mission, responsibilities/non-responsibilities, input/output contract,
review process (shared ref), test-case-specific checklist, severity definition (shared + examples),
finding format (shared ref), Wiki/source usage policy (shared ref), memory policy, learning candidate
policy, HUMAN gate policy.
