# AIP_Sample_CreateMailConfirmRequirement_v1.md

**Version:** v1.0
**Date:** 2026-04-16
**Target Task:** Create email to confirm requirements with customer during software development
**Primary AIP Type:** PLAN AIP
**Required Flow Additions:** Input understandings trước khi soạn, review viewpoint + self review trước khi gửi

---

## 1. Rule bắt buộc cho task này

Từ nay, flow cho task **Soạn mail confirm yêu cầu với KH** phải có:

1. **Input understandings**
   - AI phải output ra:
     - current understanding về yêu cầu / thay đổi cần confirm qua mail
     - grouped open points (những điểm chưa rõ hoặc cần KH xác nhận chính thức)
     - expected answer types (confirm / reject / partial / cần thêm info)
     - downstream impact understanding (nếu KH confirm/reject thì ảnh hưởng gì tới development / design)
   - BrSE confirm AI đã hiểu đúng context trước khi soạn draft mail

2. **Review viewpoint + self review**
   - Trước khi gửi mail, phải tự review:
     - nội dung có đúng yêu cầu cần confirm không
     - câu hỏi / mục confirm có được nhóm logic không
     - tone / wording có phù hợp mail chính thức gửi KH Nhật không
     - subject line có rõ mục đích không
     - next action sau khi nhận reply có rõ không

---

## 2. Objective

- Soạn mail confirm yêu cầu với KH một cách có cấu trúc, chính thức, dễ đọc và dễ reply
- Output input understandings để BrSE confirm trước khi soạn draft
- Dùng review viewpoint để self-review draft trước khi finalize và gửi

---

## 3. Đặc điểm riêng của Mail (so với Chat)

| Khía cạnh | Mail |
|---|---|
| Độ dài | Đầy đủ — có thể cover nhiều điểm, nhưng phải có cấu trúc rõ |
| Tone | Formal / polite — phù hợp mail chính thức KH Nhật |
| Grouping | Group tất cả open points liên quan vào một mail — tránh gửi nhiều mail nhỏ |
| Reply speed | Kỳ vọng reply trong 1–3 ngày làm việc |
| Thread | Dùng reply-to-thread để giữ context trong chuỗi mail |
| Follow-up | Log lại trong spec / design document sau khi có reply |
| Subject | Subject rõ ràng: "【確認依頼】〇〇について" |

---

## 4. Input Understandings

### 4.1 Output bắt buộc trước khi soạn mail

- understanding summary về yêu cầu / change request / specification cần confirm chính thức
- grouped open points: tất cả điểm cần KH confirm trong lần gửi này — phân loại theo topic/feature
- expected answer types: mỗi điểm cần KH trả lời dạng gì (confirm / clarify / decide / approve)
- downstream impact: nếu KH confirm / từ chối từng điểm thì development / design ảnh hưởng thế nào
- assumptions hiện tại đang dùng để tiếp tục development (nếu chưa có reply)

### 4.2 BrSE Confirmation Rule

- BrSE phải confirm working-level understanding trước khi draft mail được coi là valid để gửi KH
- BrSE phải approve nội dung mail cuối cùng trước khi gửi

---

## 5. Q&A bổ sung

- Yêu cầu / thay đổi cần confirm là gì? Source document là gì?
- Điểm nào đang block development nếu chưa được KH confirm?
- KH có expectation gì về timeline reply?
- Subject line nên viết thế nào (hỏi BrSE về format tiêu chuẩn)?
- Sau khi KH reply, output tiếp theo là gì (update spec / update design / start coding)?
- Có điểm nào nên hỏi qua chat trước để unblock nhanh không?

---

## 6. Review Viewpoint

Review viewpoint cho task này nên tự kiểm:

- subject line có rõ mục đích mail không (confirm / clarify / approval)
- greeting / opening có phù hợp KH Nhật không
- nội dung có đúng yêu cầu / change request cần confirm không
- các điểm confirm có grouped theo logic (feature / screen / flow / priority) không
- expected answer type cho từng điểm có rõ không
- hiện tại đang assume gì nếu chưa có reply — có ghi rõ không
- tone / wording có phù hợp mail chính thức KH Nhật không (lịch sự, trực tiếp, không ambiguous)
- có ghi rõ deadline mong muốn nhận reply không
- closing / next action sau khi nhận reply có rõ không

---

## 7. Template bổ sung

### Metadata bổ sung

- Yêu cầu / change request cần confirm:
- Source document:
- Blocking items:
- Expected reply deadline:
- Input Understanding Status:
- Review Viewpoint Status:

### Section bổ sung

#### Input Understanding and BrSE Confirmation

- understanding summary
- grouped open points (phân loại theo topic)
- expected answer types
- downstream impact
- current assumptions nếu chưa có reply
- BrSE confirmation

#### Review Viewpoint / Self Review

- review items checklist
- self-review result
- remaining concern trước khi gửi

---

## 8. Sample flow

1. Nhận yêu cầu / change request / specification cần confirm chính thức qua mail
2. Read source documents + mail thread liên quan
3. Output input understandings (theo mục 4.1)
4. BrSE confirm understandings ở mức working level
5. Soạn draft mail — có cấu trúc, grouped theo topic, mỗi điểm có expected answer type rõ
6. Tạo review viewpoint và self-review draft
7. BrSE review và approve trước khi gửi KH
8. Gửi mail, log ngày gửi + expected reply date
9. Track reply và update downstream artifacts (spec / design / issue)

---

## PLAN-to-EXEC linkage

### Linked / Recommended EXEC AIP

AIP_EXEC_CreateMailConfirmRequirement.md

### Why EXEC should follow this PLAN

Thực thi soạn và gửi mail confirm chính thức — sau khi PLAN đã xác nhận understandings và tất cả grouped open points đã được BrSE approve

### Outputs from this PLAN that EXEC should inherit

- grouped open points đã confirmed (phân loại theo topic)
- expected answer types cho từng điểm
- current assumptions nếu chưa có reply
- downstream impact understanding
- approved wording direction và tone
- expected reply deadline

### EXEC entry conditions

- yêu cầu / change request đã được grouped rõ theo topic
- receiver / KH contact đã xác định
- không còn major ambiguity về những gì cần confirm trong lần gửi này
- BrSE đã confirm key understandings và approve nội dung

### When NOT to create EXEC yet

- không tạo EXEC nếu PLAN outputs trên vẫn unstable
- không tạo EXEC nếu BrSE chưa confirm key understandings
- không tạo EXEC nếu danh sách điểm cần confirm vẫn đang thay đổi
- không tạo EXEC nếu chưa rõ subject / tone / language policy

### Handoff checklist from PLAN to EXEC

- [ ] PLAN objective và scope đã stable
- [ ] grouped open points đã visible và reusable
- [ ] open points / assumptions carried forward đã explicit
- [ ] review viewpoint source cho EXEC đã xác định
- [ ] BrSE đồng ý execution có thể bắt đầu an toàn

### Rule if no PLAN exists

- Nếu không có PLAN AIP **nhưng inputs đã đủ rõ**, có thể tạo EXEC trực tiếp.
- Nếu không có PLAN AIP **và inputs chưa rõ**, tạo PLAN trước, sau đó derive EXEC từ PLAN outputs.

### Trace note for AI / BrSE

Khi tạo EXEC từ PLAN này, AI nên đọc / hỏi:
1. Outputs nào của PLAN này đã được confirmed?
2. Open points nào vẫn còn live và phải carry vào EXEC?
3. Review viewpoint hoặc checklist nào EXEC nên reuse?
4. Completion condition nào của PLAN này trở thành entry condition của EXEC?
