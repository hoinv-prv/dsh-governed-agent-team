# WIKI_FIRST_RUNTIME_GUIDANCE_v0_1

## 1. Purpose
Tài liệu này định nghĩa **Wiki-first Runtime Guidance** cho AI Work System trong sprint hiện tại.

Mục tiêu:
- giúp AI ưu tiên dùng tri thức đã được chuẩn hóa trong Wiki trước
- giảm việc phải đọc lại raw/source artifacts không cần thiết
- vẫn giữ an toàn khi Wiki chưa đủ hoặc chưa chắc
- làm rõ boundary giữa:
  - Task Lens
  - Wiki Meta / Index
  - source/raw artifacts
  - AIP execution
  - governance/update flow

Trong sprint này, guidance được define ở mức **minimal but usable**.

---

## 2. Why this guidance is needed
Nếu không có runtime guidance rõ, AI dễ:
- đọc lại quá nhiều source artifacts
- bỏ qua tri thức đã được curate trong Wiki
- trộn lẫn notebook findings, wiki meta, raw source
- hoặc ngược lại, tin Wiki quá mức khi Wiki chưa đủ

Do đó cần chốt:
- ưu tiên runtime layer nào trước
- khi nào escalate xuống layer sâu hơn
- khi nào chỉ nên warning thay vì giả định đủ knowledge

---

## 3. Core runtime principle
Runtime nên **Wiki-first**, nhưng không phải **Wiki-only**.

Điều đó nghĩa là:
- AI nên ưu tiên dùng current context + notebook + Wiki Meta / Index trước
- nhưng nếu các layer này chưa đủ, AI vẫn có thể:
  - mở linked artifacts
  - đọc source/raw deeper
  - hoặc mark unresolved / limited confidence

---

## 4. Runtime layer order
Thứ tự khuyến nghị trong runtime:

### Layer 1 — Current work context
- current task context
- confirmed short-term session context
- active notebook findings nếu relevant

### Layer 2 — Wiki Meta / Index
- artifact meta
- object meta
- aliases
- link/traceability
- supplemental status/reflection markers
- lightweight sufficiency/reference hints

### Layer 3 — Linked artifacts / targeted artifact consultation
- artifacts đã được route vào scope bởi Task Lens / links / known relations
- specific supporting artifacts needed for confirmation

### Layer 4 — Source/raw deeper investigation
- raw artifact reading
- broader grep/search through source artifacts
- extra expansion when curated layers are insufficient

### Rule
Không nên nhảy thẳng xuống Layer 4 như default,
trừ khi task hoặc context cho thấy raw/source là bắt buộc ngay từ đầu.

---

## 5. Relationship with Task Lens
Task Lens vẫn là layer:
- task → knowledge routing
- deciding what kind of knowledge to seek
- where to start
- how to expand

Wiki-first Runtime Guidance không thay Task Lens.

### Boundary
- Task Lens quyết định **nên tìm knowledge nào**
- Runtime Guidance quyết định **nên consult layer nào trước trong lúc thực thi**

---

## 6. Relationship with AIP
AIP có thể chỉ ra:
- expected outputs
- checkpoints
- wiki dependency note
- if_wiki_is_insufficient_then
- add-to-wiki handoff expectations

Nhưng AIP không nên encode full retrieval order chi tiết cho mọi case.

### Boundary
- AIP = execution flow for task
- Runtime Guidance = general consultation priority during execution

---

## 7. What “Wiki-first” means operationally

### 7.1. Prefer normalized knowledge first
AI nên ưu tiên dùng:
- object/artifact meta
- explicit links
- status/reflection information
- reusable curated knowledge

trước khi mở lại whole source documents.

### 7.2. Re-open source only when needed
Source/raw nên được mở sâu hơn khi:
- meta không đủ chi tiết
- relation quan trọng chưa explicit
- unresolved marker đang chặn task
- confidence thấp
- user/task explicitly requires deeper confirmation

### 7.3. Warning instead of overclaim
Nếu Wiki hiện tại chỉ đủ một phần,
AI nên:
- nói rõ giới hạn
- continue conservatively nếu phù hợp
- hoặc escalate to artifact/source consultation

---

## 8. Default runtime behavior by task situation

### 8.1. Artifact understanding task
Trong task hiểu artifact mới, AI gần như chắc chắn sẽ cần Layer 3/4,
vì source artifact là grounding chính.

### 8.2. Reuse / lookup / review-support task
Trong các task như:
- tra relation
- review support
- weekly reporting support
- identify linked artifacts
AI nên bắt đầu mạnh ở Layer 1/2 trước.

### 8.3. Canonical update or CR-prep task
Trong các task liên quan update canonical layer,
AI nên dùng Layer 2 trước, rồi mở source/layer sâu hơn để confirm change basis khi cần.

### 8.4. Ambiguous / weak-meta case
Nếu meta yếu hoặc cũ,
AI nên:
- dùng meta như entry point
- nhưng sớm escalate nếu thấy insufficiency rõ

---

## 9. Insufficiency handling rule

### 9.1. Signals that Wiki may be insufficient
Ví dụ:
- unresolved markers on key relation
- missing artifact linkage
- reflection status unclear
- alias mapping weak
- required slot absent
- known format drift / outdated mapping pattern

### 9.2. Allowed reactions
AI có thể:
- consult linked artifact
- inspect source/raw section
- mark limited confidence
- generate candidate/meta improvement suggestion
- note that current result is based only on curated layer

### 9.3. Important rule
Insufficient Wiki không đồng nghĩa:
- task phải dừng ngay

nhưng cũng không được dẫn tới:
- giả vờ đủ knowledge coverage

---

## 10. Runtime output expectation
Khi runtime heavily relies on Wiki,
AI nên cố gắng làm rõ nếu cần:

- what was answered mainly from Wiki Meta / Index
- what required direct artifact reading
- what remains unresolved
- whether result is still only based on curated layer

Không phải task nào cũng cần nói ra đầy đủ,
nhưng rule này hữu ích cho high-stakes or review-heavy tasks.

---

## 11. Relationship with notebook
Notebook là working layer hữu ích cho:
- recent working findings
- hot pointers
- still-maturing synthesized notes

### Rule
Notebook có thể được ưu tiên trước Wiki trong current active task,
nhưng:
- notebook không thay canonical Wiki
- notebook không nên được coi là source of truth ngang với curated Wiki hoặc source artifact

### Practical use
- notebook = current-working acceleration layer
- wiki meta = reusable normalized project knowledge layer

---

## 12. Relationship with governance and update
Runtime Guidance không nói:
- cái gì được update canonical
- ai được approve
- CR structure là gì

Tuy nhiên, nếu runtime repeatedly hits Wiki insufficiency,
AI có thể:
- surface candidate
- suggest CR-prep path
- or suggest meta improvement need

### Boundary
- runtime guidance may surface improvement needs
- governance decides canonical change

---

## 13. Suggested runtime decision pattern

### Pattern A — enough from Wiki
1. use current context/notebook
2. consult wiki meta/index
3. answer or continue task
4. note unresolved only if needed

### Pattern B — partly enough
1. use current context/notebook
2. consult wiki meta/index
3. identify missing point
4. consult linked artifact
5. continue conservatively

### Pattern C — not enough
1. use wiki as entry point
2. detect insufficiency early
3. escalate to source/raw deeper investigation
4. keep confidence/limitations visible
5. optionally suggest meta improvement candidate

---

## 14. Minimal anti-confusion notes

### 14.1. Wiki-first ≠ Wiki-only
Wiki-first means preferred first, not exclusive only source.

### 14.2. Wiki-first ≠ never read source
Source/raw remains necessary for:
- artifact understanding
- low-confidence cases
- unresolved deep confirmation
- structure/template analysis

### 14.3. Wiki-first ≠ direct canonical trust in all cases
Curated layer can still be incomplete, stale, or unresolved.

### 14.4. Wiki-first ≠ governance shortcut
Even if runtime finds useful new knowledge, canonical update still follows candidate / CR / governance flow.

---

## 15. Common pitfalls
- always reopening raw files before checking Wiki
- trusting weak meta too much
- ignoring unresolved markers
- using notebook like canonical truth
- treating Task Lens and runtime layer order as the same thing
- assuming all tasks should stay at meta layer only

---

## 16. If missing then do
Nếu runtime feels weak because Wiki is not enough:
- use Wiki as entry point
- identify missing point clearly
- escalate to linked artifact or raw source
- keep unresolved/limited-confidence visible
- suggest candidate/meta improvement only when useful

---

## 17. Relationship with other sprint artifacts
Guidance này được thiết kế để nối:
- `TASK_LENS_AND_WIKI_KNOWLEDGE_PROFILE_BOUNDARY_NOTE_v0_1`
- `AIP_WIKI_INTEGRATION_SPEC_v0_1`
- `WIKI_META_INDEX_SPEC_v0_2`
- `WIKI_CANDIDATE_SUGGESTION_RULE_v0_1`
- `WIKI_MINIMAL_GOVERNANCE_RULE_v0_1`
- `GUIDELINE_INDEX_FLOW_NAVIGATOR_v0_1`
- `WIKI_SOURCE_DISAMBIGUATION_GUIDELINE_v0_1` — runtime rule khi multiple sources có overlapping terms

---

## 18. Completion criteria for BL-15
BL-15 is considered done when:
- Wiki-first principle is clearly defined
- runtime layer order is clearly defined
- insufficiency handling is clearly defined
- boundary with Task Lens and AIP is clearly defined
- relation with notebook and governance is clearly defined

---

## No-Match Escalation + PRE-FLIGHT GATE — 2026-05-27 Addendum

**Source:** Applied from wiki_improvement_request.md Nhóm 13+15 (validated in vti-ai-work-system-demo, 2026-05-26).

### No-match escalation (MANDATORY when lookup returns 0 results)

When `lookup_wiki_source.py` returns `(no matches)` (exit code 1), the AI **must not** conclude "not found" without completing this protocol:

1. **Retry semantic mode** (if first attempt was lexical):
   `py .ai-work/tooling/lookup_wiki_source.py --query <keyword> --mode semantic`

2. **Raw search:**
   Open `.ai-work/wiki/reference/document_search_guidelines.md` → "Raw search fallback" section → Glob/Grep in listed artifact dirs.

3. **If artifact dirs not documented:** Ask HUMAN for dir locations, then update `document_search_guidelines.md`.

4. **If found in raw:** Read artifact directly for this task; register later via `/aiws-wiki build-meta`.

5. **Only report "no relevant documents found"** if steps 1–4 all miss.

❌ **Never silently conclude "not found" after a single index miss.** The index is never 100% complete in an active project.

### PRE-FLIGHT GATE pattern (wiki-first in skills)

Skills that consume canonical artifacts (RD/BD/DD/spec) as input enforce a **PRE-FLIGHT GATE**: wiki lookup must run before any direct file open. This is baked into `aiws-aip/operations/create.md` and `aiws-aip/operations/run.md` as a dedicated HARD GATE section. Forbidden shortcuts:
- Glob/Grep for artifact files without wiki lookup first
- Inferring peer artifact paths from a path the user already provided ("anchor-path" pattern)
- Skipping lookup because "I already know where it is"
