# PROMPT_BUILD_WIKI_META_FROM_MAPPING_v0_1

## Purpose
Prompt mẫu để AI build Wiki Meta / Index từ artifact understanding + canonical mapping.

## Prompt
Dưới đây là:
1. artifact understanding
2. canonical slot mapping
3. project mapping pattern (nếu có)
4. project-customized meta rules (nếu có)

Hãy build Wiki Meta / Index draft theo rule của AI Work System.

### Yêu cầu
1. Xác định build scope:
   - artifact-level
   - object-level
   - link-level
   - alias-level
   - supplemental-status-level
2. Tạo output rõ:
   - artifact_meta_records
   - object_meta_records
   - link_records
   - alias_records
   - supplemental_status_records (nếu relevant)
   - unresolved_records
3. Chỉ derive các meta/relation/search fields có giá trị rõ cho:
   - search
   - routing
   - review
   - traceability
4. Merge project-customized enrichment nếu có.
5. Thêm build_summary:
   - what was built
   - what was inferred
   - what remains unresolved

### Rule rất quan trọng
- Không biến mọi canonical slot thành meta field một cách máy móc.
- Giữ traceability giữa meta và source basis.
- Nếu chưa chắc object/relation/alias, hãy tạo unresolved marker thay vì ép certainty.
