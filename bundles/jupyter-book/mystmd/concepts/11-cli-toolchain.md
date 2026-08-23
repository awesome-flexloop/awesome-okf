---
type: concept
title: CLI 工具链（mystmd）
description: mystmd 是基于 commander 的命令行工具，提供 init/build/start/clean/templates 五个核心子命令，通过 myst-cli 包的 Session 系统执行文档构建、开发服务器和模板管理。
tags: [mystmd, cli, commander, build, dev-server]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "/references/mystmd-cli-source.md"
    facts: [F-113, F-114, F-115, F-116]
---

## CLI 概述

`mystmd` 是 MyST Markdown 的命令行工具入口，提供项目初始化、构建、开发服务器、清理和模板管理功能。底层通过 `myst-cli` 包的 Session 系统和 build 函数执行实际工作。

## 全局选项

| 选项 | 缩写 | 说明 |
|------|------|------|
| `--version` | `-v` | 输出版本号 |
| `--debug` | `-d` | 启用调试模式，将完整错误栈输出到控制台 |
| `--config <path>` | — | 指定替代的 YAML 配置文件路径（默认 myst.yml） |

## 子命令

### init（初始化）

```bash
myst init
```

初始化一个新的 MyST 项目：
- 交互式创建 myst.yml 配置文件
- 引导用户设置项目标题、作者等基本信息
- 可选择从模板创建初始文档结构

### build（构建）

```bash
myst build [options]
```

构建项目为可部署的静态站点或导出文件：
- 读取 myst.yml 配置
- 解析所有 Markdown/Notebook 文件
- 执行完整转换管线（解析→指令/角色→basic transforms→project transforms）
- 渲染为指定格式输出
- 生成站点清单（SiteManifest）

| 选项 | 说明 |
|------|------|
| `--watch` | 持续构建模式，监听文件变更自动重新构建 |
| `--site` | 构建站点（多页） |
| `--pdf` | 导出 PDF（通过 LaTeX 或 Typst） |
| `--docx` | 导出 DOCX |
| `--tex` | 导出 LaTeX |
| `--jats` | 导出 JATS XML |
| `--typst` | 使用 Typst 导出 |
| `--meca` | 导出 MECA 归档 |
| `--md` | 导出标准 Markdown |
| `--all` | 导出所有格式 |

### start（开发服务器）

```bash
myst start [options]
```

启动本地开发服务器：
- 启动 HTTP 服务器（默认端口 3000）
- 监听文件变更，自动重新构建
- 浏览器热更新（LiveReload）
- 提供构建预览和错误诊断界面

| 选项 | 说明 |
|------|------|
| `--port <port>` | 指定端口（默认 3000） |
| `--headless` | 无头模式（不自动打开浏览器） |
| `--server` | 仅服务器模式（不监听文件变更） |

### clean（清理）

```bash
myst clean
```

清理构建产物：
- 删除 `_build/` 目录（或配置的输出目录）
- 删除临时缓存文件
- 不删除源文件和配置

### templates（模板管理）

```bash
myst templates <subcommand>
```

管理文档和站点模板：
- `list` — 列出可用模板
- `install` — 安装/下载模板
- `remove` — 移除已安装模板
- `default` — 设置默认模板
- `publish` — 发布自定义模板

## CLI 启动流程

```
myst build
     │
     ▼
1. 导入 core-js/actual（向后兼容 polyfill）
     │
     ▼
2. 抑制 punycode DeprecationWarning
     │ （Node.js 内置模块弃用警告噪音）
     │
     ▼
3. 创建 commander Command 实例
     │
     ▼
4. 白标（White Label）检查
     │ ├─ 读取 package.json 中的白标配置
     │ └─ 设置自定义 CLI 名称、描述、版本
     │
     ▼
5. 注册子命令
     │ ├─ makeInitCLI(program)    → init 命令
     │ ├─ makeBuildCLI(program)   → build 命令
     │ ├─ makeStartCLI(program)   → start 命令
     │ ├─ makeCleanCLI(program)   → clean 命令
     │ └─ makeTemplatesCLI(program) → templates 命令
     │
     ▼
6. 注册全局选项
     │ ├─ -v, --version
     │ ├─ -d, --debug
     │ └─ --config <path>
     │
     ▼
7. 添加默认命令（无子命令时显示帮助）
     │
     ▼
8. process.argv 解析与执行
     │
     ▼
9. clirun 包装器执行
     │ ├─ 加载配置文件（--config 指定路径或 myst.yml）
     │ ├─ 创建 Session 实例
     │ ├─ 加载插件
     │ ├─ 执行命令逻辑（build/start/init/clean/templates）
     │ └─ 处理错误（非 debug 模式下简化输出）
```

## clirun 运行时包装器

clirun 是 CLI 命令的通用执行包装器，处理：
- 配置文件加载与验证
- VFile 消息收集与格式化输出
- 错误处理（debug 模式输出完整栈，否则友好提示）
- 进程退出码（0=成功，1=有错误）
- 日志级别控制

## Build 流程详解

build 命令委托给 myst-cli 包：

```
myst build
     │
     ▼
Session 初始化
     ├─ 加载 myst.yml 配置
     ├─ 验证配置
     ├─ 加载插件（MystPlugin）
     └─ 初始化存储（Store）
     │
     ▼
发现源文件
     ├─ 扫描项目目录的 .md/.ipynb 文件
     ├─ 排除 exclude 模式匹配的文件
     └─ 确定入口文件（index 配置）
     │
     ▼
逐文档处理
     ├─ 读取文件内容
     ├─ mystParse → 原始 MDAST
     ├─ applyDirectives/Roles
     ├─ basicTransformations（22 个 transform）
     └─ 提取 Frontmatter
     │
     ▼
项目级处理
     ├─ enumerateTargets（全局编号）
     ├─ buildToc（目录树）
     ├─ includeFiles（嵌入外部文件）
     ├─ resolveReferences（交叉引用）
     ├─ embedNodes（节点嵌入）
     └─ transformCitations（参考文献）
     │
     ▼
渲染输出
     ├─ HTML（站点模式）
     ├─ PDF（LaTeX/Typst）
     ├─ DOCX
     ├─ LaTeX
     ├─ Typst
     ├─ JATS
     ├─ Markdown
     └─ MECA 归档
     │
     ▼
生成 SiteManifest + 写入文件
```

## 相关概念

- [MyST 解析器](/concepts/02-myst-parser.md)
- [MDAST 转换管线](/concepts/03-myst-transforms.md)
- [配置系统](/concepts/10-configuration-system.md)
- [Frontmatter 元数据](/concepts/08-frontmatter.md)
- [基本解析示例](/examples/00-basic-parsing.md)
