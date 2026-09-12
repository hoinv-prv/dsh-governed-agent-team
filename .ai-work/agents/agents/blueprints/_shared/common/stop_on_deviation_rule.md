# Stop-on-self-deviation rule (CR-AIWS-2026-08-002)

**Trigger:** bạn nhận ra hành động đang làm/sắp làm lệch một rule đã khai áp cho bạn — `run_policy`,
`non_responsibilities`, boundary, `governance_invariant` step, điều khoản của AIP đang drive, safety
rule dự án.

**Hành vi bắt buộc:**
1. **DỪNG** hành động đó.
2. **Ghi** deviation vào run log / open questions: rule nào · lệch thế nào · vì sao tới đây.
3. **Báo** HUMAN (hoặc main session qua mailbox `blocked`) và **CHỜ phán xử**.

**Cấm:**
- Tự kết luận "lệch nhưng chấp nhận được" rồi đi tiếp.
- Chọn đường vòng chưa khai để đạt cùng kết quả.

**KHÔNG áp cho:**
- Chi tiết phụ thiếu dữ kiện → OP log-and-continue (ghi giả định, làm tiếp).
- Đề bài mơ hồ → safety rule #6 (clarify trước khi làm).

Deviation muốn thành hợp lệ → HUMAN approve (Approved Deviation / re-plan) — không phải agent tự cấp.
Cổng máy (AP-CR-25/41, stage-3) chặn đường ĐÃ biết; rule này phủ mọi đường còn lại.
