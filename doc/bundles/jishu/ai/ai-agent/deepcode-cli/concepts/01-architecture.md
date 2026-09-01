---
type: Concept
title: 三包 monorepo 架构
description: deepcode-cli 采用 npm workspaces monorepo，分为 cli（Ink TUI）、core（无 UI 依赖的核心库）和 vscode-ide-companion（VSCode 扩展）三个包。
tags: [deepcode-cli, 架构, monorepo, npm-workspaces, 包结构]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T10:00:00+08:00 }
verified: { by: "process:grep-verification", at: 2026-08-23T10:00:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/source.md
    title: deepcode-cli 源码信源
---

# 三包 monorepo 架构

## 架构概览

deepcode-cli 使用 npm workspaces 管理三个子包，根 `package.json` 声明 `"workspaces": ["packages/*"]`。TypeScript 项目引用（`tsconfig.json` references）将三个包串联为可增量编译的复合项目。

```
deepcode-cli/
├── packages/
│   ├── core/                    # @vegamo/deepcode-core
│   ├── cli/                     # @vegamo/deepcode-cli
│   └── vscode-ide-companion/    # deepcode-vscode
├── package.json                 # 根 monorepo 配置
└── tsconfig.json                # 项目引用根配置
```

## 包依赖关系

```
vscode-ide-companion ──┐
                       ├──▶ core
cli ───────────────────┘
```

CLI 包和 VSCode 扩展包均通过 `"@vegamo/deepcode-core": "file:../core"` 引用核心库。

## @vegamo/deepcode-core

**路径**：`packages/core/`
**版本**：0.2.1
**模块类型**：ESM（`"type": "module"`）
**入口**：`dist/index.js`（类型声明 `dist/index.d.ts`）

Core 包是无 UI 依赖的纯逻辑库，其 `package.json` 中的运行时依赖为：

| 依赖 | 用途 |
|------|------|
| `openai` | OpenAI 兼容 API 客户端 |
| `ejs` | 提示模板渲染 |
| `gray-matter` | Markdown frontmatter 解析 |
| `zod` | 数据校验 |
| `undici` | HTTP 客户端 |
| `chalk` | 终端颜色 |
| `ignore` | .gitignore 风格过滤 |

Core 包通过 `src/index.ts` 统一导出公共 API，主要模块包括：

- **设置模块**：`resolveCurrentSettings`、`readSettings`、`writeSettings` 等
- **会话管理**：`SessionManager` 类、会话类型定义
- **MCP 模块**：`McpManager`、`McpClient`
- **工具执行**：`ToolExecutor` 及 8 个内置工具处理器
- **提示构建**：`getSystemPrompt`、`getCompactPrompt`、`getPlanModePrompt`

核心库导出的 8 个工具处理器（来自 `packages/core/src/index.ts:86-93`）：

```typescript
export { handleBashTool, clearSessionWorkingDir } from "./tools/bash-handler";
export { handleReadTool } from "./tools/read-handler";
export { handleWriteTool } from "./tools/write-handler";
export { handleEditTool } from "./tools/edit-handler";
export { handleUpdatePlanTool } from "./tools/update-plan-handler";
export { handleUnderstandImageTool } from "./tools/understand-image-handler";
export { handleWebSearchTool } from "./tools/web-search-handler";
export { handleAskUserQuestionTool } from "./tools/ask-user-question-handler";
```

## @vegamo/deepcode-cli

**路径**：`packages/cli/`
**版本**：0.2.1
**模块类型**：ESM
**二进制入口**：`dist/cli.js`（通过 `bin.deepcode` 注册）
**Node 要求**：>= 22

CLI 包负责终端交互层，依赖 Ink + React 构建 TUI：

| 依赖 | 用途 |
|------|------|
| `ink` | React for CLI 渲染框架 |
| `react` | UI 组件 |
| `yargs` | 命令行参数解析 |
| `chalk` | 终端颜色 |
| `gradient-string` | 渐变文字 |
| `ignore` | 文件过滤 |
| `read-package-up` | 包信息查找 |

CLI 入口 `src/cli.tsx` 的核心流程：

1. 解析命令行参数（yargs）
2. 处理 `--version`/`--help`
3. 配置 Windows shell 环境
4. 解析 `--last`/`--resume`/`--fork` 会话选项
5. 若 `--exec` 则运行非交互模式
6. 检查 TTY 可用性
7. 挂载 Ink `AppContainer` 组件

## deepcode-vscode

**路径**：`packages/vscode-ide-companion/`
**版本**：0.2.1
**发布者**：vegamo
**模块类型**：CommonJS
**VSCode 要求**：^1.85.0

VSCode 扩展提供编辑器内的 AI 聊天面板：

- 贡献命令 `deepcode.openView`（"Open Deep Code"）
- 在活动栏注册 `deepcode` 视图容器
- 包含 webview 视图 `deepcode.chatView`
- 依赖 `markdown-it` 渲染 Markdown
- 通过 esbuild 打包为 CJS 输出

## 构建系统

根目录 `scripts/` 包含构建脚本：

| 脚本 | 功能 |
|------|------|
| `esbuild.config.js` | 打包 CLI 和 core |
| `esbuild-vscode.config.js` | 打包 VSCode 扩展 |
| `build.js` | 统一构建入口 |
| `copy-bundle-assets.js` | 复制模板和技能资源 |
| `generate-git-commit-info.js` | 生成 Git 提交信息 |

根 `package.json` 中的关键脚本命令：

```json
{
  "typecheck": "npm run typecheck --workspaces --if-present",
  "bundle": "npm run generate && node scripts/esbuild.config.js && node scripts/copy-bundle-assets.js",
  "build": "node scripts/build.js",
  "test": "npm run test --workspaces --if-present"
}
```

## 模块类型差异

三个包的模块系统存在差异：core 和 cli 使用 ESM（`"type": "module"`），vscode-ide-companion 使用 CommonJS。这种差异通过 esbuild 打包解决——VSCode 扩展构建时将 core 的 ESM 代码打包为 CJS 输出。

## 相关概念

- [项目简介](00-introduction.md)
- [权限系统](02-permission-system.md)
- [MCP 集成](03-mcp-integration.md)
- [CLI 命令与会话管理](04-cli-commands.md)
