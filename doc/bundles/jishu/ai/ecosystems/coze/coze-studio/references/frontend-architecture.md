---
type: reference
title: "前端架构参考"
description: "Coze Studio 前端 Rush.js monorepo、四级包层次、Rsbuild 构建、技术栈与 Docker 构建的完整技术参考"
tags: [前端, React, Rush.js, Rsbuild, TypeScript]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-23T02:30:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T02:30:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: F-cs-046
    resource: /references/frontend-architecture.md
    title: "Rush.js monorepo 配置"
  - id: F-cs-047
    resource: /references/frontend-architecture.md
    title: "四级包层次结构"
---

# 前端架构参考

## Monorepo 配置

| 工具 | 版本 |
|------|------|
| Rush.js | 5.147.1 |
| pnpm | 8.15.8 |
| Node.js | `.nvmrc` 指定 lts/iron (Node 20.x)；`rush.json` 要求 >=21 |
| TypeScript | ~5.8.2 |

### Rush.js 配置要点

- **项目深度**：minDepth=3, maxDepth=6
- **postRushInstall 钩子**：`scripts/hooks/post-rush-install.sh`
- **allowedProjectTags**：
  - 团队标签：`team-arch`, `team-builder`, `team-community`, `team-data`, `team-devops`, `team-automation`, `team-studio`, `team-qa`, `team-fullcode-app`
  - 级别标签：`level-1`, `level-2`, `level-3`, `level-4`
  - 功能标签：`rush-x`, `rush-tools`, `core`, `enabled-bundle-diff`, `phase-prebuild`, `channel-coze`

## 四级包层次结构

```
packages/
├── arch/          # level-1 核心基础包（20+ 包）
├── common/        # level-2 共享组件包
├── agent-ide/     # level-3 智能体 IDE 领域
├── workflow/      # level-3 工作流领域
└── studio/        # level-3 Studio 领域
apps/
└── coze-studio/   # level-4 主应用 (@coze-studio/app v0.0.1, private)
```

### level-1: arch/ 核心包（20+ 个）

| 包名 | 说明 |
|------|------|
| `api-schema` | API Schema 定义 |
| `bot-api` | Bot API 客户端 |
| `bot-env` | 环境变量 |
| `bot-error` | 错误处理 |
| `bot-flags` | 特性开关 |
| `bot-hooks` | React Hooks |
| `bot-http` | HTTP 客户端 |
| `bot-space-api` | Space API |
| `bot-store` | 状态存储 |
| `bot-tea` | 埋点 SDK |
| `bot-typings` | 类型定义 |
| `bot-utils` | 工具函数 |
| `fetch-stream` | 流式请求 |
| `hooks` | 通用 Hooks |
| `i18n` | 国际化 |
| `idl` | IDL 处理 |
| `logger` | 日志 |
| `pdfjs-shadow` | PDF.js 封装 |
| `report-events` | 事件上报 |
| `report-tti` | TTI 性能上报 |
| `tea` | 埋点核心 |
| `tea-adapter` | 埋点适配器 |
| `tea-interface` | 埋点接口 |
| `utils` | 通用工具 |
| `web-context` | Web 上下文 |

### level-3: workflow/ 工作流包

| 包名 | 说明 |
|------|------|
| `base` | 基础类型与常量 |
| `nodes` | 节点定义 |
| `render` | 渲染引擎 |
| `sdk` | SDK 接口 |
| `history` | 历史记录（撤销/重做） |
| `test-run` | 测试运行 |
| `variable` | 变量管理 |
| `setters` | 属性设置器 |

### level-3: agent-ide/ 智能体 IDE 包

| 包名 | 说明 |
|------|------|
| `context` | 上下文管理 |
| `entry` | 入口模块 |
| `layout` | 布局组件 |
| `navigate` | 导航 |
| `prompt` | 提示词编辑 |
| `tool` | 工具配置 |
| `workflow` | 工作流集成 |
| `commons` | 公共组件 |

### infra/idl/ IDL 工具链（6 个工具）

| 工具 | 说明 |
|------|------|
| `idl-parser` | Thrift IDL 解析器 |
| `idl2ts-cli` | IDL 转 TS 命令行工具 |
| `idl2ts-generator` | IDL 转 TS 生成器 |
| `idl2ts-helper` | IDL 转 TS 辅助工具 |
| `idl2ts-plugin` | IDL 转 TS 插件 |
| `idl2ts-runtime` | IDL 转 TS 运行时 |

## 构建配置

### Rsbuild

- 构建工具：**Rsbuild ~1.1.0**（基于 Rspack）
- 环境变量：`IS_OPEN_SOURCE=true`
- 代码分割：`split-by-size`，minSize 3MB，maxSize 6MB
- 装饰器：legacy 模式（支持 inversify 的 `@injectable()`/`@inject`）
- 源码包含：`packages/`、`flags-devtool`、以及 `node_modules` 中 `marked/markedjs/@dagrejs/@tanstack`（ES2022 语法）

### 开发代理

开发模式下，`/api` 和 `/v1` 路径代理到后端 `http://localhost:8888`。

### HTML

页面标题为 **"扣子 Studio"**。

## 核心技术栈

| 类别 | 技术 | 版本 |
|------|------|------|
| 框架 | React | ~18.2.0 |
| DOM | react-dom | ~18.2.0 |
| 路由 | react-router-dom | ^6.11.1 |
| 状态管理 | Zustand | ^4.4.7 |
| 错误边界 | react-error-boundary | ^4.0.9 |
| UI 组件 | Semi Design (@coze-arch/coze-design) | 0.0.6-alpha.346d77 |
| CSS | Tailwind CSS | ~3.3.3 |
| 测试 | Vitest | ~3.0.5 (with @vitest/coverage-v8) |

## 配置包

`config/` 目录下的共享配置：

| 配置 | 说明 |
|------|------|
| `eslint-config` | ESLint 共享配置 |
| `postcss-config` | PostCSS 配置 |
| `rsbuild-config` | Rsbuild 共享配置 |
| `stylelint-config` | Stylelint 配置 |
| `tailwind-config` | Tailwind CSS 配置 |
| `ts-config` | TypeScript 共享配置 |
| `vitest-config` | Vitest 测试配置 |

## Docker 构建

前端 Docker 采用**两阶段构建**：

1. **构建阶段**：`node:22-alpine`
   - 执行 `rush build --to @coze-studio/app`
   - 支持中国镜像加速（aliyun alpine、npmmirror.com）
   - 构建产物输出到 dist 目录

2. **运行阶段**：`nginx:1.25-alpine`
   - 将构建产物复制到 nginx `/usr/share/nginx/html`
   - nginx 监听 80 端口
   - 通过 `${WEB_LISTEN_ADDR:-8888}` 映射到宿主机
