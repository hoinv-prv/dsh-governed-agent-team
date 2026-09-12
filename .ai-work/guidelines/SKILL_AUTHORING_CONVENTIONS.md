# Skill-Authoring & Maintenance Conventions (MVP)

> Canonical conventions for authoring/maintaining AIWS `SKILL.md` files. Established by **CR-AIWS-2026-06-032** (CAP-060-01 + CAP-058-01). Companion guard for the Object Kind Catalog: `Knowledge_Object_Model_Spec_MVP §3bis.1` (CAP-064-01).

## 1. Traceability separation — keep opaque codes out of AI action text  *(CAP-060-01)*

Opaque governance/decision codes — `#NN` (rule numbers), `DPn` (design principles), `INV-x` (invariants) — must **NOT** appear as **labels or identifiers inside AI action text** (the steps/instructions the AI executes). The AI reads such a tag as noise and may skip the step.

- **Evidence (HUMAN-ruled 2026-05-31):** a step labelled `… (#19)` was skipped because `#19` was read as noise, not as part of the instruction.
- **Rule:** move the codes to a dedicated **`## Traceability`** section at the end of the skill (code → the rule/decision/step it governs). The action text states *what to do*; the Traceability section records *which governance code it derives from*.
- **Acceptable exception — inline provenance citations.** A code in an end-of-rule parenthetical that cites *why* a rule holds (e.g. "never auto-build an object meta (DP6/INV-8)") is a citation, not a step-identifier. These may remain inline, but prefer `## Traceability` when several accumulate.
- **Precedent:** CR-AIWS-2026-05-038 (CR-038) introduced the `## Traceability` section in `aiws-wiki build-meta`/`aiws-wiki register`.

## 2. Skill 4-tree topology — body-edit only the full trees  *(CAP-058-01)*

| Tree | Role | Body-edit? |
|---|---|---|
| `.ai-work/procedural/skills/<skill>/SKILL.md` | **FULL** (live) | ✅ edit here |
| `product/procedural/skills/<skill>/SKILL.md` | **FULL** (canonical mirror) | ✅ mirror byte-identical |
| `.claude/skills/<skill>/SKILL.md` | **STUB** (pointer) | ❌ never body-edit |
| `product/skills/<skill>/SKILL.md` | **STUB** (pointer) | ❌ never body-edit |

- Edit the skill **body in the 2 FULL trees only**, byte-identical (`diff -q` clean). The 2 STUB trees are pointers to the full definition — never body-edit them.
- A SKILL.md body change is `no_cr` (tooling/procedural dual-tree edit-flow); a *convention* like this guideline is `cr_required`.

## 4. `description` = the skill-selection signal  *(CR-AIWS-2026-08-108)*

`description` is the **only** text an AI reads when deciding whether to invoke a skill — the body is
loaded only *after* the skill is chosen. A missing or contentless description therefore does not
degrade gracefully: the skill is either **never selected**, or **selected for the wrong request**.
Both fail silently.

### 4.1 Which tree owns it  *(DP-108-A = (b) — deliberate split)*

The §2 table is about the **body**. `description` follows a different rule, and this is the exception
that table does not state:

| Tree | Body | `description` |
|---|---|---|
| `.ai-work/procedural/skills/<skill>/` · `product/procedural/skills/<skill>/` (**FULL**) | ✅ edit here | **compact, but SELF-STANDING** |
| `.claude/skills/<skill>/` · `product/skills/<skill>/` (**STUB**) | ❌ never body-edit | ✅ **rich** — this is what Claude Code matches on |

- The STUB frontmatter carries the full NL trigger vocabulary, because that is the surface the
  harness registers and scores. Editing frontmatter there is **allowed**; editing the body is not.
- The FULL description must **stand on its own**. Do not write "see the shim" — the FULL tree is what
  `adapter_agents.md` / `adapter_copilot.md` point non-Claude tools at, and what the domain router
  itself tells a reader to open. Keep it compact: enough to pick the domain *and* the verb, not a
  copy of the stub's trigger list (that text is read inline every session).
- Both trees keep their own text byte-identical **within** their pair (`diff -q` clean).

### 4.2 Minimum bar (enforced)

A description must answer **what it does** and **when to use it**. "When" has two valid forms — pick
the one that matches who calls the skill:

- **Human-invocable** → quote the user's actual words as NL triggers, **VN and EN**
  (e.g. `"tạo AIP"`, `"run lint"`). Naming what it is *not* prevents the near-miss.
- **Called by another step** → say so explicitly: `NOT directly user-invocable — CALLED by …`.
  This counts as a full answer; such a skill needs no trigger list.
  (Note `user-invocable: false` is AIWS-only metadata — **Claude Code does not read it**, so those
  skills remain selectable and the prose is the only real guard.)

Enforced by `lint_wiki.py`:

| Rule | Level | Fires when |
|---|---|---|
| `skill_description_missing` | **ERROR** | key absent, or empty once the block scalar is parsed |
| `skill_description_thin` | **WARN** | no selection signal at all (any length); **or** trigger-style under **200** chars; **or** contract-style under **80** chars |

Two floors, because the two forms need different room: a trigger set has to fit VN + EN phrasings,
while a contract only has to state *what* and name its caller. Holding a caller-only skill to the
trigger-sized floor would contradict the paragraph above — so it doesn't.

`thin` stays a WARN: it is a heuristic about prose and must not gate a build.

### 4.3 Reading a description in a viewer — folded scalars

Long descriptions use a YAML **folded scalar**, so line 3 reads `description: >` with the text on the
indented lines below. A viewer that shows only the first line displays this as **blank**. It is not.
Verify with the parser, never by eye or by `grep '^description:'`:

```
py -c "import sys;sys.path.insert(0,'.ai-work/tooling');from _common import parse_frontmatter;print(parse_frontmatter(open('<SKILL.md>',encoding='utf-8').read())[0]['description'])"
```

Any tooling that reads this field **must** go through `_common.parse_frontmatter`. A hand-rolled
`^description:` regex returns the indicator character `>` and reports a healthy description as empty
— the bug `CR-AIWS-2026-08-063` fixed in `_read_block_scalar`, and the same illusion that made a
HUMAN report every description as blank (the driving observation behind CR-AIWS-2026-08-108).

## 3. Kind-vs-term guard (pointer)

When editing the Object Kind Catalog (`Knowledge_Object_Model_Spec_MVP §3bis.1`), a kind name may also be a `knowledge_target`/domain term (e.g. `business_rule`) — triage each occurrence by **role** (kind = edit; term = leave); never blind grep-replace. See that section's editing guard.

## Relationships
- `Knowledge_Object_Model_Spec_MVP §3bis.1` (kind-vs-term guard).
- `AIWS_Change_Request_Spec_MVP` (governs changes to this guideline; AIWS-Product-Owner approves).
- CR-AIWS-2026-06-032 (source), CR-AIWS-2026-05-038 (Traceability precedent), CR-AIWS-2026-08-108 (§4 `description`).
