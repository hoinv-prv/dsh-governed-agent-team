---
artifact_type: wiki_source_meta
source_id: SRC-METHOD-methodology-20-specs-standard-pack-contract-spec-mvp-md-5917
title: methodology / 20_specs/Standard_Pack_Contract_Spec_MVP.md
source_type: methodology_spec
artifact_locator: .ai-work/truth/canonical/methodology/20_specs/Standard_Pack_Contract_Spec_MVP.md
profile_id: methodology_spec
status: active
updated_at: 2026-09-11T05:12:48.063366+00:00
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
system: aiws
---
# Wiki Source Meta — methodology / 20_specs/Standard_Pack_Contract_Spec_MVP.md

## Summary
Một Standard Pack là gói tài sản quy trình CÓ VERSION của một tổ chức, được AIWS chở tới dự án. Spec này chốt HỢP ĐỒNG, không chốt nội dung: layout area-first của pack (§2), frontmatter bắt buộc của asset với bảy kind và bốn classification (§3–§4), phân vai AIP / Skill / Rule trong một task (§5), schema task_catalog.yml với sáu archetype bind sang asset · AIP · skill · role · human_gate (§6), cách cài skill của pack (§7), ranh giới pack-owned .ai-work/standard_pack ↔ project-owned .ai-work/project_process kèm header provenance và thứ tự ưu tiên project > pack (§8), ba lớp version AIWS · pack · pin của dự án (§9), ngoại lệ rule 8 cho product/standard_pack (§10), 11 mã lint của lint_standard_pack.py (§11) và wiki projection qua profile standard_asset (§12). Nội dung quy trình thuộc chủ pack, không thuộc AIWS.

## Knowledge Targets
- reference
- domain
- pattern

## Lookup Keys
- Standard Pack Contract Spec for AI Work System MVP
- for AI Work System MVP pack.yml
- for AI Work System MVP asset_id
- for AI Work System MVP kind bảy giá trị
- for AI Work System MVP Ranh giới process ↔ dự án
- Standard Pack Contract Spec MVP
- Standard Pack Contract Spec MVP layout va frontmatter cua asset
- Standard Pack Contract Spec MVP task_catalog schema va archetype
- standard pack
- quy trinh chuan cong ty
- company standard process pack
- classification mandatory default tailorable reference
- pack version pin
- pack.yml
- task_catalog.yml
- asset_id
- tailoring
- project_process
- pull_standard_pack
- lint_standard_pack
- install_standard_pack
- resolve_task
- build_standard_pack_package
- standard_asset
- aiws_min_version
- human_gate
- pack
- area
- aiws
- asset
- skill
- task
- lint
- aip
- hai
- template
- quy
- task_id
- tailored
- roles

## Source-Specific Hints
- heading: Standard Pack Contract Spec for AI Work System MVP
- heading: 1. Mục đích và phạm vi
- heading: 2. Layout của một pack
- heading: 2.1 `pack.yml`
- heading: 3. Frontmatter của asset
- heading: 3.1 `asset_id`
- heading: 3.2 `kind` — bảy giá trị
- heading: 4. Ngữ nghĩa `classification`
- heading: 4.1 Ranh giới process ↔ dự án
- heading: 4.2 Ai đổi được classification
- heading: 4.3 "Definition of good" nằm ở đâu
- heading: 5. AIP vs Skill vs Rule — ba vai, không chồng nhau
- heading: 6. `task_catalog.yml`
- heading: 6.1 `task_id`
- heading: 6.2 `archetype` — sáu giá trị
- heading: 6.3 `assets` — bind bằng `asset_id`, không bằng đường dẫn
- heading: 6.4 `roles` và `common/roles.yml`
- heading: 6.5 `human_gate`
- heading: 7. Skills & Install Mapping — skill của pack và cách cài
- heading: 7.1 Hình dạng
- heading: 7.2 Cài
- heading: 7.3 `skills[]` trong task catalog
- heading: 8. Ranh giới pack ↔ bản tailored của dự án
- heading: 8.1 Hai cây, hai chủ
- heading: 8.2 Header provenance của một bản tailored
- heading: 8.3 Thứ tự ưu tiên lúc chạy
- heading: 8.4 Override task catalog
- heading: 9. Ba lớp version
- heading: 9.1 Không tự nâng cấp
- heading: 9.2 Tương thích ngược
- heading: 9.3 Guard lúc cài
- heading: 10. Ngoại lệ rule 8 cho `product/standard_pack/`
- heading: 11. Lint — `lint_standard_pack.py`
- heading: 11.1 Chỗ khác trong AIWS phải biết pack tồn tại
- heading: 12. Wiki projection
- heading: 13. Open points
- heading: 13.1 Mở từ lúc soạn spec
- heading: 13.2 Phát hiện lúc thực thi (mission `vti-standard-pack`, T23)
- heading: 14. Quan hệ
