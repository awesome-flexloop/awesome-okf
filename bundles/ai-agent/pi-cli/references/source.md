---
type: reference
scope: pi-cli
name: source
version: "0.1.0"
source: local
description: pi-cli 源码信源索引
---

# 源码信源索引

本文件列出 pi-cli 项目中被本 wiki bundle 引用的关键源文件，标注其角色和关联的事实 ID。

## 项目根目录

| 文件 | 角色 | 事实 ID |
|------|------|---------|
| `package.json` | monorepo 配置、workspaces、构建/检查脚本、依赖版本 | F-001 ~ F-007 |
| `README.md` | 项目概览、包列表、权限说明、开发命令、供应链安全 | F-008 ~ F-012 |
| `AGENTS.md` | 开发规则：代码风格、命令、Git、发布流程 | F-013 ~ F-016 |
| `tsconfig.json` | TypeScript 配置、路径别名 | F-017 |

## packages/ai

| 文件 | 角色 | 事实 ID |
|------|------|---------|
| `src/index.ts` | 核心无副作用入口，重新导出类型、auth、models、utils | F-018 |
| `src/cli.ts` | pi-ai CLI 可执行脚本，支持 login/list 命令 | F-019 |
| `src/models.ts` | Provider/Models 接口定义、createModels/createProvider 工厂、成本计算、思考级别 | F-020 ~ F-023, F-050, F-051 |
| `src/oauth.ts` | OAuth 类型仅导出入口 | F-024 |
| `src/types.ts` | 核心类型定义：API 类型、Provider ID、Model、Message、Stream 选项、Compat 配置 | F-025 ~ F-029 |
| `src/compat.ts` | 旧版全局 API 兼容层，含 api-registry 和内置 API 注册 | F-030, F-031 |
| `src/images.ts` | 图片生成入口函数 generateImages() | F-032 |

## packages/tui

| 文件 | 角色 | 事实 ID |
|------|------|---------|
| `src/index.ts` | TUI 库公共导出：组件、模糊搜索、LaTeX、键绑定、终端图片 | F-033, F-034 |
| `src/tui.ts` | TUI 核心实现：Component 接口、TuiBase 差分渲染、overlay 栈、焦点管理、终端查询 | F-035, F-036, F-037 |

## packages/agent / client / server

| 文件 | 角色 | 事实 ID |
|------|------|---------|
| `packages/agent/README.md` | agent-core 文档：Agent 类、事件流、工具执行模式、状态管理 | F-038 ~ F-040 |
| `packages/client/README.md` | client 文档：PiClient、CBOR 传输、会话租约 | F-041, F-042 |
| `packages/server/README.md` | server 文档：PiServer、PiServerService、协议桥接（实验性） | F-043, F-044 |

## .pi/prompts

| 文件 | 角色 | 事实 ID |
|------|------|---------|
| `cl.md` | Changelog 审计 prompt | F-045 |
| `is.md` | GitHub issue 分析 prompt | F-046 |
| `pr.md` | PR 审查 prompt | F-047 |
| `sa.md` | 安全公告更新 prompt | F-048 |
| `wr.md` | 任务收尾（changelog/commit/push/close）prompt | F-049 |
