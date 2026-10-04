# Source/design consistency — qualification checkpoint

Date: 2026-10-04. This is a limited qualification checkpoint, not final implementation acceptance.

Official GAT design consulted: `DETAIL_DESIGN.md` DD-09/DD-15/DD-16 and §§5/7/8, `BASIC_DESIGN.md` external binding flow, `DURABLE_AGENT_INTEGRATION.md`, `SOURCE_CODE_MAP.md`, and member-binding freeze §§2–4/8/12. External DA Architecture AD-02–05, Basic BD-02–05 and Detail DD-02–04/DD-06–09 preserve provider/consumer/Host ownership and per-call snapshots.

Changed design: prospective `DETAIL_DESIGN.md` §9, before the experimental test/config. It specifies public current GAT/WK qualification, per-request freshness/logging, and explicit missing-operation stop. Earlier accepted direct composition sections retain their original bytes; checkpoint manifest verifies the planning baseline prefix.

Experimental source exists only in `/tmp/gat-exec024-host-c1157f7e`: `packages/experimental/gat-core/tests/durable-binding-qualification.spec.ts` and `vitest.exec024.config.ts`. Exact copies are retained under this workspace `qualification/`. WK public lib and source-map source archive are copied unchanged to isolated `vendor/gat-qualification-wk/`; yaml 2.9.1 is reused. Test aliases intentionally select one Host Cordis 4.0.4 instance versus WK's declared 4.0.2; production peer compatibility is not accepted from this experiment.

GAT `packages/durable-agent/` production source/build/exports are unchanged. DSH core/loop/Team persistence and WK source/provider APIs are unchanged. The new production adapter is not implemented because the requested refresh invariant fails on current Host retry semantics. The result is consistent with §9's prospective gating, not a claim that the intended adapter contract has been delivered.

Runtime evidence, pending decision and unqualified areas reside in this workspace. Existing unrelated GAT installer/snapshot/manifest edits and DSH Mission Board/skill/tool edits remain outside this task. No accepted historical evidence is overwritten. AIP startup mutations are limited to status active, workspace provenance and imported preflight captures; no Done Criteria were ticked.
