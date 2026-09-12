# AIP_Sample_ReviewTestCase_Shared.md

**Version:** v1.2
**Date:** 2026-04-21
**Target Task:** Review test case
**Priority Basis:** High practical reuse in BrSE QA-coordination and test quality control tasks
**Recommended Primary AIP Type:** Shared AIP
**Secondary Pattern:** Review-oriented / QA-coordination / Coverage-quality-control
**Audience:** AI + BrSE + QA + Testcase Author + Reviewer + Offshore

---

## 1. Vì sao task này nên có AIP

Task **"Review test case"** là điểm kiểm soát chất lượng quan trọng trước khi testcase được dùng để execute hoặc handoff sang offshore/QA.

Đây không chỉ là việc "đọc testcase và comment".
Trong thực tế, review testcase thường bao gồm:

- xác định đúng scope review và mục tiêu review
- nhìn testcase từ nhiều góc độ:
  - coverage vs test viewpoint đã được approve
  - logic vs spec/design
  - clarity của steps / preconditions / expected results
  - handling của open points / assumptions
  - downstream executability (offshore có execute được không?)
- tách rõ:
  - issue logic (testcase sai hoặc incomplete)
  - issue coverage (thiếu viewpoint, thiếu case)
  - issue clarity (steps/expected result không rõ)
  - pending point (spec/design chưa rõ ảnh hưởng testcase)
  - recommendation
- phối hợp nhiều bên:
  - testcase author
  - BrSE / QA lead
  - offshore team
  - PM nếu có blocker ảnh hưởng schedule

Task này rất phù hợp với **Shared AIP** vì:
- review findings không chỉ dành cho một người
- kết quả review ảnh hưởng execution readiness
- cần rule rõ về:
  - ai review
  - ai update testcase
  - ai xác nhận closure
  - khi nào re-review

AIP cho task này giúp:
- chốt review objective và scope
- structure findings / severity / coverage gap / next action
- làm rõ coordination rule sau review
- tăng chất lượng testcase trước khi execution

---

## 2. AIP type đề xuất

### 2.1. Primary AIP Type
**Shared AIP**

#### Vì sao
- review findings ảnh hưởng đến nhiều bên: author, QA, offshore, BrSE
- có coordination / rework / re-review
- có thể ảnh hưởng đến execution schedule và quality gate

### 2.2. Secondary style
**Review-oriented / QA-coordination / Coverage-quality-control**

#### Vì sao
- không phải tạo artifact mới
- trọng tâm là đánh giá chất lượng và completeness của testcase hiện có
- cần structure findings rõ để author update và reviewer confirm

### 2.3. Khi nào có thể dùng loại khác
- **PLAN AIP**: nếu review nhỏ, thiên về personal checklist nhanh
- **PM AIP**: nếu focus là tracking review status / coverage gap metrics cho toàn project
- **Member AIP**: nếu chỉ là self-check / pre-review investigation cá nhân
- **EXEC AIP**: khi review flow đã rất chuẩn hóa và chỉ cần đi từng bước theo checklist cố định

---

## 3. Rule bắt buộc mới cho flow "Review test case"

Từ nay, flow cho task **Review test case** phải có các step bắt buộc sau:

0. **Làm rõ build context** *(bước mới — thực hiện trước tất cả)*
   - AI hỏi BrSE:
     - build type (feature release / bug-fix / CR / mixed)
     - build có change log / release notes không
     - known issues trong build
     - downstream team (offshore / QA / UAT)
   - AI output summary và BrSE confirm trước khi thu thập input testcase
   - **Lý do:** không biết build context → không xác định được review focus, scope, và execution priority

1. **Làm rõ input understandings**
   - AI đọc input và output ra:
     - test objective understanding
     - test viewpoint alignment understanding (testcase có bám viewpoint đã approve không?)
     - scope / boundary understanding
     - known pending/open-point understanding trong testcase
     - intended downstream usage (execute trực tiếp / handoff offshore / UAT prep?)
   - BrSE / reviewer confirm AI đã hiểu đúng input ở mức working level

2. **Thực hiện review / tạo findings draft**
   - chỉ thực hiện sau khi understandings đã được confirm đủ để làm việc
   - review theo viewpoints đã xác định

3. **Tạo review viewpoint để self-review trước khi close**
   - review viewpoint dùng để tự kiểm:
     - scope review đã đúng chưa
     - coverage gaps đã đủ chưa
     - findings có đúng và đủ chưa
     - severity / impact có hợp lý chưa
     - testcase sau update có execute được không

### Ý nghĩa của rule này
Rule này giúp:
- AI không review sai scope do hiểu sai viewpoint hoặc spec
- findings không bị rời rạc
- review package usable hơn cho testcase author và downstream team
- BrSE có điểm kiểm soát sớm để confirm AI đã hiểu đúng testcase và viewpoint trước khi review sâu

### Flow chuẩn
```text
Clarify build context (build type + changes + downstream + known issues)
    ↓
Collect review inputs (testcase + viewpoint + spec/design + build change log)
    ↓
Extract and structure understandings (build + testcase)
    ↓
BrSE / reviewer confirms understandings
    ↓
Review: build coverage + regression risk + testcase quality + execution priority + known blockers
    ↓
Create review viewpoint
    ↓
Self review using review viewpoint
    ↓
Finalize gap report / handoff / re-review rule
```

---

## 4. Mục tiêu của AIP cho "Review test case"

AIP của task này nên giúp trả lời được các câu hỏi sau:

1. Review testcase nào, cho scope nào?
2. Test viewpoint nào được dùng làm baseline review?
3. AI/reviewer đã hiểu đúng testcase và viewpoint input đến mức nào?
4. Review từ góc nhìn nào (coverage / logic / clarity / executability)?
5. Kết quả review được ai dùng tiếp?
6. Findings nào là major / minor / note?
7. Coverage gap nào cần bổ sung?
8. Sau review thì ai làm gì tiếp theo?
9. Khi nào testcase review được coi là done?

---

## 5. Khi nào nên tạo AIP riêng cho "Review test case"

Nên tạo AIP khi có một hoặc nhiều điều kiện sau:

- bộ testcase có độ phức tạp vừa hoặc lớn
- có nhiều reviewer hoặc nhiều viewpoint cần check
- kết quả review ảnh hưởng đến execution schedule hoặc offshore handoff
- cần re-review hoặc coverage gap tracking
- cần structure severity / owner / next action
- testcase sẽ được nhiều bên dùng (QA / offshore / UAT)

Không nhất thiết cần full AIP khi:
- chỉ review một testcase rất nhỏ, isolated
- chỉ quick checklist nội bộ không có downstream dependency
- chỉ self-check cá nhân trước khi gửi đi

---

## 6. Bộ Q&A để clarify task "Review test case"

AI nên hỏi theo thứ tự sau.

### Q1. Review testcase nào?
- testcase cho screen / UI
- testcase cho API
- testcase cho batch / report
- testcase cho business flow (end-to-end)
- testcase cho IF / integration
- nhiều object liên quan

### Q2. Test viewpoint đã được finalize và approve chưa?
- đã finalize và BrSE đã approve
- đã có nhưng chưa finalize
- chưa có — cần xác định viewpoint trước khi review
- không dùng viewpoint (review độc lập theo spec)

### Q3. Scope review là gì?
- toàn bộ bộ testcase
- chỉ phần thay đổi / mới thêm
- chỉ các case liên quan đến CR / bug fix
- chỉ case có severity cao / business critical
- issue-focused review

### Q4. Mục tiêu review là gì?
- check coverage vs viewpoint
- check logic vs spec/design
- check clarity (steps / expected result / precondition)
- check assumption / open point visibility
- check executability cho offshore
- chuẩn bị cho UAT / customer-facing execution

### Q5. Input chính để review là gì?
- testcase document
- finalized test viewpoint
- spec / requirement / design
- clarification results
- open issue / assumption list
- prior review comments
- common checklist

### Q6. Review từ góc nhìn nào?
- coverage vs viewpoint
- logic vs spec / design
- clarity / executability
- assumption visibility
- pending point handling
- consistency giữa các case

### Q7. Ai sẽ dùng kết quả review?
- testcase author
- QA lead
- offshore team
- BrSE
- PM
- UAT preparation team

### Q8. Output review cần ở dạng nào?
- coverage gap list
- issue list (logic / clarity / missing case)
- severity summary
- checklist result
- recommendation
- go/no-go for execution

### Q9. Có cần classify issue theo severity không?
- không
- có: blocker / major / minor / note
- có: critical / medium / low

### Q10. Sau review, flow xử lý issue là gì?
- testcase author update rồi re-review
- discuss trong QA meeting
- log vào issue tracker
- accept as pending / defer
- escalate to BrSE / PM

### Q11. Khi nào task này được coi là done?
- findings đã được structure rõ
- coverage gaps đã visible
- review package đã handoff đúng owner
- re-review rule rõ
- downstream (offshore / QA) biết có thể execute hay chưa

### Q12. Build type là gì? *(cho build-contextualized review)*
- feature release — có feature mới
- bug-fix patch — chỉ fix bug
- CR release — build theo Change Request
- mixed — kết hợp nhiều loại
- không áp dụng — review không gắn với build cụ thể

### Q13. Build có release notes / change log không?
- có đầy đủ
- có nhưng chỉ tóm tắt
- không có — sẽ liệt kê thủ công
- không có — review thuần testcase

### Q14. Có danh sách known issues trong build không?
- có — sẽ cung cấp
- không có / chưa biết
- có nhưng chưa đầy đủ

### Q15. Cần triage execution priority không?
- có — cần phân loại must-run / should-run / can-defer
- không — chỉ cần gap report, không cần priority

### Q16. Output chính là gì?
- gap report đầy đủ (build coverage + quality + priority)
- chỉ cần quality review (không cần build coverage analysis)
- chỉ cần execution priority list
- go/no-go recommendation cho build

---

## 7. Section trọng tâm của AIP cho task này

Các section nên được nhấn mạnh:

1. **Review Objective**
2. **Review Scope**
3. **Test Viewpoint Alignment**
4. **Input Understandings / Reviewer Confirmation**
5. **Review Viewpoints**
6. **Coverage Gap Analysis**
7. **Findings / Severity / Impact**
8. **Review Viewpoint / Self Review**
9. **Coordination / Re-review Plan**
10. **Done Criteria**
11. **Build Context** *(mới)* — build type, change log, known issues, downstream
12. **Build Coverage Analysis** *(mới)* — mỗi change trong build có testcase cover không?
13. **Regression Risk Assessment** *(mới)* — build ảnh hưởng area nào ngoài target scope?
14. **Execution Priority** *(mới)* — must-run / should-run / can-defer theo risk của build
15. **Known Execution Blockers** *(mới)* — testcase nào sẽ fail do known build issue?

---

## 7.5 AI Execution Protocol — Hướng dẫn AI thực thi AIP loại này

> Phần này dành cho AI khi được BrSE giao AIP có type "Review test case".
> Khi BrSE tạo AIP từ template này và yêu cầu AI execute, AI phải follow toàn bộ protocol này thay vì tự suy.
> BrSE cũng có thể dùng phần này làm reference khi tự viết skill `/review-testcase` cho dự án.

---

### P1. Intake Form — One-shot, trình bày ngay khi nhận lệnh review

AI phải present form này ngay, không hỏi trước:

```text
📋 REVIEW TESTCASE — INPUT

1. Build: [name/version]

2. Change log:
   A: Có (paste nội dung bên dưới)  |  B: Không có
   → [A/B]:
   ___

3. Known build issues:
   A: Có (paste bên dưới)  |  B: Không có
   → [A/B]:
   ___

4. Downstream:
   A: Offshore  |  B: QA internal  |  C: BrSE  |  D: UAT  |  E: Khác → specify: ___
   → [A/B/C/D/E]:

5. Testcase:
   A: Paste nội dung  |  B: File path (.md hoặc .xlsx)
   → [A/B]:
   ___

6. Viewpoint (finalized):
   A: Có (paste hoặc file path)  |  B: Không có
   → [A/B]:
   ___

7. Spec / design:
   A: Có (paste hoặc file path)  |  B: Không có
   → [A/B]:
   ___

7a. Build SRS wiki từ spec trên? *(chỉ trả lời nếu câu 7 = A)*
    A: Có — AI đọc spec, tạo SRS wiki cấu trúc hoá, save file, dùng wiki cho review
    B: Không — dùng spec trực tiếp
    *(Chọn A nếu spec lớn hoặc sẽ review nhiều TC file — tiết kiệm quota từ lần review thứ 2)*
    → [A/B]:

8. Output format:
   A: Markdown  |  B: Excel (.xlsx)  |  C: Cả hai
   → [A/B/C]:

9. Fix mode:
   A: Review only
   B: Review + auto-fix Minor/Note (clarity, consistency, assumption visibility)
   C: Review + auto-fix tất cả có thể (bao gồm Major clarity)
   → [A/B/C]:

10. Save path: [để trống = dùng default: 04_generated_outputs/]

11. Language (gap report):
    A: Tiếng Việt  |  B: Tiếng Anh  |  C: Tiếng Nhật
    → [A/B/C]:
```

**Notes:**

- Field 7a chỉ trả lời khi câu 7 = A; bỏ qua nếu câu 7 = B
- Excel input (.xlsx/.xls) → AI convert sang markdown trước khi xử lý
- Build type và Function type được auto-detect — không cần BrSE khai báo

---

### P2. Coverage Mode Selection

AI tự chọn mode cao nhất có thể từ input BrSE cung cấp:

| Mode | Input cần | Coverage quality | Ghi chú trong report |
| ------ | ----------- | ----------------- | ---------------------- |
| **A — Viewpoint** | Finalized viewpoint (field 6 = A) | ✅ Full | "Coverage assessed via viewpoint" |
| **B — Derive from spec** | Spec (field 7 = A, 7a = B) | 🟡 Good | AI generates Proposed Viewpoint file; "see proposed viewpoint file" |
| **B-wiki** | Spec + field 7a = A | ✅ Full | AI builds SRS wiki first → uses as Mode A baseline; saves wiki file |
| **C — Heuristics** | Chỉ có testcase (không có viewpoint/spec) | 🟠 Partial | AI auto-detects function type; generates heuristic viewpoint |
| **D — No baseline** | Không có gì | 🔴 Logic/clarity only | "Coverage not assessed" |

**Function type auto-detection (Mode C):** AI đọc testcase content và infer:
- **UI screen**: button / field / screen / validation / error message / navigation
- **API**: request / response / endpoint / status code / auth / header / payload
- **Batch / report**: schedule / trigger / data volume / output file / filter / date range
- **Business flow**: status transition / approval / rollback / end-to-end / workflow

**Build type auto-inference:** AI đọc change log và infer:
- **Bug-fix**: "fix / bug / defect / patch / hotfix"
- **Feature**: "new / add / feature / implement / release"
- **CR**: "CR / change request / client request / modification"
- **Mixed**: nhiều loại rõ ràng cùng tồn tại

---

### P3. SRS Wiki Build (field 7 = A AND 7a = A)

Thực hiện **trước micro-checkpoint**, silent:

1. Đọc spec content
2. Identify distinct areas (screens / features / APIs / flows)
3. Per area, extract: business rules, testable conditions (normal/boundary/exception), data constraints, permissions
4. Viết wiki theo format:

```markdown
# SRS Wiki — [System / Feature Name]
**Source:** [file path | "pasted"]  **Build:** [build]  **Built:** YYYY-MM-DD
**Quality note:** AI-generated — BrSE validate trước khi reuse làm authoritative baseline.

## [Area 1]
### Business Rules
- BR-01: [rule]
### Testable Conditions
- [Normal] [condition] → [expected]
- [Boundary] [field] → [expected]
- [Exception] [condition] → [expected]
### Data Constraints
- [field]: [constraint]
### Permissions / Roles
- [role]: [allowed / not allowed]

## [Area 2: ...]
```

5. Save: `SRS_WIKI_<build>_<YYYY-MM-DD>.md` tại save path → use as Mode A baseline

BrSE có thể reuse wiki ở lần review sau bằng cách paste wiki path vào field 6.

---

### P4. Pre-processing & Micro-checkpoint

**Pre-processing (silent):**
- Excel input → convert sang markdown trước
- SRS Wiki Build nếu field 7a = A
- Auto-detect function type (C1), build type (C2)
- **Quick Mode trigger:** testcase ≤ 10 TC entries AND không có change log AND không có spec/viewpoint → Quick Mode: D1/D2/D5 skip, compact output

**Micro-checkpoint (output trước khi chạy dimensions):**
```
▶ Proceeding: Build [name] | Type: [inferred] | Testcase: N entries | Mode: [Full/Quick] | Coverage baseline: [A/B-wiki/B/C/D] | SRS Wiki: [saved at <path> / not built] | Downstream: [who] | Fix mode: [A/B/C]
  If incorrect → reply to correct before gap report is generated.
```
AI proceed ngay — không chờ BrSE reply.

---

### P5. Review Dimensions — D1 đến D5

Thực hiện tuần tự. Skip dimension có điều kiện ghi rõ bên dưới.

**D1 — Build Coverage** *(skip nếu không có change log hoặc Quick Mode)*

Với mỗi change trong build:
- ✅ Full coverage → không gap
- ⚠️ Partial → Major nếu critical path, Minor nếu không
- ❌ Not covered → Critical nếu business-critical, Major nếu không

**D2 — Regression Risk** *(skip nếu không có change log hoặc Quick Mode)*

Với mỗi change, identify impacted areas ngoài direct scope:
- 🔴 High: change ảnh hưởng shared module / core logic / data layer
- 🟡 Medium: adjacent UI / secondary flow bị ảnh hưởng
- 🟢 Low: change isolated, không có shared dependency

**D3 — Testcase Quality** *(always)*

Check tất cả sub-dimensions áp dụng:
- **Coverage** *(skip nếu Mode D)*: testcase có cover đủ viewpoint areas không?
- **Logic vs spec**: expected result có match confirmed spec không?
- **Clarity/executability**: steps + precondition + expected result có đủ rõ cho downstream?
- **Assumption visibility**: assumption/pending mark có explicit không?
- **Consistency**: cùng nhóm có nhất quán về format, ID, expected result pattern không?

**Downstream-aware severity cho clarity issues:**

| Downstream | Step/expected result cần interpretation | Minor ambiguity, executable |
|------------|----------------------------------------|----------------------------|
| Offshore (A) | **Major** | Minor |
| QA internal / BrSE / UAT (B/C/D) | Minor | Note |

**Heuristics table (Mode C):**

| Function type | Coverage areas cần check |
|--------------|--------------------------|
| UI screen | Normal flow, field validation, boundary, mandatory/optional, permission/role, error messages, navigation |
| API | Happy path, error codes (4xx/5xx), missing/invalid params, auth, response format, idempotency |
| Batch / report | Normal data, empty data, large volume, filter, date range, output format, trigger/schedule |
| Business flow | End-to-end happy path, branch conditions, rollback/cancel, status transitions, external dependency, re-entry |

**D4 — Execution Priority** *(always)*

- 🔴 Must-run: covers critical build change OR critical business path OR 🔴 regression area
- 🟡 Should-run: regression of impacted area / quality gate / high-risk module
- 🟢 Can-defer: low-risk / không bị ảnh hưởng bởi build này / stable regression suite

**D5 — Known Blockers** *(skip nếu không có known issues list hoặc Quick Mode)*

Với mỗi known issue: identify testcases bị ảnh hưởng → mark "Expected to fail — [issue]"

---

### P6. Self-Review Gate (internal — không output ra ngoài)

Trước khi viết gap report, AI verify tất cả 6 điểm:
1. **Severity consistent?** Critical chỉ khi zero coverage trên critical path hoặc expected result sai trên critical flow. Major chỉ khi execution area unreliable without fix.
2. **No over-classification?** Minor/Note cho issues fixable mà không block execution.
3. **Each finding actionable?** Mọi gap có "Suggested Action" cụ thể — không phải "add testcase" chung chung.
4. **Viewpoint coverage complete?** Mọi viewpoint area có explicit status: covered / partial / not covered.
5. **Clarity severities calibrated to downstream?** Offshore = stricter; QA internal/BrSE = lenient.
6. **Execution-ready after fixes?** Nếu tất cả Critical/Major resolved → testcase có execution-ready không? Nếu không → có gì đó vẫn missing, revise.

Nếu bất kỳ check nào fail → revise findings trước khi output.

---

### P7. Severity Classification

| Level | Definition | Impact on Execution |
|-------|-----------|---------------------|
| **Critical** | Build change không có testcase; hoặc testcase sẽ cho kết quả sai trên critical path | Must resolve trước khi bất kỳ execution nào bắt đầu |
| **Major** | Gap đáng kể; execution của area bị ảnh hưởng unreliable without fix | Must resolve trước khi execute area đó |
| **Minor** | Testcase executable nhưng kết quả có thể inaccurate/incomplete | Fix trước final execution report |
| **Note** | Improvement point; execution không bị block | Optional |

---

### P8. Go/No-go Decision Logic

| Recommendation | Condition |
|---------------|-----------|
| ⛔ Not ready | Bất kỳ Critical gap nào tồn tại |
| ⚠️ Ready with conditions | Major gaps tồn tại nhưng scoped vào non-critical areas; conditions nêu rõ |
| ✅ Ready | Chỉ có Minor/Note gaps; tất cả critical path testcases confirmed executable |

---

### P9. Fix Mode (field 9)

| Gap type | Severity | Mode B | Mode C |
|----------|----------|--------|--------|
| Clarity — ambiguous step/expected result | Minor/Note | ✅ Fix | ✅ Fix |
| Clarity — requires interpretation | Major | ❌ Skip | ✅ Fix |
| Consistency — format, ID, naming | Minor/Note | ✅ Fix | ✅ Fix |
| Assumption visibility — missing mark | Minor | ✅ Fix | ✅ Fix |
| Coverage gap — missing testcase | Any | ❌ Never | ❌ Never |
| Logic — wrong expected result | Any | ❌ Never | ❌ Never |

Fix mode B/C: sau khi output gap report, AI show **confirm gate** trước khi sửa:
```
🔧 Fix preview (Mode [B/C]):
Sẽ fix [N] gaps: [Gap ID list]
Không fix (cần human review): [Gap ID list]
Proceed with fixes? [Y / N]
```
Chờ BrSE reply Y. Fixes được save vào `<testcase>_fixed_<YYYY-MM-DD>.md` — **không bao giờ overwrite file gốc**.

---

### P10. Gap Report Format

**Skip-if-empty rule:** Section/sub-section không có finding → omit hoàn toàn, không print empty header.

**Header block:**
```markdown
# Gap Report — Test Case Review
**Build:** [name/version]  **Build type:** [auto-inferred]  **Review date:** YYYY-MM-DD
**Testcase target:** [name/version]
**Coverage baseline:** [A/B-wiki/B/C/D]  **Proposed viewpoint / SRS wiki:** [path or N/A]
**Downstream:** [who]  **Severity threshold:** [strict/standard]  **Mode:** [Full/Quick]

> **AI Understanding:** [1–2 câu scope và focus — BrSE reply nếu sai để AI re-review]

## Executive Summary
| Item | Value |
|------|-------|
| Build type | |
| Overall risk level | 🔴/🟡/🟢 |
| Go/No-go recommendation | ⛔/⚠️/✅ |
| Total gaps | N (Critical: X, Major: Y, Minor: Z, Note: W) |
| Execution-blocked testcases | N |
| Must-run testcase groups | N |
```

**Sections (omit if empty):**
1. Build Coverage Gaps — table: ID / Change / Coverage / Gap / Severity / Action / Owner
2. Regression Risk Areas — table: Area / Impacted by / Risk Level / Existing TC / Recommendation
3. Testcase Quality Gaps — table: ID / Type / Issue / TC Ref / Severity / Suggested Action / Owner
4. Execution Priority — 🔴 Must-run / 🟡 Should-run / 🟢 Can-defer
5. Execution Blockers — table: TC / Known Issue / Action
6. Action Items — table: ID / Action / Severity / Owner / By When
7. Fix Log *(Fix mode B/C only)*

**Quick Mode format (compact):** Header + Summary + Quality Gaps table + Priority line + Action Items only.

**Save path:** `04_generated_outputs/REVIEW_TC_GAP_REPORT_<build>_<YYYY-MM-DD>.md` trong task workspace.

---

## 8. Template đề xuất

# Template — Shared AIP for "Review test case"

## A. Metadata
- AIP ID:
- Title:
- Status: Draft
- Owner:
- Related Project / Phase:
- Review Target: (testcase document name / version)
- Test Viewpoint Reference:
- Input Understanding Status:
- Review Viewpoint Status:
- Related Documents:
- Related AIPs:
- Reviewers:
- Testcase Author:

## B. Objective
- Mục tiêu của review này là gì?
- Review này nhằm phục vụ bước tiếp theo nào (execute / handoff / UAT)?
- Sau review, điều gì phải trở nên rõ hơn hoặc an toàn hơn?

## C. Context Summary
- Background ngắn của bộ testcase
- Vì sao cần review lúc này
- Downstream impact nếu testcase có issue mà không phát hiện sớm
- Review round hiện tại là round mấy nếu có

## D. Input Sources / Required References

| Input | Description | Required/Optional | Source | Used in step |
| ----- | ----------- | ----------------- | ------ | ------------ |
| Testcase document | target review | Required | Internal | E, G, H, I |
| Finalized test viewpoint | coverage baseline | Required | Internal | G, H |
| Requirement / spec / design | logic baseline | Required | Internal/Customer | I.2 |
| Clarification results | confirmed business rules | Optional | Internal/Customer | I.2 |
| Open issue / assumption list | uncertainty visibility | Optional | Internal | I.4 |
| Common review checklist | standard criteria | Optional | Internal | H |
| Prior review comments | continuity | Optional | Internal | I |
| **Build release notes / change log** | list of changes in this build | Optional* | Internal/Dev team | G.1, G.2, K.1 |
| **Targeted bug fix list** | what exactly is fixed (bug-fix builds) | Optional* | Internal/Dev team | G.1 |
| **Known build issues list** | defects already known in this build | Optional* | Internal/Dev team | K.2 |

*Optional nhưng strongly recommended khi nhận build: không có build context → không thể thực hiện Dimensions 1, 2, 5.

## D.1 Build Context

*Điền khi AIP được tạo trong bối cảnh nhận bản build cụ thể.*

| Field | Value |
| ----- | ----- |
| Build ID / version | |
| Build type | feature release / bug-fix / CR / mixed |
| Key changes in build | [list features / fixes / CRs] |
| Known issues in build | [list or "none"] |
| Downstream executor | offshore / QA internal / BrSE / UAT |
| Execution deadline | |

## E. Input Understanding and Reviewer Confirmation
### E.1 Understanding outputs
Trước khi review sâu, AI phải output tối thiểu:
- test objective understanding
- test viewpoint coverage understanding (viewpoint cover những gì?)
- scope / boundary understanding (in/out-of-scope testcase)
- known pending/open-point understanding trong testcase hiện tại
- intended downstream usage understanding (execute trực tiếp / offshore handoff / UAT?)

### E.2 Reviewer / BrSE Confirmation Rule
- BrSE hoặc reviewer phải confirm working-level understanding trước khi review findings được coi là hợp lệ để đi tiếp
- nếu có phần input chưa đủ chắc, phải giữ visible như uncertainty note

## F. Review Scope
### In Scope
- phần nào của testcase được review
- viewpoint nào sẽ cover
- case categories nào được focus

### Out of Scope
- phần không review trong round này
- case defer sang phase khác
- execution-level detail không thuộc review task này

## G. Test Viewpoint Alignment Check
| Viewpoint (from approved viewpoint) | Covered in testcase? | Gap / Note |
| ------------------------------------ | -------------------- | ---------- |
| Normal flow | yes / partial / no | |
| Abnormal flow | yes / partial / no | |
| Boundary | yes / partial / no | |
| Validation | yes / partial / no | |
| Permission / role | yes / partial / no | |
| Dependency / IF | yes / partial / no | |

## G.1 Build Coverage Analysis
*(Thực hiện khi có build change log. Skip nếu không có — ghi rõ "Not assessed: build change log unavailable")*

| Change (from build) | Build Type | Testcase Exists? | Coverage Level | Gap Description | Severity |
| ------------------- | ---------- | ---------------- | -------------- | --------------- | -------- |
| [feature / fix / CR name] | feature / fix / CR | Yes / No | Full / Partial / None | | Critical / Major / — |

**Build coverage summary:**
- Total changes: N | Fully covered: X | Partially covered: Y | Not covered: Z

## G.2 Regression Risk Assessment
*(Thực hiện khi có build change log. Skip nếu không có.)*

| Area | Impacted by (build change) | Risk Level | Existing Testcases | Recommendation |
| ---- | -------------------------- | ---------- | ------------------ | -------------- |
| | | 🔴 High / 🟡 Medium / 🟢 Low | | |

Risk classification basis:
- 🔴 High: change ảnh hưởng shared module / core business logic / data layer
- 🟡 Medium: change ảnh hưởng adjacent UI / secondary flow
- 🟢 Low: change isolated, không có shared dependency

## H. Review Viewpoints
| Viewpoint | What to check | Why it matters | Priority |
| --------- | ------------- | -------------- | -------- |
| Coverage vs viewpoint | tất cả viewpoint area có testcase cover không | prevent coverage gap | High |
| Logic vs spec/design | expected result có đúng với spec không | prevent wrong execution | High |
| Clarity / executability | steps, precondition, expected result có đủ rõ để execute không | offshore executability | High |
| Assumption visibility | assumption/pending point có được mark rõ không | prevent silent test failure | High |
| Consistency | các case trong cùng nhóm có nhất quán không | reduce confusion | Medium |
| Priority / criticality | case nào là must-run, case nào là optional | test efficiency | Medium |

## I. Findings / Issues
### I.1 Coverage Gap
| ID | Missing Area | Viewpoint Reference | Impact | Suggested Action | Owner |
| -- | ------------ | ------------------- | ------ | ---------------- | ----- |

### I.2 Logic / Spec Issues
| ID | Issue | Testcase Ref | Severity | Impact | Suggested Action | Owner |
| -- | ----- | ------------ | -------- | ------ | ---------------- | ----- |

### I.3 Clarity / Executability Issues
| ID | Issue | Testcase Ref | Severity | Suggested Action | Owner |
| -- | ----- | ------------ | -------- | ---------------- | ----- |

### I.4 Notes / Improvement Points
| ID | Note | Why it matters | Optional/Required |
| -- | ---- | -------------- | ----------------- |

### I.5 Positive Confirmations
| Item | What is already good / clear | Why useful |
| ---- | ---------------------------- | ---------- |

## J. Review Viewpoint / Self Review

**Reviewer:** BrSE / AI | **Purpose:** Tự kiểm review package trước khi handoff | **Pass condition:** Tất cả checks = PASS

| Check | Pass condition |
| ----- | -------------- |
| Review scope có đúng không | Scope khớp với Section F — không review ngoài scope khai báo |
| Tất cả viewpoint area đã được check chưa | Mọi area trong Section G đều có status (covered / partial / no) |
| Coverage gap có đầy đủ và actionable không | Mỗi gap có Suggested Action cụ thể (không phải "add testcase" chung chung) |
| Logic issue có đúng spec không | Issue logic có reference confirmed spec / clarification result |
| Severity / impact có hợp lý không | Major chỉ khi execution bị ảnh hưởng; Critical chỉ khi không thể execute |
| Downstream có execute được sau khi update không | Nếu tất cả Critical/Major resolved → testcase execution-ready |

## K. Coordination / Re-review Plan

| Step | Action | Input | Owner | Output |
| ---- | ------ | ----- | ----- | ------ |
| 1 | Confirm input understandings | Section D inputs | BrSE / Reviewer | confirmed understanding (Section E) |
| 2 | Draft review findings | confirmed understandings + viewpoint + spec | Reviewer / AI | findings draft (Section I) |
| 3 | Create review viewpoint and self review | findings draft | Reviewer / AI | reviewed findings (Section J) |
| 4 | Send consolidated result to testcase author | reviewed findings | BrSE / Reviewer | handoff review package |
| 5 | Testcase author updates document | handoff review package | Testcase author | revised testcase |
| 6 | Re-review Major issues | revised testcase | Reviewer | confirmed closure |
| 7 | Update AIP status and tracker | confirmed closure | BrSE | AIP status = Closed; tracker updated |

## K.1 Execution Priority
*(Based on build risk + testcase criticality)*

| Priority | Testcase / Group | Basis | Note |
| -------- | ---------------- | ----- | ---- |
| 🔴 Must-run | | covers critical build change / critical business path | |
| 🟡 Should-run | | regression risk area / quality gate | |
| 🟢 Can-defer | | low-risk / not affected by this build | |

## K.2 Known Execution Blockers
*(Testcases expected to fail due to known build issues. Skip nếu không có known issues list.)*

| Testcase / Group | Known Build Issue | Action |
| ---------------- | ----------------- | ------ |
| | | Mark as expected-fail; re-test after fix |

*(Empty = no known blockers identified)*

## L. Downstream Impact / Proceed Rule

| Downstream Task | How review result affects it | Blocked by which severity |
| --------------- | ---------------------------- | ------------------------- |
| Test execution (offshore) | unsafe if steps/expected result unclear | Critical/Major |
| QA execution | weak if coverage gap exists | Major |
| UAT preparation | risky if business logic wrong | Major |
| Regression suite | inconsistent if cases not structured | Medium |

## M. Expected Outputs

| Output | File name | Format | Save path |
| ------ | --------- | ------ | --------- |
| Input understanding confirmation | (inline — Section E) | Markdown section | AIP document |
| Viewpoint alignment check | (inline — Section G) | Markdown table | AIP document |
| Review findings (coverage / logic / clarity) | (inline — Section I) | Markdown tables | AIP document |
| Issue list with severity / owner / action | (inline — Section I) | Markdown table | AIP document |
| Re-review / handoff plan | (inline — Section K) | Markdown table | AIP document |
| Gap report (AI-generated per Section 7.5 protocol) | `REVIEW_TC_GAP_REPORT_<build>_<YYYY-MM-DD>.md` | Markdown | `04_generated_outputs/` trong task workspace |

## N. Done Criteria
Task is done when:
- input understandings are confirmed
- viewpoint alignment has been checked
- review findings are structured clearly
- review viewpoint exists and self-review has been performed
- issue list is handed over to the correct owner
- tracker has been updated (AIP status = Closed)
- downstream team knows whether testcase is execution-ready or needs update

## O. Risks

| # | Risk | Likelihood | Impact | Mitigation |
| - | ---- | ---------- | ------ | ---------- |
| R-01 | AI hiểu sai scope review → findings sai hướng | Medium | Review không valuable; phải redo | BrSE confirm Section E understandings trước khi finalize |
| R-02 | Viewpoint chưa finalize được dùng làm baseline → coverage assessment sai | Medium | Coverage gap missed hoặc false gap | Verify viewpoint status trước khi bắt đầu (Section G) |
| R-03 | Severity over-classified → testcase author ưu tiên sai | Medium | Effort bị lãng phí vào minor issue | BrSE spot-check Major/Critical findings trước khi handoff |
| R-04 | Build change log không đầy đủ → G.1/G.2 assessment thiếu | Medium | Coverage gap bị bỏ sót | Note "change log incomplete" trong Section G.1; verify với Dev team |

---

## 9. Sample AIP

# Sample — AIP for "Review testcase màn hình Order Entry"

## A. Metadata
- AIP ID: AIP-SHARED-008-review-testcase-order-entry
- Title: Review testcase màn hình Order Entry
- Status: Draft
- Owner: BrSE
- Related Project / Phase: Test design review / QA gate
- Review Target: Order Entry Testcase v1.0
- Test Viewpoint Reference: Order Entry Test Viewpoint (finalized)
- Input Understanding Status: pending reviewer confirmation
- Review Viewpoint Status: to be created before finalize
- Related Documents:
  - Order Entry Testcase v1.0
  - Order Entry Test Viewpoint (finalized)
  - Requirement summary v0.2
  - Basic Design v1.0
  - Clarification result on duplicate handling
  - Open issue / assumption list
  - Common checklist for testcase review
- Related AIPs:
  - AIP-PLAN-007-create-testcase-order-entry
  - AIP-SHARED-004-review-basic-design-order-entry
- Reviewers:
  - BrSE
  - QA lead (optional for coverage alignment viewpoint)
- Testcase Author:
  - QA / SE

## B. Objective
- Review bộ testcase Order Entry để phát hiện coverage gap vs viewpoint, logic issue vs spec, và clarity issue ảnh hưởng offshore execution
- Tạo review package có cấu trúc để testcase author update hiệu quả
- Giảm risk execution failure do testcase thiếu hoặc sai trước khi handoff offshore

## C. Context Summary
Bộ testcase Order Entry đã được draft dựa trên finalized test viewpoint, basic design và các clarification quan trọng.
Trước khi dùng cho execution hoặc handoff offshore, cần review để kiểm tra:
- coverage có bám viewpoint đã approve không
- logic expected result có đúng với spec/design không
- steps và precondition có đủ rõ để offshore execute không
- open point / assumption có visible không

Nếu không review trước:
- offshore có thể execute sai hoặc không hiểu expected result
- coverage gap có thể dẫn đến defect bị bỏ sót
- assumption bị giấu trong testcase có thể tạo false pass

## D. Input Sources / Required References

| Input | Description | Required/Optional | Source | Used in step |
| ----- | ----------- | ----------------- | ------ | ------------ |
| Order Entry Testcase v1.0 | target review | Required | Internal | E, G, H, I |
| Order Entry Test Viewpoint (finalized) | coverage baseline | Required | Internal | G, H |
| Requirement summary v0.2 | logic baseline | Required | Internal | I.2 |
| Basic Design v1.0 | behavior structure | Required | Internal | I.2 |
| Clarification result on duplicate handling | confirmed business rules | Required | Internal/Customer | I.2 |
| Open issue / assumption list | uncertainty visibility | Optional | Internal | I.4 |
| Common checklist for testcase review | standard review criteria | Optional | Internal | H |

## E. Input Understanding and Reviewer Confirmation
### E.1 Understanding outputs
Trước khi review sâu, AI/reviewer phải output tối thiểu:
- Order Entry testcase được tạo để cover: normal flow, duplicate handling, mandatory field validation, và một số abnormal/boundary cases
- Test viewpoint đã finalize và approve bởi BrSE — là baseline bắt buộc cho review
- Intended downstream usage: handoff sang offshore để execute trực tiếp
- Một số open point về duplicate validation timing vẫn đang được handled bằng visible assumption
- auto-save nằm ngoài scope và không nên có testcase

### E.2 Reviewer / BrSE Confirmation Rule
- BrSE/reviewer phải confirm các understandings trên đúng ở mức working level trước khi findings được finalize
- nếu có phần chưa chắc, phải giữ visible như uncertainty note

## F. Review Scope
### In Scope
- coverage alignment vs Order Entry test viewpoint (finalized)
- logic alignment vs requirement / clarification / basic design
- clarity và executability của steps, precondition, expected result
- assumption / open point visibility trong testcase
- consistency giữa các case trong cùng nhóm

### Out of Scope
- test execution (không execute testcase trong task này)
- review test viewpoint (viewpoint đã finalize — không phải scope review này)
- performance / security test
- testcase ngoài phạm vi màn hình Order Entry

## G. Test Viewpoint Alignment Check
| Viewpoint (from approved viewpoint) | Covered in testcase? | Gap / Note |
| ------------------------------------ | -------------------- | ---------- |
| Normal flow — create order successfully | partial | thiếu case confirm sau save |
| Duplicate handling | yes | có nhưng assumption về timing chưa rõ |
| Mandatory field validation | yes | đủ coverage |
| Abnormal / invalid input | partial | thiếu một số edge case về customer code |
| Role / permission exception | no | chưa có — defer vì spec chưa confirm |
| Dependency — customer code master | partial | có nhưng chưa cover case master không tồn tại |

## H. Review Viewpoints
| Viewpoint | What to check | Why it matters | Priority |
| --------- | ------------- | -------------- | -------- |
| Coverage vs viewpoint | từng viewpoint area có được cover không | prevent gap | High |
| Logic vs spec/design | expected result có đúng với confirmed rules không | prevent wrong execution | High |
| Clarity / executability | offshore có execute được step-by-step không | handoff quality | High |
| Assumption visibility | assumption / pending point có mark rõ không | prevent silent failure | High |
| Consistency | case cùng nhóm có nhất quán không | reduce execution confusion | Medium |
| Priority / must-run | case nào là critical execution | test efficiency | Medium |

## I. Findings / Issues

### I.1 Coverage Gap
| ID | Missing Area | Viewpoint Reference | Impact | Suggested Action | Owner |
| -- | ------------ | ------------------- | ------ | ---------------- | ----- |
| CG-01 | Thiếu case confirm state sau save thành công | Normal flow | offshore không biết success state cần verify gì | thêm case confirm sau save | Testcase author |
| CG-02 | Thiếu case customer code không tồn tại trong master | Dependency | dependency error không được cover | thêm case hoặc mark defer nếu spec chưa rõ | Testcase author |

### I.2 Logic / Spec Issues
| ID | Issue | Testcase Ref | Severity | Impact | Suggested Action | Owner |
| -- | ----- | ------------ | -------- | ------ | ---------------- | ----- |
| LG-01 | Expected result của duplicate case không match confirmed rule | TC-DUP-02 | Major | offshore execute sai, có thể mark false pass | update expected result theo confirmed clarification | Testcase author |
| LG-02 | Validation order trong testcase khác với basic design | TC-VAL-01 | Minor | execution order misleading | align step order với BD | Testcase author |

### I.3 Clarity / Executability Issues
| ID | Issue | Testcase Ref | Severity | Suggested Action | Owner |
| -- | ----- | ------------ | -------- | ---------------- | ----- |
| CL-01 | Precondition không nêu rõ trạng thái customer code master | TC-DUP-01 | Major | offshore không setup đúng data | bổ sung explicit precondition | Testcase author |
| CL-02 | Steps sử dụng "hệ thống" mà không rõ UI element nào | TC-NORM-03 | Minor | offshore phải đoán | thay bằng mô tả rõ button/field | Testcase author |

### I.4 Notes / Improvement Points
| ID | Note | Why it matters | Optional/Required |
| -- | ---- | -------------- | ----------------- |
| N-01 | Thêm cột "Assumption" vào các case có pending spec | tăng transparency với offshore | Optional |
| N-02 | Group testcase theo viewpoint area rõ hơn | giảm confusion khi execute | Optional |

### I.5 Positive Confirmations
| Item | What is already good / clear | Why useful |
| ---- | ---------------------------- | ---------- |
| PC-01 | Coverage của mandatory field validation đủ và rõ | có thể execute ngay sau update minor |
| PC-02 | Cấu trúc testcase ID nhất quán và có prefix rõ | dễ reference trong bug report |
| PC-03 | Assumption về auto-save out-of-scope đã visible | offshore không bị confuse |

## J. Review Viewpoint / Self Review

**Reviewer:** BrSE / AI | **Purpose:** Tự kiểm review package trước khi handoff sang testcase author | **Pass condition:** Tất cả checks = PASS

| Check | Pass condition |
| ----- | -------------- |
| Coverage gap có cover đủ viewpoint area không | Mọi viewpoint area trong Section G đều có status rõ |
| Logic issue có reference đúng confirmed spec không | Mỗi logic issue (LG-*) cite đúng confirmed clarification hoặc spec section |
| Clarity issue có actionable cho testcase author không | Mỗi clarity issue có Suggested Action đủ cụ thể để author hiểu và sửa ngay |
| Severity classification có hợp lý không | Major chỉ khi offshore không thể execute đúng; Critical khi không thể execute |
| Findings có usable cho offshore không | Sau khi author update Critical/Major issues, offshore có thể execute mà không cần hỏi thêm |

## K. Coordination / Re-review Plan

| Step | Action | Input | Owner | Output |
| ---- | ------ | ----- | ----- | ------ |
| 1 | Confirm input understandings | Section D inputs (testcase + viewpoint + spec) | BrSE / Reviewer | confirmed understanding (Section E) |
| 2 | Draft review findings | confirmed understandings + viewpoint + spec | Reviewer / AI | findings draft (Section I) |
| 3 | Create review viewpoint and self review | findings draft | Reviewer / AI | reviewed findings (Section J) |
| 4 | Send consolidated issue list to testcase author | reviewed findings | BrSE / Reviewer | handoff review package |
| 5 | Testcase author updates document | handoff review package | Testcase author | revised testcase v1.1 |
| 6 | Re-review Major issues (CG-01, LG-01, CL-01) | revised testcase v1.1 | Reviewer | confirmed closure of major issues |
| 7 | Confirm execution readiness | confirmed closure | BrSE / QA lead | go/no-go for offshore execution |
| 8 | Update AIP status and tracker | go/no-go decision | BrSE | AIP status = Closed; tracker updated |

## L. Downstream Impact / Proceed Rule

| Downstream Task | How review result affects it | Blocked by which severity |
| --------------- | ---------------------------- | ------------------------- |
| Offshore execution | unsafe if steps/expected result unclear | Critical/Major |
| QA execution | incomplete if coverage gap exists | Major |
| UAT preparation | risky if business logic wrong | Major |
| Regression suite | inconsistent if cases not structured | Medium |

## M. Expected Outputs

| Output | File name | Format | Save path |
| ------ | --------- | ------ | --------- |
| Input understanding confirmation | (inline — Section E) | Markdown section | AIP document |
| Viewpoint alignment check | (inline — Section G) | Markdown table | AIP document |
| Review findings (coverage / logic / clarity) | (inline — Section I) | Markdown tables | AIP document |
| Issue list with severity / owner / action | (inline — Section I) | Markdown table | AIP document |
| Re-review / coordination plan | (inline — Section K) | Markdown table | AIP document |
| Gap report (AI-generated per Section 7.5 protocol) | `REVIEW_TC_GAP_REPORT_OrderEntry_<YYYY-MM-DD>.md` | Markdown | `04_generated_outputs/` trong task workspace |

## N. Done Criteria
Task is done when:
- input understandings are confirmed
- viewpoint alignment has been checked for all areas
- review findings are structured clearly
- review viewpoint exists and self-review has been performed before close
- issue list is handed over to the correct owner (testcase author)
- major issues (CG-01, LG-01, CL-01) have been re-reviewed after update
- tracker has been updated (AIP status = Closed)
- downstream team (offshore / QA) knows whether testcase is execution-ready

## O. Risks

| # | Risk | Likelihood | Impact | Mitigation |
| - | ---- | ---------- | ------ | ---------- |
| R-01 | Duplicate handling spec còn ambiguous → LG-01 không resolve được | Medium | Review round 2 bị block | BrSE escalate clarification trước khi handoff; ghi rõ trong AIP là pending spec |
| R-02 | Offshore không hiểu visible assumption về auto-save out-of-scope | Low | False fail trên assumption | Add explicit note vào testcase precondition (CL-01 fix) |
| R-03 | Role/permission testcase bị defer dài hạn → coverage gap tồn tại đến UAT | Medium | Defect leak đến UAT | BrSE xác nhận defer condition và set re-review trigger khi spec confirm |

---

## 10. Variant nên có cho task này

### Variant 1 — Review testcase for coverage completeness
Dùng khi trọng tâm là check coverage vs viewpoint, không phải logic detail.

### Variant 2 — Review testcase for offshore executability
Dùng khi trọng tâm là clarity của steps / precondition / expected result cho offshore team.

### Variant 3 — Review changed testcase after CR / bug fix
Dùng khi chỉ review phần testcase thay đổi do CR hoặc bug fix.

### Variant 4 — Multi-reviewer consolidated testcase review
Dùng khi BrSE + QA lead cùng review và cần merge kết quả.

### Variant 5 — Review testcase for UAT readiness
Dùng khi chuẩn bị testcase cho customer / UAT team — focus vào business flow và wording.

### Variant 6 — Review testcase for feature release build
Dùng khi nhận build có feature mới. Focus: build coverage gaps cho feature + regression risk của modules bị ảnh hưởng.
Requires: build change log + feature spec. Output priority: gap report section 1 (Build Coverage) + execution priority.

### Variant 7 — Review testcase for bug-fix build
Dùng khi nhận bug-fix patch. Focus: testcase cho từng bug fix target + regression xung quanh fix area.
Requires: bug fix list + related testcases. Output priority: bug fix verification coverage + known blocker assessment.

### Variant 8 — Review testcase for CR release
Dùng khi nhận build theo Change Request. Focus: CR scope coverage + alignment vs updated spec/design.
Requires: CR document + updated spec. Output priority: CR coverage gaps + logic/spec alignment issues.

### Variant 9 — Review testcase for mixed build (feature + fix + CR)
Dùng khi build kết hợp nhiều loại thay đổi. Focus: toàn bộ 5 dimensions. Prioritize by risk level.
Requires: full build change log. Output priority: full gap report + execution priority phân loại theo change type.

---

## 11. Gợi ý sample tiếp theo liên quan chặt tới task này

Sau sample này, các sample tiếp theo nên làm là:

1. **Member AIP — Bug root cause investigation** (sau khi execution phát hiện lỗi)
2. **PM AIP — Risk / issue tracking** (nếu coverage gap ảnh hưởng schedule)
3. **Shared AIP — Clarification round after offshore questions** (nếu execution gap cần escalate)
4. **PLAN AIP — Create test viewpoint** (nếu viewpoint cần revise do review findings)
5. **PLAN AIP — Customer status report** (nếu test quality impact cần báo cáo KH)

---

## 12. Final note

Task "Review test case" không chỉ là check "testcase đúng sai".

AIP cho task này nên tập trung vào:

> **viewpoint alignment + logic correctness + offshore executability + assumption visibility + structured findings + coordination / re-review rule**

để bộ testcase sau review thực sự execution-ready và downstream-safe.
