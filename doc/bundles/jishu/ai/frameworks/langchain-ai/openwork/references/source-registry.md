---
type: reference
scope: openwork
name: source-registry
version: "0.1.0"
source: https://github.com/langchain-ai/openwork
description: openwork 信源登记——源码文件清单与溯源映射
---

# 信源登记

本文件登记本 bundle 所有事实与概念派生的源码材料，供溯源验证。

## 仓库信息

| 项目 | 值 |
|---|---|
| 仓库 | https://github.com/langchain-ai/openwork |
| 版本 | 0.1.0 |
| 许可证 | MIT |
| 作者 | LangChain |
| 本地路径 | `external/libs/ai/langchain-ai/openwork/` |

## 源码文件清单

### 入口与配置

| 文件 | 行数 | 用途 | 对应事实 |
|---|---|---|---|
| `package.json` | 124 | 包元数据、依赖声明、脚本 | F-001 ~ F-004 |
| `bin/cli.js` | 64 | CLI 启动器，spawn Electron | F-005 ~ F-006 |
| `tsconfig.json` | — | TypeScript 配置 | — |
| `electron.vite.config.ts` | — | Electron Vite 构建配置 | — |

### 主进程

| 文件 | 行数 | 用途 | 对应事实 |
|---|---|---|---|
| `src/main/index.ts` | 102 | Electron 主进程入口，窗口创建与 IPC 注册 | F-007 ~ F-008 |
| `src/main/types.ts` | 186 | 主进程类型定义（Thread、StreamEvent、HITL 等） | F-024 ~ F-025 |
| `src/main/storage.ts` | 124 | 数据目录、API 密钥、检查点路径管理 | F-021 |

### Agent 子系统

| 文件 | 行数 | 用途 | 对应事实 |
|---|---|---|---|
| `src/main/agent/runtime.ts` | 188 | 代理运行时创建、模型选择、checkpointer 缓存 | F-009 ~ F-011 |
| `src/main/agent/local-sandbox.ts` | 221 | 本地沙箱后端，shell 命令执行 | F-012 ~ F-013 |
| `src/main/agent/system-prompt.ts` | 114 | 基础系统提示词 | F-014 ~ F-015 |
| `src/main/agent/types.ts` | 4 | DeepAgent 类型别名 | — |

### IPC 处理器

| 文件 | 行数 | 用途 | 对应事实 |
|---|---|---|---|
| `src/main/ipc/agent.ts` | 304 | 代理调用、恢复、中断、取消 | F-016 ~ F-017 |
| `src/main/ipc/models.ts` | 523 | 模型列表、API 密钥、工作区管理 | F-018 ~ F-019 |
| `src/main/ipc/threads.ts` | 135 | 线程 CRUD、标题生成、历史 | F-020 |

### 持久化

| 文件 | 行数 | 用途 | 对应事实 |
|---|---|---|---|
| `src/main/db/index.ts` | 245 | sql.js 应用数据库（threads/runs/assistants 表） | F-022 |
| `src/main/checkpointer/sqljs-saver.ts` | 470 | LangGraph 检查点 SQLite 持久化 | F-023 |

### 服务

| 文件 | 行数 | 用途 | 对应事实 |
|---|---|---|---|
| `src/main/services/title-generator.ts` | 51 | 启发式标题生成 | — |
| `src/main/services/workspace-watcher.ts` | 118 | 文件系统监听与变更通知 | F-026 |

### 渲染进程

| 文件 | 用途 |
|---|---|
| `src/renderer/src/App.tsx` | React 应用根组件 |
| `src/renderer/src/components/chat/` | 聊天界面（消息、工具调用、Todo、模型切换） |
| `src/renderer/src/components/kanban/` | 看板式子代理面板 |
| `src/renderer/src/components/panels/` | 文件系统、子代理、Todo 面板 |
| `src/renderer/src/components/tabs/` | 文件查看器（代码、图片、PDF、二进制） |
| `src/renderer/src/lib/` | Electron 传输、状态管理、工作区工具 |

### 预加载

| 文件 | 用途 |
|---|---|
| `src/preload/index.ts` | contextBridge IPC 桥接 |
| `src/preload/index.d.ts` | 预加载类型声明 |

## 关键依赖版本

| 依赖 | 版本 | 角色 |
|---|---|---|
| `deepagents` | ^1.5.1 | 深度代理框架内核 |
| `@langchain/langgraph` | ^1.0.15 | 代理图运行时 |
| `@langchain/core` | 1.2.9 | LangChain 核心抽象 |
| `@langchain/anthropic` | ^1.3.11 | Anthropic Claude SDK |
| `@langchain/openai` | ^1.2.3 | OpenAI GPT SDK |
| `@langchain/google-genai` | ^2.1.12 | Google Gemini SDK |
| `electron` | ^43.4.0 | 桌面应用框架 |
| `sql.js` | ^1.12.0 | 纯 JS SQLite（WASM） |
| `react` | ^19.2.1 | UI 框架 |
| `zustand` | ^5.0.3 | 前端状态管理 |
