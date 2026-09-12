---
artifact_type: wiki_source_meta
node_kind: object
source_id: SRC-FUNC-sample-login
title: "Object-node golden fixture — sample login function"
source_type: function
artifact_locator: __OBJECT__
profile_id: knowledge_object
status: active
---

## Summary
Golden-fixture object node (node_kind=object) used by the lint CI guard `_lint_object_golden_fixtures`
to assert a spec-correct Knowledge Object meta stays lint-clean: profile_id required (CR-AIWS-2026-06-004
C1), source_type whitelisted via the knowledge_object profile (C2/C3), never-empty body with one out-edge
(INV-4), __OBJECT__ sentinel agreeing with node_kind=object (INV-9). Represents a sample login function.

## Knowledge Targets
- object_identity
- object_relations

## Lookup Keys
- sample login function
- login
- F-sample

## Related Sources
- **SRC-BD-SAMPLE-LOGIN** — role: represented_by — fixture-only pointer to the design doc that would describe this function [asserted]
