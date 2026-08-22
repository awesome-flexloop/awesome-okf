---
type: concept
title: "统一导出架构"
description: "理解 myst-exporters 统一的 Serializer + Handler 表驱动架构、unified Plugin 模式和各格式导出器的共性设计"
tags: [myst-exporters, architecture, serializer, unified-plugin, handler]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "myst-to-tex/src/index.ts"
    facts: [F-002, F-003, F-004, F-005]
  - path: "myst-to-jats/src/index.ts"
    facts: [F-014, F-015]
  - path: "myst-to-typst/src/index.ts"
    facts: [F-021, F-022]
  - path: "myst-to-docx/src/plugin.ts"
    facts: [F-012]
  - path: "myst-to-html/src/renderMdast.ts"
    facts: [F-036]
  - path: "myst-to-md/src/index.ts"
    facts: [F-019, F-020]
  - path: "myst-cli/src/build/utils/localArticleExport.ts"
    facts: [F-039, F-040]
---

# 统一导出架构

myst-exporters 包含 6 种格式的导出器（HTML、LaTeX、DOCX、JATS XML、Markdown、Typst）和 2 种格式的导入转换器（JATS→MyST、LaTeX→MyST）。所有导出器遵循统一的架构模式，使新增格式和扩展现有格式变得可预测。

## 核心模式：unified Plugin + Serializer

每个导出器包都实现为一个 [unified](https://unifiedjs.com) 生态的 `Plugin`。unified 是文本处理的 AST 框架，MyST 文档经过 myst-parser 解析为 MDAST（Markdown Abstract Syntax Tree），导出器的 Compiler 阶段将 MDAST 转换为目标格式。

```typescript
// 统一 Plugin 模式（所有导出器都遵循）
const plugin: Plugin<[Options?], Root, VFile> = function (opts) {
  this.Compiler = (node, file) => {
    // 1. 创建 Serializer 实例
    const state = new XxxSerializer(file, node, opts);
    // 2. Serializer 构造函数中已经完成渲染（调用 renderChildren）
    // 3. 将结果写入 file.result
    file.result = state.getResult();
    return file;
  };
  return (node: Root) => {
    // 可选的预处理（大部分导出器直接透传）
    return node;
  };
};
```

关键特征：
- **Compiler 是核心**：转换逻辑集中在 `this.Compiler` 中
- **预处理透传**：大部分导出器的 `return (node) => node` 不做预处理，转换前的 MDAST 变换在 myst-transforms 层完成
- **VFile 承载结果**：转换结果写入 `file.result`，不同格式类型不同（string、Buffer/Blob、结构化对象）

## Serializer 状态类

每个导出器定义一个 Serializer 类，管理渲染过程中的状态：

```
┌─────────────────────────────────────────────────┐
│                  Serializer                     │
├─────────────────────────────────────────────────┤
│  file: VFile            # 输出文件，承载 result  │
│  data: StateData        # 格式特定的状态数据     │
│  options: Options       # 配置选项              │
│  handlers: Record<string, Handler>  # 节点处理表 │
├─────────────────────────────────────────────────┤
│  write(value)           # 追加输出              │
│  text(value, escape?)   # 写入转义后的文本       │
│  renderChildren(node)   # 遍历子节点→查表分发    │
│  renderEnvironment()    # 渲染块级环境          │
│  renderInlineEnvironment() # 渲染内联命令       │
│  closeBlock()           # 块级结束（换行等）     │
└─────────────────────────────────────────────────┘
```

不同格式的 Serializer 有各自的特色：
- **TexSerializer**：收集 `\usepackage` 到 Set，管理 footnotes/glossary/acronyms 字典
- **JatsSerializer**：使用 Element 栈（openNode/closeNode）构建 XML 树
- **TypstSerializer**：收集 macros 到 Set，处理 headingIdentifiers 避免重复
- **DocxSerializer**：直接构建 docx 库的 Document 对象
- **HTML 路径特殊**：不手写 Serializer，复用 mdast→hast→rehype→stringify 管道

## Handler 表驱动分发

Serializer 的核心是 `handlers: Record<string, Handler>`——一个节点类型到处理函数的映射表。`renderChildren` 遍历 AST 子节点，按 `child.type` 查找 handler 并调用：

```typescript
renderChildren(node: Parent, inline = false, delim = '') {
  node.children?.forEach((child, index) => {
    const handler = this.handlers[child.type];
    if (handler) {
      handler(child, this, node);  // 传递 node/state/parent
    } else {
      fileError(this.file, `Unhandled node type: "${child.type}"`);
    }
  });
}
```

以 LaTeX 导出为例，heading 节点的 handler：

```typescript
heading(node, state) {
  const { depth, label, enumerated } = node;
  const star = enumerated !== false || state.options.beamer ? '' : '*';
  if (depth === 1) state.write(`\\section${star}{`);
  if (depth === 2) state.write(`\\subsection${star}{`);
  // ... 更多层级
  state.renderChildren(node, true);
  state.write('}');
  if (enumerated !== false && label) state.write(`\\label{${label}}`);
  state.closeBlock(node);
}
```

Handler 通过 opts.handlers 可以覆盖或扩展默认 handlers，这是插件化扩展点。

## 输出结果类型

各导出器写入 `file.result` 的类型不同：

| 导出器 | file.result 类型 | 说明 |
|--------|-----------------|------|
| myst-to-html | `string` | HTML 字符串 |
| myst-to-tex | `LatexResult` | `{ value, imports, preamble, commands }` 结构化对象 |
| myst-to-typst | `TypstResult` | `{ value, macros, commands }` 结构化对象 |
| myst-to-docx | `Buffer` (Node) / `Blob` (浏览器) | 二进制 DOCX |
| myst-to-jats | `string` | XML 字符串 |
| myst-to-md | `string` | Markdown 字符串（含 YAML frontmatter） |

注意 LaTeX 和 Typst 输出结构化对象（包含 imports/macros/commands），而非纯字符串。这是因为包管理、数学宏、导言区等信息需要在 jtex 模板渲染阶段与模板整合。

## 构建编排层

myst-exporters 包本身只做单文件 MDAST→目标格式转换。项目级的多文件构建、PDF 编译、模板整合等编排逻辑在 [myst-cli](/concepts/03-myst-cli-relationship.md) 的 build 层实现。

`localArticleExport` 函数（myst-cli/src/build/utils/localArticleExport.ts）根据 export format 分发到具体的 `runXxxExport` 函数：
- runTexExport：调用 myst-to-tex 得到 LatexResult → jtex renderTemplate → 写 .tex 文件
- runWordExport：调用 myst-to-docx 得到 Buffer → 写 .docx 文件
- runJatsExport：调用 myst-to-jats 得到 XML 字符串 → 写 .xml 文件
- PDF 路径：runTexExport → latexmk 编译 .tex → .pdf

## HTML 导出的特殊性

HTML 导出不走手写 Serializer 模式，而是复用 unified 生态：

```typescript
// myst-to-html/src/renderMdast.ts
export function mystToHtml(tree, opts?) {
  const state = new State();
  const pipe = unified()
    .use(transform, state)     // MDAST 预处理（编号/引用解析）
    .use(mystToHast, opts?.hast)  // MDAST→HAST
    .use(formatHtml, opts?.formatHtml)  // 可选格式化
    .use(rehypeStringify, opts?.stringifyHtml);  // HAST→HTML 字符串
  const result = pipe.runSync(tree);
  return pipe.stringify(result).trim();
}
```

`mystToHast` 定义了 MDAST 节点到 HAST（HTML AST）节点的映射，后续使用标准 rehype 生态处理。

## 扩展自定义导出器

要新增一种输出格式，遵循以下步骤：

1. 创建新包 `myst-to-xxx`，实现 `Plugin<[Options?], Root, VFile>`
2. 定义 `XxxSerializer` 类，包含 handlers 映射表和核心渲染方法
3. 定义 `Handler` 类型和 `Options` 类型
4. 在 myst-cli 的 `localArticleExport` 中添加对应的 `runXxxExport` 和 format 分发
5. 如需模板支持，在 jtex 中添加对应 kind 的 imports 渲染

## 相关概念

- [01-html-export](/concepts/01-html-export.md)：HTML 导出管线
- [02-latex-export](/concepts/02-latex-export.md)：LaTeX 序列化器详解
- [03-pdf-export](/concepts/03-pdf-export.md)：PDF 生成流程（TeX→latexmk）
- [04-docx-export](/concepts/04-docx-export.md)：DOCX 导出
- [05-jats-export](/concepts/05-jats-export.md)：JATS XML 导出
- [06-markdown-export](/concepts/06-markdown-export.md)：Markdown 回环导出
- [07-typst-export](/concepts/07-typst-export.md)：Typst 导出
- [08-jtex-template-engine](/concepts/08-jtex-template-engine.md)：jtex 模板引擎
- [09-import-converters](/concepts/09-import-converters.md)：导入转换器
- [01-multi-format-export](/examples/01-multi-format-export.md)：多格式到处示例
