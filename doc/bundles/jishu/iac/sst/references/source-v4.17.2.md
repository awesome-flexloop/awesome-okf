---
type: Reference
title: "SST v4.17.2 固定源码快照"
description: "登记 SST v4.17.2 对应的不可变 Git 提交、核心源码路径与本教程采用的实现事实边界。"
tags: [SST, source-code, v4.17.2, 源码快照]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-10-20T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-10-20T00:00:00Z" }
status: stable
stale_after: 2027-10-20
sources:
  - id: sst-repository
    resource: https://github.com/anomalyco/sst/tree/e49ac31411f63ab4ed0d802b7e15d95f6b827e47
    title: SST repository at the v4.17.2 commit
  - id: self
    resource: /references/source-v4.17.2.md
    title: SST v4.17.2 固定源码快照登记
---

# SST v4.17.2 固定源码快照

本教程关于源码实现的陈述以 SST 仓库 `v4.17.2` 对应的固定提交为准。链接全部指向该提交，不依赖浮动分支、开发者本机目录或临时文件。

## 版本指纹

| 项目 | 内容 |
|---|---|
| 上游仓库 | [anomalyco/sst](https://github.com/anomalyco/sst) |
| Release tag | `v4.17.2` |
| 固定 commit | `e49ac31411f63ab4ed0d802b7e15d95f6b827e47` |
| 固定快照入口 | [GitHub tree](https://github.com/anomalyco/sst/tree/e49ac31411f63ab4ed0d802b7e15d95f6b827e47) |
| 源码事实登记 | F-001–F-034，详见概念文档中的固定提交行号引用 |

## 代表性源码路径

| 路径 | 本教程核验范围 |
|---|---|
| [`cmd/sst/`](https://github.com/anomalyco/sst/tree/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/cmd/sst) | CLI 根命令、dev 与 deploy 命令入口 |
| [`pkg/project/`](https://github.com/anomalyco/sst/tree/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/pkg/project) | 项目发现、App/Stage 字段、runtime 初始化、配置构建与 stack 执行 |
| [`pkg/project/provider/`](https://github.com/anomalyco/sst/tree/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/pkg/project/provider) | Home 与 Provider 接口以及 AWS、Cloudflare 项目 provider 实现 |
| [`pkg/runtime/`](https://github.com/anomalyco/sst/tree/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/pkg/runtime) | runtime 匹配、Build/Run 分发及运行环境标记 |
| [`pkg/server/`](https://github.com/anomalyco/sst/tree/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/pkg/server) | `/rpc` JSON-RPC handler 与服务注册 |
| [`pkg/bus/`](https://github.com/anomalyco/sst/tree/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/pkg/bus) | 事件订阅和发布接口 |
| [`platform/src/components/`](https://github.com/anomalyco/sst/tree/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/platform/src/components) | 组件命名空间、Linkable/Link 与代表性 AWS Function 实现 |
| [`platform/src/auto/run.ts`](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/platform/src/auto/run.ts) | Pulumi Automation 程序入口 |
| [`sdk/js/src/resource/`](https://github.com/anomalyco/sst/tree/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/sdk/js/src/resource) | `SST_RESOURCE_*` 环境变量解析与资源 Proxy |
| [`cmd/sst/mosaic/`](https://github.com/anomalyco/sst/tree/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/cmd/sst/mosaic) | 本地 HTTP 事件端点、deployer 与 AWS/AppSync 实现 |

## 使用边界

- 源码事实编号为 F-001–F-034；概念文档按主题引用编号，并链接到固定提交中的具体文件和行段。
- 固定快照用于说明代码中存在的字段、接口、命令映射与调用关系，不自动代表 SST 官网在 2026-10-20 的全部产品行为。
- 示例中若引用官网配置语法，将另行引用 [官网文档登记](official-docs-2026-10-20.md)；无法由固定源码与注明日期的官方页面共同确认的内容会显式标注边界。

## 覆盖范围

本登记覆盖本教程使用的 F-001–F-034 源码事实。每条实现断言应在相应概念文档中保留 F 编号及具体 GitHub 行号链接，便于读者直接复查。
