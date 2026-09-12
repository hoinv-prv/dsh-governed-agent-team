# PROMPT_REVISE_AIP_TEMPLATE_CUSTOMIZATION_v0_1

## Purpose
Prompt mẫu để revise AIP template customization sau khi BrSE review.

## Prompt
Dưới đây là:
1. customized AIP template hiện tại
2. comment / correction / additional rules từ BrSE

Hãy revise template customization theo các comment đó.

### Yêu cầu
1. Chỉ update những phần cần thiết.
2. Tách rõ:
   - what was confirmed by BrSE
   - what was changed
   - what remains project-pending
3. Update lại nếu cần:
   - knowledge behavior
   - wiki handoff behavior
   - completion criteria
   - project reuse note
4. Thêm change_summary ngắn:
   - what was corrected
   - what was added
   - what remains open

### Rule rất quan trọng
- Không tự thêm complexity không được BrSE yêu cầu.
- Nếu comment của BrSE thay đổi deliverable/wiki-eligible/governance behavior, phải phản ánh rõ vào template wording.
