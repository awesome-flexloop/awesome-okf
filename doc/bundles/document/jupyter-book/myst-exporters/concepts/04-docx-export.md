---
type: concept
title: "DOCX 导出"
description: "myst-to-docx 使用 docx 库直接构建 Office Open XML 文档对象，支持 Node.js Buffer 和浏览器 Blob 双环境输出"
tags: [myst-exporters, docx, word, office, myst-to-docx]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "myst-to-docx/src/plugin.ts"
    facts: [F-012, F-013]
  - path: "myst-to-docx/src/index.ts"
    facts: [F-011]
  - path: "myst-to-docx/src/schema.ts"
    facts: []
  - path: "myst-to-docx/src/types.ts"
    facts: []
---

# DOCX 导出

DOCX（Word 文档）导出由 `myst-to-docx` 包提供。与其他文本格式导出器不同，DOCX 导出使用 [docx](https://docx.js.org/) 库直接构建 Office Open XML 文档对象，然后打包为二进制 .docx 文件。

## 核心 API

### mystToDocxPlugin

```typescript
const mystToDocxPlugin: Plugin<[IDocxSerializerOptions?], Root, VFile> = function (opts) {
  this.Compiler = (node, file) => {
    const docx = serializeDocx(node as unknown as Root, opts, file);
    file.result = Blob;  // 浏览器环境
    return file;
  };
  return (node: Root) => node;
};
```

### createDocxFile（Node.js 环境）

```typescript
async function createDocxFile(
  tree: Root,
  opts?: IDocxSerializerOptions & { useFieldsForCrossReferences?: boolean },
  file?: VFile,
): Promise<Buffer>
```

- Node.js 环境下将 Document 对象通过 `Packer.toBuffer(doc, { images })` 打包为 Buffer
- 返回 Buffer 可直接写入 .docx 文件
- `opts.useFieldsForCrossReferences`：是否使用 Word 域代码处理交叉引用

### serializeDocx（统一入口）

```typescript
function serializeDocx(
  tree: Root,
  opts?: IDocxSerializerOptions,
  file?: VFile,
): Document
```

- 直接返回 docx 库的 Document 对象
- 可用于浏览器环境（通过 Packer.toBlob）或 Node.js 环境（通过 Packer.toBuffer）

## DOCX Document 结构

docx 库的 Document 对象代表整个 Word 文档，包含：

```
Document {
  creator: "MyST",
  title: "...",
  description: "...",
  keywords: "...",
  features: { updateFields: true },
  styles: [/* 自定义样式 */],
  numbering: { config: [/* 列表编号配置 */] },
  comments: { children: [/* 评论 */] },
  footnotes: { "1": [/* 脚注内容 */], "2": [...] },
  sections: [{
    properties: { page: { size: {...}, margin: {...} } },
    children: [Paragraph, Table, ...]
  }]
}
```

## 节点到 DOCX 的映射

myst-to-docx/src/schema.ts 定义了 MDAST 节点到 docx 元素的映射。与其他导出器的文本拼接方式不同，DOCX 元素是强类型的 JavaScript 对象：

| MyST 节点 | docx 元素 | 说明 |
|----------|----------|------|
| heading(1-6) | HeadingLevel.HEADING_1..6 | Word 内置标题样式 |
| paragraph | Paragraph | 普通段落 |
| text/strong/em | TextRun + bold/italic | 文本运行（带格式属性） |
| list | Numbering/ListLevel | 有序/无序列表编号配置 |
| table | Table + TableRow + TableCell | Word 表格 |
| code | Paragraph + monospaced TextRun | 等宽字体段落，可选背景色 |
| image | ImageRun | 嵌入二进制图片数据 |
| link | ExternalLink/InternalHyperlink | 超链接 |
| math | OMML（Office MathML）| Word 原生公式 |
| container/figure | Paragraph + ImageRun + Caption | 图文容器 |
| crossReference | SimpleField/Bookmark | Word 域代码交叉引用 |

## Node.js 与浏览器双环境

myst-to-docx 通过运行时检测支持双环境：

- **Node.js 环境**（`process.release.name === 'node'`）：
  - 图片通过 `fs.readFile` 同步/异步读取本地文件
  - 最终输出 Buffer（通过 `Packer.toBuffer(doc)`）
  - 使用 `createDocxFile()` 直接得到 Buffer
- **浏览器环境**：
  - 图片通过 `fetch(url).then(r => r.arrayBuffer())` 加载
  - 最终输出 Blob（通过 `Packer.toBlob(doc)`）
  - 使用 `serializeDocx()` 得到 Document 对象，再手动打包

## 图片处理

DOCX 中的图片需要嵌入二进制数据：

1. 解析图片路径（本地文件路径或网络 URL）
2. Node.js：`fs.readFile` 读取图片 Buffer
3. 浏览器：`fetch` 获取 ArrayBuffer
4. 通过尺寸检测（JPEG/PNG 头解析或 sharp/jimp 库）获取 width/height
5. 转换为 `ImageRun({ data: buffer, transformation: { width, height } })`
6. 注册到 Document 的 images 映射中，Packer 自动嵌入

## 交叉引用与域代码

Word 的交叉引用使用域代码（Field Code）而非简单超链接：

- **书签定义**：`BookmarkStart(name, id)` + 内容 + `BookmarkEnd(name)`
- **引用**：`new SimpleField("REF bookmarkId \\h", "placeholder")`
- **页码引用**：`SimpleField("REF bookmarkId \\p \\h")`
- 设置 `features: { updateFields: true }` 后，Word 打开文档时会自动更新所有域编号

`useFieldsForCrossReferences=true` 选项启用域代码模式，关闭则使用静态文本链接。

## 样式定义

DOCX 导出在 Document.styles 中注册自定义样式：

- **标题样式**：映射到 Word 内置 Heading1-6 样式，支持字号和加粗
- **代码样式**：Courier New/monospace 字体，浅灰色背景
- **引用样式**：左边框缩进，斜体
- **caption 样式**：小字号，居中或左对齐
- **目录样式**：TOC 域代码配合 \o "1-3" 参数

## 使用方式

### 通过 myst-cli / Jupyter Book

```bash
myst build document.md --docx
# 或
jupyter-book build document.md --docx
# 输出 _build/exports/document.docx
```

### 直接调用（Node.js）

```typescript
import { unified } from 'unified';
import mystParse from 'myst-parser';
import { createDocxFile } from 'myst-to-docx';
import { writeFileSync } from 'fs';

const pipe = unified().use(mystParse);
const tree = pipe.runSync(pipe.parse('# Hello\n\nWorld.'));
const buffer = await createDocxFile(tree, { useFieldsForCrossReferences: true });
writeFileSync('output.docx', buffer);
```

## 相关概念

- [00-exporter-architecture](00-exporter-architecture.md)：统一导出架构
- [01-html-export](01-html-export.md)：HTML 导出（对比文本格式）
- [01-multi-format-export](../examples/01-multi-format-export.md)：多格式到处示例
