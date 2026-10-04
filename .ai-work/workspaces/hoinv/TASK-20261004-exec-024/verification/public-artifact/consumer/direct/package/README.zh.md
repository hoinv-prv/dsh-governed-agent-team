---
description: "为受治理的 Team 成员附加可按需读取的持久 memory。"
kind: "package-reference"
---

# @vuhoi/gat-durable-agent

[English](README.md) | 中文

## 概述

Team 成员可以获取持久指导、读取单个 memory item 并提交未确认 candidate。每次请求都会在 prompt 渲染前刷新 memory catalog。所选 Host 要求精确的 mission/task 授权、专用 provider，以及每个 workspace 仅一个进程。确认 memory 的提交仍是独立 Host 操作。

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

在明确选择的 Host 中，将 [Durable profile](../gat-durable-profile/README.zh.md) 叠加到 [GAT profile](../gat-profile/README.zh.md) 之后。Host 提供 `serviceBindingKey` 和已验证的专用 provider/单 Host 声明。

公开组合入口为 `@vuhoi/gat-durable-agent/provider` 和 `@vuhoi/gat-durable-agent/composition`。读取有大小限制的普通 `team_members.durable.yaml` 文件，并明确指定 `fresh`、`workspace` 和 model route；无效声明会失败，不会回退到默认 roster。

-----

<a id="understand-the-implementation"></a>
## 理解实现

<details>
<summary>实现细节 — 点击展开</summary>

Binder 在创建成员前准备独占 workspace/name 所有权，在隔离状态下安装 generation-scoped contribution，并在异步 provider 调用前后检查授权。恢复使用持久 attachment record，而不重新读取 YAML。清理会立即撤销 contribution，仅在实际 provider 清理成功后释放所有权。Cordis service proxy 会被展开，以比较实际注册的 provider 身份。

</details>

-----

<a id="further-exploration"></a>
## 进一步探索

- [Binder 所有权](src/binder.ts)、[严格 initializer](src/initializer.ts)、[工具](src/tools.ts)。
- [Team runtime](../gat-core/README.zh.md) 与 [profile 层](../gat-durable-profile/README.zh.md)。

-----

<a id="model-experience"></a>
## 模型体验

### Durable memory 上下文

#### 模型看到的内容

Prompt 包含指导和 catalog metadata。`durable_agent_read_memory` 仅返回所选 item；`durable_agent_submit_candidate` 返回明确未确认的 candidate。

#### Token 影响

Catalog 刷新会替换同一所有者的 section。读取结果仅添加所请求的 body；candidate 结果添加有大小限制的 metadata。

#### KV Cache 影响

Catalog 变化可能改变 prompt 前缀。未变化的指导和 catalog 会保留该 section；持久 memory body 按需读取。

## 已知限制与延期工作

<a id="known-limitations-and-deferred-work"></a>

这些限制要求明确的 Host 所有权。

- 仅支持 WK API v1，固定在 `a8e215433ae050e36e0ba27205701be1a5f114a1` 和 Host `5c02ce9f3e44dfce3f87498f65cf684194ad4572`。
- 仅支持 workspace/fresh direct child；不支持 global 共享、分布式锁和确认 memory 的模型工具。清理失败会保持该身份隔离。

<a id="dev-note"></a>
### 开发备注

集成资格验证记录在 AIP-EXEC-022 中；部署需要单独批准。
