---
type: concept
title: "JATS XML 导出"
description: "myst-to-jats 将 MDAST 转换为 JATS XML 的 JatsSerializer 栈式架构、JatsDocument 文档构建和引用数据提取"
tags: [myst-exporters, jats, xml, publishing, pubmed, crossref]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "myst-to-jats/src/index.ts"
    facts: [F-014, F-015, F-016, F-017, F-018]
---

# JATS XML 导出

JATS（Journal Article Tag Suite）XML 导出由 `myst-to-jats` 包提供。JATS 是 NISO 标准的学术论文 XML 格式，被 PubMed、Crossref、PMC 等学术出版系统广泛使用。myst-to-jats 使用栈式（stack-based）Serializer 构建 XML 元素树。

## JATS 简介

JATS 定义了三种文档类型：
- **Article Authoring**：作者投稿用的简化标签集
- **Publishing**：出版商发布用的完整标签集（MyST 默认输出此类型）
- **Archiving and Interchange**：存档交换用的最完整标签集

JATS XML 结构：
```xml
<article article-type="research-article">
  <front>...</front>     <!-- 元数据：标题/作者/摘要/基金 -->
  <body>...</body>       <!-- 正文：section/fig/table/eq -->
  <back>...</back>       <!-- 附录：参考文献/附录 -->
</article>
```

## JatsSerializer 栈式架构

与 TexSerializer 的字符串拼接不同，JatsSerializer 基于 Element 栈构建 XML 树：

```typescript
class JatsSerializer implements IJatsSerializer {
  file: VFile;
  data: JatsArticleMeta;
  options: Options;
  stack: Element[];        // 当前节点栈
  footnotes: Record<string, any>;
  refs: Record<string, Ref>;
  citations: CitationRef[];
  expressions: Record<string, any>;
  slug: string;
  numbering: JatsNumbering;
}
```

### 栈操作方法

| 方法 | 说明 |
|------|------|
| `openNode(name, attributes?, isLeaf?)` | 创建新 Element，压入栈顶；isLeaf=true 时添加到父级后立即弹出 |
| `closeNode()` | 弹出栈顶节点 |
| `pushNode(el?)` | 将节点添加到栈顶的 children |
| `text(text?)` | 添加/合并文本节点到栈顶 |
| `renderChildren(node)` | 遍历子节点→查表分发（与其他 Serializer 一致）|
| `renderInline(node, name, attributes?)` | 便捷方法：openNode→renderChildren→closeNode |
| `addLeaf(name, attributes?)` | 便捷方法：openNode(isLeaf=true)→closeNode |

### openNode 行为详解

```typescript
openNode(name, attributes, isLeaf = false) {
  const node: Element = { type: 'element', name, attributes, children: [] };
  const top = this.stack[this.stack.length - 1];
  if (top) top.children?.push(node);
  if (!isLeaf) this.stack.push(node);
  return node;
}
```

- 对于块级元素（如 `<sec>`、`<p>`、`<fig>`），不设置 isLeaf，压入栈顶，后续子节点会作为 children 添加
- 对于叶元素（如 `<graphic>`、`<break/>`），设置 isLeaf=true，添加到父级后立即弹出，不会成为当前父节点
- 每次 openNode 必须配对 closeNode（非叶节点）

## JatsDocument：完整文档构建

JatsSerializer 输出的是 `<body>` 内的内容，完整的 JATS 文档由 JatsDocument 类组装：

```typescript
class JatsDocument implements IJatsDocument {
  serializer: JatsSerializer;
  article: Element;  // 完整 <article> 元素
  references: References;
}
```

JatsDocument 负责：
1. 构建 `<front>` 元数据：
   - `<journal-meta>`：期刊信息（journal-id、journal-title、issn、publisher）
   - `<article-meta>`：文章信息（article-id、title-group、contrib-group、aff、abstract、funding-group、volume/issue/fpage 等）
   - `<custom-meta-group>`：自定义元数据（tag、subject、doi、key-value 对）
2. 调用 JatsSerializer 渲染 `<body>`
3. 构建 `<back>`：
   - `<ref-list>`：参考文献列表（从 citations/refs 构建）
   - `<fn-group>`：脚注
   - `<app-group>`：附录

### DOI 和 URL 处理

JatsDocument 有特殊的 DOI/URL 检测逻辑：
- 如果 frontmatter.doi 存在，添加 `<article-id pub-id-type="doi">`
- 如果 URL 包含 doi.org 前缀，提取 DOI
- 支持 eLife/JOSS/PMC/PLOS 等平台的 URL 模式自动提取 ID

## 编号系统

JATS 中的图表公式编号由 `JatsNumbering` 管理：

```typescript
type JatsNumbering = {
  figures: number;
  tables: number;
  equations: number;
  supplements: number;
}
```

当遇到 `container` 节点（figure/table/supplement）或 `math`（display）节点时递增编号，生成 `<label>Figure 1</label>` 等。

## 引用数据提取

JatsSerializer 在渲染过程中提取参考文献数据：

1. `this.citations`：按顺序收集所有 citation 节点
2. `this.refs`：按引用 key 索引的参考文献数据，包含：
   - 解析后的 HTML 片段（`html` 属性）
   - DOI（从 URL 或属性提取）
   - 作者/年份/标题等元数据
3. `renderBack()` 使用这些数据构建 `<ref-list>`：
   ```xml
   <ref-list>
     <ref id="ref1">
       <mixed-citation publication-type="journal">...</mixed-citation>
     </ref>
   </ref-list>
   ```

## 节点映射要点

| MyST 节点 | JATS 元素 | 说明 |
|----------|----------|------|
| heading | `<title>`（在 `<sec>` 内）| 标题层级映射到 `<sec>` 嵌套 |
| paragraph | `<p>` | 段落 |
| text/strong/em | `<bold>`/`<italic>`/`<underline>` | 内联格式 |
| list | `<list list-type="bullet/order">` | 列表 |
| container/figure | `<fig id="..."><label/><caption/><graphic/></fig>` | 图片 |
| container/table | `<table-wrap id="..."><label/><caption/><table/></table-wrap>` | 表格 |
| math/display | `<disp-formula id="..."><label/>...</disp-formula>` | 公式 |
| math/inline | `<inline-formula>...</inline-formula>` | 行内公式 |
| crossReference | `<xref ref-type="fig/table/sec/eq/bibr" rid="..."/>` | 交叉引用 |
| cite | `<xref ref-type="bibr" rid="..."/>` | 引用 |
| footnoteReference | `<xref ref-type="fn" rid="fn..."/>` | 脚注引用 |
| raw/jats | 直接透传 XML | JATS 原生 XML 透传 |
| admonition | `<boxed-text>` | 提示框 |

### 特殊处理

- **fig-group**：JATS 中多图用 `<fig-group>` 标签（MyST 输出中 fig-group 转为 tabSet/tabItem 是 HTML 导出的行为，JATS 导出保留 fig-group）
- **graphic**：图片通过 `<graphic xlink:href="path" xlink:type="simple"/>` 引用，mimetype 根据扩展名判断
- **table**：直接输出 HTML 表格的 CALS 或 HTML 表格模型（myst-to-jats 输出 HTML 表格模型，即 `<table><thead><tbody><tr><td/>`）
- **xref 的 ref-type 映射**：
  - `ref-type="sec"` → 引用节
  - `ref-type="fig"` → 引用图
  - `ref-type="table"` → 引用表
  - `ref-type="disp-formula"` → 引用公式
  - `ref-type="bibr"` → 参考文献引用
  - `ref-type="fn"` → 脚注引用

## 输出结果

`file.result` 为完整 JATS XML 字符串（由 JatsDocument 的 `getArticle(trim)` 生成，内部使用 `xml-js` 转换 Element 树为 XML 字符串）。XML 声明为 `<?xml version="1.0" encoding="UTF-8"?>`。

## 使用方式

```bash
myst build paper.md --jats
# 输出 _build/exports/paper.xml
```

或直接调用：

```typescript
import { unified } from 'unified';
import mystParse from 'myst-parser';
import { mystToJatsPlugin } from 'myst-to-jats';

const file = unified()
  .use(mystParse)
  .use(mystToJatsPlugin)
  .processSync('# Title\n\nContent.');

console.log(file.result);  // JATS XML 字符串
```

## 与 jats-to-myst 的对称性

myst-to-jats（导出）和 jats-to-myst（导入）共享对称的架构设计：
- 导出用 JatsSerializer（栈式构建 XML）
- 导入用 JatsParser（栈式构建 MDAST）
- 两者都使用 handler 映射表分发节点处理逻辑
- DEFAULT_HANDLERS 在两个包中分别定义，但处理思路对称

## 相关概念

- [00-exporter-architecture](00-exporter-architecture.md)：统一导出架构
- [09-import-converters](09-import-converters.md)：JATS 导入（jats-to-myst）
- [03-latex-import](../examples/03-latex-import.md)：LaTeX 导入示例
