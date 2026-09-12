# AIWS Change Request Spec (MVP) — v0.1

> **Status:** canonical methodology spec (MVP). **Authority:** the general, AIWS-wide standard for how Change Requests (CRs) are written, governed, approved, and applied for **all canonical AIWS documents**. `WIKI_CHANGE_REQUEST_SPEC` is the **wiki-meta-specialized profile** of this spec (see §18).
> **Placement:** `product/methodology/ai_work_system/20_specs/AIWS_Change_Request_Spec_MVP.md`.

## 1. Purpose & scope

A **Change Request (CR)** is the sanctioned, reviewable unit by which canonical AIWS content is changed. This spec defines the CR's structure, governance, and lifecycle for **every canonical AIWS doc type**:

- **Truth** — `SOP_MASTER`, `AI_WORK_CONTRACT`.
- **Methodology & MVP specs** — `product/methodology/**` (incl. this spec).
- **Guidelines & wiki_guidelines** — `product/guidelines/**`, `product/wiki_guidelines/**`.
- **AIP templates** — `product/aip_templates/**`.
- **Procedural docs & doc-bearing skills** — `product/procedural/**`, the body of `*/SKILL.md`.

Drafting a CR is the sanctioned governance **entry point** (it is not itself a canonical edit). Applying a CR changes canonical content and is gated on AIWS-Product-Owner approval (§15).

## 2. When a CR is required (governance boundary)

| Surface | Class | Rule |
|---|---|---|
| Any canonical `product/` doc (specs, guidelines, methodology, wiki_guidelines, AIP templates, procedural, SKILL.md **body**) | **`cr_required`** | CR + AIWS-Product-Owner approval before apply (safety rule #8 / SOP §4.1). |
| Truth (`SOP_MASTER`/`AI_WORK_CONTRACT`) | **`cr_required`** | As above; highest precedence content. |
| **Lint rules** (pass/fail or diagnostic logic) | **`cr_required`** | Frozen by CR-037 — even though they live in tooling code, a rule/diagnostic change is CR-routed. |
| Tooling code (dual-tree `.ai-work/tooling` ↔ `product/tooling`), excluding lint rules | **`no_cr`** | Tooling-edit-flow: edit `.ai-work` → verify → mirror byte-identical to `product`. AIP may still be required by project rule. |

> **Output-contract exception (CR-AIWS-2026-07-043).** A `no_cr` tooling change that alters a tool's **output format/contract** (a table, a JSON schema, a message that docs or SKILL bodies quote) is only `no_cr` for the *code*. Before applying, grep canonical docs + SKILL bodies for surfaces that **pin** that format; every surface found is `cr_required` and MUST be listed in §2 Target — the CR becomes **mixed**. *(Proven: CR-054 — `wiki_meta.py --view` output was pinned in 3 canonical surfaces; missing them would have under-scoped the apply, §9.)*
| AIP files, runtime workspace state | **`no_cr`** | Not canonical product; AIP Re-plan Log / workspace are the record. |

- **`mixed`** — a CR whose content spans both classes labels each surface explicitly (e.g. a spec note = `cr_required` + a SKILL.md sweep = `no_cr` dual-tree).
- **Drafting any CR is always `no_cr`** (the entry point), regardless of what it later applies.

## 3. Foundational principles

- **3.1 No direct canonical edits from an ad hoc finding.** Canonical changes flow through a CR.
- **3.2 AIWS-Product-Owner controls the update.** Apply requires explicit approval **and** an explicit request to apply (an approved CR alone is insufficient — SOP §5 Rule C). AI never self-approves nor self-applies.
- **3.3 Output-driven by default.** A CR proposes a concrete change with evidence, not open-ended discussion.
- **3.4 AI-executable.** A CR is specific enough that an apply-AIP can execute it deterministically (exact targets, before/after, guardrails).

## 4. AIWS change_type vocabulary

Practical, extensible set (pick the closest; add a clear new value + rationale if none fits):
`add_curated_knowledge` · `modify_spec` · `add_spec` · `refine_lint_precision` · `tooling_update` · `process_template_update` · `guideline_update` · `governance_rule` · `deprecate` · `migrate`.

(The wiki profile keeps its own wiki-meta-specific `change_type`/`target_layer` enums — §18.)

## 5. CR structure

### 5.1 Frontmatter
`cr_id` · `title` · `request_type` · `change_type` · `requester` · `reviewer_or_product_owner` · `status` · `created_at` · `needs_human_confirmation_after_draft` · `driving_source` · `related_cr` (optional list).

### 5.2 Body sections
`Context` · §1 Request identity · §2 Target · §3 Requested change · §4 Source basis · §5 Proposed update direction · §6 Guardrails · §7 Maturity/grounding · §8 §15 propagation checklist · §9 Governance Note · §10 Alternatives weighed · **Apply Outcome** (added at apply) · **Revision History**.

## 6. Field reference (essentials)

- **`cr_id`** — `CR-AIWS-YYYY-MM-NNN` (§10 allocation). **`title`** — one line, names the change + drivers.
- **`request_type`** — coarse class (`tooling_update` / `process_template_update` / `spec_change` / …). **`change_type`** — §4 vocabulary.
- **`reviewer_or_product_owner`** — usually `aiws_product_owner`. **`status`** — §16 lifecycle.
- **`driving_source`** — where the change came from (capture id, triage report, re-plan, IR) — verbatim/traceable.
- **`related_cr`** — sibling CRs sharing target files or lineage (see §11.1, §11.2).
- **`needs_human_confirmation_after_draft: true`** — drafting applies nothing.

## 7. Minimal mandatory fields

A conformant CR MUST carry: `cr_id`, `title`, `request_type` (or `change_type`), `requester`, `reviewer_or_product_owner`, `status`, a **Target** (every path), a **Requested change** (summary + reason + expected outcome), and a **Source basis**. Missing any → not ready for review.

**Upgrade-impact khai LÚC APPLY (CR-AIWS-2026-08-102).** Khi chuyển `status: applied`, CR MUST mang thêm
`upgrade_impact: ledger | none`, và `upgrade_impact_reason: <lý do>` khi giá trị là `none`.
`ledger` = adopter thấy thay đổi này ⇒ phải có một mục trong `product/UPGRADE_IMPACT_NOTE_next_release.md`.
`none` = adopter không thấy (vd toàn bộ target nằm trong exclusion set của payload) ⇒ ghi lý do ngay tại đây.

Vì sao khai lúc **apply** chứ không lúc cắt release: thông tin để trả lời (CR chạm path nào, path đó có
ship không) chỉ đầy đủ ở thời điểm apply, còn `release-checklist` chạy **một lần**, nhiều ngày sau, thường
bởi người khác. Đo 2026-08-18: **5/10** CR applied kể từ build `v1.2.0` không có mục ledger nào, cả 5 đều
sửa bề mặt có ship, và **không lệnh nào đỏ**. Helper trả lời câu "path này có ship không": `_common.ships()`.
Enforced by lint WARN `cr_upgrade_impact_unset` / `cr_upgrade_impact_missing_entry`.

**Register-new-canonical-doc (CR-AIWS-2026-07-043).** A CR that CREATES a new canonical doc (guideline / spec / procedural doc that ships to target projects) MUST either (a) register a Wiki Source Meta for it and reproject the index **in the same apply**, or (b) **defer explicitly** with a reason in §15. A canonical doc without a meta is invisible to `lookup_wiki_source` — every later wave has to hand-point its path. Enforced by lint WARN `canonical_doc_unregistered`.

## 8. Lightweight CR form

For a small, fully AI-executable change, the body may collapse to: Context + Target + Requested change (before/after) + Source basis + Guardrails + a one-line §15 N/A. Frontmatter mandatory fields still apply. (Larger or node-model/vocab changes use the full §5.2 body.)

## 9. Targets & dual-tree apply discipline

- **Enumerate every touched path** in §2 Target (no "etc.").
- **Dual-tree:** tooling and SKILL.md-body changes apply byte-identical to both trees (`.ai-work/...` ↔ `product/...`); verify `diff -q`. For a **SKILL.md body** edit, §2 Target MUST list **both** `.ai-work/procedural/skills/<name>/SKILL.md` **and** `product/procedural/skills/<name>/SKILL.md` (the `product/skills/<name>/SKILL.md` pointer is unchanged) — listing one tree under-scopes the apply *(CR-AIWS-2026-06-037 C2)*.
- **Pair classes — not every twin is byte-identical** *(CR-AIWS-2026-07-043; mirrors the classes `check_dual_tree.py` already implements)*:
  | Class | Examples | Guardrail a CR may claim |
  |---|---|---|
  | **mirror pair** | tooling `.ai-work/tooling/x.py` ↔ `product/tooling/x.py`; SKILL bodies; canonical spec ↔ `product/` mirror | **byte-identical** — verify `diff -q`; `dual_tree_drift = 0` |
  | **source ↔ template pair** | project instance (`.ai-work/wiki/reference/document_search_guidelines.md`) ↔ shipped template (`product/wiki_guidelines/install/*.template.md`) | **semantic correspondence only** — state WHICH parts must stay in sync and verify by targeted diff. **Claiming byte-identity here is a spec violation** (CR-052 over-claimed exactly this). |
  | **generated / skip** | bundles produced at build time (e.g. `payload/aiws_wiki/`) | not a dual-tree pair — no guardrail |
- **Re-anchor before edit; never pin line numbers** — re-grep OLD wording at apply (it may have drifted). Run a pre-close OLD-wording sweep.
- **Sweep every token variant + forgotten surfaces** *(CR-AIWS-2026-07-030)* — when a CR retires/renames a concept, the OLD-wording sweep MUST cover ALL token variants (snake/upper/prose — e.g. `AIP_ROOT` / `aip_root` / `root_aip` / "root AIP") AND the surfaces single-token greps miss: preset/sample instances, workspace templates, runtime-tooling parameters, prose mentions — not just specs/templates/lint. (Proven: the CR-026 apply sweep caught 4 target groups the intake had missed.)
- **Draft-time sweep for retire/rename CRs** *(CR-AIWS-2026-08-034; lesson CR-AIWS-2026-08-031)* — a CR that retires/renames a concept MUST run the SAME full-token-registry sweep as its apply gate **at draft time** (every variant: EN + VN prose, hyphen AND underscore forms, CLI-flag forms) and fold every live hit into §2 Target. Do not leave discovery to the apply-gate sweep. *Real case:* CR-031's draft survey missed `object_id` and the hyphenated `--canonical-object-refs`; 7 live surfaces surfaced only at apply and had to be handled as deviations.

## 10. id & registry discipline  *(OP-A, ruled 2026-06-19)*

- **`cr_id = CR-AIWS-YYYY-MM-NNN`. NNN is MONTH-SCOPED** — unique within `YYYY-MM`, restarting each month (de-facto: May 2026 ran 002–038; June 2026 restarted at 001).
- **Mint with `allocate_cr_id.py` — MANDATORY when the tool is present** *(CR-AIWS-2026-08-020)*. Run `py .ai-work/tooling/allocate_cr_id.py` at draft time and **re-verify immediately before writing the CR file**; the manual union scan below is the **fallback only** for environments without the tool. Rationale: a compliant manual scan is not atomic — same-day parallel sessions minted `013..018` AFTER a compliant scan and forced a renumber (`CR-AIWS-2026-08-019` r3); the tool re-reads disk ∪ `git log --all` at invocation. Caveat (tool docstring): unfetched sibling clones need `git fetch --all` before minting.
- **Allocate cross-branch — never single-branch `max+1`.** In a multi-branch program, CR ids (and AIP ids) are allocated against an **authoritative view across all branches** (e.g. `git log --all` scan, or `allocate_aip_id.py` for AIP ids). A single-branch `max+1` causes collisions: **CAP-001** — `CR-025` was independently used on two branches for different content, and a hand-picked AIP id (`114/115`) collided with sibling branches, forcing a renumber.
- **Do not pin a not-yet-existing sibling id** (CR or AIP) — reference by stable description + the stable id you do have (see §11).
- Burned/superseded ids are not reused (record supersession instead).
- **Enforced since CR-AIWS-2026-07-071:** lint **ERROR `duplicate_cr_id`** fails the tree when two CR documents carry the same `cr_id` (Lint_and_Tooling_Spec §21). It is **detection, not prevention** — it only fires once both documents sit in the tree being linted, so it catches vector (b) below at merge/lint time and nothing else. The three ways a collision is actually born: **(a)** two people/sessions drafting on the **same branch** — `allocate_cr_id.py` is a *scanner, not a claim*, so consecutive calls return the same id until a file exists on disk (use `--count N`, or write each file before allocating the next); **(b)** branches not yet fetched from each other, which `git log --all` cannot see; **(c)** a **downstream project** minting an upstream-namespace id, which no upstream lint can ever see — addressed at the source by §18's request-folder convention. Prevention for (a)/(b) — mandatory fetch or a central ledger — remains open (CR-AIWS-2026-07-071 §7 residual).
- **Scan working-tree ∪ git — never committed-only or counter-only** *(CR-AIWS-2026-06-037 C1)*. A `git log` scan of only the current checkout, or a counter-only allocate, misses ids **applied concurrently / just-committed on another branch / uncommitted in another worktree** — exactly how `CR-AIWS-2026-06-034` collided (renumbered → `035`). Union (a) the working tree on disk (`product/change_requests/**` + `.ai-work/aip/**`, incl. `applied|drafts|rejected`), (b) `git log --all`, (c) the counter. `allocate_aip_id.py` now unions disk + `git log --all` + counter and tolerates `-slug` artifact_ids.

## 11. CR-authoring conventions  *(absorbed from AIP-093)*

- **11.1 Concurrent-CR coordination (CAP-073-02; sharpened CR-AIWS-2026-07-043).** Before finalizing a draft CR, grep open/draft CRs — **including CRs drafted in the same session/wave, and CRs already APPLIED in that same wave/day** — for **shared EDIT/apply targets**: files that BOTH CRs actually **modify** (i.e. appear in both §2 Target tables). A file merely *cited* (governance note, example, future extension point) is **NOT** an overlap and must **not** produce a `related_cr` — over-counting invents apply-sequencing that does not exist. On a real overlap, add a reciprocal `related_cr` noting region-ownership and that **apply must be coordinated/sequenced**. A same-day **applied** CR may have already changed your target, which silently turns your change block into a **no-op** at apply time — so grep `change_requests/applied/` filtered to the current wave, not just open/draft. *Real case:* CR-AIWS-2026-08-036 C11 was drafted against a README that CR-AIWS-2026-08-035, applied the same day, had already replaced with a stronger tombstone; the block applied as a no-op. (Complements §12's within-CR propagation with across-concurrent-CR coordination.)
- **11.2 Stable sibling-refs (CAP-073-01).** When a CR references a sibling CR's edit, anchor on a **stable region description + the sibling's `cr_id`**, never the sibling's internal change-number (`Cn`, unstable until applied).
- **11.3 Defer-to-apply-AIP (CAP-055-03).** A CR Apply-Outcome that defers work references **"the apply AIP for this CR"**, never a specific not-yet-existing AIP id (the `cr_id` is stable; the applying-AIP id is not).
- **11.4 Numbered-test labels (CR-AIWS-2026-06-037 C2).** When a CR adds a **numbered test case** to a test file, do NOT pin the label in the CR — verify the **next-free** label against the target file at apply (a `T5` clash forced a `T6` rename), or reference the assertion by **name**, not number.
- **11.5 State the RULE that computes an anchor, not the path (CR-AIWS-2026-08-023).** When a CR targets an artifact that is **computed** — a lint rule's anchor, the first element after a `sort`, whatever an algorithm picks — the CR states the **computation rule** and **how to verify it at apply**, never a hard-coded path. That path is **stale by design**: it moves when the member set changes, and again when one member changes directory. *Real case:* CR-AIWS-2026-07-071 pinned a path for the file carrying a `lint_accept`. The anchor of the `06-013` cluster flipped **twice in one day** — first when a CR moved to `applied/`, then when a `superseded` CR moved to `rejected/` — and the accept had to follow both times. Placed wrong, it emits **no warning at all**.
- **11.6 An `exact_apply` block holding schema'd config must cite the schema source (CR-AIWS-2026-08-023).** `exact_apply` means *paste verbatim, do not think* — so it carries **no verify-against-schema step**. When the block is schema'd configuration (a `lint_accept` entry, frontmatter, tool config), the CR must name the **schema source** (file + symbol) so the applier can check before pasting. *Real case:* CR-AIWS-2026-07-071 §3 T2 pasted a `lint_accept` snippet keyed `rule`/`cr` (the real schema is `code`/`reason`/`accepted_by`) plus a multi-line `>` string the parser does not fold. The `exact_apply` label carried the defect straight into the apply.
- **11.7 A CR adding/changing a lint rule sweeps its SIBLING rules before settling §12 propagation (CR-AIWS-2026-08-023).** Grep the name of an **existing rule of the same family** across the repo; the result is the list of surfaces that rule appears on (the spec defining the invariant · Lint_Spec · release note · skill · template). A surface carrying the old rule but **missing** the new one is very likely missed propagation. *Real case:* `duplicate_cr_id` shipped, yet §10 — where that id invariant is actually defined — never pointed at it, while its sibling `applied_without_apply_outcome` **does** carry a cross-ref inside §16.
- **11.8 A CR changing tool behavior must list test files in §2 Target (CR-AIWS-2026-08-023).** One line is mandatory: the tests asserting the old behavior, or an explicit **"grepped, none found"**. How to look: grep `.ai-work/tests/` for the tool name plus the rule/constant being changed. *Real case:* CR-AIWS-2026-08-021 §2 omitted `test_cr_status_integrity.py`, whose A2 fixture places an `applied` CR at the root and asserts "no findings" — the new rule turned that into an ERROR. The battery caught it **after** the apply had already run.
  **Evidence, not just the list (CR-AIWS-2026-08-082 C1).** §2 must show the **command actually run and its hit count**, then the list — or the literal `"grepped, none found"`. A list written from memory and a list produced by grep are indistinguishable on the page, so a reviewer cannot tell whether the search was wide enough; the gap surfaces at the battery, i.e. **after** the apply. Same shape §11.12 already requires for counts. Grep **more than one string** — the tool name AND the rule/constant/finding-code being changed reach different test files. *Real cases (wave 1067, measured 2026-08-17):* 10/11 CRs carried the table, **0/11** recorded a command, and three tables each missed a test that was pinning the very contract the CR meant to change — CR-AIWS-2026-08-072 (`test_quick_install_aiws` T5b), CR-AIWS-2026-08-079 (`test_refresh_draft_hygiene` B5 + `test_wiki_regression` ×2), CR-AIWS-2026-08-080 (`test_dual_tree_drift` case b/c). All three were caught by the battery, none by lint or by the applier's own probes.
- **11.9 Region ownership when the sibling CR does not exist yet (CR-AIWS-2026-08-023).** §11.1 assumes the sibling already has a `cr_id` to declare reciprocally. When a batch is **known** to be coming for the same region but has not been drafted, §10 forbids pinning a not-yet-existing id — so declare **region ownership by stable description** instead ("BATCH-3 will own §10; this CR owns §11 only"), and the CR drafted **later** carries the duty to grep back over CRs applied in the same wave. *Real case:* this very convention — BATCH-2 and BATCH-3 were decided before either had an id.
- **11.10 Dropping or replacing a change block in a later revision sweeps by CONTENT, not just by label (CR-AIWS-2026-08-042).** When revision *rN* removes or rewrites a change block (C1/C2/…), run **two** sweeps: (a) by the block's **label**, and (b) by the block's **content traces** — the anchor text it edits, the section it touches, and any row/line the CR pre-specified for it elsewhere in its own body. Content traces usually do **not** carry the label, so sweep (a) alone always leaves some behind. *Real case:* CR-AIWS-2026-08-040 r3 dropped C1 and fixed every "C1" mention, but the Revision-History row that §3 had pre-worded ("adds §1/§3") named only the sections — it survived to apply time and had to be corrected as a deviation.
- **11.10b Do NOT renumber change-block labels between revisions — append (CR-AIWS-2026-08-098).** When revision *rN* adds a change block, give it the **next free label** (C9, C10 …). Renumbering existing labels rewrites the identity that every cross-reference already points at. If a renumber is unavoidable, sweep **every** cross-referencing site — §2 Target, §5 apply order, §9 Governance, §11.1 region ownership, `assets/README` — and record an old→new mapping table in the Revision History. Real case: CR-067 r3 renumbered its blocks; the apply AIP then reported an Apply Outcome against labels that no longer meant what the reader thought, and reconstructing which block was which cost a full review round.
- **11.11 A claim about external/environment behavior is checked against that system's official source at draft time (CR-AIWS-2026-08-042).** When a CR ships a claim about a system you do not control — harness defaults, TTLs, pricing, version-gated behavior — check the official documentation **even when internal measurements back the claim**, and stamp the **fetch date + version** next to it. Measurements prove *what was observed then*, not *what is true now*: an external default can change faster than your document's revision cycle. *Real case:* CR-AIWS-2026-08-040 §5.2 was about to ship "fork mode is an experimental env-var feature" (true in the 08/2026 measurements) when the official docs showed it had become the interactive default in v2.1.232.
- **11.12 A CR with a sweep / rename / retire clause declares the TOTAL COUNT in §2 (CR-AIWS-2026-08-042).** §2 Target must state the **total number of matching points at draft time** (with the command that produced the count) plus the **classification criteria** that split them into *change* vs *keep* — then apply re-counts and records any delta as a deviation. Declaring a footprint from the points you happened to notice while drafting is how a CR under-scopes its own sweep. *Real case:* CR-AIWS-2026-08-039 declared "retire-wording 6 anchors ×2 trees" and applied exactly those six; 68 further references to the deleted tree survived and needed CR-AIWS-2026-08-041 to clean up.
  **Scope: ANY number in §2, not only sweep/rename/retire clauses (CR-AIWS-2026-08-082 C2).** A count is a claim about the tree, and a claim drafted by inspection is a guess however plainly it is written. Apply starts by re-measuring and records the delta as a deviation; a delta large enough to change the SHAPE of the work amends the CR before any edit. *Real cases (wave 1067):* CR-AIWS-2026-08-078 declared 24 broken links — measured **41 real + 10 false positives**, and its false-positive class needed a new sub-change nobody had scoped. CR-AIWS-2026-08-075 split its links "11 convert to TEXT / 13 keep the link" — measured **0 of 41** could keep the link, so half the CR described work that did not exist.
  **Con số phải đến từ một lệnh ĐẾM, không từ việc NHÌN danh sách (CR-AIWS-2026-08-110 C7).** §11.8 đã đòi *lệnh đã chạy + hit count*; khoảng cách còn lại nằm **giữa lệnh và con số** — tức ở chỗ người soạn **đọc** output. Một pipe `head`/`tail` chẻ đôi hai thứ đó và **không để lại dấu vết nào trên trang giấy**: lệnh ghi trong CR hoàn toàn đúng, người review chạy lại ra số khác, mà CR vẫn ghi số cũ. Vì vậy: lấy số bằng `grep -c` · `wc -l` · `sort | uniq -c`; nếu CR **chép danh sách** thì đó phải là output **ĐẦY ĐỦ**, không qua `head`. **Dấu hiệu review:** thấy `head` trong lệnh của §2 ⇒ nghi ngay. *Real case:* CR-AIWS-2026-08-106 §2 khai "C3 sửa **3** chỗ" (lệnh đúng); apply đo lại được **4** — con số đã được lấy từ một output bị `head` cắt.
- **11.13 Canonical nén nội dung rồi trỏ ngược doc phi-canonical = phụ thuộc phải khai báo (CR-AIWS-2026-08-050).** Khi một CR đưa vào canonical một đoạn VIỆN DẪN doc phi-canonical (draft CR, design doc, impl package…) làm **authority cho chính nội dung của nó** (kiểu "full wording xem X §N"), CR phải chọn một trong hai: **(a) fold đủ nội dung vào canonical** (canonical tự đứng, nguồn chỉ còn là provenance), hoặc **(b) đánh dấu doc nguồn là load-bearing dependency** — banner trên doc nguồn + ghi trong CR rằng doc đó không được xóa/di dời khi chưa fold. Citation provenance thuần túy (Source:/Built by — không giữ nội dung thay canonical) không thuộc rule này. *Real case:* `agent_runtime_design.md` §9 trỏ "full wording: draft CR-002 §14" và authoring guide trỏ "Detailed Design §3..§15" — audit AIP-1040 phải tự phát hiện các phụ thuộc ẩn này khi cân nhắc xóa impl package; carrier backlog AIP-PLAN-005 rỗng ruột theo đúng dạng lỗi này.

- **11.14 CR dựng từ một IR/intake phải TỰ MANG background — IR là provenance, không phải authority cho lý do (ruling AIWS-Product-Owner 2026-08-19; CR-AIWS-2026-08-106).** Một IR/intake tồn tại để dựng nên một CR: xong việc thì nó **xoá được**, và việc xoá phải an toàn. Vì vậy một CR **không được để lý do tồn tại của chính nó nằm trong IR**. Khi `driving_source` trỏ một IR / intake / triage report, phần Context của CR phải tự nói, bằng lời của nó: **(a)** quan sát được gì và ở đâu (path/line, lệnh, số đo), **(b)** vì sao điều đó quan trọng, **(c)** hiện trạng đo được lúc soạn — đủ để một người **chưa từng đọc IR** vẫn đánh giá được CR. Trích IR như **provenance** (*việc này đến từ đâu*) thì được; trích IR **thay cho lý do** (*"chi tiết xem IR §N"*) thì không. Đây đúng hình dạng lỗi của **§11.13**, thấp hơn một tầng — chỉ khác ở chỗ nguy hiểm hơn: doc nguồn ở §11.13 *có thể* bị xoá, còn IR thì **được thiết kế để bị xoá**, nên phụ thuộc chắc chắn gãy. Phía máy đã được lo riêng: `lint_aip` coi ref tới `change_requests/intake/` là ref tới vật tư đã tiêu thụ nên không báo `ref_missing` (CR-AIWS-2026-08-106 C0) — tức lint sẽ **không** cứu bạn ở đây, chỉ review mới cứu được. Kiểm khi review: checklist `cr_ir_review_checklist.md` nhóm **C — Source basis**. *Cố ý chưa cơ giới hoá* (DP-106-F): "background đủ để hiểu" là phán đoán ngữ nghĩa; một rule chỉ đo được vỏ sẽ vừa bỏ sót CR viết dài mà rỗng, vừa báo oan CR ngắn mà đủ — và tệ nhất là tạo cảm giác đã được gác.

- **11.15 CR mở rộng phạm vi một RULE ĐANG CHẠY phải có: DP "số liệu quyết định" + guardrail ĐẾM DELTA + ca âm bản cho từng hình dạng nhiễu (CR-AIWS-2026-08-110).** Nới một rule đã live là thay đổi **định lượng**: bạn không biết trước nó sẽ bắt thêm bao nhiêu, và bao nhiêu trong đó là nhiễu. Vì vậy CR phải khai sẵn ba thứ: **(i)** một DP nói rõ *nếu phương án này gây nhiễu thật thì số liệu sẽ hiện ra ngay khi apply*, **(ii)** guardrail buộc **đếm delta trước/sau** và **phân loại** hit, **(iii)** ca âm bản khoá **từng hình dạng nhiễu** tìm được, để lần siết sau không nới lại. *Real case:* CR-AIWS-2026-08-101 C2 viết "quét mọi token có `/`"; apply đúng chữ ⇒ `ref_missing` đi từ **0 lên 65**, và **65/65 là nhiễu** (`§4.1/§5`, `INTAKE-05/06`, `#7/#8` — dấu `/` phân tách MỤC). Phải siết **ba lần** mới còn 2 hit thật. Thứ cứu được tình huống là DP-101-B đã viết sẵn *"số liệu sẽ quyết định"* và §6 bắt đếm — nhờ vậy sai khác giữa chữ CR và hiện thực được **khai báo** chứ không im lặng.
- **11.16 CR nói "người hiện thực phải xử lý X" ⇒ apply phải để lại BẰNG CHỨNG HÀNH VI cho X; comment trong code KHÔNG tính (CR-AIWS-2026-08-110).** Bằng chứng hành vi = **một ca test**, **một phép đo**, hoặc **một dòng Apply Outcome nói X đã được xử thế nào**. Lý do rule tồn tại: một cảnh báo **được chép lại** trông **giống hệt** một cảnh báo **đã được xử lý** — và trông còn đáng tin hơn im lặng, nên nó chặn cả người sau lẫn chính người viết khỏi kiểm lại. *Real case:* CR-AIWS-2026-08-102 §Context viết *"PAYLOAD_MAP có 17 khoá, PAYLOAD_SECTIONS có 16 — người hiện thực C1 PHẢI XỬ LÝ bất đối xứng này"*; khi hiện thực, cảnh báo đó được **chép thành comment** trong `_common.py` và dừng ở đó. `ships()` mù với `aiws_meta`, rà tiếp lộ thêm hai đường mù nữa ⇒ tốn nguyên **CR-AIWS-2026-08-105** để vá. Cách kiểm khi đóng CR: grep các câu *"phải xử lý / phải kiểm"* trong CR và đối chiếu từng câu với Apply Outcome.
- **11.17 "Sẽ gãy / không thể / phải giữ vì có N chỗ trỏ" là một CLAIM VỀ CÂY MÃ, không phải một nguyên tắc — phải ĐO trước khi nó định hình phương án (CR-AIWS-2026-08-110).** §11.12 đã bắt mọi **con số** trong §2 phải đo; điều này mở rộng sang **nỗi sợ**, vốn cũng là một con số chưa đo. Phạm vi hẹp: chỉ áp cho mệnh đề dùng để **LOẠI BỎ một phương án**, không áp cho mọi câu trong CR. Phép đo rẻ nhất: **thực nghiệm phá huỷ tạm thời** (đổi tên file, gỡ một dòng) rồi khôi phục, và đếm hậu quả thật. *Real case:* CR-AIWS-2026-08-106 r1 loại phương án "xoá file IR" bằng lý do *"sẽ gãy ref của 10 AIP"* — viện đúng doctrine đã có nên nghe rất vững, nhưng **chưa từng được đo**. Đo mất hai lệnh: **9/10** AIP trỏ trong bảng mà rule **không hề quét**; thực nghiệm đổi tên file ⇒ **0** `ref_missing`. r2 đổi hẳn phương án. Cái sai không ở kết luận mà ở **thứ tự**: một giả định chưa đo được phép định hình phương án, rồi CR được viết mạch lạc quanh nó — và **sự mạch lạc làm giả định trông như đã được kiểm**.

## 12. Node-model / vocab-change propagation checklist (§15)

When a CR changes the **node model** or a **validated vocabulary** (e.g. a `META_REQUIRED`/`INDEX_REQUIRED` field, a `SOURCE_TYPE_VOCAB`/profile, an index projection, a node-kind), it MUST resolve the propagation checklist (promoted from / linked to `WIKI_CHANGE_REQUEST_SPEC §15`): each affected surface is marked propagated-plan or N/A-with-reason. A CR that touches neither marks §15 **N/A**.

## 13. Lint gate

`apply_gates` MUST require `/aiws-lint` clean (0 errors) before the CR flips to `applied`. Tooling changes additionally verify dual-tree byte-identity + fixtures/regression. Verification fixtures cited in `apply_gates` MUST be **in-repo** — never a consumer/downstream-project artifact (rule #9). When ≥2 approved CRs co-edit shared files, prefer ONE **batch apply-AIP by file-pass** (edit each shared file once) over one-AIP-per-CR. *(CR-AIWS-2026-06-034)* Scoped finalize-lint (CR-AIWS-2026-06-067) applies to **task-execution** finalize only; it does NOT relax this gate — a CR still flips `applied` only after whole-tree `/aiws-lint` is clean (0 errors) + dual-tree byte-identity + in-repo fixtures (the scoped driver auto-escalates to whole-tree on a `product/` or CR-apply footprint). **Dual-tree drift enforcement** *(CR-AIWS-2026-07-030)*: the whole-tree lint's `dual_tree_drift` check reports WARN by default, but an apply-CR AIP MUST reach `dual_tree_drift` = 0 on its own footprint before flipping `applied`.

**Sweep evidence at apply time (CR-AIWS-2026-08-095).** For a CR that retires or renames a concept, the Apply Outcome MUST quote the pre-close OLD-wording sweep — the command actually run (all token variants, §9), its scope (tree-wide over every shipped surface minus the default carve-outs; declared by tree, never by doc type) and the per-group hit counts (intentional provenance vs real residual). A bare "grep = 0" is not evidence — it is indistinguishable from "= 0 in the one file just edited" (real case: CR-071 C11 → residual shipped, IR-2026-08-17 F17-r). This is §11.8's evidence rule (CR-082) applied at apply time.

## 14. Version / changelog / install-package impact

- A canonical-doc change may warrant a version/changelog note in the affected package's manifest/baseline.
- **Auto-ship:** `product/**` payload sections are copied wholesale into the install package — a new/edited file under such a section ships on the next build with no build-script change (confirm the section is wholesale-copied before scoping a packaging edit).
- **Content-only doc additions do NOT bump the package version per-addition** *(CR-AIWS-2026-06-037 C5)*. A new doc added to a versioned package (e.g. a `wiki_guidelines` core guideline) is **registered** (manifest / canonical-doc index / navigator) but the package version + version-stamped install/rollout file labels **rebadge together at the next package build/release** — not per content addition (avoids a label-rename cascade on every doc).

## 15. CR + AIWS-Product-Owner approval flow

```
draft (no_cr)  →  status: proposed  →  AIWS-Product-Owner APPROVE (status: approved_for_ai_update)
              + explicit "apply" request (SOP §5 Rule C)  →  APPLY (cr_required, dual-tree)
              →  status: applied  +  Apply Outcome (truthful post-mortem)
```
AI never self-approves nor self-applies. A rejected CR is revised and re-presented (never partially applied).

## 16. Status lifecycle

**Live path:** `proposed` → `approved_for_ai_update` → `applied`.

**Terminal-not-applied states (CR-AIWS-2026-08-021):** `rejected` · `superseded` · `deferred`. `superseded` is *not* a rejection — the CR was replaced by a later one and carries `superseded_at` / `superseded_by`; `deferred` means parked, not refused. They were already in de-facto use before being named here; §16 was simply incomplete.

**Folder (CR-AIWS-2026-06-034, mapping completed by CR-AIWS-2026-08-021):**

| `status` | folder |
|---|---|
| `draft` | `drafts/` |
| `proposed`, `approved_for_ai_update` | main `product/change_requests/` |
| `applied` | `applied/` |
| `rejected`, `superseded`, `deferred` | `rejected/` |

`rejected/` therefore holds **every CR that reached a terminal state without being applied**, not only refused ones — the `status` field, not the folder, carries which kind. One folder rather than one per terminal state is deliberate: `lint_aip._CR_SUBDIRS` pins the folder set for CR-reference resolution, so a new folder is a coupled change, and the corpus was already 2-of-3 in `rejected/` when this was decided.

Enforced by lint **ERROR `cr_placement_mismatch`** (folder vs status) and **WARNING `cr_status_offvocab`** (status outside this lifecycle) — Lint_and_Tooling_Spec §22/§23.

**Status integrity (CR-AIWS-2026-08-004):** approval/apply có hiệu lực máy-đọc CHỈ khi field `status` được flip trong cùng hành động ghi nhận quyết định. Chuẩn thuận/apply chỉ ghi ở văn xuôi (body, §X, commit message) = chưa có hiệu lực với tool (lint/index/allocator đọc field). Một CR `applied` phải mang section `Apply Outcome` (lint WARN `applied_without_apply_outcome`).

## 17. Source-basis rule

A CR is grounded in **project source** (file/line, capture, triage, IR, prior CR). Any AI inference beyond the source is **clearly separated** (in §5/§7), so a reviewer can see what is grounded vs proposed. External-IR claims are adversarially verified against canonical before being folded in. **A source may be EPHEMERAL.** An IR/intake exists in order to build a CR and may be deleted once it has; the CR therefore restates its own background instead of pointing back at the IR for it — see **§11.14**.

## 18. Relationship to WIKI_CHANGE_REQUEST_SPEC

- **This spec is the general AIWS-wide CR authority.** `WIKI_CHANGE_REQUEST_SPEC` is its **wiki-meta-specialized profile**: it adds wiki-meta-specific `change_type`/`target_layer` enums and the canonical §15 propagation checklist (which this spec promotes/links).
- Where this spec and the wiki profile overlap, the wiki profile governs **wiki-meta** CRs; this spec governs **all other** canonical AIWS CRs. WCR carries a matching relation note.
- **Two approval roles (by scope) — CR-AIWS-2026-06-031:** AIWS-canonical CRs (this spec) are approved by the **AIWS-Product-Owner** (the AIWS design project only); wiki-meta CRs (the WCR profile) by the **Wiki-Manager** (common to every project using AIWS). The roles are parallel, not hierarchical; the AIWS side uses `reviewer_or_product_owner`, the wiki side `reviewer_or_wiki_manager`.
- **Downstream projects (consuming AIWS):** must NOT apply changes to AIWS canonical docs/tools themselves — only PoC/test locally, then raise a CR **upstream** to the AIWS project, where the **AIWS-Product-Owner** decides. (Wiki changes within a consuming project remain that project's Wiki-Manager's call.)
- **Id namespace (CR-AIWS-2026-08-001):** downstream projects must NOT mint ids in upstream namespaces (`CR-AIWS-*`, `AP-CR-*`). Raise findings upstream as an IR (intake), and keep local change-records in a project-local namespace (e.g. `CR-<PROJECT>-*`). Upstream mints the official id at promote time (§10). A downstream file carrying an upstream-namespace id is invalid regardless of content. *(Evidence: 5/5 ids minted by a downstream demo project collided with existing upstream ids — IR-2026-08-05.)*
- **Where a downstream project keeps these documents (CR-AIWS-2026-08-018).** The installed tree ships two homes, separated by **direction of travel**, each with a README (and, for the outbound one, an `IR_TEMPLATE.md`):

  | Installed path | Holds | Namespace |
  |---|---|---|
  | `.ai-work/upstream_requests/` | IRs the project raises **to** the AIWS team | `IR-YYYY-MM-DD-<slug>` |
  | `.ai-work/change_requests/` | the project's **own** change records | `CR-<PROJECT>-*` |

  The rule above was already canonical, but nothing told a project *where to put the file* — so four downstream submissions landed in four different places (one of them in `history/`, an immutable zone; one outside the repo entirely), and the project that named its file like an upstream CR duplicated an applied `cr_id`. Separating "my record" from "my request to AIWS" by folder — not by a frontmatter field — is what removes the temptation to imitate upstream naming. The shipped `IR_TEMPLATE.md` already carries intake-conformant frontmatter, so promoting an IR upstream is a **copy plus an id**, not a re-normalisation. Existing projects are **not** required to migrate; the homes are the default from now on.

## 19. Worked AIWS examples

- **Ex.1 — methodology-spec edit (`cr_required`):** a CR modifying `AIP_Detail_Spec_MVP §6.3`; Target = the spec path; before/after wording; apply via an apply-CR AIP after approval.
- **Ex.2 — lint-precision (`cr_required` via CR-037):** `CR-AIWS-2026-06-029` narrowed `capture_refs` + added a `lint_aip` diagnostic — tooling code, but CR-routed because lint rules are frozen; applied dual-tree with fixtures.

## 20. Out of scope (this spec)

- Back-compat migration / normalization of the existing ~50 `CR-AIWS-*` files.
- Building a CR **document template** or a CR-id **allocation tool** (this spec may recommend them; building is follow-on).
- Rewording Truth or AIP templates to cite this spec (follow-on CR).
- **Applied-CR folder (resolved by CR-AIWS-2026-06-034):** applied CRs are moved to `applied/`; drafts in `drafts/`.

## 21. Relationships

- **Truth:** `SOP_MASTER §4.1/§5`, `AI_WORK_CONTRACT §2/§4/§5` (this spec cites and conforms to them; does not reword them here).
- **`AIP_Detail_Spec_MVP`** (apply-CR AIPs instantiate `AIP_EXEC_APPLY_CR_TEMPLATE`).
- **`WIKI_CHANGE_REQUEST_SPEC`** (wiki-meta profile — §18).

## 22. Completion criteria

This spec is complete when: it covers the §1 doc types; the governance boundary (§2) is unambiguous; the field reference + mandatory set (§6/§7) match de-facto practice; id discipline (§10) codifies month-scoped + cross-branch allocation; the 3 conventions (§11) are stated; the approval flow + lifecycle (§15/§16) match SOP; and it is registered in the wiki source index + methodology indexes with `WIKI_CHANGE_REQUEST_SPEC` carrying the reciprocal profile note.
