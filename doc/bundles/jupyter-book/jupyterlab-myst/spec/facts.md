---
type: facts
bundle: jupyterlab-myst
version: "4.0.0"
generated: 2026-08-23
sources:
  - d:\spaces\SpecWeave\external\libs\ai\jupyter-book\jupyterlab-myst\package.json
  - d:\spaces\SpecWeave\external\libs\ai\jupyter-book\jupyterlab-myst\src\index.ts
  - d:\spaces\SpecWeave\external\libs\ai\jupyter-book\jupyterlab-myst\src\MySTMarkdownCell.tsx
  - d:\spaces\SpecWeave\external\libs\ai\jupyter-book\jupyterlab-myst\src\widget.tsx
  - d:\spaces\SpecWeave\external\libs\ai\jupyter-book\jupyterlab-myst\src\myst.ts
  - d:\spaces\SpecWeave\external\libs\ai\jupyter-book\jupyterlab-myst\src\actions.ts
  - d:\spaces\SpecWeave\external\libs\ai\jupyter-book\jupyterlab-myst\src\mime.tsx
  - d:\spaces\SpecWeave\external\libs\ai\jupyter-book\jupyterlab-myst\src\userExpressions.ts
  - d:\spaces\SpecWeave\external\libs\ai\jupyter-book\jupyterlab-myst\src\MySTContentFactory.ts
  - d:\spaces\SpecWeave\external\libs\ai\jupyter-book\jupyterlab-myst\src\renderers.tsx
  - d:\spaces\SpecWeave\external\libs\ai\jupyter-book\jupyterlab-myst\jupyterlab_myst\__init__.py
  - d:\spaces\SpecWeave\external\libs\ai\jupyter-book\jupyterlab-myst\jupyterlab_myst\notary.py
---

# jupyterlab-myst 事实清单

## 包元数据

- F-001：jupyterlab-myst 是 Executable Book Project 开发的 JupyterLab 扩展，npm 包名为 `jupyterlab-myst`，版本依赖 JupyterLab ^4.0.0。
- F-002：许可证为 MIT（源码仓库 LICENSE 文件），Python 包名为 `jupyterlab_myst`。
- F-003：前端扩展导出三个 JupyterFrontEndPlugin：`jupyterlab-myst:content-factory`、`jupyterlab-myst:executor`、`jupyterlab-myst:mime-renderer`。

## 三个插件

- F-004：`jupyterlab-myst:content-factory` 插件提供 `NotebookPanel.IContentFactory`，创建自定义的 `MySTContentFactory`，替代默认 MarkdownCell 为 MySTMarkdownCell。
- F-005：`jupyterlab-myst:executor` 插件监听 `NotebookActions.executed` 信号，当代码单元格执行完成后调用 `notebookCellExecuted()` 函数处理 Markdown 单元格中的 inline expression。
- F-006：`jupyterlab-myst:mime-renderer` 插件向 `IRenderMimeRegistry` 注册 MyST markdown 渲染工厂（`mystMarkdownRendererFactory`），MIME 类型为 `text/markdown`，默认 rank 为 50，标记为 safe。
- F-007：mime-renderer 插件可选依赖 `IMarkdownViewerTracker`（确保内置 Markdown 渲染器先注册）和 `ISettingRegistry`（自动设置 hideFrontMatter=false）。

## MySTMarkdownCell

- F-008：MySTMarkdownCell 继承自 JupyterLab 的 `MarkdownCell` 类，实现 `IMySTMarkdownCell` 接口，是 jupyterlab-myst 的核心 UI 组件。
- F-009：MySTMarkdownCell 在构造函数中创建 `MySTModel` 和 `MySTWidget`（MyST React 渲染器），替换默认的 Markdown renderer。
- F-010：MySTMarkdownCell 使用 AttachmentsResolver 处理单元格附件（图片等），resolver 链向 notebook rendermime 的 resolver。
- F-011：MySTMarkdownCell 创建自定义 ActivityMonitor（timeout=100ms），通过 `_metadataJustChanged` 标志位实现 metadata-only 变更时跳过渲染（防止 inline expression 结果更新触发不必要的重渲染）。
- F-012：MySTMarkdownCell 监听 model 的 trusted 变化（`onModelTrustedChanged`），同步更新 MySTWidget 的 trusted 属性并从 metadata 恢复 expressions。
- F-013：`fragmentMDAST` 属性存储该单元格单独解析的 MDAST（调用 `updateFragmentMDAST()` 生成），供 notebook 级聚合使用。
- F-014：`render()` 方法先调用 `updateFragmentMDAST()` 解析本单元格 Markdown，再调用 `renderNotebook(parent)` 对整个 notebook 的所有 MyST markdown cells 做全局 MDAST 处理（跨单元格引用解析），最后等待 MySTWidget 渲染完成后挂载到 inputArea。

## MySTWidget

- F-015：MySTWidget 继承自 VDomRenderer<IMySTModel>，是 MyST 内容的 React 渲染容器，使用 Lumino VDom 模式。
- F-016：MySTModel 继承自 VDomModel，实现 IMySTModel 接口，包含四个可观察属性：`references`（引用解析结果）、`mdast`（处理后的 MDAST 节点）、`expressions`（inline expression 执行结果）、`frontmatter`（文档 frontmatter）。
- F-017：MySTWidget.render() 使用多层 React Provider 嵌套：TaskItemControllerProvider → ThemeProvider → SanitizerProvider → UserExpressionsProvider → TabStateProvider → ArticleProvider → MyST 组件。
- F-018：MySTWidget 通过 `document.body.dataset.jpThemeLight` 检测 JupyterLab 主题（light/dark），传入 ThemeProvider。
- F-019：MySTWidget 使用 `FrontmatterBlock`（来自 @myst-theme/frontmatter）渲染文档 frontmatter（仅第一个单元格包含 frontmatter）。
- F-020：MySTWidget 通过 `<MyST ast={mdast}>` 组件（来自 myst-to-react）渲染 MDAST 树。
- F-021：MySTWidget 暴露 `taskItemChanged` 信号（ISignal），当用户点击复选框时触发，回调中更新单元格 Markdown 源码中的 `[ ]` / `[x]`。

## MyST 解析管道（myst.ts）

- F-022：`markdownParse(text)` 使用 myst-parser 的 `mystParse()` 解析 MyST Markdown，启用 linkify，注册 directives：cardDirective、gridDirectives、proofDirective、exerciseDirectives、tabDirectives。
- F-023：`markdownParse()` 只运行 `basicTransformationsPlugin`（基础转换），不做引用解析和链接处理。
- F-024：`processArticleMDAST(mdast, resolver)` 处理独立 Markdown 文件（Markdown Viewer 场景），运行完整转换管道：mathPlugin → glossaryPlugin → abbreviationPlugin → enumerateTargetsPlugin → linksPlugin → footnotesPlugin → resolveReferencesPlugin → addCiteChildrenPlugin → keysPlugin → internalLinksTransform → imageUrlSourceTransform → reconstructHtmlTransform。
- F-025：`processNotebookMDAST(mdast, resolver)` 处理 Notebook 场景，管道与 processArticleMDAST 相同，但 frontmatter 从第一个子节点提取（因为 Notebook 的 MDAST 是各单元格 fragment 拼接的 root）。
- F-026：`buildNotebookMDAST(mystCells)` 将多个单元格的 fragmentMDAST（每个设为 type:'block'）拼接为一个 root 节点：`{ type: 'root', children: blocks }`。
- F-027：`renderNotebook(notebook)` 收集所有已渲染的 MySTMarkdownCell，聚合它们的 fragmentMDAST，调用 `processNotebookMDAST()` 做全局处理，然后将处理后的 MDAST 分片（按 index）分配回各单元格的 MySTModel。
- F-028：linkTransforms 包含四个外部链接转换器：WikiTransformer（维基链接）、GithubTransformer（GitHub 引用）、DOITransformer（DOI 链接）、RRIDTransformer（研究资源标识符）。
- F-029：`processCellMDAST(resolver, mdast)` 仅对单个单元格做图片 URL 转换（imageUrlSourceTransform），用于 placeholder 状态下的 fragment 更新。

## Inline Expression（内联表达式执行）

- F-030：inline expression 是 MyST Markdown 中的特殊节点类型 `inlineExpression`，其 value 属性为 Python 表达式文本。
- F-031：`executeUserExpressions(cell, sessionContext)` 从单元格 MDAST 中通过 `selectAll('inlineExpression', mdast)` 提取所有表达式，使用 Jupyter 内核的 `kernel.requestExecute({ code: '', user_expressions: {...} })` 请求执行。
- F-032：Jupyter 内核协议中 `user_expressions` 字段允许在 execute_request 中传递命名字典，内核执行完 code 后会对这些表达式求值并在 reply 中返回结果。jupyterlab-myst 将空 code + 编号的 user_expressions 发送，避免执行任意代码单元。
- F-033：内核返回的 user_expressions 结果有两种状态：`status: 'ok'`（含 data/metadata）和 `status: 'error'`（含 traceback/ename/evalue）。
- F-034：表达式执行结果存储在单元格 metadata 的 `user_expressions` 字段（metadataSection = 'user_expressions'），类型为 `IUserExpressionMetadata[]`，每项包含 `expression`（原始表达式字符串）和 `result`（IExpressionResult）。
- F-035：`notebookCellExecuted(notebook, cell, tracker)` 在代码单元格执行后触发：查找对应的 NotebookPanel → 获取 SessionContext → 更新 fragmentMDAST → 调用 executeUserExpressions → 将结果存入 metadata → 设置 cell.model.trusted = true。
- F-036：只有受信任的单元格（trusted=true）才会显示 inline expression 的执行结果。MySTMarkdownCell 在 metadata 变化时通过 `restoreExpressionsFromMetadata()` 恢复 expressions 到 MySTModel。
- F-037：`getUserExpressions(cell)` 和 `setUserExpressions(cell, expressions)` 兼容 JupyterLab 3.6 和 4.x 两种 metadata API（model.metadata.get/set vs model.getMetadata/setMetadata）。

## RenderedMySTMarkdown（MIME 渲染器）

- F-038：RenderedMySTMarkdown 继承自 MySTWidget，实现 IRenderMime.IRenderer 接口，用于 Markdown Viewer 中的独立 .md 文件渲染。
- F-039：RenderedMySTMarkdown.renderModel(model) 从 MIME model 的 data['text/markdown'] 获取 Markdown 文本，调用 markdownParse → processArticleMDAST，创建新 MySTModel 并赋值给 this.model。
- F-040：mystMarkdownRendererFactory 的配置为 `safe: true, mimeTypes: ['text/markdown'], defaultRank: 50`，这意味着它会替代 JupyterLab 内置的 Markdown 渲染器。

## React 组件与 Provider

- F-041：InlineExpression 组件（components/inlineExpression.tsx）渲染内联表达式结果，使用 UserExpressionsProvider 中的 rendermime 创建输出渲染器，仅在 trusted=true 时显示结果。
- F-042：TaskItemControllerProvider（providers/taskItem.tsx）提供复选框交互能力，通过 controller 回调通知 MySTWidget 更新单元格源码。
- F-043：SanitizerProvider（providers/sanitizer.tsx）将 JupyterLab 的 ISanitizer 注入 React 上下文。
- F-044：renderers.tsx 注册自定义渲染器（覆盖默认的 listItem 等），用于处理任务列表项（- [ ] / - [x]）和内联表达式。
- F-045：linkFactory 函数（transforms/links.tsx）创建自定义 Link 组件，使用 JupyterLab 的 ILinkHandler 处理内部链接导航。

## Python 端

- F-046：Python 包 jupyterlab_myst 包含 `__init__.py`（扩展入口）和 `notary.py`（Notebook 信任相关工具）。
- F-047：jupyter-server 配置位于 `jupyter-config/server-config/jupyterlab_myst.json`，nb-config 位于 `jupyter-config/nb-config/jupyterlab_myst.json`。
- F-048：notary.py 提供 MySTNotebookNotary 类，可能用于标记包含 inline expression 的 Notebook 为受信任。

## 样式

- F-049：样式文件位于 style/ 目录，包含 base.css、index.css、links.css、preflight.css、tailwind.css、jupyterlab-typography.css，通过 style/index.js 导出。
- F-050：使用 Tailwind CSS（tailwind.config.js），并引入 jupyterlab-typography.css 与 JupyterLab 主题系统协调。

## 转换模块（transforms/）

- F-051：citations.ts（addCiteChildrenPlugin）为 citation 节点添加子节点。
- F-052：images.ts（imageUrlSourceTransform）处理图片 URL，通过 JupyterLab resolver 解析相对路径和附件。
- F-053：links.tsx（internalLinksTransform）处理内部链接转换，linkFactory 创建自定义 Link 组件适配 JupyterLab 导航。

## 支持的 MyST 语法特性

- F-054：通过注册的 directives 支持：card（卡片）、grid（网格布局）、proof（证明/定理环境）、exercise（练习）、tab（标签页）。
- F-055：支持 inline expression（内联 Python 表达式执行）、任务列表（- [ ] checkbox）、frontmatter（YAML 元数据块）、脚注、引用、数学公式（MathJax/KaTeX）、缩写词、术语表、DOI/RRID/GitHub/Wiki 自动链接。
