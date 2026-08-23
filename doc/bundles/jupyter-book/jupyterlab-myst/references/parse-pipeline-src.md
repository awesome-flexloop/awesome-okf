---
type: reference
title: "MyST 解析管道源码"
description: "src/myst.ts 中的解析与转换管道：markdownParse、processArticleMDAST、processNotebookMDAST、renderNotebook �?transforms 模块"
source_path: "external/libs/ai/jupyter-book/jupyterlab-myst/src/myst.ts"
key_exports:
  - markdownParse
  - processArticleMDAST
  - processNotebookMDAST
  - processCellMDAST
  - buildNotebookMDAST
  - renderNotebook
facts: [F-022, F-023, F-024, F-025, F-026, F-027, F-028, F-029, F-051, F-052, F-053]
tags: [jupyterlab-myst, reference]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "external/libs/ai/jupyter-book/jupyterlab-myst/src/"
    facts: []
---

# MyST 解析管道源码

## 源码路径

- `src/myst.ts`：核心解析与转换管道
- `src/transforms/citations.ts`：citation 子节点插�?- `src/transforms/images.ts`：图�?URL 转换
- `src/transforms/links.tsx`：内部链接转换和 linkFactory
- `src/transforms/index.ts`：transforms 导出

## 解析函数

### markdownParse(text: string): Root

单单元格基础解析，不做引用解析：

1. 调用 `mystParse(content, { markdownit: { linkify: true }, directives: [...], roles: [] })`
2. 注册�?directives：cardDirective、gridDirectives、proofDirective、exerciseDirectives、tabDirectives
3. 运行 `basicTransformationsPlugin`（unified 同步管道�?4. 返回 MDAST Root

### processCellMDAST(resolver, mdast): mdast

单单元格处理�?1. copyNode(mdast) 深拷�?2. imageUrlSourceTransform �?通过 resolver 解析图片 URL
3. 返回处理后的 mdast

### buildNotebookMDAST(mystCells): Root

将多个单元格�?fragmentMDAST 聚合成完整文档：
```ts
const blocks = mystCells.map(cell => copyNode(cell.fragmentMDAST));
return { type: 'root', children: blocks };
```

每个 fragmentMDAST 已在 updateFragmentMDAST() 中设�?type:'block'�?
### processNotebookMDAST(mdast, resolver): Promise<IMySTDocumentState>

Notebook 场景的完整转换管道：

1. 定义 linkTransforms = [WikiTransformer, GithubTransformer, DOITransformer, RRIDTransformer]
2. �?mdast.children[0]（第一个单元格）提�?frontmatter（getFrontmatter + validatePageFrontmatter�?3. 创建 ReferenceState
4. unified 同步管道（按顺序）：
   - mathPlugin（数学宏，必须在 enumerate 前）
   - glossaryPlugin（术语表�?   - abbreviationPlugin（缩写词�?   - enumerateTargetsPlugin（枚举目�?标签�?   - linksPlugin（外部链接转换）
   - footnotesPlugin（脚注）
   - resolveReferencesPlugin（引用解析）
   - addCiteChildrenPlugin（引用子节点�?   - keysPlugin（键管理�?5. internalLinksTransform（内部链�?JupyterLab 适配�?6. reconstructHtmlTransform（修复内�?HTML�?7. 返回 { references, frontmatter, mdast }

### processArticleMDAST(mdast, resolver): Promise<IMySTDocumentState>

独立 Markdown 文件（Markdown Viewer 场景）的转换管道，与 processNotebookMDAST 基本相同，但�?- frontmatter 从整�?mdast 提取（而非 children[0]�?- 多执行一�?imageUrlSourceTransform（Notebook 场景�?processCellMDAST 中已处理�?
### renderNotebook(notebook: StaticNotebook): Promise<void>

Notebook 渲染的核心调度函数：

1. 筛选所�?rendered=true �?fragmentMDAST 已定义的 MyST Markdown 单元�?2. buildNotebookMDAST(cells) �?聚合为完�?MDAST
3. processNotebookMDAST(mdast, resolver) �?全局处理
4. 遍历每个单元格：
   - 创建�?MySTModel
   - �?0 个单元格设置 frontmatter
   - mdast = processedMDAST.children[index]（分片）
   - 保留�?model �?expressions
   - 赋值给 cell.mystModel（setter �?dispose �?model 并触发渲染）

## transforms 模块

### transforms/images.ts

imageUrlSourceTransform：遍�?MDAST 中的 image 节点，使�?JupyterLab resolver 将相�?URL（包�?attachments:）解析为可访问的 URL�?
### transforms/links.tsx

- internalLinksTransform：将内部链接（以 # 开头或相对路径）转换为 JupyterLab 可处理的格式
- linkFactory(resolver, linkHandler)：返回自定义 Link 组件，使�?ILinkHandler 处理链接点击导航

### transforms/citations.ts

addCiteChildrenPlugin：unified 插件，为 citation 节点添加格式化的子节点（显示引用内容）�?