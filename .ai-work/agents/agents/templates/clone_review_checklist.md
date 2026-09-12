# Clone Memory Review — checklist (AP-CR-28 / FR-AI-11)

After `/aiws-agent-clone`, the carried-over confirmed memory is flagged `clone_review: pending` (+ `cloned_from`).
The HUMAN keeps or prunes each entry **for the NEW project** via `/aiws-agent-review-learning` — nothing is silently
dropped or auto-confirmed. Run `py tooling/run_agent.py memory <new_id> --full` to see the flagged entries.

## Per-entry decision (for each `clone_review: pending`)
- [ ] **Keep** — still true/useful for the new project → clear the `clone_review` flag (entry stays confirmed).
- [ ] **Prune** — source-project-specific / no longer applies → remove the entry.
- [ ] **Re-scope** — keep but adjust `applies_when` / `scope_tags` for the new project's context.

## Guardrails
- Decide per entry by relevance to the **new** project — do not bulk-keep blindly (the value of a clone is a *curated* baseline, not a verbatim copy).
- `confirmed_by` stays `HUMAN`; no auto-confirm. Lineage (`cloned_from`) is retained for kept entries.
- Pruning here does not touch the source instance (clone is independent).

## Warm-start default (DP-913-C — CR-AIWS-2026-07-017)

Clone + prune IS the sanctioned warm-start path for a new same-role instance: clone from the
nearest same-role instance, then keep/prune each `clone_review: pending` entry via
`/aiws-agent-review-learning` — per relevance for the NEW project, no bulk-keep. This reuses the
existing AP-CR-28 gate; do not build a separate seed mechanism unless clone proves too coarse in
practice (gated follow-up in CR-017).
