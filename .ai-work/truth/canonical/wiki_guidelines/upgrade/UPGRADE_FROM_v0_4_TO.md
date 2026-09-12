# UPGRADE_FROM_v0_4_TO_v0_5_0.md

## 1. Upgrade intent
Tài liệu này hỗ trợ project đang ở khoảng `v0.4` nâng lên `v0.5.0`.

## 2. Expected main gaps from v0.4
So với `v0.4`, package `v0.5.0` chủ yếu tăng cường:
- clearer semantic-to-canonical mapping flow
- stronger project mapping pattern concept
- stronger meta build/update separation
- clearer guideline index / flow navigator
- clearer Wiki-first runtime behavior
- clearer preset/common vs project-specific vs task-instance layering

## 3. Recommended upgrade steps
1. Keep existing useful project customizations
2. Add missing docs from Wave 3 and Wave 4
3. Review whether old customizations belong to:
   - preset/common
   - project-specific
   - task-instance
4. Rework old ad hoc runtime behavior toward:
   - notebook/current context
   - Wiki Meta / Index
   - linked artifacts
   - raw/source as deeper escalation
5. Review AIP templates for:
   - deliverable vs working distinction
   - wiki-eligible handling
   - add-to-wiki handoff wording

## 4. Migration caution
Do not blindly overwrite project-local rules that already work well.
Instead:
- compare them to the new package
- keep them if still useful
- move them to the right layer if needed
- propose promote-back only when pattern is sufficiently reusable

## 5. Validation
At minimum:
- test one existing runtime use case
- test one meta update use case
- test one AIP customization use case
