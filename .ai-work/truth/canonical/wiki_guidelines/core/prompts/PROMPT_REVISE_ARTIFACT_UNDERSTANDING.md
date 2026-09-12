# PROMPT_REVISE_ARTIFACT_UNDERSTANDING_v0_1

## Purpose
Prompt mẫu để BrSE yêu cầu AI revise artifact understanding sau review.

## Prompt
Dưới đây là:
1. artifact understanding draft hiện tại
2. comment / correction / clarification của BrSE

Hãy revise artifact understanding theo các comment đó.

### Yêu cầu
1. Giữ nguyên structure understanding output nếu vẫn còn phù hợp.
2. Chỉ update những phần cần thiết theo correction/comment mới.
3. Tách rõ:
   - phần nào được xác nhận thêm từ BrSE
   - phần nào là AI inference còn giữ lại
   - phần nào vẫn unresolved
4. Nếu comment của BrSE làm thay đổi:
   - artifact type candidate
   - requirement chain position
   - reflection status understanding
   - related artifact links
   thì hãy phản ánh rõ trong bản revise.
5. Cuối cùng, cho thêm một `change summary` ngắn:
   - what was corrected
   - what was added
   - what remains unresolved

### Rule
- Không tự mở rộng suy luận ngoài những gì cần để phản ánh đúng comment của BrSE.
- Nếu comment chưa đủ rõ để revise chắc chắn, hãy giữ unresolved thay vì đoán.
