# AI_WORK_SYSTEM_UPDATE_GUIDE_FOR_SOURCE_ROLES_MVP
Version: 0.1  
Status: Update guide  
Scope: MVP only

---

# 1. Purpose

Tài liệu này hướng dẫn cách cập nhật AI Work System hiện tại để support:
- `source_role=working`
- `source_role=legacy`

mà không cần redesign hệ thống.

---

# 2. Core conclusion

Không cần thay đổi core design lớn của AI Work System.

Chỉ cần update nhẹ ở:
- Wiki/source-side contract
- tooling / lint / guide / prompt liên quan đến wiki
- optional baseline package templates nếu muốn đưa vào deploy kit

---

# 3. What does NOT need redesign

Các phần sau không cần đổi lớn:
- Methodology Design
- Conceptual Design
- Architecture Design
- AIP model
- Workspace model
- Contract-driven / SOP-guided overall structure

Lý do:
Current source-side model already has enough room for:
- working source
- legacy source

through:
- `Wiki Source Artifact`
- `Wiki Source Meta`
- `Wiki Source Index`
- `Source Interpretation Profile`

---

# 4. What should be updated

## 4.1. Wiki/source-side contract
Bổ sung vào source-side model các fields/policies:

### Recommended fields
- `source_role`
- `source_use_rule`

### Recommended relation support
- `legacy_of`
- `working_successor_of`
- `compare_with`
- `same_function_different_generation`
- `migration_related`

### Reading rule
For current work:
Truth → Working source-side → Curated Wiki → Legacy source-side when needed → History

---

## 4.2. Wiki freeze summary
Update or annotate:
- `WIKI_V1_FREEZE_SUMMARY_MVP.md`

to mention:
- both working and legacy source fit the same source-side model
- reading priority differs by source role

---

## 4.3. Tooling spec
Update tooling responsibilities so that source-side tools can:
- preserve `source_role`
- preserve `source_use_rule`
- support compare-friendly lookup
- expose working-vs-legacy relation hints

Typical tools affected conceptually:
- source meta builder
- source index builder
- lookup tool
- maintenance / refresh flow

---

## 4.4. Lint / tooling spec
Update lint expectations so that:
- source-side entries can validate role/use-rule
- working/legacy relations are syntactically valid when used
- index/meta keep role/use-rule consistent

---

## 4.5. Wiki creation guide and prompts
Update wiki-related LLM guides so that:
- LLM prefers working source-side artifacts/metas for current work
- LLM uses legacy only as compare/reference unless task explicitly centers legacy analysis
- update drafts can mention whether evidence came from working or legacy source

---

# 5. Minimal update strategy

## Phase A — policy first
Add:
- `WIKI_SOURCE_ROLE_POLICY_MVP.md`

## Phase B — contract refinement
Reflect:
- `source_role`
- `source_use_rule`
- working vs legacy reading priority

in wiki-related docs/specs

## Phase C — tooling awareness
Teach tooling to carry the role and use-rule through:
- meta build
- index build
- lookup
- compare flows

This is enough for MVP.

---

# 6. Things to keep soft

To stay extendable, do NOT freeze too hard:
- exact storage format
- exact relation taxonomy beyond minimal set
- exact tool command names
- exact folder layout for working vs legacy
- exact compare logic

Keep hard only:
- role distinction
- priority distinction
- same-model integration

---

# 7. Suggested update targets

If you want to update the existing document/package set, these are the priority targets:

## Priority 1
- Wiki freeze summary
- tooling spec
- lint/tooling spec
- wiki creation guide
- wiki creation prompt template

## Priority 2
- baseline package docs/templates
- source interpretation profiles for specific source types

## Priority 3
- broader design docs only if you want them to explicitly mention working/legacy source roles

---

# 8. Final note

The right update is:
- **refine the Wiki/source-side layer**
- not redesign the whole AI Work System

This preserves extendability while keeping MVP scope tight.
