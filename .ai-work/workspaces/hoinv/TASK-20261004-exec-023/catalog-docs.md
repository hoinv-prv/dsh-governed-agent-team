# Catalog documentation pairing

Updated the DSH Agent Note pair at `.agents/notes/proposed/process/2026-10-04-active-catalog-replacements.md` and `.agents/notes/proposed/process/2026-10-04-active-catalog-replacements.zh.md`, with its `.i18n.yaml` consistency record. The Chinese text preserves all sections and acceptance/risk clauses. The English and Chinese language switchers are present. The note remains `Status: proposed`; implementation qualification has not been reported to this task.

The scoped pairing write and check passed:

```text
node --import tsx/esm scripts/verify-translation-pairing.ts --write .agents/notes/proposed/process/2026-10-04-active-catalog-replacements.md
node --import tsx/esm scripts/verify-translation-pairing.ts .agents/notes/proposed/process/2026-10-04-active-catalog-replacements.md
```

Read DSH `AGENTS.md`, `docs/AGENTS.md`, `docs/i18n/README.md`, `docs/i18n/translation-rules.md`, and `docs/i18n/terminology.md`. Read GAT `docs/gat-design/DETAIL_DESIGN.md` §7 after wiki lookup resolved `SRC-GAT-DETAIL-DESIGN`.

Generated bilingual documentation implications from DSH `docs/i18n/README.md` §“Scope and exclusions” and `docs/AGENTS.md`:

- `docs/cordis-api/inherited.md` is the only generated catalog page explicitly excluded from pairing; do not create `.zh.md` or `.i18n.yaml` for it.
- `docs/persistence-catalog.md` is a generated English reference with a reviewed Chinese counterpart; if regeneration changes it, update `docs/persistence-catalog.zh.md` and re-record its existing `.i18n.yaml` pair.
- `scripts/gen-cordis-catalog.ts` updates generated `cordis-surface` regions in both English and Chinese subsystem pages. Those pages are paired, and the generator handles the region projection and pair records; avoid manual edits to generated regions.
- The client-slot catalog output is TypeScript (`packages/extensions/cordis-client-runner/src/client/slot-catalog.ts`), so it has no Markdown locale pair. The generated runtime Cordis API output is also TypeScript.
- The pairing rules require reviewed Chinese counterparts for generated English references whenever available; generators remain the English source of truth and freshness and pairing gates apply independently.

No generated outputs, source code, host docs, or GAT design files were edited by this task.

## Persistence catalog update

Compared `docs/persistence-catalog.md` against DSH baseline `c291e7961a515f6d7af9304e7fd1d257929aef26` and applied only the changed content to its existing Chinese counterpart. Added the new `agent/execution-reserved`, `subagent/initial-admission`, `team/member-add-approved`, `team/mission`, `team/plan-approved`, and `team/work` entries; synchronized the changed `agent/inbox/spliced`, `team/member`, `team/message/delivered`, `team/message/queued`, and `team/task` source/type declarations; and copied the updated `tool/ptc-dispatch-start` documentation comment verbatim. Existing Chinese prose was retained. The English generated file and generated TypeScript outputs were not edited.

Recorded and checked only the named persistence catalog pair. The check passed. Command outputs are in `verification/catalog-persistence-pair.log`.
