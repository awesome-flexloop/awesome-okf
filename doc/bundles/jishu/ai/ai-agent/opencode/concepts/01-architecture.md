---
type: Concept
title: 架构概览
description: OpenCode 的模块化架构，包括 infra 层（app/console/lake/stage/stats/secret）、核心包、TUI 包和 V2 API 规范
tags: [architecture, infra, packages, sst, effect, monorepo]
generated:
  by: "reference_agent/trae-cn"
  at: 2026-08-23T10:00:00+08:00
verified:
  by: "process:grep-verification"
  at: 2026-08-23T10:00:00+08:00
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/source.md
    title: 源码信源
---

# 架构概览

OpenCode 采用分层 monorepo 架构，通过 Bun workspaces 和 Turbo 编排构建，使用 SST 管理基础设施部署。

## 包间依赖方向

项目严格执行以下依赖方向（见 `AGENTS.md:3`）：

```
Schema → Core, Protocol → Server
Client → Schema, Protocol（不可依赖 Core 或 Server）
sdk-next → Client + Core + Server（嵌入式组合）
```

这意味着：
- **Schema** 是最底层的叶子包，定义共享数据类型，不依赖数据库、Drizzle、Session 执行等
- **Core** 消费 Schema 实现领域行为
- **Protocol** 将 Schema 值组合为路径、载荷、信封、错误、游标和流
- **Server** 导入 Core 和 Protocol，托管 Protocol 的 API 组
- **Client** 仅依赖 Schema 和 Protocol，保证浏览器安全
- **sdk-next** 在进程内组合 Client/Core/Server，实现嵌入式 OpenCode

## 基础设施模块（infra/）

SST 配置拆分为多个基础设施模块，由 `sst.config.ts` 统一导入：

| 模块 | 职责 |
|------|------|
| `infra/stage.ts` | 阶段域名解析、AWS 部署开关、Cloudflare 区域主机名、短域名 |
| `infra/app.ts` | API Cloudflare Worker、Astro 文档站、StaticSite Web 应用、R2 Bucket |
| `infra/console.ts` | PlanetScale 数据库、Auth Worker、Stripe 产品/价格/优惠券、SolidStart Console、LogProcessor、Stat Worker |
| `infra/lake.ts` | AWS S3 Tables（Iceberg）、Glue Catalog、Kinesis Firehose、Athena Workgroup、ECS 摄入服务、VPC/集群 |
| `infra/stats.ts` | Stats SolidStart 应用、Stats 数据库、StatsSync 服务、推理事件表定义 |
| `infra/secret.ts` | 密钥封装（R2、Honeycomb、Upstash Redis、Support API） |
| `infra/enterprise.ts` | 企业版功能 |
| `infra/monitoring.ts` | 监控（仅 production 和 vimtor 阶段） |

### 部署条件逻辑

`infra/stage.ts:8-9` 定义 `deployAws` 标志，仅当阶段为 `production` 或 `dev` 时部署 AWS 资源（数据湖）。`sst.config.ts:33-34` 据此条件导入 lake 和 stats 模块。

## 核心架构模式

### Effect 函数式编程

Core 包深度使用 Effect 4.0.0-beta.83：
- 使用 `Effect.gen(function* () { ... })` 进行组合
- 使用 `Effect.fn("Domain.method")` 创建命名/追踪 effect
- 使用 `Context.Service` 定义可注入服务
- 使用 `Layer` 组装依赖
- 使用 `Schema.Class`、`Schema.brand`、`Schema.TaggedErrorClass` 定义数据和错误

### 自导出模块模式

每个模块文件底部使用 `export * as Foo from "./foo"` 进行自导出，消费者通过命名空间导入：

```ts
import { SessionV2 } from "@opencode-ai/core/session"
yield* SessionV2.Service
```

这种模式避免了 `export namespace`，支持 tree-shaking 和 Node 原生 TypeScript 运行器。

### 双运行时条件导入

Core 包通过 Bun 的 subpath imports 支持 Bun 和 Node 双运行时：

```json
"#sqlite": {
  "bun": "./src/database/sqlite.bun.ts",
  "node": "./src/database/sqlite.node.ts"
}
```

涉及的抽象包括 SQLite 数据库、PTY 伪终端、FFF 文件系统。

## V2 API 规范

V2 API 定义在 `specs/v2/` 目录中，核心规范包括：

- **config.md**：配置系统重设计（11 个审查组）
- **session.md**：会话 API、Context Epoch、自动压缩、工具注册表切片
- **tools.md**：工具定义、调用上下文、注册、执行、输出限制、失败语义
- **provider-policy.md**：提供商策略语义
- **provider-model.md**：提供商模型配置
- **instructions.md**：指令系统
- **todo.md**：待办事项工具
- **schema-changelog.md**：Schema 变更日志

HTTP API 通过 Effect HttpApi 在 `packages/protocol` 中定义，路由组位于 `packages/opencode/src/server/routes/instance/httpapi/groups/`，包括 session、event、config、provider、agent、file、pty、question、permission、mcp、project、workspace 等。

## 前端架构

- **TUI**：`packages/tui` 基于 `@opentui/solid`（SolidJS 渲染到终端），使用 `@opentui/keymap` 处理键盘映射
- **Web Console**：`packages/console/app` 基于 SolidStart，部署为 Cloudflare Worker with SSR
- **Web App**：`packages/app` 基于 Vite + SolidJS，部署为静态站点
- **文档站**：`packages/web` 基于 Astro

## 相关概念

- [OpenCode 简介](00-introduction.md)
- [配置系统](02-config-system.md)
- [会话与工具](03-session-tools.md)
- [部署与基础设施](04-deployment-infra.md)
