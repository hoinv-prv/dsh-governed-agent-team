# Problem Analysis — 5-Why / Root Cause (shared, pack-level)

> Added by CR-AIWS-2026-07-013. Role-AGNOSTIC (MAPPING_NOTE §4): PM agents root-cause schedule/issue
> problems; review agents may root-cause finding clusters (referenced lens, NOT a mandatory review
> step); coordinators may root-cause plan drift. PM packaging: `aiws_pm_agent/docs/reference_content/issue_resolution_process.md`
> + `aiws_pm_agent/output_templates/rca_report.md`.

## Process

1. **Problem statement** — ONE sentence, anchored to evidence (what happened, where, observed impact).
   No analysis yet. If the problem cannot be stated in one evidenced sentence → clarify first.
2. **Evidence table** — the facts: source (log/report/run/document + locus), what it shows. Facts only.
3. **5-Why chain** — ask "why" iteratively (typically ~5 levels, stop when actionable root reached).
   - BRANCHING allowed: one "why" may have several candidate causes — fork the chain per candidate.
   - **Fact/inference discipline (mandatory):** every "why" node is either anchored to an evidence
     row `[fact: E-n]` or explicitly tagged `[inference]`. A chain of untagged assertions is invalid.
   - Stop criteria: reached a cause the team can act on; or reached an `[inference]` that needs
     HUMAN/data to verify → that becomes an open question, not a conclusion.
4. **Root-cause candidates** — ranked by confidence (backed-by-facts first). State disconfirming
   evidence if any.
5. **Countermeasure options** — ≥2 options with trade-offs (fix-now / prevent-recurrence /
   accept-with-monitoring). Map each to the root-cause candidate it addresses.
6. **HUMAN decision request** — the agent PROPOSES; the HUMAN decides.

> ⚖ **governance_invariant** `advisory_rca` — RCA output is a proposal: the agent never declares an
> official root cause or applies countermeasures on its own; the conclusion is HUMAN-confirmed.

## Output
Use `aiws_pm_agent/output_templates/rca_report.md` (PM) or embed the same section structure in the
caller's report. Recurring root-cause patterns → `project_issue_pattern` learning candidate
(see `lesson_capture_rule.md`).
