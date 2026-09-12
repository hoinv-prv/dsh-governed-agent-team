# Runtime Review Methodology (MVP)

Status: Canonical methodology spec
Version: v0.1
Date: 2026-06-24
Source: CR-AIWS-2026-06-060 (lifts the review-reproducibility principle proven under CR-AIWS-2026-06-056 into a reusable methodology home)

---

## 1. Purpose & scope

This spec defines a **framework-independent methodology for making AIWS reviews reproducible** — *the same review inputs should yield the same verdicts run-to-run* — and honest about residual risk.

It applies to **any** AIWS review activity (design review, test-case review, spec review, artifact audit), regardless of which skill or executor runs it. The current operational **instance** of this methodology is the `aiws-runtime-review-checklist` skill (CR-AIWS-2026-06-053 / -056) and its co-located `runtime_review_breakdown_strategies.md` data asset; a future `aiws-review-plan` skill is expected to reuse the same methodology.

This spec documents the **principle, the mechanism, and the empirical basis**. It does **not** carry per-artifact operational data (e.g. the per-`item_type` HARD/SOFT leg sets) — that stays in the review skill's data asset. The spec is the *why/what*; the skill is the *how*.

---

## 2. Core stance

```text
Review reproducibility is a first-class quality goal, not a side effect.
```

Two stances follow:

- **Verdict determinism comes from data the AI follows, not from perception judgment.** A reproducible verdict is a *mechanical function* of objective legs at cited loci — never a "does this block implementation?" gut call (which drifts run-to-run).
- **Reproducibility is the success metric, not raw defect count.** The methodology's value is that two runs *converge* on the same verdicts and findings — not that a single run finds the most defects.

---

## 3. The three reproducibility layers

A review verdict is reproducible only if all three layers are pinned:

| Layer | What it pins | Mechanism |
|---|---|---|
| **(a) Which items are reviewed** | the closed universe of review items | = the artifact's own sections (no open-ended "review everything") |
| **(b) Which checks run per item** | the checks applied to each item | method templates (per `item_type`) |
| **(c) Which verdict each check gets** | the verdict token per check | the **leg-classified verdict rubric** (§4) |

Layer (c) — *verdict-per-check* — was empirically the **#1 source of run-to-run divergence** (§8): the same finding was scored `RISK` in one run and `FAIL` in another. Pinning (c) is the core lever of this methodology.

---

## 4. Leg-classified verdict rubric

Each method template expresses its decision as a set of **legs**, each tagged:

- **HARD** — its absence/contradiction ⇒ **FAIL**.
- **SOFT** — its absence, or presence only as advisory/modal ("nên / should / may", no named step) ⇒ **RISK**.

The verdict is a mechanical ladder over the legs (no perception verbs, no "blocks-implementation?" judgment):

```text
verdict = N/A      if an explicit n_a_condition / cited scope-out applies
                   (guarded categories: N/A only on an explicit match or HUMAN confirm)
        else QUESTION if a needed leg requires an out-of-scope (un-openable) source
        else FAIL    if ANY HARD leg is absent / contradicted
        else RISK    if ANY SOFT leg is absent, or present only as advisory/modal
        else PASS
```

The per-template HARD/SOFT leg sets are **instance data** authored in the review skill's data asset (not in this spec). Worked anchors from the proving instance: invalid-state-transition handling, defined-validation-without-message, stated-hazard-with-no-control-and-no-owner, and mutating-action-without-authorization are **HARD ⇒ FAIL**; an undefined value is **SOFT ⇒ RISK**.

Consolidating scattered per-template RISK/FAIL hints into **one mechanical ladder** is what stops a single locus from swinging PASS↔RISK↔FAIL across runs.

---

## 5. Ensemble protocol

For **high-stakes** review, the rubric alone is not relied on to be perfectly deterministic on a weak model. Run an ensemble:

- Run the checklist **k ≥ 3 (default 5)** independently.
- Resolve each item by **majority vote** of the verdict token.
- **Union** the findings across runs for recall.
- Flag any item lacking a clean majority as **`contested → escalate to HUMAN`**.

The **ensemble is the reproducibility guarantee**; the leg-classified rubric raises the single-run floor so that a clean majority is reached. The two are complementary — the rubric reduces variance at the source, the ensemble resolves the residual tail. **High-stakes review MUST run the ensemble.**

A project may lower `k` to 3 for cheap reviews; record the chosen `k`.

---

## 6. RISK-in-headline derivation

The headline status is machine-derived from the (ensemble-resolved) per-item verdicts:

```text
headline = FAIL        if any selected non-N/A item is FAIL
         else RISK      if any selected non-N/A item is RISK      (e.g. "RISK / CONDITIONAL-PASS")
         else INCOMPLETE if any selected non-N/A item is QUESTION or NOT_CHECKED
         else PASS
```

A clean `PASS` headline is **forbidden** while any selected non-`N/A` item is `FAIL`/`RISK`/`QUESTION`/`NOT_CHECKED`. This is **tightening-only**: it can only *downgrade* an over-optimistic headline, never upgrade one. Its purpose is honesty — a review carrying real production `RISK` items can no longer summarise as `PASS`.

---

## 7. Finding-trace convention

Every **non-`PASS`** verdict links a finding carrying:

- `Related Runtime Item: <runtime-item-id>`
- `Source Checklist Item: <source-item-id>`

so two runs are **diff-able** (compare run A's verdict on a given item against run B's). The finding uses **the caller's finding/severity convention** (e.g. a Task Workspace `04_findings.md`, or an agent pack's finding format on reuse) — never a hard-coded path. This keeps the methodology framework-independent.

---

## 8. Empirical basis

The methodology was validated by a controlled **2×2 re-test** (CR-AIWS-2026-06-056 §7; AIP-EXEC-166, 2026-06-24) — factors {flow: item-first vs region} × {rubric: prior soft tie-break vs leg-classified}:

- **Leg-classified rubric is the lever:** single-run verdict agreement rose **41.7% → 91.7%** holding flow constant (replicated in both flow legs), and **RISK↔FAIL drift fell to 0**.
- **Ensemble closes the tail:** both rubric arms reached **100% clean majority under a 3-of-5 ensemble**.
- **Review *flow* is NOT a reproducibility lever:** region-flow *cost* ~−16.7 pts single-run agreement with no recall payoff → it belongs to review *planning* (the future `aiws-review-plan` skill), not to verdict reproducibility.

**Honest caveats.** On a weak/fast model the single-run floor can sit around ~66.7% even with the rubric; that is why the **ensemble** (not single-run) is the mandated guarantee, with genuinely-borderline items resolved by the `contested → escalate to HUMAN` rule. The proving PoC was small-N (single fixture/domain) with designer-bias mitigations — directionally clear, not a statistical claim. Some by-design-accepted hazards (e.g. "last write wins") sit on a genuine strict-vs-lenient line that a future calibration may soften from FAIL to RISK.

---

## 9. Relationship to skills & specs

- **Operational instance:** `aiws-runtime-review-checklist` (CR-053/056) — `SKILL.md` + `runtime_review_breakdown_strategies.md` carry the per-`item_type` legs + the operational rubric. This spec is the methodology it instantiates.
- **Future consumer:** a `aiws-review-plan` skill (IR-2026-06-24) — review *planning* (coverage/region structure), distinct from verdict reproducibility; expected to reuse §4–§7.
- **Adjacent (distinct) specs:** `Minimal_Runtime_Testing_Stance_Spec_MVP` (testing stance) and `Runtime_Sanity_Checklists_MVP` (deterministic sanity guardrails). Review reproducibility is distinct from both.
- **Status set unchanged:** this methodology pins *how* the existing `PASS/FAIL/RISK/QUESTION/N/A/NOT_CHECKED` tokens are assigned and rolled up; it introduces no new token.

---

## 10. Measurement discipline (CR-AIWS-2026-08-003)

Rules for **measuring** review/agent quality — how to know a review process is actually better, not just busier. Normative for any AIWS quality measurement; numbers cited in Provenance are external reported evidence, not constants.

1. **Noise floor before A/B.** Trước khi so hai biến thể quy trình review, đo mức bất đồng lượt-với-lượt của CHÍNH quy trình (same input, same checklist, ≥2 lượt độc lập). Khác biệt A/B dưới noise floor → không kết luận.
2. **Hygiene gates ≠ coverage.** Gate PASS (format, evidence-binding, verdict đủ) đo chất lượng HỒ SƠ; nó không nói gì về phần khuyết tật KHÔNG được nêu. Muốn nói về độ phủ phải có mẫu đối chứng (known-defect set / error-injection — cf. `aiws-eval` meta).
3. **Denominators are mandatory.** Mọi tỉ lệ/gate đi kèm mẫu số tường minh; mẫu số 0 = NO-SIGNAL, cấm đếm như PASS.
4. **Pre-registration.** Khoá đơn vị/công thức/mẫu số TRƯỚC khi thấy kết quả; đổi giữa chừng = lượt đo mới.
5. **Pin tools mid-run.** Tool đo/gate không được sửa khi lượt đang chạy; đổi version phải công bố delta.
6. **Blind by CONTENT, not by name.** Danh sách CẤM-đọc cho lượt blind được phép nêu đường dẫn; cấm chứa nội dung hậu nghiệm (số khuyết tật, verdict, tên finding).
7. **A rule must patch its enforcing file.** Công bố một luật đo → cập nhật file/checklist thi hành trong cùng lượt; nếu không, luật chết ngay khi sinh.
8. **Hash the thing you are checking.** Phép kiểm hash phải hash chính vật đang kiểm và in cả hai giá trị cạnh nhau; cấm chép giá trị nguồn sang ô của bản sao. (Cùng lớp: fixture đối chứng phải có khả năng FAIL — "người kiểm ≠ người bị kiểm".)

**Provenance.** Rules 1–8 rút từ sự cố đo được của một AIWS deployment (demo PoC 2026-08, số liệu **reported**: đồng thuận verdict 2 lượt độc lập 62–65%; recall 50.0% = 17/34 ở một lượt qua 12 cổng xanh với precision 100%) và sự cố trong-repo (CR-AIWS-2026-06-054 — "một cờ cảnh báo chỉ có giá trị khi bước sau CLEAR được nó"; CAP-002 wave CR-051/053 — fixture tự chứng minh chính nó). Nguồn: `product/change_requests/intake/IR-2026-08-05-demo-agents-cr-inventory.md`.

---

## Revision History

| Date | Author | Change |
|---|---|---|
| 2026-08-05 | hoinv (AI-authored, AIP-EXEC-992 applying CR-AIWS-2026-08-003) | +§10 Measurement discipline (8 normative rules; demo numbers cited as reported evidence in Provenance). |
| 2026-06-24 | hoinv (AI-authored, AIP-EXEC-174 applying CR-AIWS-2026-06-060) | Initial canonical spec. Lifts the review-reproducibility principle proven under CR-056 (leg-classified HARD/SOFT verdict rubric §4 + ensemble §5 + RISK-in-headline §6 + finding-trace §7 + empirical basis §8) into a framework-independent methodology home reusable across review skills. Documents the principle + rationale; per-`item_type` operational data stays in the `aiws-runtime-review-checklist` data asset (CR-053/056). §15 N/A (prose spec — no node-model / validated-vocabulary change). |
