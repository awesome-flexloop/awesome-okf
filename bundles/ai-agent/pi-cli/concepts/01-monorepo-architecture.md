---
type: Concept
title: Monorepo 架构
description: pi-monorepo 使用 npm workspaces 组织多个包，按 tui→telemetry→ai→agent→protocol→client→server→coding-agent 的顺序构建。
tags: [pi-cli, monorepo, 架构, workspaces]
generated: 2026-08-23
verified: 2026-08-23
status: stable
stale_after: 2026-11-23
sources:
  - package.json:5-17
  - README.md:26-36
  - tsconfig.json:7-36
---

# Monorepo 架构

pi-monorepo 使用 npm workspaces 管理多包项目。根 `package.json` 的 `workspaces` 字段包含 `packages/*`、`packages/session-backends/*` 以及 coding-agent 的扩展示例目录。

## 包职责

| 包 | npm 名称 | 职责 |
|----|----------|------|
| `packages/ai` | `@earendil-works/pi-ai` | 统一多提供商 LLM API，支持 OpenAI、Anthropic、Google、Bedrock 等 |
| `packages/tui` | `@earendil-works/pi-tui` | 终端 UI 组件库，差分渲染、键盘输入、终端图片、模糊搜索 |
| `packages/agent` | `@earendil-works/pi-agent-core` | 有状态代理运行时，工具调用、事件流、会话管理 |
| `packages/client` | `@earendil-works/pi-client` | 传输无关的远程会话客户端，CBOR 消息 |
| `packages/server` | `@earendil-works/pi-server` | 实验性会话服务器，组合传输监听器 |
| `packages/coding-agent` | `@earendil-works/pi-coding-agent` | 交互式编码代理 CLI（面向最终用户） |
| `packages/telemetry` | `@earendil-works/pi-telemetry` | 厂商中立遥测契约和适配器 |
| `packages/protocol` | `@earendil-works/pi-protocol` | 客户端/服务器线协议 DTO 和 schema |
| `packages/session-backends/sqlite-node` | `@earendil-works/pi-session-backend-sqlite-node` | SQLite 会话后端 |

## 构建顺序

构建脚本按严格的依赖顺序执行：

1. `packages/tui`
2. `packages/telemetry`
3. `packages/ai`
4. `packages/agent`
5. `packages/session-backends/sqlite-node`
6. `packages/protocol`
7. `packages/client`
8. `packages/server`
9. `packages/coding-agent`

存在两种构建模式：
- `npm run build`：刷新模型数据后构建所有包
- `npm run build:offline`：使用现有模型数据构建，无需网络访问

## 路径别名

`tsconfig.json` 配置了完整的包路径映射，使得源码间可以直接通过包名导入而无需先构建。例如：
- `@earendil-works/pi-ai` → `./packages/ai/src/index.ts`
- `@earendil-works/pi-ai/providers/*` → `./packages/ai/src/providers/*.ts`
- `@earendil-works/pi-agent-core` → `./packages/agent/src/index.ts`
- `@earendil-works/pi-tui/*` → `./packages/tui/src/*`

## 版本控制

所有包使用锁步版本控制（lockstep versioning），共享同一个版本号。当前版本为 `0.0.3`。`patch` 版本用于修复和新增功能，`minor` 版本用于破坏性变更，不发布 `major` 版本。

## 相关概念

- [项目简介](/concepts/00-introduction.md)
- [AI 包详解](/concepts/02-ai-package.md)
- [TUI 终端 UI 系统](/concepts/03-tui-system.md)
