---
type: Reference
title: myst-spec / myst-spec-ext 节点类型源码信源
description: myst-spec 包定义的 50+ MyST 规范 AST 节点类型，以及 myst-spec-ext 的 deprecated 类型别名源码登记。
tags: [mystmd, myst-spec, ast, node-types, mdast]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "myst-spec/src/index.ts"
    facts: [F-095, F-096, F-097]
  - path: "myst-spec/src/ext.ts"
    facts: [F-098, F-099, F-100, F-101, F-102]
  - path: "myst-spec-ext/src/index.ts"
    facts: [F-103, F-104]
---

## 源码位置

- `myst-spec/src/index.ts` — 主入口，从 schema.d.ts 和 ext.ts 导出所有类型
- `myst-spec/src/schema.d.ts` — 基础节点类型定义（CommonMark + MyST 基础）
- `myst-spec/src/ext.ts` — MyST 扩展节点类型
- `myst-spec/src/search.ts` — 搜索索引相关类型
- `myst-spec-ext/src/index.ts` — Deprecated 别名导出

## 基础节点类型（来自 schema.d.ts）

### 文档结构

| 类型 | type 值 | 说明 |
|------|---------|------|
| `Root` | root | AST 根节点 |
| `Paragraph` | paragraph | 段落 |
| `Heading` | heading | 标题（depth: 1-6） |
| `Blockquote` | blockquote | 引用块 |
| `List` | list | 列表（ordered, spread, start） |
| `ListItem` | listItem | 列表项 |
| `ThematicBreak` | thematicBreak | 水平分隔线 |
| `DefinitionList` | definitionList | 定义列表 |
| `DefinitionTerm` | definitionTerm | 定义术语 |
| `DefinitionDescription` | definitionDescription | 定义描述 |
| `Table` | table | 表格 |
| `TableRow` | tableRow | 表格行 |
| `TableCell` | tableCell | 表格单元格（header, align） |

### 行内元素

| 类型 | type 值 | 说明 |
|------|---------|------|
| `Text` | text | 纯文本（value） |
| `Emphasis` | emphasis | 斜体 |
| `Strong` | strong | 粗体 |
| `InlineCode` | inlineCode | 行内代码 |
| `Break` | break | 硬换行 |
| `Delete` | delete | 删除线 |
| `Subscript` | subscript | 下标 |
| `Superscript` | superscript | 上标 |
| `Underline` | underline | 下划线 |
| `Smallcaps` | smallcaps | 小体大写 |
| `Link` | link | 链接（url, title） |
| `CrossReference` | crossReference | 交叉引用 |
| `Image` | image | 图片（url, alt, title） |
| `FootnoteReference` | footnoteReference | 脚注引用 |
| `HTML` | html | HTML 原始内容 |

### 代码与数学

| 类型 | type 值 | 说明 |
|------|---------|------|
| `Code` | code | 代码块（lang, value） |
| `InlineMath` | inlineMath | 行内数学 |
| `Math` | math | 块级数学 |
| `MathGroup` | mathGroup | 数学公式组 |

### 容器与指令

| 类型 | type 值 | 说明 |
|------|---------|------|
| `Container` | container | 容器（kind: figure/table/quote/code） |
| `Caption` | caption | 标题/说明 |
| `Legend` | legend | 图例 |
| `Directive` | mystDirective | 指令（解析中节点，最终会被提升） |
| `Role` | mystRole | 角色（解析中节点，最终会被提升） |
| `Admonition` | admonition | 提示块（kind: note/warning/error 等） |
| `AdmonitionTitle` | admonitionTitle | 提示块标题 |

### 引用与脚注

| 类型 | type 值 | 说明 |
|------|---------|------|
| `FootnoteDefinition` | footnoteDefinition | 脚注定义 |
| `Cite` | cite | 引用（kind: narrative/parenthetical） |
| `CiteGroup` | citeGroup | 引用组 |

### MyST 扩展节点（来自 ext.ts）

| 类型 | type 值 | 扩展字段 |
|------|---------|---------|
| `Block` | block | kind?, visibility? |
| `BlockBreak` | blockBreak | meta? |
| `Comment` | comment | value |
| `Target` | mystTarget | label |
| `Aside` | aside | kind?: sidebar/margin/topic |
| `TabSet` | tabSet | — |
| `TabItem` | tabItem | title, sync?, selected? |
| `Iframe` | iframe | src, width?, align?, class?, title? |
| `Include` | include | file, literal?, filter?, lang?, showLineNumbers? |
| `Embed` | embed | source?, remove-input?, remove-output? |
| `Raw` | raw | lang?, tex?, typst?, value? |
| `Output` | output | jupyter_data |
| `Outputs` | outputs | visibility?, scroll?, id? |
| `AnyWidget` | anywidget | esm, id, model, css?, class? |
| `InlineExpression` | inlineExpression | value, identifier?, result? |
| `IndexEntry` | —（非 AST 节点） | entry, subEntry?, emphasis? |
| `SiUnit` | si | number?, unit?, units?, alt?, value |
| `AlgorithmLine` | algorithmLine | indent?, enumerator? |
| `CaptionNumber` | captionNumber | kind, label, identifier, html_id, enumerator |
| `Dependency` | —（非 AST 节点） | url?, slug?, kind?, title?, label? |
| `CodeBlock` | block(kind=notebook-code) | data?, children: Code[] |

### 类型扩展字段

- `Target` mixin：label?, identifier?, html_id?, indexEntries?
- `Heading` 扩展：implicit?: true
- `Image` 扩展：urlSource?, urlOptimized?, height?, placeholder?
- `Link` 扩展：urlSource?, dataUrl?, internal?, static?, protocol?, error?, class?
- `CrossReference` 扩展：urlSource?, remote?, url?, dataUrl?, remoteBaseUrl?, html_id?, class?
- `Math` 扩展：kind?: 'subequation', tight?, typst?
- `InlineMath` 扩展：typst?
- `Admonition` 扩展：icon?, open?
- `Code` 扩展：executable?, filename?, visibility?
- `ListItem` 扩展：checked?
- `Container` 扩展：kind, source?, subcontainer?, noSubcontainers?, parentEnumerator?
- `TableCell` 扩展：colspan?, rowspan?, width?

### 枚举

| 枚举 | 值 |
|------|-----|
| `SourceFileKind` | Article = 'Article', Notebook = 'Notebook', Part = 'Part' |
| `CiteKind` | 'narrative' \| 'parenthetical' |
| `InlineCite` (citation-js-utils) | 'p' \| 't' |

### 搜索相关类型

| 类型 | 说明 |
|------|------|
| `MystSearchIndex` | MyST 搜索索引 |
| `SearchRecord` | 搜索记录 |
| `SearchRecordBase` | 搜索记录基类 |
| `HeadingRecord` | 标题记录 |
| `ContentRecord` | 内容记录 |
| `DocumentHierarchy` | 文档层级结构 |

## myst-spec-ext 兼容层

myst-spec-ext 包将 myst-spec 的所有扩展类型重新导出并标记为 @deprecated，共 38 个类型别名。SourceFileKind 枚举在 myst-spec-ext 中重复声明（esbuild/bun 兼容性）。新代码应直接从 myst-spec 导入。
