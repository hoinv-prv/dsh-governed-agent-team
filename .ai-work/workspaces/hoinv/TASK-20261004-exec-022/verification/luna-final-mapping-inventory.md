# Luna final mapping inventory

Read-only comparison of the AIP-EXEC-022 final production file set against `docs/gat-design/SOURCE_CODE_MAP.md`, `source-code-map.json`, `source-baseline.json`, Detail Design §§6/8, and `DURABLE_AGENT_INTEGRATION.md`. Wiki-first input resolution was performed by the active AIP. No source/design files were edited.

## Coverage and missing rows

The new implementation falls under these existing design rows, but the current map/baseline is incomplete:

- **DD-01 / DD-02 / DD-16:** `packages/core/src/member-host.ts` — production reserved-member host and binder ownership; `packages/core/tests/production-binding.spec.ts` — production lifecycle/admission coverage. `source-code-map.json` DD-16 currently stops at generic `member-binding.ts`/roster/mailbox and foundation tests; neither file is listed. `source-baseline.json` has no entry for either.
- **DD-15 / DD-16 / DD-17:** `packages/durable-agent/src/composition.ts`, `packages/durable-agent/src/provider.ts`, and `packages/durable-agent/tests/composition.spec.ts` — Cordis production composition/provider selection and composed-path tests. DD-15 lists the library initializer/binder/ownership/tools but omits these production files; DD-16 likewise omits composition, and no composed-path test is listed. Baseline has no entries.
- **DD-11 / DD-15 / DD-17:** `packages/durable-profile/package.json` and `packages/durable-profile/cordis.patch.yml` — opt-in Durable profile and Loader wiring. DD-11 currently names only `packages/profile` and `packages/web-profile`; DD-15/16 do not list the profile. Baseline has no entries.
- **DD-11 / DD-17:** additive selected-host distribution files: `installer/verify-binding.mjs`, `installer/verify-binding-exports.mjs`, `installer/verify-binding-runtime.mjs`, `installer/tests/binding-compatibility.test.mjs`, and `scripts/generate-binding-compatibility.mjs`. Existing DD-11 lists `installer/index.mjs` and the legacy generic compatibility/verify path, but not these files or the new test/generator. DD-17's mapped source set is the prerequisite repository and does not cover these GAT distribution files. Baseline has no entries for these additions. `installer/index.mjs` itself is already mapped and present in the baseline, but its changed selected-artifact behavior needs its current symbol/line/hash baseline refreshed.

The prose map's DD-15 production-gated and DD-16 foundation-only labels no longer describe the completed production composition. DD-11's “Current” row is incomplete for the new profile and changed-host distribution. Existing DD-01/02/16 coverage can remain; add the production rows/files and tests rather than treating the generic foundation tests as production qualification evidence.

## Stale status prose to reconcile

- `DETAIL_DESIGN.md` §6 says “Production status remains gated” and that core refuses nonempty attachments and has no supported profile/installer activation. §8 now describes the production implementation and its qualification, so §6 should be explicitly marked as the pre-§8 snapshot or have its present-tense status superseded.
- `SOURCE_CODE_MAP.md` Coverage and known gaps says DD-15 “production activation remains gated”; its DD-15 row says “production gated”; DD-16 says “production gated”. Update these to the final qualified implementation state, while retaining any deployment authorization boundary separately.
- `DURABLE_AGENT_INTEGRATION.md` “AIP-EXEC-022 foundation implementation” says production composition “remains unavailable” until prerequisites qualify and current core rejects required attachments. Its “Intended production composition” says remaining work connects the library to reserved children. Those are pre-implementation statuses superseded by §8 and final qualification; mark as historical/pre-§8 or update.
- `SOURCE_CODE_MAP.md` purpose paragraph says “Parent production binder/package/deployment qualification remains separate.” Binder/package qualification is now covered by the completed AIP-EXEC-022 final qualification; deployment remains separate. Narrow this sentence to deployment (and any explicitly unqualified external action).

Historical caveat: `DURABLE_AGENT_INTEGRATION.md` states that the older integration report preserves its pending-acceptance wording as original submitted bytes while the ledger records later acceptance. That is deliberately historical and should remain labeled as such, not rewritten as a current project status.

## Baseline implication

Of the requested paths, `source-baseline.json` currently contains only `installer/index.mjs`. All other listed new paths are absent. Refresh the map and baseline after final settled bytes so links, symbols, repository identity, and hashes match the qualified tree.
