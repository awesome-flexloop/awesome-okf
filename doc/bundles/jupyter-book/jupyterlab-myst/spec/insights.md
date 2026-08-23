---
type: insights
bundle: jupyterlab-myst
generated: 2026-08-23
verified: true
status: stable
sources:
  - /spec/facts.md
---

# jupyterlab-myst 核心洞察与知识地图

## 洞察 1：三插件架构实现无缝集成

jupyterlab-myst 通过三个独立但协作的 JupyterLab 插件实现对 Markdown 单元格和 Markdown 文件的 MyST 渲染增强，而非替换整个 Markdown 系统：

- **content-factory 插件**在单元格层面拦截——通过提供自定义 `NotebookPanel.IContentFactory`，让 JupyterLab 创建 MySTMarkdownCell 而非默认 MarkdownCell。这是 JupyterLab 扩展点的标准用法，不需要 monkey-patching。
- **executor 插件**在执行层面监听——通过连接 `NotebookActions.executed` 信号，在代码单元格执行完毕后自动触发 Markdown 单元格中 inline expression 的求值。这意味着"Shift+Enter 执行代码"后，Markdown 中的 `{eval}` 结果会自动刷新。
- **mime-renderer 插件**在文件层面增强——通过向 IRenderMimeRegistry 注册 `text/markdown` 渲染工厂（rank=50），使得 Markdown Viewer 打开的独立 .md 文件也使用 MyST 渲染。

这种分层设计让 jupyterlab-myst 既能在 Notebook 中增强 Markdown 单元格，又能在文件查看器中渲染独立 MyST 文档，且三者互不干扰。

## 洞察 2：Fragment-per-Cell + 全局聚合的两阶段渲染

MyST 的引用解析（脚注、交叉引用、citation 等）需要文档全局上下文，但 JupyterLab 的 Markdown 单元格是独立编辑单元。jupyterlab-myst 采用了两阶段渲染策略解决这个矛盾：

1. **Fragment 解析**：每个 MySTMarkdownCell 维护自己的 `fragmentMDAST`（仅做基础解析和图片 URL 转换），在单元格编辑时增量更新。
2. **全局聚合**：渲染时调用 `renderNotebook(notebook)`，将所有单元格的 fragmentMDAST 拼接为完整 root，运行完整转换管道（enumerateTargetsPlugin、resolveReferencesPlugin、footnotesPlugin 等），然后分片回传给各单元格。

关键设计：每个单元格的 fragmentMDAST 在 `updateFragmentMDAST()` 中设置 `type = 'block'`，使得拼接后的 root 是合法的 MDAST 树。第一个单元格的 fragment 用于提取 frontmatter。全局聚合保证了跨单元格引用（如"见图 1"）能正确解析。

## 洞察 3：利用 Jupyter 内核协议的 user_expressions 机制执行内联表达式

inline expression 的执行没有走常规的 `execute_request(code=...)` 路径（那样会在单元格输出区域产生副作用），而是巧妙地利用了 Jupyter 内核协议的 `user_expressions` 字段：

```ts
kernel.requestExecute({
  code: '',  // 空 code，不执行任何代码单元格
  user_expressions: { '0': 'x + 1', '1': 'df.shape[0]' }
})
```

Jupyter 内核协议规定：execute_request 执行完 code 后，会对 user_expressions 字典中的每个表达式在用户命名空间中求值，结果在 execute_reply 中返回。由于 code 为空字符串，这个请求不会产生任何输出或副作用，只会求值指定的表达式并返回 MIME bundle 结果。结果通过 `selectAll('inlineExpression', mdast)` 从 MDAST 中按位置提取，存入单元格 metadata 的 `user_expressions` 字段，持久化到 .ipynb 文件中。

这是一个非常优雅的设计——它复用了内核的执行上下文（前一个代码单元格定义的变量都可用），但不干扰单元格输出。

## 洞察 4：信任机制与安全

jupyterlab-myst 遵循 Jupyter 的信任模型：
- inline expression 的执行结果存储在单元格 metadata 中
- 只有 `trusted = true` 的单元格才会渲染这些结果（防止打开不受信任的 Notebook 时执行任意 HTML/JS 输出）
- MySTWidget 接收 trusted 属性，通过 UserExpressionsProvider 传递给 InlineExpression 组件
- `notebookCellExecuted()` 执行成功后自动设置 `cell.model.trusted = true`（因为用户刚主动执行了内核代码，隐式信任）
- SanitizerProvider 将 JupyterLab 的 ISanitizer 注入渲染管道，对 HTML 输出做安全清洗

## 知识地图

```
jupyterlab-myst
├── 入口层（3个插件）
│   ├── jupyterlab-myst:content-factory → MySTContentFactory → MySTMarkdownCell
│   ├── jupyterlab-myst:executor → NotebookActions.executed 信号
│   └── jupyterlab-myst:mime-renderer → mystMarkdownRendererFactory → RenderedMySTMarkdown
│
├── 核心组件
│   ├── MySTMarkdownCell（extends MarkdownCell）
│   │   ├── fragmentMDAST（单单元格解析结果）
│   │   ├── MySTModel（VDomModel）
│   │   ├── MySTWidget（React 渲染器）
│   │   ├── ActivityMonitor（防抖，100ms）
│   │   └── AttachmentsResolver（附件解析）
│   │
│   ├── MySTWidget（extends VDomRenderer）
│   │   └── React Provider 链
│   │       ├── TaskItemControllerProvider（复选框交互）
│   │       ├── ThemeProvider（主题适配）
│   │       ├── SanitizerProvider（安全清洗）
│   │       ├── UserExpressionsProvider（内联表达式结果）
│   │       ├── TabStateProvider（标签页状态）
│   │       └── ArticleProvider → <MyST ast={mdast}/>
│   │
│   └── RenderedMySTMarkdown（extends MySTWidget, MIME 渲染器）
│       └── 用于 Markdown Viewer 场景
│
├── 解析管道（myst.ts）
│   ├── markdownParse() → 单单元格基础解析
│   ├── processCellMDAST() → 图片URL转换
│   ├── buildNotebookMDAST() → 多单元格聚合
│   ├── processNotebookMDAST() → Notebook完整转换
│   └── processArticleMDAST() → 独立文档完整转换
│
├── 内联表达式执行（actions.ts + userExpressions.ts）
│   ├── notebookCellExecuted() → 入口（代码单元格执行后触发）
│   ├── executeUserExpressions() → kernel.requestExecute({user_expressions})
│   ├── metadata['user_expressions'] → 结果持久化
│   └── IExpressionResult → ok/error 两种类型
│
├── 转换模块（transforms/）
│   ├── citations.ts → addCiteChildrenPlugin
│   ├── images.ts → imageUrlSourceTransform
│   └── links.tsx → internalLinksTransform + linkFactory
│
├── 自定义组件（components/ + renderers.tsx）
│   ├── InlineExpression → 内联表达式渲染
│   ├── listItem → 任务列表复选框
│   └── 自定义 renderers 覆盖默认
│
└── Python 端（jupyterlab_myst/）
    ├── __init__.py
    └── notary.py（Notebook 信任工具）
```

## 与 myst-execute/thebe 的关系

- **myst-execute** 在**构建时**执行整个 Notebook 的代码单元格，输出静态结果缓存到磁盘。生成的 HTML 不包含可交互性。
- **thebe** 在**运行时**（浏览器中）连接 Jupyter 内核执行代码，提供完全交互式体验，但需要后端服务器或 Pyodide。
- **jupyterlab-myst** 在 **JupyterLab IDE 内**增强 Markdown 单元格的渲染能力，将 MyST 语法（directives、roles、cross-references、inline expression）带入 Notebook 编辑体验。它不是独立的文档渲染方案，而是 JupyterLab 的增强扩展。

三者的定位：myst-execute 是静态站点构建工具，thebe 是浏览器运行时交互层，jupyterlab-myst 是 IDE 内的编辑增强层。
