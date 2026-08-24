---
type: bundle
title: "jupyterlab-myst JupyterLab 扩展"
okf_version: "0.2"
---

# jupyterlab-myst JupyterLab 扩展知识库

本知识包覆盖 [jupyterlab-myst](https://github.com/jupyter-book/jupyterlab-myst) 的完整知识体系——这是 Executable Book Project 开发的 JupyterLab 扩展，将 MyST Markdown 的增强语法（directives、交叉引用、脚注、内联表达式、任务列表等）带入 JupyterLab Notebook 和 Markdown Viewer 中。三个 JupyterFrontEndPlugin 协同工作：content-factory 替换默认 MarkdownCell、executor 监听代码执行触发 inline expression 求值、mime-renderer 注册 MyST Markdown 渲染工厂。所有内容均溯源至 TypeScript 源码（`src/` 目录）和 Python 包（`jupyterlab_myst/`），遵循 [OKF v0.2 规范](https://github.com/awesome-flexloop/awesome-okf)。

## 包信息

| 属性 | 值 |
|------|-----|
| npm 包名 | `jupyterlab-myst` |
| Python 包名 | `jupyterlab_myst` |
| JupyterLab 兼容性 | ^4.0.0 |
| 许可证 | MIT |
| 核心依赖 | @myst-theme/providers 1.3.0、myst-common 1.10.0、myst-parser、myst-to-react |
| 插件数量 | 3（content-factory、executor、mime-renderer） |

## 架构与插件（concepts/）

* [架构与插件系统](concepts/00-architecture-plugins.md) — 三个 JupyterFrontEndPlugin 的职责、JupyterLab 扩展点（IContentFactory、INotebookTracker、IRenderMimeRegistry）、插件间协作关系和 autoStart 机制。
* [MyST 解析与渲染管道](concepts/01-myst-rendering-pipeline.md) — 两阶段渲染（单单元格 fragment 解析 + 全局聚合）、myst-parser 配置、unified 转换管道（mathPlugin→enumerateTargets→resolveReferences→...）、linkTransformers（Wiki/GitHub/DOI/RRID）。
* [MySTMarkdownCell 生命周期](concepts/02-myst-markdown-cell.md) — 构造函数中的四个 HACK（替换 renderer、重建 ActivityMonitor、覆写回调）、编辑/渲染模式切换、ActivityMonitor 防抖机制、metadata 变更拦截、任务列表交互和 fragment 模式。

## 核心功能（concepts/）

* [Inline Expression 内联表达式执行](concepts/03-inline-expressions.md) — 利用 Jupyter 内核协议 user_expressions 字段的巧妙设计、executeRequest/Reply 流程、metadata 持久化（兼容 JL 3.6/4.x）、JupyterLab trust 安全模型、表达式结果的 MIME 渲染。
* [MySTWidget React 渲染系统](concepts/04-myst-widget-react.md) — VDomRenderer 桥接模式、MySTModel 可观察数据模型、六层 React Provider 嵌套链（TaskItem→Theme→Sanitizer→UserExpressions→TabState→Article）、自定义 renderers 和 linkFactory、RenderedMySTMarkdown MIME 渲染器。
* [支持的 MyST 语法与安全模型](concepts/05-syntax-security.md) — 注册的 directives（card/grid/proof/exercise/tab）、数学公式/脚注/交叉引用/自动链接、任务列表交互、frontmatter、JupyterLab trust 模型、ISanitizer HTML 清洗、safe 标记。

## 实战示例（examples/）

* [安装与基本使用](examples/01-using-jupyterlab-myst.md) — pip/conda 安装、在 Notebook 中使用任务列表/数学公式/directives、inline expression 基本用法、Markdown Viewer 支持和故障排除。
* [与 MyST 构建流程集成](examples/02-integrating-with-myst.md) — jupyterlab-myst（JupyterLab 编辑）+ myst-execute（构建时执行）的完整工作流、项目配置、构建过程、thebe 运行时交互部署和兼容性说明。
* [Inline Expression 高级工作流](examples/03-inline-expression-workflow.md) — 表达式类型（数值/字符串/复杂对象）、预格式化技巧、错误处理、刷新机制、MIME 类型支持、安全注意事项和常见陷阱，附带完整机器学习实验报告示例。

## 信源登记簿（references/）

* [插件入口与架构源码](references/plugin-entry-src.md) — src/index.ts 三个插件定义、MySTContentFactory 工厂类。
* [MySTMarkdownCell 与 MySTWidget 源码](references/cell-widget-src.md) — MySTMarkdownCell 类（构造函数 HACK、render 流程、ActivityMonitor、fragment 解析）、MySTWidget/MySTModel 类（VDomRenderer 桥接、Provider 嵌套、主题检测）。
* [MyST 解析管道源码](references/parse-pipeline-src.md) — src/myst.ts 中的 markdownParse/processArticleMDAST/processNotebookMDAST/renderNotebook、unified 插件管道顺序、transforms 模块（citations/images/links）。
* [Inline Expression 执行与 React 组件源码](references/execution-components-src.md) — executeUserExpressions/userExpressions metadata 操作、RenderedMySTMarkdown MIME 渲染器、components/（InlineExpression、listItem）和 providers/（UserExpressions、TaskItem、Sanitizer）。

## 学习路径建议

1. **快速上手**：examples/01-using-jupyterlab-myst.md → 安装并体验基本功能
2. **理解架构**：concepts/00-architecture-plugins.md → concepts/01-myst-rendering-pipeline.md
3. **核心功能**：concepts/02-myst-markdown-cell.md → concepts/03-inline-expressions.md
4. **React 渲染**：concepts/04-myst-widget-react.md
5. **构建集成**：examples/02-integrating-with-myst.md（结合 myst-execute）
6. **高级用法**：examples/03-inline-expression-workflow.md → concepts/05-syntax-security.md
7. **源码溯源**：阅读 references/ 中的信源文档

## 与 myst-execute/thebe 的关系

| 工具 | 阶段 | 位置 | 交互性 |
|------|------|------|--------|
| jupyterlab-myst | 编辑时 | JupyterLab IDE | ✅ 交互式（内核实时执行） |
| myst-execute | 构建时 | Node.js CLI | ❌ 静态输出 |
| thebe | 运行时 | 浏览器 | ✅ 交互式（Binder/直连/Lite） |

jupyterlab-myst 是 IDE 内的编辑增强工具，让作者在编写 Notebook 时享受 MyST Markdown 渲染和 inline expression 即时求值。myst-execute 是构建工具，生成静态 HTML。thebe 是前端运行时库，为静态 HTML 添加交互性。三者构成 MyST 可计算文档的完整工具链。

## 信任与生命周期说明

* **status 判定依据**：全部 15 个内容文档（6 个概念 + 3 个示例 + 4 个信源登记 + 2 个 spec 文档 + 根 index.md），非 index 文件均 `status: stable`。内容基于对 jupyterlab-myst 源码（`external/libs/ai/jupyter-book/jupyterlab-myst/src/`）的逐模块阅读与事实提取。
* **stale_after 解释**：统一设置为 `2027-12-31`。jupyterlab-myst 针对 JupyterLab 4.x 设计，核心 API（三个插件、MySTMarkdownCell、inline expression 的 user_expressions 机制）自 v2.0 以来保持稳定。如果 JupyterLab 5.x 发布可能需要适配，但核心概念和 MyST 语法支持不会有大变化。
* **核验链路**：`generated` 记录原始生成时刻（2026-08-23）；`verified: true`，所有类名、函数名、插件 ID、参数名均通过源码 Read 工具验证。

```{toctree}
:hidden:

concepts/index
examples/index
references/index
spec/facts
spec/insights
log
```
