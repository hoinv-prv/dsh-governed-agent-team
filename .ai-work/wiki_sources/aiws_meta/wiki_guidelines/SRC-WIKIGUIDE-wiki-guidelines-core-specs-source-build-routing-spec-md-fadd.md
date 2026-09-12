---
artifact_type: wiki_source_meta
source_id: SRC-WIKIGUIDE-wiki-guidelines-core-specs-source-build-routing-spec-md-fadd
title: wiki_guidelines / core/specs/SOURCE_BUILD_ROUTING_SPEC.md
source_type: wiki_guideline
artifact_locator: .ai-work/truth/canonical/wiki_guidelines/core/specs/SOURCE_BUILD_ROUTING_SPEC.md
profile_id: wiki_guideline
status: active
updated_at: 2026-07-04T03:00:10.070126+00:00
promotion_status: draft
source_representation_caution: Representation quality has not been reviewed.
representation_type: markdown
system: aiws
maintenance_status: active
review_required: False
review_status: approved_to_apply
lint_accept:
  - code: meta_lookup_key_marker_midname
    reason: "Ở key này `SUPERSEDED` là VĂN XUÔI mô tả quan hệ Stage 1 <-> Stage 2 bên trong chính tài liệu ('Stage 1 (SUPERSEDED by Stage 2 retained as history)'), KHÔNG phải nhãn trạng thái của tài liệu này — tài liệu vẫn active. Gỡ token sẽ bẻ gãy nghĩa của câu (đã thử: 'Stage 1 by Stage 2' + ngoặc mồ côi). Trạng thái thật, nếu cần, thuộc về field `status`, không phải chữ trong key (CR-AIWS-2026-08-107 §7.4)."
    accepted_by: "hoinv (Wiki-Manager, duyệt CR-AIWS-2026-08-107 — apply 2026-08-19)"
---
# Wiki Source Meta — wiki_guidelines / core/specs/SOURCE_BUILD_ROUTING_SPEC.md

## Summary
Định nghĩa cách AIWS map một `source_type` → **tool/skill nào dùng để BUILD và REFRESH** wiki source

## Knowledge Targets
- reference
- pattern
- domain

## Lookup Keys
- SOURCE_BUILD_ROUTING_SPEC (Stage 2 MVP)
- SOURCE_BUILD_ROUTING_SPEC (Stage 2 MVP) Purpose
- SOURCE_BUILD_ROUTING_SPEC (Stage 2 MVP) Verified gap (vì sao cần)
- SOURCE_BUILD_ROUTING_SPEC (Stage 2 MVP) Config home invariant (KEY co decided với CR 017)
- SOURCE_BUILD_ROUTING_SPEC (Stage 2 MVP) Stage 1 (SUPERSEDED by Stage 2 retained as history) static seam, no registry
- Stage
- builder
- source_type
- source
- build
- AIWS
- wiki
- tool
- meta
- bulk
- generic
- register
- routing
- file
- route
- spec
- MVP
- sources
- stdlib
- static
- registry
- A3b
- tooling
- Build
- driven
- java_source
- subdir
- partial
- directive
- AIP
- EXEC
- dispatch
- artifact
- build_java_wiki_metas
- refresh

## Source-Specific Hints
- heading: SOURCE_BUILD_ROUTING_SPEC (Stage 2 — MVP)
- heading: 1. Purpose
- heading: 2. Verified gap (vì sao cần)
- heading: 3. Config-home invariant (KEY — co-decided với CR-017)
- heading: 4. Stage 1 (SUPERSEDED by Stage 2 — retained as history) — static seam, no registry
- heading: 5. Stage 2 (IMPLEMENTED — MVP; CR-AIWS-2026-05-019 Stage 2 applied 2026-06-15 via AIP-EXEC-101)
- heading: 6. See Also

## Related Sources
- **SRC-WIKIGUIDE-wiki-guidelines-core-specs-wiki-meta-index-spec-md-15a8** — role: system_foundation — Every builder this routing table dispatches to must emit a meta in the schema owned there (frontmatter + Summary / Knowledge Targets / Lookup Keys, or a partial carrying `needs_completion`), while this spec's own _build_routing.json registry is explicitly NOT projected into index.jsonl (§3 invariant) and §A12 there was amended to sanction this spec; coupling = the meta record schema plus the index projection boundary; a change to the meta schema changes the build-tool contract and what lint_wiki will accept from a routed builder. [asserted]
