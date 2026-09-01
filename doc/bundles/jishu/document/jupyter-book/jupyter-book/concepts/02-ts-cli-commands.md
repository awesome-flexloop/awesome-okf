---
type: concept
title: "TypeScript CLI 命令体系"
description: "Jupyter Book v2 TypeScript 层的 commander 命令注册、clirun 统一执行器和各子命令实现"
tags: [jupyter-book, typescript, cli, commander, clirun, commands]
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

# TypeScript CLI 命令体系

Jupyter Book v2 的 TypeScript 层基于 [commander](https://github.com/tj/commander.js) 构建 CLI。TS 层的主要工作是配置白标环境变量、注册命令、然后将实际逻辑委托给 myst-cli。

## CLI 入口：index.ts

### 执行顺序

index.ts 的执行有严格的顺序要求：

1. **兼容性导入**：`import "core-js/actual"` 提供旧版 Node.js 兼容
2. **抑制警告**：禁用 punycode 弃用警告
3. **设置白标环境变量**（必须在 commander 解析之前，在 myst-cli 导入之前）
4. **导入 myst-cli 模块**（此时环境变量已设置，myst-cli 读取白标配置）
5. **创建 commander Program**
6. **注册子命令**
7. **解析命令行参数**（`program.parseAsync`）

### 白标环境变量详解

在所有 myst-cli import 之前设置的环境变量：

```typescript
process.env.MYSTMD_READABLE_NAME = "Jupyter Book";
process.env.MYSTMD_BINARY_NAME = "jupyter book";
process.env.MYSTMD_HOME_URL = "https://jupyterbook.org/stable";
process.env.MYSTMD_NPM_BINARY_NAME = "jupyter-book";
process.env.MYSTMD_NPM_PACKAGE_NAME = "jupyter-book";
```

这些变量在 myst-cli 内部用于：
- 帮助信息中的程序名称显示
- 错误消息中的品牌名
- 升级检查时的 npm 包名
- 文档链接指向
- 欢迎信息和 prompt 文本

### 全局选项

```typescript
program.option("-d, --debug", "Debug mode with verbose logging");
```

`--debug` 标志控制日志级别：
- 默认：`info` 级别
- `--debug`：`debug` 级别（显示更多细节，包括栈跟踪）

### 默认命令

当用户只输入 `jupyter-book` 不带任何子命令时，`addDefaultCommand(program)` 让 commander 默认执行 `init` 命令。这提供了友好的入门体验——新用户直接运行即可进入项目初始化向导。

## clirun 统一执行器

`clirun` 是一个高阶函数，为所有命令提供统一的执行上下文：

```typescript
function clirun(
  sessionClass: typeof Session,
  func: (session: ISession, ...args: any[]) => Promise<void> | void,
  program: Command,
  nArgs?: number
): (...args: any[]) => Promise<void>
```

### 执行流程

```
clirun 包装的命令被调用
  │
  ├── 1. 创建日志器
  │     const logger = chalkLogger({ level: debug ? 'debug' : 'info' })
  │
  ├── 2. 创建 Session
  │     const session = new sessionClass({ logger })
  │     await session.reload()
  │     Session 包含配置加载、项目状态、API 客户端等
  │
  ├── 3. 版本日志
  │     getNodeVersion(session)
  │     logVersions(session)  // 输出 Jupyter Book/Node.js/OS 版本
  │     checkNodeVersion(session)  // 版本不满足则 exit(1)
  │
  ├── 4. 执行命令函数
  │     try {
  │       await func(session, ...args.slice(0, nArgs))
  │     } catch (err) {
  │       session.log.debug(err)  // debug 模式显示栈
  │       session.log.error(err.message)  // 普通模式显示消息
  │       process.exit(1)
  │     }
  │
  └── 5. 升级提示
       session.showUpgradeNotice?.()
       检查 npm 上是否有新版本，提示升级
```

### 为什么用 clirun

- **统一日志**：所有命令使用相同的日志格式和级别控制
- **Session 生命周期**：统一创建/销毁 Session，确保资源正确初始化
- **错误处理**：统一的 try/catch，避免未处理的 Promise rejection
- **版本检查**：Node.js 版本检查集中在一处
- **升级通知**：所有命令完成后都检查升级
- **代码复用**：每个命令文件只需关注自己的业务逻辑

## 子命令详解

### init（项目初始化）

**文件**：ts/init.ts

```
jupyter-book init [path] [options]
```

- **描述**：Initialize a Jupyter Book project
- **参数**：可选的项目路径（默认为当前目录）
- **选项**：
  - `--project`：仅初始化 project 配置
  - `--site`：仅初始化 site 配置
  - `--write-toc`：自动生成目录文件
  - `--gh-pages`：添加 GitHub Pages 部署配置
  - `--gh-curvenote`：添加 Curvenote 部署配置
- **委托**：`init(session, path, opts)` 来自 myst-cli
- **特殊**：通过 `addDefaultCommand(program)` 设为默认命令

init 命令执行交互式向导，创建 `myst.yml` 配置文件和目录结构。

### build（构建文档）

**文件**：ts/build.ts（仅 1 行有效代码）

```
jupyter-book build [path] [options]
```

- **委托**：`makeBuildCommand()` 和 `build()` 完全来自 myst-cli
- **所有 build 选项**（--pdf、--docx、--html、--tex、--all 等）都继承自 myst-cli
- Jupyter Book 没有自定义 build 选项（完全复用 myst-cli 的 build）

build 命令解析文档、执行转换、生成输出文件（HTML/PDF/DOCX 等）。

### start（启动开发服务器）

**文件**：ts/site.ts（仅 1 行有效代码）

```
jupyter-book start [path] [options]
```

- **委托**：`makeStartCommand()` 和 `startServer()` 来自 myst-cli
- 启动本地开发服务器，支持热重载和浏览器预览
- 默认端口 3000（可通过 --port 修改）

### clean（清理构建产物）

**文件**：ts/clean.ts（仅 1 行有效代码）

```
jupyter-book clean [path] [options]
```

- **委托**：`makeCleanCommand()` 和 `clean()` 来自 myst-cli
- 删除 `_build/` 目录和临时文件
- `--html`、`--pdf`、`--exports`、`--temp` 等选项选择性清理

### templates（模板管理）

**文件**：ts/templates.ts（最复杂的命令，约 120 行）

```
jupyter-book templates <subcommand> [options]
```

包含两个子命令：

#### templates list [name]

列出公共模板仓库中的可用模板，或查看特定模板的详情。

- **参数**：`name` 可选，模板名称（不传则列出全部）
- **选项**：
  - `--tag <tag>`：按标签过滤
  - `--pdf` / `--tex` / `--typst` / `--docx` / `--site`：按模板类型过滤
- **实现**：调用 myst-templates 的 `listPublicTemplates` 或 `fetchPublicTemplate`
- 输出格式化的表格（模板名、描述、类型、标签）

#### templates download <template> [path]

下载模板到本地。

- **参数**：
  - `template`：模板名称（必填）
  - `path`：本地路径（默认当前目录）
- **选项**：
  - `--force`：覆盖已存在的模板文件
- **实现**：调用 myst-templates 的 `resolveInputs`（解析模板来源）和 `downloadTemplate`（下载文件）

### 选项工厂：options.ts

options.ts 提供 Jupyter Book 特有的 CLI 选项工厂函数：

| 函数 | 选项 | 说明 |
|------|------|------|
| `makeProjectOption(desc)` | `--project` | 项目配置选项 |
| `makeWriteTOCOption()` | `--write-toc` | 自动生成 TOC |
| `makeGithubPagesOption()` | `--gh-pages` | GitHub Pages 配置 |
| `makeGithubCurvenoteOption()` | `--gh-curvenote` | Curvenote 配置 |

这些函数返回 commander option 配置对象，在 init.ts 中使用。

## 命令委托模式总结

Jupyter Book TS 层有三种委托模式：

1. **完全委托**（build/clean/start）：
   - 1 行代码：从 myst-cli 导入 makeXxxCommand 和 xxx 函数
   - 直接 action 到 clirun 包装
   - 无任何自定义逻辑

2. **少量自定义**（init）：
   - 创建命令后添加 Jupyter Book 特有的选项（--gh-pages 等）
   - action 仍委托到 myst-cli 的 init 函数

3. **较多自定义**（templates）：
   - 自定义命令描述和帮助文本
   - 自定义子命令（list/download）
   - 调用 myst-templates API 实现功能
   - 自定义输出格式化

这种分层设计让 Jupyter Book 可以在保持与 myst-cli 功能同步的同时，逐步添加 Jupyter 生态特有的功能。

## 相关概念

- [00-v2-architecture](00-v2-architecture.md)：v2 双层架构
- [01-python-entry-nodeenv](01-python-entry-nodeenv.md)：Python 入口
- [03-myst-cli-relationship](03-myst-cli-relationship.md)：与 myst-cli 的关系
- [01-create-book](../examples/01-create-book.md)：创建 Jupyter Book 示例
