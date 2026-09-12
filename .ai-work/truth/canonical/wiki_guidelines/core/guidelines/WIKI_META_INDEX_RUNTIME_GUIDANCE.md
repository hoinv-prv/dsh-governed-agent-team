# WIKI_META_INDEX_RUNTIME_GUIDANCE_v0_9_8

Status: Canonical runtime guidance  
Version: v0.9.8  
Date: 2026-04-26  
Compatibility baseline: AIWS MVP v0.9.2 Wiki Source Meta / Index mechanism

---

## 1. Purpose

This document explains how AI should use Wiki Source Meta / Wiki Source Index during runtime.

It preserves current v0.9.2 field names and tooling.

---

## 2. Runtime flow

```text
Current context / Workspace / current task state
  ↓
Clarify task intent if needed
  ↓
Use Task Lens to shape access when applicable
  ↓
Run lookup_wiki_source.py or inspect Wiki Source Index
  ↓
Review candidate source records
  ↓
Open meta_locator
  ↓
Read Wiki Source Meta
  ↓
Check Summary / Knowledge Targets / Lookup Keys / Hints / Cautions
  ↓
Open artifact_locator only when details/evidence are needed
  ↓
(OPT-IN) IF intent needs impact / reverse / neighbours:
   wiki_relations.py --relations <source_id>  → out-edges + IN-edges ("who points AT it")
  ↓
Use artifact/source in task
```

---

## 3. Lookup command

```bash
python .ai-work/tooling/lookup_wiki_source.py --query "<keyword>"
```

Useful query order:
1. task intent term
2. function/screen ID
3. business term
4. Japanese/English term
5. artifact family term
6. known alias

---

## 4. Meta-first rule

After lookup, AI consults the meta's ORIENTATION value-add — preferably via the reader (skips what the index already carries):

```bash
python .ai-work/tooling/wiki_meta.py --view <source_id>
```

Read (the value-add): **Summary** (full) · **Source-Specific Hints** (how to use) · **Cautions** (trust) · a **Related Sources signal** (out-edge count + relationship_type breakdown + a `wiki_relations.py --relations` pointer — `--view` does NOT print the full out-edges; the signal is **out-only**, so reverse/impact still needs `wiki_relations` — CR-AIWS-2026-06-054).
Do NOT re-read **Lookup Keys** / **Knowledge Targets** — already seen at lookup (the reader skips them).

> **Tenet (CR-AIWS-2026-05-024):** a meta is an **AI orientation surface** — understand the artifact + decide the next
> action — NOT human prose. Keep it terse; the reader strips index-duplicated sections so meta-first stays cheap.

Then decide whether to open `artifact_locator` — use **Source-Specific Hints** to open the RIGHT section, not the whole file.

---

## 4.1. Relations — opt-in reverse / impact (CR-AIWS-2026-05-022)

`## Related Sources` in the meta gives the node's **out-edges** (authoritative). At `wiki_meta.py --view` those
out-edges appear as a **signal** (count + relationship_type breakdown + a `--relations` pointer), NOT the full list —
out-only (CR-AIWS-2026-06-054); the full out-edges are served by `--expand`. IF the task intent needs the
**reverse** view — impact ("who points AT this / who calls it"), what-feeds-this, or neighbours — that is NOT in the
meta (and `out-count == 0` does NOT imply "no relations" — in-edges may exist). Use the opt-in projection query
(one-hop, additive; `lookup_wiki_source.py` unchanged):

```bash
python .ai-work/tooling/wiki_relations.py --relations <source_id>   # out-edges + IN-edges (reverse / impact)
python .ai-work/tooling/wiki_relations.py --expand   <source_id>   # meta out-edges only (authoritative)
```

Opt-in per intent — discovery-only intents skip it. Spec: Knowledge_Relationship Spec v0.4 §6A.

---

## 5. Artifact locator rule

`artifact_locator` points to the AIWS-readable source artifact.

For non-text original files, this should be the converted markdown/source representation.

AI should not directly read original non-text raw files.

---

## 6. Source representation quality issue

If the markdown/source representation is insufficient for the task, classify as:

```text
source_representation_quality_issue
```

AI should:
- state limitation
- explain what cannot be verified
- request better conversion or HUMAN confirmation
- avoid unsupported inference

---

## 7. Rebuild and verify rule

After meaningful meta update:

```bash
python .ai-work/tooling/build_wiki_source_index.py --scope project
python .ai-work/tooling/lookup_wiki_source.py --query "<verification keyword>"
```

Do not edit generated index files manually.

---

## 8. Lightweight maintenance vs controlled promotion

Lightweight maintenance:
- add lookup key
- fix typo
- update Summary
- correct artifact_locator
- add simple caution

Controlled Knowledge Promotion:
- set source_of_truth
- change source_id
- split/merge meta
- broad optional enrichment
- major status/authority changes

---

## 9. Guardrails

- Wiki-first, not Wiki-only.
- Meta first, artifact when needed.
- Preserve current field names.
- Use existing sections before adding new fields.
- Do not change index schema/tooling in MVP.
- Do not set source_of_truth without HUMAN instruction.
