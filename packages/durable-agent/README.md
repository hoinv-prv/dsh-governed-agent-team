---
description: "Attach selective persistent memory to governed Team members."
kind: "package-reference"
---

# @vuhoi/gat-durable-agent

English | [中文](README.zh.md)

## Summary

Team members can receive persistent guidance, read one memory item and submit an unconfirmed candidate. Each request refreshes its memory catalog before prompt rendering. The selected host requires exact mission/task authorization, a dedicated provider and one process per workspace. Confirmed memory commits remain separate host operations.

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

Apply the [Durable profile](../gat-durable-profile/README.md) after the [GAT profile](../gat-profile/README.md) in an explicitly selected host. The host supplies `serviceBindingKey` and verified dedicated-provider/single-host assertions.

The public composition entries are `@vuhoi/gat-durable-agent/provider` and `@vuhoi/gat-durable-agent/composition`. Load a regular bounded `team_members.durable.yaml` with explicit `fresh`, `workspace` and model routes; invalid declarations fail without default fallback.

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

### Durable memory context

#### What the model sees

The prompt contains guidance and catalog metadata. `durable_agent_read_memory` returns only the selected item; `durable_agent_submit_candidate` returns an explicitly unconfirmed candidate.

#### Token effect

Catalog refresh replaces one owner section. Read results add only the requested body; candidate results add bounded metadata.

#### KV Cache effect

A changed catalog can change the prompt prefix. Unchanged guidance and catalog preserve that section; persistent memory bodies are read selectively.

## Known Limitations and Deferred Work

<a id="known-limitations-and-deferred-work"></a>

These constraints require explicit host ownership.

- WK API v1 only, pinned to `a8e215433ae050e36e0ba27205701be1a5f114a1` and host `5c02ce9f3e44dfce3f87498f65cf684194ad4572`.
- Workspace/fresh direct children only; global sharing, distributed locking and confirmed-memory model tools are unsupported. Failed cleanup keeps the identity quarantined.

<a id="dev-note"></a>
### Dev Note

Integration qualification is recorded under AIP-EXEC-022; deployment requires separate approval.
