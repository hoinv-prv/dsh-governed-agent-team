---
name: aiws-util-personal-notebook
description: >
  Personal Notebook — ghi/khởi tạo ghi chú cá nhân dạng file (status / authority / source hints) qua
  `scripts/notebook_write.py`; operations: init_notebook · append_inbox_note · create_note_file ·
  mark_capture_candidate · archive_note. Dùng khi HUMAN muốn "ghi chú cá nhân" / "lưu note" / "note
  this for later". KHÔNG phải capture inbox của workspace, KHÔNG phải wiki: notebook là ghi chú cá
  nhân — không phải source of truth, không tự promote lên Knowledge Hub, chỉ ghi khi HUMAN xác nhận.
user-invocable: true
---

# SKILL: aiws-util-personal-notebook

## Purpose
Help AI/HUMAN create, append, and lightly update file-based Personal Notebook notes.

## Guardrails
- Write only when HUMAN explicitly asks or confirms, unless local setup clearly allows otherwise.
- Do not auto-promote notebook content to Knowledge Hub.
- Do not treat notebook content as source of truth by default.
- Preserve status / authority / source hints.
- Do not rewrite or delete aggressively.
- Do not become decision authority or orchestrator.

## Inputs
- notebook path
- operation
- title
- status
- authority
- source
- intended use
- review needed
- body

## Supported operations
- `init_notebook`
- `append_inbox_note`
- `create_note_file`
- `mark_capture_candidate`
- `archive_note`

## Tool
`scripts/notebook_write.py`

## Example
```bash
python scripts/notebook_write.py \
  --operation append_inbox_note \
  --notebook-path ./.aiws/personal_notebook \
  --title "Future sprint idea: Notebook search" \
  --status future_sprint_idea \
  --authority personal \
  --source self \
  --intended-use "sprint planning" \
  --review-needed yes \
  --body "Consider a later sprint for Personal Notebook search/index support."
```

## Result
The tool writes to the configured Personal Notebook and returns a short JSON result.
