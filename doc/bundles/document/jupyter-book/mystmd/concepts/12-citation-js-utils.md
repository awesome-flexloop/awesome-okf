---
type: concept
title: 参考文献处理（citation-js-utils）
description: citation-js-utils 包基于 citation-js 提供 BibTeX 解析、CSL-JSON 处理和引用文本格式化能力，支持 APA/Vancouver/Harvard 等引用样式。
tags: [mystmd, citation, bibtex, csl, bibliography]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "/references/mystmd-cli-source.md"
    facts: [F-127, F-128, F-129, F-130, F-131, F-132, F-133, F-134, F-135, F-136, F-137, F-138]
---

## 参考文献处理概述

MySTmd 使用 citation-js-utils 包处理学术引用。它基于 [citation-js](https://citation.js.org/) 库，提供：
- BibTeX/CSL-JSON 解析
- 引用渲染器创建（按 key 索引）
- 内联引用文本格式化（APA/Vancouver/Harvard 样式）
- HTML 清理（安全白名单）

## 核心数据结构

### CSL（Citation Style Language）

CSL 是学术引用的标准 JSON 格式，核心字段：

```ts
type CSL = {
  type: CSLType;               // 'article-journal'|'book'|'paper-conference'|...
  id: string;                  // 引用 key
  author?: CSLName[];          // 作者列表
  issued?: CSLDate;            // 发布日期
  title?: string;              // 标题
  'container-title'?: string;  // 期刊/书名
  DOI?: string;                // 数字对象标识符
  URL?: string;                // URL
  volume?: string;             // 卷号
  issue?: string;              // 期号
  page?: string;               // 页码
  publisher?: string;          // 出版商
  'publisher-place'?: string;  // 出版地
  // ... 50+ 其他字段
};

type CSLName = {
  family?: string;             // 姓
  given?: string;              // 名
  literal?: string;            // 机构名（非个人作者）
};

type CSLDate = {
  'date-parts'?: Array<Array<number>>;  // [[2023, 6, 15]]
  literal?: string;            // 非结构化日期
};
```

### CitationRenderer

```ts
type CitationRenderer = Record<string, {
  render(style?: string): string;     // 渲染完整引用条目（HTML）
  inline(style?: string): string;     // 渲染内联引用（HTML）
  getDOI(): string | undefined;       // 获取 DOI
  getURL(): string | undefined;       // 获取 URL
  cite(kind: InlineCite, opts?: InlineOptions): InlineNode[];  // 生成 MDAST 节点
  getLabel(): string;                 // 获取标签（Author Year）
  exportBibTeX(): string;             // 导出 BibTeX
}>;
```

CitationRenderer 是一个按 cite key 索引的渲染器映射，每个 key 对应一个可渲染的引用对象。

## 引用样式

### CitationJSStyles 枚举

```ts
enum CitationJSStyles {
  apa = 'citation-apa',
  vancouver = 'citation-vancouver',
  harvard = 'citation-harvard1',
}
```

### InlineCite 枚举

```ts
enum InlineCite {
  p = 'p',   // parenthetical — 括号式: (Author, 2023)
  t = 't',   // textual/narrative — 叙述式: Author (2023)
}
```

## 核心 API

### parseBibTeX

```ts
parseBibTeX(source: string): CSL[]
```

解析 BibTeX 字符串为 CSL 对象数组。支持的 BibTeX 条目类型：article、book、inproceedings、phdthesis、mastersthesis、techreport、misc 等。

```ts
import { parseBibTeX } from 'citation-js-utils';

const bibtex = `
@article{einstein1905electrodynamics,
  title={On the electrodynamics of moving bodies},
  author={Einstein, Albert},
  journal={Annalen der Physik},
  volume={322},
  number={10},
  pages={891--921},
  year={1905}
}
`;

const csl = parseBibTeX(bibtex);
// [{ type: 'article-journal', id: 'einstein1905electrodynamics', ... }]
```

### getCitationRenderers

```ts
getCitationRenderers(data: CSL[]): CitationRenderer
```

为 CSL 数组创建渲染器映射。每个引用 key 对应一个带有 render/inline/cite 等方法的渲染器。

```ts
import { getCitationRenderers } from 'citation-js-utils';

const renderers = getCitationRenderers(csl);
const entry = renderers['einstein1905electrodynamics'];

entry.render('citation-apa');
// → "Einstein, A. (1905). On the electrodynamics of moving bodies. ..."

entry.inline('citation-apa');
// → "Einstein, 1905"
```

### getInlineCitation

```ts
getInlineCitation(data: CSL, kind: InlineCite, opts?: InlineOptions): InlineNode[]
```

生成内联引用的 MDAST 节点数组（用于 MyST 文档树）。

```ts
type InlineOptions = {
  prefix?: string;       // 前缀文本
  suffix?: string;       // 后缀文本
  partial?: 'author' | 'year';  // 只输出部分
};

type InlineNode = {
  type: string;          // 'text' | 'strong' | 'emphasis' | ...
  value?: string;
  children?: InlineNode[];
};
```

#### 作者数量格式化规则

| 作者数 | kind=t（叙述式） | kind=p（括号式） |
|--------|-----------------|-----------------|
| 1 | `Family (Year)` | `(Family, Year)` |
| 2 | `Family & Family (Year)` | `(Family & Family, Year)` |
| 3+ | `Family *et al.* (Year)` | `(Family *et al.*, Year)` |
| 无作者 | `Publisher/Title (Year)` | `(Publisher/Title, Year)` |
| 无年份 | `Family (n.d.)` | `(Family, n.d.)` |

"et al." 使用 emphasis（斜体）节点标记。

#### partial 选项

- `partial: 'author'`：仅输出作者部分（如 `Family et al.`），不含年份和括号
- `partial: 'year'`：仅输出年份部分（如 `2023`），不含作者和括号

```ts
// {cite:t}`@key` → 叙述式
getInlineCitation(csl, InlineCite.t);
// → [text "Einstein", text " (1905)"]

// {cite:p}`@key` → 括号式
getInlineCitation(csl, InlineCite.p);
// → [text "(Einstein, 1905)"]

// 部分引用
getInlineCitation(csl, InlineCite.t, { partial: 'author' });
// → [text "Einstein"]
```

### yearFromCitation

```ts
yearFromCitation(data: CSL): number | string
```

从 CSL 数据中提取年份。优先取 issued.date-parts[0][0]，其次取 literal 中的数字，无法提取返回空字符串。

### createSanitizer

```ts
createSanitizer(): { cleanCitationHtml(html: string): string }
```

创建 HTML 清理器。citation-js 生成的 HTML 可能包含不安全标签，清理器只白名单以下标签：
- `<b>` — 粗体
- `<a>` — 链接（保留 href 属性）
- `<u>` — 下划线
- `<i>` — 斜体

其他标签被剥离，只保留文本内容。

## MyST 中的引用处理流程

```
Markdown: [cite:@einstein1905; @feynman1948]
     │
     ▼
markdown-it (citationsPlugin)
     │ 生成 cite_group 和 cite Token
     ▼
tokensToMyst → citeGroup { children: [cite, cite] }
     │
     ▼
transformCitations (document/project stage)
     │ 1. 收集所有 cite 节点的 key
     │ 2. 读取 bibliography 文件（.bib）
     │ 3. parseBibTeX → CSL[]
     │ 4. getCitationRenderers → CitationRenderer
     │ 5. 对每个 cite 节点：
     │    ├─ 查找 renderer
     │    ├─ getInlineCitation → InlineNode[]
     │    ├─ 替换 cite 节点的 children
     │    └─ 找不到 → citeNotFound 错误
     │ 6. 在文档末尾生成 bibliography 部分
     │    └─ 使用 renderer.render() 生成完整引用列表
     ▼
渲染时
     ├─ HTML: bibliography 渲染为 <dl>/<ol> 列表
     ├─ PDF (LaTeX): 转为 \cite{} 命令和 \bibliography{}
     └─ 其他格式: 使用内联文本
```

## 引用语法总结

| 语法 | 说明 | 渲染结果示例 |
|------|------|-------------|
| `[cite:@key]` | 括号引用（默认） | (Einstein, 1905) |
| `{cite:p}`@key`{cite:p}` | 括号引用 | (Einstein, 1905) |
| `{cite:t}`@key`{cite:t}` | 叙述引用 | Einstein (1905) |
| `[cite:@key1; @key2]` | 多引用 | (Einstein, 1905; Feynman, 1948) |
| `[see @key, p. 10]` | 带前缀/后缀 | (see Einstein, 1905, p. 10) |

## 参考文献列表格式

参考文献列表（bibliography）由 transformBiblio transform 生成，按引用顺序排序：

```markdown
## References

[Einstein, 1905] Einstein, A. (1905). On the electrodynamics of moving bodies.
  Annalen der Physik, 322(10), 891–921.

[Feynman, 1948] Feynman, R. P. (1948). Space-time approach to non-relativistic
  quantum mechanics. Reviews of Modern Physics, 20(2), 367–387.
```

支持的输出格式控制：
- 引用样式：APA/Vancouver/Harvard（通过 bibliography 配置）
- 编号方式：作者年份或数字编号
- 排序：引用顺序或字母顺序

## 相关概念

- [目标与引用系统](07-targets-references.md)
- [MDAST 转换管线](03-myst-transforms.md)
- [错误处理与规则 ID](05-error-handling.md)
- [参考文献引用示例](../examples/03-citations-example.md)
