# WIKI_SOURCE_ROLE_POLICY_MVP
Version: 0.1  
Status: Policy baseline  
Scope: MVP only
## Terminology note
Trong AI Work System:
- **Knowledge Hub** là tên chính thức của component
- **Wiki** là tên vắn tắt vẫn được dùng bên trong hệ thống để chỉ Knowledge Hub


---

# 1. Purpose

Tài liệu này chốt policy cho việc đưa **source working** và **source legacy** vào Knowledge Hub / Wiki system của AI Work System MVP.

Mục tiêu:
- đưa cả 2 loại source vào cùng một source-side model
- phân vai rõ ràng giữa current working source và historical/reference source
- không cần redesign core AI Work System
- vẫn giữ hệ extendable cho các phase sau

---

# 2. Core decision

## 2.1. Both source sets should be included
Cả **source working** và **source legacy** đều nên được đưa vào Knowledge Hub / Wiki system.

## 2.2. But they should live in the source-side layer
Chúng không được đổ thẳng thành curated wiki.

Thay vào đó, chúng đi vào source-side model gồm:
- `Wiki Source Artifact`
- `Wiki Source Meta (Knowledge Hub source meta)`
- `Wiki Source Index (Knowledge Hub source index)`
- `Source Interpretation Profile`

## 2.3. No separate concept system is needed
Không cần tạo một hệ model khác cho working và legacy.
Chỉ cần dùng cùng model nhưng khác:
- `source_role`
- `source_use_rule`
- relation semantics
- reading priority

---

# 3. Source role model

## 3.1. source_role
Mỗi source-side object nên có field:

- `source_role: working | legacy`

### working
Source đang phục vụ implementation hiện tại / công việc hiện tại.

### legacy
Source cũ, dùng để:
- tra cứu
- so sánh
- reverse engineer
- tìm rationale/history
- hỗ trợ migration or understanding gaps

---

# 4. Source use rule model

## 4.1. source_use_rule
Khuyến nghị dùng một field:

- `source_use_rule`

Recommended values:
- `primary_for_current_work`
- `reference_only`
- `compare_when_needed`

## 4.2. Recommended mapping
### For working source
- `source_role: working`
- `source_use_rule: primary_for_current_work`

### For legacy source
- `source_role: legacy`
- `source_use_rule: reference_only`
or
- `source_use_rule: compare_when_needed`

---

# 5. Reading priority rule

## 5.1. For current active work
Khi task là công việc implementation / review / investigation hiện tại, AI nên ưu tiên:

1. Truth liên quan
2. Working source-side objects
3. Existing curated wiki
4. Legacy source-side objects khi cần đối chiếu hoặc bổ sung context
5. History

## 5.2. Meaning
Legacy source không nên mặc định chen lên trước current working source khi task đang xử lý implementation hiện tại.

---

# 6. Working vs legacy relation semantics

## 6.1. Recommended relation types
Giữa working và legacy source, có thể dùng một số relation types như:

- `legacy_of`
- `working_successor_of`
- `compare_with`
- `same_function_different_generation`
- `migration_related`

## 6.2. Why these relations matter
Các relation này giúp AI:
- tìm source legacy tương ứng khi đang ở source working
- chỉ mở legacy khi thật sự cần compare
- tránh dùng legacy như source mặc định cho current behavior

---

# 7. What working source should be used for

Working source nên là nguồn chính để:
- hiểu implementation hiện tại
- verify current behavior
- điều tra impact
- build/update module/function/data wiki
- trace exact identifiers in current code/docs
- support working tasks directly

Working source không tự động trở thành curated wiki.
Nó chỉ là source-side input chính.

---

# 8. What legacy source should be used for

Legacy source nên dùng cho:
- historical context
- compare old/new behavior
- migration analysis
- terminology lookup
- reverse engineering when current source is incomplete
- supporting reference notes and compare-oriented wiki drafts

Legacy source không nên mặc định được dùng để assert current implementation truth.

---

# 9. Storage / modeling recommendation

## 9.1. Same model, different role fields
Cả working và legacy source nên dùng chung:
- `Wiki Source Artifact`
- `Wiki Source Meta (Knowledge Hub source meta)`
- `Wiki Source Index (Knowledge Hub source index)`

Điểm khác nhau nằm ở field:
- `source_role`
- `source_use_rule`
- relation refs
- priority in reading logic

## 9.2. Optional physical separation
Có thể tách physical folders nếu tiện vận hành, ví dụ:
- `sources/working/...`
- `sources/legacy/...`

Nhưng đó là physical organization, không phải concept split bắt buộc.

---

# 10. Extendability note

Policy này được thiết kế để:
- giữ nguyên core design của Wiki v1.0
- chỉ refine source-side contract
- cho phép thêm source categories khác sau này mà không phải redesign

Ví dụ future source roles có thể có:
- `reference`
- `external`
- `vendor`

Nhưng MVP chỉ cần:
- `working`
- `legacy`

---

# 11. Freeze statement

In MVP:
- both working source and legacy source belong in the Knowledge Hub / Wiki system
- both should be modeled in the same source-side framework
- working source should be the default primary source for current work
- legacy source should be used as reference or comparison source
- role, use-rule, and relation semantics are the key differentiators