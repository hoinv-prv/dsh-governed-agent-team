# PROMPT_UPDATE_WIKI_META_INCREMENTALLY_v0_1

## Purpose
Prompt mẫu để AI update Wiki Meta / Index khi có evidence / artifact / change mới.

## Prompt
Dưới đây là:
1. existing Wiki Meta / Index records
2. new source evidence / updated mapping / approved CR / human correction
3. project mapping pattern và project-customized meta rules (nếu có)

Hãy update Wiki Meta / Index một cách incremental theo rule của AI Work System.

### Yêu cầu
1. Xác định update scope:
   - records nào bị ảnh hưởng
   - layer nào cần update
2. Chỉ update những phần cần thiết:
   - add/revise link
   - add/revise alias
   - update status/reflection
   - add searchable field
   - mark superseded/deprecated
   - resolve hoặc thêm unresolved marker
3. Output rõ:
   - updated_records
   - new_records
   - deprecated_records
   - unresolved_changes
   - update_summary
4. Giữ provenance rõ:
   - update này dựa trên nguồn nào
   - vì sao cần update
   - phần nào vẫn chưa chắc

### Rule rất quan trọng
- Không rebuild toàn bộ nếu chỉ có delta nhỏ.
- Không xóa uncertainty nếu source mới vẫn chưa đủ chắc.
- Nếu update chạm canonical layer theo governance flow, hãy giữ wording/shape phù hợp với approved change direction.
