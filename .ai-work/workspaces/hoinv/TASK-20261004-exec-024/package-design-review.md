# Independent WK dependency classification review

Reviewer: `/root/review_contract_design`. Date: 2026-10-04. Bounded review before package mutation; no production or formal design files changed. No compatibility exemption, Host bypass, provider modification or live activation authorized.

## Verdict

**APPROVED: move `@deepseek-ai/dsh-durable-agent: "0.1.0"` from `peerDependencies` into `dependencies` of `@vuhoi/gat-durable-agent`, preserving the exact version and selected WK artifact.** This is the smallest plugin-only metadata correction. Replace the temporary exemption paragraph in official Detail Design section 10 before applying the manifest change. Keep all actual DSH runtime peers and every existing public export intact.

The WK package is an independently versioned runtime library consumed by the adapter: `src/provider.ts` imports its public `LocalDurableAgentProvider` and constructs the service itself; direct/execution Consumers and pure review helpers use the same package. The WK manifest has version `0.1.0`, public library subpath exports, dependencies on Cordis `4.0.2` and yaml `2.9.1`, and no DSH runtime peer. Its ability to act as a Cordis plugin does not make its independent release number a DSH Host compatibility requirement.

## Inspected evidence

- Official `docs/gat-design/DETAIL_DESIGN.md` section 10, including ports/configuration/build, the optional review port and the temporary snapshot exemption proposal; preserved sections 5/7/8 and member-binding freeze sections 1–3. This metadata relocation changes no lifecycle, authority, required-attachment or storage owner.
- `packages/durable-agent/package.json`, `src/provider.ts`, `src/execution-binding.ts`, `src/composition.ts`, `src/binder.ts` and `tsdown.config.ts`.
- Exact public WK package manifest and `src/{index,service,consumer}.ts` at `/home/hoinv/work/dsh-durable-agent/durable-agent-plugin/`; selected Host vendored WK manifest.
- Actual Host `packages/boot/app-boot/src/plugin-compatibility.ts`: `evaluatePluginCompatibility` checks only `@deepseek-ai/dsh` / `@deepseek-ai/dsh-*` **peer** ranges against the Host version. It does not interpret an ordinary dependency's independently versioned API as a runtime peer requirement.
- Installed tsdown dependency policy in `node_modules/tsdown/dist/format-DMceewlS.mjs`, `getProductionDeps`: both dependencies and peerDependencies enter the production-dependency set. Existing emitted adapter entries retain public WK imports rather than embedding its service class.

Read-only executable check: imported the actual Host compatibility evaluator, read the unchanged adapter manifest, relocated the WK property in an in-memory clone, and evaluated both with empty exemptions and runtime `0.1.7-rc.2`. Original result reports only `@deepseek-ai/dsh-durable-agent: 0.1.0` incompatible, `exempted: false`; proposed clone is compatible and retains exact dependency `0.1.0`. No manifest, Host policy or profile was mutated by this check.

## Identity and duplication contract

Moving dependency classification does not itself create a second provider or grant any capability. The selected GAT provider and adapter entries reside in one package and must resolve the same installed WK module. Preserve WK externalization through the joint build; do not inline separate service classes or Consumers into different entry bundles. Preserve one emitted GAT ownership coordinator module shared by root/direct/execution entries.

The execution binding currently requires the registered unwrapped provider to be `instanceof` the imported `DurableAgentService`, then checks API/features and exact identity. A provider supplied by a distinct WK module copy can correctly fail that check even if its version string matches. Do not weaken this check to accommodate accidental duplicate installations. Instead qualify the package resolution and use the provider entry from the same adapter artifact. The provider entry already rejects an existing `durableAgent` registration; loading a second provider is not part of this fix.

WK root and `/service` must expose the same service constructor, and `/consumer` must resolve within that same selected package. All entries must preserve opaque ref ownership by the actual service. Cordis `4.0.2` versus the Host's qualified framework version remains a real integration constraint; relocating metadata neither resolves nor expands its tested compatibility. Current framework tracing uses the public `Symbol.for('cordis.original')`, but that fact alone is not proof of full cross-version compatibility.

The exact private WK artifact must remain resolvable through the selected vendored/packed dependency closure. A bare `0.1.0` string is not proof of artifact provenance or public-registry availability. Preserve the existing pinned source/package hashes and use the supported existing dependency resolution arrangement; do not fetch a same-named substitute, rewrite WK metadata, or silently change package-manager overrides.

## Required verification after the correction

1. Run actual Host compatibility/preflight on the resulting manifest with no exemption and unchanged genuine DSH peers; launch the shipped keyless CLI/profile route under that policy.
2. Inspect/rebuild the emitted and packed artifact: public WK imports remain external; root/direct/provider/execution exports and declarations resolve; one ownership chunk remains shared. Check installed resolution and actual provider constructor identity, not only manifest strings.
3. Run the real provider + execution Loader scenario from that artifact and focused existing direct-export/composition regressions on their compatible accepted Host. No source API or runtime behavior change is intended; a previous 48-test result is not automatically relabeled as a test of a changed installation graph.
4. Update only applicable package/distribution dependency metadata and exact artifact evidence. Preserve the WK pin, provider bytes and ordinary DSH compatibility policy. Live activation stays excluded.

This is a correction of dependency ownership, not acceptance of incompatible Host code. No risk-exemption workflow is needed for this proposed classification. Final installed behavior still requires the stated artifact/Loader evidence; this review does not claim those post-change checks have already passed.
