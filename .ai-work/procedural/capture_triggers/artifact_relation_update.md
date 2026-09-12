# artifact_relation_update — Quan hệ giữa sources chưa có trong meta/index
- **type:** relation_candidate · **suggested_target:** wiki_meta · **timing:** ⚡ capture NGAY (CR-AIWS-2026-07-008 — relations là HUMAN priority) · **knowledge_value default:** high
## When
AI phát hiện hai hoặc nhiều source artifact có quan hệ với nhau (depends_on, supersedes, companion_of, references...), nhưng quan hệ đó chưa được mô tả trong source meta hay index. Dấu hiệu: lookup/đọc nhiều source thấy chúng liên kết nhau mà meta/index không phản ánh. **Capture NGAY lúc phát hiện** — đó là lúc AI hiểu quan hệ rõ nhất; đừng dồn cuối step.
## Capture as
**Family (CR-AIWS-2026-08-126 C1):** `relation_or_object` — tên trigger `artifact_relation_update` giữ làm nhãn **capture-time**; giá trị ghi vào `candidate_kind` là `relation_or_object`. `improvement_scope` mặc định: `project`.

candidate_kind `artifact_relation_update` — kèm block máy-đọc (BẮT BUỘC từ CR-008):
```json
"relation": {"from_id": "SRC-...", "to_id": "SRC-...", "role": "references",
             "basis_note_draft": "<objective + intent-blind: data-flow + why/when cần đọc kèm + change impact>",
             "confidence": "candidate"}
```
`basis_note_draft` viết NGAY theo doctrine basis-note (proven lever 2026-06-01: TYPE alone fails — prose data-flow + why/when + impact mới làm AI đọc đúng related docs). `role` theo registry `build_relations.py` hoặc `x:` prefix.
## Suggested action
Gom vào **Relations Enrichment CR** batch (template: `.ai-work/procedural/relations_enrichment_cr_template.md`; cadence định kỳ + ngoại lệ high-value ngay — DP-912-7). Wiki-Manager review **per-edge** (accept/reject/defer từng edge); edges accept → edit `## Related Sources` + `build_relations.py` rebuild + lint; confidence flip candidate→asserted per-edge. `knowledge_value: high` mặc định của kind này KHÔNG mang nghĩa ưu tiên promote lúc triage.
## Example
Khi build meta cho spec A, thấy A `references` spec B nhưng relation chưa có trong index → capture ⚡ với relation block đầy đủ + basis note draft → batch Enrichment CR kỳ này.
## Notes
aiws-aip run wrap-up liệt kê relation candidates riêng (counter trong `aiws-aip run status`).
