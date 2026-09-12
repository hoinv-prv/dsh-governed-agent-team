# WIKI_CREATION_PROMPT_TEMPLATE_MVP
Version: 0.2  
Status: Draft baseline  
Scope: MVP only

---

# 1. Purpose

This file provides copy-paste prompt templates to ask an LLM to:
- create new wiki candidates
- create wiki update drafts
- classify wiki entry type / knowledge class
- convert source materials into wiki-ready draft

This version is aligned with **Wiki v1.0 freeze**, including source-side flow:
- `Wiki Source Index`
- `Wiki Source Meta`
- `Wiki Source Artifact`
- `Source Interpretation Profile`

---

# 2. General prompt — New Wiki Candidate

```text
Hãy tạo một wiki candidate theo AI Work System MVP.

Target:
- entry_type: <domain|function|module|data|pattern|reference>
- title: <title>
- output_type: new wiki candidate
- desired_knowledge_class: <curated|reference>

Trước khi viết, hãy đọc theo thứ tự:
1. .ai-work/truth/SOP_MASTER.md
2. .ai-work/truth/AI_WORK_CONTRACT.md
3. .ai-work/procedural/wiki_authoring_guideline.md
4. nếu có, hãy đọc Wiki Source Index để tìm source phù hợp
6. nếu có, hãy đọc Wiki Source Meta tương ứng để xác nhận relevance
7. nếu source type cần guidance, hãy đọc Source Interpretation Profile
8. chỉ khi cần mới mở Wiki Source Artifact thật
9. đọc các wiki liên quan nếu có

Yêu cầu:
- không viết như source_of_truth
- nếu còn điểm chưa chắc, hãy note rõ
- dùng YAML metadata ở đầu
- luôn có các section:
  Purpose
  Scope
  Canonical References
  Recommended Next Reads
- thêm các section phù hợp với entry_type
- ưu tiên useful navigation hints
- không assume beyond evidence
- nếu có source-side lookup data, hãy dùng chúng trước khi đọc raw source thật

Output format:
1. Classification summary:
   - entry_type
   - knowledge_class
   - use_rule
   - source metas used
   - source profiles used
   - key evidence basis
   - caution points if any
2. Full wiki candidate markdown
```

---

# 3. Prompt — Wiki Update Draft

```text
Hãy tạo một wiki update draft theo AI Work System MVP.

Target:
- entry_type: <domain|function|module|data|pattern|reference>
- title: <title>
- output_type: update draft
- desired_knowledge_class: <curated|reference>

Inputs:
- existing wiki entry: <path>
- canonical refs: <paths>
- source-side materials:
  - Wiki Source Index entries: <if available>
  - Wiki Source Meta: <if available>
  - Wiki Source Artifact(s): <if needed>
  - Source Interpretation Profile(s): <if available>
- findings/candidates: <paths if any>

Trước khi viết, hãy đọc theo thứ tự:
1. .ai-work/truth/SOP_MASTER.md
2. .ai-work/truth/AI_WORK_CONTRACT.md
3. .ai-work/procedural/wiki_authoring_guideline.md
4. existing target wiki entry
6. source index/meta if available
7. source profiles if needed
8. actual source artifacts only when needed
9. findings/candidates if relevant

Yêu cầu:
- chỉ đề xuất phần cần sửa/bổ sung
- nêu rõ source refs dùng để justify update
- nếu có điểm chưa chắc, đừng flatten uncertainty
- không apply official update, chỉ tạo draft update
- giữ structure nhất quán với MVP

Output format:
1. Target entry summary
2. What should change
3. Why
4. Source refs used
5. Source metas used
6. Source profiles used
7. Updated section drafts
```

---

# 4. Prompt — Function Wiki Candidate

```text
Hãy tạo một wiki candidate cho một function theo AI Work System MVP.

Target:
- entry_type: function
- title: <function title>
- output_type: new wiki candidate
- desired_knowledge_class: curated

Trước khi viết, hãy đọc:
1. truth/SOP_MASTER.md
2. truth/AI_WORK_CONTRACT.md
3. procedural/wiki_authoring_guideline.md
4. Wiki Source Index entries liên quan nếu có
6. Wiki Source Meta tương ứng
7. Source Interpretation Profile nếu source type cần guidance
8. source artifacts chỉ khi cần
9. wiki/function/ liên quan nếu có

Yêu cầu:
- metadata YAML ở đầu
- luôn có:
  Purpose
  Scope
  Canonical References
  Recommended Next Reads
- nên thêm:
  Key Situations / Events
  Related Functions
  Upstream / Downstream Hints
  Review Hints
- nếu dependency chỉ là likely hint, đừng viết như fact chắc chắn
- preserve useful exact identifiers/terms when relevant

Output:
1. Classification summary
2. Full function wiki candidate
```

---

# 5. Prompt — Module / Component Wiki Candidate

```text
Hãy tạo một wiki candidate cho một module/component theo AI Work System MVP.

Target:
- entry_type: module
- title: <module title>
- output_type: new wiki candidate
- desired_knowledge_class: curated

Trước khi viết, hãy đọc:
1. truth/SOP_MASTER.md
2. truth/AI_WORK_CONTRACT.md
3. procedural/wiki_authoring_guideline.md
4. source index/meta liên quan nếu có
6. source interpretation profile nếu có
7. module design docs / code map / source artifacts khi cần
8. wiki/module/ và wiki/function/ liên quan

Yêu cầu:
- metadata YAML ở đầu
- luôn có:
  Purpose
  Scope
  Canonical References
  Recommended Next Reads
- nên thêm:
  Main Responsibilities
  Key Source Areas
  Dependency Hints
- đừng over-generalize beyond evidence

Output:
1. Classification summary
2. Full module wiki candidate
```

---

# 6. Prompt — Data / Table Wiki Candidate

```text
Hãy tạo một wiki candidate cho một data/table entry theo AI Work System MVP.

Target:
- entry_type: data
- title: <table or data object title>
- output_type: new wiki candidate
- desired_knowledge_class: curated

Trước khi viết, hãy đọc:
1. truth/SOP_MASTER.md
2. truth/AI_WORK_CONTRACT.md
3. procedural/wiki_authoring_guideline.md
4. source index/meta liên quan nếu có
6. source interpretation profile nếu có
7. schema / source artifacts khi cần
8. wiki/data/ liên quan nếu có

Yêu cầu:
- metadata YAML ở đầu
- luôn có:
  Purpose
  Scope
  Canonical References
  Recommended Next Reads
- nên thêm:
  Business Meaning
  Main Writers / Readers
  Data Risks
- nếu writer/reader chưa chắc, note rõ là to-verify
- preserve exact identifiers useful for grep/use later

Output:
1. Classification summary
2. Full data wiki candidate
```

---

# 7. Prompt — Domain Wiki Candidate

```text
Hãy tạo một wiki candidate cho một domain entry theo AI Work System MVP.

Target:
- entry_type: domain
- title: <domain title>
- output_type: new wiki candidate
- desired_knowledge_class: curated

Trước khi viết, hãy đọc:
1. truth/SOP_MASTER.md
2. truth/AI_WORK_CONTRACT.md
3. procedural/wiki_authoring_guideline.md
4. source index/meta liên quan nếu có
6. source interpretation profile nếu có
7. domain overview docs / source artifacts khi cần
8. wiki/domain/ liên quan nếu có

Yêu cầu:
- metadata YAML ở đầu
- luôn có:
  Purpose
  Scope
  Canonical References
  Recommended Next Reads
- nên thêm:
  Key Concepts
  Main Areas
  Common Questions
- đừng viết domain summary như fully verified if evidence is partial

Output:
1. Classification summary
2. Full domain wiki candidate
```

---

# 8. Prompt — Pattern / Guidance Entry

```text
Hãy tạo một pattern/guidance wiki entry theo AI Work System MVP.

Target:
- entry_type: pattern
- title: <pattern title>
- output_type: new wiki candidate
- desired_knowledge_class: reference

Trước khi viết, hãy đọc:
1. truth/SOP_MASTER.md
2. truth/AI_WORK_CONTRACT.md
3. procedural/wiki_authoring_guideline.md
4. source index/meta nếu có
6. profiles / playbooks / findings / capture candidates / source artifacts khi cần
7. wiki/pattern/ và wiki/reference/ liên quan nếu có

Yêu cầu:
- metadata YAML ở đầu
- knowledge_class nên là reference trừ khi có lý do mạnh để dùng curated
- luôn có:
  Purpose
  Scope
  Canonical References
  Recommended Next Reads
- nên thêm:
  When to Use
  How to Apply
  Pitfalls / Cautions
- đừng viết guidance như authoritative rule nếu chưa phải truth

Output:
1. Classification summary
2. Full pattern/reference wiki candidate
```

---

# 9. Prompt — Convert Source Materials to Wiki-Ready Draft

```text
Hãy đọc source materials tôi cung cấp và chuyển chúng thành một wiki-ready draft theo AI Work System MVP.

Target:
- entry_type: <domain|function|module|data|pattern|reference>
- title: <title>
- output_type: wiki-ready draft
- desired_knowledge_class: <curated|reference>

Yêu cầu:
- trước hết hãy xác định entry_type và knowledge_class phù hợp
- nếu có source-side support, hãy dùng:
  Wiki Source Index → Wiki Source Meta → Source Interpretation Profile → Source Artifact
- nếu không đủ evidence để viết curated mạnh, hãy hạ xuống reference
- không flatten uncertainty
- luôn có metadata YAML ở đầu
- luôn có:
  Purpose
  Scope
  Canonical References
  Recommended Next Reads
- không assume beyond evidence

Output:
1. Classification summary
2. Wiki-ready markdown draft
3. Source metas used
4. Source profiles used
5. Unresolved points
```

---

# 10. Prompt — Conservative Update When Evidence Is Weak

```text
Hãy tạo một conservative wiki update draft theo AI Work System MVP.

Context:
- existing wiki entry: <path>
- new evidence/source-side materials:
  - source index entries: <if any>
  - source metas: <if any>
  - source artifacts: <if needed>
  - source profiles: <if any>

Yêu cầu:
- chỉ cập nhật những phần có basis rõ
- phần nào chưa chắc phải ghi visible caution
- nếu evidence chưa đủ để sửa phần curated, hãy đề xuất update ở mức reference/guidance note thay vì viết như fact chắc chắn
- không apply official update, chỉ tạo draft

Output:
1. What is safe to update now
2. What still needs verification
3. Draft changed sections
```

---

# 11. Prompt — Classification Only

```text
Trước khi tạo wiki, hãy chỉ làm bước classification theo AI Work System MVP.

Inputs:
- target title: <title>
- source materials: <paths>
- source index/meta/profile paths nếu có

Hãy trả lời:
1. entry_type phù hợp nhất là gì?
2. knowledge_class phù hợp nhất là gì?
3. use_rule nên là gì?
4. source index/meta có đủ để proceed chưa?
5. source profiles nào nên đọc trước khi viết thật?
6. source artifact nào thật sự cần mở?
7. risk lớn nhất nếu viết ngay lúc này là gì?
```

---

# 12. Prompt — Self-check Before Finalizing

```text
Trước khi finalize wiki draft, hãy tự check theo AI Work System MVP:

- Đã đọc Truth / procedural docs cần thiết chưa?
- Đã dùng source index/meta trước khi mở source artifact chưa, nếu available?
- Đã chọn đúng entry_type chưa?
- Đã chọn đúng knowledge_class chưa?
- Đã có Purpose / Scope / Canonical References / Recommended Next Reads chưa?
- Có đang viết như source_of_truth dù evidence chưa đủ không?
- Có flatten uncertainty không?
- Canonical References có verify được không?
- Recommended Next Reads có thực sự hữu ích không?

Hãy trả lời:
1. pass/fail từng mục
2. điểm nào cần sửa
3. source metas used
4. source profiles used
5. bản draft đã chỉnh sau self-check
```

---

# 13. Practical use

Use these templates by filling:
- entry_type
- title
- output_type
- desired_knowledge_class
- source files / source index/meta/profile paths
- existing wiki paths if applicable

If unsure:
- between `curated` and `reference` → choose `reference`
- between `curated` and `source_of_truth` → choose `curated`
