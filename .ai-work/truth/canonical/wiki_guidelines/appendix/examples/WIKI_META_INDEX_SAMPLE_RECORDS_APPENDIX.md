# WIKI_META_INDEX_SAMPLE_RECORDS_APPENDIX_v0_9_8

Status: Canonical appendix  
Version: v0.9.8  
Date: 2026-04-26  
Source: Wiki Meta / Index Minimal Spec Sprint — WMI-11

---

## Purpose

This appendix provides current-compatible sample Wiki Source Meta records.

These samples preserve the v0.9.2 field names and body sections.

---

# AIWS_WMI-11_SAMPLE_META_RECORDS_v1

Status: Draft  
Sprint: Wiki Meta / Index Minimal Spec Sprint  
Baseline: AI Work System MVP v0.9.7  
Compatibility baseline: AIWS MVP v0.9.2 Wiki Source Meta / Index mechanism

---

## 1. Purpose

WMI-11 provides sample Wiki Source Meta records that are compatible with the current v0.9.2 Wiki Source Meta / Index mechanism.

The samples demonstrate:

- current field names
- current body sections
- `artifact_locator` pointing to AIWS-readable markdown/source representation
- original raw file reference as optional body note
- practical `Knowledge Targets`
- practical `Lookup Keys`
- useful `Source-Specific Hints`
- useful `Change Impact Hints`
- useful `Cautions`
- expected JSONL projection shape

These samples are not new schema requirements.  
They are examples of good usage of the current format.

---

## 2. Current-compatible meta structure

Current frontmatter:

```yaml
artifact_type: wiki_source_meta
source_id:
title:
source_type:
knowledge_class:
artifact_locator:
profile_id:
status:
updated_at:
```

Current body sections:

```markdown
## Summary
## Knowledge Targets
## Lookup Keys
## Artifact Reference
## Source-Specific Hints
## Change Impact Hints
## Cautions
```

---

# 3. Sample 1 — Requirement document, markdown source

## 3.1. Use case

A requirement definition document already exists as markdown and can be read directly by AIWS runtime.

## 3.2. Meta file

Recommended file:

```text
.ai-work/wiki_sources/meta/SRC-RD-F02-SEARCHROOM.md
```

```markdown
---
artifact_type: wiki_source_meta
source_id: SRC-RD-F02-SEARCHROOM
title: Requirement Definition F02 SearchRoom
source_type: requirement_doc
knowledge_class: curated
artifact_locator: __PROJECT_ROOT__/docs/requirements/F02_SearchRoom_Requirement.md
profile_id: requirement-definition-v1
status: active
updated_at: 2026-04-26
---

# Wiki Source Meta — Requirement Definition F02 SearchRoom

## Summary
Requirement definition for F02 SearchRoom. Covers available meeting room search conditions, search result display, and basic business rules for room availability.

## Knowledge Targets
- F02 SearchRoom requirement
- available meeting room search
- room search condition
- search result display rules
- meeting room booking requirement

## Lookup Keys
- F02
- SearchRoom
- room search
- search room
- available room
- meeting room
- 会議室検索
- 空き会議室
- RD F02
- requirement F02

## Artifact Reference
- artifact_locator: __PROJECT_ROOT__/docs/requirements/F02_SearchRoom_Requirement.md

## Source-Specific Hints
- Use section "Search Conditions" for search input behavior.
- Use section "Search Result Rules" for result list display.
- Related basic design: SRC-BD-F02-SEARCHROOM
- Relevant for requirement clarification, basic design creation, design review, and testcase creation.

## Change Impact Hints
- If search condition rules change, update Knowledge Targets and Lookup Keys.
- If related customer Q&A changes search behavior, update Source-Specific Hints and related BD/DD meta.
- If this document becomes official source of truth, update knowledge_class only after HUMAN instruction.

## Cautions
- This requirement is curated but not automatically source_of_truth.
- If conflict exists with customer Q&A, verify latest Q&A source before final decision.
```

## 3.3. Expected index projection

Approximate generated JSONL record:

```json
{
  "source_id": "SRC-RD-F02-SEARCHROOM",
  "title": "Requirement Definition F02 SearchRoom",
  "source_type": "requirement_doc",
  "artifact_locator": "__PROJECT_ROOT__/docs/requirements/F02_SearchRoom_Requirement.md",
  "meta_locator": "__PROJECT_ROOT__/.ai-work/wiki_sources/meta/SRC-RD-F02-SEARCHROOM.md",
  "meta_id": "SRC-RD-F02-SEARCHROOM",
  "profile_id": "requirement-definition-v1",
  "summary_short": "Requirement definition for F02 SearchRoom. Covers available meeting room search conditions...",
  "knowledge_targets": [
    "F02 SearchRoom requirement",
    "available meeting room search",
    "room search condition",
    "search result display rules",
    "meeting room booking requirement"
  ],
  "lookup_keys": [
    "F02",
    "SearchRoom",
    "room search",
    "search room",
    "available room",
    "meeting room",
    "会議室検索",
    "空き会議室",
    "RD F02",
    "requirement F02"
  ],
  "status": "active",
  "updated_at": "2026-04-26"
}
```

---

# 4. Sample 2 — Converted Excel testcase

## 4.1. Use case

Original testcase is Excel.  
AIWS runtime reads converted markdown representation.

## 4.2. Meta file

Recommended file:

```text
.ai-work/wiki_sources/meta/SRC-IT-F04-MYBOOKINGS.md
```

```markdown
---
artifact_type: wiki_source_meta
source_id: SRC-IT-F04-MYBOOKINGS
title: Integration Testcase F04 MyBookings
source_type: testcase
knowledge_class: reference
artifact_locator: __PROJECT_ROOT__/docs/testcases/converted/F04_MyBookings_Testcase.md
profile_id: testcase-v1
status: needs_review
updated_at: 2026-04-26
---

# Wiki Source Meta — Integration Testcase F04 MyBookings

## Summary
Integration testcase for F04 MyBookings. Covers booking list display, cancellation operation, status transitions, and expected messages.

## Knowledge Targets
- F04 MyBookings testcase
- booking cancellation test
- booking list display
- reservation status transition
- integration test for my bookings

## Lookup Keys
- F04
- MyBookings
- my bookings
- booking cancellation
- cancel booking
- 予約取消
- 予約キャンセル
- 予約一覧
- IT F04
- testcase F04

## Artifact Reference
- artifact_locator: __PROJECT_ROOT__/docs/testcases/converted/F04_MyBookings_Testcase.md
- original_artifact_locator: __PROJECT_ROOT__/raw/testcases/F04_MyBookings_Testcase.xlsx
- conversion_note: converted as-is from Excel to markdown
- representation_quality: partial

## Source-Specific Hints
- Testcase rows are converted to markdown tables.
- Use testcase ID column when referencing specific cases.
- Related requirement: SRC-RD-F04-MYBOOKINGS
- Related detail design: SRC-DD-F04-MYBOOKINGS
- Use this source for testcase review and test coverage check.

## Change Impact Hints
- If Excel conversion is improved, update artifact_locator or representation_quality.
- If cancellation business rule changes, update Knowledge Targets and Lookup Keys.
- If testcase is reviewed/approved, update status from needs_review to active.

## Cautions
- representation_quality: partial
- Original file was Excel; formulas, hidden sheets, filters, and merged-cell layout may not be fully represented.
- For high-impact testcase review, request HUMAN confirmation if converted markdown table is unclear.
- Do not infer hidden Excel content that is not present in the markdown representation.
```

## 4.3. Expected index projection

```json
{
  "source_id": "SRC-IT-F04-MYBOOKINGS",
  "title": "Integration Testcase F04 MyBookings",
  "source_type": "testcase",
  "artifact_locator": "__PROJECT_ROOT__/docs/testcases/converted/F04_MyBookings_Testcase.md",
  "meta_locator": "__PROJECT_ROOT__/.ai-work/wiki_sources/meta/SRC-IT-F04-MYBOOKINGS.md",
  "meta_id": "SRC-IT-F04-MYBOOKINGS",
  "profile_id": "testcase-v1",
  "summary_short": "Integration testcase for F04 MyBookings. Covers booking list display...",
  "knowledge_targets": [
    "F04 MyBookings testcase",
    "booking cancellation test",
    "booking list display",
    "reservation status transition",
    "integration test for my bookings"
  ],
  "lookup_keys": [
    "F04",
    "MyBookings",
    "my bookings",
    "booking cancellation",
    "cancel booking",
    "予約取消",
    "予約キャンセル",
    "予約一覧",
    "IT F04",
    "testcase F04"
  ],
  "status": "needs_review",
  "updated_at": "2026-04-26"
}
```

---

# 5. Sample 3 — Source of truth artifact

## 5.1. Use case

HUMAN explicitly confirms that this overall requirement document is source of truth.

## 5.2. Meta file

Recommended file:

```text
.ai-work/wiki_sources/meta/SRC-RD-OVERALL-MEETINGROOM.md
```

```markdown
---
artifact_type: wiki_source_meta
source_id: SRC-RD-OVERALL-MEETINGROOM
title: Requirement Definition Overall MeetingRoomBooking
source_type: requirement_doc
knowledge_class: source_of_truth
artifact_locator: __PROJECT_ROOT__/docs/requirements/Overall_MeetingRoomBooking_Requirement.md
profile_id: requirement-definition-v1
status: active
updated_at: 2026-04-26
---

# Wiki Source Meta — Requirement Definition Overall MeetingRoomBooking

## Summary
Overall requirement definition for Meeting Room Booking system. Covers system scope, main actors, function list, common rules, booking lifecycle, and shared business constraints.

## Knowledge Targets
- meeting room booking overall requirement
- system scope
- function list
- booking lifecycle
- common business rules
- source of truth for requirement overview

## Lookup Keys
- overall requirement
- MeetingRoomBooking
- meeting room booking
- room booking
- booking lifecycle
- function list
- common rules
- 全体要件
- 会議室予約
- RD overall

## Artifact Reference
- artifact_locator: __PROJECT_ROOT__/docs/requirements/Overall_MeetingRoomBooking_Requirement.md

## Source-Specific Hints
- Use this source first for overall scope and common business rule confirmation.
- Related function requirement sources:
  - SRC-RD-F02-SEARCHROOM
  - SRC-RD-F03-CREATEBOOKING
  - SRC-RD-F04-MYBOOKINGS
- Use function-level sources for detailed behavior.

## Change Impact Hints
- If overall function list changes, update related function-level meta references.
- If common business rule changes, review related BD/DD/Testcase meta.
- Any change to this source should be treated as high-impact.

## Cautions
- knowledge_class is source_of_truth because HUMAN explicitly confirmed it.
- This source covers overall rules; use function-level sources for detailed screen/function behavior.
```

## 5.3. Important note

`knowledge_class: source_of_truth` must not be set by AI alone.

It requires HUMAN instruction/approval.

---

# 6. Sample 4 — Deprecated artifact

## 6.1. Use case

Old basic design file exists but has been superseded.

## 6.2. Meta file

Recommended file:

```text
.ai-work/wiki_sources/meta/SRC-BD-F03-CREATEBOOKING-OLD.md
```

```markdown
---
artifact_type: wiki_source_meta
source_id: SRC-BD-F03-CREATEBOOKING-OLD
title: Basic Design F03 CreateBooking old draft
source_type: basic_design
knowledge_class: history
artifact_locator: __PROJECT_ROOT__/docs/design/basic/archive/F03_CreateBooking_BD_old.md
profile_id: basic-design-v1
status: deprecated
updated_at: 2026-04-26
---

# Wiki Source Meta — Basic Design F03 CreateBooking old draft

## Summary
Old draft of Basic Design for F03 CreateBooking. Kept for historical reference only.

## Knowledge Targets
- old F03 CreateBooking basic design
- historical design reference
- booking creation old draft

## Lookup Keys
- F03
- CreateBooking
- old basic design
- archive
- deprecated
- 予約作成
- BD F03 old

## Artifact Reference
- artifact_locator: __PROJECT_ROOT__/docs/design/basic/archive/F03_CreateBooking_BD_old.md

## Source-Specific Hints
- Prefer replacement source: SRC-BD-F03-CREATEBOOKING
- Use only when investigating history or old design decisions.

## Change Impact Hints
- If old draft is removed from project, archive or delete this meta according to project policy.
- If replacement source changes, update replacement source_id hint.

## Cautions
- status: deprecated
- Do not use this artifact for current design or testcase creation.
- Use SRC-BD-F03-CREATEBOOKING for current basic design.
```

## 6.3. Expected behavior

Lookup may still return this source, but AI should avoid using it for current work because status is deprecated and caution points to replacement.

---

# 7. Sample 5 — Diagram converted to markdown description

## 7.1. Use case

Original artifact is an image/diagram.  
Converted markdown representation describes the diagram contents.

## 7.2. Meta file

Recommended file:

```text
.ai-work/wiki_sources/meta/SRC-DIAGRAM-BOOKING-FLOW.md
```

```markdown
---
artifact_type: wiki_source_meta
source_id: SRC-DIAGRAM-BOOKING-FLOW
title: Diagram Booking Flow
source_type: project_diagram
knowledge_class: reference
artifact_locator: __PROJECT_ROOT__/docs/diagrams/converted/Booking_Flow_Diagram.md
profile_id: diagram-v1
status: active
updated_at: 2026-04-26
---

# Wiki Source Meta — Diagram Booking Flow

## Summary
Markdown representation of booking flow diagram. Describes user search, booking creation, confirmation, cancellation, and status transitions.

## Knowledge Targets
- booking flow diagram
- booking lifecycle
- room search to booking creation flow
- booking cancellation flow
- status transition overview

## Lookup Keys
- booking flow
- booking lifecycle
- status transition
- booking diagram
- 予約フロー
- 予約ステータス
- cancellation flow
- Diagram Booking Flow

## Artifact Reference
- artifact_locator: __PROJECT_ROOT__/docs/diagrams/converted/Booking_Flow_Diagram.md
- original_artifact_locator: __PROJECT_ROOT__/raw/diagrams/Booking_Flow_Diagram.png
- conversion_note: diagram converted as-is to markdown textual description
- representation_quality: sufficient

## Source-Specific Hints
- Use this source for flow-level understanding.
- Use function-level RD/BD/DD sources for detailed rules.
- Related sources:
  - SRC-RD-OVERALL-MEETINGROOM
  - SRC-RD-F03-CREATEBOOKING
  - SRC-RD-F04-MYBOOKINGS

## Change Impact Hints
- If booking status values change, update this diagram representation.
- If diagram image changes, regenerate markdown representation and update updated_at.

## Cautions
- This is a markdown representation of a diagram.
- If visual layout/order is critical, confirm that the converted markdown fully captures it.
- Do not infer diagram elements that are not present in the markdown representation.
```

---

# 8. Lookup verification examples

After rebuild, verify:

```bash
python .ai-work/tooling/lookup_wiki_source.py --query "F02 SearchRoom"
python .ai-work/tooling/lookup_wiki_source.py --query "会議室検索"
python .ai-work/tooling/lookup_wiki_source.py --query "予約取消"
python .ai-work/tooling/lookup_wiki_source.py --query "booking flow"
python .ai-work/tooling/lookup_wiki_source.py --query "source of truth overall requirement"
```

Expected:
- relevant sources appear near top
- deprecated source shows status `deprecated`
- converted Excel/diagram sources expose cautions in meta
- AI opens meta first, then artifact when needed

---

# 9. Sample quality checklist

For each sample/current meta:

```markdown
- [ ] Current field names preserved
- [ ] source_id stable and unique
- [ ] title readable
- [ ] source_type practical
- [ ] artifact_locator points to AIWS-readable artifact
- [ ] original_artifact_locator noted if original is non-text
- [ ] representation quality noted when relevant
- [ ] Summary useful
- [ ] Knowledge Targets semantic/use-oriented
- [ ] Lookup Keys practical and multilingual if useful
- [ ] Source-Specific Hints guide AI runtime use
- [ ] Change Impact Hints guide maintenance
- [ ] Cautions prevent misuse
- [ ] status/knowledge_class appropriate
- [ ] source_of_truth only if HUMAN confirmed
```

---

# 10. Conclusion

WMI-11 provides current-compatible samples.

Core sample stance:

```text
Keep current v0.9.2 field names and tooling.
Use better content and hints to improve AI runtime.
Represent non-text sources through AIWS-readable markdown artifact.
```

Next: WMI-12 Canonical Merge Map.
