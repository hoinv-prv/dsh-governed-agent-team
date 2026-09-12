---
description: Nhân bản một Agent Task Desk đã được huấn luyện sang desk mới: copy lớp desk-owned, gắn cờ review cho memory mang theo (không auto-confirm), ghi lineage. KHÔNG copy run-history.
argument-hint: <source-desk> --as "<display name>" [--id <new-id>] [--why "..."]
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, TodoWrite
---

# /aiws-agent-clone — pointer stub (generated at build — do not edit; CR-AIWS-2026-08-019)

Read and follow the authoritative verb spec: `.ai-work/agents/commands/aiws-agent-clone.md`.
Every gate in that spec (HUMAN confirm, aip_driven, no-auto-promotion, …) applies unchanged.
NL alternative: the `/aiws-agent` router skill.
