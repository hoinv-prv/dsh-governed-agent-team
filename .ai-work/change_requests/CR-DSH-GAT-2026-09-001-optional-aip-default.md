---
cr_id: CR-DSH-GAT-2026-09-001
title: "Make AIP use optional by default for this project"
request_type: process_update
change_type: governance_rule
requester: hoinv
reviewer_or_product_owner: project_owner
status: draft
created_at: 2026-09-26
needs_human_confirmation_after_draft: true
driving_source: "Human request on 2026-09-26"
related_cr: []
---

# Local change request — optional AIP default

## Context

The installed AIWS core rules currently require an AIP before a substantive task. The project owner requests a different local operating default: agents should not require or create an AIP by default; the project owner will request one when it is needed.

## §1 Request identity

- Scope: this repository’s project-owned SOP.
- Relationship to upstream: the matching change to the installed, package-owned AIWS core rules is requested separately in `IR-2026-09-26-optional-aip-default.md`.

## §2 Target

| Path | Class | Requested action |
|---|---|---|
| `.ai-work/truth/SOP_MASTER.md` | Project Truth, CR-required | Seed the project’s default execution policy. |

No package-canonical file is a local apply target.

## §3 Requested change

Seed `SOP_MASTER.md` with this policy:

> AIPs are optional by default. Do not require or create an AIP solely because a task is substantive or non-trivial. Create or use an AIP only when the Human explicitly requests it or an explicitly approved, task-specific project process requires it. Other applicable approval gates, including CR approval before Truth changes, remain in force.

Expected outcome: normal repository tasks can be handled directly; AIPs remain available when the Human or an accepted process calls for them.

## §4 Source basis

- Direct Human request: “Please update AIWS.md and SOP so that it is not required to use AIP for tasks in this repo as default. I will for AIP when required.”
- Current installed core rules: `.ai-work/AIWS.md`, `Execution policy`, requires an AIP before non-trivial work.
- `.ai-work/truth/SOP_MASTER.md` is currently empty.

## §5 Proposed update direction

Apply only the quoted SOP policy. Do not alter `AI_WORK_CONTRACT.md`, methodology, tooling, or package contents in this repository.

## §6 Guardrails

- Apply only after project-owner approval and an explicit request to apply this CR.
- Preserve CR approval for Truth changes; making AIPs optional must not weaken it.
- Do not modify `.ai-work/AIWS.md` locally; that file is package-owned. Use the linked upstream request for a core-rule change.

## §7 Maturity / grounding

The requested policy is a deliberate Human decision, not an inference from existing AIWS methodology.

## §8 §15 propagation checklist

N/A — this change does not alter the AIWS wiki node model or a validated vocabulary.

## §9 Governance note

This CR concerns only project Truth. The upstream IR is not an approval to alter package-canonical AIWS content.

## §10 Alternatives weighed

- Keep the installed AIP-mandatory core policy: rejected by the project owner.
- Locally rewrite package-owned `.ai-work/AIWS.md`: rejected because this repository is an AIWS consumer.
- Record a project-level SOP override and ask upstream to make the core policy configurable: selected.

## Revision History

- 2026-09-26: Drafted from the project owner’s request.
