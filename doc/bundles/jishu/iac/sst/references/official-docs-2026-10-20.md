---
type: Reference
title: "SST 官方文档（2026-10-20 采集）"
description: "登记本教程使用的 SST 官方 Basics、Components、Providers、Linking、CLI、SDK、Live、Console 与 State 页面及其时点口径。"
tags: [SST, official-docs, documentation, 官网资料]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-10-20T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-10-20T00:00:00Z" }
status: stable
stale_after: 2027-04-20
sources:
  - id: basics
    resource: https://sst.dev/docs/
    title: SST Basics
  - id: components
    resource: https://sst.dev/docs/components/
    title: Components
  - id: providers
    resource: https://sst.dev/docs/providers/
    title: Providers
  - id: provider-directory
    resource: https://sst.dev/docs/all-providers#directory
    title: Provider directory
  - id: linking
    resource: https://sst.dev/docs/linking/
    title: Resource Linking
  - id: cli
    resource: https://sst.dev/docs/reference/cli/
    title: CLI reference
  - id: sdk
    resource: https://sst.dev/docs/reference/sdk/
    title: SDK reference
  - id: live
    resource: https://sst.dev/docs/live/
    title: Live
  - id: console
    resource: https://sst.dev/docs/console/
    title: Console
  - id: state
    resource: https://sst.dev/docs/state/
    title: State
  - id: self
    resource: /references/official-docs-2026-10-20.md
    title: SST 官方文档采集登记
---

# SST 官方文档（2026-10-20 采集）

本登记记录本教程于 **2026-10-20** 查阅的 SST 官方文档页面。官网是随时间更新的产品资料；下列 W 编号表示页面在采集日期的陈述，不能直接作为 SST v4.17.2 源码行为的证据。固定版本实现以 [v4.17.2 源码快照](source-v4.17.2.md) 为准。

## 页面与事实映射

| 页面 | URL | 对应事实 | 使用范围 |
|---|---|---|---|
| Basics | [sst.dev/docs](https://sst.dev/docs/) | W-001、W-015 | `sst.config.ts`、组件、link、项目结构、常用工作流；Monorepo 的根配置拆分示例 |
| Components | [Components](https://sst.dev/docs/components/) | W-004、W-005 | SST built-in 与 provider components 的区分，以及 `sst.aws.*`、`sst.cloudflare.*` 页面说明 |
| Providers | [Providers](https://sst.dev/docs/providers/) | W-006、W-007 | 页面所述 provider 支持、添加方法、版本与凭证说明 |
| Provider directory | [All providers](https://sst.dev/docs/all-providers#directory) | W-006 | 页面列出的 provider directory 与“150+ providers”采集日宣称 |
| Resource Linking | [Linking](https://sst.dev/docs/linking/) | W-008、W-009 | 创建资源、Link 关联、SDK 使用及 `sst dev` 本地资源说明 |
| CLI reference | [CLI](https://sst.dev/docs/reference/cli/) | W-002、W-010、W-011、W-015 | stage、dev 模式、deploy/diff/remove 命令及 `--config` |
| SDK reference | [SDK](https://sst.dev/docs/reference/sdk/) | W-012 | 页面列出的应用对象与 JavaScript/TypeScript、Python、Go、Rust 资源访问说明 |
| Live | [Live](https://sst.dev/docs/live/) | W-013 | 官网对本地机器、远端 Lambda、AppSync Events 与 stub function 的产品说明 |
| Console | [Console](https://sst.dev/docs/console/) | W-014 | 官网对 SST 管理 dashboard 的功能说明 |
| State | [State](https://sst.dev/docs/state/) | W-003 | JSON state、home provider bucket 备份及 passphrase 的官网说明 |

## 关键段落锚点

- **Stage**：CLI reference 的 [`stage`](https://sst.dev/docs/reference/cli/#stage) 章节。
- **Dev**：CLI reference 的 [`dev`](https://sst.dev/docs/reference/cli/#dev) 章节。
- **Monorepo 配置选择**：CLI reference 的 [`config`](https://sst.dev/docs/reference/cli/#config) 章节；项目结构示例见 Basics 页的 [Monorepo](https://sst.dev/docs/#monorepo) 段落。
- **Providers**：provider 总量等厂商自述只保留为采集时点陈述；本教程不据此报告固定源码的 provider/API 数量。

## 采集与版本边界

- 采集日期：2026-10-20。
- 所列页面为公开 SST 官方文档 URL；网页内容可能在此日期之后变化。
- 官方文档中的用户用法与源码实现事实分别标注为 W 编号和 F 编号；只有存在固定提交证据时，正文才将实现行为归于 v4.17.2。
- Monorepo 章节内容仅由可访问的 Basics 页面与 CLI `config` 章节支持；教程不依赖未能独立读取的 Monorepo 专页。
