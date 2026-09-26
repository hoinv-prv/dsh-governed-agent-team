---
name: aiws-pkg
description: >
  AIWS package lifecycle domain — build một install package tự chứa có version từ `product/`, cài vào
  dự án mới, upgrade bản đã cài, quick-install thẳng từ dev tree để dùng thử (dev-only, không ship),
  hoặc install-pack một **Standard Pack** (package THỨ HAI, nội dung quy trình của tổ chức) lên một dự
  án đã có AIWS. VERBS: build · install · upgrade · quick-install · install-pack. Dùng khi: "đóng
  gói/tạo package AIWS", "cài AIWS vào project", "nâng cấp AIWS", "cài thử AIWS", "cài/nâng cấp
  standard pack — quy trình chuẩn công ty" · "build install package", "install/upgrade AI Work
  System", "install standard pack". Version AIWS pin ở `product/aiws_version.md`, version pack ở
  `pack.yml`; mọi lượt install/upgrade/install-pack đều HUMAN-confirmed.
user-invocable: true
---

# SKILL: aiws-pkg (domain router)

> Consolidated by CR-AIWS-2026-07-025 — the former per-action skills of this domain are now VERBS of this ONE skill.
> **Old-name translation:** `aiws-pkg-<X>` → verb `X` (authority: `product/rename_map.json`).

## Router protocol (MANDATORY)
1. Parse the request → pick ONE verb from the table below (NL triggers).
2. **Read `operations/<verb>.md` (this folder) BEFORE executing** — it is the full, authoritative operation definition; every gate in it stays binding.
3. Verb mơ hồ → HỎI HUMAN (safety rule #6). Router adds NO gates, removes NONE.

## Verb routing table
| Verb | Operation | NL triggers | Params | Key gates (full text in operation file) |
|---|---|---|---|---|
| build | operations/build.md | VN: tạo package AIWS / đóng gói AIWS / xuất package · EN: build install package / release new AIWS version | version pinned in product/aiws_version.md (never CLI); prev package path (opt, auto-detect); output path (opt); runs build_aiws_install_package.py (no --version | version-pin no-CLI-version; output-folder-must-not-exist pre-flight; never overwrite previous package; do-NOT-ship runtime/Truth/personal/brainstorming+delta+tracking+Detail_Design; strip-and-copy 10_design; no source modification during build; generic install_templates + VERSION stamped at build only (CR-066); CLAUDE_SLIM deprecated-1-release |
| install | operations/install.md | VN: setup project mới / cài AIWS vào project / khởi tạo project · EN: init new project / install AI Work System | project_root (req); project_name (req); package_path (req); rule_targets (opt, multi-select claude|agents|copilot, default claude; alias claude_target=X -> rule_targets=claude + claude_rule_file=X); claude_rule_file (opt, CLAUDE.local.md|CLAUDE.md); helpers: merge_wiki_source_profiles.py --apply, accoun | HUMAN confirm before any file change; never overwrite existing files without asking; never invent Truth (stubs only); stop on pre-flight fail; settings.local.json only-if-absent no auto-merge; profiles MERGE never overwrite + never project_stopwords.yml (CR-04 |
| install-pack | operations/install-pack.md | VN: cài standard pack / cài quy trình chuẩn công ty vào dự án / nâng cấp standard pack / cài pack VTI · EN: install standard pack / upgrade the company process pack | pack_package_path (req — thư mục package pack, chứa `payload/` + `install_guide.md`); project_root (req); mode (fresh \| upgrade — tool tự suy từ `.ai-work/standard_pack/` đang có, KHÔNG hỏi rồi đoán); CLI: py .ai-work/tooling/install_standard_pack.py --package <pkg> --target <root> [--dry-run] | NOT the AIWS package — target phải đã có `.ai-work/` + `project_profile.yml`; `--dry-run` là OPT-IN (chạy trần là GHI THẬT) ⇒ luôn dry-run rồi HUMAN confirm trước khi chạy thật; mọi guard chạy TRƯỚC byte đầu tiên — từ chối = target còn nguyên; AIWS thấp hơn `aiws_min_version` **hoặc không đọc được version** → refuse; đã cài pack khác `pack_id` → DỪNG (cùng pack khác version = upgrade, cây pack bị THAY, file pack không còn ship sẽ bị xoá); skill trùng tên mà không do pack này cài → DỪNG, KHÔNG đè; `wiki_source_profiles` MERGE không đè (`standard_asset.yml` BẮT BUỘC, thiếu → `meta_source_type_unknown`); `.ai-work/project_process/` (bản tailored của dự án) KHÔNG BAO GIỜ bị chạm; kết thúc bằng pin `standard_pack` trong `project_profile.yml` + dựng lại index `aiws` |
| quick-install | operations/quick-install.md | VN: cài thử AIWS vào dự án / dùng thử AIWS trước khi release / cài nhanh AIWS · EN: quick install AIWS / install AIWS from source | target (req); name (opt, default 'AIWS Trial'); apply (opt, UPDATE-mode write gate); CLI: py .ai-work/tooling/quick_install_aiws.py --target <path> --name "<nam | HUMAN confirm before write, never auto-confirm; never touch rule files (CLAUDE*.md / AGENTS.md / copilot-instructions.md) unless --tools is passed explicitly (CR-066); never invent Truth; UPDATE dry-run-first (--apply only); trial package ephemeral never in releases/; anti-self-clobber guard; read-only on product/; DEV-ONLY never shipped ( |
| upgrade | operations/upgrade.md | VN: cập nhật AIWS / nâng cấp AI Work System · EN: upgrade AIWS / update aiws package / install new version | package_path (req); project_root (opt, default cwd); sections (req: all / numbers / changed); helpers: merge_wiki_source_profiles.py, build_wiki_source_index.py | temp-first MANDATORY (.aiws-upgrade.tmp) + never apply before user confirmation; never overwrite Truth; never touch project runtime; never auto-delete REMOVED (sole exception: rename_map.json-listed folders, temp-first + HUMAN-confirmed; special deprecation po |
