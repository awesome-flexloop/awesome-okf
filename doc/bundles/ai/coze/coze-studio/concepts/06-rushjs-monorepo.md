---
type: concept
title: "Rush.js Monorepo 前端架构"
description: "Coze Studio 前端 Rush.js monorepo 架构、四级包层次、Rsbuild 构建系统、Semi Design UI 与 Zustand 状态管理"
tags: [Rush.js, Monorepo, React, Rsbuild, 前端架构, TypeScript]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-23T02:30:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T02:30:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: F-cs-046
    resource: /references/frontend-architecture.md
    title: "Rush.js 5.147.1 + pnpm 8.15.8"
  - id: F-cs-050
    resource: /references/frontend-architecture.md
    title: "四级包层次结构"
---

# Rush.js Monorepo 前端架构

Coze Studio 前端采用 Rush.js 管理的 monorepo 架构，将代码按职责和领域拆分为 50+ 个独立包。Rush.js 5.147.1 配合 pnpm 8.15.8 提供了可靠的依赖管理、增量构建和发布编排能力。整个前端遵循严格的四级包层次结构：从 level-1 的基础核心包到 level-4 的主应用，上层包依赖下层包，禁止反向依赖，确保架构清晰。

## Monorepo 工具链配置

| 工具 | 版本 | 用途 |
|------|------|------|
| **Rush.js** | 5.147.1 | Monorepo 编排、依赖管理、增量构建 |
| **pnpm** | 8.15.8 | 包管理器（Rush 内置） |
| **Node.js** | lts/iron (20.x) / rush.json >=21 | 运行时 |
| **TypeScript** | ~5.8.2 | 类型系统 |
| **Rsbuild** | ~1.1.0 | 构建工具（基于 Rspack） |
| **Vitest** | ~3.0.5 | 单元测试（含 @vitest/coverage-v8 覆盖率） |

### Rush.js 关键配置

- **项目搜索深度**：minDepth=3, maxDepth=6（从仓库根目录开始）
- **postRushInstall 钩子**：`scripts/hooks/post-rush-install.sh`，安装完成后执行环境初始化
- **Node 版本**：`rush.json` 要求 `nodeSupportedVersionRange: ">=21"`，`.nvmrc` 指定 `lts/iron`（Node 20.x LTS）

### 项目标签体系

Rush 的 `allowedProjectTags` 定义了三类标签：

| 标签类型 | 标签值 | 用途 |
|----------|--------|------|
| **团队标签** | `team-arch`, `team-builder`, `team-community`, `team-data`, `team-devops`, `team-automation`, `team-studio`, `team-qa`, `team-fullcode-app` | 标识包的归属团队 |
| **级别标签** | `level-1`, `level-2`, `level-3`, `level-4` | 标识包在四级架构中的层级 |
| **功能标签** | `rush-x`, `rush-tools`, `core`, `enabled-bundle-diff`, `phase-prebuild`, `channel-coze` | 标识构建和发布特性 |

## 四级包层次

```
                         ┌─────────────────────┐
                         │  level-4: apps/     │
                         │  @coze-studio/app   │
                         │  (主应用 v0.0.1)    │
                         └─────────┬───────────┘
                                   │ depends on
              ┌────────────────────┼────────────────────┐
              ▼                    ▼                    ▼
    ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
    │  level-3:       │  │  level-3:       │  │  level-3:       │
    │  agent-ide/     │  │  workflow/      │  │  studio/        │
    │  (智能体IDE)    │  │  (工作流领域)   │  │  (Studio 领域)  │
    │  context/entry  │  │  base/nodes/    │  │                 │
    │  layout/navigate│  │  render/sdk/    │  │                 │
    │  prompt/tool/   │  │  history/test-  │  │                 │
    │  workflow/commons│ │  run/variable/  │  │                 │
    │                 │  │  setters        │  │                 │
    └────────┬────────┘  └────────┬────────┘  └────────┬────────┘
             │                    │                    │
             └────────────────────┼────────────────────┘
                                  │ depends on
                         ┌────────┴───────────┐
                         │  level-2: common/  │
                         │  (共享组件/工具)    │
                         └────────┬───────────┘
                                  │ depends on
                         ┌────────┴───────────┐
                         │  level-1: arch/    │
                         │  (核心基础包 20+)  │
                         │  api-schema/bot-  │
                         │  http/bot-store/  │
                         │  i18n/idl/hooks/  │
                         │  logger/tea/...   │
                         └────────────────────┘
```

### level-1: arch/ 核心基础包（20+ 个）

arch/ 是整个前端的基础层，提供框架无关的核心能力：

| 包 | 职责 |
|----|------|
| `api-schema` | API Schema 定义和校验 |
| `bot-api` | Bot API 客户端封装 |
| `bot-env` | 环境变量管理 |
| `bot-error` | 统一错误处理 |
| `bot-flags` | 特性开关（Feature Flags） |
| `bot-hooks` | 业务级 React Hooks |
| `bot-http` | HTTP 请求客户端（Fetch 封装） |
| `bot-space-api` | Space 域 API 客户端 |
| `bot-store` | 状态管理（Zustand store 基类） |
| `bot-tea` | 埋点 SDK 封装 |
| `bot-typings` | 全局类型定义 |
| `bot-utils` | 通用工具函数 |
| `fetch-stream` | 流式 Fetch（SSE/流式响应处理） |
| `hooks` | 通用 React Hooks |
| `i18n` | 国际化框架 |
| `idl` | IDL 生成的 TS 类型 |
| `logger` | 日志系统 |
| `pdfjs-shadow` | PDF.js 渲染封装 |
| `report-events` | 事件上报 |
| `report-tti` | TTI 性能指标上报 |
| `tea` | 字节跳动埋点 SDK 核心 |
| `tea-adapter` | 埋点适配器 |
| `utils` | 工具函数集 |
| `web-context` | Web 应用上下文 |

### level-2: common/ 共享包

common/ 层提供跨领域复用的 UI 组件和业务逻辑，是 arch/ 和 feature 层之间的桥梁。

### level-3: 特性领域包

三个主要的特性领域：

- **agent-ide/**：智能体 IDE，包含上下文管理（context）、入口（entry）、布局（layout）、导航（navigate）、提示词编辑（prompt）、工具配置（tool）、工作流集成（workflow）、公共组件（commons）
- **workflow/**：工作流编辑器，基于 FlowGram 引擎，包含基础类型（base）、节点定义（nodes）、渲染引擎（render）、SDK（sdk）、历史管理（history）、测试运行（test-run）、变量管理（variable）、属性设置器（setters）
- **studio/**：Studio 主界面域

### level-4: apps/ 主应用

主应用包 `@coze-studio/app` v0.0.1（私有包），位于 `frontend/apps/coze-studio/`，是所有上层包的集成入口。它将 agent-ide、workflow、studio 等领域包组装为完整的 Web 应用。

## IDL 工具链

前端通过 `infra/idl/` 中的 6 个工具包实现从 Thrift IDL 到 TypeScript 的代码生成：

| 工具 | 职责 |
|------|------|
| `idl-parser` | Thrift IDL 词法/语法分析器 |
| `idl2ts-cli` | 命令行入口 |
| `idl2ts-generator` | 代码生成核心引擎 |
| `idl2ts-helper` | 生成辅助工具 |
| `idl2ts-plugin` | 插件系统（支持自定义生成规则） |
| `idl2ts-runtime` | 运行时序列化/反序列化库 |

这与后端的 hz 工具形成双端代码生成体系，确保前后端类型一致。

## 构建配置

### Rsbuild 构建

Rsbuild 是基于 Rspack（Rust 实现的 Webpack 替代）的高性能构建工具：

- **代码分割**：按大小分割（split-by-size），minSize 3MB，maxSize 6MB
- **装饰器支持**：legacy 模式，支持 inversify 的 `@injectable()`/`@inject()` 依赖注入装饰器
- **ES2022 语法**：支持 node_modules 中 `marked`、`markedjs`、`@dagrejs`、`@tanstack` 等包的 ES2022 语法
- **开源标识**：构建时设置 `IS_OPEN_SOURCE=true` 环境变量
- **开发代理**：dev server 将 `/api` 和 `/v1` 代理到 `http://localhost:8888`（后端服务）

### 共享配置

`config/` 目录提供统一的构建和质量检查配置：

| 配置包 | 用途 |
|--------|------|
| `eslint-config` | ESLint 规则 |
| `postcss-config` | PostCSS 处理 |
| `rsbuild-config` | Rsbuild 共享配置 |
| `stylelint-config` | Stylelint CSS 规则 |
| `tailwind-config` | Tailwind CSS 主题配置 |
| `ts-config` | TypeScript 编译选项 |
| `vitest-config` | Vitest 测试配置 |

## UI 技术栈

| 类别 | 技术 | 版本 |
|------|------|------|
| UI 框架 | React | ~18.2.0 |
| DOM 渲染 | react-dom | ~18.2.0 |
| 路由 | react-router-dom | ^6.11.1 |
| 状态管理 | Zustand | ^4.4.7 |
| UI 组件库 | Semi Design (@coze-arch/coze-design) | 0.0.6-alpha.346d77 |
| CSS 框架 | Tailwind CSS | ~3.3.3 |
| 错误边界 | react-error-boundary | ^4.0.9 |
| HTML 标题 | "扣子 Studio" | — |

Zustand 作为轻量级状态管理方案，配合 `bot-store` 包提供的 store 基类，实现了简洁高效的状态管理。Semi Design 是字节跳动开源的企业级 UI 组件库，Coze Studio 使用定制版 `@coze-arch/coze-design`。

## Docker 构建

前端 Docker 使用两阶段构建：

```dockerfile
# 阶段1: 构建
FROM node:22-alpine AS builder
# 配置中国镜像加速（aliyun alpine, npmmirror.com）
# rush update → rush build --to @coze-studio/app
# 产物输出到 dist/

# 阶段2: 运行
FROM nginx:1.25-alpine
# 复制 dist/ → /usr/share/nginx/html
# nginx 监听 80 端口
# 宿主机映射: ${WEB_LISTEN_ADDR:-8888}:80
```

构建命令：
```bash
rush build --to @coze-studio/app
```

## 相关概念

- [整体架构概览](00-overview-ddd-architecture.md)
- [工作流与智能体编辑器](07-workflow-editor.md)
- [Thrift IDL 与代码生成](02-thrift-idl-codegen.md)
- [部署与运维](08-deployment-operations.md)
- [前端架构参考](../references/frontend-architecture.md)
