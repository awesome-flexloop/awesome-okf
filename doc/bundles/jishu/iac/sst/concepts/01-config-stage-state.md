---
type: Concept
title: "配置、stage 与 state"
description: "区分 SST 项目发现、App/Stage 源码字段与官网所述 stage 和 state 持久化行为，避免跨版本合并结论。"
tags: [SST, configuration, stage, state]
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

# 配置、stage 与 state

阅读 SST 配置模型时，应分别回答三个问题：CLI 如何找到应用配置、stage 在应用模型中是什么、state 如何持久化。前一个问题可由固定源码回答；stage 的使用规则与 state 存储方式在本教程中引用 2026-10-20 官网说明，不能冒充 v4.17.2 源码结论。

## 配置发现与项目对象

在 v4.17.2 中，`project.Discover()` 从当前目录向上查找 `sst.config.ts`，找到后创建解析得到的 `.sst` 工作目录（F-003，[源码](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/pkg/project/project.go#L115-L130)）。随后 `project.New()` 检查输入 stage，并据配置设置项目根目录和 `.sst` 目录（F-005，[源码](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/pkg/project/project.go#L160-L203)）。

`project.App` 的字段包括 `Name`、`Stage`、`Removal`；`project.State` 的字段包括 `Purge`、`Compress`、`Retention`（F-004，[源码](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/pkg/project/project.go#L30-L55)）。字段清单只说明该固定快照定义了这些字段，不足以单独推出其完整配置语义或持久化协议。

## 官网所述的 stage 规则

CLI reference 的 `stage` 章节将 stage 描述为资源名前缀，使同一账户中可以运行多个环境；未显式传入时，页面称 CLI 使用本机用户名，并把 personal stage 写入 `.sst/stage` 供后续读取（W-002，[官网章节](https://sst.dev/docs/reference/cli/#stage)）。

部署时可以显式选择 stage，例如：

```sh
sst deploy --stage production
```

该命令形式来自官网 CLI reference（W-011）。它是使用示例，不是本任务在云账户中执行成功的证据。stage 名的校验实现见 `project.New()`（F-005）；教程不从单个正则校验实现推导出官网所列的全部命名规则。

## 官网所述的 state 存储

State 页面称 SST 在本地生成 JSON state file，并将 state 备份到应用 home provider 的 bucket；页面还称 passphrase 存储于 SSM parameter（W-003，[官网 State 页面](https://sst.dev/docs/state/)）。

这些是官网采集日的产品说明。当前事实清单中的 v4.17.2 源码证据只登记了 `project.State` 的字段和 `provider.Home` 接口（F-004、F-012），尚不足以据此确认 JSON 文件布局、备份实现或 passphrase 的内部读写调用。因此本教程将存储细节限定为官网说明，而不是源码已验证行为。

## Monorepo 中的配置选择

Basics 页面展示了 monorepo 中把配置拆到 `infra/` 等位置的组织方式；CLI reference 说明 `--config` 可在包含多个 SST app 的 monorepo 中选择配置文件（W-015，[Basics Monorepo](https://sst.dev/docs/#monorepo)、[CLI config](https://sst.dev/docs/reference/cli/#config)）。这两条用于说明官网现行使用方式，不应与源码中 `Discover()` 的向上查找单独等同。

## 相关概念

- [SST 应用模型与阅读边界](/concepts/00-application-model.md)
- [CLI 到项目执行生命周期](/concepts/02-cli-project-lifecycle.md)
- [最小应用与组件示例](/examples/01-minimal-component-app.md)
