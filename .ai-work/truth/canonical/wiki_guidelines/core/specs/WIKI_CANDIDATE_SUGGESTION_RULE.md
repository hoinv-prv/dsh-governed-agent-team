# WIKI_CANDIDATE_SUGGESTION_RULE_v0_1

## 1. Purpose
Tài liệu này định nghĩa rule tối thiểu cho việc AI **gợi ý Wiki candidate** trong sprint hiện tại.

Mục tiêu:
- làm rõ điều kiện để một information có thể được suggest như một Wiki candidate
- tách rõ giữa:
  - `wiki-candidate-eligible`
  - `wiki-canonical-eligible`
- giúp AI biết khi nào nên:
  - suggest candidate
  - skip
  - giữ ở notebook/backlog
- giảm nguy cơ đẩy các idea chưa đủ chín vào canonical Wiki

---

## 2. Why this rule is needed
Không phải mọi information hữu ích đều nên:
- thành canonical Wiki ngay
- hoặc thậm chí thành candidate mạnh ngay

Nếu không có rule rõ, AI có thể:
- suggest quá nhiều thứ không đủ chín
- suggest những insight quá mơ hồ
- làm Wiki bị phình với low-value items
- trộn candidate với canonical-ready change

Do đó cần tách:
- **candidate eligibility**
- **canonical eligibility**

---

## 3. Foundational distinctions

### 3.1. Candidate is not canonical
Một information có thể đáng được gợi ý như candidate
nhưng vẫn chưa đủ chín để update canonical Wiki.

### 3.2. Suggestion is lighter than canonical promotion
AI có thể suggest candidate với bar thấp hơn canonical update,
nhưng vẫn cần threshold tối thiểu.

### 3.3. Notebook/backlog remain valid holding areas
Nếu thông tin:
- chưa đủ rõ
- chưa đủ grounded
- chưa đủ reusable
thì notebook hoặc backlog vẫn là nơi phù hợp hơn candidate/canonical Wiki.

---

## 4. Two eligibility levels

## 4.1. `wiki-candidate-eligible`
Một information có thể được AI suggest như candidate khi:
1. có giá trị dùng lại cho dự án
2. có source basis / grounding đủ rõ
3. có target placement tương đối xác định trong Wiki
4. không bị project profile loại trừ

## 4.2. `wiki-canonical-eligible`
Một candidate đủ chín để đi tiếp sang canonical update khi:
1. đã đủ rõ target update
2. đã đủ rõ source basis
3. đã đủ rõ change direction
4. không có conflict chưa resolve quá lớn
5. đi qua CR + wiki manager flow

### Rule
Every canonical-eligible item should also be candidate-eligible,
but not every candidate-eligible item is canonical-eligible.

---

## 5. Candidate classes in scope

### 5.1. Artifact publication candidate
Ví dụ:
- Basic Design mới tạo
- Weekly Report mới tạo
- Requirement Definition mới tạo
- artifact hiện có nhưng đáng được publish vào Wiki

### 5.2. Metadata / linkage candidate
Ví dụ:
- alias mapping
- raw requirement ↔ Q&A ↔ requirement definition linkage
- BD ↔ DD ↔ testcase linkage
- reflected_to / superseded_by update
- missing object linkage found during task execution

### 5.3. Curated project knowledge candidate
Ví dụ:
- clarified reusable project rule
- reusable task hint
- meaningful synthesis of several grounded project artifacts
- curated note that helps later BrSE tasks

---

## 6. Candidate eligibility rule

### 6.1. Reusability requirement
The information should have potential reuse value for future project work.

Examples:
- future clarify requirement tasks
- future design creation/review
- future testcase review
- future traceability / investigation work

If it is only useful for one tiny one-off local context, candidate strength is low.

### 6.2. Grounding requirement
The information should be traceable to one or more of:
- project artifacts
- AIP task outputs
- structured session outputs
- existing wiki objects/meta
- notebook entries with clear grounding

### 6.3. Placement requirement
AI should be able to tell, at least roughly:
- what wiki object/section/layer this belongs to
- what candidate class it is

If placement is too unclear, prefer:
- notebook
- parked candidate
- backlog

### 6.4. Maturity requirement
The information should not be only a weak, immature, or highly speculative hypothesis.

If it is:
- too vague
- too context-bound
- too weakly grounded
- too immature

then it should usually stay outside strong candidate promotion.

### 6.5. Project-profile requirement
If project profile explicitly says this class should not be curated in Wiki,
AI should skip suggestion.

---

## 7. Canonical eligibility rule

### 7.1. Clear target
AI/BrSE can identify where the update should land.

### 7.2. Clear basis
The source basis is clear enough for CR.

### 7.3. Clear direction
The expected update direction is clear enough.

### 7.4. Governance readiness
The item is ready to enter:
- CR
- wiki manager review/request
- canonical update flow

### 7.5. Conflict caution
If the item would likely conflict with existing canonical knowledge
and that conflict is not yet resolved,
do not treat it as canonical-ready.

---

## 8. Candidate suggestion sources

### 8.1. AIP-driven sources
Strongest formal source in this sprint:
- artifact creation outputs
- review outputs
- structured findings
- artifact understanding outputs
- explicit linkage/meta discoveries

### 8.2. Non-AIP sources
AI may also suggest candidate from:
- ad hoc Q&A
- ad hoc brainstorming
- ad hoc research
- short review or discussion interactions

### 8.3. Boundary
Outside AIP:
- suggestion is encouraged
- but the process is not formalized in equal detail in this sprint

---

## 9. Artifact-specific candidate rule

### 9.1. Artifact publication candidate eligibility
An artifact may be candidate-eligible when:
- it has reuse value
- it is identifiable as an artifact class
- project profile does not exclude it
- AI can place it reasonably in Wiki

### 9.2. Deliverable-driven strength
If an artifact is:
- deliverable
- wiki-eligible by project profile

then candidate strength is high, and AIP-driven flow should usually suggest it.

### 9.3. Working-only artifact
If an artifact is:
- working-only
- temporary
- explicitly non-wiki-eligible

AI should usually skip suggestion.

---

## 10. Metadata / linkage candidate rule

### 10.1. Candidate when useful to future tasks
Metadata or relation updates are candidate-eligible when they would likely help:
- routing
- traceability
- review efficiency
- requirement evolution understanding
- clarification reuse

### 10.2. Typical examples
- alias discovery
- relation discovery
- reflected_to update
- superseded_by update
- missing canonical object linkage

### 10.3. Rule
If a relation is too uncertain, do not promote strongly.
Prefer:
- unresolved marker
- weaker candidate
- notebook/backlog note

---

## 11. Curated project knowledge candidate rule

### 11.1. Candidate when meaningful and reusable
Curated knowledge can be candidate-eligible when:
- it adds reusable project value
- it is not just a casual thought
- it has grounded basis
- it is not excluded by project profile

### 11.2. Examples
- clarified project rule from multiple grounded artifacts
- reusable review note
- reusable interpretation of reflected Q&A pattern
- stable explanation of artifact relation that repeatedly helps work

### 11.3. Rule
If it is mostly:
- personal note
- one-off observation
- weak synthesis
- highly speculative

prefer notebook/backlog over Wiki candidate.

---

## 12. Skip rule
AI should skip candidate suggestion when one or more of the following is true:
- project profile excludes this class
- information is too weakly grounded
- placement is too unclear
- reuse value is too low
- it is mainly a temporary/local/private working note
- it is better kept as notebook/backlog material
- it is likely to create noise rather than reusable value

---

## 13. Notebook / backlog preference rule
When in doubt between:
- low-confidence candidate
- notebook/backlog

prefer notebook/backlog unless there is clear project reuse value and reasonable grounding.

This rule keeps candidate suggestion useful without over-promoting noise.

---

## 14. Relationship with CR and governance

### 14.1. Candidate stage
This rule governs suggestion of candidate.

### 14.2. CR stage
If candidate is considered mature enough, it may be turned into CR.

### 14.3. Governance stage
Canonical update still depends on:
- CR
- wiki manager review/request
- AI applying the approved update

### Anti-confusion note
Candidate suggestion does not bypass governance.

---

## 15. Minimal evaluation questions for AI
Before suggesting a candidate, AI should roughly check:
1. Is this reusable for future project work?
2. Is it grounded enough?
3. Can I place it in Wiki with reasonable clarity?
4. Is it excluded by project profile?
5. Is it better as notebook/backlog instead?

If the answers are weak, candidate suggestion should be conservative.

---

## 16. Minimal examples

### 16.1. Strong artifact publication candidate
A new Requirement Definition document is created under AIP.
It is a deliverable and project profile says it is wiki-eligible.
→ strong candidate suggestion

### 16.2. Strong linkage candidate
A review task repeatedly needs manual tracing from DD to testcase.
AI identifies a stable DD ↔ testcase linkage with clear source basis.
→ strong metadata/linkage candidate

### 16.3. Weak speculative insight
A brainstorming session produces a vague idea that may or may not matter later.
No clear grounding or target placement exists.
→ keep as notebook/backlog, not a strong Wiki candidate

### 16.4. Reflected Q&A clarification note
A Q&A-derived clarification is already reflected into requirement definition.
AI may still suggest a metadata/reflection-state update,
but not necessarily a new curated knowledge item if it adds no reuse value.

---

## 17. Out of scope for this sprint
- candidate ranking engine
- candidate scoring formula
- automatic prioritization queue
- advanced de-duplication
- automatic candidate-to-CR conversion engine

---

## 18. Completion criteria for BL-09
BL-09 is considered done when:
- `wiki-candidate-eligible` is clearly defined
- `wiki-canonical-eligible` is clearly defined
- candidate classes are clearly defined
- skip rule is clearly defined
- notebook/backlog preference rule is clearly defined
- relation to CR and governance is clearly captured
