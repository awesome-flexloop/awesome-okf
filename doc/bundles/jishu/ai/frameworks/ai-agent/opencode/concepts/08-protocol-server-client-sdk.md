---
type: Concept
title: "OpenCode 2.0.32 Protocol、Server、Client 与 SDK 边界"
description: "从类型化 API 定义追踪 Server 装配、handler 接线、生成客户端契约和 SDK 导出"
tags: [opencode, protocol, server, client, sdk, api, 2.0.32]
generated: { by: "reference_agent/trae-cn", at: 2026-10-20T12:01:30+08:00 }
verified: { by: "process:seven-concepts-e", at: 2026-10-20T12:01:30+08:00 }
status: draft
stale_after: 2027-04-20
sources:
  - id: opencode-source-map-2.0.32
    resource: /references/source-code-map-2.0.32.md
    title: OpenCode 2.0.32 固定源码地图
---

# OpenCode 2.0.32 Protocol、Server、Client 与 SDK 边界

OpenCode 2.0.32 的 API 路径可以按四层理解：Protocol 声明契约，Server 装配路由并接入 handler，Client 从 `ClientApi` 生成调用契约，SDK 再组织开发者入口。沿这条链阅读，能避免只看 handler 后凭经验猜测客户端类型，或把 SDK 简化成纯 HTTP 包装。（F-101～F-105、F-114）

本篇所述均限定于固定 commit `6ec56821d63100fe5bda45b759364f561c56b359`。它展示代表性 session 路径与生成边界，不是全部 API endpoint 的目录。

## Protocol 定义 API 契约

`packages/protocol/src/api.ts` 组合 API group middleware，并在默认 API 上挂载 `Authorization` 与 `SchemaErrorMiddleware`；`makeDefaultApi` 是 API 构造入口。Session group 声明 `session.list`、`session.create`、`session.prompt`、`session.interrupt` 等 endpoint。本轮没有对 session group 的 endpoint 总数作断言。（F-101、F-102、F-111）

Protocol 还导出 `ClientApi`。这使 API 契约成为 Server 与生成客户端之间可定位的边界，而不是由每个调用方根据路由处理器自行拼装一份类型定义。（F-104）

## Server routes 与 handler

Server 的 `api.ts` 通过 `makeDefaultApi` 注入 Server middleware；`routes.ts` 导出 `createRoutes` 与 `createEmbeddedRoutes`。Session handler 负责将 prompt 请求字段转交给 Core 的 `session.prompt`，随后由 Core session 实现执行输入准备、admission 和条件唤醒。（F-103、F-114）

因此，追踪 API 行为时可以分段检查：

1. Protocol endpoint 声明：路径、输入 schema 与 API 组装。
2. Server route 与 middleware：API 如何进入服务端。
3. handler：请求字段如何被转交。
4. Core service：请求如何进入会话生命周期。

该分段是对本轮已核验源码关系的阅读方法；其他 endpoint 的 handler 行为需要按其源码单独确认。

## Client contract 生成

Client 构建脚本分别使用 Protocol 的 `ClientApi` 编译 promise contract 与 Effect contract。Promise client 的 `make(options)` 再调用生成客户端的 `OpenCode.make(options)`。这条生成路径将契约来源与客户端调用入口连接起来，但本轮并未逐个核对所有生成 endpoint。（F-104）

变更 API 时，至少要对照 Protocol 定义、Server 接线和 Client 构建输入。只在某一层看到类型或处理函数，不能据此推断其余各层已经同步。

## SDK 的导出边界

SDK 入口分别将 `./opencode` 与 `./tool` 导出为 `OpenCode`、`Tool` namespace。其 manifest 的 production dependencies 包含 client、core、plugin、schema、server 与 util；devDependencies 则包含 ai、httpapi-codegen 与 protocol。将两类依赖混为一谈，会错误描述 SDK 的构建依赖与运行时包边界。（F-105）

所以，SDK 的角色不能仅根据名称概括成“远端 HTTP 的薄客户端”：快照中的依赖列表还包含 core、plugin 和 server。进一步说明这些依赖在具体 SDK API 中如何使用，需要继续阅读各 namespace 的实现，本轮不据此推断未检查的实现细节。

## 版本边界与核验入口

API endpoint 名称和层次关系仅代表本轮固定快照中的源码。旧版 `concepts/03-session-tools.md` 属于 1.18.21 历史内容，不应与 2.0.32 的 API 定义拼接成一个无版本区分的契约。具体文件入口和事实编号映射见[固定源码地图](/references/source-code-map-2.0.32.md)及[版本化事实清单](/spec/facts-2.0.32.md)。

## 相关概念

- [OpenCode Monorepo 包地图](/concepts/05-monorepo-package-map.md)
- [会话执行生命周期](/concepts/06-session-execution-lifecycle.md)
- [产品入口与工程交付](/concepts/09-product-surfaces-and-delivery.md)
