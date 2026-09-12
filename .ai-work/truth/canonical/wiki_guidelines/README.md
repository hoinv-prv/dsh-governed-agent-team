# AIWS Wiki Rollout Installation Package v0.5.0

Đây là full installation package cho sprint Wiki của AI Work System.

## Package goals
- hỗ trợ **new installation**
- hỗ trợ **version upgrade** từ các bản cũ như `v0.3`, `v0.4`
- cung cấp bộ **canonical docs**
- cung cấp **rollout guidelines**
- cung cấp **install / upgrade checklists**
- cung cấp **changelog / migration notes**

## Recommended reading order
1. `install/NEW_INSTALLATION_GUIDE_v0_5_0.md` hoặc `upgrade/UPGRADE_GENERAL_GUIDE_v0_5_0.md`
2. `rollout/PROJECT_ROLLOUT_GUIDELINE_v0_5_0.md`
3. `core/guidelines/GUIDELINE_INDEX_FLOW_NAVIGATOR_v0_1.md`

## Main package sections
- `core/specs` — canonical specs
- `core/guidelines` — canonical guidelines
- `core/prompts` — prompt pairs / operational prompts
- `install` — new install docs and checklists
- `upgrade` — upgrade docs from old versions
- `rollout` — rollout plan / rollout checklist / project onboarding
- `appendix` — backlog, execution notes, deprecated transition notes

## Notes
- Package này ưu tiên **usable rollout** hơn là perfect formal release engineering.
- Các docs cũ kiểu `WIKI_ARTIFACT_PROFILE_SPEC` và `WIKI_USAGE_PROFILE_SPEC` đã được supersede bởi `WIKI_KNOWLEDGE_PROFILE_SPEC`.
- Canonical runtime direction hiện tại là:
  - Task Lens routes task → knowledge
  - runtime is Wiki-first, not Wiki-only
  - canonical update vẫn qua candidate / CR / governance
