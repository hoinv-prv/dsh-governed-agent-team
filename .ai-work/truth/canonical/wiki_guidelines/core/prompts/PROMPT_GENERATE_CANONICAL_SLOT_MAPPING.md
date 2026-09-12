# PROMPT_GENERATE_CANONICAL_SLOT_MAPPING_v0_1

## Purpose
Prompt mẫu để AI đọc artifact thực tế và map sang canonical slots.

## Prompt
Hãy đọc artifact dưới đây và thực hiện **semantic-to-canonical mapping** theo rule của AI Work System.

### Yêu cầu
1. Xác định artifact type và scope của artifact.
2. Dùng common understanding để suy ra các **canonical slots** phù hợp cho loại artifact này.
3. Map các section/table/pattern trong tài liệu vào các canonical slots đó.
4. Cho output rõ:
   - `recognized_canonical_slots`
   - `source_to_slot_mapping`
   - `important_missing_slots`
   - `proposed_meta_fields`
   - `proposed_relation_fields`
   - `proposed_index_search_fields`
   - `confidence_note`
5. Nếu artifact có vẻ thuộc một project format lặp lại, hãy gợi ý:
   - `candidate_project_format_label`
   - `reusable_mapping_note`

### Rule rất quan trọng
- Không đòi exact heading match.
- Ưu tiên semantic understanding và common structure clues.
- Không trộn inferred mapping vào confirmed source mapping mà không note rõ.
- Nếu confidence thấp vì template lạ, hãy nói rõ và nêu cần sample gì để chuẩn hóa tiếp.
