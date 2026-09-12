# PRESET_TO_PROJECT_CUSTOMIZATION_RULE_v0_1

## 1. Purpose
Tài liệu này định nghĩa rule tối thiểu cho việc chuyển từ:
- **preset/common layer**
sang
- **project-specific customized layer**

trong sprint hiện tại.

Mục tiêu:
- tận dụng preset/common assets tối đa
- nhưng không ép project phải fit máy móc theo preset
- giữ rõ boundary giữa:
  - cái gì nên giữ ở common layer
  - cái gì nên customize theo project
  - cái gì có thể promote ngược từ project lên preset/common về sau

Trong sprint này, rule được define ở mức **minimal but usable**.

---

## 2. Why this rule is needed
Nếu không có rule này, dễ xảy ra hai cực đoan:

### Cực đoan A
Mọi thứ đều bị project hóa quá sớm:
- mất reuse
- duplicate effort
- khó bảo trì

### Cực đoan B
Mọi thứ đều bị ép theo preset:
- lệch project reality
- giảm usability
- làm AI/HUMAN phải workaround bằng cách ad hoc

Do đó cần một rule để quyết định:
- cái gì giữ preset
- cái gì customize
- cái gì có thể promote ngược

---

## 3. Core principle
**Preset-first, project-fit, human-confirmed.**

Điều đó nghĩa là:
1. bắt đầu từ preset/common gần nhất
2. customize vừa đủ để fit project
3. các customize quan trọng nên được HUMAN confirm
4. nếu một customize chứng minh có giá trị dùng chung, có thể đề xuất promote lên common/preset layer

---

## 4. Main layer definitions

### 4.1. Preset / Common layer
Là layer dùng chung cho nhiều project, ví dụ:
- common artifact understanding ideas
- common canonical slots
- common meta/index baseline
- common AIP template skeletons
- common guideline structure
- common candidate / governance principles

### 4.2. Project-specific layer
Là layer phản ánh đặc thù của một project, ví dụ:
- artifact naming/style riêng
- format/template riêng
- project mapping pattern
- extra meta/search fields
- deliverable/wiki-eligible rules
- project-specific AIP behavior
- project-specific review/search hotspots

### 4.3. Task-instance layer
Là layer ad hoc cho một task cụ thể, ví dụ:
- một exception tạm thời
- một missing artifact workaround
- một local task decision chưa đủ để common hóa hoặc project hóa

---

## 5. Default rule
Mặc định khi chưa rõ, nên phân lớp như sau:

- thứ gì có vẻ reusable across many projects → giữ ở preset/common
- thứ gì phản ánh project reality cụ thể → để ở project-specific
- thứ gì chỉ phục vụ một task instance → để ở task-instance / notebook / local adjustment

---

## 6. What usually belongs to preset/common layer

### 6.1. Common understanding
- artifact family concepts
- canonical slot concepts
- common relation families
- common runtime layer ordering
- common candidate/governance logic

### 6.2. Common template skeletons
- AIP preset skeleton
- prompt skeleton
- output shape skeleton
- review checklist skeleton

### 6.3. Common baseline rules
- keep confirmed / inferred / unresolved separate
- resolved vs reflected distinction
- candidate ≠ canonical update
- Wiki-first, not Wiki-only

### Rule
Nếu một rule vẫn hợp lý cho nhiều project mà không cần thay đổi bản chất,
nó nên ở preset/common.

---

## 7. What usually belongs to project-specific layer

### 7.1. Project artifact reality
- project artifact classes
- naming conventions
- template decomposition style
- project-specific alias patterns
- project mapping pattern

### 7.2. Project search/review needs
- extra meta fields
- extra relation fields
- extra searchable fields
- business keywords
- review hotspots
- dependency cues

### 7.3. Project execution expectations
- deliverable vs working distinction
- wiki-eligible vs not
- add-to-wiki handoff expectations
- project AIP adjustments
- project-specific evidence expectations

### Rule
Nếu nội dung chủ yếu để fit project này và không chắc dùng chung tốt,
nó nên ở project-specific layer.

---

## 8. What usually belongs to task-instance layer

### 8.1. Local temporary decisions
- one-off workaround
- short-term handling for missing docs
- one-time exception mapping
- tentative note not yet confirmed

### 8.2. Still-maturing findings
- weak insight
- low-confidence mapping
- task-only prioritization note
- unresolved temporary interpretation

### Rule
Không nên promote quá sớm từ task-instance lên project-specific hoặc common nếu chưa đủ chín.

---

## 9. Customization decision rule

### 9.1. Keep in preset if
- reusable beyond this project
- low need for project-specific wording
- structurally stable
- not tightly bound to project artifacts/process

### 9.2. Move to project-specific if
- depends on project profile
- depends on project artifact style/template
- depends on project search/review needs
- depends on project governance/application choice

### 9.3. Keep task-local if
- still too weak
- too temporary
- too one-off
- not worth formalizing yet

---

## 10. Human confirmation rule

### 10.1. Why HUMAN confirm matters
Project-specific customization có thể ảnh hưởng mạnh tới:
- runtime behavior
- meta fields
- candidate suggestion
- AIP flow
- search/review effectiveness

### 10.2. Rule
Những customize quan trọng nên được HUMAN confirm, nhất là:
- project-specific meta enrichment
- project mapping pattern used for strong reuse
- deliverable/wiki-eligible decisions
- project-customized AIP completion behavior
- promote-to-common suggestions

---

## 11. Promote-back rule (project → common)

### 11.1. Why promote-back matters
Một project-specific customization đôi khi rất tốt và có thể hữu ích cho nhiều project khác.

### 11.2. Promote-back candidate signs
Có thể cân nhắc promote lên common/preset khi:
- pattern ổn định
- không quá project-bound
- đã được reuse nhiều lần
- mang lại value rõ ràng
- ít cần project-only assumptions

### 11.3. Rule
Promote-back nên là:
- suggestion
- review
- then merge into common layer if appropriate

Không nên tự động coi project-specific improvement là new preset immediately.

---

## 12. Suggested decision checklist
Khi gặp một rule/template/mapping/meta customization mới, nên hỏi:

1. Cái này có fit nhiều project không?
2. Nó có phụ thuộc mạnh vào project profile không?
3. Nó có chỉ là workaround cho task hiện tại không?
4. Nếu reuse, reuse ở layer nào là hợp lý nhất?
5. Có cần HUMAN confirm trước khi formalize không?
6. Có dấu hiệu đáng promote-back lên common không?

---

## 13. Examples

### 13.1. Common layer example
Rule:
- “confirmed / inferred / unresolved phải tách rõ”
→ nên ở common layer

### 13.2. Project-specific example
Rule:
- “Weekly Report của project này là deliverable và wiki-eligible”
→ nên ở project-specific layer

### 13.3. Task-instance example
Note:
- “Task review hôm nay tạm skip artifact X vì khách chưa gửi”
→ nên ở task-instance layer

### 13.4. Promote-back example
Pattern:
- “DD split FE/API/BE mapping pattern” nếu dùng tốt ở nhiều project tương tự
→ có thể là candidate để promote-back sau review

---

## 14. Relationship with existing sprint artifacts
Rule này được thiết kế để nối:
- `WIKI_PROFILE_GENERATION_CUSTOMIZATION_GUIDELINE_v0_1`
- `WIKI_META_BUILD_UPDATE_GUIDELINE_v0_1`
- `AIP_TEMPLATE_CUSTOMIZATION_GUIDELINE_v0_1`
- `AIP_WIKI_INTEGRATION_SPEC_v0_1`
- `GUIDELINE_INDEX_FLOW_NAVIGATOR_v0_1`

---

## 15. Common pitfalls
- customize quá sớm thứ đáng lẽ giữ ở common layer
- cố common hóa thứ quá project-bound
- promote task-local workaround thành project rule quá nhanh
- promote project rule thành common preset quá sớm
- không rõ layer ownership nên về sau khó maintain

---

## 16. If missing then do
Nếu chưa rõ nên xếp vào layer nào:
- giữ ở layer thấp hơn trước
- mark as tentative
- ask HUMAN confirm if impact is meaningful
- only promote upward when pattern becomes clearer

---

## 17. Completion criteria for BL-16
BL-16 is considered done when:
- preset/common vs project-specific vs task-instance boundary is clear
- default customization decision rule is clear
- human confirmation rule is clear
- promote-back rule is clear
- practical examples are clear
