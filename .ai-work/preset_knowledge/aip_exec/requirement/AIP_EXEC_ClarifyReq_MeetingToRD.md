---
artifact_type: aip_exec
artifact_id: AIP-EXEC-[NNN]-clarify-req-meeting-to-rd
title: Clarify Requirements — Meeting Transcript to RD
status: draft
project: <project-name>
owner: <owner>
plan_source: direct — inputs already clear (repeatable task with fixed flow)
updated_at: 2026-06-20
migrated_from: quy-task/AIP-EXEC-T1_ClarifyReq-CreateRD.md (v1.0 2026-04-09)
related_exec: AIP_EXEC_ClarifyYeuCauMoHo.md (general ambiguity clarification)
pilot_tested: 2026-04-16 (Notta transcript, quality C → Step 1.5 triggered)
---

<!-- Stable control: Done Criteria declarative (never tick [x]). Runtime state → workspace, not here. -->

# AIP_EXEC — Clarify Requirements: Meeting Transcript to RD

## SOP Compliance
SOP_MASTER (`.ai-work/truth/SOP_MASTER.md`) Universal Gates applicable to this task:
- **Gate U1 Confirm-understanding-of-task (HARD GATE)** — see `STEP-00` below
- **Gate U2 Confirm-understanding-of-input (soft)** — see `## Input Understanding`
- **Gate U3 Open Points tracking (soft)** — see `## Known Open Points`

---

## Objective

Chuyển biên bản họp / transcript cuộc họp với khách hàng (JP/VN) thành bộ tài liệu yêu cầu có cấu trúc, sẵn sàng cho design (T2) và offshore (T5).

Cụ thể:
- Đánh giá input quality và pre-process nếu transcript garbled
- Phân loại nội dung: confirmed / ambiguous / missing / assumption
- Tạo Req Note + Open Questions + Gap Log
- Tổng hợp thành RD (Requirement Definition) hoàn chỉnh

> **Khác biệt với AIP_EXEC_ClarifyYeuCauMoHo:** File đó xử lý ambiguity list đã có sẵn. File này xử lý từ raw meeting transcript (có thể garbled) → structured RD, bao gồm pre-processing step.

---

## Selected Task Lens / Mode
<!-- Task Lens runtime content (CR-AIWS-2026-05-030) — HINT, not a hard filter; presets in .ai-work/wiki/task_lens_presets/. -->
- Lens: requirement_understanding
- Reason: Turning a raw meeting transcript into a structured RD — the whole task is understanding/clarifying requirements (confirmed / ambiguous / missing) before downstream design.
- Search/execution effect: Prioritises `requirement_definition`, `meeting_note`, `basic_design` + object kinds (`function`) when assembling inputs and ordering the reading surface.
- Expansion allowed: yes — pull prior spec / design for conflict or freshness checks; never resolve ambiguity by assumption (log Open Questions / Gap Log).

## Execution Scope

### In Scope
- Đọc và phân tích biên bản họp / transcript tiếng Nhật / Việt / mixed
- Pre-process transcript thô nếu quality thấp (Step 1.5)
- Phân loại: confirmed / ambiguous / missing / assumption / out-of-scope
- Tạo Req Note, Open Questions, Gap Log (nếu có spec cũ)
- Tạo RD có cấu trúc cho downstream (T2 design / T5 offshore)

### Out of Scope
- Không tự quyết định các điểm ambiguous — chỉ flag và đặt câu hỏi
- Không tạo thiết kế (BD/DD) — đó là T2
- Không dịch toàn bộ tài liệu gốc — chỉ trích xuất requirement
- Không escalate trực tiếp lên khách

---

## Expected Outputs

| # | Output | Description | Owner |
|---|---|---|---|
| O-01 | Req Note | MD table — ID, requirement, priority, status | AI → BrSE review |
| O-02 | Open Questions | MD list — blocking level, grouped by topic | AI → BrSE review |
| O-03 | Gap Log | MD table — gap vs spec cũ (conditional: skip nếu không có spec) | AI → BrSE review |
| O-04 | RD (Requirement Definition) | MD document có cấu trúc chuẩn cho downstream | AI → BrSE review → PM review |

---

## Execution Input Package

### Plan Source
`direct` — Task scope đã rõ (input = transcript, output = RD). Flow cố định, lặp lại nhiều lần. Mỗi lần chạy khác nhau chỉ ở input.

### Required Inputs
| Input | Description | Required/Optional |
|---|---|---|
| I-01 Biên bản / transcript | Meeting minutes hoặc auto-transcript (đã masking) | Required |
| I-02 Spec hiện có | Tài liệu yêu cầu / thiết kế hiện tại | Optional |
| I-03 Context dự án | Tên hệ thống, module, phase hiện tại | Required |
| I-04 RD template | Template riêng nếu dự án có chuẩn | Optional |
| I-05 Supplementary notes | Chat log, email, slide — để cross-reference khi transcript quality thấp | Optional |

### Workspace Preconditions
- [ ] Input I-01 đã được masking thông tin bảo mật
- [ ] BrSE có đủ domain knowledge để verify AI output
- [ ] Ngôn ngữ output đã xác định (JP cho khách / VN cho nội bộ)

---

## Input Understanding

<!-- Gate U2 — AI điền sau khi đọc inputs, TRƯỚC STEP-01. -->

| Input artifact | Key understandings | Assumptions | Ambiguities / questions | BrSE confirmed? |
|---|---|---|---|---|
| I-01 Transcript | `<AI điền: tóm tắt nội dung, chất lượng A/B/C, ngôn ngữ, số người tham gia>` | `<assumptions>` | `<phần không đọc được>` | ⬜ pending |
| I-02 Spec (nếu có) | `<AI điền: scope spec cover gì, version nào>` | `<assumptions>` | `<phần chưa rõ>` | ⬜ pending |
| I-03 Context | `<AI điền: hiểu hệ thống/module/phase thế nào>` | `<assumptions>` | `<cần BrSE clarify>` | ⬜ pending |

---

## References to Read First

**Required:**
- `<path to transcript / meeting minutes (masked)>`
- `<path to project context doc>`

**Optional:**
- `<path to existing spec / design doc>`
- `<path to supplementary notes (chat log, email, slide)>`

---

## Current Risks / Constraints

- **Transcript quality:** Auto-transcription (Notta, Otter) tiếng Việt trong phòng họp Nhật thường < 30% usable. Pilot test cho thấy < 15%. Bắt buộc qua Step 1.5 nếu quality = C.
- **Hallucination risk:** Với input noise cao, AI dễ "bịa" nội dung cho hợp lý. Anti-hallucination check bắt buộc ở Step 5.
- **Masking:** BrSE quên masking = rủi ro bảo mật. Warning ở STEP-00.
- **Version control:** Khách thay đổi yêu cầu sau RD → tạo version mới, không overwrite.

---

## Known Open Points

Log: `.ai-work/workspaces/<workspace>/05_open_questions.md`

> Điền bất kỳ open point nào phát sinh trong quá trình EXEC vào file trên.

---

## Workspace Execution Rule

All runtime state (findings, draft, open questions) → workspace files. AIP này read-only trong execution.

---

## Execution Steps

### Step: STEP-00 — Confirm Task Understanding (HARD GATE)

Objective:
Trình bày ý hiểu về task: loại transcript, context dự án, output mong đợi, ngôn ngữ. Đánh giá input quality (A/B/C). Dừng chờ BrSE confirm.

Recommended Mode:
Clarifying

Applicable Guidelines:
- SOP_MASTER Gate U1

Inputs:
- I-01 Transcript + I-03 Context dự án
- Input Understanding table trên

Expected Outputs:
- Input quality assessment (A = rõ ràng / B = có noise nhưng dùng được / C = garbled, cần Step 1.5)
- Task understanding summary (3-5 câu)
- Danh sách chủ đề chính trong transcript
- BrSE confirmation

AI Prompt:
```
Tôi cung cấp [biên bản họp / transcript] và context dự án.

**Context:** Hệ thống: [masked], Module: [...], Phase: [...], Ngôn ngữ gốc: [JP/VN/mixed]

**Nhiệm vụ:**
1. Đánh giá chất lượng input: A (rõ) / B (có noise) / C (garbled)
2. Tóm tắt nội dung chính trong 3-5 câu
3. Liệt kê chủ đề thảo luận
4. Ghi rõ điểm chưa hiểu hoặc cần bổ sung

Chưa cần phân tích sâu — chỉ confirm understanding.
```

Done Condition:
BrSE confirm AI hiểu đúng context. Nếu quality = C → route sang STEP-01-ALT.

Notes / Constraints:
- ⚠️ **Masking check:** Xác nhận input đã masking tên KH, hệ thống, hợp đồng
- Nếu quality = A hoặc B → STEP-01
- Nếu quality = C → STEP-01-ALT (pre-process)

Workspace Actions:
- Write assessment → `04_findings.md`
- Log BrSE confirmation

---

### Step: STEP-01-ALT — Pre-process Transcript Thô (CONDITIONAL)

> **Chỉ chạy khi STEP-00 đánh giá quality = C**

Objective:
Reconstruct nội dung từ transcript garbled bằng cross-reference với supplementary sources.

Recommended Mode:
Investigating

Applicable Guidelines:
_(none)_

Inputs:
- I-01 Transcript (garbled)
- I-05 Supplementary notes (chat log, email, slide, human notes)

AI Prompt:
```
Transcript bị garbled nặng. Tôi cung cấp thêm [nguồn bổ sung].

Nhiệm vụ:
1. Cross-reference transcript với nguồn bổ sung
2. Reconstruct nội dung: Người phát biểu → nội dung chính, quyết định, action items
3. Đánh dấu: [confirmed from source] vs [inferred from context]
4. Liệt kê phần KHÔNG reconstruct được

**Quy tắc:** Không suy diễn nội dung không có evidence. Ghi "[UNCLEAR]" cho phần không chắc.
```

Expected Outputs:
- Reconstructed meeting content (structured)

Done Condition:
BrSE review reconstruct, sửa sai, bổ sung. Content đủ chất lượng để tiếp STEP-01.

Notes / Constraints:
- Không suy diễn nội dung không có evidence — ghi "[UNCLEAR]" cho phần không chắc.

Workspace Actions:
- Write reconstructed content → `04_findings.md`

---

### Step: STEP-01 — Phân loại nội dung biên bản

Objective:
Tách rõ mọi nội dung thành: confirmed / ambiguous / missing / assumption / out-of-scope.

Recommended Mode:
Analyzing

Applicable Guidelines:
_(none)_

Inputs:
- Confirmed content từ STEP-00 (hoặc STEP-01-ALT)

AI Prompt:
```
Dựa trên nội dung đã xác nhận, phân loại toàn bộ:

| ID | Nội dung | Loại | Confidence | Ghi chú |
|----|----------|------|------------|---------|
| R-001 | ... | CONFIRMED / AMBIGUOUS / MISSING / ASSUMPTION / OUT-OF-SCOPE | High/Med/Low | ... |
```

Expected Outputs:
- Classification table với ID và confidence level

Done Condition:
BrSE review và confirm phân loại. **Bắt buộc confirm trước STEP-02.**

Notes / Constraints:
- Bắt buộc BrSE confirm phân loại trước STEP-02.

Workspace Actions:
- Write classification → `04_findings.md`

---

### Step: STEP-02 — Tạo Req Note + Open Questions

Objective:
Từ classification → tạo 2 deliverables chính: Req Note (O-01) + Open Questions (O-02).

Recommended Mode:
Generating

Applicable Guidelines:
_(none)_

Inputs:
- Classification table đã confirm (STEP-01)

AI Prompt:
```
Từ classification table đã xác nhận:

**1. Req Note** (chỉ CONFIRMED items):
| ID | Requirement | Priority | Category | Note |
High = blocking design / Medium = scope impact / Low = nice-to-have

**2. Open Questions** (AMBIGUOUS + MISSING):
| ID | Câu hỏi | Nguồn gốc | Blocking? | Suggest answer |
Blocking items lên đầu. Group theo topic nếu > 5 câu hỏi.
```

Expected Outputs:
- O-01 Req Note
- O-02 Open Questions

Done Condition:
BrSE review, loại bỏ câu hỏi đã biết answer → chuyển vào Req Note.

Notes / Constraints:
- Blocking items lên đầu Open Questions; group theo topic nếu > 5 câu hỏi.

Workspace Actions:
- Write Req Note + Open Questions → `07_output_draft.md`

---

### Step: STEP-03 — Tạo Gap Log (CONDITIONAL)

> **Skip nếu không có I-02 (spec cũ). Ghi "No baseline" trong RD.**

Objective:
So sánh yêu cầu mới vs spec hiện có, ghi nhận thay đổi.

Recommended Mode:
Analyzing

Applicable Guidelines:
_(none)_

Inputs:
- I-02 Spec cũ + Req Note (O-01)

Expected Outputs:
- O-03 Gap Log: | ID | Yêu cầu mới | Status trong spec | Loại thay đổi | Impact | Cần update ở đâu |

Done Condition:
BrSE confirm gaps thực sự cần action.

Notes / Constraints:
- Conditional: skip nếu không có I-02 (spec cũ) — ghi "No baseline" trong RD.

Workspace Actions:
- Write Gap Log → `07_output_draft.md`

---

### Step: STEP-04 — Tổng hợp RD

Objective:
Tạo tài liệu RD hoàn chỉnh cho downstream (T2 design / T5 offshore).

Recommended Mode:
Generating

Applicable Guidelines:
_(none)_

Inputs:
- Tất cả output STEP-01 → STEP-03

AI Prompt:
```
Tổng hợp thành RD:
# RD — [Module] — [Date]
## 1. Overview
## 2. Confirmed Requirements (from Req Note)
## 3. Open Points (from Open Questions chưa resolve)
## 4. Assumptions (from ASSUMPTION items, đánh dấu rõ chưa confirm)
## 5. Out of Scope
## 6. Changes vs Current Spec (from Gap Log, hoặc "No baseline")
## 7. Next Steps (dependencies T2/T4/T5)

**Ngôn ngữ:** [JP nếu gửi khách / VN nếu nội bộ — BrSE chỉ định]
```

Expected Outputs:
- O-04 RD document

Done Condition:
BrSE review toàn bộ, đảm bảo không có assumption bị lẫn vào confirmed.

Notes / Constraints:
- Không để ASSUMPTION lẫn vào CONFIRMED; ngôn ngữ output theo BrSE chỉ định (JP khách / VN nội bộ).

Workspace Actions:
- Write RD → `07_output_draft.md`

---

### Step: STEP-05 — Self-review + Anti-hallucination Check

Objective:
Kiểm tra chất lượng toàn bộ output trước finalization.

Recommended Mode:
Reviewing

Applicable Guidelines:
_(none)_

Inputs:
- Toàn bộ output STEP-01 → STEP-04 (Req Note, Open Questions, Gap Log, RD draft)

AI Prompt:
```
Self-review toàn bộ output:
- [ ] CONFIRMED tách rõ với ASSUMPTION?
- [ ] Open Questions actionable (trả lời được)?
- [ ] Gap Log đủ thông tin để update spec?
- [ ] RD usable cho downstream (T2/T5)?
- [ ] Thông tin nhạy cảm đã masking?
- [ ] Ngôn ngữ output đúng yêu cầu?
- [ ] **Anti-hallucination:** Có nội dung nào AI tạo ra mà KHÔNG có trong input gốc?

Với mỗi FAIL → ghi rõ cần sửa gì.
```

Expected Outputs:
- Self-review report
- Fixes cho các items FAIL

Done Condition:
Tất cả checklist items PASS. BrSE final review.

Notes / Constraints:
- Anti-hallucination bắt buộc — không có nội dung nào AI tạo ra mà không có trong input gốc.

Workspace Actions:
- Write review report → `04_findings.md`

---

### Step: STEP-06 — Finalize & Lưu Output

Objective:
Lưu files theo naming convention, cập nhật KPI tracker.

Recommended Mode:
Finalizing

Applicable Guidelines:
_(none)_

Inputs:
- Output đã self-review + BrSE final review (STEP-05)

Expected Outputs:
- `REQ_NOTE_[Project]_[Date].md`
- `OPEN_QUESTIONS_[Project]_[Date].md`
- `GAP_LOG_[Project]_[Date].md` (nếu có spec cũ)
- `RD_[Project]_[Date].md`
- KPI log entry (thời gian, số items, lessons learned)

Done Condition:
Files lưu đúng chỗ, KPI log updated, BrSE final confirmation.

Notes / Constraints:
- Lưu đúng naming convention; khách đổi yêu cầu → tạo version mới, không overwrite.

Workspace Actions:
- Move final outputs → `11_output_final/`
- Update KPI tracker

---

## Done Criteria

- [ ] Req Note có ≥1 confirmed requirement
- [ ] Open Questions đã BrSE review và prioritize
- [ ] RD có đủ 7 sections
- [ ] Self-review + anti-hallucination check pass
- [ ] Không có ASSUMPTION nào lẫn vào CONFIRMED
- [ ] Output files lưu đúng naming convention
- [ ] **Gate U1** confirmed — BrSE confirmed scope và approach tại STEP-00
- [ ] **Gate U2** Input Understanding đã điền và confirmed
- [ ] **Gate U3** Open Points log updated

## Self-check / Review Points

Trước khi finalize (STEP-05), self-check:
- Mọi confirmed requirement có truy xuất được nguồn từ input gốc
- Blocking questions lên đầu Open Questions
- Assumptions visible rõ ràng, không bị ẩn trong RD
- RD usable cho T2 (design) và T5 (offshore handoff)
- Không có hallucination (nội dung AI bịa không có trong transcript)

## Finalization Notes

- Sau BrSE review → submit PM review trước khi dùng làm input cho T2/T5
- Khách thay đổi yêu cầu → tạo version mới (không overwrite)
- Open Questions blocking → ưu tiên gửi khách qua T4 (mail/chat) trước khi tiếp T2

## Re-plan Rule

Append Re-plan Log entry khi:
- Input quality thay đổi (nhận thêm supplementary notes → re-run STEP-01)
- Scope thay đổi sau STEP-00 (thêm/bớt items)
- Khách trả lời Open Questions → cập nhật Req Note + RD

## Re-plan Log

- (no re-plan yet)

---

## Guidance Notes

**Khi nào dùng file này:**
- Có biên bản họp / transcript cần chuyển thành RD
- Input có thể là human-written minutes hoặc auto-transcript (garbled)
- Output cần structured cho downstream (design / offshore)

**Khi KHÔNG dùng file này:**
- Requirement đã có sẵn dạng structured → dùng AIP_EXEC_ClarifyYeuCauMoHo
- Chỉ cần dịch tài liệu → không cần AIP
- Task đơn giản (hỏi nhanh, tóm tắt 1 file) → không cần AIP

**Pilot test finding (2026-04-16):**
Notta AI transcript tiếng Việt trong phòng họp Nhật cho quality < 15% usable. STEP-01-ALT (pre-process) là critical — cần ≥1 supplementary source để cross-reference.

---

## Changelog

| Version | Date | Author | Changes |
|---|---|---|---|
| v1.0 | 2026-04-09 | Quý NK (Sonnet) | Initial as quy-task/AIP-EXEC-T1 |
| v2.0 | 2026-04-16 | Quý NK (Opus review) | Added quality gate, Step 1.5, confidence, anti-hallucination |
| v3.0 | 2026-04-23 | Quý NK | Migrated to AIWS v0.4 format, aligned with team convention |
