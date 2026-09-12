# SUPPLEMENTAL_ARTIFACT_STATUS_REFLECTION_MODEL_v0_1

## 1. Purpose
Tài liệu này định nghĩa model tối thiểu cho:
- `status`
- `reflection_status`
- `reflected_to`
- `reflected_at`
- `superseded_by`

áp dụng cho các **supplemental artifacts** trong sprint Wiki.

Mục tiêu là giúp AI và BrSE biết:
- artifact bổ sung đó còn active hay không
- nội dung của nó đã được phản ánh vào tài liệu chính hay chưa
- nếu đã reflected rồi thì có còn cần tham khảo trực tiếp mặc định nữa không

---

## 2. Why this model is needed
Các artifact bổ sung như:
- Q&A
- findings
- open points
- clarification notes
- review comments summary
- pending decisions

thường không chỉ mang nội dung, mà còn mang **trạng thái vận hành**.

Nếu không có model này thì AI/BrSE sẽ khó biết:
- có còn phải đọc trực tiếp artifact bổ sung đó không
- hay thông tin của nó đã được absorb vào requirement / design / testcase / tài liệu chính khác rồi

---

## 3. In-scope artifact classes

### 3.1. Primary examples
- Q&A List
- findings list
- open points list
- clarification notes
- review comments summary
- pending decisions

### 3.2. Generalization rule
Bất kỳ artifact bổ sung nào có vai trò:
- clarification
- issue tracking
- refinement trail
- supplemental decision trail

đều có thể dùng model này.

---

## 4. Foundational distinction

### 4.1. Status
Cho biết bản thân item/artifact hiện đang ở tình trạng xử lý nào.

### 4.2. Reflection status
Cho biết nội dung của item/artifact đó đã được phản ánh vào tài liệu chính liên quan hay chưa.

### 4.3. Important rule
`status` và `reflection_status` không phải lúc nào cũng giống nhau.

Ví dụ:
- một Q&A có thể đã `answered`
- nhưng vẫn `not_reflected` vào requirement definition

---

## 5. Minimal status model

## 5.1. Generic status values
Model tối thiểu nên support:

- `open`
- `answered_unapplied`
- `resolved_unapplied`
- `partially_reflected`
- `reflected`
- `superseded`
- `dropped`
- `unknown`

## 5.2. Interpretation

### `open`
- item vẫn chưa được chốt hoặc chưa có kết luận usable

### `answered_unapplied`
- đã có answer
- nhưng answer đó chưa được phản ánh vào tài liệu chính

### `resolved_unapplied`
- đã có kết luận / resolved direction
- nhưng chưa phản ánh vào tài liệu chính

### `partially_reflected`
- đã phản ánh một phần
- vẫn còn phần chưa absorb vào tài liệu chính

### `reflected`
- đã phản ánh đầy đủ vào tài liệu chính liên quan

### `superseded`
- item đã bị thay thế bởi item/tài liệu mới hơn

### `dropped`
- item không còn hiệu lực hoặc không tiếp tục theo nữa

### `unknown`
- chưa đủ thông tin để xác định trạng thái

---

## 6. Reflection status model

## 6.1. Minimal reflection_status values
- `not_reflected`
- `partially_reflected`
- `reflected`
- `unknown`

## 6.2. Meaning

### `not_reflected`
- nội dung vẫn đang tồn tại chủ yếu ở artifact bổ sung
- chưa absorb vào main artifact

### `partially_reflected`
- một phần đã absorb
- vẫn cần thận trọng vì có thể còn phần chưa đi vào tài liệu chính

### `reflected`
- nội dung đã được absorb đủ vào tài liệu chính liên quan

### `unknown`
- chưa xác định được rõ đã absorb hay chưa

---

## 7. Required companion fields

### 7.1. reflected_to
Danh sách tài liệu hoặc object mà nội dung đã được phản ánh vào.

Ví dụ:
- `REQ_DEF_v2`
- `BD_F04_v1`
- `DD_F04_v3`
- `ITTC_Search_v2`

### 7.2. reflected_at
Thông tin thời điểm / version / revision note nếu có.

Không bắt buộc phải có timestamp chính xác trong sprint này, nhưng nên support ít nhất:
- version note
- revision note
- rough update reference

### 7.3. superseded_by
Nếu item bị thay thế, nên chỉ ra:
- item nào thay thế
- artifact nào mới hơn thay thế

### 7.4. reflection_note
Ghi chú ngắn để giải thích:
- tại sao được coi là reflected / partially reflected
- phần nào đã absorb
- phần nào chưa

---

## 8. Usage rule for downstream tasks

## 8.1. If status is `open`
AI/BrSE nên coi item là active supplemental knowledge và nên tham khảo trực tiếp nếu task liên quan.

## 8.2. If status is `answered_unapplied` or `resolved_unapplied`
AI/BrSE vẫn nên ưu tiên đọc trực tiếp, vì main artifact có thể chưa phản ánh nội dung đó.

## 8.3. If status is `partially_reflected`
AI/BrSE nên thận trọng:
- có thể cần đọc cả main artifact lẫn supplemental artifact

## 8.4. If status is `reflected`
AI/BrSE không cần mặc định đọc trực tiếp item đó nữa,
trừ khi:
- cần trace / audit
- cần kiểm chứng xem main artifact đã phản ánh đúng chưa
- task yêu cầu đối chiếu lịch sử

## 8.5. If status is `superseded`
AI/BrSE nên ưu tiên item/artifact thay thế nếu đã biết.

---

## 9. Q&A-specific notes

### 9.1. Q&A is not just a log
Q&A là lớp refinement quan trọng giữa:
- raw requirement
- refined requirement definition

### 9.2. Reflection-aware usage
Nếu một Q&A đã `reflected` vào requirement definition,
thì về sau task có thể không cần mặc định đọc trực tiếp Q&A đó nữa.

### 9.3. But keep traceability
Ngay cả khi reflected, Q&A vẫn có thể còn giá trị cho:
- trace
- audit
- disagreement resolution
- requirement evolution understanding

---

## 10. Findings / Open Points-specific notes

### 10.1. Findings
Một finding có thể:
- vẫn open
- resolved but unapplied
- reflected into DD/BD/testcase
- superseded by a newer revision

### 10.2. Open points
Một open point có thể:
- later become answered
- later become reflected
- later become dropped
- later become superseded

### 10.3. Rule
Do not assume that “resolved” automatically means “reflected”.

---

## 11. Minimal schema

```yaml
supplemental_item_id: SA-<id>
supplemental_type: <qa | finding | open_point | clarification_note | review_comment_summary | pending_decision | other>

status: <open | answered_unapplied | resolved_unapplied | partially_reflected | reflected | superseded | dropped | unknown>
status_note: <string>

reflection_status: <not_reflected | partially_reflected | reflected | unknown>
reflected_to:
  - <artifact ref>
reflected_at: <optional string>
superseded_by:
  - <artifact ref or item ref>
reflection_note: <string>

future_usage_note:
  direct_consultation_still_needed_by_default: <yes | no | maybe>
  reason: <string>
```

---

## 12. Integration points in this sprint

This model should be reused by:
- `ARTIFACT_UNDERSTANDING_SPEC`
- `WIKI_ARTIFACT_PROFILE_SPEC`
- `WIKI_USAGE_PROFILE_SPEC`
- `WIKI_META_INDEX_SPEC`
- `AIP_WIKI_INTEGRATION_SPEC`

---

## 13. Out of scope for this sprint
- advanced lifecycle automation
- automatic reflection detection across many artifacts
- status transition engine
- approval workflow engine
- visual dashboards for status/reflection tracking

---

## 14. Completion criteria for BL-02
BL-02 is considered done when:
- status model is clearly defined
- reflection_status model is clearly defined
- required companion fields are clearly defined
- downstream usage implications are clearly defined
- Q&A and other supplemental artifacts are explicitly covered
