# aiws-wiki — operation: deregister

> Operation of the `aiws-wiki` domain skill (consolidated by CR-AIWS-2026-07-025; former standalone skill — see `product/rename_map.json`). Content preserved verbatim; every gate herein stays binding.


REMOVE counterpart to `/aiws-wiki register` (ADD) and `/aiws-wiki refresh` (UPDATE).
Replaces the error-prone manual sequence (delete meta → rebuild index → hand-write audit log)
with one gated, schema-safe flow.

## Routing — Detect Case First

```
User says / provides                         → CASE
────────────────────────────────────────────────────────────────────
A single source_id                           → CASE 1  (single remove)
"gỡ source X", "remove this source"          → CASE 1
A folder of metas / list of source_ids       → CASE 2  (batch remove)
"toàn bộ", multiple ids                       → CASE 2
"dọn orphan", "clean dangling meta"          → CASE 3  (orphan sweep)
"source artifact đã bị xóa"                  → CASE 3
```

**Ambiguous input:** Ask 1 clarifying question:
"Bạn muốn gỡ (a) một source_id cụ thể, (b) nhiều source / cả folder, hay (c) dọn orphan (meta trỏ tới artifact không còn tồn tại)?"

---

## CASE 1 — Single Remove

```
STAGE 1 ── RESOLVE (deterministic) ───────────────────────────────
  1.1 Locate the meta via the index — do NOT guess the file path:
      py .ai-work/tooling/lookup_wiki_source.py --query "<source_id>"
      → read result, take the `meta:` path for the matching source_id
  1.2 If source_id not found in index → report "không tìm thấy trong index,
      không có gì để gỡ" and STOP (or offer CASE 3 orphan sweep).
  1.3 Read the meta frontmatter; note: source_id, title, artifact_locator, status.

STAGE 2 ── HUMAN GATE (MANDATORY) ────────────────────────────────
  2.1 Show exactly what will be removed:
      "Sẽ gỡ source này khỏi wiki:
        - source_id: <id>
        - title: <title>
        - meta: <meta path>
        - artifact_locator: <locator>
        - index entry: sẽ bị drop khi reproject
       Meta sẽ được ARCHIVE (default) hay DELETE? Xác nhận? (archive / delete / cancel)"
  2.2 Do NOT proceed without explicit confirmation. "cancel" → stop, no change.

STAGE 3 ── REMOVE + REPROJECT + AUDIT ────────────────────────────
  3.1 Archive (default) or delete the meta:
      - archive → move meta to .ai-work/history/archive/wiki_meta_deregistered/<date>/
      - delete  → remove the meta file
  3.2 Reproject the index (drops the entry whose backing meta is gone):
      py .ai-work/tooling/build_wiki_source_index.py
  3.2b Rebuild the relations projection (the removed meta's ## Related Sources edges drop out):
      py .ai-work/tooling/build_relations.py
  3.3 Append a schema-valid audit entry via the shared helper (CR-006) — never hand-write JSON:
      py -c "import sys,pathlib; sys.path.insert(0,'.ai-work/tooling'); \
from datetime import datetime,timezone; from _common import append_maintenance_log; \
aw=pathlib.Path('.ai-work'); \
append_maintenance_log(aw/'wiki_sources'/'maintenance_log.jsonl', { \
 'log_id':'WSMLOG-'+datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')+'-DEREG-<ID>', \
 'timestamp':datetime.now(timezone.utc).isoformat(), 'maintenance_model_version':'wsm_v1', \
 'action':'source_deregistered', 'source_id':'<ID>', \
 'target_artifact':'<meta locator, __PROJECT_ROOT__-relative>', \
 'change_summary':'Deregistered source <ID> (<archive|delete>); index reprojected.', \
 'review_decision':'deregistered_by_human_request', \
 'rollback_hint':'Restore meta from history/git and rebuild index to re-register.' })"
  3.4 Report:
      - Deregistered: <source_id>
      - Meta: archived to <path> | deleted
      - Index: reprojected (N entries)
      - Audit: <log_id>
```

---

## CASE 2 — Batch Remove

Same as CASE 1 but resolve a list/folder first, show the FULL list once in the HUMAN gate
(2.1), confirm once, then loop STAGE 3 per source_id. Rebuild the index **once** at the end,
and append one `source_deregistered` entry per source_id. Report a summary table.

---

## CASE 3 — Orphan Sweep

For "meta points to a nonexistent artifact" (the reverse of the index→meta stale check).

```
  3.1 Find candidates: run lint and collect meta_orphan_artifact findings:
      py .ai-work/tooling/lint_wiki.py    # → lines with code meta_orphan_artifact
  3.2 Show the orphan list in the HUMAN gate (these metas point to files that no longer exist).
  3.3 For each confirmed orphan → run CASE 1 STAGE 3 (archive/delete + reproject + audit).
```

---

## Object-aware notes (node_kind)

- **Deregister an ARTIFACT that represents/relates to an object:** does NOT cascade to the object node — the object persists. The artifact's own `## Related Sources` edges drop out with its meta; after the index reproject, rebuild the relations projection (`build_relations.py`, STAGE 3.2b) so `relations.jsonl` follows.
- **Deregister the OBJECT meta itself** (CASE 1, `node_kind=object`): in the HUMAN gate, FIRST run `wiki_relations.py --relations <object-id>` to surface IN-edges (other artifacts' `represents` / objects' `x:` pointing AT it). If the object is STILL referenced by other artifacts → require an EXPLICIT extra HUMAN confirm (removal leaves those references as `[BROKEN REF]` until the owning metas are cleaned).
- **Orphan sweep (CASE 3):** object metas are sourceless (`__OBJECT__`) → they never appear in the orphan sweep (no backing artifact to go missing).

---

## Rules

- **HUMAN gate (STAGE 2) is MANDATORY** — never delete or archive a meta without explicit confirmation.
- **Audit entry is MANDATORY** and MUST go through `append_maintenance_log()` (schema-checked,
  newline-safe) — never hand-append JSON to the log.
- Use `action: source_deregistered` (canonical removal action).
- RESOLVE via the index/lookup — do NOT guess meta file paths.
- Default to **archive**, not hard delete, unless the user chooses delete.
- Rebuild the index after removal so no dangling entry remains.
- `meta_archived` (keep-but-hide) is a different action — use `source_deregistered` only for removal.
