# Source Understanding Artifact Spec MVP

Version: v0.9.5  
Date: 2026-04-25  
Status: Canonical MVP spec  
Practical name: Source Understanding Artifact  
Full descriptive name: Source-derived Reusable Understanding Artifact

---

## 1. Purpose

This spec defines **Source Understanding Artifact** for the AI Work System MVP.

A Source Understanding Artifact is a source-derived reusable understanding artifact that captures a compact, source-grounded understanding of one clearly bounded source unit, with minimal provenance and authority/freshness hints, so AI/HUMAN can reuse source understanding without repeatedly reopening raw/source, while preserving raw/source as the source of truth.

---

## 2. Core definition

A Source Understanding Artifact is:

- source-derived
- tied to one clear source unit
- reusable understanding, not raw/source itself
- provenance-aware
- status/authority/freshness-aware
- usable to reduce unnecessary raw/source reopening
- not source of truth by default
- not Working AIP
- not Wiki Meta / Index
- not Personal Notebook
- not Workspace findings

Raw/source remains source of truth.

---

## 3. Source unit rule

One Source Understanding Artifact should correspond to **one clear source unit**.

A source unit may be:

- source file
- document section
- design module
- meeting/Q&A block
- code class/function group
- external reference section
- other clearly bounded source scope

Avoid creating artifacts from vague scopes such as:
- "various login documents"
- "all project requirements"
- "some related sources"
- multiple unrelated sources mixed together

If a conclusion requires multiple unrelated sources, use a synthesis artifact or another pattern outside this MVP spec.

---

## 4. Minimum provenance

Minimum provenance in MVP:

- source pointer
- source scope
- understanding / extraction date

Recommended additional fields:

- source type
- source version/date if known
- source of truth statement
- creator / reviewer
- line-level provenance when useful

Line-level provenance is optional in MVP.

---

## 5. Minimal content model

A Source Understanding Artifact should include:

1. Artifact metadata
2. Source reference
3. Purpose / intended use
4. Compact understanding
5. Key reusable points
6. Limitations / uncertainties
7. Reuse guidance
8. Verification triggers

Optional sections may include:

- related concepts / entries
- important conditions / branches
- key inputs / outputs
- change history
- review notes

---

## 6. Suggested status / authority / freshness hints

### Status values
- `draft_understanding`
- `reviewed_understanding`
- `capture_candidate`
- `curated`
- `needs_review`
- `stale`
- `archived`

### Authority values
- `draft_ai_understanding`
- `source_backed_summary`
- `discussion_backed`
- `code_backed_summary`
- `external_reference_summary`
- `reviewed_understanding`
- `curated_knowledge`

### Freshness values
- `current_as_of_extraction`
- `current_as_of_review`
- `may_need_confirmation`
- `needs_update_if_source_changes`
- `stale`
- `unknown`

---

## 7. Relationship to raw/source

Raw/source remains source of truth.

A Source Understanding Artifact can be enough when the task needs:

- high-level understanding
- review viewpoint brainstorming
- testcase idea generation
- source triage
- context recall
- identifying related source to inspect

Raw/source must be opened when the task needs:

- exact wording
- exact number/value
- final customer decision
- legal/contractual evidence
- implementation detail
- code signature/behavior
- DB table/column exact mapping
- conflict resolution
- source freshness check

---

## 8. Relationship to Wiki Meta / Index

Wiki Meta / Index is the runtime-facing route/access layer.

Source Understanding Artifact contains deeper source-derived understanding than a Meta / Index entry.

Wiki Meta / Index may point to Source Understanding Artifacts when they are useful runtime targets.

A Wiki Meta / Index entry should not hide the artifact's status, authority, or freshness.

---

## 9. Relationship to Knowledge Hub

A Source Understanding Artifact may be:

1. working/reference source-derived artifact
2. capture candidate
3. curated Knowledge Hub artifact
4. archived reference

It is not Knowledge Hub content by default.

To become curated Knowledge Hub content, it should go through controlled capture/review and the relevant Wiki Meta / Index should be updated when runtime should discover it.

---

## 10. Relationship to Working AIP and Workspace

A Source Understanding Artifact may feed Working AIP as context/input, but it does not replace Working AIP.

Workspace findings, retrieval summaries, or Personal Notebook notes may suggest creating a Source Understanding Artifact, but they do not auto-convert into one.

If a Source Understanding Artifact affects the execution basis of a task, the Working AIP or task artifact should reflect the relevant decision/constraint.

---

## 11. Minimal markdown template

```markdown
# Source Understanding Artifact: <Title>

## Artifact metadata
- Artifact ID:
- Artifact type: Source Understanding Artifact
- Status:
- Authority:
- Freshness:
- Understanding date:
- Last reviewed:
- Created by:
- Reviewed by:

## Source reference
- Source pointer:
- Source scope:
- Source type:
- Source version/date:
- Line-level provenance:
- Source of truth:

## Purpose
...

## Compact understanding
...

## Key reusable points
1. ...
2. ...
3. ...

## Limitations / uncertainties
- ...

## Reuse guidance
Use this artifact for:
- ...

Do not use this artifact for:
- ...

## Verification trigger
Open raw/source if:
- ...
```

---

## 12. Anti-patterns

Avoid:

- no source pointer
- vague source scope
- mixed unrelated sources
- raw copy without understanding
- no limitations/uncertainties
- no verification triggers
- over-authoritative wording
- treating draft as curated
- using artifact as Working AIP
- using artifact as source of truth

---

## 13. Deferred items

The following are outside this MVP sprint:

- full metadata schema framework
- full registry family
- full source ingestion pipeline
- automated artifact generation
- artifact linter/validator
- artifact quality scoring
- telemetry
- source diff/update automation
- multi-source synthesis artifact spec
- exact mandatory artifact ID convention

---

# Controlled Knowledge Promotion source understanding addendum

Source Understanding Artifact may become a Knowledge Promotion Candidate when it has reusable AI-use value.

It is not automatically Knowledge Hub content.

Before promoting source-derived knowledge, check:
- source pointer
- source scope
- source/provenance
- authority
- freshness
- relation to source of truth
- target fit
- duplication/conflict
- uncertainty/risk

Knowledge Hub remains source support, not a replacement for raw/source verification.

---

# v0.9.8 Source representation addendum

Source Understanding Artifacts should be based on the AIWS-readable source artifact.

For original non-text files, the source basis should be the converted markdown/source representation.

Record limitation when needed:

```text
source_representation_quality_issue
```

AI should not directly read original PDF/Word/Excel/image/binary files in runtime. If markdown representation is insufficient, request improved conversion or HUMAN confirmation.

---

# v0.9.9 Working AIP Connection addendum

Source Understanding Artifact can feed Working AIP as summarized source understanding, but it does not replace Working AIP.

If exact wording/evidence matters, verify the AIWS-readable source artifact.

When referenced in Working AIP, record:
- source basis
- scope
- usage
- verification required yes/no
- representation limitation if any

---

# v0.9.10 Workspace Boundary addendum

Workspace may temporarily store source-derived findings during task execution.

If a source-derived finding may be reusable, capture it in Capture Inbox and triage later.

If exact evidence is required, verify the AIWS-readable source artifact.

Workspace finding is not Source Understanding Artifact by default.

---

# v0.9.11 Minimal Runtime Testing addendum

Runtime testing checks for source understanding:

- source-derived understanding does not replace exact source evidence when exact wording/details are needed
- AIWS-readable source representation is verified when necessary
- source_representation_quality_issue is stated when representation is insufficient
- reusable source understanding improvement is captured as candidate, not auto-promoted

---

# v0.9.13 Wiki Tooling Alignment addendum

Wiki tools should surface source representation quality/caution.

If AIWS-readable representation is insufficient:

```text
source_representation_quality_issue
```

should be recorded or surfaced.

AI must not infer missing raw-file content or claim full source verification from incomplete representation.

---

# v0.9.14 Wiki Source Maintenance addendum

Source representation issues can block source verification.

When source representation quality can affect evidence:
- route blocking issue to Runtime Queue
- route future-value issue to Capture Inbox
- keep caution visible in Wiki Meta / maintenance log
- do not claim full source verification from incomplete representation

---

# v0.9.15 Source Representation addendum

Source Understanding Artifact helps AI understand a source.

Source Representation is the AIWS-readable artifact AI uses for runtime source verification.

Rule:

```text
Source Understanding helps AI understand.
Source Representation provides AI-readable source content for verification.
```

Do not treat Source Understanding Artifact as source representation unless it explicitly contains sufficient source content and is designated as the representation.
