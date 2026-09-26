# aiws-pkg — operation: build

> Operation of the `aiws-pkg` domain skill (consolidated by CR-AIWS-2026-07-025; former standalone skill — see `product/rename_map.json`). Content preserved verbatim; every gate herein stays binding.


## Purpose
Package the current state of AI Work System MVP into a self-contained
installable folder to be deployed into other projects via `/aiws-pkg install`.

**Hai package, hai chủ, hai lớp version (CR-AIWS-2026-09-001).** Verb này dựng **package AIWS**, và
package AIWS **không** chứa Standard Pack nào. Nội dung quy trình của một tổ chức được đóng thành
**package riêng** (`build_standard_pack_package.py`) và cài **lên trên** một dự án đã có AIWS bằng verb
`install-pack`. Đừng nhét pack vào payload AIWS: chủ nội dung khác, nhịp phát hành khác, và
`aiws_min_version` của pack chỉ có nghĩa khi hai bên tách rời. Xem mục **Release pack vN** dưới đây.

## Inputs
- `version` — **NOT a CLI input.** Pinned in `product/aiws_version.md` (repo-root TEXT path — cross-tree target, CR-AIWS-2026-07-029 §3.1) (`aiws_version` + optional `release_date`), the single source of truth so every build produces the same version. To release a new version, **bump that file FIRST**.
- `prev package path` (optional) — auto-detected from `releases/` if omitted
- `output path` (optional) — default: `releases/AI_Work_System_MVP_<pinned version>_<date>/`

## Flow
1. Read the pinned version from `product/aiws_version.md`. If the user wants a *new* release, ask them to bump `aiws_version` (+ `release_date`) there first — do NOT type a version on the CLI. (prev auto-detected; output optional.)
2. Pre-flight — verify source sections exist; output path `releases/AI_Work_System_MVP_<pinned version>_<date>/` must not yet exist (if it does, the version is already released → bump the pin)
3. Run `build_aiws_install_package.py` (no `--version` — it reads the pin file)
4. Verify output: START_HERE.md, README.md, MANIFEST.md, CHANGELOG.md, payload/ with 8 subfolders
5. Report results to user — state which pinned version was built

## Release pack vN — đóng gói một Standard Pack (CR-AIWS-2026-09-001)

Nhịp riêng, chủ riêng, version riêng. **Chủ pack** (với `vti_standard_pack` là QA Team) quyết nội dung;
AIWS chỉ sở hữu hình dạng. Năm bước, đúng thứ tự — mỗi bước là điều kiện của bước sau:

1. **Bump `pack.yml`** ở nguồn của pack: `pack_version` (semver, không tiền tố `v`) + mục trong
   `CHANGELOG.md`. Đổi `asset_id`, bỏ task, hay siết `classification` lên `mandatory` là **major**.
   `aiws_min_version` chỉ nâng khi pack thật sự cần bản AIWS mới hơn — nó là hợp đồng một chiều.
2. **Pull** vào repo AIWS — đường DUY NHẤT đưa nội dung pack vào cây:
   `py .ai-work/tooling/pull_standard_pack.py --from <pack-root> --ref <commit|tag> [--dry-run]`.
   Tool **chạy lint trước khi ghi và từ chối khi lint đỏ**, rồi ghi `PACK_SOURCE.md` (nguồn · ref ·
   thời điểm · `pack_id` · version). Vì có máy gác nên **không cần CR cho từng lần pull** — ngoại lệ
   hẹp ở rule 8 (`AIWS.md`; `Standard_Pack_Contract_Spec_MVP` §10). Đổi *hình dạng* thì vẫn cần CR.
3. **Lint lại tại chỗ:** `py .ai-work/tooling/lint_standard_pack.py --pack product/standard_pack`
   → 0 ERROR. Lint kiểm **hợp đồng**, không kiểm nội dung: nó không bao giờ phán một checklist thiếu mục.
4. **Build:** `py .ai-work/tooling/build_standard_pack_package.py --pack product/standard_pack`
   → `releases/<pack_id>_<pack_version>_<date>/`. Package tự sinh metas + `install_guide.md`, và
   **ship kèm `wiki_source_profiles/standard_asset.yml`** — thiếu profile thì mọi dự án cài pack sẽ
   `meta_source_type_unknown`, nên nó là bắt buộc chứ không phải tuỳ chọn.
5. **Publish + cài thử một lượt thật** bằng verb `install-pack` vào một dự án đã có AIWS, rồi
   `lint_standard_pack` + một `lookup_wiki_source` trả về `SRC-STDPACK-*`. Build xanh không chứng minh
   được bản cài chạy; chỉ một lượt cài thật mới chứng minh.

Ba lớp version không trộn: AIWS (`product/aiws_version.md`) · pack (`pack.yml`) · pin của dự án
(`standard_pack` trong `.ai-work/project_profile.yml`). Cắt release AIWS **không** cắt release pack, và
ngược lại.

## Rules
- **version is pinned** in `product/aiws_version.md` — never pass a version on the CLI for an official build; bump the pin to cut a new version. (`--override-version` exists ONLY for trial/ephemeral builds via `quick_install_aiws.py`.)
- **thêm payload section mới = khai loại pair (lesson AIP-945; canonical CR-AIWS-2026-07-035):** section mới trong `PAYLOAD_MAP`/build phải khai loại pair cho `check_dual_tree.py` — mirror thật (mặc định) / MERGE (`ONLY_OK_SECTIONS`) / generated-no-product-mirror (`SKIP_SECTIONS`, vd `aiws_wiki`) — nếu không, pair giả sinh hàng loạt `dual_tree_only_in_one`. Kèm: bản build kế nhớ đưa `product/UPGRADE_IMPACT_NOTE_next_release.md` (nếu tồn tại) vào release note rồi xoá draft.
- do NOT modify source files during build
- do NOT ship runtime folders (`workspaces/`, `aip/exec|plans|local/`, `history/`, `wiki/`)
- do NOT ship project Truth files (`SOP_MASTER`, `AI_WORK_CONTRACT`)
- do NOT ship personal files (`*.local.md`, `*.bak-*`, `*.preview`)
- do NOT ship `methodology/00_brainstorming/`, `methodology/90_delta_tracking/`, `aip_templates/tracking/`, `10_design/Detail_Design_MVP_Core_Artifacts.md` — fully excluded
- `10_design/` (4 files: Architecture, Basic, Conceptual, Methodology) — strip-and-copy: sections explaining AIWS design rationale/phases are removed, operational content kept
- always create a new versioned folder side-by-side — never overwrite previous package
- `install_templates/` must be generic — no project-specific references (it is the ONE source of
  rule-file content: core + adapters + identity placeholders)
- `payload/install_templates/VERSION` is **generated at build** (`stamp` step in `build()`), never
  committed under `product/` — build is the ONLY site that stamps a version; install / upgrade /
  quick-install merely carry it (CR-AIWS-2026-08-066)
- **Deprecation ledger (CR-AIWS-2026-08-066):** `CLAUDE_SLIM_TEMPLATE.md` is still emitted for ONE
  transition release, composed from `install_templates/` (no embedded string). **Remove the emit +
  `compose_slim_template()` at the NEXT release after v1.2.0.** This ledger lives here on purpose:
  `UPGRADE_IMPACT_NOTE_next_release.md` is folded away at every release cut, so a note placed there
  disappears before it is due.
- **Agents package (CR-AIWS-2026-06-055/051/049; commands re-scoped CR-AIWS-2026-07-031 T3 + CR-AIWS-2026-08-019):** `product/agents/` ships as one PAYLOAD_SECTION → `.ai-work/agents/` (self-contained — single-track, no `.aiws-staging`). Its `.claude` surfaces are wired at build by `wire_agent_pack_claude`: the `aiws-agent` router skill is copied into `payload/skills`, and one **generated pointer-stub per verb spec** is written into `payload/commands` (`/aiws-agent-<verb>` — a stub only points at the pack-internal spec `.ai-work/agents/commands/…`, never copies spec content; NO stub for the router itself — it would collide with the `/aiws-agent` skill). An **install smoke-check FAILS the build** if the router is unwired, a verb lacks its stub, or a stub carries more than pointer content. `lint_agents.py` rides inside the package; `/aiws-lint` runs it when `.ai-work/agents/` exists. NOT shipped: `agents/instances/`, `sample_project_package/`, dev-process docs. Optional — absent `product/agents/` → default build unchanged.
