---
type: spec
title: "myst-execute + thebe 核心洞察与知识地图"
---

# myst-execute + thebe 核心洞察与知识地图

> I阶段产出：核心洞察四元组 + 知识地图设计

## 核心洞察（四元组）

### 洞察1：构建时执行 vs 运行时交互的双轨架构

- **陈述**：myst-execute 与 thebe 虽然都涉及"执行 Jupyter 代码"，但面向完全不同的执行时相——myst-execute 在构建时（build-time）连接本地 Jupyter Server 执行 Notebook 并缓存输出到静态文件；thebe 在运行时（run-time）通过浏览器连接 Binder/本地/JupyterLite 内核实现交互式代码执行。二者通过 MyST AST 中的 `jupyter_data` 输出格式形成数据契约，但执行管线完全独立。
- **证据**：F-010~F-015（myst-execute 作为 unified 插件在构建管线中执行）、F-034~F-035（构建时缓存机制）、F-051~F-059（thebe 在浏览器中连接服务器）、F-071~F-075（thebe-lite 浏览器内 Pyodide 内核）
- **反常识**：初学者容易以为"执行 Notebook"就是一回事，但 myst-execute 输出的是静态 HTML 中的预计算结果（无交互），thebe 提供的是点击按钮后在浏览器中动态执行的能力。myst-execute 的缓存是磁盘文件，thebe 的"缓存"是 Binder session 的 localStorage 复用。
- **行动**：文档必须从一开始就区分"构建时预执行"和"运行时交互"两条路径，概念 00-execution-architecture 作为总览明确二者定位；示例也按此分为 configure-notebook-execution（构建时）、thebe-interactive（Binder/直连）、thebe-lite（无服务器）。

### 洞察2：多级缓存抽象——从 JSON 文件到 ipynb 格式的向后兼容

- **陈述**：myst-execute 的缓存系统采用接口抽象（ICache<T>）+ 多层实现的策略：LocalDiskCache 是基础 JSON 文件存储；LegacyExecutionCache 适配旧版纯 IOutput[] 格式；NotebookExecutionCache 将结果封装为标准 ipynb 格式（nbformat 4.5）；TieredExecutionCache 实现主备两级缓存查找。缓存键使用 MD5(kernelName + 代码内容 + 环境变量) 确保确定性。
- **证据**：F-024~F-031（四种缓存实现）、F-032~F-033（MD5 缓存键构建包含 kernelSpec、代码、raisesException 标志、环境变量）
- **反常识**：缓存键不包含执行时间戳或随机数——这是故意的：相同代码+相同内核+相同环境变量应该命中缓存，无论何时构建。缓存失效依赖代码变化或 `execute: cache: false` frontmatter 配置。
- **行动**：概念 02-execution-cache 专门讲解缓存层次结构和键计算逻辑；NotebookExecutionCache 的 ipynb 格式设计说明它不仅是内部缓存，还可作为可移植的输出交换格式。

### 洞察3：Thebe 的分层 Provider 架构——从脚本标签到 React 声明式

- **陈述**：thebe 提供三种接入层级：(1) UMD 脚本标签 + window.thebeCore 全局变量（最简方式）；(2) thebe-core 的编程式 API（Config → ThebeServer → ThebeSession → ThebeNotebook 链式创建）；(3) thebe-react 的声明式 Provider 组件（ThebeLoaderProvider → ThebeServerProvider → ThebeSessionProvider → useNotebook/useNotebookFromSource hooks）。三层共享同一核心逻辑，Provider 只是对核心 API 的 React 封装。
- **证据**：F-060~F-063（核心 API + window 挂载）、F-076~F-080（React Providers 和 hooks）、F-009（ThebeBundleLoaderProvider 动态加载 UMD script）
- **反常识**：ThebeServerProvider 中 config 只在首次创建（useMemo 依赖 core/config/options），不会响应 options 变化重建服务器——这不是 bug，而是因为服务器连接是重量级操作，变更配置需要手动 disconnect 再 connect。
- **行动**：概念 03-thebe-core-api 讲解核心链式 API；概念 07-thebe-react 讲解 Provider 嵌套顺序和 hooks 用法；示例 02-thebe-interactive 展示从核心 API 到 React 的两种用法。

### 洞察4：三种服务器连接模式的抽象统一

- **陈述**：thebe 将三种服务器连接方式（Binder 远程构建、直连 Jupyter Server、JupyterLite/Pyodide 浏览器内核）统一在 ThebeServer 类的三个方法中：connectToServerViaBinder()、connectToJupyterServer()、connectToJupyterLiteServer()。三者最终都产生一个可用的 SessionManager，上层 ThebeSession/ThebeNotebook 无需感知底层连接方式。
- **证据**：F-053~F-056（三种连接方法实现）、F-057（startNewSession 统一接口）、F-060（connectToBinder/connectToJupyter/connectToJupyterLite 三个工厂函数）、F-077（ThebeServerProvider 通过 useBinder/useJupyterLite prop 选择连接方式）
- **反常识**：JupyterLite 模式下没有真实的 WebSocket 连接和 HTTP 服务器，serviceManager 由 Pyodide 在 Web Worker 中模拟，但对上层 Session/Kernel API 来说接口完全一致——这是面向接口设计的典型案例。
- **行动**：概念 05-thebe-binder 专门讲 Binder 连接（SSE 事件流、saved sessions），概念 06-thebe-lite-pyodide 讲无服务器模式，概念 03-thebe-core-api 统一说明 Server 抽象。

---

## 知识地图

### 学习路径

```
入门/总览（1篇）
  └─ 00-execution-architecture.md  → 构建时 vs 运行时执行全景、myst-execute 与 thebe 的关系

myst-execute 核心（3篇）
  ├─ 01-myst-execute-kernel.md     → Jupyter 内核连接管理（createKernelConnection、executeCodeCell）
  ├─ 02-execution-cache.md         → 多级缓存系统（ICache、LocalDiskCache、NotebookExecutionCache、TieredExecutionCache）
  └─ 配套：kernelExecutionTransform 作为 unified 插件的使用方式

thebe 核心（4篇）
  ├─ 03-thebe-core-api.md          → 核心 API 链式调用（Config→Server→Session→Notebook）
  ├─ 04-thebe-configuration.md     → 配置选项详解（BinderOptions/KernelOptions/ServerSettings）
  ├─ 05-thebe-binder.md            → Binder 连接机制（EventSource/SSE、saved sessions）
  ├─ 06-thebe-lite-pyodide.md      → JupyterLite/Pyodide 无服务器执行
  └─ 07-thebe-react.md             → React Provider 组件和 hooks 集成
```

### 概念文档与事实映射

| 文档 | 覆盖事实 |
|------|---------|
| 00-execution-architecture | F-001~F-004, F-010, F-022~F-023, F-051~F-052, F-071 |
| 01-myst-execute-kernel | F-011~F-021, F-036~F-040, F-041~F-044 |
| 02-execution-cache | F-024~F-035 |
| 03-thebe-core-api | F-005~F-006, F-051~F-053, F-057~F-063, F-068~F-070 |
| 04-thebe-configuration | F-045~F-050, F-064~F-067 |
| 05-thebe-binder | F-054~F-056, F-047~F-048, F-058~F-059 |
| 06-thebe-lite-pyodide | F-007, F-054, F-071~F-075 |
| 07-thebe-react | F-008~F-009, F-076~F-080 |

### 示例文档规划

| 示例 | 内容 |
|------|------|
| 01-configure-notebook-execution.md | myst.yml 中配置 kernelspec 和 execute 选项、缓存控制、raises-exception/skip-execution 标签 |
| 02-thebe-interactive.md | 使用 thebe-core API 连接 Binder/本地服务器、Thebe React Provider 配置交互式代码块 |
| 03-thebe-lite.md | 加载 thebe-lite、使用 Pyodide 内核实现完全无服务器的浏览器内执行 |

### 信源清单

| 信源ID | 路径 | 覆盖范围 |
|--------|------|---------|
| myst-execute-src | mystmd/packages/myst-execute/src/execute.ts | 执行管线核心 |
| thebe-core-src | thebe/packages/core/src/index.ts | 核心导出入口 |
| thebe-lite-src | thebe/packages/lite/src/index.ts | Pyodide 支持 |
| thebe-react-src | thebe/packages/react/src/index.ts | React 集成 |
