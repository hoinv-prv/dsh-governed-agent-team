# NEW_INSTALLATION_GUIDE_v0_5_0

## 1. Goal
Hướng dẫn cài mới full Wiki package cho một project chưa có setup Wiki rõ.

## 2. Recommended install scope
Cài tối thiểu:
- toàn bộ `core/specs`
- toàn bộ `core/guidelines`
- toàn bộ `core/prompts`

Có thể giữ:
- `appendix` cho reference nội bộ
- `upgrade` chỉ để tham khảo, không bắt buộc với new install

## 3. Recommended project drop-in structure
Khuyến nghị đưa package vào một thư mục AI riêng của project, ví dụ:
- `project-root/aiws/wiki/`

Bên trong có thể giữ:
- `canonical/` cho docs canonical
- `rollout/` cho install/onboarding notes
- `local/` cho project-specific mappings/template customizations

## 4. New installation sequence
1. Read:
   - `README.md`
   - `PACKAGE_MANIFEST_v0_5_0.md`
   - `core/guidelines/GUIDELINE_INDEX_FLOW_NAVIGATOR_v0_1.md`
2. Confirm project profile at minimal level:
   - deliverable vs working artifact
   - wiki-eligible vs not
   - artifact classes currently available
3. Start with artifact understanding for existing project docs
4. Create canonical slot mappings for key artifact types
5. Build initial Wiki Meta / Index
6. Align candidate / CR / governance behavior
7. Customize AIP templates used by the project
8. Onboard members with rollout docs/checklist

> **Note — the AIWS methodology wiki ships pre-built (searchable).** Separate from the project's own domain wiki you are building above (`index.jsonl`), the AIWS methodology / spec / preset-knowledge wiki ships **pre-built** in a dedicated **`aiws` namespace** = `.ai-work/wiki_sources/index.aiws.jsonl` **+ `relations.aiws.jsonl`** (both pre-built in the package `payload/aiws_wiki_index/`, copied at install; rebuild any time with `py .ai-work/tooling/build_preset_wiki.py --target .`). It is searchable immediately after install via `py .ai-work/tooling/lookup_wiki_source.py --query "<topic>" --scope aiws`, and its relations are traversable via `py .ai-work/tooling/wiki_relations.py --relations <source_id>` (reads the project's `relations.jsonl` **and** `relations.aiws.jsonl`). AIWS upgrades refresh **only** the `aiws` namespace (`aiws_meta/` + those two files) — never your project's `index.jsonl` / `relations.jsonl`. (Shipped via CR-AIWS-2026-06-040 / -041; documented here per CR-AIWS-2026-06-059; relations preset + `build_preset_wiki.py` per CR-AIWS-2026-08-064.)

## 5. Minimum recommended first-wave setup
Tối thiểu nên setup trước cho:
- Requirement-side artifacts
- Basic Design
- Detail Design
- IT Testcase
- key supplemental artifacts if they already exist

## 6. Suggested initial outputs
- project profile note
- first artifact understanding set
- first canonical mapping pattern
- first meta/index baseline
- first project-customized AIP template note

## 7. Caution
Không cần cố canonicalize toàn bộ project ngay từ đầu.
Nên ưu tiên:
- các artifact dùng nhiều
- các relation hay tra lại
- các task BrSE thường thực hiện
