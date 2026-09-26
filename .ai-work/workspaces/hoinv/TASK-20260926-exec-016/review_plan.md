# Review Plan — GAT §§6.6, 6.9, and 7 Recheck

## Review shape
- Type: cross-document design/reference conformance review.
- Target: `docs/GAT_DESIGN_AND_FEATURE_REFERENCE.md`, only §§6.6, 6.9, and 7.
- Baselines: `/home/hoinv/work/dsh-durable-agent/DURABLE_AGENTS_MINIMVP.md`; current GAT `team-config.ts`, `index.ts`, and focused tests.
- Output contract: remaining material discrepancies only; otherwise `None.`

## Closed source-item universe
- HC-01 fallback scope
- HC-02 byte limit
- HC-03 route authority
- HC-04 SOUL ordering
- HC-05 per-task loading
- HC-06 manifest snapshots
- HC-07 restart admission
- HC-08 conditional sharing
- HC-09 filesystem ownership

## Related set and load order
1. Target §§6.6 and 6.9 (current GAT behavior and schema bridge).
2. Target §7 (boundary, target integration, failure/drift rules).
3. Durable MiniMVP §§Manifest schema, Workspace-local provisioning, Explicit global member, Stored files, Usage, Non-goals.
4. Current GAT `packages/experimental/gat-tools/src/team-config.ts`.
5. Current GAT `packages/experimental/gat-tools/src/index.ts` and focused tests.

## Cross-document edges
| Edge | Mandatory field/rule diff |
|---|---|
| GAT roster loader → target §§6.6/6.9 | failure classes, fallback scope, max UTF-8 bytes, accepted member keys, context default, count cap |
| Authorized manifest → Durable profile | name, description, prompt, context, provider, model, reasoning effort, storage scope, workspace binding |
| Host prompt assembly → Durable task context | governance authority, literal SOUL placement, member prompt, task context, selected memory |
| Session lifecycle → Durable access | canonical manifest snapshot/digest, profile revalidation, restart admission, degraded/fail-closed result |
| Workspace/global scope → shared access | explicit global declaration in every workspace, immutable profile equality, no implicit copy/share |
| Shared checkout tools → member-owned durable files | logical ownership versus filesystem isolation/locking/enforcement |

No edge may PASS with a renamed/dropped/source-unknown required rule.

## Entity-column read/write map
N/A: the scoped artifacts define configuration/runtime contracts, not an application entity/data-model interface. The equivalent closed field map is the manifest/profile edge above.

## Regions and order
1. Loader behavior: HC-01, HC-02.
2. Authority/schema: HC-03, HC-06.
3. Task context: HC-04, HC-05.
4. Lifecycle/sharing/ownership: HC-07, HC-08, HC-09.

## Execution method
For each item, apply a `consistency (cross_document)` field/rule diff plus `completeness` where the baseline mandates a behavior. Cite target, baseline, and implementation loci. Treat wording differences as non-material unless they change authority, admission, timing, scope, or safety behavior.
