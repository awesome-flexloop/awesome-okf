---
type: concept
title: "HTML 导出"
description: "myst-to-html 将 MDAST 转换为 HTML 的完整管线：transform 预处理、mystToHast 转换、rehype 格式化和字符串化"
tags: [myst-exporters, html, hast, rehype, myst-to-html]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "myst-to-html/src/renderMdast.ts"
    facts: [F-036]
  - path: "myst-to-html/src/state.ts"
    facts: [F-037]
  - path: "myst-to-html/src/format.ts"
    facts: [F-001]
  - path: "myst-to-html/src/index.ts"
    facts: [F-001]
---

# HTML 导出

HTML 导出由 `myst-to-html` 包提供。与其他格式不同，HTML 导出复用了 unified 生态中的 [hast](https://github.com/syntax-tree/hast)（HTML Abstract Syntax Tree）和 rehype 插件链，而非手写 Serializer。

## 导出管线

`mystToHtml` 函数是 HTML 导出的统一入口，构建了一条 unified 管道：

```
MDAST (MyST 文档 AST)
  │
  ▼
transform (state)    ── 编号分配、引用解析等预处理
  │
  ▼
mystToHast (opts)    ── MDAST 节点 → HAST 节点映射
  │
  ▼
formatHtml (opt)     ── 可选的 HTML 格式化（rehype-format）
  │
  ▼
rehypeStringify      ── HAST → HTML 字符串
  │
  ▼
HTML 字符串（trimmed）
```

函数签名：

```typescript
function mystToHtml(
  tree: GenericParent,
  opts?: {
    formatHtml?: boolean;
    hast?: {
      clobberPrefix?: 'm-';
      allowDangerousHtml?: boolean;
      handlers?: Handlers;
    };
    stringifyHtml?: {
      closeSelfClosing?: boolean;
      allowDangerousHtml?: boolean;
    };
  }
): string;
```

## State 类：编号与引用解析

HTML 导出的 `State` 类（myst-to-html/src/state.ts）负责在 MDAST 层面做编号分配和交叉引用解析，这是 HTML 生成前的关键预处理。

### 编号目标管理

State 维护 `targets: Record<string, Target>` 映射和 `targetCounts: TargetCounts` 计数器。可编号的目标类型：

```typescript
enum TargetKind {
  heading = 'heading',
  math = 'math',
  figure = 'figure',
  table = 'table',
  code = 'code',
}
```

`addTarget(node)` 方法为 `enumerated !== false` 的节点分配编号：
- **标题编号**：层级式，如 `1.2.3`（由 `incrementHeadingCounts` 和 `formatHeadingEnumerator` 实现）
- **其他类型**：简单递增计数器（figure=1,2,3...；math=1,2,3...）

`enumerateTargets(state, tree, opts)` 函数遍历 tree，为 container/math/heading 调用 `addTarget`。

### 引用解析

`resolveReferences(state, tree)` 处理两种引用：
1. 将 URL 链接（如 `[text](#heading-id)`）转为 `crossReference` 节点
2. 解析 `crossReference` 节点的内容，根据 ref 类型和 target 类型填充文本：

| ref 类型 | target 类型 | 行为 |
|---------|-----------|------|
| eq | math | 填充 `(编号)`，如 `(1)` |
| ref | heading | 复制 target 节点的 children 作为链接文本 |
| ref | figure/table | 取 caption > paragraph 作为链接文本 |
| numref | figure/table | 填充 `Figure %s` 或 `Table %s`，%s 替换为编号 |

### 引用解析示例

```markdown
# Introduction <intro>

See [](#intro) for more.
```

经过 `resolveReferences` 后，链接节点变为 crossReference，其 children 被填充为 `Introduction` 文本，渲染为 `<a href="#intro">Introduction</a>`。

## mystToHast：MDAST→HAST 映射

`mystToHast` 是一个 unified plugin，定义了 MDAST 节点类型到 HAST 节点的映射。它从 `./schema.js` 导出，核心是 HAST handler 表，每个 MDAST 节点类型对应一个生成 HAST 元素的函数。

HAST 元素结构：
```typescript
{
  type: 'element',
  tagName: 'div',  // HTML 标签名
  properties: { className: ['admonition'], id: '...' },
  children: [...]  // HAST 子节点
}
```

## formatHtml：可选格式化

`formatHtml` 是 rehype-format 的条件包装：
- 传入 `true` 时启用 rehype-format 对 HTML 进行缩进格式化
- 传入 `false` 或不传时跳过（性能更好，输出紧凑）
- 传入配置对象时透传给 rehype-format

```typescript
export const formatHtml: Plugin<[boolean?], string, GenericParent> = function (opt) {
  if (!opt) return () => undefined;
  return rehypeFormat(typeof opt === 'boolean' ? {} : opt);
};
```

## 数学公式渲染

`addMathRenderers` 和 `renderMath`（从 `./renderer.js` 导出）提供数学公式的 HTML 渲染能力，通常基于 KaTeX。数学节点在转换为 HAST 时会被渲染为带有 MathML/HTML 输出的元素。

## 使用方式

### 直接调用 mystToHtml

```typescript
import { unified } from 'unified';
import mystParse from 'myst-parser';
import { mystToHtml } from 'myst-to-html';

const pipe = unified().use(mystParse).use(() => (tree) => {
  // 可选：在导出前做 transforms
  return tree;
});

const tree = pipe.runSync(pipe.parse('# Hello *world*'));
const html = mystToHtml(tree, { formatHtml: true });
// <h1>Hello <em>world</em></h1>
```

### 通过 myst-cli 使用

通过 `myst build --html` 或 `jupyter-book build --html` 调用时，myst-cli 会处理项目加载、多文件导航、主题应用等完整流程。myst-to-html 只负责单文件内容转换。

## 相关概念

- [00-exporter-architecture](/concepts/00-exporter-architecture.md)：统一导出架构
- [05-jats-export](/concepts/05-jats-export.md)：JATS XML 导出（对比不同输出格式）
- [01-multi-format-export](/examples/01-multi-format-export.md)：多格式到处示例
