# retrieval_improvement — Wiki có nhưng khó retrieve
- **type:** wiki_meta_update_candidate · **suggested_target:** wiki_meta · **timing:** normal
## When
AI eventually tìm được đúng knowledge, nhưng retrieval khó: thiếu aliases, index yếu, title không rõ, routing kém, hoặc thiếu overview. Dấu hiệu: phải thử nhiều lần / tìm vòng vo mới ra đúng source.
## Capture as
**Family (CR-AIWS-2026-08-126 C1):** `retrieval_improvement`. `improvement_scope` mặc định: `project`.

Capture as candidate_kind `retrieval_improvement`.
## Suggested action
Sau HUMAN review: thêm aliases, search hints, overview links, Task Intent Guidance, hoặc meta keywords để lần sau retrieve dễ hơn.
## Example
AI cần spec về "wiki change request" nhưng lookup chỉ ra khi gõ đúng "WIKI_CHANGE_REQUEST_SPEC" → đề xuất thêm alias "CR spec", "wiki CR" vào meta.
## Notes
—
