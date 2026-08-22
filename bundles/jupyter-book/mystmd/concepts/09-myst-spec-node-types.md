---
type: Concept
title: MDAST 节点类型规范（myst-spec）
description: myst-spec 包定义了 MyST Markdown 的 50+ 种 AST 节点类型，是 MDAST 的 MyST 超集规范，myst-spec-ext 提供向后兼容的 deprecated 类型别名。
tags: [mystmd, myst-spec, mdast, node-types, ast]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "/references/myst-spec-source.md"
    facts: [F-095, F-096, F-097, F-098, F-099, F-100, F-101, F-102, F-103, F-104]
---

## myst-spec 概述

myst-spec 是 MyST Markdown 的 AST 节点类型规范包，定义了 MyST 扩展的所有 MDAST 节点类型和属性。它是 TypeScript 类型定义包，不包含运行时代码。

## 节点类型分类

### 1. 基础 Markdown 节点（CommonMark 兼容）

| 节点 | type 值 | 核心属性 | 说明 |
|------|---------|---------|------|
| Root | `root` | children | AST 根节点 |
| Paragraph | `paragraph` | children | 段落 |
| Heading | `heading` | depth(1-6), implicit? | 标题 |
| Text | `text` | value | 纯文本 |
| Emphasis | `emphasis` | children | 斜体 |
| Strong | `strong` | children | 粗体 |
| InlineCode | `inlineCode` | value | 行内代码 |
| Delete | `delete` | children | 删除线 |
| Link | `link` | url, title | 链接 |
| Image | `image` | url, alt, title | 图片 |
| List | `list` | ordered, spread, start | 列表 |
| ListItem | `listItem` | checked? | 列表项/任务项 |
| Blockquote | `blockquote` | children | 引用块 |
| Code | `code` | lang, value | 代码块 |
| ThematicBreak | `thematicBreak` | — | 水平分隔线 |
| Break | `break` | — | 硬换行 |
| HTML | `html` | value | 原始 HTML |
| Table | `table` | children | 表格 |
| TableRow | `tableRow` | children | 表格行 |
| TableCell | `tableCell` | header, align, colspan?, rowspan? | 单元格 |

### 2. 定义列表节点

| 节点 | type 值 | 说明 |
|------|---------|------|
| DefinitionList | `definitionList` | 定义列表容器 |
| DefinitionTerm | `definitionTerm` | 术语 |
| DefinitionDescription | `definitionDescription` | 描述 |

### 3. MyST 基础扩展节点

| 节点 | type 值 | 核心属性 | 说明 |
|------|---------|---------|------|
| InlineMath | `inlineMath` | value, typst? | 行内数学公式 |
| Math | `math` | value, kind?, tight?, typst? | 块级数学公式 |
| MathGroup | `mathGroup` | children, enumerator? | 公式组（subequations） |
| Container | `container` | kind, label?, identifier?, html_id? | 通用容器（figure/table/quote/code） |
| Caption | `caption` | children | 说明/标题（在 container 内） |
| Legend | `legend` | children | 图例 |
| Admonition | `admonition` | kind, icon?, open? | 提示块 |
| AdmonitionTitle | `admonitionTitle` | children | 提示块标题 |
| CrossReference | `crossReference` | identifier, label?, url? | 交叉引用 |
| Cite | `cite` | kind(p/parenthetical/t/narrative), label | 单个引用 |
| CiteGroup | `citeGroup` | children, kind? | 引用组 |
| FootnoteReference | `footnoteReference` | label, identifier? | 脚注引用 |
| FootnoteDefinition | `footnoteDefinition` | label, identifier?, children | 脚注定义 |
| Subscript | `subscript` | children | 下标 |
| Superscript | `superscript` | children | 上标 |
| Underline | `underline` | children | 下划线 |
| Smallcaps | `smallcaps` | children | 小体大写 |

### 4. MyST 解析中节点（最终被提升/移除）

| 节点 | type 值 | 说明 |
|------|---------|------|
| Directive | `mystDirective` | 原始指令节点（processed=true 后提升） |
| Role | `mystRole` | 原始角色节点（processed=true 后提升） |
| Target | `mystTarget` | 目标标记（label，被 mystTargets 处理后移除） |

### 5. MyST 高级扩展节点

| 节点 | type 值 | 核心属性 | 说明 |
|------|---------|---------|------|
| Block | `block` | kind?, visibility?, meta? | 通用块（含 Notebook 代码块） |
| BlockBreak | `blockBreak` | meta? | 块断点（+++） |
| Comment | `comment` | value | 注释 |
| Aside | `aside` | kind(sidebar/margin/topic) | 旁注/侧边栏 |
| TabSet | `tabSet` | children | 选项卡组 |
| TabItem | `tabItem` | title, sync?, selected? | 选项卡项 |
| Iframe | `iframe` | src, width?, align?, class? | 嵌入式框架 |
| Include | `include` | file, literal?, filter?, lang? | 文件包含 |
| Embed | `embed` | source?, remove-input?, remove-output? | 节点嵌入 |
| Raw | `raw` | lang?, tex?, typst?, value | 原始内容（格式特定） |
| Output | `output` | jupyter_data | Notebook 输出单元 |
| Outputs | `outputs` | visibility?, scroll?, id? | 输出组 |
| AnyWidget | `anywidget` | esm, id, model, css?, class? | Jupyter anywidget |
| InlineExpression | `inlineExpression` | value, identifier?, result? | 内联表达式 |
| SiUnit | `si` | number?, unit?, units?, alt?, value | SI 单位 |
| AlgorithmLine | `algorithmLine` | indent?, enumerator? | 算法行 |
| CaptionNumber | `captionNumber` | kind, label, identifier, html_id, enumerator | 编号标签 |

### 6. 辅助类型（非 AST 节点）

| 类型 | 说明 |
|------|------|
| IndexEntry | 索引条目（entry, subEntry?, emphasis?） |
| Dependency | 依赖项（url?, slug?, kind?, title?, label?） |

### 7. 搜索相关类型

| 类型 | 说明 |
|------|------|
| MystSearchIndex | 搜索索引根 |
| SearchRecord | 搜索记录 |
| HeadingRecord | 标题搜索记录 |
| ContentRecord | 内容搜索记录 |
| DocumentHierarchy | 文档层级结构 |

## 枚举类型

### SourceFileKind

```ts
enum SourceFileKind {
  Article = 'Article',   // Markdown 文章
  Notebook = 'Notebook', // Jupyter Notebook
  Part = 'Part',         // 文档部分
}
```

### CiteKind

```ts
type CiteKind = 'narrative' | 'parenthetical';
// narrative: Author (2023) — 叙述式
// parenthetical: (Author, 2023) — 括号式
```

## 节点扩展字段（Mixin）

多个节点类型共享以下扩展字段：

### Target 扩展（可被引用的节点）
```ts
{
  identifier?: string;   // 唯一 ID
  label?: string;        // 人类可读标签
  html_id?: string;      // HTML 锚点 ID
  indexEntries?: IndexEntry[];
  enumerator?: string;   // 编号（如 "1", "1.1", "(2)"）
}
```

适用于：Heading、Container、Math、Code、Block(kind=notebook-code)、FootnoteDefinition、CrossReference 等。

### 容器扩展
```ts
{
  kind: 'figure' | 'table' | 'quote' | 'code' | string;
  source?: string;       // 来源说明
  subcontainer?: boolean;
  noSubcontainers?: boolean;
  parentEnumerator?: string;
}
```

### 数学扩展
```ts
// Math
{
  kind?: 'subequation';
  tight?: boolean;
  typst?: boolean;       // 是否 Typst 格式
}

// InlineMath
{
  typst?: boolean;
}
```

### 链接/引用扩展
```ts
// Link
{
  urlSource?: string;    // 原始 URL（解析前）
  dataUrl?: string;
  internal?: boolean;    // 是否内部链接
  static?: boolean;      // 是否静态资源
  protocol?: string;
  error?: boolean;
  class?: string;
}

// Image
{
  urlSource?: string;
  urlOptimized?: string;
  height?: string;
  placeholder?: string;
}

// CrossReference
{
  urlSource?: string;
  remote?: boolean;      // 是否跨项目
  url?: string;
  dataUrl?: string;
  remoteBaseUrl?: string;
  html_id?: string;
  class?: string;
}
```

### Admonition 扩展
```ts
{
  icon?: boolean | string;  // 是否显示图标或自定义图标
  open?: boolean;           // 是否展开（dropdown）
}
```

### 代码扩展
```ts
// Code
{
  executable?: boolean;     // 是否可执行
  filename?: string;        // 文件名标签
  visibility?: 'show' | 'hide' | 'remove';
}
```

### 列表项扩展
```ts
// ListItem
{
  checked?: boolean | null; // null=普通项, true=已完成, false=未完成
}
```

## myst-spec-ext 兼容层

myst-spec-ext 是一个薄兼容层，将 myst-spec 的所有扩展类型重新导出为 @deprecated 类型别名（共 38 个），并重复声明 SourceFileKind 枚举（esbuild/bun 兼容性）。

**迁移路径**：新代码应直接从 `myst-spec` 导入，不再使用 myst-spec-ext。

```ts
// 旧方式（deprecated）
import type { GenericNode } from 'myst-spec-ext';

// 新方式
import type { GenericNode } from 'myst-spec';
```

## CSL（Citation Style Language）类型

myst-spec 还导出 CSL-JSON 相关类型，用于参考文献数据：
- CSL 条目类型（type/id/author/issued/title/DOI/URL 等 50+ 字段）
- CSLDate、CSLPerson、CSLNameVariable 等辅助类型

## 相关概念

- [MyST 解析器](/concepts/02-myst-parser.md)
- [公共类型系统](/concepts/04-myst-common-types.md)
- [指令与角色系统](/concepts/06-directives-and-roles.md)
