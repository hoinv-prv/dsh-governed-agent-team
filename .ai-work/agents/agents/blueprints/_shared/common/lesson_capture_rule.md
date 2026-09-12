# Lesson Capture Rule (shared)

> **Location note (CR-AIWS-2026-07-017):** moved from `_shared/review/process/` to `_shared/common/` — this rule is PACK-LEVEL (all blueprint families: review, PM, coordinator). Review-specific examples below are marked; non-review blueprints read the rule and substitute their own examples.

> Shared across all Document Review Agent blueprints.
> Mapped from: MEMORY_AND_LEARNING_RULES_TEMPLATE.md + REVIEW_AGENT_BLUEPRINT_TEMPLATE.md §13-§16
> (v0.1).
> Document-type-agnostic.

---

## 1. Core rule

```text
Run output is evidence.
Learning candidate is a proposal.
Confirmed memory requires HUMAN approval.
```

The agent never auto-confirms a candidate, never overwrites Official Wiki, never updates a
checklist or blueprint on its own. Promotion is HUMAN-gated.

> ⚖ **governance_invariant** `no_auto_promote` — never auto-confirm a candidate or overwrite Wiki / checklist / blueprint / **the instance's own process**; promotion is HUMAN-gated (incl. `process_improvement_candidate`, AP-CR-31).

## 2. When to capture

After each meaningful review run, propose learning candidates when useful — and inline on
discovery, not only at the end. Typical triggers:
- a recurring document-type review point worth adding to a checklist,
- a project-specific reference-navigation hint,
- a HUMAN-rejected finding likely to recur (false positive),
- a recurring project issue pattern,
- an output-format preference the HUMAN asked for,
- official project knowledge discovered during review (wiki_candidate),
- a reusable rule worth pushing to the blueprint (blueprint_improvement_candidate (P2 alias: `atdb_improvement_candidate` — new emissions may use either; old records stay valid)).

## 3. Candidate types

```text
review_rule_candidate
checklist_update_candidate
retrieval_hint_candidate
false_positive_note_candidate
project_issue_pattern_candidate
output_preference_candidate
wiki_candidate
blueprint_improvement_candidate
process_improvement_candidate
```

> **`process_improvement_candidate` (AP-CR-31) — universal kind, all agents.** Proposes a change to **this instance's own process** (`instances/<id>/process/`, FR-AI-13 / Detailed Design §6D). On HUMAN confirm via `/aiws-agent-review-learning` it is written to the instance process + an Instance `changelog.md` entry (`layer: override`, `source: learning-candidate`). It must NOT drop/weaken a `governance_invariant` step. Never agent-self-applied (`no_auto_promote`).

## 4. Candidate schema (JSONL)

```json
{
  "candidate_id": "LC-YYYYMMDD-001",
  "source_run": "RUN-YYYYMMDD-HHMM-<short_task_name>",
  "type": "checklist_update_candidate",
  "scope": "<review_scope>",
  "content": "<candidate content>",
  "evidence": "<why this candidate was proposed>",
  "recommended_destination": "memory | checklist | wiki | blueprint",
  "status": "candidate"
}
```

All entries are emitted with `status: candidate`. Allowed statuses over the lifecycle:
`candidate / confirmed / rejected / deferred / deprecated` (Detailed Design v0.2 §14).

## 5. Destination rules

```text
Agent Task Desk Memory:   project/context-specific review behavior, retrieval hints, false positives.
Checklist Update:        recurring document-type-specific review point.
Wiki Candidate:          official project knowledge discovered during review.
Blueprint Improvement:   reusable rule for future agents of this document type.
```

## 6. Capture routing by run context (Detailed Design v0.2 §14 / AP-CR-13)

> **Full routing table (CR-AIWS-2026-08-010):** `capture_routing_rule.md` (cùng thư mục) — chuẩn phân
> loại Desk-personal vs Task-Workspace-shared, ca "cả hai giá trị", và default khi không chắc.
> **Vocabulary bridge (CR-AIWS-2026-08-011, BẮT BUỘC):** các type §3 dưới đây là vocabulary **desk-side**;
> khi tier-up lên Task Workspace phải DỊCH sang enum TW theo mục "Vocabulary bridge" của
> `capture_routing_rule.md` (giữ nhãn gốc ở `desk_type`) — ghi thẳng type desk-side vào TW sẽ sinh lint WARNING.

- Agent running UNDER an AIP: tier the capture UP to the project capture inbox
  `08_capture_inbox.jsonl` / the wiki-candidate flow; the instance keeps only a POINTER back to
  that capture (not a duplicate).
- Agent running WITHOUT an AIP: the capture stays local in the instance
  `training/candidate_queue.jsonl`.

In both branches, promotion to confirmed memory / Official Wiki remains HUMAN-gated.

## 7. Where candidates are written

```text
workspace/completed_runs/<run_id>/learning_candidates.jsonl   (per-run evidence)
training/candidate_queue.jsonl                                (instance-level queue)
```

## 8. No auto-promotion

Instance memory files start EMPTY. Candidates are never auto-confirmed. Confirmed memory, checklist
updates, Wiki candidates, and blueprint improvements are applied only after HUMAN approval (see
`document_review_process.md` Step 8-9).

## Relations fast-path + QA precedence (CR-AIWS-2026-07-015; consumes wave-912 mechanisms)

- **Relations fast-path:** discovering a NEW relationship between sources during a run is a
  ⚡ capture-immediately trigger (project playbook trigger #2, upgraded by CR-AIWS-2026-07-008):
  record the machine-readable block `relation: {from_id, to_id, role, basis_note_draft,
  confidence: "candidate"}` — write the basis note AT DISCOVERY (objective, intent-blind). Batch
  promotion via the Relations Enrichment CR flow (`.ai-work/procedural/relations_enrichment_cr_template.md`,
  per-edge attestation; cadence DP-912-7). AIP-driven runs tier the capture to the Task Workspace inbox.
- **Q&A precedence (meta-first — QA_Memory_Spec_MVP / FIT-5):** a good Q→A pair found during a run
  is emitted as a `qa_candidate` (fields `question`/`answer`/`qa_kind`/`applies_when`; agent
  self-derived → `asked_by: ai` = `investigation_finding`, HUMAN confirm mandatory on promote).
  PRECEDENCE: if the answer reduces to a meta lookup_keys/summary fix or a relation edge — propose
  THAT instead; only answers that do NOT reduce to a meta/relation/kit edit belong in the QA store.
