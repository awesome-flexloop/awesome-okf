---
type: reference
title: "myst-exporters 导出器入口索引"
description: "各格式导出器包入口（index.ts）导出符号清单与包结构"
tags: [myst-exporters, reference, entrypoints]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "myst-to-html/src/index.ts"
    facts: [F-001]
  - path: "myst-to-tex/src/index.ts"
    facts: [F-002, F-003, F-006]
  - path: "myst-to-docx/src/index.ts"
    facts: [F-011]
  - path: "myst-to-jats/src/index.ts"
    facts: [F-013, F-016]
  - path: "myst-to-md/src/index.ts"
    facts: [F-019]
  - path: "myst-to-typst/src/index.ts"
    facts: [F-021]
---

# myst-exporters 导出器入口索引

本文档登记各格式导出器包的入口文件（index.ts）导出的公共 API，供概念文档交叉引用。

## 源码根目录

所有导出器包位于 `external/libs/ai/jupyter-book/mystmd/packages/`。

## 各包导出清单

### myst-to-html

- **路径**：`myst-to-html/src/index.ts`
- **导出符号**：

| 符号 | 来源 | 类型 | 说明 |
|------|------|------|------|
| `formatHtml` | `./format.js` | Plugin | 条件包装 rehype-format，true 时启用 HTML 格式化 |
| `addMathRenderers` | `./renderer.js` | Function | 添加数学公式渲染器 |
| `renderMath` | `./renderer.js` | Function | 渲染数学公式 |
| `mystToHast` | `./schema.js` | Plugin | MDAST→HAST 转换插件 |
| `State` | `./state.js` | Class | HTML 导出状态管理（编号/引用解析） |
| `transform` | `./transforms.js` | Plugin | HTML 导出前的 MDAST 转换 |
| `mystToHtml` | `./renderMdast.js` | Function | **统一入口函数**，MDAST→HTML 字符串 |

### myst-to-tex

- **路径**：`myst-to-tex/src/index.ts`
- **导出符号**：

| 符号 | 来源 | 类型 | 说明 |
|------|------|------|------|
| `default` (plugin) | 本文件 | Plugin | unified 编译器插件 |
| `*` (types) | `./types.js` | Types | Handler, ITexSerializer, LatexResult, Options 等 |
| `*` (preamble) | `./preamble.js` | Functions | generatePreamble, mergePreambles |

- **LatexResult 结构**：`{ value: string; imports: string[]; preamble: PreambleData; commands: Record<string, string> }`

### myst-to-docx

- **路径**：`myst-to-docx/src/index.ts`
- **导出符号**：

| 符号 | 来源 | 类型 | 说明 |
|------|------|------|------|
| `DocxSerializer` | `./serializer.js` | Class | DOCX 序列化器 |
| `defaultHandlers` | `./schema.js` | Object | 默认节点处理函数映射表 |
| `mystToDocx` | `./plugin.js` | Plugin | unified 编译器插件（命名导出为 plugin） |
| `writeDocx` | `./utils.js` | Function | 写入 DOCX 文件 |
| `createDocFromState` | `./utils.js` | Function | 从 Serializer 状态创建 docx Document |
| `fetchImagesAsBuffers` | `./utils.js` | Function | 将图片获取为 Buffer |
| `IDocxSerializer` 等 | `./types.js` | Types | 类型定义 |

### myst-to-jats

- **路径**：`myst-to-jats/src/index.ts`
- **导出符号**：

| 符号 | 来源 | 类型 | 说明 |
|------|------|------|------|
| `default` (plugin) | 本文件 | Plugin | unified 编译器插件 |
| `JatsSerializer` | 本文件 | Class | JATS XML 序列化器（栈式构建） |
| `JatsDocument` | 本文件 | Class | JATS 文档构建器（article/front/body/back） |
| `writeJats` | 本文件 | Function | 高层 JATS 写入函数 |

### myst-to-md

- **路径**：`myst-to-md/src/index.ts`
- **导出符号**：

| 符号 | 来源 | 类型 | 说明 |
|------|------|------|------|
| `default` (plugin) | 本文件 | Plugin | unified 编译器插件 |
| `writeMd` | 本文件 | Function | MDAST→Markdown 字符串（含 frontmatter） |

### myst-to-typst

- **路径**：`myst-to-typst/src/index.ts`
- **导出符号**：

| 符号 | 来源 | 类型 | 说明 |
|------|------|------|------|
| `default` (plugin) | 本文件 | Plugin | unified 编译器插件 |
| `TypstResult` | `./types.js` | Type | `{ macros, commands, value }` |

## 统一插件模式

所有导出器包遵循统一的 unified Plugin 模式：

```typescript
const plugin: Plugin<[Options?], Root, VFile> = function (opts) {
  this.Compiler = (node, file) => {
    // 创建 Serializer，渲染 AST
    // 将结果写入 file.result
    return file;
  };
  return (node: Root) => {
    // 可选预处理
    return node;
  };
};
```

## 相关概念

- [00-exporter-architecture](/concepts/00-exporter-architecture.md)：统一导出接口架构
- [01-html-export](/concepts/01-html-export.md)：HTML 导出详解
- [02-latex-export](/concepts/02-latex-export.md)：LaTeX 导出详解
- [08-jtex-template-engine](/concepts/08-jtex-template-engine.md)：jtex 模板引擎
