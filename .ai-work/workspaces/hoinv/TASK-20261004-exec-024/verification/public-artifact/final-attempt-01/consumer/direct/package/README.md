---
description: "Attach selective persistent memory to governed Team members."
kind: "package-reference"
---

# @vuhoi/gat-durable-agent

English | [中文](README.zh.md)

## Summary

The direct-continuable entry supplies persistent guidance, selective reads and unconfirmed candidate submission, with a refreshed catalog before prompt rendering. The fresh execution entry retrieves task-selected memory through tool results and supplies no memory system prompt. Both require exact authorization, a dedicated provider and one process per workspace. Confirmed memory commits remain separate host operations.

## Table of Contents

- [Use this package](#use-this-package)
- [Understand the implementation](#understand-the-implementation)
- [Further Exploration](#further-exploration)
- [Model Experience](#model-experience)
- [Known Limitations and Deferred Work](#known-limitations-and-deferred-work)
- [Dev Note](#dev-note)

-----

<a id="use-this-package"></a>
## Use this package

For direct-continuable members, apply the [Durable profile](../gat-durable-profile/README.md) after the [GAT profile](../gat-profile/README.md) in an explicitly selected host. The host supplies `serviceBindingKey` and verified dedicated-provider/single-host assertions.

The public composition entries are `@vuhoi/gat-durable-agent/provider` and `@vuhoi/gat-durable-agent/composition`. Load a regular bounded `team_members.durable.yaml` with explicit `fresh`, `workspace` and model routes; invalid declarations fail without default fallback.

### Fresh task executions

The additive `@vuhoi/gat-durable-agent/execution-composition` entry targets the qualified isolated-execution Host `c1157f7ed448b40c463c1a43fa595b12294fd50d`. Load the provider and this named Cordis plugin with explicit configuration:

```yaml
workspace: /existing/host-owned/workspace
dedicatedProvider: true
singleHostWorkspace: true
members:
  - mode: task
    declaration:
      name: worker
      description: Task memory worker
      prompt: Role instructions
      context: fresh
      scope: workspace
      provider: host-selected-provider
      model: host-selected-model
limits:
  maxBodyBytes: 4096
  maxResultBytes: 8192
  maxSelectedItems: 8
  maxReadCalls: 8
  maxReadResultBytes: 32768
```

The Host must verify the dedicated provider and single-process workspace topology before supplying these assertions. Declarations match the exact assigned member name and use explicit model routes. The task brief selects permitted items through `durable-memory:<id>` inputs. Only an explicit native `durable_agent_read_memory` call retrieves a selected body; ordinary requests add no memory guidance, catalog or body to the system prompt. Unselected items, nested calls, expired executions and changed owners fail closed. No memory write or candidate tool is installed.

Explicit `reviewer` mode requires a host-provided `gatDurableReviewInput` implementing the exported `ReviewInputPort`. It resolves one revisioned `review-packet:` input from approved contract/candidate/receipt/ACL data and supplies current authorization checks and durable audit. Its synchronous `subscribeRevocation(cutoff)` must notify before authorization, candidate or ACL withdrawal and return a synchronous disposer. Port replacement and revocation cancel the exact Agent; retained request guards deny stale retries. Reviewer tools read bounded packet, evidence and rationale; `team_execution_submit` returns a provisional result. Task acceptance and approved-input preparation remain external Host operations. Missing or stale trusted input fails before model transport.

This entry reuses public WK services and GAT assignment/settlement without DSH Core changes. Bootstrap sessions receive no binding. Cutoff cancels admission, joins admitted callbacks and releases physical references; failed cleanup retains exclusive ownership quarantine. Live activation requires a separately approved concrete workflow/profile/provider/storage proposal. Qualification and the recorded headless snapshot are tracked by AIP-EXEC-024.

-----

<a id="understand-the-implementation"></a>
## Understand the implementation

<details>
<summary>Implementation internals — click to expand</summary>

The binder prepares exclusive workspace/name ownership before member creation, installs generation-scoped contributions while quarantined and checks authority around asynchronous provider calls. Recovery uses persisted attachment records rather than YAML. Cleanup withdraws contributions immediately and releases ownership only after physical provider cleanup succeeds. Cordis service proxies are unwrapped to compare the actual registered provider identity.

</details>

-----

<a id="further-exploration"></a>
## Further Exploration

- [Binder ownership](src/binder.ts), [strict initializer](src/initializer.ts), [tools](src/tools.ts).
- [Team runtime](../gat-core/README.md) and [profile layer](../gat-durable-profile/README.md).

-----

<a id="model-experience"></a>
## Model Experience

### Direct-continuable memory context

#### What the model sees

The prompt contains guidance and catalog metadata. `durable_agent_read_memory` returns only the selected item; `durable_agent_submit_candidate` returns an explicitly unconfirmed candidate.

#### Token effect

Catalog refresh replaces one owner section. Read results add only the requested body; candidate results add bounded metadata.

#### KV Cache effect

A changed catalog can change the prompt prefix. Unchanged guidance and catalog preserve that section; persistent memory bodies are read selectively.

### Fresh execution task inputs

#### What the model sees

Task mode exposes only the selected native memory-read tool. Explicit reviewer mode exposes bounded packet/evidence/rationale reads and provisional submission. Neither mode contributes memory guidance, catalog or body to the system prompt.

#### Token effect

Authorized tool results add bounded selected bodies or reviewer evidence to the execution conversation. Ordinary task requests perform no memory-context read.

#### KV Cache effect

Memory retrieval leaves the system prefix unchanged. Tool-result history grows within the fresh execution; a subsequent assignment uses a separate conversation.

## Known Limitations and Deferred Work

<a id="known-limitations-and-deferred-work"></a>

These constraints require explicit host ownership.

- WK API v1 only, pinned to `a8e215433ae050e36e0ba27205701be1a5f114a1`. Direct entry Host: `5c02ce9f3e44dfce3f87498f65cf684194ad4572`; fresh execution entry Host: `c1157f7ed448b40c463c1a43fa595b12294fd50d`.
- Both entries require workspace/fresh members. The direct entry binds direct continuable children; execution mode binds exact assigned task Sessions. Global sharing, distributed locking and confirmed-memory model tools are unsupported. Failed cleanup keeps the identity quarantined.
- Source subpaths are workspace development routes. Packed runtime interfaces are the four public entries and their emitted declarations; source files and compiler caches are not an installation contract.

<a id="dev-note"></a>
### Dev Note

Integration qualification is recorded under AIP-EXEC-022; deployment requires separate approval.

For the combined artifact, compile the direct `tsconfig.json` on its pinned compatible Host and `tsconfig.execution-conformance.json` on the pinned current Host. Both Host package source mirrors must match this repository. Assemble their emitted graphs in a fresh directory under the current Host using the installed build tool:

```sh
node scripts/assemble-durable-agent.mjs \
  --direct-host /path/to/direct-host \
  --execution-host /path/to/current-host \
  --out /path/to/current-host/artifacts/gat-durable-agent \
  --tsdown /path/to/installed/node_modules/.bin/tsdown \
  --tsc /path/to/installed/node_modules/typescript/bin/tsc
```

The command checks commits/source/shared emitted modules, bundles all entries once, and writes `assembly-receipt.json`. Keep the complete emitted chunk set together. Run packed Node/Loader checks and the owning headless snapshot against these exact bytes before proposing installation. The current Host supports provider/execution entries; existing direct entries are qualified on the direct Host. This command performs no installation or live activation.
