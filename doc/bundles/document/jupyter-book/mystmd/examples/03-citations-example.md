---
type: example
title: 参考文献引用处理
description: 演示如何使用 citation-js-utils 解析 BibTeX、创建引用渲染器、格式化内联引用和生成参考文献列表。
tags: [mystmd, citation, bibtex, csl, bibliography]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "/references/mystmd-cli-source.md"
    facts: [F-127, F-128, F-129, F-130, F-131, F-132, F-133, F-134, F-135, F-136, F-137, F-138]
  - path: "/concepts/12-citation-js-utils.md"
    facts: []
---

## 目标

使用 `citation-js-utils` 包完成 BibTeX 解析、引用渲染器创建和内联引用文本格式化。

## 前置条件

- Node.js 16+
- 已安装 `citation-js-utils`、`@citation-js/core` 等依赖

```bash
npm install citation-js-utils
```

## 示例 1：解析 BibTeX

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
  year={1905},
  doi={10.1002/andp.19053221004}
}

@book{feynman1964lectures,
  title={The Feynman Lectures on Physics},
  author={Feynman, Richard P and Leighton, Robert B and Sands, Matthew},
  year={1964},
  publisher={Addison-Wesley},
  volume={2}
}

@inproceedings{knuth1984literate,
  title={Literate programming},
  author={Knuth, Donald E},
  booktitle={The Computer Journal},
  volume={27},
  number={2},
  pages={97--111},
  year={1984},
  organization={Oxford University Press}
}
`;

const cslEntries = parseBibTeX(bibtex);
console.log(`Parsed ${cslEntries.length} entries`);
// → Parsed 3 entries

cslEntries.forEach(entry => {
  console.log(`- [${entry.id}] ${entry.type}: ${entry.title}`);
});
// - [einstein1905electrodynamics] article-journal: On the electrodynamics of moving bodies
// - [feynman1964lectures] book: The Feynman Lectures on Physics
// - [knuth1984literate] paper-conference: Literate programming
```

## 示例 2：创建引用渲染器

```ts
import { parseBibTeX, getCitationRenderers, CitationJSStyles } from 'citation-js-utils';

const cslEntries = parseBibTeX(bibtex);
const renderers = getCitationRenderers(cslEntries);

// 获取单个引用
const einstein = renderers['einstein1905electrodynamics'];
if (einstein) {
  // 渲染完整引用条目（APA 格式 HTML）
  console.log('=== Full citation (APA) ===');
  console.log(einstein.render(CitationJSStyles.apa));
  // → Einstein, A. (1905). On the electrodynamics of moving bodies.
  //   Annalen der Physik, 322(10), 891–921. https://doi.org/10.1002/...

  // 内联引用（括号式）
  console.log('\n=== Inline citation (APA) ===');
  console.log(einstein.inline(CitationJSStyles.apa));
  // → Einstein, 1905

  // 获取 DOI 和 URL
  console.log('\nDOI:', einstein.getDOI());
  console.log('URL:', einstein.getURL());
}
```

## 示例 3：格式化内联引用文本（MDAST 节点）

```ts
import { parseBibTeX, getCitationRenderers, getInlineCitation, InlineCite } from 'citation-js-utils';

const cslEntries = parseBibTeX(bibtex);
const renderers = getCitationRenderers(cslEntries);

const einsteinCSL = cslEntries.find(e => e.id === 'einstein1905electrodynamics')!;

// 叙述式引用：Author (Year)
const narrativeNodes = getInlineCitation(einsteinCSL, InlineCite.t);
console.log('Narrative:', nodesToText(narrativeNodes));
// → Einstein (1905)

// 括号式引用：(Author, Year)
const parentheticalNodes = getInlineCitation(einsteinCSL, InlineCite.p);
console.log('Parenthetical:', nodesToText(parentheticalNodes));
// → (Einstein, 1905)

// 仅作者部分
const authorOnly = getInlineCitation(einsteinCSL, InlineCite.t, { partial: 'author' });
console.log('Author only:', nodesToText(authorOnly));
// → Einstein

// 仅年份部分
const yearOnly = getInlineCitation(einsteinCSL, InlineCite.t, { partial: 'year' });
console.log('Year only:', nodesToText(yearOnly));
// → 1905

// 带前缀/后缀
const withPrefixSuffix = getInlineCitation(einsteinCSL, InlineCite.p, {
  prefix: 'see ',
  suffix: ', p. 15',
});
console.log('With prefix/suffix:', nodesToText(withPrefixSuffix));
// → (see Einstein, 1905, p. 15)

// 多作者情况
const feynmanCSL = cslEntries.find(e => e.id === 'feynman1964lectures')!;
const feynmanCite = getInlineCitation(feynmanCSL, InlineCite.p);
console.log('3+ authors:', nodesToText(feynmanCite));
// → (Feynman et al., 1964)

// 辅助函数：将 InlineNode[] 转为纯文本
function nodesToText(nodes: any[]): string {
  return nodes.map(n => {
    if (n.value) return n.value;
    if (n.children) return nodesToText(n.children);
    return '';
  }).join('');
}
```

## 示例 4：检查 InlineNode 结构（用于 MDAST 集成）

```ts
const narrativeNodes = getInlineCitation(einsteinCSL, InlineCite.t);
console.log(JSON.stringify(narrativeNodes, null, 2));
// [
//   { "type": "text", "value": "Einstein" },
//   { "type": "text", "value": " (" },
//   { "type": "text", "value": "1905" },
//   { "type": "text", "value": ")" }
// ]

// 多作者 "et al." 使用 emphasis 标记
const feynmanCite = getInlineCitation(feynmanCSL, InlineCite.t);
console.log(JSON.stringify(feynmanCite, null, 2));
// [
//   { "type": "text", "value": "Feynman" },
//   { "type": "text", "value": " " },
//   { "type": "emphasis", "children": [{ "type": "text", "value": "et al." }] },
//   { "type": "text", "value": " (" },
//   { "type": "text", "value": "1964" },
//   { "type": "text", "value": ")" }
// ]
```

## 示例 5：提取年份

```ts
import { yearFromCitation } from 'citation-js-utils';

console.log(yearFromCitation(einsteinCSL));  // 1905
console.log(yearFromCitation(feynmanCSL));   // 1964
```

## 示例 6：清理 citation-js 生成的 HTML

```ts
import { createSanitizer } from 'citation-js-utils';

const sanitizer = createSanitizer();

const unsafeHtml = '<b>Bold</b> <script>alert("xss")</script> <a href="https://example.com">Link</a>';
const safeHtml = sanitizer.cleanCitationHtml(unsafeHtml);
console.log(safeHtml);
// → '<b>Bold</b> alert("xss") <a href="https://example.com">Link</a>'
// script 标签被移除，<b>/<a>/<u>/<i> 被保留
```

## 示例 7：在 MyST 文档处理中集成引用

```ts
import { mystParse } from 'myst-parser';
import { unified } from 'unified';
import { VFile } from 'vfile';
import { parseBibTeX, getCitationRenderers } from 'citation-js-utils';
import { basicTransformationsPlugin } from 'myst-transforms';
import { selectAll } from 'unist-util-select';
import { readFileSync } from 'fs';

// 1. 读取 BibTeX 文件并解析
const bibtexContent = readFileSync('references.bib', 'utf-8');
const cslEntries = parseBibTeX(bibtexContent);
const renderers = getCitationRenderers(cslEntries);

// 2. 解析 MyST 文档
const mdContent = `
# Quantum Mechanics

As shown by {cite:t}`@einstein1905electrodynamics`{cite:t}, 
light exhibits wave-particle duality {cite:p}`@feynman1964lectures`{cite:p}.
`;

const vfile = new VFile();
vfile.value = mdContent;

const mdast = mystParse(mdContent, { vfile });

// 3. 在 transform 中处理引用
// （这是 transformCitations 在 myst-transforms 中的核心逻辑）
const citeNodes = selectAll('cite', mdast) as any[];
citeNodes.forEach(cite => {
  const key = cite.label;
  const renderer = renderers[key];
  if (!renderer) {
    console.error(`Citation not found: @${key}`);
    return;
  }
  
  // 根据 kind 格式化
  const kind = cite.kind === 'narrative' ? InlineCite.t : InlineCite.p;
  const nodes = getInlineCitation(cslEntries.find(e => e.id === key)!, kind);
  cite.children = nodes;
});

// 4. 输出结果
console.log('Processed citations:');
citeNodes.forEach(cite => {
  const text = nodesToText(cite.children);
  console.log(`  @${cite.label} (${cite.kind}): ${text}`);
});
// → @einstein1905electrodynamics (narrative): Einstein (1905)
// → @feynman1964lectures (parenthetical): (Feynman et al., 1964)
```

## 关键点

1. **BibTeX 解析**：`parseBibTeX()` 将 BibTeX 字符串转为 CSL 对象数组
2. **渲染器创建**：`getCitationRenderers()` 创建按 key 索引的渲染器映射
3. **内联格式化**：`getInlineCitation()` 返回 MDAST InlineNode[] 而非纯字符串，支持 emphasis 等格式
4. **作者数量规则**：1位→Family，2位→Family & Family，3+位→Family *et al.*（斜体）
5. **HTML 清理**：`createSanitizer()` 只白名单 b/a/u/i 标签，防止 XSS
6. **与 MyST 集成**：在 transformCitations transform 中使用，处理 `[cite:@key]` 和 `{cite:p/t}` 语法

## 引用样式映射

| 样式 | 内联 | 完整引用 |
|------|------|---------|
| APA | Author (Year) / (Author, Year) | Author, A. (Year). Title. Journal, vol(issue), pages. |
| Vancouver | [1] / (1) | [1] Author A. Title. Journal. Year;vol(issue):pages. |
| Harvard | Author (Year) / (Author, Year) | Author, A., Year. Title. Journal, vol(issue), pp. pages. |

## 下一步

- 了解 [目标与引用系统](/concepts/07-targets-references.md)中交叉引用的处理流程
- 了解 [MDAST 转换管线](/concepts/03-myst-transforms.md)中 transformCitations 的位置
- 学习 [自定义角色](/examples/04-custom-role.md)创建自定义引用角色
