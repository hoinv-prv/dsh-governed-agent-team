# PROMPT_REVIEW_CONFIRM_MAPPING_AND_META_v0_1

## Purpose
Prompt mẫu để HUMAN/BrSE review proposal của AI rồi yêu cầu AI finalize reusable mapping và project-specific meta rule.

## Prompt
Dưới đây là:
1. canonical slot mapping proposal của AI
2. comment / correction / additional meta requirements từ BrSE

Hãy revise proposal và tạo bản cập nhật dùng được cho project.

### Yêu cầu
1. Update lại:
   - `recognized_canonical_slots`
   - `source_to_slot_mapping`
   - `important_missing_slots`
2. Merge các yêu cầu từ BrSE vào:
   - `project_customized_meta_fields`
   - `project_customized_relation_fields`
   - `project_customized_index_search_fields`
3. Tạo hoặc update:
   - `project_mapping_pattern`
4. Tách rõ:
   - phần đã được HUMAN confirm
   - phần AI vẫn đang infer
   - phần còn unresolved
5. Thêm `change_summary` ngắn:
   - what was confirmed
   - what was corrected
   - what metadata was added
   - what remains unresolved

### Rule
- Không tự thêm enrichment ngoài phạm vi comment của BrSE nếu không thực sự cần.
- Nếu project format vẫn chưa đủ rõ, giữ reusable mapping ở mức cautious thay vì over-claim.
