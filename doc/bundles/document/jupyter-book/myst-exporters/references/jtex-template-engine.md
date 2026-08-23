---
type: reference
title: "jtex 模板引擎源码"
description: "jtex 包核心源码：renderTemplate 函数、Nunjucks 环境配置、LaTeX/Typst imports 渲染"
tags: [myst-exporters, reference, jtex, template, nunjucks]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "jtex/src/jtex.ts"
    facts: [F-025, F-026, F-027]
  - path: "jtex/src/render.ts"
    facts: [F-028]
  - path: "jtex/src/tex/imports.ts"
    facts: [F-029]
  - path: "jtex/src/tex/export.ts"
    facts: [F-030]
  - path: "jtex/src/typst/imports.ts"
    facts: [F-031]
  - path: "jtex/src/types.ts"
    facts: []
---

# jtex 模板引擎源码

本文档登记 jtex 包的核心源码结构和公共 API。jtex 是 LaTeX/Typst 模板渲染引擎，基于 Nunjucks 模板语法实现。

## 包结构

```
jtex/src/
├── index.ts          # 包入口，重导出所有公共 API
├── jtex.ts           # 核心 renderTemplate 函数
├── render.ts         # renderImports 分发函数
├── types.ts          # 类型定义
├── utils.ts          # 工具函数
├── version.ts        # 版本号
├── cli/              # CLI 命令（check/index）
├── tex/              # LaTeX 专属逻辑
│   ├── exports.ts    # PDF 导出命令生成（latexmk/makeglossaries）
│   ├── imports.ts    # LaTeX usepackage/newcommand 渲染
│   └── index.ts      # LaTeX 相关导出
└── typst/            # Typst 专属逻辑
    ├── exports.ts    # Typst 导出（当前文件存在但未在 index.ts 中重导出导出函数）
    ├── imports.ts    # Typst #import/#let 渲染
    └── index.ts      # Typst 相关导出
```

## 核心 API

### renderTemplate

- **路径**：`jtex/src/jtex.ts` L46-104
- **签名**：
```typescript
function renderTemplate(
  template: MystTemplate,
  opts: {
    contentOrPath: string;       // 内容字符串或文件路径
    imports?: TexTemplateImports | TypstTemplateImports;
    preamble?: string;
    packages?: string[];          // 模板已包含的包（避免重复 usepackage）
    force?: boolean;
    frontmatter: any;
    parts: any;
    options: any;
    bibliography?: string;
    outputPath: string;
    sourceFile?: string;
    filesPath?: string;
    removeVersionComment?: boolean;
  }
): void
```

### getDefaultEnv

- **路径**：`jtex/src/jtex.ts` L15-31
- 创建 Nunjucks 环境，配置：
  - 模板目录：`template.templatePath`
  - `trimBlocks: true`
  - `autoescape: false`（输出 LaTeX/Typst，不需要 HTML 转义）
  - 自定义标签：`[# #]`（块）、`[- -]`（变量）、`%# #%`（注释）
  - 添加 `len` filter

### renderImports

- **路径**：`jtex/src/render.ts`
- 按 `kind` 分发到 `renderTexImports` 或 `renderTypstImports`

### LaTeX imports 渲染

- **路径**：`jtex/src/tex/imports.ts`
- `createTexImportCommands(commands, existingPackages?)`: 生成 `\usepackage{name}` 列表，去重排序，过滤已有包
- `createTexMathCommands(plugins)`: 从 `Record<string, string>` 生成 `\newcommand{\name}[nArgs]{definition}`，自动检测参数个数（匹配 `#[1-9]`）
- `renderTexImports(templateImports?, existingPackages?, preamble?)`: 组装带分隔线注释的完整 imports 块
- `mergeTexTemplateImports(current?, next?)`: 合并 imports（commands 覆盖合并，imports 去重并集）

### Typst imports 渲染

- **路径**：`jtex/src/typst/imports.ts`
- `renderTypstImports(output, templateImports?, preamble?)`:
  - macros → `#import "myst-imports.typ": *`，macros 内容写入 `myst-imports.typ` 文件
  - commands → `#let \name = $definition$`
- `mergeTypstTemplateImports(current?, next?)`: 合并 macros 和 commands

### PDF 编译命令

- **路径**：`jtex/src/tex/export.ts`
- `pdfTexExportCommand(texFile, logFile, template?)`: 生成 latexmk 命令（默认 xelatex 引擎）
- `texMakeGlossariesCommand(texFile, logFile)`: 生成 makeglossaries 命令

## 模板文件约定

模板目录包含：
- `template.tex` 或 `template.typ`：Nunjucks 模板文件，使用 `[-CONTENT-]`、`[-IMPORTS-]`、`[-doc.title-]` 等变量
- `template.yml`：模板元数据（模板选项、parts 定义、build 配置等，由 myst-templates 解析）
- 其他静态文件（图片、cls/sty 文件等）：由 `template.copyTemplateFiles()` 复制到输出目录

## 相关概念

- [08-jtex-template-engine](/concepts/08-jtex-template-engine.md)：jtex 模板引擎概念文档
- [02-latex-export](/concepts/02-latex-export.md)：LaTeX 导出流程
- [07-typst-export](/concepts/07-typst-export.md)：Typst 导出流程
- [02-custom-jtex-template](/examples/02-custom-jtex-template.md)：自定义 jtex 模板示例
