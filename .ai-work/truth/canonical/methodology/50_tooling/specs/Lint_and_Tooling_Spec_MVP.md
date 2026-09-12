# Lint and Tooling Spec for AI Work System MVP
Version: 0.2  
Scope: MVP only

---

# 1. Purpose

This spec defines:
- lint scope
- lint behavior
- severity model
- deterministic tooling responsibilities

This version aligns with **Wiki v1.0 freeze**, including:
- `Wiki Source Meta`
- `Wiki Source Index`
- lexical + semantic lookup support
- projection rule between index and meta

---

# 2. Core lint principles

## 2.1. Lint is guardrail, not reviewer
Lint should:
- detect
- report
- suggest minimal corrective action

Lint should not:
- deeply judge semantic truth
- rewrite official content
- replace human review

## 2.2. Deterministic-first support
Prefer:
- metadata checks
- section checks
- enum checks
- path checks
- projection consistency checks
- JSONL/Markdown parse checks

---

# 3. Lint target matrix

## 3.1. AIP
Check:
- metadata valid
- required sections
- step structure
- guideline/skill refs

## 3.2. Active Step Context
Check:
- source AIP exists
- step id exists
- required sections present
- linked pointers well-formed

## 3.3. Workspace
Check:
- required files
- queue/capture parse
- final output presence when done

## 3.4. Queue
Check:
- required fields
- enums
- duplicate ids
- question/why present

## 3.5. Capture Inbox
Check:
- required fields
- enums
- source refs recommended when promote-like targets exist

## 3.6. Official Wiki Entries
Check:
- required metadata
- required sections
- canonical refs
- next reads
- status handling

## 3.7. Wiki Source Meta
Check:
- identity fields
- summary present
- profile mapping present
- artifact reference present
- lookup keys surface present
- relation references well-formed if present
- meta remains within intended structure (not source dump)

## 3.8b. Capture close gate (`lint_workspace.py`)

Fires when the workspace's AIP frontmatter carries `status: done`, resolved via the
`.current_step.json` back-link and the workspace-folder-name fallback. Before CR-AIWS-2026-08-125 the
trigger was a hand-written brief line: measured across 573 briefs in three projects, **0** could match it,
so the whole gate body had never executed anywhere.

- `capture_untriaged_at_done` (**ERROR**) — the AIP says `done` and the workspace still holds rows with
  `status: captured`. Distinct from `capture_untriaged` (WARN, for a workspace not yet closed) rather
  than a severity change on it, so `lint_accept` entries and release-note lines can address each
  separately.
- `capture_deferred_without_pointer` (**WARN**) — a row with `status: deferred` and no `deferred_to`.
  Mirrors the existing `capture_refs` shape for `promoted` + `source_refs`: a disposition that names no
  destination cannot be acted on.

`final_missing` keeps its predicate. Note that it reports **0** both before and after the repair while
228 of 372 workspaces hold the shipped `11_output_final.md` template verbatim — the template is
pre-filled, so an untouched final output is a non-empty file. That zero is not coverage; the real check
lives at `aiws-aip run close`, which refuses while the file is still byte-identical to the template.

## 3.8c. Capture vocabulary (`lint_workspace.py`)

`candidate_kind` became a closed vocabulary of 15 values in CR-AIWS-2026-08-126. Before that it was not
validated at all: 66 distinct values across 709 in-repo records. All three codes are **WARN** — beat 1 of
the two-beat rule (CR-AIWS-2026-08-085), because 593 stored records carry a legacy value and none of them
is being rewritten.

- `capture_kind_legacy` (**WARN**) — a `candidate_kind` outside the vocabulary. The message names the
  replacement family when one is known, so the writer is not left picking a wrong-but-legal value.
  Namespaced project kinds (`<namespace>:<id>`) are accepted **by shape**: this linter must not need to
  read a project's config to be right.
- `capture_scope` (**WARN**) — `improvement_scope` outside `aiws | project`.
- `capture_correction_class` (**WARN**) — `correction_class` outside the five values.

`aiws_system_improvement` is **superseded, not legacy**: its records project onto
`improvement_scope: aiws` and are deliberately silent, because the CR forbids rewriting them and a
warning nobody may act on is noise.

## 3.9. Project profile (`project_profile.yml`)

Runs **unconditionally** in the whole-tree leg (CR-AIWS-2026-08-128 C6). Unlike a store that only
degrades when someone edits it, an incomplete profile degrades *continuously*: it gates system scoping
for every lookup, meta write and index build until it is fixed.

Check:
- `project_profile_unreadable` (**ERROR**) — the file exists but does not parse. It previously read as a
  healthy single-system project, so every guard fed by it went quiet with nothing to see.
- `project_profile_invariant` (**ERROR**) — a cross-key rule is broken. "Complete" is keys **and**
  invariants: `systems: []` under `multi_system: true` carries every required key and still disarms the
  check the pair exists to enforce.
- `project_profile_incomplete` (**WARN**) — a required key is missing. Softer on purpose: an install
  predating the schema is behind, not broken, and `project_profile.py refresh --apply` fixes it.

An **absent** profile is silent — that is a legitimate single-system project.

## 3.8. Wiki Source Index
Check:
- entry identity fields
- artifact locator present
- meta locator or meta id present
- profile id present
- short summary present
- lookup key projection present
- index entry does not embed full meta
- projection consistency with meta where possible

---

# 4. Severity model

## 4.1. Error
Must fix.

Examples:
- missing required section
- invalid enum
- broken canonical ref
- duplicate queue id
- source meta missing artifact locator
- source index entry missing meta reference

## 4.2. Warning
Should review.

Examples:
- status=needs_review
- source meta missing useful relations
- weak lookup_keys surface
- source index summary too vague
- source meta appears too large/heavy

## 4.3. Info
Helpful but not blocking.

Examples:
- no review hints in non-critical wiki entry
- no optional relation hints
- no optional semantic labels

---

# 5. Default lint profiles

## 5.1. MVP default
- structural lint
- reference lint
- metadata lint
- projection consistency lint (light)

## 5.2. Elevated profile
Allowed only on explicit user request:
- light semantic / consistency lint
- stricter wiki review
- deeper source/meta comparison

---

# 6. AIP lint summary

No major conceptual change from v0.1.

Checks still include:
- metadata
- required sections
- step fields
- guideline/skill refs

---

# 7. Workspace lint summary

No major conceptual change from v0.1.

Checks still include:
- required file presence
- queue/capture parseability
- completion sanity

---

# 8. Official Wiki entry lint

## 8.1. Metadata checks
Required:
- artifact_type
- entry_type
- artifact_id
- title
- knowledge_class
- use_rule
- status
- canonical_references
- last_verified_at
- updated_at

## 8.2. Section checks
Required:
- Purpose
- Scope
- Canonical References
- Recommended Next Reads

## 8.3. Warning checks
- source_of_truth with weak canonical basis
- needs_review entries
- weak next reads

---

# 9. Wiki Source Meta lint

## 9.1. Expected purpose
Meta should remain:
- small
- memory-friendly
- richer than index
- lighter than source artifact

## 9.2. Required metadata / identity
At minimum, source meta should support:
- `source_id`
- `title`
- `source_type`
- `artifact_locator`
- `profile_id`
- `status`

> **`source_type` validation is profile-driven** (CR-AIWS-2026-05-008 / IR-04). A `source_type`
> is valid if it is in the canonical base vocabulary **or** is declared by a shipped profile
> (`wiki_sources/profiles/*.yml` → `source_type:`). To add a project-specific type, declare it on
> a profile rather than hardcoding it in the linter — this keeps the linter in sync with the
> profiles a project actually ships.

## 9.3. Required content areas
Source meta should have at least:
- short summary
- knowledge target hints
- lookup keys
- profile mapping
- artifact pointer/reference

## 9.4. Optional but recommended
- relation hints
- source-specific hints
- change impact hints
- cautions

## 9.5. Warning conditions
- summary too long/heavy
- lookup keys absent or too weak
- lookup keys exceed the soft budget (default 40) — hygiene signal for curation; NOT a truncation (index projects keys losslessly — CR-AIWS-2026-07-037)
- intake frontmatter uses a value outside the closed vocabulary of `change_requests/intake/README.md` (`intake_frontmatter_offvocab` — CR-AIWS-2026-07-043)
- a canonical doc that SHIPS to target projects has no Wiki Source Meta (`canonical_doc_unregistered` — CR-AIWS-2026-07-043 §7): invisible to lookup
- a skill in `rename_map.json` `keep[]` has no invocable surface and is not declared `procedural_only` (`skill_keep_without_surface` — CR-AIWS-2026-07-044)
- relation fields malformed
- meta appears to include large raw source excerpts
- no useful distinction from index

## 9.5b. Lint scope — every meta namespace (CR-AIWS-2026-07-041)

Meta-lint and index-lint cover **every** meta namespace: the project's `wiki_sources/meta/` **and**
the shipped `wiki_sources/aiws_meta/` (+ `index.aiws.jsonl`). Index BUILD scope is unchanged.
In an INSTALLED project the AIWS namespace is read-only, so findings there are **downgraded to
warnings and never gate** — an upstream defect must not block a downstream task's finalize lint.

## 9.6. Error conditions (meta-level relations)
- Related Sources bullet not spec-shape or target unresolvable (`relations_edge_unresolvable` — CR-AIWS-2026-07-032)
- representation edge inverted: post-normalization source_ref of a `represents`/`describes` edge is a `node_kind: object` meta (`representation_edge_inverted` — CR-AIWS-2026-07-038; representation flows artifact → object)

---

# 10. Wiki Source Index lint

## 10.1. Expected purpose
Index is a lookup layer.
It should support:
- scan
- grep/exact lookup
- pointer to meta
- pointer to artifact

## 10.2. Required per-entry fields
At minimum:
- `source_id`
- `title`
- `source_type`
- `artifact_locator`
- `meta_locator` or `meta_id`
- `profile_id`
- `summary_short`
- `knowledge_targets`
- `status`

## 10.3. Required lookup surface
Index entry must contain a reduced lexical lookup surface:
- exact terms / aliases / identifiers / path tokens as appropriate

The lookup-key surface is projected **losslessly** from the meta (no positional cap — CR-AIWS-2026-07-037); §10.4's rule constrains embedding the full meta body, not the key list.

## 10.4. Critical projection rule
Index entry must **not** embed full meta.

## 10.5. Warning conditions
- no useful lexical keys
- summary too vague to confirm relevance
- index entry too large/heavy
- meta locator broken
- artifact locator broken

---

# 11. Projection consistency lint

Where possible, tooling should check light consistency between:
- source meta
- index projection

## Example checks
- matching source_id
- matching title or equivalent
- matching profile_id
- matching artifact locator
- overlapping lookup key surface

This is not full semantic equivalence checking.
It is just enough to detect obvious drift.

---

# 12. Tooling responsibilities

Tooling in MVP should support:
- building source meta
- building index projection
- looking up source by lexical/exact or simple search
- refreshing source meta
- linting wiki entries, source meta, and index

Tooling should not:
- silently rewrite official wiki
- act as semantic authority

---

# 13. Git-related clarification

Git may be used as an optional change signal during source change detection.

But lint should not require Git metadata in:
- official wiki entries
- wiki source meta
- wiki source index entries

Git is outside the meta contract.

---

# 14. Execution timing recommendations

Recommended lint moments:
- after creating/updating AIP
- after generating Active Step Context
- after creating/updating source meta
- after rebuilding source index
- before finalizing important wiki updates

**Finalize lint (CR-AIWS-2026-06-067):**
- **Task-execution finalize** → the **scoped** finalize lint `lint_all.py --scope task --workspace <ws> --aip <aip>` (mandatory AIP + Task-Workspace, conditional wiki/index, canonical auto-escalation). See §18.
- **Canonical / CR-apply finalize** → whole-tree `lint_all.py` (0 errors). The scoped driver auto-escalates to whole-tree on a `product/` or CR-apply footprint, so the same command is correct in both cases; and a CR still flips `applied` only after a clean whole-tree lint (CR Spec §13).

---

# 15. Conclusion

Lint in MVP now covers:
- official wiki entries
- wiki source metas
- wiki source index

while preserving the frozen design:
- index as projection
- meta as richer source context
- lexical + semantic lookup support
- no silent official rewrite.

---

# 9. Slim Meta/Index Lint Expectations — 2026-05-27 Addendum

**Source:** Applied from wiki_improvement_request.md (validated in vti-ai-work-system-demo, 2026-05-26).

## 9.1 Wiki Source Meta — updated expectations (supplements §3.7)

**Removed sections (lint must NOT flag as missing):**
`## Runtime Use`, `## Source Representation`, `## Change Impact Hints`,
`## Cautions`, `## Profile Mapping`, `## Artifact Reference`.

**Retained required sections:** `## Summary`, `## Knowledge Targets`, `## Lookup Keys`, `## Source-Specific Hints`.

**Blank frontmatter fields:** Lint must NOT flag absence of intentionally-omitted blank fields
(omit-blank pattern). Only flag if a field is present but has an invalid value.

## 9.2 Wiki Source Index — updated expectations (supplements §3.8)

**Fields no longer expected in index entries — do NOT flag as missing:**
- `meta_id` — removed permanently
- `updated_at` — removed permanently
- `knowledge_value` — removed permanently
- `intended_ai_use` — removed permanently

**Acceptable absence:** `original_source_locator` and `representation_locator` absence is acceptable
(omit-when-equal pattern).

**Lint may WARN** if `summary_short` looks like boilerplate:
`"Version: 0.1"`, `"artifact_type: guide"`, `"- (no summary extracted)"`.

---

# 16. Inline `lint_accept` — HUMAN-accepted findings (CR-AIWS-2026-06-065 Addendum)

**Source:** CR-AIWS-2026-06-065 (applied 2026-06-24 via AIP-EXEC-180).

A HUMAN may **accept** (mute) specific lint finding *codes* on a frontmatter-bearing file by adding a `lint_accept` block to that file's own frontmatter. Accepted findings are hidden by default and **excluded from the exit-code counts** — so a reviewed-and-accepted finding (e.g. a deliberately short `Summary` → `meta_summary_degenerate`, or a structural finding on an AIP accepted as-is) no longer keeps `/aiws-lint` red — while any *other* or *new* finding still surfaces, and the acceptance is **never silent**.

## 16.1 Scope (frontmatter-bearing files only)

`lint_accept` is honored only on files that carry frontmatter and lie under
`.ai-work/wiki_sources/meta/`, `.ai-work/wiki/`, or `.ai-work/aip/`.

Findings on non-frontmatter targets — workspace directories, JSONL files
(`02_runtime_queue.jsonl`, `08_capture_inbox.jsonl`, `index.jsonl`, `relations.jsonl`,
`maintenance_log.jsonl`), and `.meta.yml` — **cannot** be accepted (there is nowhere to carry
the block); they must be fixed.

## 16.2 Schema (per-code)

```yaml
lint_accept:
  - code: meta_summary_degenerate        # REQUIRED — exact finding code to mute
    reason: "Summary cố ý ngắn, đã review OK"   # REQUIRED — audit trail
    accepted_by: hoinv                    # REQUIRED — who accepted
    date: 2026-06-24                      # optional
```

- **Per-code, never whole-file:** an entry mutes exactly its `code` on that file; other/new findings still surface.
- `code`, `reason`, `accepted_by` are **required** on every entry.

## 16.3 Behavior + exit code

- An accepted finding is moved out of the error/warning counts that drive the exit code: an accepted ERROR no longer returns exit 2; an accepted WARNING no longer returns exit 1 under `--strict`.
- **Never silent:** the text summary shows `accepted=N` (when N>0) plus a hint; `--show-accepted` lists each muted finding with its `reason` + `accepted_by`. JSON output gains a top-level `accepted` array and `counts.accepted`.

## 16.4 Self-guard codes (never acceptable)

- `lint_accept_malformed` (**ERROR**) — an entry missing a required field, not a mapping, or attempting to accept a self-guard code. A malformed block mutes nothing and keeps lint failing.
- `lint_accept_unused` (**WARNING**) — an accept `code` matches no finding on the file (stale/typo'd accept).

Both are emitted by the accept post-pass itself and **cannot** be accepted away.

## 16.5 Reset on refresh (strip-on-refresh; no fingerprint)

A field-preserving rewriter that re-derives a meta's content (`refresh_wiki_source_meta.py`) **strips** the `lint_accept` block on rewrite, so an accept never silently outlives the content it was reviewed against — the HUMAN must re-review and re-accept. There is **no** content fingerprint.

**Known limitation:** strip-on-refresh resets only files that pass through a content-rebuilding rewriter — i.e. **metas**. **AIP files and wiki entries** have no canonical refresh tool, so their accepts reset only when a HUMAN removes the block (a manual edit does not auto-reset). Surgical metadata fixers that do not touch the accepted content's basis (e.g. `normalize_wiki_meta.py`, which only rewrites the `artifact_locator` / `authority_level` lines) intentionally do not strip; a locator fix that resolves the issue instead surfaces as `lint_accept_unused`.

## 16.6 Projection cleanliness

`lint_accept` is a lint directive only — it MUST NOT be projected into the slim Wiki Source Index (it is not in the index's projected field set; the index builder ignores unknown frontmatter keys).

---

# 17. Binary-by-design stub metas — `not_meta_applicable` text-meta exemption (CR-AIWS-2026-06-066)

**Source:** CR-AIWS-2026-06-066 (applied 2026-06-25 via AIP-EXEC-182). Origin: downstream-raised (Otsuka), formalized upstream.

Some source artifacts are **binary by design** — e.g. compiled/binary bodies (ASP `.DP1` DPS binaries, `.FFX` compiled FDG bodies, `.OVD` overlays), PDF object docs, image assets. They have **no text source body**, so a normal text-meta with a Summary / Knowledge Targets / Lookup Keys body and a `profile_id` cannot be derived without fabricating content. The recognized representation for such an artifact is a **stub meta** that carries `not_meta_applicable: true`.

## 17.1 Recognized flag

`not_meta_applicable: true` is a recognized boolean meta-schema flag marking a binary-by-design stub. A descriptive `artifact_kind: binary` MAY accompany it, but the **exemption gates only on `not_meta_applicable is True`** (`artifact_kind` is informational, not a gate).

## 17.2 Lint exemption (scoped)

For a meta with `not_meta_applicable: true`, `lint_wiki` exempts exactly the text-meta requirements such a stub intentionally cannot satisfy:

- **Frontmatter:** `profile_id` is NOT required (scoped carve-out from CR-AIWS-2026-06-004 C1, which otherwise requires `profile_id` on every meta).
- **Body sections:** the required `META_SECTIONS` (Summary / Knowledge Targets / Lookup Keys) are NOT required.
- **Index projection:** the index record's `profile_id` / `summary_short` / `knowledge_targets` are NOT required (kept in sync with the frontmatter exemption).

**Everything else stays required.** The identity fields — `source_id`, `title`, `source_type`, `artifact_locator`, `status` — remain mandatory even for stubs. A *normal* meta (no flag) that omits these sections/fields still errors. The exemption is strictly scoped to the flagged stub.

## 17.3 Index projection

`build_wiki_source_index` projects `not_meta_applicable: true` into the stub's index record **conditionally — only when true**. Because `_omit_blank` keeps `False`, an unconditional projection would bloat every record with `not_meta_applicable: false`; emitting the key only when true keeps normal records lean while letting the index linter apply 17.2.

## 17.4 Regression guard

A golden fixture (`tests/fixtures/wiki_corpus/metas_good/SRC-BINARY-stub-fixture.md`) is guarded by `_lint_golden_fixtures` so `/aiws-lint` fails if the exemption regresses; a negative fixture (`metas_broken/missing_sections.md`, registered in `test_wiki_regression.py` `sec_lint_negative`) proves a normal meta still errors on missing sections, and `sec_build_index` asserts the stub's record projects the flag.

---

# 18. Scoped finalize-lint driver — `lint_all.py --scope task` (CR-AIWS-2026-06-067)

**Source:** CR-AIWS-2026-06-067 (applied 2026-06-29 via AIP-EXEC-188).

`aiws-aip run` task finalization (Flow step 7) runs a **scoped** finalize lint instead of the whole-tree lint, so a task's finalize reports findings for **its own** AIP + Task Workspace (and wiki iff touched) rather than pre-existing ERRORs from unrelated AIPs/workspaces/wiki the task never touched. Selection is **deterministic and tool-driven** — `aiws-aip run` calls one command and does not judge which linters to run.

## 18.1 CLI

`python .ai-work/tooling/lint_all.py --scope {all,task} [--workspace <PATH>] [--aip <PATH|ID>]`

- `--scope all` (default) — whole-tree lint; unchanged byte-for-byte from the pre-CR behavior. The **canonical / CR-apply** finalize lint.
- `--scope task` — scoped finalize lint; **requires** both `--workspace <Task-Workspace>` and `--aip <active-AIP path or artifact_id>` (missing either → exit 2).

## 18.2 Deterministic behavior of `--scope task`

1. **Footprint** = git-changed paths in the working tree (staged ∪ unstaged ∪ untracked), via `git status --porcelain`.
2. **Mandatory legs** — lint the task's AIP (`lint_aip`) **and** Task Workspace (`lint_workspace`, incl. Step Output + Decision Trace deliverables). Both required; a broken own-deliverable blocks finalize.
3. **Conditional wiki/index leg** — if the footprint intersects `.ai-work/wiki/` or `.ai-work/wiki_sources/`, also run the wiki entry + source-meta + index + relations lint.
4. **Canonical escalation** — if the footprint intersects `product/`, **or** the AIP is an apply-CR AIP (`template_source` starts with `AIP_EXEC_APPLY_CR`), **escalate to the whole-tree lint** (which subsumes the mandatory legs — escalate-vs-scope is exclusive, no duplicate findings).
5. **Under-matched scope warning — `scope_task_footprint_unmatched` (WARNING; CR-AIWS-2026-08-065).** When the AIP DOES declare paths but none of them matches a dirty file, while `product/` is dirty, the run emits this warning against the AIP file. Rationale: that combination silently drops `product/` out of the footprint, so the run neither escalates nor reports anything — a clean-looking finalize over an unlinted canonical change (typical cause: an Expected Output naming a CR id that was not minted yet). It is **warn-only**: the footprint stays `git dirt ∩ declared` (no whole-dirt fallback, R3-09 intact) and no automatic escalation happens; the operator re-runs with `--footprint-paths <dir>` or declares the directory.

## 18.3 Guarantees

- **Whole-tree is the default and is preserved byte-for-byte** when `--scope task` is omitted.
- **CR-apply gate not relaxed** — a `product/` or CR-apply footprint auto-escalates to whole-tree, so a canonical task can never finalize on a scoped-only lint (CR Spec §13 is unchanged).
- **Output lint is mandatory** — `lint_workspace` is a required leg; a task cannot finalize while its own deliverable metadata is broken.
- **Multi-system safe (rule #12)** — footprint detection is path-only and the scoped driver performs no cross-system lookup, so no cross-system spec bleed.
- **`--strict` interplay (§16.3)** — exit-code semantics are unchanged: accepted findings are excluded from counts; under `--strict` a remaining warning returns exit 1, any error returns exit 2.

## 18.4 Regression guard

`.ai-work/tests/test_lint_scope_task.py` proves: (a) scoped lint touches only the named AIP + Task Workspace — an unrelated broken AIP is not reported (a whole-tree control proves it is detectable); (b) a `product/` footprint and an apply-CR AIP each escalate to whole-tree; (c) a broken Step-Output deliverable fails scoped lint; (e) declared paths matching no dirty file while `product/` is dirty raise `scope_task_footprint_unmatched` as a WARNING without escalating, and stay silent both when the declared paths do match and when no `product/` path is dirty. Default-path byte-identity is verified against the pre-edit whole-tree output.

# 19. Dual-tree drift check — `dual_tree_drift` (CR-AIWS-2026-07-030)

**Invariant guarded.** Every shippable surface exists twice (dual-tree): `product/**` (packaged source) ↔ its installed twin (`.ai-work/**` / `.claude/**`; methodology mirrors under `.ai-work/truth/canonical/`). History proved this invariant breaks silently in BOTH directions (mirror stale vs product — CR-066/067 era; installed stale vs product — CR-020/025 rename era; precedent re-sync: CR-064, drift recurred anyway).

## 19.1 Mechanism

- Module `check_dual_tree.py` — the pair map **derives from quick_install's `PAYLOAD_MAP`** (the single source of "what ships twice"); `methodology` maps from `product/methodology/ai_work_system`. Never duplicate the pair table by hand.
- Comparison is **EOL-insensitive** (DP-1): CRLF/LF differences are NOT drift; EOL normalizes gradually when a CR touches the file. Content difference → `dual_tree_drift`; a file on one side only, outside classified exceptions → `dual_tree_only_in_one`.
- **Classified exceptions** live in the module, in sync with CR-030 §2-A0: install-excluded methodology paths (`00_brainstorming/`, `90_delta_tracking/`, `Detail_Design_MVP_Core_Artifacts.md`); `wiki_source_profiles` installed-side extras (install = MERGE, CR-047); build-wired `skills/aiws-agent/SKILL.md`; documented content exceptions (each carries a pending-reconcile note).
- Runs as a leg of **whole-tree `lint_all`** (`--scope all`, and any scoped run that auto-escalates). On an **installed project** (no `product/` tree) the leg skips silently — zero fleet impact.

## 19.2 Severity & enforcement (DP-3)

Findings report **WARN** by default — drift caused by a parallel branch must not block unrelated work. Enforcement is at the CR gate: an **apply-CR AIP MUST reach `dual_tree_drift` = 0 on its own footprint** before flipping the CR to `applied` (CR Spec §13; APPLY_CR template Notes).

## 19.3 Regression guard

`.ai-work/tests/test_dual_tree_drift.py` proves: content drift is caught; identical and EOL-only pairs are silent; by-design only-in-product paths are silent; non-classified only-in-one is reported; an installed project (no `product/`) returns no findings.

# 20. CR-doc lint leg — `applied_without_apply_outcome` (CR-AIWS-2026-08-004)

**Invariant guarded.** CR Spec §16 status integrity: a CR with `status: applied` must carry an `Apply Outcome` section — the status field is the machine-readable record of the decision, and the outcome section is its mandatory evidence.

- Leg `lint_all._lint_change_requests` (whole-tree + escalated scoped runs) scans `product/change_requests/**/*.md`; files without a `cr_id` (intake/, drafts/, README) skip **by construction**; inline `status` comments tolerated; malformed frontmatter is another rule's finding. Installed projects (no `product/`) skip silently.
- Severity **WARNING** — a missing record is ledger debt, not a broken reference key. Legacy-by-design records are grandfathered via inline `lint_accept` **on the CR file itself** (`code`/`reason`/`accepted_by` — CR-065 schema; scope extended to `product/change_requests/` by this CR; single-line `reason` — the plain-YAML parser does not fold nested `>` scalars).
- Regression guard: `.ai-work/tests/test_cr_status_integrity.py` (A1..A6 + accept probe).

# 21. CR-id uniqueness — `duplicate_cr_id` (CR-AIWS-2026-07-071)

**Invariant guarded.** A `cr_id` must be unique **globally**. It is the reference key of the whole CR system — `related_cr`, `mapped_to_cr` in captures, `cr_id` in `rename_map.json`, and every "per CR-XXX" sentence in the docs. When two documents carry the same `cr_id`, every reference to that id loses determinacy. History: a 2026-07-24 sweep of the CR corpus found **two ids each held by two documents**, both collisions **cross-author** — two people drafting on parallel branches, each scanning its own tree, each seeing the id free. Per-file lint can never see a collision that lives in ANOTHER file; the project had already learned this for AIP (`duplicate_artifact_id`, added after FND-030/031) but the layer had never reached CR.

- Sibling of `_check_duplicate_artifact_ids`, with one deliberate difference: AIP scopes by `(account, id)` because the account folder **is** a legitimate namespace, whereas a `cr_id` has **no namespace** — hence no scope key.
- Collected inside the **same scan pass** as §20 (`lint_all._lint_change_requests`) rather than a second `rglob` — both rules want exactly the same file set under exactly the same filters. Files without a `cr_id` skip **by construction**, so `intake/`/`drafts/` can move without breaking the rule; malformed frontmatter is another rule's finding.
- Severity **ERROR** — a duplicated id breaks a reference key; that is a structural defect, not an advisory. One finding per collision **group** (a 3-way collision is one ERROR, not three).
- **Anchor determinism (do not "simplify").** The finding is pinned at ONE path and `lint_accept` matches findings by EXACT path, so the anchor must not move between platforms. `sorted(list[Path])` compares `PurePath._str_normcase` — lowercased on Windows, case-sensitive on POSIX — so for members living in different directories the two platforms disagree about which comes first. The rule therefore sorts with an explicit `relative_to(cr_root).as_posix()` key. With a bare `sorted()`, a grandfather accept placed on the Windows anchor stops matching on a POSIX CI box: the accept degrades to `lint_accept_unused`, the ERROR fires on the sibling file, and lint goes red downstream.
- Grandfathering historical collisions: inline `lint_accept` **with a reason** on the anchor file (`code`/`reason`/`accepted_by`; single-line `reason` — see §20). Never a hardcoded list in the tool, and `strip_lint_accept` (CR-065) removes the accept if the file is rewritten, so it is not a permanent amnesty. Note the ceiling: muting the same code across ≥3 files trips `lint_accept_class_noise` (§16) — from the third collision on, re-allocating the later CR's id is the intended answer.
- **DETECTION, not prevention.** The rule catches a collision only once both documents are in the tree being linted. The scenario that produced the two known cases — parallel branches not yet fetched from each other — still creates collisions; they are now caught at merge/lint instead of staying silent for months. Blocking at the source needs a mandatory `git fetch --all` before allocating, or a central ledger (`allocate_cr_id.py` docstring calls that out of scope) — a separate CR.
- Regression guard: `.ai-work/tests/test_duplicate_cr_id.py` (D1..D8; D8 pins the OS-stable anchor key, with a fixture built so the naive and stable orderings disagree on Windows — the platform this repo is developed on — so the defect cannot escape to a downstream CI run).
- **The AIP-side sibling carries the same anchor rule** (CR-AIWS-2026-08-021 T3): `_check_duplicate_artifact_ids` also sorts with `relative_to(aip_root).as_posix()`. Its members can span `exec/`, `exec/archived/` and `plan*/` inside one account scope, which is all it takes for the two platforms to disagree. Guard: `test_cr021_wave.py` P3a.

# 22. CR placement — `cr_placement_mismatch` (CR-AIWS-2026-08-021)

**Invariant guarded.** A CR's folder must match its `status` (CR Spec §16 mapping: `drafts/` · main · `applied/` · `rejected/` for every terminal-not-applied state). The folder is how humans and tools locate a CR by lifecycle stage; a file in the wrong one silently breaks that convention.

- Collected in the **same scan pass** as §20/§21 (`lint_all._lint_change_requests`) — one `rglob`, four rules. Files without a `cr_id` skip by construction.
- Severity **ERROR** (DP-021-A). A misplaced CR is not cosmetic: the corpus had exactly one, and it was the computed report anchor of a grandfathered `duplicate_cr_id`, so cleaning it up flipped the anchor and would have turned the tree red had the `lint_accept` not travelled with it.
- The finding message therefore **carries that warning explicitly** — anyone acting on it must check whether the CR is an accept anchor before moving it, because a misplaced accept emits nothing at all (no `lint_accept_unused` is produced for a file that carries no finding).
- Regression guard: `test_cr021_wave.py` P1a–P1e.

# 23. CR status vocabulary — `cr_status_offvocab` (CR-AIWS-2026-08-021)

**Invariant guarded.** `status` must be one of the CR Spec §16 lifecycle values: `draft` · `proposed` · `approved_for_ai_update` · `applied` · `rejected` · `superseded` · `deferred`.

- Severity **WARNING** (DP-021-A) — an unrecognised status is vocabulary debt, not a broken reference or a broken locating convention.
- An **empty** `status` is deliberately not reported here; other rules already cover a missing field, and duplicating it would just add noise.
- History worth keeping: when this rule was written the corpus held three off-vocabulary values (`superseded` ×2, `deferred` ×1) — and the right response was to **extend §16**, not to flag them. They carried `superseded_at`/`superseded_by`, i.e. they were designed states the spec had simply never enumerated. The rule therefore shipped at **0 warnings**. Before flagging a value as off-vocabulary, check whether the vocabulary is the thing that is incomplete.
- Regression guard: `test_cr021_wave.py` P2a–P2c.

# 24. Operating Memory store shape — `operating_memory_body_long` · `operating_memory_evidence_long` · `operating_memory_ref_unstable` · `operating_memory_group_offvocab` (CR-AIWS-2026-08-127 C4)

**Invariant guarded.** `.ai-work/memory/entries.jsonl` (Operating Memory L2, `operating_memory.md` §5) stays at its entry shape: `body` = 1–3 sentences "symptom → correct action" within `_common.OPERATING_MEMORY_BODY_MAX` (400 B) and without a ` · ` fold-join; `evidence` ≤ `OPERATING_MEMORY_EVIDENCE_MAX` (150 B); `ref` a stable locator (doc#section · `module.symbol` · CR/AIP id — never a workspace path, CAP id, temp file or line number); `group` one of the seven §3 groups (`_common.OPERATING_MEMORY_GROUPS`). Measured before the rule existed: the store grew from 68 B to 1 319 B per entry across triage waves with no command turning red.

- Leg `lint_all._lint_operating_memory` — whole-tree, and in `--scope task` when the footprint touches `.ai-work/memory/` (DP-127-D; a rule that never runs where the store is written is not a rule — CR-AIWS-2026-08-077).
- Severity **WARNING** for all four codes — the store is advisory (never a rule, never Truth); soft-budget shape of CR-AIWS-2026-07-037: no truncation, no auto-fix. A missing store is silent by design (an adopter may have none).
- The render (`_common.operating_memory_digest`) shares `OPERATING_MEMORY_BODY_MAX`: a body over the limit is shown as its first sentence + " …". One constant, two consumers — change it in `_common`, nowhere else.
- Regression guard: `.ai-work/tests/test_cr127_operating_memory_lint.py` — a firing case per code, the clean entry silent, the real repo store silent, wiring into `_lint_whole_tree` and the scope-task leg asserted by source inspection.

# 25. Step Inputs precision — `step_inputs_unresolvable` · `closing_step_inputs_vague` (CR-AIWS-2026-08-25 Item 1; precision CR-AIWS-2026-08-127 C7)

**Invariant guarded.** A step's `Inputs:` names resolvable things — file paths, `#anchors`, `STEP-NN` with a locator — not "all step evidence" / "all prior outputs" / "previous results" / the bare word "findings"; the closing step additionally must not rest on vague inputs. Both rules were shipped by CR-AIWS-2026-08-25 without a spec entry or a test (found by the §11.7 sibling sweep of CR-127).

- Leg `lint_aip._check_step_inputs_unresolvable` (every step) and `lint_aip._check_closing_step_inputs_vague` (last step only). One vocabulary `_VAGUE_INPUT_PATTERNS`; matched on **words** after `_strip_locator_tokens` removes backtick spans, path-like tokens (`x.md`, `a/b.jsonl`) and `#anchor` fragments. Before C7 the last pattern was the substring `findings`, so the concrete input `04_findings.md` fired: measured 2026-08-27 on 13 live AIPs, 14 WARN of which 9 were exactly that; after C7, 5 (the 4 real vague inputs and the 1 STEP-ref without locator).
- Severity **WARNING** — an author may justify a vague input in Done Condition; the closing-step variant exists because a final step whose inputs are unresolvable cannot be verified at close.
- Regression guard: `.ai-work/tests/test_cr127_step_inputs_precision.py` — `inputs_path_findings_md_does_not_fire` · `inputs_bare_word_findings_fires` · `inputs_all_step_evidence_fires` · STEP-ref branch · closing-step variant · single-vocabulary assertion.
