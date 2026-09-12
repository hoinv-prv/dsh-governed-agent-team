# knowledge_quality_issue — Knowledge outdated/conflict/low-confidence
- **type:** finding_candidate · **suggested_target:** wiki_meta · **timing:** normal

## When
AI phát hiện knowledge bị outdated, conflicting, low-confidence, stale, hoặc suspicious. Không quyết định chỉ dựa vào source type — phải check meta/trust fields và evidence trước.

## Capture as
**Family (CR-AIWS-2026-08-126 C1):** `wiki_quality_issue` — tên trigger `knowledge_quality_issue` giữ làm nhãn **capture-time**; giá trị ghi vào `candidate_kind` là `wiki_quality_issue`. `improvement_scope` mặc định: `project`.

candidate_kind: **knowledge_quality_issue** (type=finding_candidate). Một số dấu hiệu cụ thể để phân loại khi capture:
- **outdated/stale** → version cũ, summary lỗi thời so với source hiện tại.
- **conflict** → hai nguồn mâu thuẫn về cùng một fact.
- **low-confidence/suspicious** → trust field thấp hoặc evidence yếu, cần xác minh.

## Suggested action
Đề nghị HUMAN review source trust, version, conflict, hoặc stale summary **trước khi** cập nhật Wiki — không tự sửa.

## Example
AI thấy meta của một spec ghi version v0.4 nhưng source artifact đã là v0.5 → capture knowledge_quality_issue (stale summary), flag cho HUMAN review.

## Notes
Đây là finding để flag, không phải lệnh sửa: AI ghi nhận và chuyển HUMAN quyết định, tuyệt đối không tự update canonical Wiki/meta.
