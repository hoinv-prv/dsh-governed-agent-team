# Capture and Triage Rules

## Principle
Capture first, curate later.

## Flow
Runtime discoveries → Capture Inbox → Triage → Promote / Archive / Discard

## Safety rules
- do not promote directly to Truth by default
- if unsure between Curated and Reference → choose Reference
- if unsure between Curated and Truth → choose Curated

## AIP closing — capture/triage-related items

Trước khi flip AIP `active → done` (bổ trợ aiws-aip run SKILL §"When closing an AIP"):
- **Final Capture Sweep (mandatory):** review toàn bộ diffs/findings/execution artifacts của AIP; append candidates còn sót vào `08_capture_inbox.jsonl`; log closing-check summary vào workspace findings — không skip dù task đơn giản hay inbox đã nhiều entries.
- **Untriaged check:** `aiws-aip run close <AIP-ID>` — mọi item còn `status: captured` phải được xử lý trước khi flip `active → done`, theo **đúng hai đường**: (a) triage ngay (`promoted` / `discarded` / `retained_local`), hoặc (b) `defer` **kèm lý do**, row đi vào **Capture Backlog** (`.ai-work/capture_backlog/<account_id>.jsonl`) và inbox row giữ `deferred_to: <backlog_id>`. **Không còn đường thứ ba**: đường cũ không nêu được đích nên không phải một địa chỉ — đo 2026-08-27: 76 row đã đi đường đó, **0** row nói được đích. `run close` từ chối flip khi còn row `captured` (`build_aip_index.py --list-untriaged` liệt kê repo-wide; `triage_capture.py list` xem backlog).
- **Attribution cross-check (phía capture/triage):** target spec attribute thay đổi cho AIP-ID mà Re-plan Log im lặng → bổ sung Re-plan entry trước khi flip status; capture được `promoted` trong AIP phải có `source_refs` (CR-AIWS-2026-06-029).

## Consumer map — who triages each `candidate_kind`, and what it becomes (CR-AIWS-2026-08-126 C3)

A capture only improves something if somebody owns it and it turns into an artifact. One row per family:
**family → default scope → who triages → what it becomes**.

| `candidate_kind` | default scope | consumer (who triages) | becomes |
|---|---|---|---|
| `retrieval_improvement` | project | Wiki-Manager | lookup keys · alias · index entry |
| `process_doc_gap` | aiws | AIWS-PO | procedural doc · SOP · AIP/workspace template (CR) |
| `reusable_pattern` | project ∣ aiws | playbook owner | playbook section · task-lens preset |
| `tooling_opportunity` | aiws | tooling owner | a tool change (CR) |
| `wiki_quality_issue` | project | Wiki-Manager | meta refresh · wiki CR |
| `authoring_lesson` | project ∣ aiws | owner of that artifact family | authoring guideline · checklist · operating memory L2 |
| `tool_gotcha` | aiws | anyone | operating memory L2 |
| `decision_or_convention` | project | project owner | project rules · QA memory · operating memory |
| `spec_impl_drift` | aiws | AIWS-PO | a CR fixing the doc **or** the code |
| `review_rule` | project ∣ aiws | checklist owner | review checklist item · review preset |
| `wiki_knowledge_gap` | project | Wiki-Manager | new source registration · meta |
| `relation_or_object` | project | Wiki-Manager | Relations Enrichment CR batch |
| `deliverable_defect` | project | design / review owner | project checklist item · project-local CR |
| `output_quality_feedback` | project | owner of that output type | template · checklist · guideline |
| `qa_candidate` | project | Wiki-Manager | meta edit first; QA memory only if it does not reduce to one |

`qa_candidate`'s row **restates** the meta-first precedence rule below rather than replacing it.

**Where each scope sends work.** `improvement_scope: project` → project checklist · project rules ·
`.ai-work/change_requests/` (project namespace) · Wiki-Manager. `improvement_scope: aiws` → an AIWS CR
when working in this repo, or an **IR** under `.ai-work/upstream_requests/` when working in a deployed
project.

Per-family detail belongs in the `capture_triggers/<slug>.md` fragments, following the playbook's own
additive procedure (new fragment + one table row; never edit an old fragment).

**A project may add its own kinds** — namespaced, in `.ai-work/project_profile.yml` under
`capture_kinds:`. It may add a **kind**; it may not add a `type` or a `suggested_target`, because those
are the pipelines lint and routing understand. Project-specific destinations go in `target_artifact`.

### Two routing surfaces, and which governs what (C6)

This map governs the **Task-Workspace** inbox, keyed on `candidate_kind`. The agents-pack file
`.ai-work/agents/agents/blueprints/_shared/common/capture_routing_rule.md` governs the **agent-desk →
Task-Workspace tier-up**, keyed on `type`. They are two surfaces over one inbox, so each points at the
other rather than restating it.

**Do not conflate these two rows** — they name near-identical things in *different fields*:

| | field | rule |
|---|---|---|
| desk table | `type` | `process_improvement_candidate` is **desk-only, never tier-up** |
| this map | `candidate_kind` | `process_doc_gap` is a live family with 43 in-repo records |

Neither implies the other. A desk candidate whose `type` is desk-only can still become a TW capture
under a perfectly valid `candidate_kind`; the desk rule is about which *type* crosses the bridge.

## Triage qa_candidate — precedence meta-first (CR-AIWS-2026-07-009)

Khi triage capture `type: qa_candidate` (fields question/answer/qa_kind/asked_by — CR-008):
1. **Meta-first:** answer quy về được meta edit (lookup_keys/summary) hoặc relation edge → promote VÀO ĐÓ (wiki flow thường), KHÔNG vào QA store — tránh second-truth-surface.
2. Chỉ khi answer KHÔNG quy về meta/relation/kit edit → HUMAN confirm → append `.ai-work/wiki/qa_memory/confirmed_qa.jsonl` (schema: `QA_Memory_Spec_MVP.md` §3; `confirmed_by: HUMAN` bắt buộc; `asked_by: ai` càng bắt buộc confirm — rule #7).
3. Capture gốc → `status: promoted` + `source_refs` trỏ QA-id. Store RỖNG mặc định; AI không bao giờ tự append.

## Promote L1 → L2 (Operating Memory) — CR-AIWS-2026-08-022

Bài học **vận hành** (loại 2 — chỉ cần nhớ, không cần tuân thủ) đi vào Operating Memory, không vào
canonical doc. Mô hình + taxonomy: `operating_memory.md`.

**Ghi vào L1** (Personal Notebook) là **tự do, không gate** — ghi đắt thì không ai ghi.

**Lên L2** (`.ai-work/memory/`, chia sẻ cả đội) cần đạt **≥2 trong 3**:
- **(a)** đã cắn **nhiều hơn một lần**, hoặc cắn nhiều hơn một người;
- **(b)** người khác **không thể tự suy ra** từ code/spec;
- **(c)** tiết kiệm thời gian **đo đếm được**.

Không đạt thì giữ ở L1 — đó là chỗ đúng của nó, không phải chỗ tạm.

**Rà định kỳ (khi bước đọc phát WARN quá ngưỡng):** mỗi mục quá hạn **buộc chọn một** — *nâng lên
canonical* (nó đã chứng minh là quy tắc ⇒ thành loại 1) · *giữ* (còn đúng, cập nhật `verified_at`) ·
*xoá* (hết đúng hoặc hết cần). Không có lựa chọn "để đó": một kho chỉ-thêm sẽ ngừng được đọc.

> Operating Memory **không phải nguồn thẩm quyền**. Một mục cần được *tuân thủ* thì thuộc loại 1 —
> promote lên canonical qua CR, đừng để nó nằm ở L2 và bị trích như căn cứ.

## Verification discipline (CR-AIWS-2026-07-043)

Six rules. Each one exists because skipping it already cost a wave. Operationalises
`AIWS_Change_Request_Spec_MVP` §17 (source-basis) — a claim is evidence only when it was verified
the way the rule says.

### VD-0 — External / downstream IR (adversarial verify)
An external or downstream **improvement-request (IR)** describes THAT project's state, not
necessarily this canonical's. Before folding ANY IR claim into a plan or CR:
- **Verify each claim against canonical** (file/line) — confirm the named file/symbol/token
  actually exists and behaves as claimed.
- **Reject or annotate** false premises; fold in **only verified** claims.
- Evidence: AIP-082 demo IR — 3/5 claims carried false premises (wrong linter file, phantom tokens/targets).

### VD-1 — Delegated work: self-report is NOT evidence
Content an AI subagent **re-authors / migrates / rewrites** MUST pass an **independent adversarial
intent-preservation verify** (read OLD vs NEW, enumerate dropped items, quote the old file verbatim).
An agent's own `preserved_everything=true` is **never** evidence. On failure: repair pass with an
explicit dropped-items checklist, then re-verify.
- Evidence: CR-039 re-authored 5 presets via subagents — **all 5 self-reported success**, independent
  verify caught **3 as intent-lossy** (CreateChat dropped 12 items incl. ISMS/PII handling and the
  two-language design; CreateMail dropped 10).
- **Parity leg:** when ≥2 artifacts of the same family are authored **in parallel**, add a **parity
  post-stage** — mechanically diff file-list / sections / registry fields against the sibling before
  accepting the work (parallel fan-out drifts silently).

### VD-2 — Verify by EXECUTION, not by reading code
A CR **we draft ourselves** whose root-cause claim describes **tool behavior** must be verified by
**running the tool** — the command and its output go into §4 Source basis. Reading the code is not
enough.
- Evidence: CR-061 shipped with a false root-cause premise; a single execution refuted it (the
  seed/subprocess indirection was invisible to static reading).

### VD-3 — Existence / inventory claims
Any claim that a file / skill / tool **exists** (or does not) must be verified with a glob/ls/git
command anchored to an **absolute path inside the target repo**. Skill and file lists that appear in
**session or environment context are NOT evidence** — a multi-root IDE workspace surfaces other
projects' files.
- Evidence: AIP-920 — 2 of 3 agents claimed a skill existed "in 3-4 skill trees of this repo"; it
  belonged to a different project visible through the IDE workspace.

### VD-4 — Verify panel before promoting an IR/CR
Before promoting a **substantive** IR or CR, run ≥1 **verify panel**; for CR waves / substantive
changes run **≥2 rounds with rotated lenses** (round 1: accuracy-vs-repo · governance-feasibility ·
completeness → round 2: coherence · apply-ability · simpler-alternatives).
- Evidence: 27 findings (IR-912); 2 blockers + 6 majors (IR-913); 3 HIGH that round 1 missed (AIP-914)
  — the *apply-ability* and *simpler-alternatives* lenses systematically catch what self-review does not.

### VD-5 — Content / count claims: read the SOURCE, not a rendering of it
A claim about **content, bytes, or counts** is evidence only when taken from the **source itself**,
never from a **presentation** of the source. Four legs:
- **(a) Tool output ≠ the bytes in the file.** Search tools escape as they see fit. To claim anything
  about a backslash, an escape or a unicode character: **read the bytes**, or import the module and
  read the real value. Windows paths are where this bites first.
- **(b) Two already-changed copies compared to each other ≠ compared to the original.** Diffing
  `.ai-work/` against `product/` when **both** were transformed shows them "consistent" and still
  wrong; the correct comparison is **worktree vs HEAD blob**.
- **(c) An aggregate ≠ an enumeration.** `accepted=N` or "N/N PASS" folds in **every** rule; reading
  it as your rule's number is inference, not measurement. Enumerate (`--show-accepted`) or run a
  negative probe.
- **(d) A document you wrote yourself is still a source that must be checked.** A sentence of the form
  *"this is already covered in X"* needs one grep — **including when X is something you authored in
  this same session**. "I wrote it so I know it" is the easiest place to slip, because nobody doubts it.
- Evidence (2026-08-07, all three in one session): (a) reading `PAYLOAD_MAP` through grep output showed
  `\a` and was reported to the HUMAN as a real escape bug — the file uses `/`, and the mistake doubled
  when that literal was typed into a new test, testing the string just typed rather than the one in the
  file. (b) EOL measured by comparing two working-tree copies read clean; comparing against HEAD exposed
  **8** churned files. (c) lint printed `accepted=5`, inferred as "5 legacy accepts" — `--show-accepted`
  showed 3 pre-existing **+ 2 from the very rule under test**.
- Evidence for (d) (2026-08-12, apply CR-AIWS-2026-08-026): a findings note claimed an operating
  requirement was *"already in the guide §2/§8"*; grep returned **0 hits** for all three related terms.
  The guide had been authored by the same session, minutes earlier.

**Boundary vs VD-3.** VD-3 handles claims of **existence** (does a file/skill exist) and bans
session/environment context as evidence. VD-5 handles claims about **content and numbers** and bans a
rendering or an aggregate as evidence. They complement each other; neither replaces the other.
## Từ vựng capture — tiêu chí thêm, và nhịp rà giá trị chết (CR-AIWS-2026-08-085 C3)

`CAPTURE_TYPE_ENUM` từng **vừa thiếu vừa chết** cùng lúc: 8 giá trị đang dùng nằm ngoài enum, trong khi
4/16 giá trị trong enum chưa từng được dùng (đo 2026-08-17: 326 inbox / 573 record). Một enum chỉ-thêm
sẽ phình mãi, và **mỗi giá trị chết là một lựa chọn sai mà người ghi có thể nhầm vào** — chi phí thật,
không phải rác vô hại.

### Thêm một giá trị — ngưỡng (DP-084-D)

- **≥3 record đang dùng thật, ở ≥2 workspace.** Đo bằng cách quét
  `.ai-work/workspaces/**/08_capture_inbox.jsonl`, không bằng cảm giác "chắc sẽ cần".
- **Không trùng nghĩa** một giá trị đã có. Nếu phân biệt được bằng một câu thì nó là giá trị mới; nếu
  phải giải thích một đoạn thì nó là **từ đồng nghĩa** — gộp, đừng thêm.
- **Ngoại lệ phải ghi lý do, không hạ ngưỡng.** Tiền lệ: `gotcha_candidate` được thêm với 2 record/1
  workspace vì (a) nó nằm ở workspace **đang hoạt động** và (b) không giá trị nào phủ nghĩa "bẫy phải
  nhớ" — `insight` quá rộng, `tooling_opportunity_candidate` hàm ý *sửa được*.

### Rút một giá trị — hai nhịp (DP-084-C)

0 record **trong repo này** không có nghĩa 0 ở bản cài downstream, mà downstream thì không đo được từ đây.
Nên rút làm hai nhịp:

1. **Nhịp 1** — thêm vào `CAPTURE_TYPE_DEPRECATED`: `append_capture` **từ chối ghi mới**, còn
   `lint_workspace` **vẫn chấp nhận** record cũ. Không dữ liệu nào thành invalid.
2. **Nhịp 2** (một release sau) — bỏ hẳn khỏi `CAPTURE_TYPE_ENUM`.

### 0 record CHƯA phải bằng chứng để xoá

Kiểm **hạ tầng** trước khi kết luận một giá trị đã chết. Tiền lệ: `qa_candidate` có 0 record nhưng
`.ai-work/wiki/qa_memory/` tồn tại (`README.md` + `confirmed_qa.jsonl`) và 3 procedural doc nhắc tới nó
— đó là **kênh chưa ai đi**, không phải rác. Xoá nó là chặn một con đường, không phải dọn dẹp.

### Khi không giá trị nào hợp

Chọn giá trị **gần nhất** và ghi ý định vào `candidate_kind`, rồi mở CR theo ngưỡng ở trên. **Đừng**
chọn một giá trị sai nghĩa cho xong: giá trị off-enum ít nhất còn hiện ra dưới dạng lint WARNING, còn
một giá trị sai-nhưng-hợp-lệ thì **biến mất khỏi mọi phép đếm** — kể cả phép đếm dùng để quyết định nới enum.
