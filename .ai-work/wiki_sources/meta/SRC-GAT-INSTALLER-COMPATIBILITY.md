---
artifact_type: wiki_source_meta
source_id: SRC-GAT-INSTALLER-COMPATIBILITY
title: GAT Installer Version and Compatibility Refactor Specification
source_type: gat_design_document
artifact_locator: docs/GAT_INSTALLER_VERSION_COMPATIBILITY_REFACTOR_SPEC.md
profile_id: gat_design_document
status: active
updated_at: 2026-09-13T07:56:15.623881+00:00
authority_level: unknown
freshness_status: unknown
promotion_status: draft
source_representation_status: unknown
source_representation_caution: Representation quality has not been reviewed.
source_representation_quality_issue: false
maintenance_status: needs_review
representation_scope: unknown
knowledge_value: unknown
intended_ai_use: unknown
representation_type: markdown
conversion_method: unknown
conversion_limitations: []
---
# Wiki Source Meta — GAT Installer Version and Compatibility Refactor Specification

## Summary
Reviewed GAT installer refactor specification that separates advisory source drift from explicit GAT-to-DSH compatibility and strict post-install verification, allowing development-tree installs without authorizing unsafe target changes.

## Knowledge Targets
- implementation_guidance
- architecture
- governance

## Lookup Keys
- GAT Installer Version & Compatibility Refactor Specification
- Version & Compatibility Refactor Specification Background
- Version & Compatibility Refactor Specification Review corrections and binding safety constraints
- Version & Compatibility Refactor Specification schema_version
- Version & Compatibility Refactor Specification name
- DSH version
- post-install verification
- GAT
- installer
- compatibility
- dsh
- source
- target
- install
- unverified
- installation
- verification
- commit
- allow
- dirty
- profile
- mjs
- failure
- manifest
- should
- test
- run
- hash
- bash
- existing
- hashes
- payload
- web
- node
- behavior
- hoinv
- post
- current
- packages
- release

## Source-Specific Hints
- heading: GAT Installer Version & Compatibility Refactor Specification
- heading: 1. Background
- heading: 2. Goals
- heading: 2.1 Review corrections and binding safety constraints
- heading: 3. Non-goals
- heading: 4. Design Principles
- heading: 5. New File: `GAT_VERSION.json`
- heading: 6. `GAT_VERSION.json` Field Semantics
- heading: 6.1 `schema_version`
- heading: 6.2 `name`
- heading: 6.3 `version`
- heading: 6.4 `release_date`
- heading: 6.5 `source.repository`
- heading: 6.6 `source.commit`
- heading: 7. Compatibility Policy
- heading: 8. Recommended Compatibility States
- heading: 9. Add Explicit Override for Unverified DSH
- heading: 10. Remove Source Hashes from the Install Authorization Path
- heading: 11. Development Working Tree Behavior
- heading: 11.1 Dirty DSH target behavior
- heading: 12. Role of Existing Compatibility Manifest
- heading: 13. Backward Compatibility with Existing Manifests
- heading: 14. Release Integrity
- heading: 15. Installer Command Behavior
- heading: 16. `status` Behavior
- heading: 17. `dry-run` Behavior
- heading: 18. `install` Behavior
- heading: 19. Post-install Verification
- heading: 20. Source Location Tracking
- heading: 21. Symlink Safety
- heading: 22. `GAT_VERSION.json` Compatibility Evolution
- heading: 23. Version Range — Future Option
- heading: 24. Installer Error Categories
- heading: 25. Exit Code Expectations
- heading: 26. Logging Requirements
- heading: 27. Required Tests
- heading: Test 1 — Clean supported installation
- heading: Test 2 — Dirty GAT source
- heading: Test 3 — New untracked payload source file
- heading: Test 4 — Legacy manifest hash mismatch
- heading: Test 5 — Supported DSH commit
- heading: Test 6 — Unverified DSH commit
- heading: Test 7 — Invalid DSH target
- heading: Test 8 — Broken package entrypoint
- heading: Test 9 — Wrong symlink source
- heading: Test 10 — Rollback after install failure
- heading: 28. Existing Installer Tests
- heading: 29. Recommended New Test Files
- heading: 30. `generate:compatibility`
- heading: 31. Migration Plan
- heading: Phase A — Add version descriptor
- heading: Phase B — Add compatibility evaluator
- heading: Phase C — Downgrade source hash mismatch
- heading: Phase D — Add `--allow-unverified-dsh`
- heading: Phase E — Strengthen verification
- heading: Phase F — Tests and documentation
- heading: 32. CLI Help
- heading: 33. Example Desired Workflow
- heading: 34. Recommended Acceptance Criteria
- heading: 35. Codex Implementation Instructions
- heading: 36. Preferred Final Architecture
