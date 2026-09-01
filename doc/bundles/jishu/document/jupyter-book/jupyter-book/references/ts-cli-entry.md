---
type: reference
title: "TypeScript CLI 入口与命令委托"
description: "Jupyter Book v2 TypeScript 层源码：index.ts 入口、clirun.ts 统一执行器、各命令委托实现"
tags: [jupyter-book, reference, typescript, cli, commander]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "ts/index.ts"
    facts: [F-011, F-012, F-013]
  - path: "ts/clirun.ts"
    facts: [F-014, F-015]
  - path: "ts/build.ts"
    facts: [F-016]
  - path: "ts/init.ts"
    facts: [F-017, F-018]
  - path: "ts/clean.ts"
    facts: [F-019]
  - path: "ts/site.ts"
    facts: [F-020]
  - path: "ts/templates.ts"
    facts: [F-021, F-022, F-023, F-024]
  - path: "ts/options.ts"
    facts: [F-025]
---

# TypeScript CLI 入口与命令委托

本文档登记 Jupyter Book v2 TypeScript CLI 层的源码。TS 层是 Jupyter Book 的实际 CLI 实现，通过白标环境变量定制 myst-cli。

## 文件结构

```
ts/
├── index.ts       # CLI 入口：创建 commander 程序、注册命令、设置白标
├── clirun.ts      # 统一命令执行器（Session/日志/错误处理）
├── build.ts       # build 命令（委托 myst-cli）
├── init.ts        # init 命令（委托 myst-cli + 自定义选项）
├── clean.ts       # clean 命令（委托 myst-cli）
├── site.ts        # start 命令（委托 myst-cli）
├── templates.ts   # templates 命令（list/download，委托 myst-templates）
├── options.ts     # Jupyter Book 自定义 CLI 选项
└── version.ts     # 版本号
```

## index.ts（CLI 入口）

- Shebang：`#!/usr/bin/env node`
- 导入 `core-js/actual` 提供 Node.js 旧版兼容
- 抑制 punycode 弃用警告
- **白标环境变量**（在 commander 解析前设置）：
  - `MYSTMD_READABLE_NAME = "Jupyter Book"`
  - `MYSTMD_BINARY_NAME = "jupyter book"`
  - `MYSTMD_HOME_URL = "https://jupyterbook.org/stable"`
  - `MYSTMD_NPM_BINARY_NAME = "jupyter-book"`
  - `MYSTMD_NPM_PACKAGE_NAME = "jupyter-book"`
- **注册命令**：init、build、start（site）、clean、templates
- **全局选项**：`-d, --debug`
- **默认命令**：无参数时执行 init（通过 `addDefaultCommand`）

## clirun.ts（统一执行器）

```typescript
function clirun(
  sessionClass: typeof Session,
  func: (session: ISession, ...args: any[]) => Promise<void> | void,
  program: Command,
  nArgs?: number
): (...args: any[]) => Promise<void>
```

**执行流程**：
1. 创建 chalkLogger（debug/info 级别）
2. `new sessionClass({ logger })` 创建 Session
3. `await session.reload()`
4. `getNodeVersion(session)` + `logVersions()` 记录版本
5. `checkNodeVersion(session)` 版本不满足则 exit(1)
6. try/catch 执行 `func(session, ...args.slice(0, nArgs))`
7. catch 中输出 debug 栈、错误消息，exit(1)
8. `session.showUpgradeNotice?.()` 显示升级提示

## 各命令实现

### build.ts（1行委托）

```typescript
export function makeBuildCLI(program: Command) {
  const command = makeBuildCommand().action(clirun(Session, build, program));
  return command;
}
```
`makeBuildCommand`、`build`、`Session` 全部来自 myst-cli。

### clean.ts（1行委托）

```typescript
export function makeCleanCLI(program: Command) {
  const command = makeCleanCommand().action(clirun(Session, clean, program));
  return command;
}
```

### site.ts（1行委托，对应 start 命令）

```typescript
export function makeStartCLI(program: Command) {
  const command = makeStartCommand().action(clirun(Session, startServer, program));
  return command;
}
```

### init.ts（少量自定义选项）

- 创建 `init` 命令，描述 "Initialize a mystmd project"
- 添加选项：`--project`、`--site`（来自 myst-cli）、`--write-toc`、`--gh-pages`、`--gh-curvenote`（自定义）
- Action：`clirun(Session, init, program)` 委托 myst-cli 的 init
- `addDefaultCommand(program)`: 无参数时默认执行 init

### templates.ts（最复杂的命令）

- 创建 `templates` 命令，含两个子命令：
  - `list [name]`: 列出公共模板或查看模板详情，支持 `--tag` 过滤和类型选项（--pdf/--tex/--typst/--docx/--site）
  - `download <template> [path]`: 下载模板到本地，支持 `--force` 覆盖
- 核心函数：
  - `listTemplatesCLI(session, name?, opts?)`: 列表/详情逻辑，从 myst-templates 调用 `listPublicTemplates`/`fetchPublicTemplate`
  - `downloadTemplateCLI(session, template, path?, opts?)`: 下载逻辑，调用 `resolveInputs`/`downloadTemplate`（来自 myst-templates）
- 模板类型通过前缀匹配（`tex//typst/docx/site）或 CLI flag 推断

### options.ts（Jupyter Book 专属选项）

- `makeProjectOption(description)`: `--project` 布尔选项
- `makeWriteTOCOption()`: `--write-toc` 选项，implies writeTOC
- `makeGithubPagesOption()`: `--gh-pages` 选项
- `makeGithubCurvenoteOption()`: `--gh-curvenote` 选项

## 相关概念

- [00-v2-architecture](../concepts/00-v2-architecture.md)：v2 双层架构
- [02-ts-cli-commands](../concepts/02-ts-cli-commands.md)：TS CLI 命令详解
- [03-myst-cli-relationship](../concepts/03-myst-cli-relationship.md)：与 myst-cli 的关系
- [04-template-system](../concepts/04-template-system.md)：模板系统
