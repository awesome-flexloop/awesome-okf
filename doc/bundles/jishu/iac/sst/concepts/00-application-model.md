---
type: Concept
title: "SST 应用模型与阅读边界"
description: "从官方 Basics 页面认识 SST 应用、配置入口与常用工作流，并建立官网现行说明和固定源码事实的版本边界。"
tags: [SST, application-model, IaC, 入门]
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

# SST 应用模型与阅读边界

SST 是一套以代码描述应用基础设施并提供开发、部署工作流的工具。2026-10-20 查阅的官方 Basics 页面围绕 `sst.config.ts`、组件、资源链接、项目结构以及 `sst dev` / `sst deploy` 展开（W-001）；本教程进一步用 SST v4.17.2 固定源码快照解释这些入口背后的部分实现。

阅读时要分清两种证据：`W-` 表示官网在采集日的产品说明，`F-` 表示固定提交中可直接定位的代码事实。两者可以互相帮助理解，但官网说明不自动代表 v4.17.2 的实现。

## 应用入口与源码发现

官方 Basics 将 `sst.config.ts` 作为应用配置入口（W-001）。在 v4.17.2 源码中，`project.Discover()` 从当前工作目录向上查找名为 `sst.config.ts` 的文件，并创建解析得到的 `.sst` 工作目录（F-003，[固定源码行段](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/pkg/project/project.go#L115-L130)）。

这个发现逻辑说明 CLI 不必要求用户恰好从配置文件所在目录启动；但它只证明源码中的向上查找行为，不代表所有命令、工具或 monorepo 结构都采用完全相同的工作目录规则。多应用仓库如何选择配置文件，官网 CLI 另提供 `--config` 说明（W-015，[配置章节](https://sst.dev/docs/reference/cli/#config)）。

## 从应用模型到组件

官方文档把 SST 应用写作配置与组件的组合，并说明组件可创建或组合更低层 provider resources（W-004、W-005）。概念上可以先用以下问题拆解一个应用：

| 问题 | 阅读入口 |
|---|---|
| 配置从哪里进入？ | `sst.config.ts` 与项目发现（W-001、F-003） |
| 资源以什么抽象描述？ | SST built-in components 与 provider components（W-004、W-005） |
| 运行时如何访问资源信息？ | Link 与 SDK（W-008、F-023–F-029） |
| 命令如何推动开发或部署？ | CLI 与项目执行路径（W-010、W-011、F-009–F-011） |

这张表是教程导航，不是对 SST 所有组件或所有执行路径的穷尽清单。

## 建议学习顺序

1. 阅读[配置、stage 与 state](/concepts/01-config-stage-state.md)，理解项目发现与环境区分。
2. 阅读[CLI 到项目执行生命周期](/concepts/02-cli-project-lifecycle.md)，跟踪命令如何进入 stack 执行。
3. 阅读[组件与 provider 边界](/concepts/03-components-and-providers.md)，区分资源抽象层。
4. 再进入[资源链接](/concepts/05-resource-linking.md)和[Live/Mosaic](/concepts/06-live-mosaic-development.md)。

## 相关概念

- [配置、stage 与 state](/concepts/01-config-stage-state.md)
- [CLI 到项目执行生命周期](/concepts/02-cli-project-lifecycle.md)
- [组件与 provider 边界](/concepts/03-components-and-providers.md)
- [资源链接与 SDK 数据边界](/concepts/05-resource-linking.md)
