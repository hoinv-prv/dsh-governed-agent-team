# UPGRADE_FROM_v0_3_TO_v0_5_0.md

## 1. Upgrade intent
Tài liệu này hỗ trợ project đang ở khoảng `v0.3` nâng lên `v0.5.0`.

## 2. Expected main gaps from v0.3
Dựa trên hướng phát triển hiện tại, project ở `v0.3` thường sẽ thiếu hoặc còn yếu ở:
- unified Wiki Knowledge Profile concept
- explicit candidate / CR / governance flow
- semantic-to-canonical mapping guidance
- project mapping pattern rule
- Wiki-first runtime guidance
- preset-to-project customization rule
- rollout/navigation docs

## 3. Recommended upgrade steps
1. Preserve current project-specific materials:
   - mappings
   - meta fields
   - local AIP tweaks
2. Replace or supersede old profile thinking with:
   - `core/specs/WIKI_KNOWLEDGE_PROFILE_SPEC_v0_1.md`
3. Add missing governance/update docs:
   - change request
   - governance
   - candidate suggestion
4. Add Wave 3 guidelines:
   - artifact understanding guideline
   - profile generation/customization guideline
   - meta build/update guideline
   - AIP template customization guideline
   - guideline index / flow navigator
5. Add Wave 4:
   - Wiki-first runtime guidance
   - preset-to-project customization rule
6. Reconcile old project rules into project-specific layer, not common layer

## 4. Practical migration focus
For `v0.3` projects, recommend prioritizing:
- artifact understanding + canonical mapping
- meta build baseline
- candidate / CR / governance
- AIP template upgrade
before trying to formalize every edge case

## 5. Validation
- choose 1 BD pack
- choose 1 DD pack
- choose 1 AIP template in active use
- validate that new package can handle them with less ad hoc behavior than old version
