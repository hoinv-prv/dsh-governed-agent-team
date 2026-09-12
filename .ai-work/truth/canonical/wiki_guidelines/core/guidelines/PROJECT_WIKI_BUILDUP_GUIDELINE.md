# PROJECT_WIKI_BUILDUP_GUIDELINE_v0_1

> **Canonical home & routing (AIWS).** AIWS **first-build** guideline (canonical home: `product/wiki_guidelines/core/guidelines/`); the **maintenance** counterpart is `WIKI_META_BUILD_UPDATE_GUIDELINE.md`. Build-trigger routing → see **Triggers** below.

> Purpose: a project-agnostic, skill-like procedure for building a project **Wiki** (a.k.a. **Knowledge Hub**) — a thin **orientation layer** that lets an AI **find and understand the SHAPE of a source before opening it**, never a copy of source content.
> Audience: **an AI** running this like a skill (clear triggers, decision points, mandatory HUMAN gates, explicit per-step outputs). A human reviews each gate.
> Genericization boundary: this guideline **assumes a Knowledge-Hub tooling family providing the roles in Appendix A** as the substrate, but refers to every tool by its generic **ROLE**, not by any one install's script names (the single role→reference-implementation mapping lives in Appendix A). It is **generic over project domain, tech stack, directory layout, source-type names, ID schemes, and counts** — wherever a concrete example would help, it uses a generic category ("a requirements doc", "a source-code file", "a UI mockup", "a data-schema file") or a placeholder (`<SOURCE_TYPE>`, `<ID-SCHEME>`, "first N keys"). It works for three project shapes — **docs-only**, **code-heavy**, **mixed** — and calls out where steps adapt by shape.

---

## How an AI should use this guideline

**Triggers.** Run this guideline when asked to build, bootstrap, or substantially extend a project's Knowledge Hub / wiki; to "register a corpus", "make these docs/sources discoverable", or "set up the wiki index". For maintenance of an already-built wiki, do **not** re-run these steps by hand — use the whole-repo **sync** loop (built per **Appendix G**; its ROLE is in Appendix A) instead. First-build and maintenance are different loops.

> **Routing (AIWS install).** On a build trigger, **do not free-hand the AIP** — run the one-time **`/aiws-wiki bootstrap`** command. It pre-flights multi-system, explores the project **shape + inventory**, does Q&A with the HUMAN (scope / purpose / project shape / object-node gate / acceptance task-kinds), then **instantiates a fixed 12-step skeleton** (STEP-00 + one step per numbered Step below, each **`§`-pinning** its section in this guideline + the always-read "important points" core), applies shape as a per-step **annotation** (never deletes a step), and **delegates AIP authoring to `/aiws-aip create` + `/aiws-aip run`** (candidate→review→run). The numbered Steps below are the canonical method that skeleton encodes.

**Gate discipline (non-negotiable).**

| Rule | Meaning |
|---|---|
| **candidate → review → apply** | Every generated meta or edge is a CANDIDATE: draft, then HUMAN-review, then apply. Drafts never silently become canonical. |
| **capture-first** | Unknowns and unresolved questions go to a capture/inventory artifact, never straight into the wiki. Curate later, under review. |
| **never hand-edit projections** | The Index and Relations are PROJECTIONS of metas. Fix the **meta**, then **rebuild**. A hand-edit is wrong now and erased on the next rebuild. |
| **never silently invent object nodes or edges** | A deterministic builder must NEVER emit an object node or invent an edge. The AI may DRAFT an object node or an edge but waits for HUMAN sign-off. |
| **lint is a guardrail, not a reviewer** | Lint validates structure, not meaning. Treat its warnings as errors during review. Never ask a tool to auto-fix wiki content. |

**Every step appends to a running BUILD LOG.** From Step 1 onward, maintain ONE running build log / plan recording decisions, HUMAN-gate outcomes, tool fixes, profile/stopword/boilerplate tuning, mapping patterns, and test results. **Step 11 is generated FROM this log** — it is not written from scratch — and the Step-11 HUMAN acceptance outcome is the log's **final entry** before it is archived as the guideline's provenance. If a gate or fix has no build-log entry, it effectively did not happen. Record **WHY** (the rationale behind a gate or a tuning choice), not only **WHAT**.

**Every step also feeds a running LESSON LOG (`lesson_learned`).** Keep a SECOND running artifact, separate from the build log, capturing **generalizable** adjustments — anything you'd want changed for the NEXT wiki build, on ANY project. **Build log vs lesson log:** the build log is the project-local *provenance* trail and feeds Step 11 (the *project's* guideline); the lesson log is the curated, project-agnostic *retrospective* and feeds the improvement of **this common guideline** (and the shared tooling/profiles). **Append a lesson entry whenever** you (a) deviate from this guideline, (b) hit a footgun not in Appendix D, (c) fix a tool/profile in a way that would help other projects, (d) find a step's guidance unclear/missing/wrong, or (e) discover a better default. Do **not** log purely project-specific choices there — those belong in the build log. Entry format + the feedback loop: **Appendix F**.

**What each run produces.** Each step has a concrete artifact (an inventory file, an authority matrix, a predicted-relations table, a build plan, a tool inventory, sample/mass-run reports, a lookup-test report, and finally the generated project guideline). All working artifacts live in the workspace/build area; only the Step-11 deliverable lands in the project's guideline/reference docs (the lesson log is promoted separately, **upstream** — see below).

**Default locations (overridable).** Unless the project overrides them, write working artifacts into a single build-area directory (`<BUILD_AREA>/`, e.g. the active task workspace) with fixed filenames, and promote out only the two leaving artifacts — the final deliverable, and (separately, upstream) the lesson log:

| Artifact | Default path |
|---|---|
| Running build log | `<BUILD_AREA>/build-log.md` |
| Lesson learned (cross-project) | `<BUILD_AREA>/lesson-learned.md` → promoted upstream to improve THIS common guideline (Appendix F) |
| Inventory (Step 2) | `<BUILD_AREA>/inventory.md` |
| Authority/value/use matrix (Step 3) | `<BUILD_AREA>/authority-matrix.md` |
| Predicted-relations table (Step 4) | `<BUILD_AREA>/predicted-relations.md` |
| Build plan (Step 5) | `<BUILD_AREA>/build-plan.md` |
| Tool spec(s) (Step 6) | `<BUILD_AREA>/tool-spec-<SOURCE_TYPE>.md` |
| Sample-run report (Step 7) | `<BUILD_AREA>/sample-run-report.md` |
| Refresh-test report (Step 8) | `<BUILD_AREA>/refresh-test-report.md` |
| Mass-run spot-check report (Step 9) | `<BUILD_AREA>/mass-run-report.md` |
| Lookup-test report (Step 10) | `<BUILD_AREA>/lookup-test-report.md` |
| **Step-11 deliverable** (promoted) | the project's wiki **reference** folder, e.g. `<WIKI_REF>/wiki-buildup-guideline.md` |

Two artifacts leave the build area, to **different** targets: the **Step-11 deliverable** → the project's wiki reference folder (the project's how-to of record); the **lesson_learned** → **upstream**, as candidate input to improve this common guideline + the shared tooling/profiles (Appendix F). Every other artifact stays in the build area.

---

## Mental model

### The four-artifact orientation layer

The wiki is **exactly four artifact kinds**. Know which one you are touching at all times — each has a different authorship rule.

| # | Artifact | What it is | Who writes it |
|---|---|---|---|
| 1 | **Source artifact** | The real file (a requirements doc, a design doc, a source-code file, a UI mockup, a data-schema file). For a non-text original (PDF/Word/Excel/image), never read the binary — point the locator at an AI-readable representation of it. | It IS the source; the wiki references it, never copies it. |
| 2 | **Source Meta** | A lean Markdown card per logical unit: frontmatter + **Summary / Knowledge Targets / Lookup Keys [+ Related Sources]**. The **only thing you author**. Lighter than the artifact, richer than the index. | A builder (artifact metas) or the AI under a HUMAN directive (object nodes). |
| 3 | **Index projection** | The searchable surface rebuilt from ALL metas; what the lookup tool reads. | The index projector. **Never hand-edited.** |
| 4 | **Relations projection** | The typed-edge surface rebuilt from every meta's Related Sources; one-hop out + IN. | The relations projector. **Never hand-edited.** |

A meta must **never inline full source content**. If it does, it has failed its purpose.

### Two kinds of meta

- **Artifact meta** — one per real file (locator = a file path). **MAY be tool-generated.**
- **Object-node meta** — a logical entity (a function/feature, a screen/view, a table/entity, an API/endpoint, a module/subsystem, a concept/term) with **no backing file**: its locator is a **sentinel** (no file to read). An object node is a **pointer, not a container**: it carries identity + summary + edges only. It MUST NOT roll up or aggregate child metas' content, carry a content anchor, or reference an objects-store. "Made of parts" is a **navigation-only edge** (`part_of`/`contains`), never a content roll-up. **A deterministic builder must NEVER emit an object node.** Object nodes are AI-drafted under an explicit HUMAN directive, HUMAN-confirmed, and gated.

> **Object nodes are gated and may be unavailable.** Authoring an object-node meta is a high-friction, governed action: confirm the project's tooling guards and the named-consumer / necessity test are in place **before** authoring any object meta. Until that gate is satisfied, do **not** synthesize identity nodes — express "made of parts" and shared-function anchoring via companion-design edges on existing **artifact** metas instead (the necessity test: an object node earns its existence only when a real consumer needs it).

> Both kinds share **one meta store** and **one index**, found by the **same lookup**. The node-kind marker is a meta-only field (default = artifact) and is **not** projected into the index.

### Golden authorship rule

> **Tools generate artifact metas. OBJECT nodes and RELATIONS are AI-drafted UNDER a HUMAN directive and HUMAN-confirmed. Projections are NEVER hand-edited — always rebuilt from metas.**

A batch script never emits an object node and never invents an edge. The AI may draft either, but never silently creates one. This keeps the deterministic, regenerable layer (metas → projections) cleanly separate from the judgement layer (object identity, relations), so projections never rot and human-grade decisions are never machine-overwritten.

### Projections are rebuilt, not edited (both sides)

- **Write side:** never hand-edit the index or relations files. After any meaningful meta change, **rebuild** them and re-verify by lookup.
- **Read side:** never `Read` the whole index/relations files to enumerate. Use the lookup tool with a type filter / slim mode, the relations query tool, or grep.

### Build order — stable identity first, volatile code last

Build in order of stability so later layers attach to identities that already exist:

1. canonical / methodology / baseline docs
2. **IDENTITY object nodes** (functions/screens/tables/APIs), seeded from an enumeration source (a feature/requirement/function list), cross-checked vs requirements + design. **Conditional:** identity-node seeding requires a stable enumeration source AND the object-node gate (above) being satisfied; if no enumeration exists (common in docs-only / flat corpora) or the gate is not yet in place, **SKIP this layer** and build per-doc artifact metas + doc↔doc edges directly — **never synthesize identity nodes to fill the slot**.
3. requirements docs
4. decisions / design / prototype docs
5. source code (bulk) — *code-heavy / mixed only*
6. wire relations
7. rebuild projections
8. test

Build identity first and every later layer has a join point; build it last and you re-walk everything. **End each build stage with rebuild-projections + lint** so you never accumulate a large unverified batch.

> The numbered steps below describe the **FIRST full build**. The discovery-and-confirm front half (Steps 1–4) precedes the build/tooling half (Steps 5–9) precedes testing (Step 10) precedes deriving the project guideline (Step 11).

---

## Step 1 — Define the GOAL of the wiki

**Objective.** Fix **(1.1) SCOPE** — what information the wiki should cover — and **(1.2) PURPOSE** — Q&A-only vs. supporting execution of specific task kinds (and which). Also fix the **project SHAPE** (docs-only / code-heavy / mixed) so later steps know which sub-steps apply.

**What the AI does.** Interview the HUMAN (or read an existing brief) to extract scope and purpose. Classify the project shape from a quick repo skim using this heuristic: **docs-only** = no source-code directories in scope; **code-heavy** = source code is the majority of in-scope files with few docs; **mixed** = both a substantial doc corpus and a code corpus. When borderline, confirm at the Step-1 gate. Translate purpose into concrete **acceptance signals**: enumerate the **task kinds** the wiki must support (e.g. "find which code implements requirement Y", "review the design of feature X", "answer policy questions"). These become the **Step-10 task-simulation cases**. Open the running BUILD LOG and write the goal, the in/out scope boundary, the purpose, the shape, and the draft task-simulation list as its first entry.

**HUMAN gate.** HUMAN confirms **scope + purpose + project shape** AND signs off on the **enumerated task-kind list** — those become the Step-10 acceptance cases, so the acceptance bar must be HUMAN-set, not AI-set. Ambiguity here is clarified, never guessed.

**Outputs.** BUILD LOG created, with: goal statement, scope in/out boundary, purpose (Q&A vs task-execution + task kinds), project shape, and the draft task-simulation list for Step 10.

**Notes & footguns.**
- A vague "cover everything" scope produces an unbounded Step-2 scan — force a boundary.
- Skipping task-kind enumeration leaves Step 10 with nothing concrete to test against.
- Not recording shape causes later steps to over- or under-build (e.g. building code tooling for a docs-only project).

---

## Step 2 — Decide WHAT information goes into the wiki

**Objective.** Discover what actually EXISTS before deciding what to keep.

**What the AI does (2.1).** Scan **ALL files in the HUMAN-designated directories** (do not wander outside them). Detect natural **groups/categories** by path + extension + format signature. Read **a few samples per group** (not every file) to determine each group's format and content — read **enough** samples that Steps 3 and 4 can reason from them, since both inherit this evidence. Emit a single categorized **INVENTORY file**: one row per group with file count, representative paths, observed format, a one-line content description, a **proposed** in/out decision, and a **proposed** `<SOURCE_TYPE>`. Flag binaries and point to their AI-readable representation rather than reading the binary. Anything uncertain is recorded as an **open question in the inventory** (capture-first), not silently included or excluded.

**HUMAN gate (mandatory).** HUMAN reviews the INVENTORY and confirms, **per group**, which content goes **IN** vs **OUT** and whether the proposed `<SOURCE_TYPE>` is right. **No meta is built before this gate clears.**

**Outputs.** INVENTORY file (group · count · sample paths · format · content summary · proposed in/out · proposed source_type · open questions). BUILD LOG updated with the confirmed in/out + source_type decisions.

**Notes & footguns.**
- **Sample per group** — reading every file wastes effort; but sample thinly and Steps 3–4 inherit insufficient evidence.
- Inferring `<SOURCE_TYPE>` from extension alone misses format variants — confirm by reading samples.
- **Single-extension corpora:** when a corpus is all one extension (an all-Markdown docs repo, or an all-one-language code tree), the extension carries **no** grouping signal — derive groups and the proposed `<SOURCE_TYPE>` from **directory role + content pattern read from samples**, not from the extension.
- Too broad a directory set pulls in noise.
- **Never read a binary original directly**; follow its representation pointer. If the representation is partial, treat evidence as wiki-only.
- The AI's proposed in/out is a PROPOSAL pending the gate — not a decision.

> **Enumeration anti-pattern:** to survey what's already registered, use the lookup tool's type filter / slim mode or grep — do **not** `Read` the entire index/relations files.

---

## Step 3 — Confirm authority / value / intended use

**Objective.** Assign and confirm the per-file / per-group classification axes: **authority_level**, **knowledge_value**, and **intended_ai_use**.

**What the AI does.** For each IN group, propose an **authority tier** (source-of-truth > curated > working/reference > history — see Appendix C; the exact token spellings are install-defined and must match the local lint vocabulary), a **knowledge_value** (how much durable knowledge it carries), and an **intended_ai_use** (which Step-1 task kinds it serves). Reason from the already-read samples plus the Step-1 purpose, reading a few more samples per group where the classification is unclear. Render an **AUTHORITY / VALUE / INTENDED-USE MATRIX** (group × axes) with a one-line justification per cell. Explicitly mark **non-authoritative** groups (e.g. static mockups, sample data), note that their illustrative data must NOT be treated as requirements, and flag the need for **sample-data stopwords** later (Step 10).

**HUMAN gate (mandatory).** HUMAN confirms the matrix — **especially the source-of-truth vs reference boundary** — before it is baked into any meta frontmatter or profile. Promoting anything to the source-of-truth tier is a governed change, not a lightweight edit.

**Outputs.** AUTHORITY/VALUE/INTENDED-USE MATRIX (per group, with justifications and tier marked). BUILD LOG updated with confirmed tiers and any "NOT source of truth" caveats to embed in Summaries.

**Notes & footguns.**
- **Mis-tiering a static mockup or sample as source-of-truth** makes the AI treat fake data (names, numbers, dates) as binding — the single most damaging classification error. Pair the lower tier with a "NOT source of truth" caveat in the Summary **and** sample-data stopwords.
- `authority_level` must be a value in the install's validated lint enum or lint fails — use the project's actual vocabulary, not an illustrative label.
- Not linking `intended_ai_use` back to Step-1 task kinds leaves Step-10 testing ungrounded.
- **Additive Summary enrichment** from a HUMAN-provided authoritative source (append verbatim + a short gloss, touching nothing else) is allowed without a change request; **rewriting** curated prose is not.

---

## Step 4 — Predict the relationships

**Objective.** Predict the relationships between files/groups and **confirm the prediction with the HUMAN before any edge is authored**.

**What the AI does.** Predict edges by reasoning over the Step-2 samples (reading a few more per group where needed to predict edges) and pre-trained knowledge of the generic relation **axes** (see Appendix B): **design→source**, **cross-layer**, **intra-layer dependency**, and — for documentation — **doc↔doc**. Produce a **PREDICTED-RELATIONS TABLE**: from-group → to-group, proposed relationship type (mark project-specific types with the reserved `x:` namespaced prefix — see Appendix B), the **canonical direction** to declare it in, the expected basis, and confidence (`asserted` | `inferred` | `candidate`). Note which edges will be **machine-derived** (e.g. cross-layer endpoint/route matching) vs **AI-authored on object nodes / doc metas**. **Do NOT author any edge yet** — this is a prediction to confirm.

**HUMAN gate (mandatory).** HUMAN confirms the predicted relationship map: which edge types exist, their canonical directions, and which are machine-derived vs hand-authored. Edges are not invented — only confirmed-real links are carried forward.

**Outputs.** PREDICTED-RELATIONS TABLE (from → role → to · canonical direction · basis · confidence · derived-vs-authored). BUILD LOG updated with the confirmed relation model.

**Notes & footguns.**
- **Declare each relationship ONCE** in canonical direction — declaring both ends just dedupes back to one and invites drift.
- **Never invent edges** to fill slots — only real links; otherwise delete the line.
- A cross-layer link is **machine-derived** and **must run AFTER its source-side bulk builder**, or it gets wiped (see Step 6/8).
- A one-hop projection answers no transitive/multi-hop questions — don't expect closure.
- Write **intent-blind** basis notes (who reads/writes whose data, coupling, impact), not task-phrased advice like "read this when reviewing".

**Adapt by shape.**

| Shape | Step-4 dominant axes |
|---|---|
| **Docs-only** | The dominant axis is **doc↔doc** (supersedes/superseded_by, refines, described_by/describes, part_of/contains, references) plus **design→requirement**. There is **no** cross-layer or intra-layer-code axis. See the doc↔doc example set in Appendix B. |
| **Code-heavy** | design→source (via identity nodes), cross-layer (machine-derived), and intra-layer code dependency. |
| **Mixed** | All of the above; the design→source spine via identity nodes is the highest-value axis. |

---

## Step 5 — Plan the meta build

**Objective.** Turn Steps 1–4 into a concrete **BUILD PLAN**: build order, per-group per-file-vs-bulk treatment, profiles needed, object-node seeds, and the rebuild/lint cadence.

**What the AI does.** Synthesize the **layered build order** (baseline docs → identity nodes → requirements → design/prototype → code → wire relations → rebuild projections → test). For each group choose **per-file authoring** vs a **dedicated bulk builder** using the per-file-vs-bulk rule of thumb (below). For each group identify the **source-type PROFILE** it needs (format signature, summary extraction, key extraction, related-sources scaffold on/off). Identify the **object-node seed** (a stable enumeration such as a feature/requirement/function list) for the identity layer — and confirm the object-node gate is satisfiable before planning to author any. State the rule that **every layer ends with rebuild-index + lint**. Mark which sub-steps are skipped by shape.

**Per-file-vs-bulk rule of thumb.** Per-file authoring when a group has **≤ ~10 heterogeneous files**; a dedicated **bulk builder** when a homogeneous `<SOURCE_TYPE>` has **more than ~20 near-identical files**; the **10–20 band is a HUMAN judgement call**. (Use these as overridable defaults, not hard law.)

**HUMAN gate (lightweight).** HUMAN reviews the build plan and the per-group per-file-vs-bulk + profile choices. (Heavy gates already happened at 2/3/4.)

**Outputs.** BUILD PLAN: ordered layers · per-group build method · profiles to create/reuse · object-node seed source · rebuild+lint cadence · shape-based skips. BUILD LOG updated with the plan.

**Notes & footguns.**
- Bulk builders for a handful of docs = over-engineering; per-file authoring for hundreds of homogeneous files = un-scalable. Apply the rule of thumb above.
- A new profile **MUST declare its `source_types`** field — omit it and **every** meta of that type throws unknown-source-type at lint.
- For profiles whose type should NOT carry relations, set the **related-sources scaffold to off** so refresh stops re-emitting empty TODO edges.
- Not planning rebuild-after-each-layer leads to a giant unverified batch at the end.

**Adapt by shape.**

| Shape | Step-5 emphasis |
|---|---|
| **Docs-only** | Skip the source-code layer entirely. Seed identity nodes only if a stable enumeration exists **and** the object-node gate is satisfied; else go straight to per-doc artifact metas + doc↔doc edges. |
| **Code-heavy** | Plan dedicated bulk builders per `<SOURCE_TYPE>`, code↔code dependency precedence, and cross-layer matching. |
| **Mixed** | Do both; the **design→source spine via identity nodes** is the highest-value relation axis — plan it explicitly. |

---

## Step 6 — Identify the tools to build

**Objective.** Decide which TOOLS must be **built** vs **reused** to generate the metas.

**What the AI does.** Map the BUILD PLAN onto tool ROLES: which groups use the existing **single-artifact meta builder + a profile** (no new tool), and which `<SOURCE_TYPE>`s need a **NEW dedicated bulk meta builder**. For each new bulk builder, write a **TOOL SPEC** stating the generic contract (see Appendix A): dependency-free and runnable without an install step, with an encoding-safe write path and a help flag; standard args plus a dry-run and a limit; emits a **FULL valid meta** per file and **NEVER an object node**; **never writes the index/relations projections**; resolves edges **only to source_ids it itself generated** so it emits no broken refs; **extracts cross-layer link data up front** (e.g. endpoint/route declarations) if it handles source code; **collapses multi-edges between the same pair to one edge by a stated precedence**, keeping inheritance/implements on a separate axis; and **filters lookup keys through the config stopword union**. Register each new builder in the **build-route registry** (`<SOURCE_TYPE>` → builder + arg template + profile).

> *Reference-impl detail (a conforming tool MAY differ):* the reference build collapses code-to-code edges by the precedence `calls > uses > imports > related` and resolves edges in two passes (map paths→ids, then resolve). The body requires only the generic behavior — *collapse multi-edges to one-per-pair by a stated precedence; emit no broken refs* — not these exact mechanics.

**HUMAN gate.** An explicit HUMAN **directive** to author each new bulk builder ("build a tool for type X and register it"). That directive **IS** the authorization — no second confirmation. Absent it, the AI uses the generic per-file flow and **never self-authorizes a builder**.

**Outputs.** TOOL SPEC(s) — one generic contract per new bulk builder — plus the list of groups that reuse the single-artifact builder + profile, plus build-route registry entries. BUILD LOG updated with which tools are new vs reused; **LESSON LOG** appended for any spec/contract gap that generalizes (e.g. a contract clause this guideline should mandate by default, like up-front cross-layer extraction) (Appendix F).

**Notes & footguns.**
- Authoring a builder **without the HUMAN directive** violates the authorization rule.
- A builder that **emits object nodes** or **writes projections** is broken — both forbidden.
- **Omitting cross-layer extraction up front** means retrofitting it later forces a re-run that drops already-injected cross-layer edges. Require extraction at commission time.
- **Hardcoding stopwords in the tool** instead of config makes hygiene unportable and un-refreshable.
- Keep **dispatch (route)** separate from **interpretation (profile)**; neither projects into the index; `<SOURCE_TYPE>` stays the single canonical key.

**Adapt by shape.** Docs-only projects usually need **no new bulk builder** (per-file builder + profiles suffice) and **no cross-layer matcher**. Code-heavy/mixed projects need both.

---

## Step 7 — Trial-run the build-meta tool on samples

**Objective.** Trial-run each new build-meta tool on a few samples and **fix the tool before scaling**.

**What the AI does.** Run each new bulk builder as **dry-run**, then on a small **limited** sample. Inspect emitted sample metas: required sections present, frontmatter parses (no byte-order-mark corruption — see Footgun catalog), `<SOURCE_TYPE>` correct, edges resolve only to known ids, keys filtered. Lint the sample output (structural). Compare against the TOOL SPEC. Fix the tool and re-run on samples until clean. Record each defect + fix. For any new/unfamiliar format, build **2–3 representative samples**, run the build checklist + a **3-keyword (identifier / domain / category) lookup smoke test**, fix the profile/mapping-pattern, and only then proceed.

**3-keyword smoke test — PASS criteria.** PASS = the **identifier** keyword returns the sample at **rank 1**; the **domain** and **category** keywords each surface it **within top-N** (treat top-N as top-10 unless the project overrides). See the lookup self-test definition in Appendix A.

**HUMAN gate (mandatory before mass-building a new format).** HUMAN eyeballs a few generated sample metas and approves the format.

**Outputs.** SAMPLE-RUN REPORT: sample metas inspected · lint result · defects found · tool fixes applied · before/after. BUILD LOG updated with the tool-fix trail; **LESSON LOG** appended for any tool/profile fix or footgun that generalizes beyond this project (Appendix F).

**Notes & footguns.**
- See Footgun catalog: **BOM** (use an encoding-safe write path, not an editor/IDE path that may inject a byte-order mark) and **external-write desync** (re-read files after an external script writes them; have builders print the paths they wrote).
- Don't approve a format from the plan alone — look at **real sample output**.
- Ensure each sample has **≥1 strong identifier (T1) lookup key**.

**Adapt by shape.** **Docs-only:** there is usually no bulk builder to trial — instead trial-run the **single-artifact builder against a NEW profile** on 2–3 representative samples, run the build checklist + the 3-keyword smoke test, and **fix the PROFILE (not a tool)** before mass-authoring. (For docs-only this is the primary path, not a sub-case.)

---

## Step 8 — Build/confirm the refresh tool

**Objective.** Build (or confirm) the **refresh** tool per source type, test it on samples, then confirm across all targets.

**What the AI does.** Ensure a refresh tool exists for each source type — **reuse** the single-artifact refresh for per-file types; for a **new bulk `<SOURCE_TYPE>`**, set its refresh policy to **rerun the routed builder** (Step 6) and confirm that path preserves curated content. The refresh contract (see Appendix A): re-project a meta against its **changed** source while **preserving curated content** — **draft-by-default** (write a draft, leave the canonical meta untouched) and **apply-on-demand** (with backup); preserve the curated **Summary** unless explicitly regenerated; preserve curated frontmatter (authority/value/freshness) and enriched body sections + resolved edges; **UNION** old + newly-derived lookup keys (curated first, case-insensitive dedupe) and **re-filter the union against CURRENT config** stopwords/boilerplate; record a maintenance-log entry and report material change. Test on changed-sample metas: curated content survives, dropped config stopwords actually leave old keys, edges are not clobbered. Then run across all metas of the type to confirm.

**HUMAN gate.** HUMAN confirms refresh behavior on samples (curated content preserved, no edge loss) before relying on it for the type.

**Outputs.** REFRESH-TEST REPORT: sample refresh diffs (preserved vs regenerated) · config-stopword propagation check · edge-preservation check · all-targets confirmation. BUILD LOG updated with refresh policy per type; **LESSON LOG** appended if the refresh policy or any preservation gap is a generalizable adjustment (Appendix F).

**Notes & footguns.**
- A refresh that **regenerates from scratch** destroys curated Summary/keys/edges — the costliest data loss in a wiki.
- A **naive key UNION keeps stale keys forever** — refresh **must re-filter** against current config so a newly added stopword/boilerplate term reaches **existing** metas too.
- For source code, re-running a bulk builder regenerates Related Sources and **DROPS machine-derived cross-layer edges** — the cross-layer matcher must be **re-run after** (the single most common edge-loss footgun).
- **Applying ≠ promotion/approval** — recording an action to the maintenance log records that it happened, nothing more.

**Adapt by shape.** Docs-only projects rely on the single-artifact refresh path; the cross-layer re-run caveat does not apply.

---

## Step 9 — Mass-run with spot-checks

**Objective.** Mass-run the build-meta tool(s) across all in-scope files, with random spot-checks and rerun-on-fix, then author the confirmed object nodes and wire the confirmed relations.

**What the AI does.** Run each confirmed builder over its full root(s). During first build, call the builders **directly** (or via the build-route registry's arg template) — you may borrow the sync orchestrator's invocation-**rendering** helper to format the call, but do **not** invoke the maintenance sync loop itself (that is the separate maintenance loop). **Always pass the required identifying args** (e.g. prefix + subdir). After each layer's mass run, **rebuild the index + relations projections and lint**. **SPOT-CHECK a random sample** of outputs (not just error rows): frontmatter parses, sections complete, source_type/authority correct, edges resolve, keys sane and within the soft budget. If a **systemic defect** appears, **FIX THE TOOL and RERUN the affected root** — do not hand-patch individual metas. Re-read externally-written files before any tool re-writes them.

**Author object nodes + wire relations (all shapes).** After all in-scope artifact metas are built and projections rebuilt, **author the confirmed object nodes** from the Step-5 seed (only where the object-node gate is satisfied) and **wire the Step-4-confirmed relations**: resolve the represents/implements-style edges to identity nodes (code-heavy/mixed) and prototype edges; run the **cross-layer matcher AFTER the last source-side builder run**; declare each confirmed edge **once in canonical direction** with an intent-blind basis note; then **rebuild the relations projection**. Declare additive edges on the **new/source side** so stable identity nodes aren't churned.

**HUMAN gate.** No new heavy gate (the format was approved at Step 7); spot-check findings that imply a tool change route through the normal fix-and-rerun loop.

**Outputs.** MASS-RUN SPOT-CHECK REPORT: per-root counts · random-sample inspection results · defects · tool fixes · reruns · final lint-clean status · rebuilt projections · wired relations. BUILD LOG updated with mass-run results and any tool fixes; **LESSON LOG** appended for any systemic tool defect or invocation footgun worth fixing upstream (Appendix F).

**Notes & footguns.**
- **Hand-patching individual metas** instead of fixing the tool — the next refresh/rerun overwrites the patch.
- **Missing prefix/subdir args** can dump hundreds of garbage metas into a flat dir and spike the index — always pass identifying args.
- Forgetting to **rebuild projections before spot-checking** = you inspect a stale index.
- Spot-checking only error rows misses **silent-success defects**.

**Adapt by shape.**
- **Code-heavy / mixed:** mass-run the bulk builders per root; author identity object nodes (gated) + design→source / cross-layer / prototype edges; run the cross-layer matcher last.
- **Docs-only, seeded (enumeration + object-node gate satisfied):** mass-run the per-file builder over the confirmed doc folders, then author object nodes + design→doc edges. The cross-layer-matcher re-run caveat does **not** apply.
- **Docs-only, no seed:** mass-run the per-file builder, then wire **doc↔doc edges only** — **skip object-node authoring entirely**. The cross-layer-matcher re-run caveat does **not** apply.

---

## Step 10 — Test the wiki metas; tune the profile

**Objective.** Test discoverability and navigability; tune lookup-key hygiene (e.g. add stopwords) — **in profiles/config, never in the tool**.

**What the AI does.** Run the **test ladder in order**:

1. **LINT** — structural: required sections, frontmatter parses (no BOM), no unresolved edge TODOs, no broken refs, no unknown source_type, no orphan artifacts.
2. **LOOKUP SELF-TEST** — every entry returns itself at rank 1 by id and surfaces in top-N (treat as top-10 unless overridden) by its keys. Since CR-AIWS-2026-07-037 the index carries the meta's full key list (lossless), so the self-test sees every key.
3. **TASK SIMULATION** — the real acceptance test: run realistic multi-angle queries for the **Step-1 task kinds**. A gap = an expected source not surfaced → enrich keys. A low score = found-but-fragile.
4. **RELATIONS / navigability** — each **node that carries edges** (an object node OR an edge-bearing doc meta) resolves edges as **BOTH** an out-edge source AND an IN-edge endpoint.
5. **Re-test loop** — tests reflect the **current index only**; rebuild projections before trusting any result.

Tune hygiene via **profile/config only**: add **single-token stopwords**, add **whole-key boilerplate suppression** for phrases pinned identically across a type, add **sample-data stopwords** for non-authoritative groups. After any change, **rebuild projections and re-test**.

**HUMAN gate.** HUMAN reviews **lookup-key curation on over-budget metas** (soft-budget lint WARNs) and the **task-simulation coverage/gaps** — self-test is lexical-only, so HUMAN + task simulation are the real acceptance check. Profile/stopword changes are reviewed before they propagate via refresh.

**Outputs.** LOOKUP-TEST REPORT (lint result · self-test PASS/FAIL · task-simulation coverage + gaps + scores · relations navigability) + PROFILE UPDATES (stopwords / boilerplate / sample-data filters). BUILD LOG updated with test results and every tuning decision; **LESSON LOG** appended for any hygiene/profile insight that should become a default in the common guideline (e.g. a new stopword class or key-curation rule) (Appendix F).

**Notes & footguns.**
- **Do not trust self-test as the acceptance test** — a lexical pass says nothing about task recall/relevance; use task simulation + HUMAN review.
- Don't trust a test result from **before** the projection rebuild.
- **Tuning stopwords in the tool body** is un-portable, un-refreshable, and won't propagate via refresh.
- After a config change, **re-filter existing metas** (via refresh) or the change never reaches metas built earlier.
- See Footgun catalog: **Over-long auto-extracted key list** — front-load IDs + canonical names in all languages the project uses; the soft budget is defined once in Appendix C.

**Adapt by shape.** Docs-only: rung 4 tests **doc↔doc** edges (supersedes/refines/part_of) for bidirectional resolution; there are no object nodes in a no-seed docs-only build, so the relation-test unit is the edge-bearing doc meta.

---

## Step 11 — Produce the project's wiki build-up guideline

**Objective.** Generate the **project-specific** wiki build-up guideline — **from the running build log**, not from memory.

**What the AI does.** Generate the project guideline from the BUILD LOG accumulated across Steps 1–10. Fold in: the confirmed goal/scope/purpose/shape; the inventory + in/out decisions; the authority matrix; the relation model; the build order and per-group method; the tool specs + which builders were authored; the sample/mass-run results; the profile/stopword/boilerplate tuning; and the test/DoD outcomes. Structure it **skill-like**: triggers, the candidate→review→apply gate discipline, per-step outputs, and the **footguns actually encountered**. Keep tools referenced by **ROLE** with a role→reference-implementation mapping table. State up front that this is **self-referential**: future builds must keep the running log so the guideline stays regenerable. **Then finalize the LESSON LOG:** consolidate the running lesson entries, dedupe them, and tag each with a concrete **target** (a named section of this common guideline, a specific tool ROLE, or a profile/config mechanism), a **scope** (common-guideline-doc / tooling / install), and a **status** — ready for upstream review (Appendix F).

**HUMAN gate.** HUMAN reviews and accepts the generated project guideline as the operational how-to of record, AND **triages the lesson_learned entries** (accept / defer / reject) before any are routed upstream — promoting a change into the common guideline is itself a candidate→review→apply action.

**Outputs.** (1) The generated **PROJECT WIKI BUILD-UP GUIDELINE** (the deliverable), promoted to the project's wiki reference folder (default `<WIKI_REF>/wiki-buildup-guideline.md`). (2) The finalized **LESSON_LEARNED**, promoted **upstream** as triaged candidate input to improve this common guideline + shared tooling/profiles (Appendix F). The BUILD LOG is **finalized and archived as the project guideline's provenance**, with the Step-11 HUMAN acceptance outcome as its final entry.

**Notes & footguns.**
- **Writing it from scratch** drifts from what actually happened — generate from the log.
- **Baking in project-specific facts** that won't generalize when it becomes a template.
- **Citing tools by script name** instead of role.
- **Omitting the footguns actually hit** — those are the most valuable part of a derived guideline.
- If the log wasn't kept live throughout, the guideline can't be regenerated faithfully — record WHY, not just WHAT.

---

# Appendices

## Appendix A — Tool ROLE → reference-implementation mapping

The body uses ROLES. This single table maps each role to **one reference implementation (this install)** so a practitioner on that install can act immediately.

> **Caveat.** Script/skill names below are **ONE reference install**; a conforming Knowledge Hub may name its tools differently and split responsibilities differently. The body depends only on the **Role** and **responsibility** columns. The **Shape** column marks where a role does not apply for a docs-only build. Where a responsibility names a concrete behavior (precedence order, two-pass id resolution, config file format), that is a reference-impl detail — a conforming tool MAY differ.

| Role | Generic, verifiable responsibility | Shape | Reference implementation (this install) |
|---|---|---|---|
| **meta builder** (single artifact → one meta) | Given one artifact + a type profile, write ONE artifact meta (frontmatter + required sections); profile-driven (not hardcoded); format validation is warning-only; sets `updated_at` = source mtime; applies key stopwords; accepts AI semantic overrides; **never** writes projections; **never** emits an object node. | all | `build_wiki_source_meta.py` |
| **bulk meta builder** (one per homogeneous TYPE) | Dependency-free, encoding-safe, help flag, dry-run, limit; emits a FULL valid meta per file; **never** emits an object node; **never** writes projections; resolves edges only to ids it generated; extracts cross-layer data; collapses multi-edges per pair by a stated precedence; filters keys via config stopword union; prints paths written. | code-heavy / mixed only (docs-only uses the single-artifact builder + profiles) | `build_<lang>_wiki_metas.py` (reference matches one named language per builder) |
| **index projector** | Rebuild the searchable index from ALL metas; project the **full** lookup-key list losslessly in written order (no cap/sort/de-dup/normalize — CR-AIWS-2026-07-037); strip blanks; never hand-edited. Key-count hygiene = meta-lint soft-budget WARN. | all | `build_wiki_source_index.py` |
| **relations projector** | Rebuild the typed-edge projection from every meta's Related Sources; store one canonical direction per **named inverse pair** (flip + dedupe, union basis, strongest confidence); store documentary / symmetric types **as-authored** (never flip/dedupe); keep broken refs visibly; warn (not error) on unknown bare types; never hand-edited. | all | `build_relations.py` |
| **lookup tool** | Search the index by keyword / id / path / semantic; return ranked candidate ROUTES with meta + artifact locators; result is a route, not evidence; escalate on miss (semantic → raw → ask human). | all | `lookup_wiki_source.py` (semantic mode is a CLI flag, e.g. `--mode semantic`) |
| **relations query tool** | Given a node id, return one-hop **out** + **IN** edges from the projection; no transitive closure; reads only the projection. | all | `wiki_relations.py` |
| **lint tool** | Validate meta/index/relations/route-registry structure (sections, frontmatter, enums, projection invariants, broken refs, orphans); guardrail only, never auto-fix; strict mode promotes warnings to failures. | all | `lint_wiki.py` / `lint_all.py` |
| **lookup self-test + task simulation** | Self-test: each entry finds itself at rank 1 by id and top-N by keys (full key list — lossless index). Task simulation: realistic multi-angle queries surface expected sources and report gaps. Reuses lookup scoring; exit code gates. | all | `smoke_test_wiki_lookup.py` / aiws-wiki test-lookup |
| **refresh tool** | Re-project one meta vs its changed source preserving curated content: draft-by-default + apply-on-demand (backup); preserve summary/frontmatter/enriched sections/resolved edges; UNION + re-filter keys against current config; record to maintenance log (record ≠ promote). | all | `refresh_wiki_source_meta.py` |
| **cross-layer link matcher** | Normalize and match endpoints/routes across two layers; INJECT cross-layer edges into the consuming layer's metas; idempotent; logs unmatched; **must run AFTER the last run of the builder it writes into**. (Reference impl matches two named layers; generalize per project to any consumer-layer↔provider-layer pairing.) | code-heavy / mixed only | `link_layer_endpoints.py` |
| **whole-repo sync planner + orchestrator** | Read-only planner detects change by mtime vs `updated_at`; orchestrator gates via mandatory plan-review, auto-rebuilds code per-root only if changed, review-gates docs in covered folders, gates deletions via deregister/orphan sweep, re-applies the cross-layer matcher after any rebuild, then rebuilds projections + lints. **Maintenance loop only — not used for first build.** | all (maintenance) | `plan_wiki_sync.py` + refresh-project-wiki-all |
| **build-route registry** | Map `<SOURCE_TYPE>` → bulk builder + arg template + profile; batch registration dispatches automatically; refresh = rerun the routed tool; a config sidecar, not projected into the index. | code-heavy / mixed (mainly) | `route_build_tool.py` |
| **source-type profiles** | Per-type declarative config files in a profiles directory: format signature, summary/key extraction, related-sources scaffold on/off, `source_types` declaration (unlocks lint), key-hygiene stopword/boilerplate lists. | all | per-type config files under a profiles directory, e.g. `wiki_sources/profiles/<type>.yml` (path/format are examples) |
| **deregister / orphan sweep** | Safely remove a meta whose source is gone, behind a gate; sourced from planner orphans or lint orphan-artifact, never a generic missing-file signal (which mis-flags object nodes). | all | aiws-wiki deregister |

---

## Appendix B — Relations primer

**Declare-once, canonical direction.** Author each relationship in exactly ONE place — the declaring meta's **Related Sources** section — and in ONE canonical direction of each inverse pair. The relations projector stores one direction and answers the reverse. Example canonical pairs (**examples, not a fixed enum**):

| Canonical (declared) | Reverse (answered by query) |
|---|---|
| `called_by` | `calls` |
| `part_of` | `contains` |
| `represented_by` | `represents` |
| `described_by` | `describes` |
| `downstream_of` / `upstream_of` | (inverse) |
| `superseded_by` | `supersedes` |

**Only the named inverse pairs above are normalized** (flipped to canonical direction + deduped). **Documentary roles** (e.g. upstream-input / downstream-target / companion-design and the like) and **symmetric domain types** (e.g. an `x:equivalent_to`) are **NOT inverse pairs**, are **NOT auto-normalized**, and are **stored as-authored** — never flipped or deduped. Do not assume a documentary role like an upstream-input edge gets flipped the way `called_by`→`calls` does. Do not declare both ends of a true inverse pair — it dedupes back to one and invites drift.

**One-hop out + IN, not a graph engine.** The relations query answers a node's one-hop out-edges AND in-edges. It does **not** compute transitive closure — walk multi-hop paths yourself with repeated queries. "Everything about X" for an object = a relations query (out + IN), not a lookup.

**The generic axes** (token names below are **example vocabulary, not a fixed enum**):

| Axis | What it links | Typical authorship |
|---|---|---|
| **design → source** | requirement/design → identity node → code (a *represents*-style edge to the identity node; an *implements*-style edge from the identity node to concrete code) | AI-authored on object nodes (HUMAN-confirmed) |
| **cross-layer** | a consumer in one layer → the provider it invokes in another layer (e.g. a UI calling a service endpoint) | **machine-derived** by the cross-layer matcher, run AFTER the source-side builder |
| **intra-layer dependency** | file → file within one layer | emitted by the bulk builder; collapse to one-per-pair by a project-declared precedence (example: `calls > uses > imports > related`); keep inheritance/implements on a separate axis |
| **doc ↔ doc** (intra-documentation) | one document → another (supersedes, refines, described_by, references, part_of) | AI-authored on doc metas; the **primary axis for docs-only projects** |

**The design→source spine.** Attach both the design/requirement layer and the code layer to the **same identity node** so a single relations query reaches a function's spec, its design, its prototype, and its implementation — no repo-wide grep. **In a docs-only project with no code layer, the spine degenerates to a requirement→design→decision doc chain with no implementation endpoint.**

**Edge hygiene.** Fill a relationship slot only when the link is real; otherwise delete the line. Write the basis note **intent-blind** (who reads/writes whose data, coupling, impact), never task-phrased. Declare additive edges on the **new/source side** so stable nodes aren't churned. Reserve a **namespaced prefix** for project-specific edge types (the reference install uses an `x:` prefix) so they're always valid and never auto-normalized.

**Broken-ref handling.** An edge whose target is not in the index is **KEPT and surfaced as a broken-reference marker**, never silently dropped. An unknown bare relationship type is a **warning**, not an error. Read the warnings — broken refs accumulate quietly otherwise.

**Identity is frozen once referenced.** Once a `source_id` is referenced by an edge, it is frozen. A rename is an **ALIAS**, not a re-key — keep the old id as a lookup key, or every edge pointing at it breaks.

---

## Appendix C — Meta quality + lookup-key hygiene

**Required sections.** Every meta needs **Summary**, **Knowledge Targets**, and **Lookup Keys** (plus **Related Sources** where the type carries edges) or lint errors.

**Summary discipline.** 1–3 sentences drawn from the source's Purpose/Overview — **NOT a field list** (fields live in the source). Do not re-list fields. Keep every section terse and signal-dense.

**Discoverability.** Lookup keys decide whether a source is findable. Include:
- the **bare ID** AND the **human-readable name in every language the project's content actually uses** (often just one),
- the distinctive **domain terms**.

Tier keys: **identifiers first** (T1 — unique; passes the discriminatory test "searching this key alone returns a small, correct set, ≤ ~5"), then **domain terms** (T2), then **generic category labels** (T3 — never standalone). A generic section heading must never be a standalone T1/T2 key.

**Lossless key projection + the soft budget (CR-AIWS-2026-07-037).** The index carries the meta's **entire** `## Lookup Keys` list in **written order** — no positional cap, no sort, no de-dup, no normalization (case/whitespace/width variants count as distinct). No key is invisible to lookup or the self-test. Hygiene lives at the **meta layer**: lint WARNs (`meta_lookup_keys_over_budget`) when a meta exceeds the soft budget — read the real budget value from the lint tool/config at runtime. Curation guidance (now for ranking QUALITY, not survival):
- **front-load** the must-keep core (bare ID + canonical names in all languages used),
- merge near-duplicates, drop generic terms and those already in summary/title,
- keep one best discriminator per concept,
- validate retrieval quality by **HUMAN review + task simulation** (self-test is lexical-only).

> The soft budget is a **hygiene threshold, not a truncation** — keys over budget still index and rank. The number is an implementation value (default 40, emitter-aligned); read the real value from the meta-lint config at runtime.

**Two key-hygiene layers (both config-driven, applied at build AND refresh).**

| Layer | Drops | Tuned in |
|---|---|---|
| **A — single-token stopwords** | generic single-token noise — filler words, ubiquitous technology/role/layer labels for this project's stack, and fake sample-data tokens. *(Stack-dependent examples: framework/layer/role words, web-tech terms, CRUD verbs. Docs-only corpora: documentary boilerplate like "overview", "introduction", "scope", "section", "appendix", "document", "policy".)* Universal sets are built into the tool; project generics live in config. | config/profile, **never the tool** |
| **B — whole-key boilerplate suppression** | a multi-word key whose whole normalized form is pinned identically on **every** meta of a type (zero-discrimination noise whose tokens still leak into the scorer). | profile, **never the tool** |

To drop a term, edit the config/profile, not the builder. Layer A can't touch a pinned multi-word phrase — hence Layer B. **Refresh must re-apply the current config** to old keys so config tightening reaches metas built before the change.

**No universal/generic keys.** Exclude words that match everything, rank nothing, and dilute ranking precision — **stack-dependent examples:** language names, layer names, framework names, role words like "controller"; **for docs-only:** documentary structure words like "overview", "introduction", "scope", "appendix". Stopword these.

**Reference-tier vs source-of-truth discipline.** Tag each meta with its authority tier (**source-of-truth > curated > working/reference > history**; the exact token spellings are install-defined and must match the local lint vocabulary — these labels are illustrative, not literal enum values). Never treat reference/history content as authoritative; verify it against the underlying source when a decision depends on it. For non-authoritative sources (mockups/prototypes), state **"NOT source of truth"** in the Summary and pair it with sample-data stopwords so illustrative data is never mistaken for requirements.

**Profiles drive interpretation, not hardcoding.** Interpret each `<SOURCE_TYPE>` via a per-type PROFILE (format signature, summary extraction, key extraction, related-sources scaffold policy), not hardcoded logic. If no profile fits a new format, author one — and it **MUST declare its `source_types`** or every meta of that type throws unknown-source-type at lint. For edgeless types, set the related-sources scaffold **off**.

---

## Appendix D — Footgun catalog

| Footgun | Consequence | Prevention |
|---|---|---|
| Hand-editing a projection | Wrong now, erased on next rebuild | Fix the meta, then rebuild |
| Deterministic builder emits an object node | Unreviewed identity nodes, broken authorship contract | Builders emit artifact metas only; stop if one appears |
| Authoring an object node before its gate is satisfied | Object metas the install's lint/tooling does not yet support | Confirm tooling guards + named-consumer/necessity test first; else use companion-design edges on artifact metas |
| Declaring both ends of an inverse pair | Redundant, drifts out of sync | Declare once in canonical direction |
| Assuming a documentary/symmetric edge gets flipped | Wrong reverse navigation; phantom dedupe | Only named inverse pairs normalize; documentary/symmetric stored as-authored |
| Re-running a builder after the cross-layer matcher | Machine-injected cross-layer edges silently wiped | Run/re-run the matcher AFTER the last source-side builder run |
| Naive refresh-from-scratch | Destroys curated summary/keys/edges | Draft-by-default; preserve curated; UNION + re-filter keys |
| Over-long auto-extracted key list (scorer noise) | Generic tail keys dilute ranking precision | Heed the soft-budget lint WARN; tune stopword layers A/B in config; curate — do NOT rely on any truncation to clean up for you |
| Version/status marker inside a key NAME (`AIP v0.3 Conformance Checklist`) | Matching is WHOLE-query, so a token in the MIDDLE breaks the string: the key scores **0** for anyone typing the doc name without the version. Measured: 18 vs runner-up 17 — winning by one point | Keep one **clean-name** key; a version marker ADDS a separate key, never edits the name key. Old revisions use `status: superseded` (real ×5 ranking penalty), not words in the key. Lint WARN `meta_lookup_key_marker_midname` |
| Tuning stopwords in the tool body | Un-portable, un-refreshable, won't propagate | Tune in profile/config; refresh to propagate |
| Mis-tiering a mockup as source-of-truth | AI treats fake sample data as requirements | Lower tier + "NOT source of truth" caveat + sample-data stopwords |
| BOM injected by an editor write | Frontmatter parses empty → garbage index entry | Use an encoding-safe write path for metas (no byte-order-mark corruption) |
| Editing a script-written file without re-reading | "Modified since read"; accidental overwrite | Re-read after external writes; builders print paths written |
| Missing required builder args (prefix/subdir) | Hundreds of garbage metas; index spike | Always pass identifying args |
| Hand-patching individual metas for a systemic defect | Patch overwritten on next rerun | Fix the tool, rerun the root |
| Trusting self-test as acceptance | Lexical-only pass says nothing about task recall/relevance | Task simulation + HUMAN review is the real gate |
| Testing before rebuilding projections | Inspecting a stale index | Rebuild projections, then test |
| Fresh checkout restamps mtimes | Spurious staleness in the sync plan | HUMAN reviews the plan at the gate before any rebuild |
| Expecting transitive answers from relations | Wrong navigation; missed dependencies | One-hop only — walk multi-hop yourself |
| Re-running the manual full build for maintenance | Slow, churns metas, drops curated/injected edges | Use the whole-repo sync loop instead |
| Using the sync loop for the FIRST build | Wrong loop; gates designed for maintenance get in the way | First build calls builders directly / via the route registry; sync loop is maintenance-only |
| New doc TYPE / mixed-profile folder | Planner won't auto-register it | Covered-folders-only; new types need an initial HUMAN registration; mixed folders are flagged, never guessed |
| Fixture/hư cấu doc đăng ký dưới system THẬT | **Wiki poisoning**: trang overview/pages của system thật được grounding bằng tài liệu không tồn tại (sự cố OP-931-03: 3 RD hư cấu là requirement_definition DUY NHẤT của system `aiws`) | Fixture registered vào live index BẮT BUỘC dùng system id tổng hợp — khai `synthetic_systems:` trong `project_profile.yml`; lint `fixture_under_real_system` (ERROR) chặn tái phạm (CR-AIWS-2026-07-028) |

**Change-routing (3-way split).** Route every change to exactly one destination, never mixed:

| Change | Destination |
|---|---|
| **Wiki content** (object nodes, doc metas, edges) | Normal authoring → version control + the wiki maintenance log; **neither** change folder |
| **Local install tweak** that only tunes this project (a new builder, a profile, a build-route) | A lightweight **local change-log** entry |
| **Canonical/shared tooling** change you intend to propagate upstream | A formal **change request** with a status lifecycle + a dedicated apply step |

Rule of thumb: if a future project would also want the change, it's a propagatable change request; if it only tunes this project, it's a local change-log entry. For a **mechanism/install** change (node-model fields, validated vocabularies, builder/lint/index behavior), propagate to **every touchpoint together** — required-field sets, vocabulary/profile, index projection, the skill authoring example, the spec, and any CI fixture — or spec-correct metas will fail lint at the points you missed.

---

## Appendix E — Definition-of-Done + per-step checklist

**Definition of Done.**
> **lint clean → self-test all-PASS → the realistic task simulation surfaces the expected sources with healthy scores → every edge-bearing node resolves BOTH out- and in-edges.**

The fourth clause adapts by shape: **where object nodes exist** (code-heavy / mixed / seeded docs-only), they resolve BOTH out- and in-edges; **for docs-only builds with no identity layer**, substitute — **doc↔doc edges resolve in both directions and no edge is orphaned**. A structurally valid wiki that isn't actually navigable or discoverable is not done.

**Per-step checklist.**

| Step | Output artifact | Gate | Done when |
|---|---|---|---|
| 1 | BUILD LOG (goal/scope/purpose/shape/task list) | HUMAN confirms scope + purpose + shape + task-kind list | task-simulation cases drafted + HUMAN-signed |
| 2 | INVENTORY file (categorized) | HUMAN confirms in/out + source_type per group | every group decided IN or OUT |
| 3 | Authority/value/intended-use matrix | HUMAN confirms tiers (esp. SoT boundary) | every IN group tiered + caveats noted |
| 4 | Predicted-relations table | HUMAN confirms relation map | edge types/directions/derived-vs-authored agreed (incl. doc↔doc for docs-only) |
| 5 | Build plan | HUMAN reviews plan + per-group method | layers, methods, profiles, cadence, seeds set |
| 6 | Tool inventory + tool spec(s) + route entries | HUMAN directive per new bulk builder | each new builder spec'd + routed (docs-only: usually none) |
| 7 | Sample-run report | HUMAN approves sample format | samples lint clean + smoke-test pass |
| 8 | Refresh-test report | HUMAN confirms refresh preserves curated | curated preserved, config propagates, no edge loss |
| 9 | Mass-run spot-check report + wired relations | (fix-and-rerun loop) | all roots built, projections rebuilt, lint clean, edges wired (object nodes only where gated; else doc↔doc only) |
| 10 | Lookup-test report + profile updates | HUMAN reviews cap curation + task gaps | DoD met (lint/self-test/task-sim/relations); docs-only tests doc↔doc bidirectional |
| 11 | Project wiki build-up guideline **+ finalized lesson_learned** | HUMAN accepts the guideline **and triages lessons** | guideline generated from the BUILD LOG (role-based, footguns included; log archived as provenance); lesson_learned consolidated, targeted, and routed upstream (Appendix F) |
| — (cross-cutting) | LESSON LOG (`lesson-learned.md`) | HUMAN triages at Step 11 | every generalizable adjustment captured during Steps 1–10 with a target + scope + status |

**Drive the wiki by natural-language prompts that route to skills.** You drive the wiki by talking to the AI; phrasing routes to the right skill, which then runs the deterministic tools. Support every language the project's content/prompts actually use (often just one) if skills trigger on more than one. Consistent prompt vocabulary ensures the right deterministic flow runs instead of ad-hoc edits.

---

## Appendix F — `lesson_learned` & the improvement feedback loop

`lesson_learned` is the artifact that lets **this common guideline improve itself**. It is the curated, project-agnostic retrospective of adjustments made while building a wiki — its target is **this document** (and the shared tooling/profiles), **not** the project being built.

**Build log vs lesson log — keep them separate.**

| | BUILD LOG (`build-log.md`) | LESSON LOG (`lesson-learned.md`) |
|---|---|---|
| Scope | project-local, chronological — *everything* | curated — only what transfers to other projects |
| Question it answers | "what did we do, and why, on THIS project?" | "what should change in the reusable process/tooling next time?" |
| Primary consumer | Step 11 → the **project's** guideline | maintainer of **this common guideline** + shared tooling/profiles |
| Lifecycle | finalized + archived as the project guideline's provenance | triaged at Step 11, then routed upstream as candidate changes |

**Write a lesson entry when** you: (a) **deviate** from this guideline; (b) hit a **footgun not in Appendix D**; (c) **fix a tool or profile** in a way that would help other projects; (d) find a step's guidance **unclear, missing, or wrong**; or (e) discover a **better default** (a key-curation rule, a stopword class, a sample threshold). **Do NOT** log purely project-specific choices (a domain mapping, this project's tiers) — those stay in the build log.

**Entry format (one per adjustment):**
```
### LL-<n> — <short title>
- context:        <step / tool / profile / project shape>
- guideline said: <the expectation, or "silent / not covered">
- what happened:  <the adjustment / friction / deviation actually made>
- root cause:     <why>
- lesson:         <the project-agnostic takeaway>
- proposed change:<concrete edit> -> target: <§/Appendix here | tool ROLE | profile/config mechanism>
- scope:          common-guideline-doc | tooling | install
- status:         proposed | accepted | deferred | rejected | applied-upstream   (link the applied change)
```

**The feedback loop (how the common guideline gets better):**
1. Entries accumulate during the build (Steps 1–10) and are **consolidated at Step 11**.
2. HUMAN **triages** each `proposed` entry at the Step-11 gate, setting its status: **accept** (→ `accepted`), **defer** (→ `deferred`, revisit next revision), or **reject** (→ `rejected`).
3. Accepted entries become **candidate edits** to their target, applied under **candidate → review → apply**:
   - target = *this guideline (doc)* → edit the named section, citing the lesson as rationale;
   - target = *a tool or profile mechanism* → that is an **install/tooling change** (heavier governance than a doc edit; if it should reach other installs, raise it as a tooling change-request, not a silent edit).
4. Entries may be **batched across projects** before a revision, so a lesson seen on several projects outweighs a one-off.
5. Mark applied entries `applied-upstream` and link the resulting change, so the loop is **auditable** and a lesson is never "learned" twice.

> The lesson log also supplies the **project** guideline's *footguns-actually-encountered* section (Step 11) — but its defining job is the upstream loop above. Improving this common guideline is itself governed: **no silent rewrite** — a doc edit is candidate→review→apply; a tooling/profile change is an install-level change.

---

## Appendix G — Building the project's whole-repo refresh/sync command (the maintenance loop)

Steps 1–11 are the **first build**. This appendix is how to build the project's **own maintenance/sync command** (commonly `refresh-project-wiki-all`) that keeps the wiki current as the repo changes. It is **built per project, not shipped generic** — its planner is coupled to the project's source roots, source-types, builders, and cross-layer matcher (all fixed at Steps 5–6/9). **Maintenance ≠ first build:** different loop, different gates. Use this appendix as the **pattern**; adapt the tool/role names to your install.

**It REUSES the first-build tooling — it creates nothing new.** The maintenance command is pure **orchestration over the project-specific tools/skills produced during the first build** (`/aiws-wiki bootstrap`): the same bulk **builders** + **build-route registry** (Step 6), the same **cross-layer matcher** (Step 9), the same **source-type profiles** (Steps 3/5), the same per-file **register / refresh / deregister** skills, and the same **index/relations projectors** + **lint**. That reuse is exactly why it must be **built per project** (it is coupled to those artifacts) yet stays **thin** — it wires existing tools, it does not reimplement them. The only genuinely new piece is the **planner** (the deterministic check engine) that reads which of those roots/folders changed.

**Prerequisites (all produced by the first build):** the project's bulk builders + build-route registry (Step 6); the cross-layer matcher if any (Step 9); the source-type profiles (Steps 3/5); and source-backed metas that store `updated_at = source-file mtime` (so the change rule is precise).

**The check engine (planner ROLE).** A deterministic, **read-only planner** (e.g. a `plan_wiki_sync` tool) is the SINGLE source for "what changed": it scans the configured **source roots** + **covered doc folders** and emits a plan. **Change rule = file mtime > meta `updated_at`** (aware-UTC): unchanged ⇒ mtime == updated_at ⇒ NOT stale (precise, not sticky); changed (even same-day) ⇒ stale; meta missing/unreadable ⇒ stale. The plan carries: per source-root `needs_rebuild` + changed/new counts; source changed/new/**orphans**; covered doc folders, docs new (+ inferred profile), docs changed, doc **orphans**, mixed-profile folders. **Deletion source = the planner's orphans OR `lint` orphan-artifact — NEVER a naive "missing file" detector** (it mis-flags object-node sentinels as missing → inflated count, unsafe to deregister).

**Policy (fixed — do not loosen):**

| Layer | Scope | Apply mode |
|---|---|---|
| **source code** | rescan ALL configured roots (new + changed files) | **AUTO** — rerun the deterministic builder (tool-owned metas) |
| **documents** | only folders already covering ≥1 registered doc | **REVIEW-GATED** — candidate → HUMAN → apply |
| **deletions** | both layers | **GATED** via the deregister / orphan-sweep |

**The gated flow:**
1. **CHECK (read-only)** — run the planner → a full plan artifact (`_sync_plan_<stamp>`). Optional arg scopes it (`all` / `source-only` / `docs-only`).
2. **PRESENT PLAN + GATE 1 (mandatory)** — show roots to rerun, source orphans, covered folders, new/changed docs (+ inferred profile), orphans, and any **mixed-profile** folder; ask `all / source-only / docs-only / cancel`. Nothing destructive before OK.
3. **SOURCE AUTO-APPLY** (skip if docs-only) — rerun the builder **only for roots with `needs_rebuild=true`** (leave unchanged roots untouched → preserve their metas + edges). Builders are whole-root (to resolve edges) → gate at ROOT level. If 0 roots → skip steps 3–4 entirely.
4. **RE-LINK CROSS-LAYER EDGES (mandatory if any builder reran)** — rerun the cross-layer matcher AFTER the last builder. Builders regenerate `Related Sources` from scratch and **drop machine-injected cross-layer edges**; skipping this wipes them on every sync.
5. **DOCS REVIEW-GATED** (skip if source-only) — new docs → register (inferred profile; mixed-profile → ask, don't guess); changed docs (mtime > meta `updated_at` only) → refresh (respect the **Promotion HARD-STOP**). Apply only after HUMAN reviews the doc set; never auto-apply docs.
6. **DELETIONS RECONCILE** — every orphan (source + doc) through the deregister / orphan-sweep gate (its own HUMAN gate → archive + reproject + audit log). Not a Promotion CR (the file is already gone).
7. **REBUILD PROJECTIONS** — rebuild the index + relations projections; then **regenerate overview pages** (`build_wiki_overview.py` — per-system khi multi_system; final index rebuild chạy bên trong tool; CR-AIWS-2026-07-010) — bỏ bước này = lint WARN `overview_fingerprint_stale`; refresh the change-snapshot if your tools keep one.
8. **LINT + REPORT** — lint (treat warnings as errors); report metas rebuilt, docs registered/refreshed, orphans deregistered, lint result, and what was **skipped** (mixed-profile defers, uncovered folders, out-of-scope roots).

**Gates:** plan review (2); doc-apply — no silent rewrite, doc metas carry AI authoring (5); deregister STAGE-2 HUMAN gate (6); **Promotion HARD-STOP** (5) — a changed doc hitting a promotion trigger (deprecate / source-of-truth / split-merge) STOPs and needs a CR.

**Footguns (the ones that bite):**
- Rerunning a builder regenerates source metas from scratch → loses hand-edits AND tool-injected cross-layer edges → **re-run the matcher after** (step 4).
- A fresh `git checkout` restamps mtimes → the plan may over-report "changed" → HUMAN reviews at GATE 1.
- An editor write path that injects a BOM corrupts frontmatter → use an encoding-safe write path for metas.
- A naive missing-file detector mis-flags object-node sentinels as deleted → use planner orphans / lint orphan-artifact for deletions.
- This command **orchestrates**; for a single changed file use the per-file register/refresh skill, not the whole-repo loop.

**Build it per project.** Adapt the planner's source roots, the source-type set, and the cross-layer matcher to the project (from Steps 5–6/9). Ship it as a project-local `.claude/commands/refresh-project-wiki-all.md` (the thin orchestration) + a project planner tool (the deterministic check engine). Compose the existing AIWS reference tools — the change-detector + build-route registry (rerun source), the register/refresh/deregister skills (docs + deletions), the index/relations projectors, and lint — the orchestration calls them, it does not reimplement them. (Reference pattern, genericized; tool/role names are install-defined — see Appendix A.)
