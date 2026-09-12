# AIP_TEMPLATE_CUSTOMIZATION_GUIDELINE_v0_1

## 1. Purpose
Guideline này hướng dẫn cách AI và BrSE:
- chọn preset AIP template phù hợp
- customize template đó cho project thực tế
- phản ánh đúng:
  - Task Lens
  - Wiki / Knowledge Hub usage
  - project profile
  - deliverable vs working artifact
  - wiki-eligible vs not
  - candidate / CR / governance handoff
- giữ AIP đủ usable ngay, nhưng không over-design quá sớm

## 2. What this guideline is for
Guideline này dùng khi cần:
- tạo AIP template dùng cho project mới
- customize preset AIP template theo project rule
- điều chỉnh AIP template sau khi hiểu rõ hơn về artifact structure / wiki behavior / project profile
- thêm minimal Wiki-first behavior vào AIP template

Guideline này không phải:
- hướng dẫn runtime retrieval chi tiết
- guideline build meta/index trực tiếp
- governance rule

## 3. Foundational principles

### 3.1. Start from preset, then customize
Mặc định nên:
- chọn preset AIP template gần nhất
- rồi customize theo project
thay vì viết template hoàn toàn từ zero trong mọi trường hợp.

### 3.2. AIP should stay execution-oriented
AIP template phải giúp AI/HUMAN thực hiện task,
không nên biến thành tài liệu policy quá nặng.

### 3.3. Task Lens stays separate
AIP template có thể reference:
- related lens
- lens hint
nhưng không nên nhồi full retrieval logic vào template.

### 3.4. Wiki-first does not mean source-never
AIP template nên ưu tiên:
- current context / notebook
- Wiki Meta / Index
- linked artifacts
- source/raw deeper reading when needed

AIP không được giả định rằng Wiki luôn đủ.

### 3.5. Project profile must shape the template
AIP template customization phải phản ánh:
- deliverable vs working artifact
- wiki-eligible vs not
- project-specific artifact classes
- project-specific search/review priorities

### 3.6. Add-to-wiki handoff is not direct publish
Nếu template có add-to-wiki step,
step đó là:
- candidate / CR / governance handoff
không phải direct canonical update bypass governance.

## 4. Main inputs for AIP template customization
Một flow tốt nên dùng một phần hoặc nhiều phần sau:
- preset AIP template
- task intent / use case
- project profile
- Task Lens or lens hint
- known artifact classes
- Wiki Meta / Index expectations
- project mapping pattern
- governance expectations
- BrSE-specific review or customization needs

## 5. Recommended customization flow

### Step 1 — Select nearest preset
AI xác định preset gần nhất theo:
- task type
- output type
- artifact family
- review/create/clarify/report nature

### Step 2 — Confirm task understanding
AI tóm tắt ngắn:
- task là gì
- output mong muốn là gì
- major artifact classes liên quan là gì
rồi HUMAN confirm.

### Step 3 — Apply project profile constraints
AI customize template theo:
- deliverable vs working artifact
- wiki-eligible vs not
- required handoff expectations
- project-specific artifact naming/classification

### Step 4 — Apply knowledge behavior
AI thêm vào template các phần phù hợp như:
- recommended knowledge to load
- lens hint
- wiki dependency note
- if wiki is insufficient then
- linked artifact escalation note

### Step 5 — Apply output and handoff behavior
AI thêm / chỉnh:
- expected outputs
- review checkpoints
- candidate suggestion note
- add-to-wiki handoff note if relevant
- what counts as completion

### Step 6 — HUMAN review and correction
HUMAN có thể:
- chỉnh scope
- thêm step
- bớt step
- tăng/giảm mức wiki integration
- thay đổi required handoff behavior

### Step 7 — Save project-customized template rule
Nếu template có giá trị dùng lại,
AI nên tạo reusable project-specific template note/rule.

## 6. What parts of an AIP template are usually customizable
- task summary / intent framing
- knowledge loading hints
- work steps
- output structure
- wiki handoff behavior
- completion criteria

## 7. Minimal Wiki-first customization points
Khi customize AIP cho project có Wiki/Knowledge Hub,
template nên cân nhắc thêm tối thiểu:
- related_task_lens_or_lens_hint
- recommended_knowledge_to_load
- wiki_dependency_note
- if_wiki_is_insufficient_then
- wiki_candidate_suggestion_note
- artifact_publication_rule_note
- governance_handoff_note

## 8. Deliverable / working artifact rule in template customization
### 8.1. Deliverable-producing templates
Nếu template tạo artifact loại deliverable,
AI nên check project profile xem artifact đó:
- có wiki-eligible không
- có cần add-to-wiki suggestion không

### 8.2. Working-only templates
Nếu output chỉ là:
- working draft
- local note
- temporary scratch
- private intermediate artifact
thì template thường không nên có add-to-wiki step mặc định.

### 8.3. Rule
Không biến mọi AIP template thành template có add-to-wiki step,
chỉ vì project có Wiki.

## 9. Candidate / CR / governance handoff rule
Nếu template nên hỗ trợ Wiki integration,
thì wording phải rõ:
- candidate suggestion
- CR preparation / handoff
- wiki manager / governance path

Template không nên mô tả sai thành:
- direct canonical publish

## 10. Suggested reusable template layers
- preset layer
- project-customized layer
- task-instance layer

### Rule
Nên giữ ba layer này tách tương đối rõ để giảm confusion khi bảo trì template.

## 11. Suggested output structure for customization result
Một kết quả customize tốt nên có:
- selected_preset_template
- customization_summary
- project_constraints_applied
- knowledge_behavior_updates
- wiki_handoff_behavior
- completion_criteria_updates
- project_reuse_note

## 12. Minimal review questions
1. Preset này có đúng task type không?
2. Knowledge loading hints đã đủ chưa?
3. Wiki-first behavior có vừa đủ, không quá nặng không?
4. Deliverable vs working distinction đã đúng chưa?
5. Add-to-wiki handoff có bị gắn sai chỗ không?
6. Completion criteria có thực dụng không?

## 13. Common pitfalls
- customize từ zero dù đã có preset gần đúng
- nhét full retrieval logic của Task Lens vào AIP template
- ép mọi template phải có add-to-wiki step
- quên project profile constraints
- wording làm hiểu nhầm candidate = canonical publish
- completion criteria quá nặng khiến AIP khó dùng

## 14. If missing then do
Nếu chưa đủ thông tin để customize mạnh:
- chọn preset gần nhất
- giữ template ở mức conservative
- mark project-specific part as pending customization
- xin HUMAN confirm các decision points quan trọng
- avoid overcommitting to wiki behavior not yet confirmed

## 15. Completion criteria for BL-13
BL-13 is considered done when:
- preset-first customization flow is clear
- project profile interaction is clear
- minimal Wiki-first customization points are clear
- deliverable vs working handling is clear
- candidate/CR/governance handoff wording is clear
- reusable template layering is clear
