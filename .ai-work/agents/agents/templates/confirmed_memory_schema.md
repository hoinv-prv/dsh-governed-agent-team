# Confirmed Memory Schema (Detailed Design v0.2 §15; AP-CR-26)

HUMAN-confirmed memory only. File: `memory/confirmed_memory.jsonl`.

## JSONL record
```json
{"id":"CM-004","type":"domain","confirmed_by":"HUMAN","applies_when":"Reviewing the F-02 Search Room design specifically.","scope_tags":["function:f02","topic:search"],"content":"F-02 capacity rule: room capacity validated against booking count; check the validation path + the seat-vs-room count table gotcha."}
```

### Fields
| Field | Required | Notes |
|---|---|---|
| `id` | yes | unique within instance (CM-NNN) — the stable key |
| `type` | yes | methodology / process / guideline / domain / lesson / ... |
| `confirmed_by` | yes | must be HUMAN (no auto-confirm) |
| `content` | yes | the confirmed memory |
| `applies_when` | no | 1-line condition describing when the entry is relevant |
| `scope_tags` | no | array of scope tags (e.g. `function:f02`, `topic:search`); special tag `always` = load on every run |
| `clone_review` | no | `pending` on entries carried into a CLONE (AP-CR-28) — HUMAN keeps/prunes via `/aiws-agent-review-learning`; absent = not from a clone |
| `cloned_from` | no | source instance id, set with `clone_review` when an entry was carried in by `/aiws-agent-clone` (AP-CR-28) |

> A confirmed_memory entry MUST carry `confirmed_by: HUMAN` (no auto-confirm).
> Other confirmed knowledge surfaces (lessons_learned.md / local_guidelines.md / retrieval_hints.jsonl) follow the
> same HUMAN-gated promotion.

### Relevance-scoped loading (AP-CR-26)
On each run the agent loads the always-on + task-relevant entries in FULL and indexes ALL of them:
- `scope_tags` contains `always` → load every run.
- `scope_tags` / `applies_when` overlap the task → load (token overlap, or separator-stripped substring so `function:f02` matches "F-02").
- **Backward-compat:** an entry with neither `applies_when` nor `scope_tags` is treated as always-load — it is never hidden. (A malformed/legacy line is likewise kept and always loaded.)

### Clone carry-over (AP-CR-28)
`/aiws-agent-clone` copies confirmed memory into the new instance and marks each entry `clone_review: "pending"` + `cloned_from: <source_id>` (the relevance fields `applies_when`/`scope_tags` are preserved unchanged). The HUMAN keeps or prunes each flagged entry **for the new project** via `/aiws-agent-review-learning` (see `clone_review_checklist.md`) — never silently dropped, never auto-confirmed.

### Knowledge digests (CR-AIWS-2026-07-017)

Confirmed synthesis DOCUMENTS live as `.md` files under `memory/knowledge_digests/` (subdirectory of
instance memory). Each file carries frontmatter:

```yaml
digest_id: DG-001            # unique within instance
purpose: "<which intent/task-type this digest serves>"
source_refs: ["<source_id or path>", ...]
verification_level: verified | inferred    # inferred = AI synthesis not fully source-verified
reuse_when: "<1-line condition>"
status: confirmed | deprecated
confirmed_by: HUMAN
confirmed_at: YYYY-MM-DD
```

Rules:
- A digest enters this store ONLY via `/aiws-agent-review-learning` confirm of a
  `digest_synthesis_candidate` (rule #7 / FR-MEM-04 — never auto).
- **Discovery channel = `retrieval_hints.jsonl`:** on confirm, exactly ONE hint entry is appended
  (`digest_id` + path + `reuse_when`). The ARC surfaces hints (§5) — there is no separate digest index.
- **Two-tier promotion:** a digest with project-wide value is additionally proposed via the project
  capture inbox (playbook trigger #20) and, on HUMAN approval, materialized to the wiki via
  `build_reading_kit.py --materialize` + registered as a wiki source (derived-surface doctrine —
  never hand-written to the wiki). Pure-AI-synthesis digests keep `verification_level: inferred`.
