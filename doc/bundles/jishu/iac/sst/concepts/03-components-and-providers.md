---
type: Concept
title: "组件与 provider 边界"
description: "区分项目初始化 provider、Pulumi provider components 与 SST 高层组件，并限定官网 provider 总量陈述的统计口径。"
tags: [SST, components, providers, Pulumi, AWS, Cloudflare]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-10-20T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-10-20T00:00:00Z" }
status: draft
stale_after: 2027-10-20
sources:
  - id: source
    resource: /references/source-v4.17.2.md
    title: SST v4.17.2 固定源码快照
  - id: docs
    resource: /references/official-docs-2026-10-20.md
    title: SST 官方文档（2026-10-20 采集）
---

# 组件与 provider 边界

SST 中的“provider”会出现在不同抽象层。理解组件生态前，先把项目初始化接口、Pulumi provider 资源与 SST 高层组件分开；名称相近不表示它们属于同一接口。

## 三种不同角色

| 名称 | 本教程证据 | 能确认的职责边界 |
|---|---|---|
| 项目 provider | `pkg/project/provider` 定义 `Home` 与 `Provider` 接口，并包含 AWS、Cloudflare 实现文件（F-012–F-014） | Home 接口含 bootstrap、按 key/app/stage 读写删除数据及 passphrase 等方法；Provider 接口声明 `Init(app, stage, args)` 与 `Env()` |
| Pulumi provider | 官方 Providers 页面说明 SST 基于 Pulumi/Terraform，并说明添加 provider 的方法（W-006、W-007） | 作为官网描述的底层 provider 扩展面；本教程不据此穷举 provider API |
| SST 高层组件 | 官方 Components 页面区分 built-in components 与 provider components（W-004、W-005） | 页面称高层组件可由较低层 provider resources 组合，并列出 `sst.aws.*`、`sst.cloudflare.*` 组件命名空间 |

项目 provider 接口可在固定源码中核对：[接口定义](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/pkg/project/provider/provider.go#L23-L46)。AWS 与 Cloudflare 的项目 provider 实现文件也存在于该快照（F-014，[AWS](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/pkg/project/provider/aws.go)、[Cloudflare](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/pkg/project/provider/cloudflare.go)）。这些事实不能替代对 Pulumi 资源 provider 的独立说明。

## 平台组件命名空间

v4.17.2 的 `platform/src/components/index.ts` 导出 `aws`、`cloudflare`、`vercel` 命名空间及其他组件导出（F-021，[源码](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/platform/src/components/index.ts#L1-L4)）。官方 Components 页面则描述 `sst.aws.*` 与 `sst.cloudflare.*` built-in namespace，并说明其内部使用 Pulumi AWS 与 Cloudflare provider（W-005）。

这两类资料回答的问题不同：源码导出表证明特定快照的模块导出；官网说明帮助读者理解当前产品文档中的使用方式。不能仅根据源码 namespace 数量推断 SST 支持的全部云 provider 数量。

## Provider 总量如何表述

2026-10-20 查阅的 Providers / provider directory 页面宣称支持 “150+ providers”，并介绍使用 `sst add <provider>` 添加 provider（W-006，[Providers](https://sst.dev/docs/providers/)、[directory](https://sst.dev/docs/all-providers#directory)）。这是官网采集日的产品陈述，不是本教程对固定源码仓库的计数结果。

实际选型时，应以项目需求、当前官方 provider 目录、版本锁定和凭证配置为准。官方页面说明 provider 版本可在 `sst.config.ts` 配置，并介绍 credentials 设置方式（W-007）；本教程不对具体 provider 的参数、费用或资源覆盖作穷尽说明。

## 相关概念

- [SST 应用模型与阅读边界](/concepts/00-application-model.md)
- [运行时、RPC 与平台程序](/concepts/04-runtime-server-architecture.md)
- [资源链接与 SDK 数据边界](/concepts/05-resource-linking.md)
- [最小应用与组件示例](/examples/01-minimal-component-app.md)
