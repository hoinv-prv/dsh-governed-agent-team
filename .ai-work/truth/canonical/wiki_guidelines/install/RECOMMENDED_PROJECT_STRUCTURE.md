# RECOMMENDED_PROJECT_STRUCTURE_v0_5_0

## Recommended structure
```text
project-root/
  aiws/
    wiki/
      package/
        core/
          specs/
          guidelines/
          prompts/
        rollout/
        upgrade/
        appendix/
      project-local/
        project_profile/
        mapping_patterns/
        meta_build_outputs/
        aip_customizations/
        rollout_notes/
        reference/                # curated project-local reference docs (e.g. document_search_guidelines.md)
```

Trong **runtime tree** (`.ai-work/`), bản cài còn tạo sẵn hai chỗ cho tài liệu đề xuất/thay đổi —
tách theo **hướng đi**, không theo loại tài liệu (CR-AIWS-2026-08-018):

```text
.ai-work/
  upstream_requests/     # IR gửi LÊN team AIWS      — README + IR_TEMPLATE.md, đặt tên IR-YYYY-MM-DD-<slug>
  change_requests/       # hồ sơ thay đổi CỦA dự án  — README, namespace CR-<TÊN-DỰ-ÁN>-*
```

## Notes
- `package/` giữ bộ canonical install package
- `project-local/` giữ phần project-specific và outputs sinh ra sau khi áp dụng package
- không nên trộn lẫn project-local files vào canonical package files
- `reference/` giữ project-local reference docs (curated reading guides).
- `upstream_requests/` vs `change_requests/`: **KHÔNG** dùng namespace `CR-AIWS-*` / `AP-CR-*` ở cả hai — id upstream do AIWS cấp lúc promote (CR Spec §10/§18). Dự án đang để IR/CR ở chỗ khác không bị ép migrate; đây là chỗ mặc định từ nay. Upgrade chỉ ghi đè README/template do AIWS ship — file của dự án trong hai thư mục đó không bị đụng.
- `wiki/pages/` giữ **curated synthesis pages** (system overview, function/table list, business flow, directory map, read-first, glossary...) do `/aiws-wiki build-pages` sinh — HUMAN-gated, `source_type: wiki_page` `curated_reference` (CR-AIWS-2026-07-023). KHÁC `wiki/overview/` (deterministic generated, navigation-only). Bắt buộc có `document_search_guidelines.md` (scaffold từ `install/document_search_guidelines.template.md`) — xem `INSTALL_CHECKLIST.md`. Trong runtime tree hiện hành, path là `.ai-work/wiki/reference/document_search_guidelines.md`.
