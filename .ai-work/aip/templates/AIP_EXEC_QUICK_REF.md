# AIP_EXEC Quick Reference

Quick checklist for authoring AIP_EXEC files. Read this before writing.
Full spec: `product/methodology/ai_work_system/20_specs/AIP_Detail_Spec_MVP.md` §6.3 + §7.

---

## Required sections for aip_exec (§6.3)

1. `## Objective`
2. `## Execution Scope` — with `### In Scope` + `### Out of Scope`
3. `## Expected Outputs`
4. `## References to Read First`
5. **`## Execution Steps`** ← exact name — **NOT** `## Steps` or anything else
6. `## Current Risks / Constraints`
7. `## Done Criteria`
8. `## Self-check / Review Points` (or `## Finalization Notes`)
9. `## Re-plan Rule`
10. `## Re-plan Log`

> **Optional (CR-AIWS-2026-05-030 / -032):** `## Selected Task Lens / Mode` — record the Task Lens (or No-Lens) that shapes which `source_types`/`reference_types` to reference (Required Wiki Inputs + References) and the ASC reading-surface order. Add **Resolved references** (subject + standards filled at create time — AI inference ∪ lens) and **Deferred lookups** (doc + lens for aiws-aip run to resolve). The lens is an **ADDITIVE** hint — AI inference is primary; inputs = inference ∪ lens, never lens-only/filter. Consult presets in `.ai-work/wiki/task_lens_presets/`. `lint_aip` does **NOT** require this section.

---

## Step format (§7 — all fields required)

```
### Step: STEP-01 — <title>

Objective:
<what this step achieves — 1–3 sentences>

Recommended Mode:
Executing | Reviewing | Clarifying | Canonical-edit

Applicable Guidelines:
- <path/to/guideline>  OR  wiki:none

Recommended Skills:
- <skill-name>  OR  (none)

Inputs:
- <file paths or context needed>

Expected Outputs:
- <concrete, verifiable deliverables>

Done Condition:
<verifiable criteria — grep check, file exists, lint pass, etc.>

Notes / Constraints:
<constraints, gotchas, what NOT to do>

Workspace Actions:
- <what to write to workspace files>
```

**Rules for step format:**

- Field names must be on their own line followed by `:` — NOT bold inline (`**Mode:** Executing` ❌)
- STEP numbering must be sequential — no gaps (STEP-01, STEP-02, STEP-03...)
- Use `wiki:none` in Applicable Guidelines to confirm explicit opt-out from wiki lookup
- **Exception — the two single-line optional fields `Difficulty:` and `Kind:` may carry their value inline** (`Kind: code, review`) or on the next line; both parse (CR-AIWS-2026-08-127 C9). Every other field: label alone on its line, value below.

---

## Common mistakes

| Wrong                                                       | Correct                                                                |
| ----------------------------------------------------------- | ---------------------------------------------------------------------- |
| `## Steps`                                                | `## Execution Steps`                                                 |
| `**Mode:** Executing`                                     | `Recommended Mode:` on its own line, then `Executing` on next line |
| STEP-01, STEP-02, STEP-04 (gap at 03)                       | Sequential: STEP-01, STEP-02, STEP-03                                  |
| Copy governance comment from another AIP                    | Write Governance Note specific to this AIP                             |
| Report "AIP done" without running lint                      | Run lint first → 0 errors                                             |
| Vague `## Self-check` step                                | Explicit checklist + mandatory lint invocation                         |
| `## References to Read First` missing (using custom name) | Always include exact `## References to Read First` section           |

---

## Authoring gotchas

Recurring authoring-time traps that each cost real rework — each is invisible until `lint_aip` runs (or until an unnecessary edit is made). Check these before writing.

### `Applicable Guidelines:` — bare root-relative paths only, no markdown links

Step `Applicable Guidelines:` entries must be **bare root-relative paths**:

- ✅ `product/wiki_guidelines/core/specs/WIKI_CHANGE_REQUEST_SPEC.md`
- ❌ `[WIKI_CHANGE_REQUEST_SPEC](../../../product/wiki_guidelines/.../WIKI_CHANGE_REQUEST_SPEC.md)`

A markdown link fails `lint_aip` `ref_missing` — lint resolves a bare path token, not a link. (Observed: 18× `ref_missing` from link-style refs in one AIP.)

**HARD-GATE steps need a wiki path.** A step whose Recommended Mode/title makes it a HARD GATE must list at least one path under `product/wiki_guidelines/` or `.ai-work/wiki/` (or the `wiki:none` opt-out) to satisfy `lint_aip` `wiki_first_preflight_at_hard_gate`. A `product/methodology/...` path does **NOT** satisfy it (methodology specs aren't wiki entries).

### Don't scope a build-package edit to "ship a file" in a wholesale-copied payload section

When an AIP (esp. an apply-CR AIP) adds a **new file** under a payload section that the install builder copies **wholesale/recursively** — e.g. `product/wiki_guidelines/`, `product/aip_templates/` (`build_aiws_install_package.py` `PAYLOAD_SECTIONS` + `copy_tree_filtered`) — the file **auto-ships** with **zero** build-tool change. Do **not** add a `aiws-pkg build` SKILL/script edit to the AIP scope just to "ship" it; that over-scopes the CR and adds an unnecessary apply step. First confirm the section is wholesale-copied — a file added to a section the builder enumerates file-by-file would still need wiring. (Precedent: CR-AIWS-2026-06-018 Apply Outcome (e).)

### Step field labels must start at column 0

Required step field labels (`Objective:`, `Recommended Mode:`, `Applicable Guidelines:`, `Inputs:`, `Expected Outputs:`, `Done Condition:`, …) must begin at **column 0**. An indented label (e.g. 2 spaces, so it renders as a continuation of the preceding bullet list) is reported by `lint_aip` as **`step_field_missing`** even though the field is present — its field regex is anchored at column 0. (Observed: ~60 false `step_field_missing` in AIP-084/087.) Fix = move the label to column 0. (A clearer lint diagnostic for this trap shipped via CR-AIWS-2026-06-029 / AIP-EXEC-121.)

---

## Lint quick check (run before reporting "AIP done")

```bash
py .ai-work/tooling/lint_aip.py --path .ai-work/aip/exec/<aip-file>.md
```

0 errors = format correct.

---

## Frontmatter required fields (aip_exec)

```yaml
artifact_type: aip_exec
artifact_id: AIP-EXEC-NNN
title: <title>
status: draft
project: <project-name>
owner: <optional>
plan_source: <AIP-PLAN-NNN — description">
updated_at: YYYY-MM-DD
```
