# INSTALL_CHECKLIST_v0_5_0

- [ ] Đã copy package vào thư mục AI riêng của project
- [ ] Đã đọc `README.md`
- [ ] Đã đọc `GUIDELINE_INDEX_FLOW_NAVIGATOR_v0_1.md`
- [ ] Đã xác định deliverable vs working artifact
- [ ] Đã xác định wiki-eligible vs not
- [ ] Đã chọn nhóm artifact setup trước
- [ ] Đã tạo first artifact understanding
- [ ] Đã tạo first canonical slot mapping
- [ ] Đã build first meta/index baseline
- [ ] Đã chốt candidate / CR / governance minimal flow
- [ ] Đã customize ít nhất một AIP template chính cho project
- [ ] Đã chuẩn bị rollout/onboarding cho member liên quan

---

## Wiki Tooling Quality Checklist

When the wiki source index + metas are first set up, verify before go-live:

### Tooling
- [ ] `lookup_wiki_source.py` runs on Windows: `py .ai-work/tooling/lookup_wiki_source.py --query "test"` exits 0 or 1 (not 2+)
- [ ] the project's rule file(s) (`CLAUDE.local.md` / `CLAUDE.md` / `AGENTS.md` / `.github/copilot-instructions.md`)
      specify the Python command: `py` (Windows) or `python3` (Linux/macOS)
- [ ] `.ai-work/AIWS.md` (core rules) and `.ai-work/install_templates/VERSION` are present, and **every**
      wired rule file carries an `AIWS:BEGIN rules` block on the manifest version
      (`py .ai-work/tooling/compose_aiws_rules.py --check` → rc=0) — CR-AIWS-2026-08-066
- [ ] `build_wiki_source_index.py` uses `_omit_blank()` — no blank fields written to index
- [ ] `build_wiki_source_meta.py` supports `--summary`, `--knowledge-targets`, `--lookup-keys` args

### Index quality
- [ ] Index entries do NOT contain: `meta_id`, `updated_at`, `knowledge_value`, `intended_ai_use`
- [ ] Each entry in `index.jsonl` < 250 tokens
- [ ] `summary_short` answers "file này có gì + dùng vào việc gì" in 1–2 sentences
- [ ] `lookup_keys` contains specific IDs (F04, BR-F04-01) rather than generic words (list, filter)

### Meta quality
- [ ] Meta files do NOT have duplicate body sections (Runtime Use, Source Representation, Cautions)
- [ ] Meta frontmatter does NOT have blank optional fields
- [ ] Canonical docs have useful summaries (not "Version: 0.1")

### Escalation
- [ ] `lookup_wiki_source.py` prints raw fallback hint when 0 results
- [ ] `.ai-work/wiki/reference/document_search_guidelines.md` exists with artifact dir table
- [ ] `aiws-wiki lookup/SKILL.md` has No-match escalation protocol

### Architecture
- [ ] Profile files contain ONLY: `profile_id`, `description`, `knowledge_targets`
- [ ] PMP files (`pmp_<type>.yml`) contain project-specific extraction spec
- [ ] `build_wiki_source_meta.py` loads PMP when present (confirmed by testing)
