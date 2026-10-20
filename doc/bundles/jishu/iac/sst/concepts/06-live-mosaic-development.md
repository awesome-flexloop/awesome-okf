---
type: Concept
title: "Live 与 Mosaic 开发机制"
description: "区分 SST v4.17.2 Mosaic 的本地 HTTP/event/deployer 实现与官网 Live 产品说明，明确云端依赖和版本验证边界。"
tags: [SST, Live, Mosaic, development, AppSync]
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

# Live 与 Mosaic 开发机制

SST 的本地开发体验不应被简化成“所有资源都在本机模拟”。固定提交中的 Mosaic 代码提供本地 HTTP 端点、事件流和部署协调路径；官网 Live 页面则说明本地机器与远端 Lambda 间的通信方式。两组证据相关，但不应在未验证版本一致性的情况下合并成同一实现描述。

## Mosaic 本地服务端点

v4.17.2 的 Mosaic dev 服务注册 `/stream`、`/api/deploy`、`/api/env`、`/api/completed` handlers（F-030，[源码](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/cmd/sst/mosaic/dev/dev.go#L44-L126)）。

- `/stream` 设置 NDJSON content type，订阅事件总线并将事件逐项编码到 HTTP response（F-031，[源码](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/cmd/sst/mosaic/dev/dev.go#L44-L78)）。
- `/api/deploy` 发布 `DeployRequestedEvent`（F-032，[源码](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/cmd/sst/mosaic/dev/dev.go#L80-L81)）。
- Mosaic deployer 订阅文件变更、部署请求和构建成功事件；处理部署请求时调用 `Project.Run()` 并传入 `Command: "deploy"`、`Dev: true`（F-033，[源码](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/cmd/sst/mosaic/deployer/deployer.go#L21-L50)）。

这些是固定提交的 handler 与订阅行为，不能据此声称整个部署过程都离线运行。

## Runtime 与 Live 标记

`runtime.Collection.Run()` 在运行相应 runtime 前追加 `SST_LIVE=true` 与 `SST_DEV=true`（F-019，[源码](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/pkg/runtime/runtime.go#L220-L229)）。Mosaic AWS 启动代码调用 provider 的 `ResolveAppSync()`；相关 AppSync 实现包含 WebSocket connection 的 `Subscribe()` 与 `Publish()`（F-034，[启动路径](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/cmd/sst/mosaic/aws/aws.go#L20-L39)、[AppSync 实现](https://github.com/anomalyco/sst/blob/e49ac31411f63ab4ed0d802b7e15d95f6b827e47/cmd/sst/mosaic/aws/appsync/appsync.go#L105-L170)）。

## 官网 Live 说明及其边界

官网 Live 页面称 Live 通过 AWS AppSync Events 在本地机器与远端 Lambda function 之间通信，并说明 `sst dev` 会创建对应 AppSync Events API、部署 stub function（W-013，[Live 页面](https://sst.dev/docs/live/)）。官网 CLI 页面另称 `sst dev` 默认启动 multiplexer，协调应用部署、本地函数和前端进程，并列出 `multi`、`basic`、`mono` 模式（W-010，[dev 章节](https://sst.dev/docs/reference/cli/#dev)）。

官网的“AppSync Events”陈述与源码中 Mosaic AWS/AppSync WebSocket 实现不是同一项版本事实；本教程没有证明官网页面描述与 v4.17.2 的接口、资源创建细节完全对应。因此正文不把二者静默拼成一条已经验证的实现链。

## 运行边界

- `sst dev` 的本地开发使用方式见官网页面；本教程未启动完整 SST 开发环境。
- Live/AppSync 相关行为可能需要云端 provider、凭证与远端资源；本任务未执行云端部署，也未验证费用或清理行为。
- 若要实操，请先阅读官网 Live 与 CLI 说明，并按自己的账号、stage 和资源策略评估影响。

## 相关概念

- [CLI 到项目执行生命周期](/concepts/02-cli-project-lifecycle.md)
- [运行时、RPC 与平台程序](/concepts/04-runtime-server-architecture.md)
- [本地开发到部署示例](/examples/03-local-development-and-deployment.md)
