---
name: aiws-wiki
description: >
  Project Knowledge Hub domain — dựng, tra cứu và bảo trì wiki: Wiki Source Index, source meta,
  relations, mapping pattern (PMP), local knowledge, overview + trang curated. 14 verbs: lookup ·
  register · register-batch · build-meta · refresh · refresh-meta · deregister · build-pattern ·
  refresh-pattern · test-lookup · add-local-knowledge · build-overview · build-pages · bootstrap.
  Dùng khi: "tìm trong wiki", "tra cứu spec", "đăng ký tài liệu vào wiki", "cập nhật/refresh wiki",
  "build trang wiki" · "look up a spec", "register this file", "refresh wiki meta".
user-invocable: true
---

# SKILL: aiws-wiki (domain router)

> Consolidated by CR-AIWS-2026-07-025 — the former per-action skills of this domain are now VERBS of this ONE skill.
> **Old-name translation:** `aiws-wiki-<X>` → verb `X` (authority: `product/rename_map.json`).

## Router protocol (MANDATORY)
1. Parse the request → pick ONE verb from the table below (NL triggers).
2. **Read `operations/<verb>.md` (this folder) BEFORE executing** — it is the full, authoritative operation definition; every gate in it stays binding.
3. Verb mơ hồ → HỎI HUMAN (safety rule #6). Router adds NO gates, removes NONE.

## Verb routing table
| Verb | Operation | NL triggers | Params |
|---|---|---|---|
| lookup | operations/lookup.md | tìm trong wiki / wiki có gì về X / tìm doc về X / tra cứu spec / lookup source / find doc in Knowledge Hub before raw read | --query --mode {lexical/id/path/tokens/catalog} --limit --full --excludes --scope --authorized --include-raw --lookup-mode object --source-type --system/--all-s |
| register | operations/register.md | add file này vào wiki / đăng ký tài liệu này / thêm vào wiki index / register this file (+ folder & PMP phrasings route onward to register-batch / build-pattern) | file path + hint; derives source_id SRC-<PREFIX>-<ID>[-<LAYER>], artifact_type, profile, title; delegates aiws-doc-convert-skill for binaries |
| register-batch | operations/register-batch.md | add toàn bộ file trong thư mục vào wiki / register wiki sources batch / bulk ingestion / folder of design files | <folder> / --files ...; --incremental; route_build_tool.py get/render/set; smoke_test --self-test --only |
| build-meta | operations/build-meta.md | thêm source mới vào wiki / tạo meta cho source / đăng ký tài liệu mới vào wiki index / build wiki source meta / register new document | --artifact --source-id --source-type --profile --title [--summary --knowledge-targets --lookup-keys] --system/--common --mode {create/refresh} --no-related-sour |
| refresh | operations/refresh.md | update/refresh/cập nhật wiki / file đã thay đổi / source đã thay đổi / sync wiki source / tài liệu gốc đã update (PMP phrasings route onward to refresh-pattern) | delegates detect/refresh/evaluate tools; wiki_relations --relations before edge changes; build_relations.py; build_wiki_overview.py --system/--all-systems |
| refresh-meta | operations/refresh-meta.md | cập nhật wiki meta / refresh meta / source đã thay đổi / periodic wiki maintenance | --meta --profile [--apply] [--regenerate-summary] [--regenerate-lookup-keys] [--review-decision] [--impact-level] [--change-summary] |
| deregister | operations/deregister.md | gỡ source khỏi wiki / xóa tài liệu khỏi wiki index / bỏ đăng ký source / dọn orphan registration / deregister wiki source / remove this source / clean up dangling meta | source_id / list / folder; archive(default)/delete/cancel; append_maintenance_log action=source_deregistered; index+relations rebuild |
| build-pattern | operations/build-pattern.md | tạo mapping pattern / save format pattern / build PMP / (AI-triggered: new stable format detected) | N sample metas → pmp_<profile_id>.yml in profiles/; mapping_pattern_id PMP-<PROJECT>-<FORMAT>-<VERSION> |
| refresh-pattern | operations/refresh-pattern.md | cập nhật mapping pattern / refresh PMP / format đã thay đổi / format drift detected | existing pmp_<profile_id>.yml + drift samples; bump last_validated |
| test-lookup | operations/test-lookup.md | test/kiểm tra wiki lookup / thử lookup / verify lookup / lookup có tìm ra không / check if wiki can find / test xem wiki tìm được gì cho tác vụ | Mode A: --self-test [--verbose --top-n --key-limit]; Mode B: --cases <jsonl> [--format json] (fields query/expected_source_id/mode/top_n/label/system/forbid); M |
| add-local-knowledge | operations/add-local-knowledge.md | thêm knowledge source / đăng ký nguồn kiến thức local / add external source / register local knowledge / có tài liệu bên ngoài muốn AI biết | meta_dir label description search_triggers; build_wiki_source_index.py --scope local |
| build-overview | operations/build-overview.md | tạo wiki overview / regenerate overview / cập nhật trang tổng quan wiki / wiki có gì / after index-relations rebuild / lint overview_fingerprint_stale | build_wiki_overview.py --system <id>/--all-systems [--pages contents,search,health,nav] [--no-register] |
| build-pages | operations/build-pages.md | build trang wiki dự án / tạo trang tổng hợp wiki / system overview / function list / business flow page / onboarding pages | build_wiki_page_base.py {survey/skeleton/check-grounding} --system/--all-systems --page <KIND> --out <ws>; subverbs survey/build/register/refresh/status |
| bootstrap | operations/bootstrap.md | bootstrap wiki / build project Knowledge Hub lần đầu / khởi tạo wiki dự án / first wiki build (ONE-TIME, not maintenance) | $1 optional corpus-root; lint_aip.py 0-error gate; build_wiki_overview.py at STEP-11 |

> Guardrail của từng verb nằm trong chính operation file của nó — đọc ở đó khi chạy
> verb, đừng trông vào bảng này. (Bảng từng chép lại guardrail; đó là bản sao, và mọi
> run đều trả tiền cho 13 verb mình không dùng. CR-AIWS-2026-09-005)
