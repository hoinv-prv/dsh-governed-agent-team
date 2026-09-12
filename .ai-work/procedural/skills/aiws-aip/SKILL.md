---
name: aiws-aip
description: >
  AIP lifecycle domain — lập kế hoạch và thực thi task dưới governance của AIWS (workspace-based,
  wiki-first HARD GATE, promotion do HUMAN quyết). VERBS: create (soạn AIP PLAN/EXEC/LOCAL, cấp id) ·
  run (start/resume/step/status/list) · init-workspace · point-step · build-step-context.
  Dùng khi: "tạo AIP", "lập kế hoạch", "chạy/tiếp tục task", "nhảy step", "xem status AIP" ·
  "create/run/resume an AIP", "plan this task", "jump to step".
user-invocable: true
---

# SKILL: aiws-aip (domain router)

> Consolidated by CR-AIWS-2026-07-025 — the former per-action skills of this domain are now VERBS of this ONE skill.
> **Old-name translation:** `aiws-aip-<X>` → verb `X` (authority: `product/rename_map.json`).

## Router protocol (MANDATORY)
1. Parse the request → pick ONE verb from the table below (NL triggers).
2. **Read `operations/<verb>.md` (this folder) BEFORE executing** — it is the full, authoritative operation definition; every gate in it stays binding.
3. Verb mơ hồ → HỎI HUMAN (safety rule #6). Router adds NO gates, removes NONE.

## Verb routing table
| Verb | Operation | NL triggers | Params | Key gates (full text in operation file) |
|---|---|---|---|---|
| create | operations/create.md | VN: tạo AIP / cần AIP / lập kế hoạch / tạo plan · EN: create an AIP, plan this task, start task; auto-route before canonical/Truth/wiki authoring, canonical review, audit, CR drafting | --template <id/path> (EXEC/PLAN/LOCAL/APPLY_CR alias, or path — review templates are project-local per CR-AIWS-2026-07-033 T5); internally allocate_aip_id.py --kind exec/plan/local, lookup_wiki_source.py - | HARD GATE artifact lookup + FORBIDDEN glob/path-inference patterns; MANDATORY STEP 0a id allocation (DỪNG hỏi HUMAN if account_info missing, no glob max+1); template STOP-and-ASK never-fallback-EXEC; mandatory self-check + lint_aip 0 errors before reporting do |
| run | operations/run.md | VN: chạy AIP / bắt đầu task / tiếp tục task / nhảy step / xem status AIP / đóng AIP · EN: run/start/resume AIP, resume task, jump to step, AIP status, close an AIP; subverbs start/resume/step/status/list/close | start/resume/step/status/list/close; --title, --step STEP-NN, --task-id, --force (wipes workspace); pre-start lint_aip.py --path; finalize lint_all.py --scope task -- | Pre-start lint 0-errors stop; HARD GATE resolved-inputs lookup + VẪN FORBIDDEN patterns; CR-052 scope/raw authorization halt-and-ask; >1-workspace STOP-and-ask never-silent-pick; CLOSE refuses while any capture is `captured` (non-interactive: prints + rc≠0, never silent defer-all, CR-125); PENDING CAPTURE SWEEP mandatory non-skippable; FINAL CAPTURE SWEEP mandatory non- |
| init-workspace | operations/init-workspace.md | VN: tạo workspace / khởi tạo workspace · EN: init workspace for task; normally auto via run start — manual only when run not used | --task-id TASK-YYYYMMDD-<slug>, --title, --aip, --aip-path, --aip-type, --account, --force; tool init_workspace.py | No reuse without --force; runtime lives in workspace not AIP; capture-first to 08_capture_inbox.jsonl; per-account only-new (legacy flat untouched) |
| point-step | operations/point-step.md | VN: chuyển sang step / nhảy step · EN: point to step, set current step, move to STEP-NN; manual advance without run step; pointer correction | --workspace, --aip, --aip-path, --step-id STEP-NN, --status active/blocked/done; tool set_current_step.py | Never point to nonexistent step; MUST run before build-step-context; status enum active/blocked/done |
| build-step-context | operations/build-step-context.md | VN: tạo active step context / cập nhật step context · EN: build ASC, rebuild context; after pointer moved; normally auto via run | --workspace (pointer mode) or --workspace --aip --step-id (explicit); --digest-lines, --scope-lines; tool build_active_step_context.py | No runtime state into AIP; rebuild on every pointer move; ASC = projection (AIP+workspace remain sources); always read ASC before touching workspace files |
