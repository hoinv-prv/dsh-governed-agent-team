# SOURCE_BUILD_ROUTING_SPEC (Stage 2 — MVP)

**Status:** active (Stage 1 + Stage 2 MVP, applied 2026-06-15 via AIP-EXEC-101) · **Introduced by:** CR-AIWS-2026-05-019 · **Co-decided with:** CR-AIWS-2026-05-017
**Class:** tooling dispatch (NOT a knowledge-representation layer)

## 1. Purpose

Định nghĩa cách AIWS map một `source_type` → **tool/skill nào dùng để BUILD và REFRESH** wiki source
meta của loại đó. Mục tiêu: source code & artifact đặc thù (Java now; COBOL/Python sau) dùng **bulk
builder chuyên dụng** thay vì luồng generic per-file, mà không phải hardcode trong từng `CLAUDE.local.md`.

## 2. Verified gap (vì sao cần)

- `build_wiki_source_meta.py` (engine) là per-file (1 meta / 1 artifact); `aiws-wiki register-batch` Stage B
  loop per-file cho **mọi** file — **không có nhánh** cho source_type cần bulk builder.
- Đã tồn tại các bulk builder (vd `build_java_wiki_metas.py`, ship trong `tooling/`) nhưng **không có
  chỗ canonical** ghi "source_type X → dùng builder Y" → AI mặc định chạy sai luồng generic trên cây code.

## 3. Config-home invariant (KEY — co-decided với CR-017)

> Đây là quy tắc "per-source_type config sống ở đâu", áp dụng cho CẢ CR-017 lẫn CR-019.

| Mối quan tâm | Sống ở | Ghi/đọc |
|---|---|---|
| **Interpretation + relations** (knowledge_targets, lookup hints, section hints, related_sources) | `profiles/*.yml` + PMP | human/AI-edited (read-mostly) |
| **Build dispatch** (tool nào build/refresh) cần machine auto-upsert | **JSON sidecar riêng** (Stage 2) | machine-written qua tool |

Lý do tách (load-bearing, đã verify): `_common.py dump_frontmatter` chỉ serialize scalar + flat list;
**không có stdlib YAML round-trip writer** → W2 machine-upsert không thể ghi an toàn vào YAML profile.
JSON round-trip sạch bằng `json` stdlib.

Invariant bắt buộc:
- **Cả hai KHÔNG project vào `index.jsonl`** (mirror CR-017).
- `source_type` là **single canonical key** (CR-008 đã làm source_type profile-derived). Build routing
  **không** tạo authoritative key thứ 2; nếu route tham chiếu `profile_id` thì chỉ là **back-reference
  non-authoritative**.
- Build Routing là **tooling dispatch table orthogonal**, KHÔNG phải first-class concept parallel với
  Source Interpretation Profile (tránh lặp shape Knowledge Object đã bị xóa ở CR-005).

## 4. Stage 1 (SUPERSEDED by Stage 2 — retained as history) — static seam, no registry

> Stage 1 routed via a **static table** in `aiws-wiki register-batch` A3b. As of Stage 2 (§5, 2026-06-15) A3b is
> **data-driven** (reads `_build_routing.json`); the static `java_source` row below was migrated into the registry.

Routing was implemented bằng **static table trong skill** `aiws-wiki register-batch` (Stage A3b):

| source_type | bulk builder (reference) | refresh (Stage 1) |
|---|---|---|
| `java_source` | `tooling/build_java_wiki_metas.py --root {root} --source-prefix {prefix} --meta-subdir {subdir}` (preview `--dry-run`) | rerun build trên subdir đã đổi |
| `asp_cobol_source` | `tooling/build_cobol_wiki_metas.py --root {root} --source-prefix {prefix} --meta-subdir {subdir} --config .ai-work/asp_cobol_wiki.config.yml` (preview `--dry-run`; live tree needs `--write-live`) | rerun build trên subdir đã đổi — **luôn kèm `--meta-subdir`** (thiếu nó, thư mục meta lấy tên từ `source_type`) |
| *(project-defined)* | dự án có thể có thêm bulk builder riêng | — |
| *(mọi loại khác)* | **default route** = generic per-file `/aiws-wiki build-meta` | `/aiws-wiki refresh-meta` |

Quy tắc: **default = generic; bulk = opt-in.** Nếu `source_type` khớp một bulk builder → preview
(`--dry-run`) → chạy → rebuild index + lint, **bỏ qua** loop per-file. Ngược lại → luồng generic.

## 5. Stage 2 (IMPLEMENTED — MVP; CR-AIWS-2026-05-019 Stage 2 applied 2026-06-15 via AIP-EXEC-101)

> **Gate waiver (Approved Deviation, AI_WORK_CONTRACT §5) — CLOSED 2026-08-12.** Stage 2 was gated on a 2nd real
> source_type (COBOL/Python). The wiki-manager WAIVED that gate on 2026-06-15 to ship the data-driven register
> command with the MECHANISM only — at that point no concrete new source_type route was populated (registry
> seeded with `java_source` alone, migrated from the Stage-1 static table).
>
> **The gate is now met on its own terms** (CR-AIWS-2026-08-026): `python_source` followed, and the **ASP COBOL**
> preset shipped a real third builder — engine `cobol_wiki/` + parser `cobol_parser/` + entry point
> `build_cobol_wiki_metas.py` + profile `asp_cobol_source.yml` + config template + operating guide. Scoped to
> **Fujitsu ASP**, deliberately not to COBOL in general: the dialect lives in the config, so another dialect is a
> new preset on the same engine. Route registration stays with the **consuming project** (§3 invariant — the
> registry is runtime, project-owned; AIWS ships the builder and the `route_build_tool.py set` recipe, and holds
> no ASP COBOL sources of its own).

Shipped:
- **`_build_routing.json`** (JSON sidecar, `.ai-work/wiki_sources/`, runtime-only) + **`route_build_tool.py`**
  (stdlib CLI: `get/set/list/remove/render`; placeholders `{root}{prefix}{subdir}{artifact}`; `default_route`
  fallback = generic). NOT projected into `index.jsonl` (§3 invariant).
- **Hardening:** portable paths (`__PROJECT_ROOT__` via `portable_locator`/`resolve_locator`); `--args` as a
  shlex string → argv LIST; `render` emits argv list + `shlex.join` preview; tool-path existence re-check at READ
  + soft-WARN at `set`; atomic write (`mkstemp` + `os.replace`); unknown-placeholder WARN. Routing keys are EXACT
  source_types → deterministic (no glob overlap). `lint_wiki` validates the registry (required keys / profile_id
  back-ref / known placeholders / refresh_mode / default_route).
- **Build-tool contract:** a custom builder is stdlib-only, accepts the registry placeholders, supports
  `--dry-run`, and emits a valid meta (frontmatter + Summary / Knowledge Targets / Lookup Keys).
- **Build-tool contract — write discipline (CR-AIWS-2026-08-059, fold CAP-1051-01/02):**
  - **LF-stable writes:** builder ghi file qua `_common.write_text`/`write_jsonl` (LF mọi OS) — không tự
    `Path.write_text` thiếu `newline=` (đó là nguồn EOL churn đã trả giá 4 lần, CAP-1008-02).
  - **Rerun/refresh phải carry curation-state** (`carry_curation_state`, CR-AIWS-2026-08-058). Phân loại builder
    theo cách đụng meta cũ: **merge-preserve** (tự đọc + giữ field cũ — vd cobol) · **delegate** (shell-out qua
    `build_wiki_source_meta --mode refresh`, tự hưởng luật preserve — vd canonical-package, asp) ·
    **overwrite-wholesale** (đè cả file — vd java/python): loại thứ 3 **bắt buộc wire carry tường minh**, nếu
    không field HUMAN curate bị XÓA im lặng (không chỉ reset).
  - **Refresh tối thiểu hóa LLM (PO ruling 2026-08-15):** với route không dùng LLM (deterministic builders),
    refresh mặc định là thao tác **thuần cơ học (tool-only)** — chỉ dùng LLM khi bắt buộc cần suy luận (vd
    summary AI-derived truyền qua `--summary` / completion layer ở trên) hoặc khi cần HUMAN confirm.
- **Completion layer (CR-AIWS-2026-07-002 H1 — un-defers the former MVP note).** A builder MAY emit a
  **partial** meta (mechanical fields + `needs_completion: [summary, lookup_keys, related_sources]`) for a
  downstream **LLM completion** pass that improves those fields; `lint_wiki` **blocks a partial from being
  treated as finished** (`meta_needs_completion` = error) until the flag is cleared. `build_wiki_source_meta.py`
  supports `--emit-partial`. This gives every build path (generic + bulk) a tool-does-the-mechanical /
  LLM-does-the-semantic seam without the builder having to fake a quality summary. A builder may still emit a
  FULL meta directly (no partial) when its mechanical output is sufficient.
- **W2 — author-on-the-fly + register (directive model):** under ONE explicit HUMAN directive ("build a tool for
  X and register it"), AI authors a builder per the contract, runs it, **format-checks** the output (`lint_wiki`;
  fix-and-rerun if wrong), then registers it — **no second confirm**. AI never authors+registers on its own
  initiative (Rule 8). Wired into `aiws-wiki register-batch` A3b (now data-driven).
- **W2-suggest — route-suggestion at GATE 4 (CR-AIWS-2026-07-002 H4):** the HUMAN directive above need not
  arrive unprompted. When `aiws-wiki register-batch` detects a **stable new format** whose `source_type` has no
  route (`route_build_tool.py get` → `generic`) across ≥3 files, GATE 4 asks the operator a SECOND question —
  "create a route/builder for this source_type?" — alongside the PMP question. A HUMAN **yes** becomes the W2
  directive (then the no-second-confirm flow above runs). AIWS thus *proposes* a route when it recognises a
  routable format, but **never creates one silently** (Rule 8 unchanged). Registry-seeded example builders:
  `build_java_wiki_metas.py` (`java_source`), `build_python_wiki_metas.py` (`python_source`, stdlib `ast`).
- **Refresh = rerun the tool** (`refresh_mode: rerun_tool`); FORBID regenerating a whole directory on a one-file
  change (do-not-clobber).
- **Index always standard** (`build_wiki_source_index.py`); a custom builder never writes the index.

### Revision history
- 2026-08-15 — **Write-discipline contract** added by CR-AIWS-2026-08-059 (AIP-EXEC-1052): LF-stable writers + carry curation-state (phân loại merge-preserve/delegate/overwrite-wholesale) + refresh tối thiểu hóa LLM cho route không-LLM (PO rider kèm approve CAP-1051-01).
- 2026-08-12 — **Stage-2 gate CLOSED** by CR-AIWS-2026-08-026 (applied via AIP-EXEC-1020): the ASP COBOL preset is the real 2nd/3rd source_type the 2026-06-15 waiver deferred. §4 example table gains the `asp_cobol_source` row; §5 waiver blockquote records the closure. Route registration remains project-side per §3.
- 2026-06-15 — Stage 2 implemented (MVP) via AIP-EXEC-101 / CR-AIWS-2026-05-019 Stage 2 (gate waived). Stage 1 §4 retained as history; A3b is now data-driven.

## 6. See Also
- `CR-AIWS-2026-05-019` (CR gốc, staged) · `CR-AIWS-2026-05-017` (config-home co-decision)
- `WIKI_META_INDEX_SPEC.md §A12` (deferral — đã amend để sanction spec này)
- IR nguồn: FE/Soumu `AIWS-IR-20260530-wiki-source-build-routing`
