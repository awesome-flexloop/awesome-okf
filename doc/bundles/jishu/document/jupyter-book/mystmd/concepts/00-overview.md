---
type: concept
title: MySTmd 整体架构
description: MySTmd（Markedly Structured Text Markdown）是 Jupyter Book 团队开发的 MyST Markdown 引擎，包含解析器、转换管线、配置系统、frontmatter 处理和 CLI 工具链，支持从 Markdown 到 HTML/PDF/DOCX/LaTeX/Typst/JATS 等多格式输出。
tags: [mystmd, overview, architecture, parser, transforms, cli]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "/references/myst-parser-source.md"
    facts: [F-001, F-002, F-003, F-004, F-145, F-146, F-147, F-148]
  - path: "/references/mystmd-cli-source.md"
    facts: [F-113, F-114, F-115, F-116]
---

## 什么是 MySTmd

MySTmd 是 [MyST（Markedly Structured Text）](https://mystmd.org) Markdown 的 TypeScript 参考实现引擎，由 Jupyter Book 团队开发维护。它实现了 MyST Markdown 语法规范的完整解析、MDAST（Markdown Abstract Syntax Tree）转换和多格式输出管线，是 Jupyter Book、mystmd CLI 等工具的核心依赖。

MyST 在 CommonMark Markdown 基础上扩展了以下能力：
- **指令（Directives）**：块级扩展语法，如 ` ```{note} ` 提示块、` ```{figure} ` 图片
- **角色（Roles）**：行内扩展语法，如 `{math}`e=mc^2`{math}` 行内公式
- **Frontmatter**：YAML 元数据头
- **数学公式**：$...$ 和 $$...$$ 语法
- **引用与交叉引用**：`[](target)`、`{cite}`key`{cite}` 等
- **脚注**：`[^1]` 语法
- **定义列表**：术语/描述对
- **任务列表**：`- [x]` 复选框
- **块分隔**：`+++` 块断点

## 包架构总览

MySTmd 采用 monorepo 架构，核心包及其职责如下：

```
┌──────────────────────────────────────────────────────────────┐
│                     mystmd (CLI)                             │
│  init / build / start / clean / templates                    │
├──────────────────────────────────────────────────────────────┤
│                     myst-cli (CLI 核心)                       │
│  build (html/pdf/docx/jats/tex/typst/meca/md) / session     │
│  process / project / store / transforms / utils              │
├──────────────────────────────────────────────────────────────┤
│  myst-parser  │ myst-transforms  │ myst-common  │ myst-spec  │
│  分词+解析     │ 30+ AST转换插件   │ 类型+工具     │ 节点类型规范│
├───────────────┼──────────────────┼──────────────┼────────────┤
│ myst-config   │ myst-frontmatter  │ simple-validators          │
│ 配置验证       │ 20+元数据模块      │ 运行时校验函数              │
├───────────────┴──────────────────┴───────────────────────────┤
│ markdown-it-myst │ myst-directives │ myst-roles                │
│ markdown-it 插件  │ 内置指令实现     │ 内置角色实现               │
├──────────────────────────────────────────────────────────────┤
│ citation-js-utils  │ myst-spec-ext  │ myst-execute             │
│ 引用格式化工具       │ 类型兼容层      │ 代码执行引擎              │
└──────────────────────────────────────────────────────────────┘
```

## 核心数据流

MySTmd 的文档处理管线分为以下阶段：

```
Markdown 字符串
     │
     ▼
┌─────────────────────┐
│ 1. Tokenization     │  markdown-it + myst 插件
│    (分词)           │  → markdown-it Token 流
└─────────────────────┘
     │
     ▼
┌─────────────────────┐
│ 2. MDAST Build      │  MarkdownParseState 栈式解析
│    (AST 构建)       │  tokensToMyst → 原始 MDAST 树
└─────────────────────┘
     │
     ▼
┌─────────────────────┐
│ 3. Directives/Roles │  applyDirectives / applyRoles
│    (指令/角色处理)   │  替换 mystDirective/mystRole 节点
└─────────────────────┘
     │
     ▼
┌─────────────────────┐
│ 4. Basic Transforms │  basicTransformationsPlugin
│    (基础转换)        │  22 个有序 transform
└─────────────────────┘
     │
     ▼
┌─────────────────────┐
│ 5. Frontmatter      │  getFrontmatter 提取 YAML 元数据
│    (元数据提取)      │  与首个 H1 合并标题
└─────────────────────┘
     │
     ▼
┌─────────────────────┐
│ 6. Project Transforms│ enumerateTargets / resolveReferences
│    (项目级转换)      │  buildToc / include / links / citations
└─────────────────────┘
     │
     ▼
┌─────────────────────┐
│ 7. Renderers        │  HTML / PDF (LaTeX/Typst) / DOCX
│    (渲染输出)        │  JATS / Markdown / MECA
└─────────────────────┘
```

## 插件体系

MySTmd 的扩展点通过三种 Spec 类型定义：

| 插件类型 | Spec 接口 | 注册方式 | 阶段 |
|---------|----------|---------|------|
| Directive（指令） | `DirectiveSpec` | `mystParse({directives: [...]})` | 解析阶段 |
| Role（角色） | `RoleSpec` | `mystParse({roles: [...]})` | 解析阶段 |
| Transform（转换） | `TransformSpec` | MystPlugin.transforms | 转换阶段（document/project） |

多个插件可以打包为 `MystPlugin` 对象（含 directives/roles/transforms 数组），通过配置文件的 `plugins` 字段加载。

## 关键设计特点

1. **markdown-it 作为分词层**：不使用 micromark，复用 markdown-it 的 Token 系统，MyST 语法扩展全部通过 markdown-it 插件实现
2. **声明式 Token 映射**：`defaultMdast` 表定义 40+ token→MDAST 映射，`MarkdownParseState` 栈式自动构建嵌套节点
3. **两阶段指令处理**：先解析为 mystDirective/mystRole 原始节点，再通过 Spec 表二次处理替换 children
4. **有序转换管线**：basicTransformations 按严格顺序执行 22 个 transform，顺序依赖在源码注释中说明
5. **unified 兼容**：mystParser 作为 unified Plugin 暴露，各 transform 也提供 Plugin 包装，可以融入 unified 生态
6. **VFile 错误报告**：所有解析/转换错误通过 fileError/fileWarn 上报到 VFile，配合 RuleId 支持错误级别覆盖

## 技术栈

- **语言**：TypeScript（Node.js）
- **Markdown 解析**：markdown-it + markdown-it-myst 插件
- **AST 生态**：unist（unist-builder, unist-util-visit, unist-util-select, unist-util-remove）
- **插件协议**：unified Plugin
- **错误收集**：VFile
- **CLI 框架**：commander
- **YAML 解析**：js-yaml
- **引用处理**：@citation-js/core + @citation-js/plugin-bibtex + @citation-js/plugin-csl
- **HTML 实体处理**：he
- **数学渲染**：KaTeX（在 transform 层）

## 相关概念

- [统一插件架构](01-unified-plugin-architecture.md)
- [MyST 解析器](02-myst-parser.md)
- [MDAST 转换管线](03-myst-transforms.md)
- [公共类型系统](04-myst-common-types.md)
