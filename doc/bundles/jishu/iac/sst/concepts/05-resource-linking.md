---
type: Concept
title: "资源链接与 SDK 数据边界"
description: "沿 Linkable、平台环境变量转换和 JavaScript SDK Proxy 追踪 SST 资源链接信息如何进入应用运行时。"
tags: [SST, linking, SDK, environment, JavaScript]
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

# 资源链接与 SDK 数据边界

SST Resource Linking 把基础设施资源暴露的信息带入应用 runtime code。官网将使用过程概括为创建资源、通过 `link` 属性关联、再由 runtime 使用 SDK 访问（W-008，[Linking 页面](https://sst.dev/docs/linking/)）。v4.17.2 源码进一步显示，这条跨边界数据路径包含 Linkable 数据、环境变量序列化与 JavaScript SDK 解析。

## 固定源码中的数据流

### 1. 资源声明 Linkable 数据

`Link.Linkable` 接口要求 `urn` 与 `getSSTLink()`；`Link.isLinkable()` 检查对象是否包含 `getSSTLink` 属性（F-023，[源码](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/platform/src/components/link.ts#L97-L105)）。Link 构建逻辑读取该方法返回的数据，并将 properties 与 URN 末段名称组合为链接信息（F-024，[源码](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/platform/src/components/link.ts#L112-L129)）。

### 2. 平台将属性转成环境变量

`Link.propertiesToEnv()` 将每个链接属性序列化为 `SST_RESOURCE_<key>` 环境变量，并增加包含 app name 与 stage 的 `SST_RESOURCE_App`（F-025，[源码](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/platform/src/components/link.ts#L159-L174)）。

`Linkable` 类提供 `getSSTLink()`、静态 `wrap()` 与 `env()`；`wrap()` 将 `getSSTLink` 写入被包装资源类的 prototype（F-026，[源码](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/platform/src/components/linkable.ts#L182-L208)）。一个代表性实现是 AWS `Function`，它实现 `Link.Linkable` 并读取被链接资源的 `getSSTLink()`（F-027，[接口实现](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/platform/src/components/aws/function.ts#L1713-L1748)、[链接读取](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/platform/src/components/aws/function.ts#L1898-L1915)）。

### 3. JavaScript SDK 读取链接数据

JS SDK 的 `loadResourceEnvironment()` 扫描 `SST_RESOURCE_` 前缀的字符串环境变量并解析 JSON 值（F-028，[源码](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/sdk/js/src/resource/shared.ts#L21-L36)）。`createResource()` 返回 Proxy；对未链接属性的读取会按源码逻辑报错，并提示 SST links 未激活的上下文（F-029，[源码](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/sdk/js/src/resource/shared.ts#L40-L76)）。

因此，这条路径可以概括为：

**Linkable 资源 → `getSSTLink()` 数据 → `SST_RESOURCE_*` 环境变量 → JS SDK 解析 → Resource Proxy**

关键点是跨进程边界传递的是序列化数据，而不是将 Pulumi 资源对象直接交给业务代码。

## 产品用法与语言范围

官方 Linking 页面介绍了 `sst.Linkable`、`Linkable.wrap`、`Linkable.env()`，并称 `sst dev` 可将链接资源加载到本地开发环境（W-009）。API 具体用法以官网页面为该采集日期的产品文档；本文源码数据流则限定于 v4.17.2 的 JS SDK 与平台组件实现。

SDK reference 页面列出 JavaScript/TypeScript、Python、Go、Rust 的资源访问说明（W-012）。本篇只追踪已核验的 JavaScript SDK 源码路径，不把该页面的语言列表当作四种 SDK 源码均已在本教程中逐项分析。

## 相关概念

- [组件与 provider 边界](/concepts/03-components-and-providers.md)
- [运行时、RPC 与平台程序](/concepts/04-runtime-server-architecture.md)
- [资源链接到 runtime 示例](/examples/02-link-resources-to-runtime.md)
