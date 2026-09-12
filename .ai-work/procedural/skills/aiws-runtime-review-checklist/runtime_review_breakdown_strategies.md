---
doc_id: RUNTIME-REVIEW-BREAKDOWN-STRATEGIES-001
title: Runtime Review — Breakdown-Strategy Method Templates
version: v1.0
status: active
applies_to: aiws-runtime-review-checklist skill (per-item_type METHOD TEMPLATE data asset)
provenance: CR-AIWS-2026-06-053 (apply AIP-EXEC-158); templates hardened per the AIP-EXEC-157 clean-room re-test
---

# Runtime Review — Breakdown-Strategy Method Templates

Per-`item_type` **METHOD TEMPLATE** data asset for the `aiws-runtime-review-checklist` skill. The skill **dispatches** each selected source-checklist item to the template matching its `item_type` and instantiates `<doc-specifics>` — the author never invents a per-item method. Keeping the templates here (data) rather than in the SKILL.md body lets a project tune review heuristics without a SKILL.md `cr_required` change.

A runtime check item produced from a template carries: **Assert** (objective claim) · **Method** (numbered steps, each citing an EXACT target-doc locus) · **PASS / FAIL / N·A-iff** (objective, measurable) · **Evidence** · **Verdict** (filled by the caller/executor).

## Determinism rules (apply to EVERY template)
1. **Closed universe** — any "enumerate X" step MUST name the exact source section(s) it reads from; the resulting set is closed (no reviewer-supplied members).
2. **No perception verbs** — never "enough / appropriate / obvious / vague / needs-a-guess". Use presence/absence, set-membership, or a named-attribute rubric.
3. **Locus-validity** — every cited locus MUST exist in the in-scope inputs. If a step would read an out-of-scope or absent locus, record the absence as **GAP** (referenced-but-undefined) or **QUESTION** (source unavailable) — never enumerate from an un-openable source.
4. **Template-conformance** — an item satisfies its template's FULL PASS-iff OR explicitly declares the reduced legs it covers ("partial-X check"). No silent partial PASS.
5. **Objective sufficiency** — every "addressed / present / consistent" judgement resolves to a named-attribute or set-membership test (see each template).
6. **Machine-checkable `iff`** — the `PASS / FAIL / N·A-iff` MUST be a mechanical predicate (closed-enumeration / presence / equality / set-membership on a cited locus), verbatim-verifiable by a second reader from the `iff` ALONE. The banned perception verbs (rule 2) are a **lint** target, not a self-audit — enforcement is a checklist lint over the produced `06_runtime_review_checklist.md` *(the lint rule is a tracked follow-on where a checklist-lint path exists; the predicate requirement holds regardless of whether the lint is wired yet)*.

## Status semantics
`PASS` checked, compliant, evidence present · `FAIL` required info missing / wrong / contradictory · `RISK` present but may cause rework / quality / security / production risk · `QUESTION` cannot determine from available inputs (needs HUMAN / extra source) · `N/A` not applicable to this target/scope (record the basis) · `NOT_CHECKED` selected but not yet checked.

## Verdict rubric — LEG-CLASSIFIED (assign the token mechanically; the reproducibility lever)
Every template's PASS/FAIL/RISK is a decision over its **legs**, each leg tagged **HARD** (absent ⇒ FAIL) or **SOFT** (absent/advisory ⇒ RISK). The token is a mechanical function — do NOT re-judge "does it block implementation?":
```
verdict = N/A       if an explicit n_a_condition / cited scope-out applies (guarded categories: only on explicit match or HUMAN confirm)
        else QUESTION if a needed leg requires an OUT-OF-SCOPE (un-openable) source
        else FAIL    if ANY HARD leg is absent / contradicted
        else RISK    if ANY SOFT leg is absent, or present only as advisory/modal ("nên/should/may", no named step)
        else PASS
```
"Absent" = not stated at a citable locus in the in-scope text. A contradiction (two literals for one concept; a defined rule with no counterpart) is a HARD failure. This pins the same finding to the same token across runs (empirically: 41.7%→91.7% single-run agreement, RISK↔FAIL drift→0).

**Per-`item_type` legs** (HARD = absent⇒FAIL · SOFT = absent⇒RISK):
- **db_access** — HARD: every processing-referenced table present with op + projection; each projected column has data-type AND nullability; PK per table; IF a write op → transaction boundary. SOFT: FK for join keys; enum-domain (status/flag); range (numeric); index/concurrency note.
- **api** — HARD: request schema (every input); typed success response; error responses + HTTP status codes; an endpoint exists for every action the design defines. SOFT: endpoint-level auth when a screen-level precondition exists; committed (non-"example") contract.
- **state_workflow** — HARD: status set present/closed; every allowed transition states trigger+actor+data-effect; **invalid-transition handling explicit** (guarded); every action verb has a transition/endpoint. SOFT: terminal-state declaration; cancel/return/resubmit/rollback paths.
- **completeness** — HARD: every error/abnormal condition enumerated from the named § has a message id AND a designed counterpart; every in-scope item (§1) has a design. (no SOFT — a defined validation with no message ⇒ FAIL).
- **consistency (within/cross)** — HARD: no contradictory duplicate; no one-concept-two-literals; no violated exclusion. QUESTION if a cross-doc baseline is out-of-scope/un-openable.
- **risk** — HARD: each stated hazard has a named control step OR an explicit acceptance-owner + basis. SOFT: a control present but advisory/modal ⇒ RISK. (no control AND no owner ⇒ FAIL).
- **permission_security** — HARD: an auth precondition stated; an authz boundary for EVERY mutating action. SOFT: session-handling detail; authz for read-only endpoints.
- **ambiguity** — (no HARD). SOFT: each implementer-needed value (format/threshold/unit/timezone/boundary) has a measurable definition ⇒ any undefined value ⇒ RISK (not FAIL).
- **traceability** — HARD: every VAL maps to a step AND a message (a VAL with neither ⇒ FAIL); a consolidated matrix exists OR every VAL is traced inline. SOFT: VAL→BR/req leg; matrix-vs-inline form (partial trace ⇒ RISK).
- **testability** — HARD: every behavior has an observable, deterministic expected result (a behavior with none ⇒ FAIL). SOFT: derivable boundary/error cases; named test-data/preconditions for a dependency ⇒ absence ⇒ RISK.
- **process** — HARD: revision history + status field present. SOFT: a forward revision plan when pre-approval.

## Anti-weakening exclusion guard
High-severity / security / DB / state-transition / permission / governance items may **NOT** be auto-excluded. They may be `N/A` only on an **explicit `n_a_condition` match (cite it)** or **HUMAN confirmation**. An inferred "not applicable" is recorded as a visible `NOT_CHECKED` (or `CANDIDATE-EXCLUDE` pending confirm) — never silently dropped.

## Completeness honesty + headline derivation
The headline is **machine-derived** from the per-item verdicts (each item in exactly one bucket; counts sum to the selected total), by precedence:
```
headline = FAIL              if any selected non-N/A item is FAIL
         else RISK/CONDITIONAL if any selected non-N/A item is RISK
         else INCOMPLETE       if any selected non-N/A item is QUESTION or NOT_CHECKED
         else PASS
```
A global `PASS` is **forbidden** while any selected non-`N/A` item is `FAIL` / `RISK` / `QUESTION` / `NOT_CHECKED` — a recorded production `RISK` can never hide under `PASS`. The summary carries the full `PASS/FAIL/RISK/QUESTION/N/A/NOT_CHECKED` counts + an **INCOMPLETE** flag if any selected item is `NOT_CHECKED`.

**Findings invariant (every non-PASS is traceable).** Every item whose verdict ≠ `PASS` (`FAIL` / `RISK` / `QUESTION` / `NOT_CHECKED`) MUST emit exactly ONE Findings row carrying `Related Runtime Item` + `Source Checklist Item` + the per-item reason — so `#findings == #non-PASS verdicts` and no flagged item is lost between per-item reasoning and the findings list (a `RISK`/`FAIL` that stays only in per-item reasoning, never surfaced as a finding, is a defect of the run).

## Ensemble (high-stakes review) — the reproducibility multiplier
Run the checklist **k≥3 (default 5) independent times**; resolve each item by **majority vote** of the verdict token; **union** the findings for recall (a defect flagged by any run is surfaced). Flag any item with **no clean majority** as **`contested → escalate to HUMAN`** (these are genuine 3-way splits the leg-classified rubric could not pin). The leg-classified rubric reaches ~100% clean majority under 3-of-5; ensemble lifts residual single-run noise and is the complement to the rubric, not a substitute.

## Doc-type applicability + method positioning
- **What this method is (positioning).** The breakdown + verdict rubric deliver **reproducibility, traceability, and mechanical/structural coverage** — same inputs → same verdicts run-to-run, every finding traced to an item. They are **NOT** a recall/correctness guarantee.
- **Cross-document designs** (a target reconciled vs RD / OVERALL / sibling functions — e.g. a basic design): the full method (this asset + a cross-doc review plan = forced interface-contract field-diff + the entity-column read/write map in `consistency (cross_document)`) is the **validated mechanical-recall lever** — it surfaces orphan columns, ID collisions, CRUD/payload mismatches that free reading misses.
- **Dense single documents** (reviewed largely on their own — e.g. a detailed design): the per-item checklist is a **reproducibility lever, NOT a recall lever — and can REDUCE mechanical recall vs free reading** (the dense per-item pass constrains the reviewer). For such docs prefer a **HYBRID: a free-read recall pass + a checklist reproducibility/coverage pass**, or a project-specialised dense-doc checklist. Do not present the generic breakdown as maximising recall on dense docs.
- **Deep-logic / business-rule / semantic-contradiction recall is OUT-OF-METHOD** — reasoning-bound (gated by model capability + project review depth), not delivered by checklist/plan structure. Treat it as a separate (model/human) concern.

---

## METHOD TEMPLATES

> **VERDICT AUTHORITY — read first.** The numbered steps below are the **METHOD** (what to enumerate/check). Assign every item's verdict **TOKEN ONLY** via the `## Verdict rubric — LEG-CLASSIFIED` + the per-`item_type` HARD/SOFT legs (above) — each template's `Verdict:` line restates its legs. Do **NOT** pick a token by feel or from prose: HARD leg absent ⇒ **FAIL** · SOFT leg absent/advisory ⇒ **RISK** · QUESTION/N·A per the rubric · else **PASS**.

### `db_access`
1. Enumerate every table named in the processing steps [cite the steps].
2. Locate each in the DB-access section; confirm an operation + a projection (columns).
3. Per **projected** column require: data-type AND nullability; PLUS enum-domain IF the column carries status/flag semantics; PLUS range IF numeric.
4. Require a PK per table + an FK for each join key used.
5. IF any write op (INSERT/UPDATE/DELETE) → require a transaction boundary; ELSE transaction = **N/A with basis** (cite the read-only statement).
6. Require an index / concurrency note where multi-row reads or overlap checks occur.
- **Verdict:** leg-classified rubric — **HARD**: every processing-referenced table present w/ op + projection; each projected column type+nullability; PK per table; write op ⇒ transaction boundary. **SOFT**: FK for join keys; enum-domain; range; index/concurrency note.

### `api`
1. Endpoint `path + method` is **committed** (not an example / "vd").
2. Request schema lists **every** input by name + type + required [cross-map the input-field section].
3. Typed success-response schema present.
4. Error responses + HTTP status codes present.
5. Endpoint-level auth/authz stated.
- **Verdict:** leg-classified rubric — **HARD**: request schema, typed success response, error responses + HTTP status codes, an endpoint for EVERY action the design defines. **SOFT**: endpoint-level auth when a screen-level precondition exists; committed (non-"example") contract.

### `traceability`
1. List every requirement/BR/VAL/MSG/processing-step id [cite §§].
2. Build the mapping.
3. Flag any id with no counterpart (a VAL with no source BR/req, a BR with no impl, an MSG with no trigger).
4. Check a **consolidated** cross-reference matrix exists.
- **Verdict:** leg-classified rubric — **HARD**: every VAL ↦ a Step AND a Message (a VAL with neither ⇒ FAIL); a consolidated matrix exists OR every VAL is traced inline. **SOFT**: the VAL→BR/req leg; matrix-vs-inline form (partial trace ⇒ RISK).

### `consistency (within-doc)`
1. Extract the term/field/status/row set under review [name the §].
2. Pairwise-compare every occurrence.
3. A duplicate row with conflicting content, or one concept under two literals, is a **contradiction**.
4. **Cross-check any "does NOT access / does NOT use X" claim against what the processing/DB steps actually reference** (a stated exclusion that the steps violate is a self-contradiction).
- **Verdict:** leg-classified rubric — **HARD**: no contradictory duplicate; no one-concept-two-literals; no violated exclusion claim (any contradiction ⇒ FAIL).

### `consistency (cross_document)`
1. Extract shared terms / fields / status / IDs / behaviors.
2. Open the **named** baseline § (verify against the actual baseline docs).
3. Diff: a value the target **contradicts** or **under-implements** vs the baseline is a defect; a shared ID that means a **different** thing across docs is a collision.
4. **Entity-column read/write map (cross-doc obligation — the validated mechanical-recall lever).** Enumerate EVERY entity-column the target reads / writes / displays as a CLOSED list; cross-check each against the canonical data-model (OVERALL): *defined there? written by some step? read-but-never-written / undefined (orphan)?* An orphan or undefined column is a defect. This is **in addition** to the named producer→consumer edge field-diffs, and is the cross-doc lever that surfaces orphan columns / CRUD-vs-data-model mismatches free reading misses.
- **Verdict:** leg-classified rubric — **HARD**: no contradiction / under-implementation / ID-collision vs a named baseline; **no orphan/undefined entity-column** (a column read/displayed but never written, or absent from the OVERALL data-model). **QUESTION** iff a genuinely-needed baseline is out-of-scope/un-openable (emit an Open Question — never silent PASS).

### `risk`
1. Name the dimension (concurrency / performance / dependency / observability / security).
2. Locate the document's handling + its trigger.
3. **Objective concreteness test:** the handling names a specific step/check/lock by id AND its exact trigger; for residual risk, an explicit owning function + acceptance basis.
- **Verdict:** leg-classified rubric — **HARD**: each stated hazard has a named control step OR an explicit acceptance-owner + basis (no control AND no owner ⇒ FAIL). **SOFT**: a control present but advisory/modal only ("nên/should/may", no named step) ⇒ RISK. (A by-design deferral to a named owning function with a stated basis is a legitimate PASS.)

### `completeness`
1. Enumerate the universe from the named § **and from the baseline that mandates it** — in particular, enumerate **every shared validation the system baseline requires** (e.g. duration, advance-limit, working-hours, capacity) and every input / flow / error-case / state.
2. Check each member has a designed counterpart at a cited locus.
3. FAIL lists each uncovered member.
- **Verdict:** leg-classified rubric — **HARD**: every enumerated error/abnormal condition has a message id AND a designed counterpart; every in-scope item (§1) has a design (a baseline-mandated validation / defined rule with no counterpart ⇒ FAIL). (no SOFT — completeness is hard.)

### `ambiguity`
1. From the named §, list each value / threshold / format an implementer needs (grace values, limits, units, timezone, enum domains).
2. Check each has a measurable definition at a cited locus; an open-issue/TBD value counts as undefined.
- **Verdict:** leg-classified rubric — (no HARD) **SOFT**: each implementer-needed value has a measurable definition ⇒ any undefined value ⇒ **RISK** (never FAIL, unless it also breaks a HARD leg of another check).

### `permission_security`
1. Actor / role list.
2. Auth precondition + session handling.
3. Authz boundary per action.
- **Verdict:** leg-classified rubric — **HARD**: an auth precondition stated; an authz boundary for EVERY mutating action. **SOFT**: session-handling detail; authz for read-only endpoints.

### `process`
- Per check, cite the specific convention clause it tests (template section list / naming-numbering pattern / required revision-history columns / approval-field rule / config-vs-hardcode rule).
- **Verdict:** leg-classified rubric — **HARD**: revision history + status field present. **SOFT**: a forward revision plan when status is pre-approval. (Pre-approval `Reviewed/Approved = TBD` is acceptable iff status is pre-approval AND a revision plan exists.)

### `state_workflow`
1. Enumerate the **status set** from the named status/state §/table [cite] — closed universe.
2. Enumerate the **allowed transitions** `from→to`; for EACH require a **trigger**, an **actor/role**, and the **data update** (fields/records changed) [cite the row].
3. For each action verb (submit/approve/reject/return/cancel…): is there an explicit **invalid-transition handling** (rejected/error path) when invoked on a status where it is not allowed (e.g. approve an already-Approved/Cancelled request)?
4. Each terminal status is declared terminal; each non-terminal has ≥1 outgoing transition; cancel/return/resubmit/rollback paths present where the domain implies them.
- **Verdict via the leg-classified rubric** (HARD = status set closed · trigger+actor+data-effect per transition · invalid-transition handling explicit · an action verb with no transition/endpoint; SOFT = terminal-state declaration · cancel/rollback paths). **N·A** only on an explicit no-stateful-entity statement or HUMAN confirm (guarded — else visible `NOT_CHECKED`).

### `testability`
1. Enumerate the **behaviors/rules/validations** needing coverage from the named §§ [cite] — closed universe = the design's stated behaviors / VAL / BR.
2. Each behavior has an **observable, deterministic** expected result (a concrete output/state/message id), not "works correctly / validates appropriately".
3. normal + validation/error + boundary cases derivable; role/status variations specified enough to write a case; DB/API/external-dependency test points + required **test data/preconditions** (stub/contract for an external system, and its failure behavior) named.
- **Verdict via the leg-classified rubric** (HARD = every behavior has an observable expected result; SOFT = derivable boundary/error cases · named dependency test-data/preconditions). **QUESTION** if a needed dependency contract is only in an out-of-scope source. **N·A** if the document type is not intended to support testcase creation (cite scope).

---

## Pairing rule (warning ↔ empty-state)
When the target defines a **non-blocking warning** rule (an item flagged but not removed), the reviewer MUST also check that no message/edge-case elsewhere describes that same condition as a **filter/empty-result** — a warning rule plus an "empty due to that filter" message is a contradiction (route to `consistency (within-doc)` → FAIL). This catches the common "warn-only vs filter" drift on optional filters.
