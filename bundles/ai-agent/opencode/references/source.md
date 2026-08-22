---
type: reference
scope: opencode
name: source
version: "0.1.0"
source: local
description: "OpenCode 关键源文件索引与事实 ID 映射"
---

# 源文件参考

本文件列出 OpenCode 项目中的关键源文件及其对应的事实 ID，便于溯源验证。

## 项目配置

| 文件路径 | 说明 | 事实 ID |
|---------|------|---------|
| `package.json` | 根项目清单、工作区、catalog 依赖版本 | F-001, F-002, F-003, F-004, F-005, F-006, F-010, F-017~F-021, F-078, F-079, F-080 |
| `bunfig.toml` | Bun 安装与测试配置 | F-008, F-009 |
| `tsconfig.json` | TypeScript 配置 | F-007 |
| `turbo.json` | Turbo monorepo 任务配置 | F-004 |
| `sst.config.ts` | SST 基础设施配置入口 | F-050, F-051 |
| `AGENTS.md` | AI agent 开发规范、架构约束 | F-025, F-067, F-068, F-069, F-071, F-072, F-073 |
| `CONTEXT.md` | 会话运行时术语表与领域语言 | F-076 |
| `README.md` | 项目介绍、安装、内置 agent | F-046~F-049 |

## 基础设施

| 文件路径 | 说明 | 事实 ID |
|---------|------|---------|
| `infra/stage.ts` | 阶段域名、AWS 部署开关、Cloudflare DNS | F-052, F-053 |
| `infra/app.ts` | API Worker、文档站、Web 应用 | F-054, F-055, F-056, F-061 |
| `infra/console.ts` | Console 控制台、Auth、Stripe、数据库 | F-057 |
| `infra/lake.ts` | AWS 数据湖（S3 Tables、Firehose、Athena、ECS） | F-058, F-059 |
| `infra/stats.ts` | Stats 应用与同步服务 | F-060 |
| `infra/secret.ts` | 密钥封装（Honeycomb、Upstash、R2） | — |

## V2 规范

| 文件路径 | 说明 | 事实 ID |
|---------|------|---------|
| `specs/v2/config.md` | V2 配置规范（11 个审查组） | F-038~F-042 |
| `specs/v2/session.md` | V2 会话 API、Context Epoch、压缩、工具注册表 | F-025~F-032 |
| `specs/v2/tools.md` | V2 工具定义、注册、执行、输出限制、失败语义 | F-033~F-036 |
| `specs/project.md` | 项目与会话的 REST API 端点列表 | — |

## 核心包

| 文件路径 | 说明 | 事实 ID |
|---------|------|---------|
| `packages/core/package.json` | Core 包清单、AI SDK provider 列表、条件导入 | F-011, F-022, F-070 |
| `packages/core/src/session.ts` | V2 会话核心门面 | F-025 |
| `packages/core/src/config.ts` | 配置 Schema 定义与加载 | — |
| `packages/opencode/package.json` | 主 CLI 包清单 | F-012 |
| `packages/opencode/src/index.ts` | CLI 入口、yargs 命令注册 | F-014, F-015, F-016 |
| `packages/tui/package.json` | TUI 包清单 | F-013 |

## .opencode 目录

| 文件路径 | 说明 | 事实 ID |
|---------|------|---------|
| `.opencode/opencode.jsonc` | 项目自身的 OpenCode 配置 | F-044 |
| `.opencode/tui.json` | TUI 插件配置 | F-045 |
| `.opencode/env.d.ts` | 文本模块类型声明 | F-077 |

## GitHub Action

| 文件路径 | 说明 | 事实 ID |
|---------|------|---------|
| `github/action.yml` | Action 元数据与输入参数 | F-062, F-063 |
| `github/index.ts` | Action 执行逻辑 | F-064, F-065, F-066 |

## 内置工具源码目录

| 目录路径 | 说明 | 事实 ID |
|---------|------|---------|
| `packages/opencode/src/tool/` | 内置工具实现（bash、read、write、edit、grep、glob、apply_patch、webfetch、websearch、todo、todowrite、task、skill、lsp 等） | F-037 |
| `packages/opencode/src/session/` | 会话执行、LLM 调用、压缩、系统提示 | F-031 |
| `packages/opencode/src/server/routes/instance/httpapi/` | HTTP API 路由组与处理器 | — |
| `packages/schema/src/` | 共享 Schema 定义（session、agent、model、event 等） | F-067 |
| `packages/protocol/src/` | HTTP API 协议定义与中间件 | F-067, F-069 |
