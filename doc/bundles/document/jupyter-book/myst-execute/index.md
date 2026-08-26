---
type: bundle
title: "myst-execute 与 Thebe 交互式执行"
okf_version: "0.2"
---

# myst-execute + Thebe 交互式执行知识库

本知识包覆盖 [myst-execute](https://github.com/executablebooks/mystmd/tree/main/packages/myst-execute)（MyST 构建时 Notebook 执行插件）和 [Thebe](https://github.com/executablebooks/thebe)（浏览器端交互式代码执行库）的完整知识体系。myst-execute 负责静态构建时的代码执行与缓存，thebe（thebe-core / thebe-lite / thebe-react）负责运行时的交互式执行。两者共同为 MyST Markdown 文档提供从静态输出到交互式计算的完整代码执行链路。所有内容均溯源至源码（`mystmd/packages/myst-execute/src/`、`thebe/packages/core/src/`、`thebe/packages/lite/src/`、`thebe/packages/react/src/`），遵循 [OKF v0.2 规范](https://github.com/awesome-flexloop/awesome-okf)。

## 包信息

| 包 | 版本 | 许可证 | npm 包名 | 用途 |
|---|---|---|---|---|
| myst-execute | 0.4.0 | MIT | `myst-execute` | 构建时 Notebook 执行插件 |
| thebe-core | (latest) | MIT | `thebe-core` | 浏览器端核心执行引擎 |
| thebe-lite | (latest) | MIT | `thebe-lite` | Pyodide/JupyterLite 无服务器支持 |
| thebe-react | (latest) | MIT | `thebe-react` | React Hooks 和 Provider |

## 架构总览（concepts/）

* [执行架构：构建时 vs 运行时](concepts/00-execution-architecture.md) — myst-execute 构建时执行与 thebe 运行时交互的双模式架构、数据流对比、插件集成点和适用场景。
* [myst-execute 内核管理](concepts/01-myst-execute-kernel.md) — Jupyter 内核连接创建（KernelManager→KernelConnection）、代码单元执行（executeCodeCell）、内联表达式求值（evaluateInlineExpression）、可执行节点发现与错误处理。
* [执行缓存与输出转换](concepts/02-execution-cache.md) — ICache<T> 接口、LocalDiskCache、LegacyExecutionCache（旧格式兼容）、NotebookExecutionCache（ipynb 格式存储）、TieredExecutionCache（分层缓存）、MD5 缓存键计算和缓存失效条件。

## Thebe 运行时（concepts/）

* [Thebe 核心 API](concepts/03-thebe-core-api.md) — Config→ThebeServer→ThebeSession→ThebeNotebook→ThebeCodeCell 对象层次、链式 API、服务器状态管理、RenderMime 注册表、事件系统、UMD/ESM 入口点。
* [Thebe 配置选项](concepts/04-thebe-configuration.md) — CoreOptions 五组子配置（MathJax/Binder/Kernel/ServerSettings/SavedSessions）、各选项含义、默认值和三种连接模式的配置示例。
* [Binder 与 Jupyter 服务器连接](concepts/05-thebe-binder.md) — BinderHub SSE 事件流、构建阶段（waiting/building/pushing/launching/ready）、saved sessions localStorage 持久化、直连 Jupyter Server 流程、REST API 和静态状态检查。
* [Thebe Lite：Pyodide 无服务器执行](concepts/06-thebe-lite-pyodide.md) — JupyterLite + Pyodide WASM 架构、startJupyterLiteServer 函数、内存 ServiceManager、浏览器内核限制、包安装方式。
* [Thebe React：声明式集成](concepts/07-thebe-react.md) — 四层 Provider 嵌套（BundleLoader→RenderMime→Server→Session）、useThebeServer/useThebeSession Hooks、useNotebook/useNotebookFromSource Notebook 管理 Hook、cellRefs DOM 挂载机制。

## 实战示例（examples/）

* [构建时 Notebook 执行配置](examples/01-configure-notebook-execution.md) — myst.yml 项目配置、frontmatter 文档配置、代码块标签（raises-exception/label）、内联表达式 `{eval}`、缓存控制、超时配置、环境变量依赖和 CI/CD 集成。
* [Thebe 交互式代码执行](examples/02-thebe-interactive.md) — 纯 HTML/JS（UMD）+ Binder、ES Module + 本地 Jupyter、React Provider 三种集成方式，状态监听、错误处理和资源清理。
* [Thebe Lite：浏览器内 Pyodide 执行](examples/03-thebe-lite.md) — 无后端 Pyodide 执行的完整 HTML 示例和 React 组件、第三方包安装（%pip/piplite）、预装包列表、内存限制和三种模式对比。

## 信源登记簿（references/）

* [myst-execute 源码索引](references/myst-execute-src.md) — `myst-execute/src/` 目录结构、核心文件（execute.ts、kernel.ts、cache.ts、transform.ts、index.ts）、导出 API 和关键依赖。
* [thebe-core 源码索引](references/thebe-core-src.md) — `thebe-core/src/` 目录结构、ThebeServer/ThebeSession/ThebeNotebook/ThebeCodeCell 核心类、Config 配置系统、事件系统、入口点挂载。
* [thebe-lite 源码索引](references/thebe-lite-src.md) — `thebe-lite/src/` 目录结构、startJupyterLiteServer 函数、JupyterLite Server 初始化、Pyodide 内核集成、service-worker 注册。
* [thebe-react 源码索引](references/thebe-react-src.md) — `thebe-react/src/` 目录结构、四个 Context Provider（BundleLoader/Server/Session/RenderMime）、Notebook Hooks、OutputAreaByRef 组件。

## 学习路径建议

1. **理解架构**：00-execution-architecture → 了解构建时和运行时两种执行模式的区别
2. **构建时执行**：01-myst-execute-kernel → 02-execution-cache → 运行 examples/01-configure-notebook-execution.md
3. **运行时交互（Binder 模式）**：03-thebe-core-api → 04-thebe-configuration → 05-thebe-binder → 运行 examples/02-thebe-interactive.md
4. **无服务器模式**：06-thebe-lite-pyodide → 运行 examples/03-thebe-lite.md
5. **React 开发**：07-thebe-react → 结合 examples/02 或 03 中的 React 组件示例
6. **源码溯源**：阅读 references/ 中的信源文档，理解各模块的底层实现

## 信任与生命周期说明

* **status 判定依据**：全部 17 个内容文档（8 个概念 + 3 个示例 + 4 个信源登记 + 2 个 spec 文档 + 根 index.md），非 index 文件均 `status: stable`。内容基于对 myst-execute 0.4.0 源码（`external/libs/ai/jupyter-book/mystmd/packages/myst-execute/src/`）和 thebe 源码（`external/libs/ai/jupyter-book/thebe/packages/`）的逐模块阅读与事实提取。
* **stale_after 解释**：统一设置为 `2027-12-31`。myst-execute 作为 MyST 构建插件核心 API 自 0.1 以来保持稳定；thebe-core 的链式 API（Config→Server→Session→Notebook→Cell）自 thebe v0.5+ 定型；thebe-react 的 Provider/Hook 模式也已稳定。该日期作为对未来大版本变化的保守重新评估节点。
* **核验链路**：`generated` 记录原始生成时刻（2026-08-23）；`verified: true`，所有类名、函数名、参数名均通过源码 Read 工具验证。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
spec/facts
spec/insights
log
```
