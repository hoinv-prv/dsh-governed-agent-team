# Wiki (Knowledge Hub) Authoring Guideline
## Terminology note
Trong AI Work System:
- **Knowledge Hub** là tên chính thức của component
- **Wiki** là tên vắn tắt vẫn được dùng bên trong hệ thống để chỉ Knowledge Hub


## Core model
Wiki (Knowledge Hub shorthand) is curated + guidance-centric.
It is not the same as Truth and not the same as History.

## Required core sections
- Purpose
- Scope
- Canonical References
- Recommended Next Reads

## Metadata for important entries
- artifact_type
- entry_type
- artifact_id
- title
- knowledge_class
- use_rule
- status
- canonical_references
- last_verified_at
- updated_at

> `last_verified_at` and `updated_at` are **UTC ISO 8601 timestamps** (CR-AIWS-2026-06-024); a legacy `YYYY-MM-DD` date is also accepted.

## Staleness
Use status:
- active
- needs_review