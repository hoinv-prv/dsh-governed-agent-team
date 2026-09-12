# AP-CR Ledger (CR-AIWS-2026-08-001 — DP-990-B Option A, ledger-lite)

> **Namespace `AP-CR-*` là của upstream AIWS agents pack.** Downstream KHÔNG mint id trong namespace
> này — raise IR upstream (CR Spec §18) + dùng namespace local riêng. Ledger này là registry-lite để
> mọi bên check collision TRƯỚC khi tham chiếu; seed 2026-08-05 từ grep các surface đã ship
> (`tooling/run_agent.py`, `commands/*.md`, `docs/*`, `README.md`). Id không có file CR riêng — AP-CR
> lịch sử sống dưới dạng reference trong docs/code. **Cao nhất đã cấp: AP-CR-41.** Cấp id mới = thêm
> row ở đây TRONG CÙNG thay đổi.

| ID | Nội dung (1 dòng) | Status | Referenced tại |
|---|---|---|---|
| AP-CR-10 | Promotion staging → canonical | **fulfilled** — CR-AIWS-2026-06-055 (2026-06-24); docs formalized CR-AIWS-2026-08-036 | agent_runtime_design.md §7 |
| AP-CR-13 | Capture tier-up lên Task Workspace inbox | applied | run_agent.py:563 |
| AP-CR-19 | Run/feedback command set (surface B) | applied | run_agent.py:12; aiws-agent-run.md |
| AP-CR-20 | `start` subcommand | applied | aiws-agent-run.md §start |
| AP-CR-21 | `/aiws-agent-feedback` | applied | aiws-agent-feedback.md; agent_runtime_design.md §5 |
| AP-CR-22 | `list`/`memory` subcommands + fuzzy instance resolve | applied | run_agent.py:12,26; aiws-agent.md |
| AP-CR-23 | Fuzzy resolution (partial id/role/display_name) | applied | run_agent.py:26,137; aiws-agent-create.md |
| AP-CR-24 | PROMOTION-EXCLUDES invariant | applied | promotion_readiness_note.md §3 |
| AP-CR-25 | `aip_driven` gate — refuse start without `--aip` (presence, before scaffold) | applied | run_agent.py:1360; aiws-agent-run.md:15 |
| AP-CR-26 | Relevance-scoped confirmed-memory loading (digest/hints) | applied | run_agent.py:205,588; aiws-agent-review-learning.md |
| AP-CR-27 | `upgrade` verb (blueprint drift reconcile) | applied | run_agent.py:21; aiws-agent-upgrade.md |
| AP-CR-28 | `clone` verb | applied | run_agent.py:22; aiws-agent-clone.md |
| AP-CR-29 | Two-track `.aiws-staging` install | **superseded** (CR-AIWS-2026-06-055/049 single-track) | README.md:19,44 |
| AP-CR-30 | `rename` verb + `previous_ids` alias | applied | run_agent.py:23; aiws-agent-rename.md |
| AP-CR-31 | Governance-invariant floor + process_improvement_candidate | applied | lint_agents.py:5; learning_candidate_schema.md |
| AP-CR-35 | (nội dung không tra được từ surface — internal) | unknown | run_agent.py:257 |
| AP-CR-36 | (nội dung không tra được từ surface — internal) | unknown | run_agent.py:285; aiws-agent-create.md:87 |
| AP-CR-39 | Run templates ship EMPTY + example rows | applied | learning_candidate_schema.md:5 |
| AP-CR-41 | Template-conformance gate (consume `template_source`; `--strict-template`) | applied | run_agent.py:1280; aiws-agent-run.md:28 |
| (11-12, 14-18, 32-34, 37-38, 40) | Không referenced trên surface đã ship — coi như đã đốt (không tái sử dụng) | burned/unknown | — |
