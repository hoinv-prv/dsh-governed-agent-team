---
description: "为受治理的 Team profile 选择严格 Durable memory 绑定。"
kind: "package-bundle"
---

# @vuhoi/gat-durable-profile

[English](README.md) | 中文

## 概述

该显式 profile 层为受治理的 Team 成员提供持久指导和按需 memory 工具。它在 GAT Host 层之后选择严格 workspace 声明和专用 WK provider。随附默认 profile 均不选择本层。所有者必须验证每个 workspace 仅一个 Host 进程，并单独批准部署。

## 目录

- [使用本包](#use-this-package)
- [理解实现](#understand-the-implementation)
- [进一步探索](#further-exploration)
- [模型体验](#model-experience)
- [已知限制与延期工作](#known-limitations-and-deferred-work)
- [开发备注](#dev-note)

-----

<a id="use-this-package"></a>
## 使用本包

在已初始化的隔离 profile 中，于 `@vuhoi/gat-profile` 之后选择 `@vuhoi/gat-durable-profile`。本包通过 `dsh.bundle.patch` 声明 Loader patch；实际部署需要所有者单独批准。

本层选择外部 Team 初始化、一个专用 provider、一个严格 initializer 和必需的 v1 binder。`team_members.durable.yaml` 中的成员声明必须明确指定 workspace/fresh 和 model route。

-----

<a id="understand-the-implementation"></a>
## 理解实现

<details>
<summary>实现细节 — 点击展开</summary>

[Patch](cordis.patch.yml) 替换 Team initializer 选择并插入 adapter provider/composition 入口。它保留 Team tool 限制和 inspection 限制。[Adapter](../gat-durable-agent/README.zh.md) 负责刷新、工具与清理；[Core](../gat-core/README.zh.md) 负责精确授权和 reserved-child admission。

</details>

-----

<a id="further-exploration"></a>
## 进一步探索

- [GAT profile](../gat-profile/README.zh.md)、[Durable adapter](../gat-durable-agent/README.zh.md)、[patch](cordis.patch.yml)。

-----

<a id="model-experience"></a>
## 模型体验

### Durable memory 上下文

#### 模型看到的内容

Adapter 负责 `durable_agent_read_memory`、`durable_agent_submit_candidate` 和 catalog 指导。Team tools 负责协作 schema 和 policy；本层不添加独立模型文本。

#### Token 影响

Token 用量来自 adapter 指导、catalog 和 tool result。Profile 选择不添加单独 prompt section。

#### KV Cache 影响

前缀稳定性取决于所选 adapter catalog 和 Team policy。Catalog 变化可能使相关 prompt 前缀失效。

## 已知限制与延期工作

<a id="known-limitations-and-deferred-work"></a>

这些限制要求明确的 Host 所有权。

- 在 GAT Host 层之后应用；默认初始化不得与外部 initializer 竞争。
- 仅支持固定 WK v1 和 reserved-child Host。本层不提供分布式锁、隔离执行或部署授权。

<a id="dev-note"></a>
### 开发备注

集成资格验证记录在 AIP-EXEC-022 中；部署需要单独批准。
