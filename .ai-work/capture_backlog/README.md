# Capture Backlog

Captures deferred at AIP close, one JSONL file per account (`<account_id>.jsonl`).

A row here is a **decision already taken that lacks a destination**: someone judged it worth keeping but
not worth triaging in that session. It is NOT a parking space for undecided rows — an untriaged capture
stays `captured` in its workspace and blocks the close, on purpose.

Each row is **self-contained**: workspaces are gitignored and get archived, so a backlog row that merely
pointed at one would rot. Written only by `triage_capture.py`; never hand-edited.

- `status`: `open` | `triaged` | `promoted` | `discarded` — a backlog vocabulary, deliberately NOT part
  of `CAPTURE_STATUS_ENUM`.
- `resolution`: `{resolved_at, resolved_by, disposition_ref}`, where `disposition_ref` names what the row
  *became* — a CR id, a checklist item, a wiki `source_id`, a lint code.
