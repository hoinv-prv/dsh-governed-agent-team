# Task Lens Spec MVP

Version: v0.9.13  
Date: 2026-05-31  
Status: Canonical MVP spec  
Scope: Task Lens Minimal Spec Sprint merge  
Last update: v0.9.13 (CR-AIWS-2026-05-033) — added the reference_type→source_type bridge table to §B (non-binding convenience map for `lookup_wiki_source.py --source-type`; reference_type vocab stays open). Prior v0.9.13 (CR-AIWS-2026-05-032) — extended the v0.9.12 addendum: added `relevant_reference_types` to the preset schema (§B); sharpened the HINT semantics as ADDITIVE + NON-EXHAUSTIVE with AI inference primary and docs-to-find = inference ∪ lens (new §F invariant, edits to §C/§D/§E); documented the aiws-aip create(front-load) → aiws-aip run(follow) division with explicit Deferred lookups (§C/§D). Builds on CR-030 (stays applied); §12 engine stays deferred.
Previous: v0.9.12 (CR-AIWS-2026-05-030) — added the "Task Lens presets + skill integration (MVP)" addendum; narrowed §12 (preset-driven hints are now MVP; the lens engine stays deferred).

---

## 1. Purpose

This spec defines **Task Lens** for the AI Work System MVP.

Task Lens is an optional runtime viewpoint that helps AI route a task to relevant knowledge after the task intent is clear.

It helps AI decide:
- what type of knowledge to look for
- how to use Wiki Meta / Index and Knowledge Hub
- when to read Source Understanding Artifact
- when to verify raw/source
- when to expand or adjust viewpoint
- when not to use an explicit lens

Task Lens is a support mechanism, not a hard constraint.

---

## 2. Core definition

Task Lens is:

- runtime viewpoint
- task → knowledge routing support
- intent-based
- optional in MVP
- adjustable by HUMAN at runtime
- expandable by AI when too narrow
- not a hard scope limiter
- not source of truth
- not Knowledge Hub
- not Wiki Meta / Index
- not AIP Template
- not Working AIP

---

## 3. Core principles

## 3.1. Intent first, lens second

Task Lens selection requires task intent to be clear enough.

If intent is unclear:
- AI must not choose lens only from keyword
- AI should clarify / infer / confirm intent first
- after intent is clear, AI may select or propose Task Lens

Principle:

> Intent first, lens second.

## 3.2. Explicit lens is optional in MVP

Because Task Lens is not fully designed/tested in MVP, explicit lens usage is not mandatory for every task.

AI may choose **No-Lens / AI-decides-search-scope** when:
- lens choice is uncertain
- explicit lens may narrow search scope incorrectly
- task requires broad exploration
- task is simple and lens adds overhead
- output quality may be better with flexible intent-based reasoning

## 3.3. Task Lens must not limit AI capability

Task Lens guides AI attention and knowledge routing, but must not mechanically constrain AI search/reasoning.

AI may:
- look broader than the initial lens if needed
- propose lens expansion
- use raw/source verification
- use No-Lens option
- warn if HUMAN-adjusted lens appears too narrow

## 3.4. HUMAN may adjust runtime lens

Allowed flow:

```text
HUMAN inputs task
  ↓
AI clarifies / confirms intent
  ↓
AI proposes suitable Task Lens
  ↓
HUMAN adjusts Task Lens if desired
  ↓
AI uses the HUMAN-adjusted Task Lens
```

This is not mandatory default behavior for every task. It is an allowed HUMAN adjustment path.

---

## 4. Minimal runtime flow

```text
User task / current step
  ↓
Task understanding
  ↓
Intent clarification / inference / confirmation if needed
  ↓
Optional Task Lens proposal
  ↓
HUMAN runtime lens adjustment if desired
  ↓
Task Lens selection OR No-Lens / AI-decides-search-scope
  ↓
Knowledge route decision
  ↓
Wiki Meta / Index / Knowledge Hub / Source Understanding Artifact
  ↓
raw/source if verification is needed
  ↓
Working AIP / execution support
```

---

## 5. Starter lenses

MVP includes starter lens examples, not a full catalog:

1. Requirement Understanding Lens
2. Design Review Lens
3. Test Design Lens
4. Code Investigation Lens
5. Knowledge Capture Lens
6. Source Verification Lens
7. Planning / WBS Lens

These are intent-based routing viewpoints, not keyword mappings and not hard filters.

---

## 6. Selection / confirmation / adjustment rules

AI may infer lens when:
- task intent is clear
- output type is clear
- source/knowledge target is clear
- risk of wrong lens is low

AI should confirm with HUMAN when:
- task intent is ambiguous
- lens choice is high-impact
- custom/runtime lens is introduced
- lens expansion changes task direction/scope
- lens affects AIP Template / Working AIP basis

AI should record lens when:
- HUMAN confirmed/adjusted lens
- lens affects task direction
- lens expansion occurred
- custom/runtime lens is used
- lens affects Working AIP basis

AI may use No-Lens when:
- explicit lens may reduce quality
- explicit lens may narrow search incorrectly
- task needs broad exploration
- lens adds overhead without value

---

## 7. Relation to Wiki Meta / Index and Knowledge Hub

Task Lens guides how AI uses Wiki Meta / Index and Knowledge Hub.

- Wiki Meta / Index stores structured routing metadata.
- Knowledge Hub stores reusable knowledge.
- Source Understanding Artifact stores source-derived understanding.
- Raw/source remains source of truth.

Task Lens itself does not store metadata or knowledge.

Optional `related_lenses` hints may exist in metadata, but they are not hard filters.

Principle:

> Wiki-first, not Wiki-only.

Raw/source verification remains necessary when exactness, evidence, conflict resolution, implementation detail, or freshness check matters.

> **Two-kind node note (CR-AIWS-2026-05-029):** Task Lens is **node-kind-agnostic** — object-node metas (`node_kind=object`)
> live in the same Index and are found by the same lookup, so lens-based routing surfaces them automatically. For an
> "everything about \<object\>" intent, AI may resolve the object-node and use `wiki_relations.py --relations`
> (representation register) to gather the describing docs — an expansion choice, not a lens change.

---

## 8. Relation to AIP Template and Working AIP

Task Lens may influence or suggest an AIP Template, but it does not replace AIP Template.

Task Lens may feed Working AIP context, but it does not replace Working AIP.

Working AIP remains the task-specific execution guardrail.

If selected/adjusted/expanded lens affects execution basis, reflect it in Working AIP or Workspace trace when appropriate.

---

## 9. No-Lens / AI-decides-search-scope option

No-Lens is a safety fallback for MVP.

In No-Lens mode:
- AI confirms/understands task intent
- AI decides search/reasoning scope directly from intent
- AI uses Wiki Meta / Index, Knowledge Hub, Source Understanding Artifact, and raw/source as needed
- AI preserves Working AIP guardrail for meaningful execution
- AI asks HUMAN for important scope/direction decisions

No-Lens does not mean unstructured work.  
It means no explicit lens label is forced when that could harm quality.

---

## 10. Custom/runtime lens

AI may propose a custom/runtime lens when starter lenses are insufficient.

Examples:
- COBOL Migration Compatibility Lens
- Manufacturing Allocation Review Lens
- Security Impact Review Lens
- AIWS Sprint Closure Lens

If a custom/runtime lens is reusable:
- mark as capture candidate
- do not auto-promote to full catalog or Knowledge Hub
- use controlled capture if needed

---

## 11. Anti-patterns

Avoid:

- selecting lens from keyword alone
- treating Task Lens as AIP Template
- treating Task Lens as Working AIP
- treating Task Lens as Wiki Meta / Index
- treating Task Lens as a Knowledge Hub node/object (Task Lens is a routing viewpoint, NOT a stored object-node meta)
- using lens as hard search scope limiter
- forcing explicit lens when No-Lens would preserve quality better
- ignoring HUMAN-adjusted lens
- skipping raw/source verification because lens points to Knowledge Hub

---

## 12. Deferred items

> **Narrowed by CR-AIWS-2026-05-030 (v0.9.12).** A **minimal, hand-authored `task-lens-presets` hint store** plus
> `aiws-aip create` / `aiws-aip run` consultation of it are now **MVP** (see the "Task Lens presets + skill integration (MVP)"
> addendum below). What stays deferred is the *engine* machinery, listed here. Presets remain **hints, not hard filters**;
> No-Lens stays valid.

The following are outside this MVP sprint:

- full lens catalog
- full lens registry framework (beyond the minimal hand-authored `task-lens-presets` hint store now shipped at MVP)
- lens scoring/ranking
- lens orchestration engine
- automatic lens selection algorithm
- UI lens selector
- lens telemetry
- mandatory `related_lenses` metadata
- mandatory Task Lens field in every Working AIP

---

# Controlled Knowledge Promotion lens addendum

Custom/runtime Task Lens and lens-related routing lessons may become Knowledge Promotion candidates if they have reusable AI-use value.

A custom lens does not automatically become:
- Knowledge Hub content
- official lens catalog entry
- canonical runtime rule

Candidate requires review and target fit check.

---

# v0.9.9 Working AIP Connection addendum

Task Lens can shape Working AIP, but cannot replace it.

Working AIP should record selected Task Lens / No-Lens when relevant:

```markdown
## Selected Task Lens / Mode
- Lens:
- Reason:
- Search/execution effect:
- Expansion allowed:
```

Task Lens must not replace:
- task intent
- scope
- expected output
- execution steps
- guardrails
- done criteria

If Task Lens is too narrow, AI may propose expansion with reason and confirm if high-impact.

---

# v0.9.10 Workspace Boundary addendum

Workspace may record selected Task Lens / Mode for the active task.

Task Lens is not Workspace.

Workspace stores task/session state; Task Lens shapes search/reasoning focus.

If Task Lens changes during task, update Workspace and reflect execution-impacting change into Working AIP.

---

# v0.9.11 Minimal Runtime Testing addendum

Runtime testing checks for Task Lens:

```text
Intent before lens.
Lens shapes, but does not blind.
```

Check:
- task intent is clear before selecting lens
- selected lens is recorded if used
- No-Lens is allowed
- lens does not replace scope/output/done criteria
- AI expands beyond lens when relevant sources/context may affect correctness

---

# v0.9.12 Task Lens presets + skill integration (MVP) addendum (CR-AIWS-2026-05-030)

This addendum gives Task Lens a **bounded MVP implementation**: a minimal, project-customizable **`task-lens-presets`
hint store** that `aiws-aip create` and `aiws-aip run` consult to decide **which document types to reference** and **how to order
the reading surface**. It does NOT build the deferred engine (§12): no scoring/ranking, no orchestration, no automatic
selection, no UI, no telemetry. **Presets are HINTS, never hard filters; No-Lens stays valid; the lens is AI-inferred and
HUMAN-adjustable** (§2 / §3.3 / §3.4 / §9 / §11 are unchanged).

## A. The task-lens-presets store

- **Location:** `.ai-work/wiki/task_lens_presets/` — a project-customizable store, mirroring how `.ai-work/wiki/`
  already hosts `project_profile/`.
- **Default shipped:** the canonical default lives at
  `product/methodology/ai_work_system/30_templates/task_lens_presets.default.yml` (the §5 starter lenses as preset
  records). `aiws-pkg install` / `aiws-pkg upgrade` install it to `.ai-work/wiki/task_lens_presets/starter_lenses.yml`
  so presets work out of the box.
- **Customization:** projects edit / extend `.ai-work/wiki/task_lens_presets/` to add project lenses or tune the
  starter ones; reusable custom/runtime lenses (§10) are captured here. **Presets are DATA consulted by AI — not code.**

## B. Preset schema (per lens)

```yaml
- lens_id:                  # stable id, e.g. requirement_understanding (matches a §5 starter lens or a project lens)
  intent:                   # one line: the task intent this lens serves
  relevant_source_types:    # prioritised list of Artifact_Type_Taxonomy source_type values (+ object kinds, §3bis of
                            #   Knowledge_Object_Model_Spec) the lens pulls toward — the SUBJECT docs read/produced.
                            #   A HINT for input assembly, not a filter
  relevant_reference_types: # NON-EXHAUSTIVE hint list of process/standard artifact kinds the lens should ALSO surface
                            #   — the HOW-TO-DO-IT standards: guideline / checklist / template / sop / methodology_spec /
                            #   process_guideline / process_template / naming_convention (open, project-extensible).
                            #   Distinct from relevant_source_types (subject docs); both are HINTS, not filters
  register_priority:        # ordering over the 3 relation registers for expansion: [documentary, representation, domain]
  expansion_priority:       # ordered relation roles to follow first (e.g. upstream_input, companion_design, represents)
  no_lens_when:             # conditions under which No-Lens is preferable for this intent (keeps §3.2 / §9 explicit)
```

`relevant_source_types` / `register_priority` reuse existing vocab — the `source_type` enum
(`Artifact_Type_Taxonomy_Spec`) plus the object kinds (§3bis), and the three relation registers
(documentary / representation / domain — `Knowledge_Relationship`/`Knowledge_Expansion_Link` + Knowledge_Routing/Access,
CR-029). Nothing new to learn; the preset just orders them per intent.

`relevant_reference_types` surfaces the **standards artifacts** (guidelines, checklists, templates, SOPs) a task needs to
*do it right* — e.g. authoring an RD needs a requirement template + guideline; reviewing a design needs a review
checklist. Its vocabulary is **OPEN and project-extensible** (no hard enum, no membership lint) — keep it an additive
hint, consistent with §F. Distinct from `relevant_source_types`: the latter lists the *subject* docs read/produced, the
former lists the *process/standard* docs that govern how the work is done.

**Reference_type → source_type bridge (CR-AIWS-2026-05-033).** The open `relevant_reference_types` labels are fine-grained;
the wiki-meta `source_type` vocab (what `lookup_wiki_source.py --source-type` filters on) is coarser. Use this **non-binding
convenience map** to translate a lens reference_type into a `source_type` you can filter on — it does NOT constrain the
reference_type vocab (which stays open):

| relevant_reference_type (lens) | source_type to filter on |
|---|---|
| `*_template` (requirement_template, design_doc_template, test_case_template, …) | `process_template` |
| `*_guideline` / `*_checklist` / `naming_convention` / `*_playbook` | `process_guideline` |
| `sop` | `sop` |
| `methodology_spec` | `methodology_spec` |

The map is a hint for retrieval, not a requirement; a reference_type need not be a member of the `source_type` vocab.

## C. How aiws-aip create consults presets (front-load: infer first, lens adds, fill into AIP)

`aiws-aip create` **front-loads** the inputs. After task intent is clear (Intent-first, §3.1), it:

1. **Infers first** — from the task intent, AI infers what documents (subject + reference standards) it needs. This
   inference is **PRIMARY** and stands on its own; a lens is not required for it.
2. **Adds the lens as a checklist** — selects or proposes a Task Lens (§3.4) and looks it up in the presets store (or
   No-Lens, §3.2 — then skip presets). The preset's `relevant_source_types` (subject docs) and `relevant_reference_types`
   (guidelines / checklists / templates / SOPs) act as an **ADDITIVE "also-consider" checklist** to catch artifacts the
   inference may have missed. `register_priority` orders the candidates.
3. **Takes the UNION** — the final input set = **(AI inference) ∪ (lens suggestions)** (§F). Never lens-only, never
   filtered by the lens.
4. **Resolves + FILLS** the union into the AIP: subject docs + reference standards go into `Required Wiki Inputs` and
   `References to Read First` at create time (resolved via wiki lookup where possible).
5. **Records Deferred lookups** — for anything that cannot be resolved now, record a *Deferred lookup* (the doc to find +
   the lens to use) in the AIP's `## Selected Task Lens / Mode`, alongside the resolved choice. No-Lens ⇒ infer fully,
   skip presets, leave the section empty.

## D. How aiws-aip run consults presets (follow: execute from resolved AIP; lookup only for deferred)

`aiws-aip run` **follows** the AIP — it does NOT re-search. It executes from the AIP's already-resolved `Required Wiki Inputs`
+ `References to Read First`. The active lens (from the AIP's `## Selected Task Lens / Mode`, or a step-specific lens) is
used to:

1. **Order the reading** among the already-listed inputs — `build_active_step_context.py` populates an `active_task_lens`
   field on the ASC, and AI applies the preset's `register_priority` / `expansion_priority` as a **HINT** when reading the
   ASC reading surface (it may still read broader, expand, or verify raw/source — §3.3); and
2. **Drive a TARGETED lookup ONLY** for items the AIP explicitly lists under **Deferred lookups** (doc to find + lens to
   use). aiws-aip run resolves those, and nothing else, by lens-driven lookup.

When nothing is deferred and No-Lens, reading is unchanged (zero forced overhead). The lens never expands scope on its
own at run time — it only resolves what the AIP declared.

## E. Invariants (unchanged)

- **Hint, not filter** — presets order/surface; they never exclude relevant knowledge or block expansion. This applies to
  both `relevant_source_types` and `relevant_reference_types`.
- **No-Lens preserved** — every integration point works with no lens, at zero forced overhead.
- **Engine still deferred (§12)** — only the preset hints + recording the selected lens are un-deferred.
- **AI-inferred + HUMAN-adjustable** — HUMAN may adjust/override the lens at runtime (§3.4).

## F. Additive-hint invariant (CENTRAL — CR-AIWS-2026-05-032)

> **The Task Lens is an ADDITIVE, NON-EXHAUSTIVE hint. AI's own intent-inference is PRIMARY: AI infers what it needs
> first. The lens only ADDS reminders ("ah, this is also worth finding"). The set of documents to find = (AI inference)
> UNION (lens suggestions) — never only what the lens lists, never a whitelist, never a filter, never a scope-limiter.
> The lens NEVER bounds, filters, or replaces AI's search. No-Lens ⇒ AI infers fully.**

This invariant is CENTRAL and governs every Task Lens integration point (presets, aiws-aip create §C, aiws-aip run §D, AIP
templates). It applies equally to `relevant_source_types` and `relevant_reference_types`. Consequences:

- **aiws-aip create front-loads** — infers first, adds the lens as an "also-consider" checklist, takes the UNION, fills the
  resolved inputs into the AIP, and records any unresolved items as Deferred lookups (§C).
- **aiws-aip run follows** — executes from the AIP's resolved inputs without re-searching; lens-driven lookup happens ONLY for
  AIP-declared Deferred lookups (§D).
- A lens that returns nothing useful, or No-Lens, must never reduce what AI would otherwise find on its own.
