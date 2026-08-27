---
type: concept
title: "MyST 解析与渲染管道"
description: "详解 jupyterlab-myst 中的 MyST Markdown 解析流程：从 myst-parser 解析到 unified 转换管道，再到 React 渲染的完整链路"
tags: [jupyterlab-myst, myst-parser, unified, mdast, pipeline, transforms]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "/references/parse-pipeline-src.md"
    facts: [F-022, F-023, F-024, F-025, F-026, F-027, F-028, F-029, F-051, F-052, F-053, F-054, F-055]
---

# MyST 解析与渲染管道

jupyterlab-myst 在浏览器中使用 myst-parser（JavaScript 版）解析 MyST Markdown，通过 unified 插件管道做转换，最终使用 myst-to-react 将 MDAST 渲染为 React 组件。解析过程分为单单元格解析和 Notebook 全局聚合两个阶段。

## 管道总览

```
Markdown 文本
    │
    ▼
┌─────────────────────────────────────────────┐
│  阶段1: markdownParse(text)                 │
│  ├─ mystParse (myst-parser)                 │
│  │   ├─ markdownit: { linkify: true }       │
│  │   ├─ directives: card, grid, proof,      │
│  │   │              exercise, tabs           │
│  │   └─ roles: []                           │
│  └─ basicTransformationsPlugin (unified)    │
│                                             │
│  输出: MDAST Root（单单元格）                 │
└─────────────────┬───────────────────────────┘
                  │
                  ▼ (Notebook 场景)
┌─────────────────────────────────────────────┐
│  阶段2: 全局聚合                             │
│  ├─ buildNotebookMDAST(cells)               │
│  │   └─ 拼接所有 fragmentMDAST → root       │
│  └─ processNotebookMDAST(root, resolver)    │
│      ├─ getFrontmatter (从第一个子节点)       │
│      ├─ unified 转换管道（见下方）            │
│      ├─ internalLinksTransform              │
│      └─ reconstructHtmlTransform            │
│                                             │
│  输出: { references, frontmatter, mdast }   │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│  阶段3: React 渲染                          │
│  ├─ MySTModel.mdast = 分片后的 MDAST         │
│  ├─ MySTWidget.render()                    │
│  │   └─ <MyST ast={mdast} /> (myst-to-react)│
│  └─ 自定义 renderers 覆盖 listItem,          │
│      inlineExpression 等                   │
└─────────────────────────────────────────────┘
```

## 阶段 1：单单元格解析

### markdownParse(text)

`markdownParse()` 是解析入口，对每个 Markdown 单元格的源码独立解析：

```ts
export function markdownParse(text: string): Root {
  const parseMyst = (content: string) => {
    return mystParse(content, {
      markdownit: { linkify: true },
      directives: [
        cardDirective,
        ...gridDirectives,
        proofDirective,
        ...exerciseDirectives,
        ...tabDirectives
      ],
      roles: []
    });
  };

  const mdast = parseMyst(text);
  unified()
    .use(basicTransformationsPlugin, { parser: parseMyst })
    .runSync(mdast as any);
  return mdast as Root;
}
```

### 注册的 Directives

| Directive | 来源包 | 功能 |
|-----------|--------|------|
| `cardDirective` | myst-ext-card | 卡片容器 |
| `gridDirectives` | myst-ext-grid | 网格布局（含 grid-item） |
| `proofDirective` | myst-ext-proof | 证明/定理/引理环境 |
| `exerciseDirectives` | myst-ext-exercise | 练习/解答环境 |
| `tabDirectives` | myst-ext-tabs | 标签页切换 |

这些 directives 覆盖了学术写作中常用的结构化内容块。

### basicTransformationsPlugin

这是 myst-transforms 提供的基础转换插件，处理：
- 代码块语言标记
- 内联代码标记
- 基本的文本节点规范化

这个阶段不做引用解析（脚注、交叉引用等需要全局上下文）。

## 阶段 2：Notebook 全局聚合

### buildNotebookMDAST(cells)

将所有 Markdown 单元格的 fragmentMDAST 拼接为一个完整文档：

```ts
export function buildNotebookMDAST(mystCells: IMySTMarkdownCell[]): any {
  const blocks = mystCells.map(cell => copyNode(cell.fragmentMDAST));
  return { type: 'root', children: blocks };
}
```

每个 fragmentMDAST 在 `updateFragmentMDAST()` 中已设置 `type: 'block'`，确保拼接后是合法的 MDAST 树。

### processNotebookMDAST(mdast, resolver)

Notebook 场景的完整转换管道：

```ts
// 1. 外部链接转换器
const linkTransforms = [
  new WikiTransformer(),    // [[WikiLink]] → 链接
  new GithubTransformer(),  // #123, @user → GitHub 链接
  new DOITransformer(),     // doi:xxx → https://doi.org/xxx
  new RRIDTransformer(),    // RRID:xxx → 研究资源标识符链接
];

// 2. 提取 frontmatter（从第一个子节点）
const { frontmatter: frontmatterRaw } = getFrontmatter(file, mdast.children[0]);
const frontmatter = validatePageFrontmatter(frontmatterRaw, {...});

// 3. 创建引用状态
const state = new ReferenceState('<PATH>', { frontmatter, vfile: file });

// 4. Unified 转换管道
unified()
  .use(mathPlugin, { macros: frontmatter?.math ?? {} })      // 数学公式（必须在 enumerate 前）
  .use(glossaryPlugin)                                       // 术语表
  .use(abbreviationPlugin, { abbreviations: frontmatter.abbreviations }) // 缩写
  .use(enumerateTargetsPlugin, { state })                    // 枚举目标（标题、图表编号）
  .use(linksPlugin, { transformers: linkTransforms })        // 外部链接转换
  .use(footnotesPlugin)                                      // 脚注
  .use(resolveReferencesPlugin, { state })                  // 交叉引用解析
  .use(addCiteChildrenPlugin)                                // 引用子节点
  .use(keysPlugin)                                           // 键管理
  .runSync(mdast as any, file);

// 5. 后处理
await internalLinksTransform(mdast, { resolver });           // 内部链接 JupyterLab 适配
reconstructHtmlTransform(mdast);                             // 修复内联 HTML
```

### 插件执行顺序的重要性

插件顺序不是随意的，存在严格的依赖关系：
1. **mathPlugin 必须在 enumerateTargetsPlugin 之前**：数学公式可能产生带 label 的节点，需要在枚举目标时被计数。
2. **glossaryPlugin 必须在 enumerateTargetsPlugin 之前**：术语表术语可能被引用，需要先注册。
3. **enumerateTargetsPlugin 必须在 resolveReferencesPlugin 之前**：先注册所有目标，再解析对目标的引用。
4. **linksPlugin 在 footnotesPlugin 和 resolveReferencesPlugin 之前**：外部链接转换不依赖内部引用解析。
5. **addCiteChildrenPlugin 在 resolveReferencesPlugin 之后**：引用解析后才能为 citation 节点添加格式化子节点。

### processArticleMDAST vs processNotebookMDAST

两个函数几乎相同，关键区别：

| 差异 | processArticleMDAST | processNotebookMDAST |
|------|-------------------|---------------------|
| frontmatter 来源 | 整个 mdast（getFrontmatter 处理 root） | mdast.children[0]（第一个单元格） |
| 图片处理 | imageUrlSourceTransform（管道内） | 不在管道内（由 processCellMDAST 单独处理） |
| 使用场景 | Markdown Viewer（独立 .md 文件） | Notebook 单元格 |

### processCellMDAST(resolver, mdast)

单单元格的轻量处理，仅做图片 URL 转换：

```ts
export async function processCellMDAST(resolver, mdast) {
  mdast = copyNode(mdast);
  try {
    await imageUrlSourceTransform(mdast, { resolver });
  } catch (error) {
    // pass — 图片解析失败不阻断渲染
  }
  return mdast;
}
```

这是在单元格编辑时（未触发全局渲染）做的最小处理，确保编辑模式下图片能正确显示。

### renderNotebook(notebook)

全局渲染调度函数：

1. 筛选已渲染（rendered=true）且有 fragmentMDAST 的 MyST 单元格
2. buildNotebookMDAST → 聚合为完整文档
3. processNotebookMDAST → 全局转换
4. 遍历单元格，分片回传 MDAST：
   - 第 0 个单元格获得 frontmatter
   - 每个单元格获得 processedMDAST.children[index]
   - 保留原 model 的 expressions（不重新执行）
5. 赋值 cell.mystModel = nextModel 触发 React 重渲染

```ts
mystCells.forEach((cell, index) => {
  if (cell.rendered) {
    const nextModel = new MySTModel();
    nextModel.references = references;
    nextModel.frontmatter = index === 0 ? frontmatter : undefined;
    nextModel.mdast = processedMDAST.children[index];
    nextModel.expressions = cell.mystModel.expressions;
    cell.mystModel = nextModel;
  }
});
```

## 阶段 3：React 渲染

处理后的 MDAST 通过 myst-to-react 的 `<MyST>` 组件渲染为 React 元素。jupyterlab-myst 通过自定义 renderers 覆盖默认渲染行为：

- **listItem**：支持任务列表复选框（- [ ] / - [x]）
- **inlineExpression**：渲染内核执行的表达式结果
- **link**：通过 linkFactory 创建，使用 JupyterLab ILinkHandler 处理导航

Provider 嵌套（在 MySTWidget.render() 中）提供渲染所需的上下文：
- TaskItemControllerProvider → 复选框交互
- ThemeProvider → JupyterLab 主题适配
- SanitizerProvider → HTML 安全清洗
- UserExpressionsProvider → inline expression 结果
- ArticleProvider + TabStateProvider → myst-to-react 需要的文档上下文

## 相关概念

- [00-architecture-plugins.md](00-architecture-plugins.md)：插件架构
- [02-myst-markdown-cell.md](02-myst-markdown-cell.md)：单元格生命周期
- [03-inline-expressions.md](03-inline-expressions.md)：内联表达式执行
- [01-using-jupyterlab-myst.md](../examples/01-using-jupyterlab-myst.md)：使用示例
