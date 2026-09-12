# AIP_WIKI_INTEGRATION_SPEC_v0_1

## 1. Purpose
Tài liệu này định nghĩa cách **AIP** và **Wiki / Knowledge Hub** phối hợp với nhau trong sprint hiện tại.

Mục tiêu:
- để AIP không đứng tách rời khỏi Wiki
- để AI biết khi nào nên load/use Wiki knowledge trong flow theo AIP
- để AI biết khi nào nên gợi ý bổ sung output vào Wiki
- để add-to-wiki step được thực hiện có kiểm soát, phù hợp với project profile và governance rule

Trong sprint này, integration được define ở mức minimal nhưng usable.

---

## 2. Scope in this sprint
In-scope:
- AIP-driven flows as the main formal scope
- relation between AIP execution and Wiki consultation
- relation between AIP outputs and Wiki candidate / publication suggestion
- deliverable vs working artifact distinction
- wiki eligibility rule
- add-to-wiki suggestion step for artifact-creating AIPs
- project profile interaction
- CR / governance handoff point

Out-of-scope:
- dynamic orchestration engine
- fully automatic mode/lens/tool orchestration
- autonomous publish workflow without human control
- advanced runtime optimization logic

---

## 3. Foundational principles

### 3.1. AIP and Wiki are complementary
AIP guides execution of work.
Wiki / Knowledge Hub supports reusable project knowledge.

AIP should not ignore Wiki.
Wiki should not be treated as detached from AIP-driven work.

### 3.2. AIP-driven flows are the main formal integration scope in this sprint
This sprint describes explicit rules mainly for flows that run under AIP.

### 3.3. Task Lens remains the task → knowledge routing layer
Task Lens helps AI determine what knowledge to seek.
AIP-Wiki Integration should not replace Task Lens.

### 3.4. Runtime should mostly consult Wiki Meta / Index
During normal execution, AI should mostly rely on:
- Task Lens
- Wiki Meta / Index
- current context / notebook

Wiki Knowledge Profile is mainly a build/update/maintenance asset and should be consulted when needed, not treated as a default runtime artifact in every step.

### 3.5. Canonical Wiki update still goes through governance
Even when AIP suggests add/update to Wiki, canonical update is still controlled by:
- candidate
- CR
- wiki manager request
- AI applies update

---

## 4. What AIP-Wiki Integration should cover
AIP-Wiki Integration should tell AI/BrSE:

- when Wiki should be consulted during AIP execution
- what class of knowledge should be expected from Wiki
- what to do when Wiki is insufficient
- when AIP outputs should be turned into Wiki candidates
- when artifact-creating AIPs should suggest add-to-wiki
- when that suggestion becomes a required step
- when to skip the suggestion
- how project profile influences all this

---

## 5. AIP-driven runtime consultation

### 5.1. Default runtime knowledge flow
During AIP execution, AI should generally prefer:
1. current work context / notebook if relevant
2. Wiki Meta / Index
3. linked artifacts if needed
4. source/raw deeper investigation only when needed

### 5.2. Role of Task Lens
Task Lens determines:
- what knowledge to seek
- where to start
- how to expand

### 5.3. Role of AIP
AIP determines:
- what task is being executed
- what outputs are expected
- what checkpoints exist
- what candidate/wiki-related step should be triggered in that flow

### 5.4. Rule
AIP should not hardcode full retrieval logic that belongs to Task Lens.
AIP-Wiki Integration should stay at the level of:
- expected wiki dependence
- candidate/update behavior
- runtime reaction when knowledge is missing

---

## 6. Minimal AIP integration fields
This sprint does not require a strict universal AIP schema update,
but AIP templates/guidelines should support at least conceptually:

- `recommended_knowledge_to_load`
- `related_task_lens_or_lens_hint`
- `wiki_dependency_note`
- `if_wiki_is_insufficient_then`
- `wiki_candidate_suggestion_note`
- `artifact_publication_rule_note`

These may later be represented as explicit fields or structured sections.

---

## 7. When Wiki should be consulted in AIP-driven flow

### 7.1. Requirement-related AIPs
Examples:
- requirement clarification
- create basic design

Wiki is useful for:
- refined requirement chain
- Q&A reflection state
- related objects/aliases
- reusable project knowledge
- prior clarified rules

### 7.2. Review-related AIPs
Examples:
- review detail design
- review IT testcase

Wiki is useful for:
- trace chain visibility
- active supplemental artifacts
- object linkage
- reuse of prior project knowledge

### 7.3. Communication/reporting AIPs
Examples:
- weekly report
- meeting minutes to todos

Wiki is useful for:
- current project status context
- prior related outputs
- ongoing active unresolved items
- reflected vs still-active supplemental items

---

## 8. If Wiki is insufficient

### 8.1. Minimal reactions allowed
If Wiki is insufficient, AI may:
- consult linked artifacts directly
- mark unresolved linkage/gap
- produce a conservative output with explicit limits
- create or suggest metadata/linkage candidate
- create or suggest later Wiki update candidate

### 8.2. Rule
Insufficient Wiki should not automatically block task execution.
But AI should not silently pretend full knowledge coverage.

---

## 9. Artifact-creating AIPs and Wiki suggestion rule

### 9.1. Core rule
For AIPs that create a new artifact, AI should consider whether the resulting artifact should be suggested for Wiki addition.

### 9.2. Suggestion should depend on project profile
AI should not suggest add-to-wiki for every artifact blindly.
It should consult the project profile or project rule if available.

### 9.3. Main distinctions
Artifacts may be classified as:
- deliverable
- working
- temporary
- communication
- other project-defined role

Artifacts may also be classified as:
- wiki-eligible
- not wiki-eligible
- conditionally wiki-eligible

### 9.4. Rule
If an artifact is project-defined as:
- deliverable
- and wiki-eligible

then AI should suggest adding it to Wiki.

If BrSE agrees, the add-to-wiki path becomes a required step in that AIP flow.

If the artifact is not wiki-eligible, AI should skip this suggestion.

---

## 10. Add-to-wiki required-step rule

### 10.1. What “required” means in this sprint
If BrSE confirms that a newly created artifact should be added to Wiki,
the AIP flow should not consider itself complete until the Wiki addition handoff is prepared.

### 10.2. What the required step includes minimally
At minimal level, the step may include:
- identify artifact as wiki candidate
- prepare candidate / CR basis
- hand off to wiki manager / CR flow
- optionally prepare draft update material

### 10.3. Important boundary
“Required” does not mean:
- AI directly updates canonical Wiki without governance

It means:
- the AIP flow must include the necessary handoff toward proper Wiki update

---

## 11. Project profile interaction

### 11.1. Project profile may define
- deliverable vs working artifact
- wiki-eligible vs not
- conditionally publishable artifact types
- artifact classes that should be skipped
- curation preferences for metadata/linkage/curated knowledge

### 11.2. Rule
AIP-Wiki Integration should defer to project profile when available.

### 11.3. If project profile is missing or weak
AI should:
- act conservatively
- suggest candidate instead of assuming publishability
- ask for confirmation when needed

---

## 12. Output types that may lead to Wiki candidate
In AIP-driven flow, relevant outputs may include:
- newly created deliverable artifact
- metadata/linkage discovery
- curated reusable project knowledge
- reflection/superseded state clarification
- relationship clarification between artifacts

### Rule
Not all such outputs become canonical updates immediately.
They first become:
- candidate
- then possibly CR
- then canonical update if properly requested

---

## 13. AIP-driven vs non-AIP distinction

### 13.1. AIP-driven
This sprint explicitly specifies:
- when candidate suggestion is expected
- when artifact publication suggestion is expected
- when add-to-wiki becomes required after confirmation

### 13.2. Non-AIP
Outside AIP:
- AI may still suggest useful Wiki candidates
- but this sprint does not formalize the flow in equal detail
- governance still applies once canonical update is considered

---

## 14. Minimal examples

### 14.1. Example — Create Basic Design
- AIP creates a BD artifact
- project profile says BD is a deliverable and wiki-eligible
- AI suggests adding it to Wiki
- BrSE agrees
- add-to-wiki handoff becomes a required step before the AIP flow is considered complete

### 14.2. Example — Working draft note
- AIP produces a working-only draft note
- project profile says this class is not wiki-eligible
- AI skips add-to-wiki suggestion

### 14.3. Example — Review DD surfaces useful linkage
- AIP output includes a reusable linkage candidate
- AI suggests this as a Wiki candidate
- governance takes over if canonical update is wanted

---

## 15. Anti-confusion notes

### 15.1. AIP-Wiki Integration is not Task Lens
Task Lens decides what knowledge to seek.
AIP-Wiki Integration decides how AIP execution and Wiki behavior relate.

### 15.2. AIP-Wiki Integration is not Wiki Knowledge Profile
Wiki Knowledge Profile describes how knowledge is built and what it means.
AIP-Wiki Integration describes when AIP execution should consume Wiki and when AIP outputs should feed Wiki.

### 15.3. AIP-Wiki Integration is not governance itself
Governance controls canonical update.
AIP-Wiki Integration only defines where AIP hands off into candidate/CR/governance flow.

---

## 16. Relationship with other sprint artifacts
This spec is intended to work with:
- `TASK_LENS_AND_WIKI_KNOWLEDGE_PROFILE_BOUNDARY_NOTE`
- `WIKI_META_INDEX_SPEC`
- `WIKI_CHANGE_REQUEST_SPEC`
- `WIKI_MINIMAL_GOVERNANCE_RULE`
- future AIP template customization guidance
- future task execution guidance

---

## 17. Out of scope for this sprint
- fully automated artifact publication engine
- policy engine for all artifact classes
- automatic candidate prioritization engine
- dynamic runtime orchestration
- heavy workflow automation across many human roles

---

## 18. Completion criteria for BL-08
BL-08 is considered done when:
- runtime consultation boundary is clearly defined
- artifact-creating AIP suggestion rule is clearly defined
- add-to-wiki required-step rule is clearly defined
- project profile interaction is clearly defined
- AIP-driven vs non-AIP distinction is clearly defined
- governance handoff boundary is clearly defined
