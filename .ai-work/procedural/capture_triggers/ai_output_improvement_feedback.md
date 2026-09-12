# ai_output_improvement_feedback — HUMAN feedback về chất lượng output AI
- **type:** guideline_improvement_candidate · **suggested_target:** guideline · **timing:** ⚡immediate
## When
**Mọi lần HUMAN sửa output** — không chỉ khi reject kèm lý do (CR-AIWS-2026-08-126 C8).
Ngưỡng cũ hẹp đến mức cả corpus chỉ có **2 record** cho cả lớp này; đó là lỗi cách viết trigger,
không phải bằng chứng lớp này hiếm. Một sửa chữa im lặng — HUMAN viết lại một đoạn rồi đi tiếp —
mang đúng lượng thông tin như một lời chê có giải thích.

Ba nguồn, cả ba đều capture:
1. **HUMAN sửa / reject / đề xuất hướng khác** cho một output (nguồn cũ).
2. **Recurring non-PASS trong `06_runtime_review_checklist.md`** — cùng một lớp finding xuất hiện **hai lần**.
   Lần thứ hai không còn là sự cố, nó là một pattern.
3. **Diff `07_output_draft.md` → `11_output_final.md` lúc accept** — thứ *thực sự* đã phải đổi.
   *Đo được 2026-08-27: **228/372** workspace vẫn giữ nguyên file final-output mẫu, nên hôm nay
   nguồn này vô hình ở phần lớn task. Đó là lý do nó được nêu ra đây, không phải lý do để bỏ.*
## Capture as
**Family (CR-AIWS-2026-08-126 C1):** `output_quality_feedback` — tên trigger `ai_output_improvement_feedback` giữ làm nhãn **capture-time**; giá trị ghi vào `candidate_kind` là `output_quality_feedback`. `improvement_scope` mặc định: `project`.

candidate_kind: `output_quality_feedback` (giá trị cũ `ai_output_improvement_feedback` vẫn hợp lệ trên record đã có; record MỚI dùng tên mới). Bắt buộc `improvement_scope`; thêm `correction_class` để đếm được kiểu sai:
`missing_section` · `wrong_format` · `wrong_approach` · `factual_error` · `scope`.
Phải include nguyên văn feedback của HUMAN trong `content` (hoặc đoạn diff, với nguồn 2/3). Chọn `type` theo bản chất gap:
- `guideline_improvement_candidate` → feedback chỉ ra quy tắc/hướng dẫn chung cần cải thiện (mặc định phổ biến).
- `run_aip_improvement_candidate` → vấn đề nằm ở cách thực thi AIP / quy trình run.
- `aip_template_improvement_candidate` → template AIP cần bổ sung/sửa.
- `notebook_note_candidate` → quan sát rời rạc, chưa đủ thành đề xuất canonical → để notebook.
## Suggested action
Review tại AIP close, gom recurring patterns qua các interaction, rồi propose cải thiện skill/guideline/template tương ứng (qua CR nếu chạm canonical product).
## Example
HUMAN: "Output thiếu acceptance criteria và dùng sai format bảng — lần sau bám template" → capture `guideline_improvement_candidate` kèm nguyên văn feedback.
## Notes
TIMING RULE: capture ngay khi feedback được đưa ra (⚡immediate), không đợi cuối step.
