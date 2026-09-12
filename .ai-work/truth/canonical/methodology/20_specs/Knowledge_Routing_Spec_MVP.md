# Knowledge Routing Spec for AI Work System MVP
Version: 0.1  
Status: Canonical merged spec  
Scope: Knowledge Hub / Specs / Guidelines

## Related Specs (Other Layer)
*(Added CR-G3 — AIP-EXEC-015 STEP-01)*

- **Lookup Key Strategy:** `product/wiki_guidelines/core/specs/Lookup_Key_Strategy_Spec_MVP.md`
  — T1/T2/T3 tier system defines how lookup keys in artifact meta support this spec's routing inputs
- **WIKI_META_INDEX_SPEC:** `product/wiki_guidelines/core/specs/WIKI_META_INDEX_SPEC.md`
  — artifact meta structure (Lớp 1) that this routing spec consumes

> **2-layer reconciliation (CR-AIWS-2026-05-020 / AIP-EXEC-038):** "object/concept" and "Knowledge Hub objects"
> below denote the abstract resolved concept; the knowledge unit is the **artifact-level meta** (Lớp 1).
> Expansion uses the meta's **`## Related Sources`** (typed roles) — retired record: xem
> `Knowledge_Object_Model_Spec_MVP` §8 (CR-AIWS-2026-05-005).
>
> **Two-kind node update (CR-AIWS-2026-05-023 / CR-AIWS-2026-05-029):** "object/concept" now resolves to an
> **object-node meta (`node_kind=object`)** when one exists, ELSE to the describing artifact metas — still **no
> retired-record shape** (INV-1/INV-2 — xem `Knowledge_Object_Model_Spec_MVP` §8). Identity = ordinary
> `source_id` (family prefix e.g. `SRC-FUNC-`). Expansion follows the meta's `## Related Sources` (three registers —
> documentary / representation `represented_by` / domain `x:`) and `wiki_relations.py --relations` for reverse/impact;
> the one-hop / no-precomputed-global-graph stance is **unchanged**. Where the text below says "resolve object" /
> "direct expansion links từ object", read it as resolving the object-node (or describing metas) and following its
> `## Related Sources` edges.

---

# 1. Purpose of this spec

Tài liệu này mô tả phần **canonical spec ở mức routing** cho `Knowledge Routing` trong Knowledge Hub của AI Work System current canonical baseline.

Mục tiêu của tài liệu là:
- chốt cách AI **tìm, lọc, mở rộng, và dừng** trong Knowledge Hub
- làm rõ:
  - AI route dựa trên input nào
  - AI chọn scope precedence thế nào
  - AI resolve object/concept ở bước nào
  - AI expansion theo hướng nào
  - khi nào AI cần kéo HUMAN vào
  - khi nào AI phải warning rằng kết quả mới chỉ dừng ở wiki layer
- giữ nguyên tắc:
  - **wiki first**
  - **không grep full raw source quá sớm**
  - **deep research phải có scope rõ**

Lưu ý:
- đây là routing spec logic
- không phải implementation của search engine / graph traversal / MCP / vector DB
- không thay thế Task Lens policy hay object model
- nhưng là cầu nối giữa:
  - Task Lens
  - Knowledge Hub objects
  - Discovery / Selection
  - Working AIP preparation

---

# 2. What Knowledge Routing is / is not

## 2.1. What Knowledge Routing is
Trong AI Work System, `Knowledge Routing` là:

> **cơ chế AI dùng để quyết định bắt đầu tìm ở đâu, ưu tiên knowledge nào, resolve object/concept thế nào, mở rộng tiếp theo hướng nào, và dừng ở mức nào để đi sang bước tiếp theo**

Knowledge Routing tồn tại để:
- tránh search lan man
- giúp AI đi đúng scope và đúng task lens
- giúp AI biết khi nào knowledge ở wiki đã đủ
- giúp AI biết khi nào cần đi sâu hơn vào source artifact raw

## 2.2. What Knowledge Routing is not
Knowledge Routing **không phải**:
- full-text grep mọi nơi mặc định
- full source scan by default
- search engine implementation detail
- object model itself
- full research workflow độc lập với task

---

# 3. Core routing principles

## 3.1. Wiki-first by default
AI phải ưu tiên:
- search trong Knowledge Hub / Wiki
- dùng curated objects
- dùng aliases
- dùng natural-language expressions
- dùng expansion links
- dùng source anchors

AI không nên nhảy thẳng vào raw grep/full source scan trừ khi:
- wiki chưa đủ cho next decision
- task yêu cầu phân tích sâu hơn
- hoặc HUMAN yêu cầu rõ

## 3.2. Resolve before deep expansion
AI nên resolve:
- target object
- target concept
- task lens
- domain
- scope precedence

ở mức đủ rõ **trước khi expansion sâu**.

## 3.3. Search should be task-lens-aware
AI không nên route chỉ theo raw keyword.
AI phải route theo:
- task lens
- domain
- scope
- resolved objects/concepts

## 3.4. Expansion should be controlled
Sau khi thấy object/concept đầu tiên,
AI không mở rộng mọi thứ liên quan một cách vô hướng.

AI nên:
- ưu tiên expansion links phù hợp với task lens
- dừng khi đã đủ cho next decision
- tránh information sprawl

## 3.5. Evidence depth must be explicit
Nếu AI mới chỉ dừng ở wiki layer,
AI phải nói rõ điều đó.

Nếu task cần deep analysis mà AI chưa kiểm tra raw source artifact,
AI phải warning để tránh tạo cảm giác overconfidence.

## 3.6. Deep research beyond wiki must be scoped
Nếu cần deep research ngoài wiki:
- AI không nên grep full source mặc định
- AI nên đề xuất scope dưới dạng:
  - folder
  - nhóm folder
  - source zone
- rồi để BrSE chọn trước

---

# 4. Routing goals

Knowledge Routing nên đạt các goals sau:

## 4.1. Fast initial orientation
AI nhanh chóng biết bắt đầu ở đâu.

## 4.2. Relevant-first retrieval
AI ưu tiên knowledge gần task nhất.

## 4.3. Controlled expansion
AI mở rộng có định hướng, không đọc lan man.

## 4.4. Efficient stop decision
AI biết khi nào đã đủ để sang bước tiếp theo.

## 4.5. Honest evidence signaling
AI biết nói rõ kết quả đang ở:
- wiki-only level
- hay đã source-checked

---

# 5. Routing inputs

Knowledge Routing nên dùng các input tối thiểu sau:

## 5.1. `task_family`
Ví dụ:
- `clarify_requirement`
- `create_design`
- `review_design`
- `write_testcase`
- `implement_code`
- `investigate_issue`

## 5.2. `task_lens`
Có thể là:
- preset lens
- runtime-defined lens đã được confirm
- hoặc lens do AI suy ra từ context hiện tại

## 5.3. `target_object_ref`
Ví dụ:
- chức năng A
- 0001
- 受注入力
- order entry
- Basic Design
- MES

## 5.4. `target_object_type`
Nếu đã biết, ví dụ:
- `function`
- `concept`
- `artifact`
- `table`
- `interface`

## 5.5. `domain_hint`
Ví dụ:
- `cobol_migration`
- `mes_scada`
- `project_management`

## 5.6. `current_goal_or_stage`
Ví dụ:
- `discovery`
- `selection`
- `working_aip_prep`
- `execution_support`
- `capture`

---

# 6. Routing layers

Knowledge Routing nên đi theo 5 lớp chính, theo thứ tự logic sau:

## 6.1. Task Lens
AI xác định:
- đang làm loại task gì
- đang nhìn knowledge theo góc nào

Ví dụ:
- review_detail_design_function
- write_testcase_function
- implement_function_code

## 6.2. Domain
AI xác định domain tri thức chính.

Ví dụ:
- cobol_migration
- mes_scada
- project_management

## 6.3. Scope precedence
AI xác định nên ưu tiên:
- project
- common
- local
theo mode phù hợp với task hiện tại

## 6.4. Object / concept resolution
AI resolve:
- object nào đang được nói tới
- concept nào đang được nói tới

## 6.5. Expansion
Sau khi có object/concept đầu tiên,
AI dùng expansion links để mở rộng tiếp theo hướng phù hợp với current task lens.

---

# 7. Scope precedence modes

Knowledge Routing **không nên cố định một chiều duy nhất**.
Nó nên hỗ trợ các mode sau.

## 7.1. Project-first mode
Default cho **project execution tasks**.

### Priority
1. `project`
2. `common`
3. `local`

### Typical use cases
- review detail design function A
- create testcase for function B
- coding module C

## 7.2. Common-first mode
Default cho **general/domain learning tasks**.

### Priority
1. `common`
2. `project`
3. `local`

### Typical use cases
- MES là gì
- cách quản lý dự án
- COBOL migration principles

## 7.3. Local-first mode
Chỉ nên dùng cho **working continuity / local working context**.

### Priority
1. `local`
2. `project`
3. `common`

### Typical use cases
- continue my local scratch plan
- refine my local working note
- use local runtime lens I just created

## 7.4. Design rule
`resolved_scope_precedence` nên được giữ explicit trong routing summary,
không nên để AI âm thầm đổi mode mà không rõ.

---

# 8. Object and concept resolution rules

## 8.1. Resolution should happen early
AI nên resolve:
- target object
- target concept

ở mức đủ rõ **trước khi expansion sâu**.

## 8.2. Resolution sources
AI có thể resolve bằng:
- canonical names
- alias entries
- natural-language expressions
- related keywords
- context from task lens/domain/scope

## 8.3. Canonical confirmation rule
Nếu BrSE dùng non-canonical name,
AI nên confirm canonical object/concept trước khi retrieval/expansion sâu hơn.

## 8.4. Example
Input:
> review BD của chức năng 0001

Resolution:
- `BD` → concept `Basic Design`
- `chức năng 0001` → function object `func_order_entry_0001`

Then AI confirms canonical names before going deeper.

---

# 9. Expansion rules

## 9.1. Expansion must be lens-aware
Cùng một object có thể mở rộng theo các hướng khác nhau tùy task lens.

### Example
Object: `func_order_entry_0001`

#### If lens = `review_detail_design_function`
Priority expansion:
- related design
- related requirement
- related interface/api
- related test

#### If lens = `write_testcase_function`
Priority expansion:
- related requirement
- related rule
- related design
- related test patterns

#### If lens = `implement_function_code`
Priority expansion:
- related design
- related implementation
- related test
- related system objects/modules

## 9.2. Expansion should follow meaningful links first
AI nên ưu tiên:
- direct expansion links từ object
- authoritative references
- project-relevant links
trước khi mở rộng rộng hơn theo weak semantic relations

## 9.3. Expansion should stop when enough
AI không cần đi hết tất cả nhánh expansion.
AI chỉ cần đi đến mức đủ cho next decision.

---

# 10. Stop conditions

## 10.1. Sufficient-for-next-decision
Đây là stop condition chính.

AI nên dừng routing khi đã có đủ knowledge để:
- chọn use case
- chọn template
- tạo Working AIP
- hỗ trợ execution của bước hiện tại

## 10.2. No-significant-information-gain
Nếu expansion tiếp theo không tạo thêm nhiều giá trị cho next decision,
AI nên dừng.

## 10.3. HUMAN-gate-before-broader-search
Nếu routing bắt đầu chạm:
- ambiguity lớn
- multiple candidate objects
- scope decision quan trọng
- raw source deep research boundary

AI nên kéo HUMAN vào thay vì tự mở quá rộng.

---

# 11. Evidence depth rules

## 11.1. Evidence levels
Routing nên phân biệt nhẹ giữa hai mức:

- `wiki_only`
- `source_checked`

## 11.2. `wiki_only`
AI đã dùng:
- Knowledge Hub objects
- curated notes
- aliases
- expansion links
- source anchors

Nhưng **chưa grep/đọc source artifact raw**.

## 11.3. `source_checked`
AI đã đi thêm vào raw/source artifacts như:
- requirement docs gốc
- design docs gốc
- source code
- schema
- interface spec
- raw files/artifacts

## 11.4. Required warning at wiki-only level
Nếu AI mới chỉ dừng ở wiki layer,
AI phải warning rõ khi kết quả có thể bị thiếu cho deep analysis tasks.

### Example wording
> Hiện tôi mới tìm và phân tích ở mức Wiki/Knowledge Hub. Tôi chưa grep/đọc trực tiếp source artifact gốc, nên kết luận hiện tại vẫn là ở mức curated knowledge. Nếu cần phân tích sâu hơn hoặc xác nhận chi tiết, nên đọc tiếp source artifact.

## 11.5. Deep-analysis-sensitive tasks
Rule warning này đặc biệt quan trọng cho:
- review design
- review testcase
- coding
- code review
- bug investigation
- dependency analysis
- migration analysis
- source comparison

---

# 12. Deep research rules beyond wiki

## 12.1. Wiki-first remains the default
Ngay cả khi task cần sâu hơn,
AI vẫn phải:
- search wiki trước
- xác định gap trước
- không nhảy vào raw full grep ngay

## 12.2. No full raw grep by default
AI không nên grep full source/code/docbase mặc định chỉ để “chắc ăn”.

## 12.3. Folder-scoped deep research
Nếu cần deep research ngoài wiki,
AI nên đề xuất scope dưới dạng:
- folder
- nhóm folder
- source zone

rồi để BrSE chọn trước.

## 12.4. AI should propose scoped candidates
AI không nên hỏi quá mơ hồ:
> Bạn muốn tôi tìm ở đâu?

AI nên gợi ý có định hướng, ví dụ:
- folder design
- folder testcase
- folder backend
- folder api
- folder migration
- nhóm folder liên quan tới Function A

## 12.5. Example wording
> Hiện tôi mới phân tích ở mức Wiki/Knowledge Hub, chưa grep trực tiếp source artifact gốc. Nếu cần phân tích sâu hơn để tránh thiếu thông tin, ta nên đi tiếp vào source raw. Để giữ nguyên tắc wiki first và tránh grep quá rộng, bạn hãy chọn scope trước. Tôi đang thấy phù hợp nhất là một trong các nhóm sau: `{folder/group A}`, `{folder/group B}`, `{folder/group C}`.

---

# 13. HUMAN checkpoints in routing

AI nên kéo HUMAN vào routing ở các case sau:

## 13.1. Object resolution ambiguity
Ví dụ:
- “0001” map ra nhiều function
- “BD” có thể map nhiều concept trong context lạ

## 13.2. Scope ambiguity
Ví dụ:
- search project-first hay common-first
- có được mở sang local/private notes không

## 13.3. Lens ambiguity
Ví dụ:
- task này là review hay clarify?
- AI muốn runtime-define lens mới

## 13.4. Expansion ambiguity
Ví dụ:
- có nên mở sang dependency ngoài function hiện tại không
- có nên đưa DB/interface vào scope hiện tại không

## 13.5. Deep research boundary
Ví dụ:
- cần ra khỏi wiki layer để grep raw source
- cần chọn folder / group folder trước

---

# 14. Routing output contract

Routing output không nên là artifact nặng riêng.
Nó nên là một **sub-layer của discovery/selection output**.

Routing summary nên có tối thiểu:

## 14.1. `resolved_task_lens`
Lens hiện tại AI đang dùng.

## 14.2. `resolved_domain`
Domain hiện tại.

## 14.3. `resolved_scope_precedence`
Thứ tự scope mà AI đang dùng.

## 14.4. `resolved_target_objects`
Objects/concepts AI đã resolve được.

## 14.5. `retrieval_focus_summary`
AI đang ưu tiên tìm loại knowledge nào.

## 14.6. `expansion_plan_summary`
Từ mảnh đầu tiên, AI định đi theo nhánh nào tiếp.

## 14.7. `routing_readiness`
Đã đủ để đi sang:
- use case selection
- template selection
- Working AIP generation
- execution support

## 14.8. `evidence_level`
- `wiki_only`
- `source_checked`

## 14.9. `evidence_depth_summary`
Mô tả ngắn current evidence depth.

---

# 15. Quality rules

## Rule 1
Routing phải bắt đầu từ wiki/Knowledge Hub trước khi đi sâu vào raw/source.

## Rule 2
Object/concept resolution nên xảy ra sớm, trước expansion sâu.

## Rule 3
Expansion phải do task lens định hướng, không mở rộng ngẫu nhiên.

## Rule 4
Scope precedence phải explicit, không nên ngầm đổi mode.

## Rule 5
Stop condition chính là: enough for the next meaningful decision.

## Rule 6
Nếu kết quả hiện chỉ ở wiki layer, AI phải nói rõ điều đó.

## Rule 7
Deep research ngoài wiki không nên bắt đầu bằng full raw grep mặc định.

## Rule 8
Nếu cần đi sâu hơn ngoài wiki, AI nên đề xuất folder/group-folder scope để BrSE chọn trước.

---

# 16. Proposed merged content summary

The Knowledge Hub design should be updated to reflect the following for Knowledge Routing:

1. Define routing as a task-lens-aware mechanism for finding, filtering, expanding, and stopping in Knowledge Hub.
2. Route through five logical layers:
   - Task Lens
   - Domain
   - Scope precedence
   - Object/concept resolution
   - Expansion
3. Support multiple scope precedence modes:
   - project-first
   - common-first
   - local-first
4. Resolve objects/concepts early before deep expansion.
5. Make expansion lens-aware rather than purely relation-exhaustive.
6. Use `sufficient-for-next-decision` as the main routing stop condition.
7. Distinguish between `wiki_only` and `source_checked` evidence levels.
8. Require AI to warn clearly when results are still only at the wiki/curated layer.
9. Preserve wiki-first by default and avoid full raw grep by default.
10. If deeper research beyond wiki is needed, require scope selection by folder/group-folder before proceeding.

---

# 17. Delta status

This canonical spec is considered:
- mature enough for routing-spec-level review
- suitable as the baseline Knowledge Routing contract for Knowledge Hub upgrade work
- still open to later extension in areas such as:
  - deeper integration with retrieval engines
  - richer evidence-depth handling
  - stronger folder-zone/source-zone abstractions

---

# Knowledge-runtime sprint addendum — runtime access flow

## Default runtime access order

Knowledge routing should now be read together with the following minimal runtime access order:

1. current task / current step
2. current context / notebook / Workspace state
3. Task Lens
4. Wiki Meta / Index
5. curated Knowledge Hub object
6. raw/source fallback when required

This order is **Wiki-first, not Wiki-only**.

## Raw/source fallback triggers

AI may go to raw/source when at least one of the following is true:

- detail is missing for the current step
- exact wording / fact / number must be verified
- curated/wiki objects conflict
- source-of-truth evidence is required
- the current task genuinely requires raw inspection

## Stop rule

AI should stop at the highest sufficient level.

If current context, Wiki Meta / Index, or a curated knowledge object is sufficient for the next decision or next execution step, AI should not go deeper only because more information is available.

## Tool support rule

Tools/scripts may support search, lookup, filtering, traversal, and traceability.

AI keeps responsibility for:
- task understanding
- route strategy
- synthesis
- deciding whether the retrieved context is sufficient

---

# Source Understanding Artifact routing addendum

Source Understanding Artifact is a valid runtime target when the task needs reusable understanding of a source unit.

Routing should prefer:
- existing current context if sufficient
- Wiki Meta / Index to identify candidate artifacts
- Source Understanding Artifact for source-derived understanding
- raw/source when verification, exactness, conflict, or freshness check is required

Source Understanding Artifact should reduce unnecessary raw/source reopening without weakening source-grounding.

---

# Task Lens canonical addendum

## Definition

Task Lens is an optional runtime viewpoint for task → knowledge routing.

Task Lens helps AI decide what knowledge to look for, how to use Wiki Meta / Index, when to read Source Understanding Artifact, and when to verify raw/source.

## Core rules

- Intent first, lens second.
- Explicit Task Lens is optional in MVP.
- No-Lens / AI-decides-search-scope is allowed when explicit lens may reduce quality.
- HUMAN may adjust runtime lens after AI proposes it.
- AI may expand or adjust lens when the current lens is too narrow.
- Task Lens must not become a hard scope limiter.

## Minimal routing flow

```text
Task understanding
  ↓
Intent clarification if needed
  ↓
Optional Task Lens proposal
  ↓
HUMAN adjustment if desired
  ↓
Task Lens OR No-Lens
  ↓
Knowledge routing
  ↓
Wiki Meta / Index / Knowledge Hub / Source Understanding Artifact
  ↓
raw/source when needed
```

---

# Controlled Knowledge Promotion routing addendum

Knowledge routing may produce Knowledge Promotion candidates.

Examples:
- useful source routing pattern
- custom/runtime Task Lens
- No-Lens decision pattern
- repeated source verification lesson
- missed knowledge expansion finding

Routing findings should not be added to Knowledge Hub automatically.

Use this triage:
```text
Notebook can store any.
Candidate can review potential value.
Knowledge Hub requires clear Knowledge Value.
```

If a routing finding has value for future AI retrieval/routing/reasoning, create a candidate or use `knowledge-hub-add-update` assessment.

---

# v0.9.8 Wiki Meta / Index routing addendum

For source/artifact lookup, AI should use:

```text
current context / Task Lens
  ↓
lookup_wiki_source.py or Wiki Source Index
  ↓
meta_locator
  ↓
Wiki Source Meta
  ↓
artifact_locator when source detail/evidence is needed
```

Task Lens may shape search terms and source priorities, but it should not over-narrow search.

If converted source representation is insufficient, AI should report `source_representation_quality_issue` instead of guessing from original non-text raw files.

---

# v0.9.9 Working AIP Connection routing addendum

Wiki Meta / Index lookup results can feed Working AIP, but they do not replace it.

Runtime routing should flow:

```text
task intent / Task Lens
  ↓
Wiki Meta / Index / Knowledge Hub lookup
  ↓
candidate source/context
  ↓
selected and role-defined source references
  ↓
Working AIP
  ↓
execution readiness
```

A lookup result must be selected and role-defined before execution.

Task Lens shapes search and reasoning but does not replace Working AIP scope, expected output, steps, or done criteria.

---

# v0.9.11 Minimal Runtime Testing addendum

Knowledge routing runtime checks:

```text
Wiki Meta / Index routes.
Source artifact verifies.
```

Check:
- task intent clear before source search
- Task Lens does not over-narrow
- Wiki Meta / Index used for routing when applicable
- source artifact opened when exact evidence/detail is needed
- source_representation_quality_issue recorded when source representation is insufficient

Anti-pattern:

```text
Wiki Meta summary should not be treated as final evidence for high-impact claims.
```

---

# v0.9.13 Wiki Tooling Alignment addendum

`aiws-wiki lookup` is a routing tool.

```text
aiws-wiki lookup helps AI find candidate source/meta routes.
It does not prove source evidence.
```

When exact evidence is needed:
- open AIWS-readable source artifact
- check source representation quality
- state limitation if representation is partial/unknown
- do not claim verification based on lookup/meta alone

---

# CR-G5 Addendum — Wiki-First Evidence Policy (2026-05-25)

Source: AIP-EXEC-015 STEP-01, CR-G5 from AIWS-Wiki-CR-Proposal-2026-05-25.md §5.

## Explicit evidence level policy

### Rule E-1: partial → wiki_only

Khi `source_representation_status: partial` trong artifact meta:
> **AI MUST report evidence level as `wiki_only`.**
> AI KHÔNG được claim `source_checked` chỉ dựa trên converted/partial representation.

Lý do: partial status nghĩa là converted markdown không cover đầy đủ nội dung source gốc.

### Rule E-2: Đạt `source_checked` cần

1. Mở source artifact AIWS-readable (full, không phải partial)
2. Đọc section/content liên quan trực tiếp
3. Confirm scope với user nếu representation có conversion_limitations

### Rule E-3: Trình bày evidence khi report

Khi AI cite knowledge từ Wiki, phải explicit:
- `[wiki_only]` — chỉ dựa trên meta/index/summary
- `[source_checked: partial]` — đọc converted nhưng representation là partial
- `[source_checked: complete]` — đọc source representation đầy đủ

**Cross-reference:** `WIKI_META_INDEX_SPEC.md §CR-D7 Addendum`, `ARTIFACT_UNDERSTANDING_SPEC.md` (confirmed/inferred separation)
