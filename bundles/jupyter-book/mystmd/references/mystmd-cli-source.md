---
type: Reference
title: mystmd CLI 与周边包源码信源
description: mystmd CLI 主入口、citation-js-utils 引用处理工具以及 markdown-it-myst 插件的源码登记。
tags: [mystmd, cli, citation, markdown-it, commander]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "mystmd/src/index.ts"
    facts: [F-113, F-114, F-115]
  - path: "mystmd/src/build.ts"
    facts: [F-116]
  - path: "citation-js-utils/src/index.ts"
    facts: [F-127, F-128, F-129, F-130, F-131, F-132, F-133, F-134, F-135, F-136, F-137, F-138]
  - path: "markdown-it-myst/src/index.ts"
    facts: [F-125, F-126]
---

## 源码位置

### mystmd CLI
- `mystmd/src/index.ts` — CLI 主入口
- `mystmd/src/build.ts` — build 命令
- `mystmd/src/clean.ts` — clean 命令
- `mystmd/src/init.ts` — init 命令
- `mystmd/src/start.ts` — start 命令
- `mystmd/src/templates.ts` — templates 命令
- `mystmd/src/options.ts` — CLI 选项
- `mystmd/src/clirun.ts` — CLI 运行时包装器

### citation-js-utils
- `citation-js-utils/src/index.ts` — 引用工具函数

### markdown-it-myst
- `markdown-it-myst/src/index.ts` — 包入口
- `markdown-it-myst/src/roles.ts` — rolePlugin
- `markdown-it-myst/src/directives.ts` — directivePlugin
- `markdown-it-myst/src/citations.ts` — citationsPlugin
- `markdown-it-myst/src/block.ts` — blockPlugin
- `markdown-it-myst/src/colonFence.ts` — colonFencePlugin
- `markdown-it-myst/src/utils.ts` — 工具函数

## mystmd CLI 命令

### 全局选项

| 选项 | 说明 |
|------|------|
| `-v, --version` | 输出版本号 |
| `-d, --debug` | 将错误输出到控制台 |
| `--config <config-file>` | 指定替代 YAML 配置文件路径 |

### 子命令

| 命令 | 来源 | 说明 |
|------|------|------|
| `init` | makeInitCLI | 初始化 MyST 项目 |
| `build` | makeBuildCLI | 构建项目（支持 --watch 持续构建） |
| `start` | makeStartCLI | 启动开发服务器 |
| `clean` | makeCleanCLI | 清理构建产物 |
| `templates` | makeTemplatesCLI | 模板管理 |

CLI 使用 commander 框架，build 命令委托给 myst-cli 包的 Session 和 build 函数，通过 clirun 包装器执行。

### CLI 启动流程

1. 导入 core-js/actual 提供向后兼容
2. 抑制 punycode DeprecationWarning
3. 创建 Command 实例
4. 检查白标（white labelling），设置描述
5. 注册子命令（init/build/start/clean/templates）
6. 注册全局选项（version/debug/config）
7. 设置默认命令（addDefaultCommand）
8. 解析 process.argv

## citation-js-utils API

### 类型定义

| 类型 | 说明 |
|------|------|
| `CSL` | Citation Style Language JSON 条目（type, id, author, issued, title, DOI, URL 等） |
| `CitationRenderer` | Record<string, {render, inline, getDOI, getURL, cite, getLabel, exportBibTeX}> |
| `InlineNode` | {type, value?, children?: InlineNode[]} 行内节点 |
| `InlineOptions` | {prefix?, suffix?, partial?: 'author'\|'year'} |

### 枚举

| 枚举 | 值 |
|------|-----|
| `CitationJSStyles` | apa='citation-apa', vancouver='citation-vancouver', harvard='citation-harvard1' |
| `InlineCite` | p='p', t='t' |

### 核心函数

| 函数 | 签名 | 说明 |
|------|------|------|
| `parseBibTeX` | `(source: string) => CSL[]` | 解析 BibTeX 字符串为 CSL 数组 |
| `parseCSLJSON` | `(source: object[]) => CSL[]` | 清理 CSL-JSON 数据 |
| `getCitationRenderers` | `(data: CSL[]) => CitationRenderer` | 为 CSL 条目创建渲染器映射 |
| `getCitations` | `(bibtex: string) => Promise<CitationRenderer>` | parseBibTeX+getCitationRenderers 兼容垫片 |
| `getInlineCitation` | `(data: CSL, kind: InlineCite, opts?: InlineOptions) => InlineNode[]` | 生成内联引用文本节点 |
| `yearFromCitation` | `(data: CSL) => number \| string` | 从 CSL 数据提取年份 |
| `createSanitizer` | `() => { cleanCitationHtml }` | 创建 HTML 清理器（仅允许 b/a/u/i 标签） |

### 引用格式化规则

- 1 位作者：`Family (Year)` 或 `(Family, Year)`
- 2 位作者：`Family & Family (Year)`
- 3+ 位作者：`Family *et al.* (Year)`（et al. 使用 emphasis 标记）
- 无作者：使用 publisher 或 title
- 无年份：返回 'n.d.'
- partial='author'：仅输出作者部分
- partial='year'：仅输出年份部分

## markdown-it-myst 插件

| 插件 | 说明 |
|------|------|
| `rolePlugin` | 解析 MyST 角色语法 `{role-name}`content`{role-name}` |
| `directivePlugin` | 解析 MyST 指令语法 ``` ```{directive-name} ``` |
| `citationsPlugin` | 解析 `[cite:@key]` 引用语法 |
| `blockPlugin` | 解析 MyST 块分隔（+++） |
| `colonFencePlugin` | 解析 `:::` 围栏语法 |
| `mystPlugin` | @deprecated 组合插件（rolePlugin+directivePlugin） |

所有插件均为标准 markdown-it 插件形式：`(md: MarkdownIt) => void`。
