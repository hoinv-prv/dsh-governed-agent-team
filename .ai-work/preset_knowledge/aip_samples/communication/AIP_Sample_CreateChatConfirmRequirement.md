# AIP_Sample_CreateChatConfirmRequirement_v1.md

**Version:** v1.0
**Date:** 2026-04-16
**Target Task:** Create chat message to confirm requirements with customer during software development
**Primary AIP Type:** PLAN AIP
**Required Flow Additions:** Input understandings trước khi soạn, review viewpoint + self review trước khi gửi

---

## 1. Rule bắt buộc cho task này

Từ nay, flow cho task **Soạn chat confirm yêu cầu với KH** phải có:

1. **Input understandings**
   - AI phải output ra:
     - current understanding về yêu cầu / thay đổi cần confirm qua chat
     - grouped open points (những điểm chưa rõ hoặc cần KH xác nhận)
     - expected answer types (confirm / reject / partial / cần thêm info)
     - downstream impact understanding (nếu KH confirm/reject thì ảnh hưởng gì tới development)
   - BrSE confirm AI đã hiểu đúng context trước khi soạn nội dung chat

2. **Review viewpoint + self review**
   - Trước khi gửi chat, phải tự review:
     - nội dung có đúng yêu cầu cần confirm không
     - câu hỏi / mục confirm có được nhóm logic không (không hỏi dàn trải)
     - tone có phù hợp chat (ngắn gọn, rõ ràng, không ambiguous) không
     - next action sau khi nhận reply có rõ không

---

## 2. Objective

- Soạn nội dung chat confirm yêu cầu với KH một cách súc tích, đúng trọng tâm, dễ reply ngay
- Output input understandings để BrSE confirm trước khi gửi chat
- Dùng review viewpoint để self-review nội dung trước khi finalize

---

## 3. Đặc điểm riêng của Chat (so với Mail)

| Khía cạnh | Chat |
|---|---|
| Độ dài | Ngắn — tối đa 3–5 điểm hỏi mỗi lần |
| Tone | Informal / working level — vẫn lịch sự nhưng direct |
| Grouping | Hỏi từng nhóm nhỏ, không dump toàn bộ open points |
| Reply speed | Kỳ vọng reply nhanh (same day / trong giờ làm) |
| Thread | Có thể hỏi nhiều lần — dùng thread / reply để giữ context |
| Follow-up | Log lại trong issue / spec sau khi có reply |

---

## 4. Input Understandings

### 4.1 Output bắt buộc trước khi soạn chat

- understanding summary về yêu cầu / change request cần confirm
- grouped open points: ưu tiên những điểm **block development ngay** — chỉ hỏi những gì cần thiết trong lần này
- expected answer types: mỗi điểm cần KH trả lời dạng gì (confirm / clarify / decide)
- downstream impact: nếu KH confirm / từ chối thì bước tiếp theo là gì

### 4.2 BrSE Confirmation Rule

- BrSE phải confirm working-level understanding trước khi nội dung chat được gửi

---

## 5. Q&A bổ sung

- Điểm nào đang block development và cần confirm qua chat ngay?
- Có điểm nào có thể defer sang mail formal không?
- KH thường online lúc nào và dùng chat channel nào (Chatwork / Teams / Slack)?
- Sau khi KH reply chat, cần update artifact nào ngay?

---

## 6. Review Viewpoint

Review viewpoint cho task này nên tự kiểm:

- nội dung có đúng những điểm cần confirm trong lần này không (không hỏi thừa)
- câu hỏi có ngắn gọn, rõ ràng, KH có thể reply ngay không
- tone có phù hợp chat (không quá formal, không quá informal) không
- nếu có nhiều điểm → đã nhóm hợp lý chưa, ưu tiên block-first chưa
- có ghi rõ "reply nhanh sẽ giúp unblock phần này" nếu cần urgency không

---

## 7. Template bổ sung

### Metadata bổ sung

- Điểm cần confirm qua chat:
- Chat channel:
- Blocking items (cần reply ngay):
- Input Understanding Status:
- Review Viewpoint Status:

### Section bổ sung

#### Input Understanding and BrSE Confirmation

- understanding summary
- grouped open points (ưu tiên block-first)
- expected answer types
- downstream impact
- BrSE confirmation

#### Review Viewpoint / Self Review

- review items checklist
- self-review result
- remaining concern trước khi gửi

---

## 8. Sample flow

1. Nhận yêu cầu / issue / change request cần confirm qua chat
2. Read source documents + chat thread liên quan
3. Output input understandings (theo mục 4.1)
4. BrSE confirm understandings ở mức working level
5. Soạn nội dung chat — ngắn gọn, grouped, block-first
6. Tạo review viewpoint và self-review
7. BrSE approve nội dung (nếu có impact lớn)
8. Gửi chat
9. Track reply và update downstream artifacts (issue / spec / design)

---

## PLAN-to-EXEC linkage

### Linked / Recommended EXEC AIP

AIP_EXEC_CreateChatConfirmRequirement.md

### Why EXEC should follow this PLAN

Thực thi soạn và gửi chat confirm — sau khi PLAN đã xác nhận understandings và grouped open points đã rõ

### Outputs from this PLAN that EXEC should inherit

- grouped open points (block-first) đã confirmed
- expected answer types cho từng điểm
- chat channel / receiver đã xác định
- approved tone direction

### EXEC entry conditions

- điểm cần confirm đã grouped rõ và ưu tiên block-first
- receiver / chat channel đã xác định
- BrSE đã confirm key understandings

### When NOT to create EXEC yet

- không tạo EXEC nếu điểm cần confirm vẫn unstable
- không tạo EXEC nếu BrSE chưa confirm key understandings
- không tạo EXEC nếu chưa rõ channel / receiver

### Handoff checklist from PLAN to EXEC

- [ ] PLAN objective và scope đã stable
- [ ] grouped open points đã visible và reusable
- [ ] open points / assumptions carried forward đã explicit
- [ ] review viewpoint source cho EXEC đã xác định
- [ ] BrSE đồng ý execution có thể bắt đầu an toàn

### Rule if no PLAN exists

- Nếu không có PLAN AIP **nhưng inputs đã đủ rõ và đây là confirm nhỏ**, có thể tạo EXEC trực tiếp.
- Nếu không có PLAN AIP **và có nhiều điểm cần làm rõ trước**, tạo PLAN trước.

### Trace note for AI / BrSE

Khi tạo EXEC từ PLAN này, AI nên đọc / hỏi:
1. Outputs nào của PLAN này đã được confirmed?
2. Open points nào vẫn còn live và phải carry vào EXEC?
3. Điểm nào nên hỏi qua chat lần này, điểm nào defer?
4. Completion condition nào của PLAN này trở thành entry condition của EXEC?
