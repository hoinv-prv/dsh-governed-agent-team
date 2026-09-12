# PROMPT_ARTIFACT_UNDERSTANDING_v0_1

## Purpose
Prompt mẫu để AI tạo first-pass artifact understanding.

## Prompt
Hãy thực hiện **Artifact Understanding** cho artifact dưới đây theo rule của AI Work System.

### Yêu cầu
1. Xác định artifact family và artifact type candidate.
2. Mô tả artifact role understanding:
   - artifact này dùng để làm gì
   - có vẻ nằm ở đâu trong flow dự án
   - likely upstream/downstream artifacts là gì
3. Mô tả structure/template understanding:
   - template shape
   - major sections
   - section mapping notes nếu có
4. Extract key objects and terms:
   - function / screen / batch / API / table / business rule / aliases nếu có
5. Nêu related artifacts and links:
   - explicit refs
   - inferred likely refs
   - traceability hints
6. Tách riêng rõ:
   - confirmed_from_artifact
   - ai_inference
   - unresolved_or_needs_confirmation
7. Nêu suggested_followup_actions nếu cần.

### Rule rất quan trọng
- Không được trộn AI inference vào confirmed findings.
- Nếu là requirement-side artifact, phải phân biệt rõ:
  - raw requirement
  - Q&A clarification
  - requirement definition
- Nếu là supplemental artifact như Q&A/findings/open points..., hãy thêm:
  - current status understanding
  - reflection status understanding
  - reflected target docs understanding
  - whether direct future consultation is still needed by default
- Nếu chưa chắc, hãy để unresolved thay vì đoán mạnh.

### Output style
Hãy output theo structure rõ ràng, review-friendly, để BrSE có thể sửa trực tiếp.
