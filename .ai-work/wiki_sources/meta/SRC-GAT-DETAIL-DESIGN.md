---
artifact_type: wiki_source_meta
source_id: SRC-GAT-DETAIL-DESIGN
title: GAT Detail Design
source_type: gat_design_document
artifact_locator: docs/gat-design/DETAIL_DESIGN.md
profile_id: gat_design_document
status: active
updated_at: 2026-10-03T23:35:26.598474+00:00
authority_level: working_reference
freshness_status: current
promotion_status: draft
source_representation_status: complete
source_representation_caution: Navigation metadata; inspect original source for decisions. External sources require the sibling checkout.
source_representation_quality_issue: false
maintenance_status: current
representation_scope: unknown
knowledge_value: unknown
intended_ai_use: unknown
representation_type: markdown
conversion_method: unknown
conversion_limitations: []
---
# Wiki Source Meta — GAT Detail Design

## Summary
Formal source-aligned GAT detail design: 18 DD contracts covering data, algorithms, ordering, errors and sourced WHY; current code is truth and DD-16 through DD-18 remain target-only.

## Knowledge Targets
- architecture
- behavior
- implementation_guidance

## Lookup Keys
- GAT Detail Design
- GAT-DETAIL-DESIGN
- DETAIL_DESIGN.md

## Source-Specific Hints
- heading: GAT Detail Design
- heading: 1. Authority and implementation baseline
- heading: 2. Shared current data contracts
- heading: DD-01 — Workspace configuration and Session Enable
- heading: DD-02 — Roster provisioning and child ownership
- heading: DD-03 — Journal, projection and persisted-session reads
- heading: DD-04 — Task DAG, CAS and transitions
- heading: DD-05 — Plan approval and approved-chat import
- heading: DD-06 — Mission snapshots and current approval shortcut
- heading: DD-07 — Durable peer mailbox
- heading: DD-08 — Work, waits, interrupt and disposal
- heading: DD-09 — Scoped model tools and execution guards
- heading: DD-10 — Browser Remote mount and projection rendering
- heading: DD-11 — Profiles, compatibility and installer
- heading: DD-12 — Standalone governance and reference-memory storage
- heading: DD-13 — Standalone deny-first policy and memory wrapper
- heading: DD-14 — Standalone conformance tooling
- heading: DD-15 — External Durable Agent service and provider
- heading: 3. Target design appendix — no current GAT production implementation
- heading: 4. Source/design discrepancies to preserve

## Related Sources
- **SRC-GAT-DESIGN-SOURCE-MAP** — role: downstream_navigation — The mapping locates exact source symbols/tests for DD contracts; does not prove test PASS. [asserted]
- **SRC-GAT-MEMBER-BINDING-FREEZE** — role: upstream_input — Frozen target-only attachment/authorization contracts explain DD-16/DD-17; no production implementation claimed. [asserted]
- **SRC-GAT-MISSION-DESIGN-DELTAS** — role: upstream_input — Historical/PoC evidence explains target gaps and current-versus-mission discrepancies. [asserted]
- **SRC-GAT-CODE-PACKAGES-TOOLS-SRC-TEAM-CONFIG-TS** — role: describes — DD-01: inspected implementation/configuration described by the source map; scope=gat. Source code defines implemented behavior. [asserted]
- **SRC-GAT-CODE-PACKAGES-TOOLS-SRC-INDEX-TS** — role: describes — DD-01, DD-09: inspected implementation/configuration described by the source map; scope=gat. Source code defines implemented behavior. [asserted]
- **SRC-GAT-CODE-PACKAGES-CORE-SRC-INDEX-TS** — role: describes — DD-01, DD-05, DD-06, DD-08: inspected implementation/configuration described by the source map; scope=gat. Source code defines implemented behavior. [asserted]
- **SRC-GAT-CODE-PACKAGES-TOOLS-TESTS-TEAM-CONFIG-SPEC-TS** — role: related — DD-01: inspected verification fixture described by the source map; scope=gat. Existing test file only; not a new test execution. [asserted]
- **SRC-GAT-CODE-PACKAGES-TOOLS-TESTS-TOOL-TEAM-SPEC-TS** — role: related — DD-01, DD-05, DD-09: inspected verification fixture described by the source map; scope=gat. Existing test file only; not a new test execution. [asserted]
- **SRC-GAT-CODE-PACKAGES-CORE-TESTS-TEAM-SPEC-TS** — role: related — DD-01, DD-02, DD-04, DD-05, DD-06, DD-07, DD-08: inspected verification fixture described by the source map; scope=gat. Existing test file only; not a new test execution. [asserted]
- **SRC-GAT-CODE-PACKAGES-CORE-SRC-ROSTER-TS** — role: describes — DD-02, DD-08: inspected implementation/configuration described by the source map; scope=gat. Source code defines implemented behavior. [asserted]
- **SRC-GAT-CODE-PACKAGES-CORE-TESTS-PERSISTENCE-SPEC-TS** — role: related — DD-02, DD-03, DD-07, DD-08: inspected verification fixture described by the source map; scope=gat. Existing test file only; not a new test execution. [asserted]
- **SRC-GAT-CODE-PACKAGES-CORE-SRC-JOURNAL-TS** — role: describes — DD-03: inspected implementation/configuration described by the source map; scope=gat. Source code defines implemented behavior. [asserted]
- **SRC-GAT-CODE-PACKAGES-CORE-SRC-PROJECTION-TS** — role: describes — DD-03: inspected implementation/configuration described by the source map; scope=gat. Source code defines implemented behavior. [asserted]
- **SRC-GAT-CODE-PACKAGES-CORE-SRC-PERSISTED-TS** — role: describes — DD-03: inspected implementation/configuration described by the source map; scope=gat. Source code defines implemented behavior. [asserted]
- **SRC-GAT-CODE-PACKAGES-CORE-TESTS-PROJECTION-EVENTS-SPEC-TS** — role: related — DD-03, DD-04, DD-06: inspected verification fixture described by the source map; scope=gat. Existing test file only; not a new test execution. [asserted]
- **SRC-GAT-CODE-PACKAGES-CORE-SRC-TASK-BOARD-TS** — role: describes — DD-04, DD-05: inspected implementation/configuration described by the source map; scope=gat. Source code defines implemented behavior. [asserted]
- **SRC-GAT-CODE-PACKAGES-CORE-SRC-TASK-GRAPH-TS** — role: describes — DD-04: inspected implementation/configuration described by the source map; scope=gat. Source code defines implemented behavior. [asserted]
- **SRC-GAT-CODE-PACKAGES-CORE-SRC-TYPES-TS** — role: describes — DD-04, DD-06: inspected implementation/configuration described by the source map; scope=gat. Source code defines implemented behavior. [asserted]
- **SRC-GAT-CODE-PACKAGES-CORE-SRC-APPROVED-PLAN-IMPORT-TS** — role: describes — DD-05: inspected implementation/configuration described by the source map; scope=gat. Source code defines implemented behavior. [asserted]
- **SRC-GAT-CODE-PACKAGES-CORE-SRC-MISSION-BOARD-TS** — role: describes — DD-06: inspected implementation/configuration described by the source map; scope=gat. Source code defines implemented behavior. [asserted]
- **SRC-GAT-CODE-PACKAGES-CORE-SRC-MISSION-PLAN-TS** — role: describes — DD-06: inspected implementation/configuration described by the source map; scope=gat. Source code defines implemented behavior. [asserted]
- **SRC-GAT-CODE-PACKAGES-CORE-SRC-MAILBOX-TS** — role: describes — DD-07: inspected implementation/configuration described by the source map; scope=gat. Source code defines implemented behavior. [asserted]
- **SRC-GAT-CODE-PACKAGES-CORE-SRC-SESSION-MESSAGE-TS** — role: describes — DD-07: inspected implementation/configuration described by the source map; scope=gat. Source code defines implemented behavior. [asserted]
- **SRC-GAT-CODE-PACKAGES-CORE-SRC-WORK-STATE-TS** — role: describes — DD-08: inspected implementation/configuration described by the source map; scope=gat. Source code defines implemented behavior. [asserted]
- **SRC-GAT-CODE-PACKAGES-CORE-SRC-ACTIVITY-TS** — role: describes — DD-08: inspected implementation/configuration described by the source map; scope=gat. Source code defines implemented behavior. [asserted]
- **SRC-GAT-CODE-PACKAGES-CORE-SRC-LIFECYCLE-TS** — role: describes — DD-08: inspected implementation/configuration described by the source map; scope=gat. Source code defines implemented behavior. [asserted]
- **SRC-GAT-CODE-PACKAGES-WEB-SRC-CLIENT-TEAMACTION-TSX** — role: describes — DD-10: inspected implementation/configuration described by the source map; scope=gat. Source code defines implemented behavior. [asserted]
- **SRC-GAT-CODE-PACKAGES-WEB-SRC-CLIENT-MOUNT-TS** — role: describes — DD-10: inspected implementation/configuration described by the source map; scope=gat. Source code defines implemented behavior. [asserted]
- **SRC-GAT-CODE-PACKAGES-WEB-SRC-CLIENT-INDEX-TS** — role: describes — DD-10: inspected implementation/configuration described by the source map; scope=gat. Source code defines implemented behavior. [asserted]
- **SRC-GAT-CODE-PACKAGES-WEB-TESTS-TEAM-ACTION-CLIENT-SPEC-TSX** — role: related — DD-10: inspected verification fixture described by the source map; scope=gat. Existing test file only; not a new test execution. [asserted]
- **SRC-GAT-CODE-PACKAGES-WEB-TESTS-BROWSER-PLUGIN-CLIENT-SPEC-TS** — role: related — DD-10: inspected verification fixture described by the source map; scope=gat. Existing test file only; not a new test execution. [asserted]
- **SRC-GAT-CODE-PACKAGES-PROFILE-CORDIS-PATCH-YML** — role: describes — DD-11: inspected implementation/configuration described by the source map; scope=gat. Source code defines implemented behavior. [asserted]
- **SRC-GAT-CODE-PACKAGES-WEB-PROFILE-CORDIS-PATCH-YML** — role: describes — DD-11: inspected implementation/configuration described by the source map; scope=gat. Source code defines implemented behavior. [asserted]
- **SRC-GAT-CODE-INSTALLER-INDEX-MJS** — role: describes — DD-11: inspected implementation/configuration described by the source map; scope=gat. Source code defines implemented behavior. [asserted]
- **SRC-GAT-CODE-INSTALLER-COMPATIBILITY-MJS** — role: describes — DD-11: inspected implementation/configuration described by the source map; scope=gat. Source code defines implemented behavior. [asserted]
- **SRC-GAT-CODE-INSTALLER-VERIFY-MJS** — role: describes — DD-11: inspected implementation/configuration described by the source map; scope=gat. Source code defines implemented behavior. [asserted]
- **SRC-GAT-CODE-PACKAGES-PROFILE-TESTS-PROFILE-SPEC-TS** — role: related — DD-11: inspected verification fixture described by the source map; scope=gat. Existing test file only; not a new test execution. [asserted]
- **SRC-GAT-CODE-PACKAGES-WEB-PROFILE-TESTS-PROFILE-SPEC-TS** — role: related — DD-11: inspected verification fixture described by the source map; scope=gat. Existing test file only; not a new test execution. [asserted]
- **SRC-GAT-CODE-INSTALLER-TESTS-CLI-TEST-MJS** — role: related — DD-11: inspected verification fixture described by the source map; scope=gat. Existing test file only; not a new test execution. [asserted]
- **SRC-GAT-CODE-INSTALLER-TESTS-COMPATIBILITY-TEST-MJS** — role: related — DD-11: inspected verification fixture described by the source map; scope=gat. Existing test file only; not a new test execution. [asserted]
- **SRC-GAT-CODE-INSTALLER-TESTS-VERIFY-PROFILE-TEST-MJS** — role: related — DD-11: inspected verification fixture described by the source map; scope=gat. Existing test file only; not a new test execution. [asserted]
- **SRC-GAT-CODE-PACKAGES-GAT-SRC-GOVERNANCE-INDEX-MJS** — role: describes — DD-12: inspected implementation/configuration described by the source map; scope=gat. Source code defines implemented behavior. [asserted]
- **SRC-GAT-CODE-PACKAGES-GAT-SRC-MEMORY-INDEX-MJS** — role: describes — DD-12: inspected implementation/configuration described by the source map; scope=gat. Source code defines implemented behavior. [asserted]
- **SRC-GAT-CODE-PACKAGES-GAT-TESTS-GOVERNANCE-TEST-MJS** — role: related — DD-12: inspected verification fixture described by the source map; scope=gat. Existing test file only; not a new test execution. [asserted]
- **SRC-GAT-CODE-PACKAGES-GAT-TESTS-PARTITION-STORE-TEST-MJS** — role: related — DD-12: inspected verification fixture described by the source map; scope=gat. Existing test file only; not a new test execution. [asserted]
- **SRC-GAT-CODE-PACKAGES-GAT-TESTS-TRANSACTION-AUDIT-TEST-MJS** — role: related — DD-12: inspected verification fixture described by the source map; scope=gat. Existing test file only; not a new test execution. [asserted]
- **SRC-GAT-CODE-PACKAGES-GAT-TESTS-LIFECYCLE-PRIVACY-TEST-MJS** — role: related — DD-12: inspected verification fixture described by the source map; scope=gat. Existing test file only; not a new test execution. [asserted]
- **SRC-GAT-CODE-PACKAGES-GAT-SRC-POLICY-INDEX-MJS** — role: describes — DD-13: inspected implementation/configuration described by the source map; scope=gat. Source code defines implemented behavior. [asserted]
- **SRC-GAT-CODE-PACKAGES-GAT-SRC-ADAPTER-INDEX-MJS** — role: describes — DD-13: inspected implementation/configuration described by the source map; scope=gat. Source code defines implemented behavior. [asserted]
- **SRC-GAT-CODE-PACKAGES-GAT-TESTS-POLICY-SELECTOR-TEST-MJS** — role: related — DD-13: inspected verification fixture described by the source map; scope=gat. Existing test file only; not a new test execution. [asserted]
- **SRC-GAT-CODE-PACKAGES-GAT-TESTS-WRAPPER-ADMISSION-TEST-MJS** — role: related — DD-13: inspected verification fixture described by the source map; scope=gat. Existing test file only; not a new test execution. [asserted]
- **SRC-GAT-CODE-PACKAGES-GAT-SRC-CONFORMANCE-INDEX-MJS** — role: describes — DD-14: inspected implementation/configuration described by the source map; scope=gat. Source code defines implemented behavior. [asserted]
- **SRC-GAT-CODE-PACKAGES-GAT-SRC-CONFORMANCE-SCENARIO-MJS** — role: describes — DD-14: inspected implementation/configuration described by the source map; scope=gat. Source code defines implemented behavior. [asserted]
- **SRC-GAT-CODE-PACKAGES-GAT-SRC-CONFORMANCE-RUNTIME-MJS** — role: describes — DD-14: inspected implementation/configuration described by the source map; scope=gat. Source code defines implemented behavior. [asserted]
- **SRC-GAT-CODE-PACKAGES-GAT-SRC-CONFORMANCE-CLI-MJS** — role: describes — DD-14: inspected implementation/configuration described by the source map; scope=gat. Source code defines implemented behavior. [asserted]
- **SRC-GAT-CODE-PACKAGES-GAT-SRC-INDEX-MJS** — role: describes — DD-14: inspected implementation/configuration described by the source map; scope=gat. Source code defines implemented behavior. [asserted]
- **SRC-GAT-CODE-PACKAGES-GAT-TESTS-CONFORMANCE-RUNNER-TEST-MJS** — role: related — DD-14: inspected verification fixture described by the source map; scope=gat. Existing test file only; not a new test execution. [asserted]
- **SRC-GAT-CODE-PACKAGES-GAT-TESTS-CONFORMANCE-CONTRACT-MATRIX-TEST-MJS** — role: related — DD-14: inspected verification fixture described by the source map; scope=gat. Existing test file only; not a new test execution. [asserted]
- **SRC-GAT-CODE-PACKAGES-GAT-TESTS-BUILT-PACKAGE-TEST-MJS** — role: related — DD-14: inspected verification fixture described by the source map; scope=gat. Existing test file only; not a new test execution. [asserted]
- **SRC-DA-CODE-DURABLE-AGENT-PLUGIN-SRC-SERVICE-TS** — role: describes — DD-15: inspected implementation/configuration described by the source map; scope=durable-agent. Source code defines implemented behavior. [asserted]
- **SRC-DA-CODE-DURABLE-AGENT-PLUGIN-SRC-LOCAL-PROVIDER-TS** — role: describes — DD-15: inspected implementation/configuration described by the source map; scope=durable-agent. Source code defines implemented behavior. [asserted]
- **SRC-DA-CODE-DURABLE-AGENT-PLUGIN-SRC-CONSUMER-TS** — role: describes — DD-15: inspected implementation/configuration described by the source map; scope=durable-agent. Source code defines implemented behavior. [asserted]
- **SRC-DA-CODE-DURABLE-AGENT-PLUGIN-TESTS-SERVICE-CONTRACTS-SPEC-TS** — role: related — DD-15: inspected verification fixture described by the source map; scope=durable-agent. Existing test file only; not a new test execution. [asserted]
- **SRC-DA-CODE-DURABLE-AGENT-PLUGIN-TESTS-LOCAL-PROVIDER-SPEC-TS** — role: related — DD-15: inspected verification fixture described by the source map; scope=durable-agent. Existing test file only; not a new test execution. [asserted]
- **SRC-DA-CODE-DURABLE-AGENT-PLUGIN-TESTS-MEMORY-LIFECYCLE-SPEC-TS** — role: related — DD-15: inspected verification fixture described by the source map; scope=durable-agent. Existing test file only; not a new test execution. [asserted]
- **SRC-DA-CODE-DURABLE-AGENT-PLUGIN-TESTS-CONSUMER-SPEC-TS** — role: related — DD-15: inspected verification fixture described by the source map; scope=durable-agent. Existing test file only; not a new test execution. [asserted]
- **SRC-DA-CODE-DURABLE-AGENT-PLUGIN-TESTS-COMPOSITION-SPEC-TS** — role: related — DD-15: inspected verification fixture described by the source map; scope=durable-agent. Existing test file only; not a new test execution. [asserted]
