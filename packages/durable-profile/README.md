---
description: "Select strict Durable memory binding for a governed Team profile."
kind: "package-bundle"
---

# @vuhoi/gat-durable-profile

English | [中文](README.zh.md)

## Summary

This explicit profile layer gives governed Team members persistent guidance and selective memory tools. It selects strict workspace declarations and a dedicated WK provider after the GAT host layer. No shipped default profile selects this layer. The owner must verify one host process per workspace and approve deployment separately.

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

Select `@vuhoi/gat-durable-profile` after `@vuhoi/gat-profile` in an isolated initialized profile. The package declares its Loader patch in `dsh.bundle.patch`; actual deployment needs separate owner approval.

The layer selects external Team initialization, one dedicated provider, one strict initializer and the required v1 binder. Member declarations require explicit workspace/fresh and model routes in `team_members.durable.yaml`.

-----

<a id="understand-the-implementation"></a>
## Understand the implementation

<details>
<summary>Implementation internals — click to expand</summary>

The [patch](cordis.patch.yml) replaces the Team initializer selection and inserts the adapter provider/composition entries. It retains the Team tool limits and inspection restrictions. The [adapter](../gat-durable-agent/README.md) owns refresh, tools and cleanup; the [core](../gat-core/README.md) owns exact authority and reserved-child admission.

</details>

-----

<a id="further-exploration"></a>
## Further Exploration

- [GAT profile](../gat-profile/README.md), [Durable adapter](../gat-durable-agent/README.md), [patch](cordis.patch.yml).

-----

<a id="model-experience"></a>
## Model Experience

### Durable memory context

#### What the model sees

The adapter owns `durable_agent_read_memory`, `durable_agent_submit_candidate` and catalog guidance. The Team tools own coordination schemas and policy; this layer adds no independent model text.

#### Token effect

Token use comes from the adapter guidance, catalog and tool results. Profile selection adds no separate prompt section.

#### KV Cache effect

Prefix stability follows the selected adapter catalog and Team policy. A changed catalog can invalidate the affected prompt prefix.

## Known Limitations and Deferred Work

<a id="known-limitations-and-deferred-work"></a>

These constraints require explicit host ownership.

- Apply after the GAT host layer; default initialization must not compete with the external initializer.
- Pinned WK v1 and reserved-child host only. This layer provides no distributed lock, isolated execution or deployment authority.

<a id="dev-note"></a>
### Dev Note

Integration qualification is recorded under AIP-EXEC-022; deployment requires separate approval.
