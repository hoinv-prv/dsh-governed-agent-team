# UPGRADE_GENERAL_GUIDE_v0_5_0

## 1. Goal
Hướng dẫn chung để version-up từ package cũ lên `v0.5.0`.

## 2. Recommended upgrade approach
1. Backup thư mục AIWS/Wiki hiện tại của project
2. Compare doc inventory cũ với `PACKAGE_MANIFEST_v0_5_0.md`
3. Xác định:
   - docs giữ nguyên
   - docs superseded
   - docs mới cần thêm
   - project customizations cần preserve
4. Merge package mới vào AI folder riêng
5. Reconcile project-specific customizations:
   - mapping pattern
   - meta enrichment rules
   - AIP customizations
6. Review upgrade-sensitive conceptual changes
7. Run minimal validation on 1–2 real project artifacts and 1–2 real AIP flows

## 3. Must-review upgrade-sensitive changes
- `WIKI_KNOWLEDGE_PROFILE_SPEC_v0_1` supersedes older separated profile thinking
- candidate / CR / governance flow is now explicit
- AIP-Wiki integration now distinguishes:
  - deliverable vs working
  - wiki-eligible vs not
  - add-to-wiki handoff vs direct publish
- runtime clarified as Wiki-first, not Wiki-only

## 4. What to preserve from old project
Do not discard project-local knowledge such as:
- project mapping pattern
- confirmed meta enrichment fields
- project-specific AIP behavior
- already useful alias / linkage rules

## 5. Validation after upgrade
At minimum:
- test 1 artifact understanding flow
- test 1 canonical mapping flow
- test 1 meta build/update flow
- test 1 AIP template customization / runtime flow
