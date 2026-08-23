---
type: reference
scope: deepcode-cli
name: source
version: "0.1.0"
source: https://github.com/lessweb/deepcode-cli
description: deepcode-cli 源码信源索引
---

# 源码信源索引

本文件列出 deepcode-cli 项目中用于生成本 wiki bundle 的关键源文件，及其角色和支持的事实 ID。

## 项目配置文件

| 文件路径 | 角色 | 支持事实 |
|---------|------|---------|
| `package.json` | monorepo 根配置，定义工作区、脚本、依赖 | F-001, F-002, F-003, F-004, F-005 |
| `tsconfig.json` | TypeScript 项目引用配置，严格编译选项 | F-006, F-007, F-008 |

## Core 包（`packages/core/`）

| 文件路径 | 角色 | 支持事实 |
|---------|------|---------|
| `packages/core/package.json` | Core 库包配置，声明 openai/ejs/zod 等依赖 | F-010, F-013 |
| `packages/core/src/index.ts` | Core 库公共 API 导出入口 | F-053, F-054 |
| `packages/core/src/settings.ts` | 设置类型定义、解析与合并逻辑、权限配置、MCP 服务器配置 | F-014, F-015, F-016, F-017, F-018, F-020, F-021, F-022, F-023, F-024, F-025, F-026, F-027 |
| `packages/core/src/session.ts` | 会话管理核心类、会话状态、项目代码生成、Plan Mode 权限 | F-019, F-048, F-049, F-050, F-052 |
| `packages/core/src/mcp/mcp-manager.ts` | MCP 多服务器管理、工具命名空间、状态追踪 | F-028, F-029, F-030, F-031, F-032, F-033, F-034 |
| `packages/core/src/mcp/mcp-client.ts` | MCP 单服务器客户端，JSON-RPC over stdio，协议握手 | F-035, F-036, F-037, F-038, F-039, F-040, F-041 |
| `packages/core/src/common/permissions.ts` | 权限计算、工具调用权限解析、权限计划构建 | F-014, F-016 |

## CLI 包（`packages/cli/`）

| 文件路径 | 角色 | 支持事实 |
|---------|------|---------|
| `packages/cli/package.json` | CLI 包配置，声明 ink/react/yargs 依赖和 bin 入口 | F-009, F-012 |
| `packages/cli/src/cli.tsx` | CLI 主入口，参数解析、TTY 检查、Ink TUI 挂载、会话恢复 | F-042, F-051 |
| `packages/cli/src/cli-args.ts` | yargs 参数定义、验证规则、斜杠命令 EPILOG | F-043, F-044, F-045, F-046 |
| `packages/cli/src/exec-runner.ts` | 非交互执行模式，单轮提示运行，权限错误处理 | F-047 |

## VSCode 扩展包（`packages/vscode-ide-companion/`）

| 文件路径 | 角色 | 支持事实 |
|---------|------|---------|
| `packages/vscode-ide-companion/package.json` | VSCode 扩展清单，命令、视图容器、活动栏贡献 | F-011, F-055, F-056 |

## 文档

| 文件路径 | 角色 | 支持事实 |
|---------|------|---------|
| `docs/mcp.md` | MCP 配置指南，工具命名规则、服务器示例、故障排查 | F-057, F-058, F-059 |
