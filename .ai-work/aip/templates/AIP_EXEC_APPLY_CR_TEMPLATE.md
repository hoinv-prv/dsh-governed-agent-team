---
artifact_type: aip_exec
artifact_id: AIP-EXEC-NNN
title: "Apply <CR-ID> — <short change summary>"
status: draft
# status: (auto) — `aiws-aip run start` flips draft → active (CR-AIWS-2026-07-040); close sets done by hand (draft|active → done).
project: vti-ai-work-system
owner: "<owner>"
plan_source: "Direct execution — apply approved <CR-ID> (status approved_for_ai_update)"
updated_at: YYYY-MM-DD
---

<!-- APPLY-CR EXEC MINI-TEMPLATE (CR-AIWS-2026-05-037 Option C). Lint-conformant by construction: real `### Step:` headings + all required §6.3 sections + the 7 step fields, kept TERSE (one-line fields). Use for tasks that APPLY an already-approved CR. Rule #8 HARD GATE must ALREADY be satisfied (AIWS-Product-Owner approved for AIWS-canonical CRs; Wiki-Manager for wiki CRs — CR-031) BEFORE instantiating. Replace every <…> placeholder and set updated_at to a real YYYY-MM-DD; then `lint_aip.py --path <file>` MUST report 0 errors before `aiws-aip run start` (aiws-aip run now fails fast on lint errors — CR-037 Option A). -->
<!-- DISPATCH NOTE (CR-AIWS-2026-08-014): AIP instantiate từ template này KHÔNG dispatch-eligible
     (CR-AIWS-2026-07-061 §5 — AP-CR-41 chỉ nhận AIP_EXEC_TEMPLATE cho agent run). CR có gate đòi
     agent dogfood/dispatch ⇒ đặt gate đó trong một COMPANION EXEC AIP (AIP_EXEC_TEMPLATE) tạo kèm
     NGAY TỪ ĐẦU, đừng đợi run-gate refuse giữa chừng. Đã vấp ×2 trong 1 phiên: AIP-996→997, AIP-1001→1002. -->
<!-- Stable control: Done Criteria declarative (never tick [x]). Runtime state → workspace. Scope change → Re-plan Log. -->

# AIP_EXEC — Apply <CR-ID>

## SOP Compliance
Theo `.ai-work/truth/SOP_MASTER.md` — Universal Gates: U1 (HARD GATE) → STEP-00; U2 (soft) → Input Understanding; U3 (soft) → Known Open Points.

## Objective
Apply the approved changes of <CR-ID> exactly as authorized, then set the CR `status: applied` with an Apply Outcome. No change beyond the CR's approved scope.

## Execution Scope
### In Scope
- Apply each approved change of <CR-ID> with the correct edit-flow (canonical dual-tree byte-identical; tooling .ai-work→test→product; skills full-content trees only).

### Out of Scope
- Any change not in <CR-ID>'s approved scope; re-deciding settled open_decisions.

## Expected Outputs
- All <CR-ID> changes applied; <CR-ID> `status: applied` + Apply Outcome recorded; this AIP lint-clean.

## Execution Input Package
### Plan Source
- Direct execution; grounded in approved <CR-ID>.

### Required Truth Inputs
- SOP_MASTER §4.1 (CR-before-canonical-change — satisfied by approval); AI_WORK_CONTRACT §5.

### Required Wiki Inputs
| Input | Wiki Source ID | Artifact Path | Ghi chú | Capture flag |
|---|---|---|---|---|
| I-01 Approved CR | (none — direct) | product/change_requests/<CR-ID>.md | authority for every edit | — |

## Input Understanding
| Input artifact | Key understanding | Assumptions | Ambiguities | BrSE confirmed? |
|---|---|---|---|---|
| <CR-ID> | <approved scope = list of changes> | <edit-flow per target type> | <none / list> | ⬜ pending |

## References to Read First
- <CR-ID> (Targets, each Change/Option, Guardrails, apply_gates, must_preserve).

## Current Risks / Constraints
- Dual-tree drift: verify byte-identity per pair after canonical edits (edit-one→cp→diff); never exceed CR scope.
- Concurrent-mutation drift (CAP-065-01): a shared target may change between apply_gates-resolution and the edit; re-anchor before each edit.

## Known Open Points
- Open Points log: workspace `05_open_questions.md`
- (none expected — apply of a settled CR)

## Workspace Execution Rule
Update Active Step Context · Queue · Findings · Open Questions · Draft Output · Capture Inbox as applicable.

## Execution Steps

### Step: STEP-00 — Confirm Task Understanding (HARD GATE)
Objective:
Confirm scope = apply approved <CR-ID> (restate its changes); out-of-scope items excluded; finish by marking the CR applied.
Recommended Mode:
Clarifying
Applicable Guidelines:
- SOP_MASTER Gate U1
- wiki:none — HARD GATE preflight default. Replace with the relevant `product/wiki_guidelines/...` path after running `lookup_wiki_source.py`; keep `wiki:none` only when pre-flight confirms no wiki coverage.
Inputs:
- <CR-ID> (approved); HUMAN directive to apply
Expected Outputs:
- Understanding confirmed (apply-only of approved scope)
Done Condition:
Scope restated and not contradicted by HUMAN.
Notes / Constraints:
- Apply pre-approved scope only; no expansion without a Re-plan entry.

### Step: STEP-01 — Apply <CR-ID> changes
Objective:
Resolve the CR's apply_gates AND verify the CR's DP/decision statements (tree-set, version-targets, file lists) against current repo state — flag any stale assertion before applying (CAP-045-01) — then apply each approved change with the correct edit-flow. (apply_gates verification fixtures MUST be IN-REPO — never a consumer-project artifact — rule #9 / CR-034.)
Recommended Mode:
Canonical-edit
Applicable Guidelines:
- product/wiki_guidelines/core/specs/WIKI_CHANGE_REQUEST_SPEC.md
Inputs:
- <CR-ID> Changes/Options; confirmed edit-target paths
Expected Outputs:
- All changes applied; per-pair byte-identity verified for canonical dual-tree edits
- **Danh sách test file đã grep** (kèm kết luận cho từng file: cập nhật / không liên quan / "đã grep, không có")
Done Condition:
Every approved change applied; apply_gates satisfied; nothing outside CR scope touched.
Notes / Constraints:
- Canonical dual-tree byte-identical; tooling .ai-work→test→product; skills full-content trees only.
- **Test-cùng-apply (lesson ×3, wave 2026-07-14; canonical CR-AIWS-2026-07-035):** TRƯỚC khi edit một tool, grep `.ai-work/tests/` theo tên tool — test đang assert behavior CŨ phải được cập nhật trong CÙNG apply (đừng để gate `test_*`/`quick-install`/`build` của chính CR tự gãy); test file chưa enumerate trong CR → ghi nhận vào Apply Outcome như deviation có lý do. Ở bước VERIFY thì đã muộn: edit xong rồi, biết muộn không cứu được gì.
- **Byte-identical METHOD (CAP-074-01):** edit ONE tree → `cp` to the sibling path → `diff -q` to confirm 0 difference. Do NOT hand-edit both trees.
- **Mirror pre-check (CAP-1055-01 / CAP-1120-05; CR-AIWS-2026-08-127 C8):** TRƯỚC mỗi `cp` mirror chạy `diff -q <.ai-work path> <product path>` (hoặc `git diff --quiet HEAD -- <product path>` khi cây `.ai-work` đã được sửa) — nếu cây sibling ĐÃ KHÁC ⇒ một phiên khác vừa sửa nó: DỪNG, đọc diff, merge tay, rồi mới mirror. `cp` đè xoá hunk của phiên kia mà `diff -q` chạy sau đó vẫn báo 0 (AIP-1055 ‖ AIP-1056 cùng chạm `_common.py`). Trước khi flip CR `applied` chạy lại test của cả hai wave + whole-tree lint.
- **SKILL.md body = dual-tree (CR-037 C2):** edit `.ai-work/procedural/skills/<n>/SKILL.md` → `cp` → `product/procedural/skills/<n>/SKILL.md` (the `product/skills/<n>` pointer is unchanged). **Numbered-test label (CR-037 C2):** if the CR adds a test case, verify the next-free `Tn` against the target file at apply — do not pin a colliding label.
- **Re-anchor before each edit (CAP-065-01):** immediately before each edit, re-read/re-anchor the target's current state (re-grep the OLD wording — do not pin line numbers); a parallel actor may have mutated the shared target since apply_gates were resolved.
- **Mirror dual-tree TRƯỚC mọi bulk rewrite (CAP-934-02):** nếu bước apply có edit tay lên tooling/skill rồi mới chạy scripted sweep toàn repo, phải `cp` + `diff -q` sang cây sibling **ngay sau edit tay** — nếu không, cây chưa mirror vẫn mang nội dung cũ và sẽ bị sweep viết hỏng (AIP-934: exclude string trong `build_aiws_install_package.py` của cây `product` bị sweep phá; phát hiện nhờ replacement-count lệch 25 vs 38).

### Step: STEP-02 — Verify + finalize CR (status applied + Apply Outcome)
Objective:
Run lint to 0 errors; confirm Done Criteria; **pre-close OLD-wording sweep (CAP-010; scope per CR-AIWS-2026-08-095 C1)** — before flipping status, grep the OLD wording being replaced **tree-wide over every shipped surface** (`product/` + `.ai-work/` + `.claude/`), **minus the default carve-outs** listed under Notes — scope is declared by TREE, never by doc type ("SKILL.md + guidelines" missed an Agents Pack process doc: CR-071 C11 → IR-2026-08-17 F17-r); update in-scope hits, classify every remaining hit (intentional provenance vs real residual — only the latter counts, CR-AIWS-2026-08-077 C1); set <CR-ID> `status: applied` and record an Apply Outcome (what / where / evidence) that **quotes the sweep command, its scope and per-group hit counts** — a bare "grep = 0" is not evidence (CR-095 C2, mirror of Spec §11.8/CR-082 at apply time). Then **move the CR file to `product/change_requests/applied/`** (the archive — CR-034).
Recommended Mode:
Reviewing
Applicable Guidelines:
- product/wiki_guidelines/core/specs/WIKI_CHANGE_REQUEST_SPEC.md
Inputs:
- All edited files; <CR-ID>; lint output
Expected Outputs:
- Lint-clean; <CR-ID> `status: applied` + Apply Outcome block
- **Với mỗi `lint_accept`/grandfather trong scope:** output `--show-accepted` đã **enumerate**, đối chiếu từng finding với rule của CR (hoặc kết quả probe âm bản). `accepted=N` là tổng của MỌI rule — đọc nó như con số của rule mình là suy diễn, và suy diễn đó báo xanh.
- **`upgrade_impact` đã khai trong front-matter CR (CR-AIWS-2026-08-102):** `ledger` (kèm mục đã thêm vào `product/UPGRADE_IMPACT_NOTE_next_release.md`) hoặc `none` + `upgrade_impact_reason`. Trả lời NGAY ở đây — lúc cắt release không còn ngữ cảnh để suy lại. Dùng `_common.ships(path)` nếu không chắc target có đi vào payload không.
- **Khối bằng chứng sweep trong Apply Outcome (CR-AIWS-2026-08-095 C2):** lệnh đã chạy (pattern đủ biến thể) · phạm vi (tree-wide trừ carve-out) · số hit theo nhóm *provenance-cố-ý* / *sót-thật* → residual = 0. Một dòng "grep = 0" không kèm lệnh không được tính là bằng chứng.
Done Condition:
lint 0 errors; CR marked applied with Apply Outcome (kèm khối bằng chứng sweep); nothing applied outside CR scope.
Notes / Constraints:
- Pre-existing repo lint debt out of scope.
- **Probe âm bản cho invariant tinh tế** (anchor · thứ tự · encoding · eol · hành vi phụ thuộc platform) — `tooling_authoring_conventions` Rule 13: tạm phá implement → test phải **đỏ** → khôi phục → **xanh**; ghi kết quả probe vào Apply Outcome. Một test luôn xanh **tệ hơn không có test** vì nó được đếm vào "N/N PASS".
- **Apply-order re-read:** grep `related_cr` của CR này **và** của các CR chạm cùng file; CR nào **đã apply sau ngày draft** ⇒ đọc lại vùng chung **trước khi viết code**, ghi kết luận vào Apply Outcome. (Đã có ca một CR khai "apply X trước hoặc batch" rồi vẫn được apply một mình — lần đó vô hại chỉ vì người apply tình cờ đọc code trước, không nhờ cơ chế nào.)
- **Sweep đủ biến thể (CR-AIWS-2026-07-030 C):** retire/rename một khái niệm → OLD-wording sweep phải quét ĐỦ biến thể token (snake/upper/prose, vd `AIP_ROOT`/`aip_root`/`root_aip`/"root AIP") và các surface hay bị quên: preset/sample instances, workspace templates, tham số runtime tooling — không chỉ specs/templates/lint. `dual_tree_drift` = 0 trên footprint trước khi flip `applied`.
- **Sweep carve-out mặc định (lesson AIP-944/945; canonical CR-AIWS-2026-07-035; scope tree-wide CR-AIWS-2026-08-095):** quote-context hits trong `change_requests/` + `intake/` (CR/IR tự trích pattern làm evidence), immutable zones (`history/`, `workspaces/`, `releases/` — rename_map note "NOT rewritten"), `rename_map.json` (chính bản đồ tên cũ) và vùng project-local trong section đã ship (`check_dual_tree.PROJECT_LOCAL_PREFIXES` — desk state `agents/task_desks/`, `agents/instances/`; DP-095-B) KHÔNG tính là hit mới; **mọi thứ còn lại trong `product/` + `.ai-work/` + `.claude/` đều trong phạm vi** — không thu hẹp theo loại doc; hit thật ngoài enumerated + carve-out → DỪNG, bổ sung target/Apply Outcome trước khi sửa.

## Done Criteria
- [ ] All <CR-ID> approved changes applied with the correct edit-flow
- [ ] Canonical dual-tree edits byte-identical per pair (edit-one→cp→diff)
- [ ] CR DP/decision statements verified against repo state at apply time; stale assertions flagged (CAP-045-01)
- [ ] Each edit re-anchored against the target's current state immediately before applying (CAP-065-01)
- [ ] Pre-close OLD-wording sweep run **tree-wide minus carve-outs**; no stale copy of replaced wording remains anywhere in scope (each remaining hit classified provenance vs residual) (CAP-010; CR-AIWS-2026-08-095 C1)
- [ ] Apply Outcome **quotes the sweep command + scope + per-group hit counts** — "grep = 0" without the command is not evidence (CR-AIWS-2026-08-095 C2)
- [ ] <CR-ID> set to `status: applied` with an Apply Outcome
- [ ] This AIP passes lint_aip with 0 errors
- [ ] **Đã grep `.ai-work/tests/` cho mọi tool bị đổi behavior**; danh sách test file + disposition được ghi lại (T6)
- [ ] **Với mỗi `lint_accept`/grandfather trong scope: `--show-accepted` đã enumerate**, không suy diễn từ con số tổng (T7)
- [ ] **NẾU** CR chạm một invariant tinh tế (anchor · thứ tự · encoding · eol · platform) → **đã chạy probe âm bản** và ghi kết quả vào Apply Outcome. Không có invariant loại đó → ghi "N/A" kèm lý do một dòng (Rule 13; DP-023-C)
- [ ] Nothing applied outside <CR-ID>'s approved scope
- [ ] **Gate U1/U2/U3** satisfied

## Self-check / Review Points
- Apply_gates resolved before editing? CR DP/decision statements verified vs repo (CAP-045-01)? Each edit re-anchored just before applying (CAP-065-01)? Byte-identity verified per pair via edit-one→cp→diff (CAP-074-01)?
- Pre-close OLD-wording sweep run tree-wide (`product/` + `.ai-work/` + `.claude/`, minus carve-outs), not just the CR's listed files or one doc type (CAP-010; CR-095 C1)? Apply Outcome quotes command + scope + hit counts (CR-095 C2)?
- CR status=applied with a concrete Apply Outcome? No scope creep?

## Finalization Notes
- After apply, <CR-ID> lifecycle is complete (draft → approved_for_ai_update → applied).

## Pre-flight Pending Captures
- (none)

## Re-plan Rule
Macro scope/output change → explicit Re-plan Log entry + evidence before editing AIP.

## Re-plan Log
- (no re-plan yet)
