# Relations Enrichment CR — Template (batch, per-edge attestation)

> Dùng khi gom relation candidates (capture kind `artifact_relation_update`) thành 1 CR batch (CR-AIWS-2026-07-008 C3; cadence DP-912-7: định kỳ tuần/sprint + ngoại lệ high-value promote ngay). **Wiki-meta profile** → approver = **Wiki-Manager** (WIKI_CHANGE_REQUEST_SPEC). Nguyên tắc cứng: review TỪNG edge — không accept cả cụm; `knowledge_value: high` ở capture KHÔNG mang nghĩa ưu tiên promote.

## Frontmatter mẫu

```yaml
cr_id: CR-AIWS-YYYY-MM-NNN
title: "Relations enrichment batch — <kỳ> (<N> edges từ <M> AIPs)"
request_type: wiki_meta_update
change_type: relation_update        # wiki-meta profile enum
requester: "<ai session / HUMAN>"
reviewer_or_wiki_manager: wiki_manager
status: proposed
created_at: YYYY-MM-DD
needs_human_confirmation_after_draft: true
driving_source: "capture inbox entries: <CAP-ids + workspace paths>"
```

## Bảng per-edge attestation (BẮT BUỘC — mỗi edge 1 dòng, Wiki-Manager điền cột Verdict)

| # | from_id | to_id | role | basis note (draft từ capture — objective + intent-blind: data-flow + why/when + impact) | confidence hiện tại | Nguồn (CAP-id, TASK) | **Verdict: accept / reject / defer** | Ghi chú reviewer |
|---|---|---|---|---|---|---|---|---|
| 1 | SRC-... | SRC-... | references | ... | candidate | CAP-xxx (TASK-...) | | |

## Apply rule (khi Wiki-Manager duyệt xong)

1. CHỈ edges **accept** được apply: edit `## Related Sources` của meta from-side (role + basis note đã duyệt), **confidence flip `candidate` → `asserted` PER-EDGE** (không flip cụm).
2. `py .ai-work/tooling/build_relations.py` rebuild `relations.jsonl` → `lint_wiki` (kể cả `relations_thin_basis`) clean.
3. Edges **reject** → capture tương ứng status `discarded` (+lý do); **defer** → giữ `captured` kèm note, vào batch kỳ sau.
4. Capture gốc của edges accept → status `promoted` + `source_refs` trỏ meta đã sửa.
5. Maintenance log entry theo schema hiện hành.

## Checklist trước khi trình

- [ ] Mỗi edge có basis note đọc được độc lập (không cần mở lại conversation gốc)
- [ ] Không edge nào trùng edge đã có trong `relations.jsonl` (kể cả inverse pair — check `wiki_relations.py --relations <id>`)
- [ ] role thuộc registry (`build_relations.py` KNOWN_RELATION_TYPES) hoặc `x:` prefix có giải thích
- [ ] Batch không trộn system (multi-system: edges cùng `system` hoặc ghi rõ cross-system intent)
