---
type: Concept
title: "运行时、RPC 与平台程序"
description: "梳理 SST v4.17.2 中 runtime 分发、JSON-RPC 服务注册、事件总线与 Pulumi 平台程序入口的可证职责。"
tags: [SST, runtime, JSON-RPC, Pulumi, architecture]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-10-20T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-10-20T00:00:00Z" }
status: draft
stale_after: 2027-10-20
sources:
  - id: source
    resource: /references/source-v4.17.2.md
    title: SST v4.17.2 固定源码快照
---

# 运行时、RPC 与平台程序

SST v4.17.2 的源码将运行时接口、RPC 服务、事件总线和 Pulumi Automation 程序入口放在不同模块。理解这些边界，比把所有文件压成一条未经证明的“调用链”更可靠。

## Runtime 分发

`pkg/runtime/runtime.go` 定义 `Runtime` 接口以及 `BuildInput`、`RunInput` 等类型；`Collection.Runtime` 根据 runtime 的 `Match` 结果查找实现（F-017，[源码](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/pkg/runtime/runtime.go#L18-L108)）。项目构造时将 Node、worker、Python、Go、Rust runtime 放入 collection（F-006，[源码](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/pkg/project/project.go#L192-L210)）。

`Collection.Build()` 按输入 runtime 选择实现并调用其 `Build()`；`Collection.Run()` 执行相应 runtime 的 `Run()`（F-018，[Build](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/pkg/runtime/runtime.go#L113-L157)）。在 Run 路径中，源码向环境变量追加 `SST_LIVE=true` 和 `SST_DEV=true`（F-019，[Run](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/pkg/runtime/runtime.go#L220-L229)）。

## RPC 服务边界

`server.New()` 创建 JSON-RPC server，并把 `/rpc` 注册为 HTTP handler；非 POST 请求返回 Method Not Allowed（F-015，[源码](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/pkg/server/server.go#L31-L51)）。`Server.Start()` 注册 `resource`、`aws`、`runtime` 三个 RPC 服务（F-016，[源码](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/pkg/server/server.go#L54-L62)）。

事件总线的 API 位于 `pkg/bus`，包括 `Subscribe`、`SubscribeAll` 和 `Publish`（F-020，[源码](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/pkg/bus/bus.go#L21-L67)）。Mosaic 对该 bus 的具体用法见 [Live 与 Mosaic 开发机制](/concepts/06-live-mosaic-development.md)。

## 平台程序入口

`platform/src/auto/run.ts` 导出 `run(program: automation.PulumiFn)`，并在该模块注册 stack transformations（F-022，[源码](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/platform/src/auto/run.ts#L12-L28)）。项目执行路径中可观察到配置构建与平台程序运行相关的 `js.Build` 调用（F-007、F-009）。

这些事实呈现 Go 侧项目/runtime/RPC 模块与 TypeScript 平台入口的职责位置，但没有在此列出每一种 RPC 方法的端到端调用者。读者应沿相应固定源码链接继续跟踪具体方法，而不要把“同属 SST CLI”视作调用证据。

## 相关概念

- [CLI 到项目执行生命周期](/concepts/02-cli-project-lifecycle.md)
- [组件与 provider 边界](/concepts/03-components-and-providers.md)
- [资源链接与 SDK 数据边界](/concepts/05-resource-linking.md)
- [Live 与 Mosaic 开发机制](/concepts/06-live-mosaic-development.md)
