---
type: concept
title: "导入转换器"
description: "jats-to-myst 和 tex-to-myst 将 JATS XML 和 LaTeX 转换为 MyST MDAST 的栈式解析器架构，支持学术论文和 LaTeX 文档的导入"
tags: [myst-exporters, import, jats-to-myst, tex-to-myst, converter, parser]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "jats-to-myst/src/index.ts"
    facts: [F-032, F-033, F-034]
  - path: "tex-to-myst/src/index.ts"
    facts: [F-035]
---

# 导入转换器

myst-exporters 不仅包含导出器（MyST→目标格式），还包含两个导入转换器：
- **jats-to-myst**：JATS XML → MyST MDAST（用于导入学术论文）
- **tex-to-myst**：LaTeX → MyST MDAST（用于导入 LaTeX 文档）

它们的架构与导出器对称，但方向相反——将外部格式的 AST/解析树转换为 MDAST。

## jats-to-myst：JATS XML 导入

JATS 是学术出版的标准 XML 格式（见 [JATS XML 导出](/concepts/05-jats-export.md)）。jats-to-myst 可以将 JATS XML 论文导入为 MyST 文档，实现从期刊投稿系统/PMC/PubMed 到 MyST 的工作流。

### 核心 API

```typescript
// 高层入口（推荐使用）
function jatsToMystTransform(
  source: string | Jats,  // XML 字符串或已解析的 Jats 对象
  opts?: Options
): {
  tree: Root;           // MDAST 根节点
  jats: Jats;           // 解析后的 JATS 中间表示
  file: VFile;          // VFile 对象（含错误/警告）
  references: References; // 提取的参考文献数据
}

// unified 插件
const jatsToMystPlugin: Plugin<[Options?], string, Root>;

// JATS 解析器类
class JatsParser {
  stack: Element[];              // 节点栈（与 JatsSerializer 对称）
  handlers: Record<string, JatsHandler>;
  // 栈操作方法
  openNode(name, attrs?, isLeaf?);
  closeNode();
  pushNode(el?);
  text(text?);
  renderChildren(node);
  renderInline(node, name, attrs?);
  addLeaf(name, attrs?);
}
```

### JatsParser 栈式解析

JatsParser 使用与 JatsSerializer 对称的栈式 API，但方向相反：

- JatsSerializer：MDAST → 栈式构建 XML 元素树 → XML 字符串
- JatsParser：XML 元素树 → 栈式构建 MDAST → MDAST 树

处理流程：
1. 将 JATS XML 解析为 Jats 对象（使用 xml-js 或类似工具）
2. 遍历 Jats 元素树，按元素名查找 handler
3. Handler 调用 `openNode`/`pushNode`/`closeNode` 构建 MDAST 节点
4. 完成后从栈底得到完整 MDAST

### DEFAULT_HANDLERS：JATS 元素映射

DEFAULT_HANDLERS 映射表定义了 JATS XML 元素到 MyST MDAST 节点的转换：

| JATS 元素 | MDAST 节点 | 说明 |
|----------|-----------|------|
| `<article>` | root | 根元素，处理 front/body/back |
| `<sec>` | container + heading | 节（sec 的直接子 title 转为 heading）|
| `<title>`（sec 内）| heading | 标题，深度由嵌套层级决定 |
| `<p>` | paragraph | 段落 |
| `<bold>`/`<b>` | strong | 粗体 |
| `<italic>`/`<i>` | emphasis | 斜体 |
| `<underline>` | underline | 下划线 |
| `<list>` | list | 列表（list-type 决定有序/无序）|
| `<fig>` | container(figure) + image + caption | 图片 |
| `<table-wrap>` | container(table) + table + caption | 表格 |
| `<disp-formula>` | math(display) | 块级公式 |
| `<inline-formula>` | math(inline) | 行内公式 |
| `<xref>` | crossReference/cite | 交叉引用/引用 |
| `<ref-list>`/`<ref>` | 转换为 citations/参考文献 | 参考文献列表 |
| `<abstract>` | part(abstract) | 摘要 |
| `<fig-group>` | tabSet + tabItem | 图组→标签页（HTML 风格）|

### JATS ref-type 到 MyST kind 映射

`<xref>` 元素的 `ref-type` 属性决定引用类型：

| ref-type | MyST kind | 说明 |
|---------|----------|------|
| `sec` | `heading` | 引用章节 |
| `fig` | `figure` | 引用图片 |
| `table` | `table` | 引用表格 |
| `disp-formula` | `equation` | 引用公式 |
| `bibr` | `cite` | 参考文献引用 |
| `fn` | `footnote` | 脚注引用 |
| `aff` | 无（特殊处理）| 机构引用 |

### 平台特殊处理

jats-to-myst 对几个常见的 JATS 发布平台有特殊 URL/ID 处理：
- **eLife**：图片 URL 从 elife-cdn 转换
- **JOSS**（Journal of Open Source Software）：特殊的元数据结构
- **PLOS**：图片和补充材料 URL 模式
- **PMC**（PubMed Central）：PMC ID 解析和 URL 转换

### 参考文献数据提取

jats-to-myst 在解析过程中提取参考文献数据到 `references` 对象：
- `<mixed-citation>` 或 `<element-citation>` 的内容被解析为结构化数据
- DOI 从 `<pub-id pub-id-type="doi">` 提取
- 自动生成 HTML 预览片段（用于引用悬停预览）

### 使用方式

```typescript
import { jatsToMystTransform } from 'jats-to-myst';
import fs from 'fs';

const xml = fs.readFileSync('paper.xml', 'utf-8');
const { tree, references } = jatsToMystTransform(xml);
// tree 是 MDAST，可以传给 mystToHtml/mystToTex 等导出器
```

## tex-to-myst：LaTeX 导入

LaTeX 导入由 `tex-to-myst` 包提供，成熟度低于 jats-to-myst。

### 核心 API

```typescript
// 导出的符号
class TexParser {
  // LaTeX 解析器类
  // 核心逻辑在 ./parser.js
}

const DEFAULT_HANDLERS: Record<string, TexHandler>;
```

### 成熟度说明

LaTeX 是极其复杂的语言（Turing 完备的宏系统），完整解析几乎不可能。tex-to-myst 采用实用主义策略：
- 支持常见结构：section、paragraph、list、figure、table、math
- 支持常见命令：\textbf、\textit、\emph、\url、\href、\ref、\cite
- 不支持复杂宏包定义、自定义命令、TikZ 绘图等高级功能
- 对于无法识别的命令，保留原始 LaTeX 代码（raw tex 节点透传）

### LaTeX 解析挑战

1. **宏展开**：`\newcommand` 定义的自定义命令需要展开才能正确解析
2. **环境嵌套**：`\begin{env}...\end{env}` 需要正确配对
3. **注释**：`%` 开头的行注释（注意 `\%` 是转义的百分号）
4. **数学模式**：`$...$`、`$$...$$`、`\(...\)`、`\[...\]`、`\begin{equation}...\end{equation}`
5. **可选参数**：`\command[optional]{required}` 的解析
6. **分组嵌套**：`{...}` 的多层嵌套

tex-to-myst 的 `./parser.js` 使用栈式 tokenizer + 递归下降解析处理这些情况。

## 双向转换的对称性

myst-exporters 的导入和导出形成双向转换能力：

```
                    ┌──────────────────────┐
   JATS XML ───────►│                      ├──────► HTML
                    │                      │
   LaTeX ──────────►│     MyST MDAST       ├──────► LaTeX
                    │                      │
   MyST Markdown ──►│                      ├──────► DOCX
                    │                      │
                    └──────────────────────├──────► Typst
                                           ├──────► JATS XML
                                           └──────► Markdown
```

这使得：
- 从 JATS 导入后可以导出为任何格式（HTML/PDF/DOCX）
- 从 LaTeX 导入后可以转换为更现代的 Typst
- MyST 文档可以导出后再导入（有损回环，但核心内容保留）

## 与 myst-cli 集成

在 myst-cli 中，导入功能通过 `myst init` 命令触发：

```bash
# 从 JATS XML 创建 MyST 项目
myst init paper.xml

# 从 LaTeX 创建 MyST 项目
myst init paper.tex
```

myst-cli 根据文件扩展名选择导入器，生成 `myst.yml` 配置和 `.md` 文件。

## 相关概念

- [00-exporter-architecture](/concepts/00-exporter-architecture.md)：统一导出架构（导出器共性）
- [05-jats-export](/concepts/05-jats-export.md)：JATS XML 导出（导出方向对称）
- [02-latex-export](/concepts/02-latex-export.md)：LaTeX 导出（导出方向对称）
- [03-latex-import](/examples/03-latex-import.md)：LaTeX 导入示例
