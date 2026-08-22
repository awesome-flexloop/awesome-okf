---
okf_version: "0.2"
type: group
title: "📓 Jupyter 数据科学生态"
description: "Jupyter 交互式计算生态——协议、格式、应用与部署"
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

### 格式层：数据模型

| 顺序 | 知识束 | 一句话简介 |
|------|--------|-----------|
| 2 | [nbformat](nbformat/index.md) | Notebook 文件格式——NotebookNode 数据模型、v4 JSON 格式、读写 API、验证器、信任签名机制、版本迁移 |

### 应用层：用户交互与工具

| 顺序 | 知识束 | 一句话简介 |
|------|--------|-----------|
| 3 | [jupyter-notebook](jupyter-notebook/index.md) | Jupyter Notebook v7——基于 JupyterLab 的后端 App、前端 Shell、Handler 体系、Shim 兼容层、前后端扩展系统 |
| 12 | [jupyterlab-desktop](jupyterlab-desktop/index.md) | JupyterLab 官方跨平台桌面应用（Electron）——内置Python环境管理、多窗口多会话、Jupyter Server自动启停、Factory预创建服务器、双层设置系统、CLI命令行工具、三层导航安全架构（v4.6.x） |
| 13 | [lumino](lumino/index.md) | Lumino 桌面级Web UI工具集——Widget组件模型、MessageLoop消息循环、Signal类型安全事件、Layout布局引擎（DockPanel/BoxPanel/TabPanel）、CommandRegistry命令/快捷键、VirtualDOM虚拟DOM、Application插件化应用框架、DataGrid高性能Canvas表格，是JupyterLab的核心前端基础（v2026.7.3） |
| 9 | [nbconvert](nbconvert/index.md) | Notebook格式转换工具——六阶段转换管线(Exporter→Preprocessor→Filter→Template→Writer→Postprocessor)、HTML/PDF/Markdown/脚本多格式输出、单元格标签控制、papermill参数化报告、自定义Exporter开发 |
| 15 | [jupyterlab-github](jupyterlab-github/index.md) | JupyterLab GitHub浏览器扩展——通过Contents.IDrive接口将GitHub仓库映射为只读虚拟文件系统，双模式请求（直连/代理），支持大文件Blob降级、MyBinder一键启动、GitHub Enterprise部署，TypeScript+Python双组件架构（v4.0.0） |
| 16 | [plugin-playground](plugin-playground/index.md) | JupyterLab 插件快速原型工具——浏览器端TypeScript即时转译、AsyncFunction沙箱执行、Proxy驱动Token依赖注入、CSS快照-提交-回滚事务、四级模块解析链（已知模块→联邦扩展→本地文件→CDN RequireJS），无需构建即可实时编写和测试JupyterLab插件 |
| 17 | [jupyterlab-latex](jupyterlab-latex/index.md) | JupyterLab LaTeX 编辑扩展——为 .tex 文件提供实时编译预览、双向SyncTeX导航、富编辑工具栏，后端Tornado调度LaTeX编译（xelatex/pdflatex/lualatex/tectonic多引擎+BibTeX自动检测），前端pdfjs-dist渲染PDF+Shift+Ctrl/Cmd+Click反向同步，TypeScript+Python双插件架构（v4.4.0） |
| 18 | [jupyter-renderers](jupyter-renderers/index.md) | JupyterLab 官方MIME渲染器扩展集合——FASTA生物序列(MSA)、GeoJSON地理数据(Leaflet)、KaTeX/MathJax2数学公式、Vega/Vega-Lite可视化五个预构建扩展，Lerna monorepo管理，MIME渲染器四要素模式与ILatexTypesetter服务模式，hatch-jupyter-builder Python wheel打包 |
| 10 | [try-jupyter](try-jupyter/index.md) | JupyterLite浏览器端体验站点——基于Pyodide+Xeus双内核(WASM)、零安装Python/C++/R/SQLite环境、Pixi构建管线、GitHub Pages部署、Playwright E2E测试 |
| 19 | [ui-profiler](ui-profiler/index.md) | JupyterLab UI性能基准测试扩展——Benchmark×Scenario N×M测量矩阵、6种测量方法(Execution Time/CSS Stylesheets/Rules/Groups/Usage/JS Self-Profiling)、10种内置场景、减法式CSS性能分析、MutationObserver/ResizeObserver驱动的Dramaturg自动化层、IQR鲁棒统计、火焰图可视化，支持自定义Benchmark/Scenario扩展 |
| 20 | [jupyter-collaboration](jupyter-collaboration/index.md) | Jupyter实时协作扩展——基于Yjs CRDT的多用户同时编辑、WebSocket实时同步、Awareness用户感知（光标/选区/在线状态）、SQLiteYStore CRDT持久化、外带变更检测、文档Fork分叉与时间线版本导航、RtcContentProvider透明替换JupyterLab内容提供者、Jupyter Events事件系统（v5.0.0） |

### 部署层：容器化运行

| 顺序 | 知识束 | 一句话简介 |
|------|--------|-----------|
| 4 | [jupyter-docker-stacks](jupyter-docker-stacks/index.md) | Jupyter 官方 Docker 镜像——镜像层级体系（base→minimal→scipy→专业栈）、启动生命周期、Hook 自定义、用户权限、GPU 支持、CI/CD 构建 |
| 5 | [cookiecutter-docker-stacks](cookiecutter-docker-stacks/index.md) | Jupyter Docker 镜像模板生成器——一键生成包含 Dockerfile/pytest测试/CI/CD/DevContainer 的自定义镜像项目，14个基础镜像预设、TrackedContainer测试框架、GitHub Actions自动发布 |

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
