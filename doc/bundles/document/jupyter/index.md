---
okf_version: "0.2"
type: group
title: "📓 Jupyter 数据科学生态"
description: "Jupyter 交互式计算生态——协议、格式、应用与部署"
total_bundles: 56
---

# 📓 Jupyter 数据科学生态

Jupyter 是数据科学与交互式计算的核心平台，从底层的 ZeroMQ 通信协议到顶层的 Docker 部署镜像与自动化运维工具，形成完整的技术栈。本组按 **协议层 → 格式层 → 应用层 → 部署层 → 自动化层** 的架构层次组织。

## 学习路径

### 入口层：元包与生态总览

| 顺序 | 知识束 | 一句话简介 |
|------|--------|-----------|
| 0 | [jupyter](jupyter/index.md) | Jupyter 元包——一站式安装入口（notebook/jupyterlab/nbconvert/ipykernel/ipywidgets）、配置系统、目录规范、Kernel 架构、.ipynb 文件格式、C/S 通信模型、ipywidgets 交互控件、nbconvert 转换、JupyterHub 多用户部署（v1.2.0.dev0） |

### 协议层：内核通信基础

| 顺序 | 知识束 | 一句话简介 |
|------|--------|-----------|
| 1 | [jupyter-client](jupyter-client/README.md) | Jupyter 协议客户端——ZMQ 五通道通信（Shell/IO/Stdin/Control/HB）、内核生命周期管理、会话与消息签名、KernelManager/AsyncKernelManager、多内核并行（v8.9.1，协议 v5.4） |

### 服务层：后端核心服务

| 顺序 | 知识束 | 一句话简介 |
|------|--------|-----------|
| 22 | [jupyter_server](jupyter_server/index.md) | Jupyter 后端核心服务——Tornado HTTP 服务器、REST/WebSocket API、认证授权（IdentityProvider/Authorizer）、ContentsManager 文件管理、MappingKernelManager 多内核管理、ExtensionApp 扩展系统、Gateway 远程内核代理、异步编程模型（v2.21.0.dev0） |
| 0 | [jupyter-core](jupyter-core/index.md) | Jupyter 生态核心基础库——跨平台路径管理、jupyter 命令行调度器、JupyterApp 应用基类、traitlets 配置、异步桥接工具（v5.9.1） |

### 格式层：数据模型

| 顺序 | 知识束 | 一句话简介 |
|------|--------|-----------|
| 2 | [nbformat](nbformat/index.md) | Notebook 文件格式——NotebookNode 数据模型、v4 JSON 格式、读写 API、验证器、信任签名机制、版本迁移 |

### 应用层：用户交互与工具

| 顺序 | 知识束 | 一句话简介 |
|------|--------|-----------|
| 3 | [jupyter-notebook](jupyter-notebook/index.md) | Jupyter Notebook v7——基于 JupyterLab 的后端 App、前端 Shell、Handler 体系、Shim 兼容层、前后端扩展系统 |
| 24 | [jupyterlab](jupyterlab/index.md) | JupyterLab 下一代交互式IDE——Lumino+React+TypeScript前端、Tornado/Python后端、插件化架构（Token依赖注入）、LabShell八区域布局、DocumentRegistry文档工厂模式、ServiceManager服务聚合、Notebook/Cell三层Widget、Federated扩展生态、Core/Dev/App三运行模式（v4.x） |
| 12 | [jupyterlab-desktop](jupyterlab-desktop/index.md) | JupyterLab 官方跨平台桌面应用（Electron）——内置Python环境管理、多窗口多会话、Jupyter Server自动启停、Factory预创建服务器、双层设置系统、CLI命令行工具、三层导航安全架构（v4.6.x） |
| 25 | [jupyter-ai](jupyter-ai/index.md) | Jupyter AI 官方AI助手扩展——ACP+MCP双协议架构、多Agent支持（Claude/Codex/Copilot/Goose/Kiro等）、Jupyternaut默认Persona、聊天界面与Magic Commands双模式、Notebook AI工具集、实时协作、安全护栏、自定义MCP服务器与Persona扩展（v3.1.x） |
| 29 | [jupyterlite-ai](jupyterlite-ai/index.md) | JupyterLite AI 浏览器端AI扩展——基于Vercel AI SDK的ToolLoopAgent引擎、Lumino Token DI架构、5大内置Provider（OpenAI/Anthropic/Google/Mistral/Generic）、工具调用与审批机制、MCP协议集成、Persona人设系统、JupyterLite纯浏览器WASM环境支持（v0.19.0） |
| 13 | [lumino](lumino/index.md) | Lumino 桌面级Web UI工具集——Widget组件模型、MessageLoop消息循环、Signal类型安全事件、Layout布局引擎（DockPanel/BoxPanel/TabPanel）、CommandRegistry命令/快捷键、VirtualDOM虚拟DOM、Application插件化应用框架、DataGrid高性能Canvas表格，是JupyterLab的核心前端基础（v2026.7.3） |
| 9 | [nbconvert](nbconvert/index.md) | Notebook格式转换工具——六阶段转换管线(Exporter→Preprocessor→Filter→Template→Writer→Postprocessor)、HTML/PDF/Markdown/脚本多格式输出、单元格标签控制、papermill参数化报告、自定义Exporter开发 |
| 15 | [jupyterlab-github](jupyterlab-github/index.md) | JupyterLab GitHub浏览器扩展——通过Contents.IDrive接口将GitHub仓库映射为只读虚拟文件系统，双模式请求（直连/代理），支持大文件Blob降级、MyBinder一键启动、GitHub Enterprise部署，TypeScript+Python双组件架构（v4.0.0） |
| 16 | [plugin-playground](plugin-playground/index.md) | JupyterLab 插件快速原型工具——浏览器端TypeScript即时转译、AsyncFunction沙箱执行、Proxy驱动Token依赖注入、CSS快照-提交-回滚事务、四级模块解析链（已知模块→联邦扩展→本地文件→CDN RequireJS），无需构建即可实时编写和测试JupyterLab插件 |
| 17 | [jupyterlab-latex](jupyterlab-latex/index.md) | JupyterLab LaTeX 编辑扩展——为 .tex 文件提供实时编译预览、双向SyncTeX导航、富编辑工具栏，后端Tornado调度LaTeX编译（xelatex/pdflatex/lualatex/tectonic多引擎+BibTeX自动检测），前端pdfjs-dist渲染PDF+Shift+Ctrl/Cmd+Click反向同步，TypeScript+Python双插件架构（v4.4.0） |
| 18 | [jupyter-renderers](jupyter-renderers/index.md) | JupyterLab 官方MIME渲染器扩展集合——FASTA生物序列(MSA)、GeoJSON地理数据(Leaflet)、KaTeX/MathJax2数学公式、Vega/Vega-Lite可视化五个预构建扩展，Lerna monorepo管理，MIME渲染器四要素模式与ILatexTypesetter服务模式，hatch-jupyter-builder Python wheel打包 |
| 31 | [anywidget](anywidget/index.md) | 自定义Jupyter Widget工具包——ESM零构建前端协议、AnyWidget基类(ipywidgets.DOMWidget)、WidgetTrait双观察者同步、Comm消息通道、Custom Messages自定义消息、HMR热更新(SolidJS响应式+Vite插件)、React/Svelte/Vue多框架桥接、descriptor.py零依赖traitlets替代方案，Python/JS双包架构 |
| 10 | [try-jupyter](try-jupyter/index.md) | JupyterLite浏览器端体验站点——基于Pyodide+Xeus双内核(WASM)、零安装Python/C++/R/SQLite环境、Pixi构建管线、GitHub Pages部署、Playwright E2E测试 |
| 23 | [echo-kernel](echo-kernel/index.md) | JupyterLite最小示例内核——Echo Kernel回显内核（约150行核心代码），BaseKernel模板方法模式、JupyterFrontEndPlugin插件注册、TypeScript+hatchling双构建系统，自定义JupyterLite内核开发最佳入门模板（v0.4.0） |
| 26 | [pyodide-kernel](pyodide-kernel/index.md) | JupyterLite Pyodide Python内核——基于Pyodide WASM在浏览器运行CPython 3.12，双层架构（构建Addon+运行时WASM）、Comlink/Coincident双Worker模式、piplite三级包管理、IPython三层兼容适配（Mock→Patch→Subclass）、跨边界消息桥接（v0.9.0a1，Pyodide v0.29.3） |
| 27 | [terminal](terminal/index.md) | JupyterLite浏览器端终端扩展——六插件架构替换JupyterLab TerminalManager、mock-socket WebSocket桥接、cockle WASM shell、Coincident(SAB)/Comlink(SW)双Worker通信模式、HeadlessShellPool编程式命令池、DriveFS文件系统挂载、主题自动同步（v1.7.0-a0） |
| 30 | [cockle](cockle/index.md) | Cockle 浏览器内 bash-like Shell——三层Shell架构(Shell/BaseShellWorker/ShellImpl)、四类命令(Builtin/WASM/JS/External)、Tokenizer+Parser解析管线、SharedArrayBuffer/Service Worker双路同步stdin、Emscripten MEMFS+PROXYFS虚拟文件系统、Comlink/Coincident双Worker通信模式（v1.8.0-a0） |
| 19 | [ui-profiler](ui-profiler/index.md) | JupyterLab UI性能基准测试扩展——Benchmark×Scenario N×M测量矩阵、6种测量方法(Execution Time/CSS Stylesheets/Rules/Groups/Usage/JS Self-Profiling)、10种内置场景、减法式CSS性能分析、MutationObserver/ResizeObserver驱动的Dramaturg自动化层、IQR鲁棒统计、火焰图可视化，支持自定义Benchmark/Scenario扩展 |
| 20 | [jupyter-collaboration](jupyter-collaboration/index.md) | Jupyter实时协作扩展——基于Yjs CRDT的多用户同时编辑、WebSocket实时同步、Awareness用户感知（光标/选区/在线状态）、SQLiteYStore CRDT持久化、外带变更检测、文档Fork分叉与时间线版本导航、RtcContentProvider透明替换JupyterLab内容提供者、Jupyter Events事件系统（v5.0.0） |
| 21 | [jupyterlab-webrtc-docprovider](jupyterlab-webrtc-docprovider/index.md) | JupyterLab P2P实时协作扩展——基于WebRTC DataChannel+y-webrtc实现浏览器直连文档同步，无需中心协作服务器，4插件架构(core/factory/status/retro-status)、SHA256房间ID隐私保护、三级配置优先级、SimplePeer分块补丁、BroadcastChannel同浏览器标签页发现，支持JupyterLab/JupyterLite/RetroLab（v0.2.0） |

### 部署层：容器化运行与静态部署

| 顺序 | 知识束 | 一句话简介 |
|------|--------|-----------|
| 4 | [jupyter-docker-stacks](jupyter-docker-stacks/index.md) | Jupyter 官方 Docker 镜像——镜像层级体系（base→minimal→scipy→专业栈）、启动生命周期、Hook 自定义、用户权限、GPU 支持、CI/CD 构建 |
| 5 | [cookiecutter-docker-stacks](cookiecutter-docker-stacks/index.md) | Jupyter Docker 镜像模板生成器——一键生成包含 Dockerfile/pytest测试/CI/CD/DevContainer 的自定义镜像项目，14个基础镜像预设、TrackedContainer测试框架、GitHub Actions自动发布 |
| 28 | [xeus-lite-demo](xeus-lite-demo/index.md) | JupyterLite xeus 内核部署模板——GitHub Template 一键创建 JupyterLite 站点、双环境模型（构建环境vs WASM运行时）、多语言内核（Python/R/C++）、conda 包管理（emscripten-forge）、GitHub Actions 自动部署到 GitHub Pages |

### 自动化层：社区运营工具

| 顺序 | 知识束 | 一句话简介 |
|------|--------|-----------|
| 6 | [pr-triage-board-bot](pr-triage-board-bot/index.md) | PR分类看板机器人——基于GitHub App和Project V2 GraphQL API，按7个维度（作者类型/变更规模/CI状态/审批状态/合并冲突/维护者参与度/创建时间）自动分类同步开放PR，每小时对账更新，TypeScript实现 |
| 14 | [jupyterlab-probot](jupyterlab-probot/index.md) | JupyterLab 社区维护 Probot 应用——四大核心功能：Issue/PR自动分类标签、Binder链接自动评论、CI重复Workflow自动取消、评论命令`@jupyterlab-probot please restart ci`触发CI重跑，基于Probot ^12.3.1框架+AJV配置校验，单文件TypeScript实现（~248行） |

### 治理层：社区治理与决策机制

| 顺序 | 知识束 | 一句话简介 |
|------|--------|-----------|
| 7 | [governance](governance/index.md) | Jupyter 治理模型——EC/SSC/Foundation三主体架构、共识寻求+投票兜底决策流程、子项目自治体系、常设委员会与工作组（DEI/CoC/社区建设）、排序复选选举机制、商标许可与行为准则（2022年BDFL转型后模式） |
| 11 | [frontends-team-compass](frontends-team-compass/index.md) | Jupyter Frontends 团队罗盘——Frontends Council三层成员体系（Member/Release/Admin）、周三Frontends+周二Triage双周会、on/off-record录制分段、HackMD→GitHub Issue归档、成员半年活跃确认、PR合并5原则、扩展4步贡献流程、Sphinx+MyST文档构建、2020用户调查方法论 |

### 文档工具层：文档生成与渲染

| 顺序 | 知识束 | 一句话简介 |
|------|--------|-----------|
| 8 | [papyri](papyri/index.md) | Python docstring→IR文档生成器——RST解析为类型化中间表示（IR），三端架构（Python gen/TypeScript ingest/Astro viewer），跨包交叉引用，CBOR确定性打包，交互式文档浏览，支持NumPy/SciPy等科学计算库（Python 3.13+） |

```{toctree}
:hidden:

jupyter/index
jupyter_server/index
jupyter-core/index
nbformat/index
jupyter-notebook/index
jupyterlab/index
jupyterlab-desktop/index
jupyter-ai/index
jupyterlite-ai/index
lumino/index
nbconvert/index
jupyterlab-github/index
plugin-playground/index
jupyterlab-latex/index
jupyter-renderers/index
anywidget/index
try-jupyter/index
echo-kernel/index
pyodide-kernel/index
terminal/index
cockle/index
ui-profiler/index
jupyter-collaboration/index
jupyterlab-webrtc-docprovider/index
jupyter-docker-stacks/index
cookiecutter-docker-stacks/index
xeus-lite-demo/index
pr-triage-board-bot/index
jupyterlab-probot/index
governance/index
frontends-team-compass/index
papyri/index
binderhub/index
enterprise-gateway/index
extension-cookiecutter/index
extension-template/index
fps/index
ipython/index
javascript-kernel/index
jupyter-chat/index
jupyter-resource-usage/index
jupyter-scheduler/index
jupyter-server-terminals/index
jupyter_releaser/index
jupyter_server_fileid/index
jupyterhub/index
jupyterlab-demo/index
jupyterlab-git/index
jupyterlab-pygments/index
jupyterlab-translate/index
jupyterlab_server/index
jupyterlite/index
jupyterlite-demo/index
jupyterlite-lsp/index
jupyterlite-sphinx/index
jupyverse/index
language-packs/index
litegitpuller/index
nbviewer/index
p5-kernel/index
pytest-jupyter/index
repo2jupyterlite/index
sphinx-demo/index
surveys/index
team-compass/index
the-littlest-jupyterhub/index
xeus/index
extension-examples/index
jupyter-client/index
```
