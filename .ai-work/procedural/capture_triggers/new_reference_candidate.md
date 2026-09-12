# new_reference_candidate — Reference / source-of-truth hữu ích mới
- **type:** wiki_update_candidate · **suggested_target:** knowledge_hub_reference · **timing:** normal

## When
Trong quá trình thực thi task hoặc Q&A với HUMAN, AI phát hiện một reference hữu ích, tài liệu authoritative, hoặc một ứng viên source-of-truth mà project chưa đăng ký trong Wiki. Dấu hiệu: cần trích dẫn lại tài liệu này về sau, hoặc nó là nguồn chuẩn cho một khái niệm/quy tắc.

## Capture as
**Family (CR-AIWS-2026-08-126 C1):** `wiki_knowledge_gap` — tên trigger `new_reference_candidate` giữ làm nhãn **capture-time**; giá trị ghi vào `candidate_kind` là `wiki_knowledge_gap`. `improvement_scope` mặc định: `project`.

candidate_kind: **new_reference_candidate**.

## Suggested action
Sau khi HUMAN review: tạo một source artifact và đăng ký nó vào Wiki (build source meta + cập nhật index) để các task sau có thể discover.

## Example
AI tìm thấy spec chuẩn cho định dạng JSONL capture trong khi xử lý AIP-EXEC → đề xuất đăng ký làm new_reference_candidate trong Knowledge Hub.

## Notes
—
