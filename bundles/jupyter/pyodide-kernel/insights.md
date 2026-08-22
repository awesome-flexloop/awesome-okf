# Pyodide Kernel 架构洞察

> I阶段产出：核心洞察四元组 + 知识地图 + 文档清单

## 核心架构洞察

### 洞察 I-1：双层架构——构建时 Python Addon + 运行时 JS/Python WASM Kernel

- **陈述**：pyodide-kernel 采用双层架构：Node.js/Python 构建时通过三个 JupyterLite Addon（PyodideAddon/PipliteAddon/PyodideLockAddon）准备静态资源，浏览器运行时通过主线程 PyodideKernel + Web Worker（PyodideRemoteKernel）+ WASM 内 Python 解释器三层协作执行代码。
- **证据**：F-017（三个 addon 入口点）、F-048（主线程 PyodideKernel）、F-065（Worker 端 PyodideRemoteKernel）、F-079（浏览器端 pyodide_kernel 包）
- **反常识**：初学者可能以为 kernel 全在浏览器里运行，但构建阶段的 Python Addon 负责下载 Pyodide 发行版、生成 wheel 索引、定制 lockfile，这些准备工作直接影响浏览器端的包可用性。
- **行动**：概念文档应分为"构建配置"和"运行时架构"两大块，先讲构建准备再讲运行时执行流程。

### 洞察 I-2：双 Worker 通信模式——Comlink（postMessage） vs Coincident（SharedArrayBuffer）

- **陈述**：kernel 根据 `crossOriginIsolated` 自动选择两种 Worker 通信模式：非跨源隔离时使用 Comlink（基于 postMessage，异步），跨源隔离时使用 Coincident（基于 SharedArrayBuffer + Atomics，支持同步文件系统和 stdin）。
- **证据**：F-050/F-051（initWorker 条件选择）、F-073（PyodideComlinkKernel 用同步 XHR 做 stdin）、F-075/F-076（PyodideCoincidentKernel 用 SharedBufferContentsAPI）
- **反常识**：文件系统同步和 stdin 输入这两个看似基础的功能，在非 crossOriginIsolated 环境下要么不可用（文件系统）要么通过同步 XHR 走 Service Worker 实现（stdin），体验和性能都有差异。
- **行动**：概念文档应专门解释两种通信模式的差异和适用场景，以及为什么 Firefox 隐私模式下文件系统不同步。

### 洞察 I-3：包管理三层级——Pyodide 内置包 → piplite 本地索引 → PyPI 回退

- **陈述**：浏览器端包安装采用三级查找策略：1) 先从 pyodide-lock.json 预加载的内置包查找；2) 然后从构建时生成的 all.json 本地索引（含用户 wheels 和 federated extension wheels）查找；3) 最后根据 disablePyPIFallback 配置决定是否回退到 pypi.org。
- **证据**：F-111（_query_package 查找顺序）、F-024（PipliteAddon 生成 all.json）、F-043（DISABLE_PYPI_FALLBACK 配置）、F-084（loadPackagesFromImports 自动导入加载）
- **反常识**：%pip 魔法命令不是调用真正的 pip，而是通过 LiteTransformerManager 在代码转换阶段拦截，替换为 piplite.install() 调用；且 piplite 是 micropip 的包装而非替代。
- **行动**：概念文档应讲清包管理的三级查找链，以及 %pip → piplite → micropip 的调用关系。

### 洞察 I-4：IPython 兼容层——Mock + Patch + 子类化三层适配

- **陈述**：为了在 Pyodide WASM 环境中运行 IPython 交互环境，项目采用三层适配：1) mocks 注入缺失的 POSIX 模块（termios/fcntl/resource/tornado/pexpect）；2) patches 设置 matplotlib backend 等环境变量；3) 子类化 InteractiveShell/DisplayHook/DisplayPublisher/HistoryManager 替换不兼容行为。
- **证据**：F-104（五个模块 mock）、F-105（matplotlib patch）、F-088（Interpreter 继承 InteractiveShell）、F-099（LiteDisplayPublisher 替换回调）、F-092（CustomHistoryManager 禁用历史）
- **反常识**：不是"移植 IPython 到 WASM"，而是"让 IPython 以为自己在正常 POSIX 环境中运行"，通过 mock 掉所有在浏览器中不可用的系统调用。
- **行动**：概念文档应解释 mock/patch 策略，帮助用户理解为什么有些 Python 功能在浏览器中不可用。

### 洞察 I-5：消息桥接——从 Python 回调到 Jupyter 消息协议的多层转发

- **陈述**：Python 代码执行产生的输出（stdout/stderr/display_data/execute_result/error/comm）通过四层桥接到达前端：Python 端回调 → Worker 端 JS 回调 → postMessage/proxy → 主线程 _processWorkerMessage → BaseKernel 消息分发。
- **证据**：F-098（LiteStream.write 调用 publish_stream_callback）、F-330-F-338（worker.ts 中回调绑定）、F-055（主线程消息类型处理）
- **反常识**：Python 端的 sys.stdout.write 不是直接输出到页面，而是经过 Python→JS→Worker→主线程 四次跨边界传递；stdin 方向相反，在 coincident 模式下是同步阻塞的（Atomics.wait），在 comlink 模式下通过同步 XHR 模拟。
- **行动**：概念文档应包含消息流图，解释 execute_request 从发起到结果回传的完整路径。

## 知识地图

### 文档分组

| 分组 | 文档 | 覆盖事实 | 学习顺序 |
|------|------|---------|---------|
| **入门** | 00-introduction.md | F-001~F-015 | 1 |
| **入门** | 01-getting-started.md | F-018~F-021, F-117~F-122 | 2 |
| **核心** | 02-architecture-overview.md | F-048~F-078, F-079~F-108 | 3 |
| **核心** | 03-worker-communication.md | F-050~F-054, F-065~F-078 | 4 |
| **核心** | 04-build-addons.md | F-017~F-040, F-026~F-030 | 5 |
| **核心** | 05-package-management.md | F-022~F-025, F-109~F-116, F-084 | 6 |
| **核心** | 06-python-compatibility.md | F-104~F-108, F-088~F-103 | 7 |
| **核心** | 07-message-bridge.md | F-055~F-056, F-097~F-103, F-238~F-348 | 8 |
| **高级** | 08-lockfile-customization.md | F-026~F-030, F-059~F-060 | 9 |

### 学习路径

```
入门：00 介绍 → 01 快速开始
  ↓
核心：02 架构总览 → 03 Worker通信 → 04 构建Addon → 05 包管理 → 06 Python兼容 → 07 消息桥接
  ↓
高级：08 Lockfile定制
```

## 文档清单

### concepts/（9篇）

| 文件 | type | title | 覆盖事实 |
|------|------|-------|---------|
| 00-introduction.md | Concept | Pyodide Kernel 介绍 | F-001~F-015 |
| 01-getting-started.md | Concept | 快速开始 | F-018~F-021, F-117~F-122 |
| 02-architecture-overview.md | Concept | 架构总览 | F-048~F-078, F-079~F-108 |
| 03-worker-communication.md | Concept | Worker 通信模式 | F-050~F-054, F-065~F-078 |
| 04-build-addons.md | Concept | 构建时 Addon 系统 | F-017~F-040 |
| 05-package-management.md | Concept | 浏览器端包管理 | F-022~F-025, F-109~F-116, F-084 |
| 06-python-compatibility.md | Concept | Python 兼容性层 | F-104~F-108, F-088~F-103 |
| 07-message-bridge.md | Concept | 消息桥接机制 | F-055~F-056, F-097~F-103 |
| 08-lockfile-customization.md | Concept | Lockfile 定制 | F-026~F-030, F-059~F-060 |

### examples/（2篇）

| 文件 | type | title | 说明 |
|------|------|-------|------|
| basic-install-config.md | Example | 基本安装与配置 | pip install + jupyter lite build |
| custom-wheels.md | Example | 添加自定义 Wheel 包 | --piplite-wheels 使用 |

### references/（5篇）

| 文件 | type | title | 覆盖源码 |
|------|------|-------|---------|
| addon-source.md | Reference | Python Addon 源码参考 | jupyterlite_pyodide_kernel/addons/ |
| kernel-ts-source.md | Reference | TypeScript Kernel 源码参考 | packages/pyodide-kernel/src/ |
| kernel-py-source.md | Reference | 浏览器端 Python Kernel 源码参考 | packages/pyodide-kernel/py/pyodide-kernel/ |
| piplite-source.md | Reference | piplite 源码参考 | packages/pyodide-kernel/py/piplite/ |
| extension-source.md | Reference | JupyterLab Extension 源码参考 | packages/pyodide-kernel-extension/src/ |
