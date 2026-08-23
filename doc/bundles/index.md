---
okf_version: "0.2"
type: bundles-index
title: "知识束总索引"
description: "awesome-okf-xs 知识束（bundles）分组导航——按技术域与分组组织的开源项目源码中文教程"
total_bundles: 248
groups: 28
domains: 10
---

# 知识束总索引（Bundles Index）

> **OKF (Open Knowledge Format)** 知识束是面向开源项目源码与AI平台的系统化中文教程，遵循 [OKF v0.2 规范](meta/okf-spec/index.md)，每个知识束包含概念文档（concepts/）、实战示例（examples/）、信源参考（references/）三层结构。
>
> 当前共 **248 个知识束**，按技术生态分为 **10 个技术域、28 个分组**。

---

## 生态关系概览

```
┌──────────────────────────────────────────────────────────┐
│              📐 meta/ 规范与格式（okf-spec 锚点）          │
│              所有知识束遵循的格式约定                      │
└──────────────────────┬───────────────────────────────────┘
                       │ 规范约束
┌──────────────────────▼───────────────────────────────────┐
│              🐍 python/ Python 语言核心（cpython 锚点）    │
│              对象模型 · GC · 字节码 · 导入系统             │
└──────────────────────┬───────────────────────────────────┘
                       │ 语言底座
┌──────────────────────▼───────────────────────────────────┐
│              🔨 build/ 构建系统与包管理生态                │
│   conda 环境/包管理 · cmake/scikit-build 构建 · 通用工具   │
└──────────┬──────────────────────────────┬────────────────┘
           │                              │
┌──────────▼─────────────┐  ┌─────────────▼────────────────┐
│ 📚 document/ 文档工程    │  │ 📊 data/ 数据科学与科学计算    │
│ sphinx·myst·jupyter-book│  │ pydata 科学计算全栈           │
│ jupyter·katex           │  │ NumPy→pandas→可视化→Web→HDF5 │
└──────────┬─────────────┘  └─────────────┬────────────────┘
           │                              │
┌──────────▼─────────────┐  ┌─────────────▼────────────────┐
│ 🧠 ml/ 机器学习模型生态  │  │ 📡 comm/ 通信与网络生态        │
│ ONNX 标准/转换器/编译器  │  │ ZeroMQ 消息栈 · SSH 远程控制   │
└──────────┬─────────────┘  └─────────────┬────────────────┘
           │                              │
┌──────────▼──────────────────────────────▼────────────────┐
│              🤖 ai/ 人工智能与大模型应用生态               │
│ agnes-ai · ai-agent · langchain-ai · datawhale · coze    │
│ deepseek · trae · tencent · pocketflow                   │
└──────────┬──────────────────────────────┬────────────────┘
           │                              │
┌──────────▼─────────────┐  ┌─────────────▼────────────────┐
│ 🌐 web/ Web 开发生态     │  │ 💭 think/ 思想与理论          │
│ fastapi · graphql      │  │ psi · laozi                  │
└────────────────────────┘  └──────────────────────────────┘
```

---

## 推荐入门路径

从零开始系统学习开源项目源码，推荐按以下顺序：

```
📐 meta/okf-spec        了解 OKF 知识束格式规范（30分钟）
  → 🐍 python/cpython  理解 Python 解释器底层（选读核心章节）
    → 🔨 build/        掌握构建与包管理（copier 脚手架 → pyinvoke 自动化 → conda 环境 → cmake 构建）
      → 📚 document/   掌握文档工程能力（sphinx 文档写作 → jupyter-book/myst 新一代工具链 → jupyter 交互计算）
        → 📊 data/     pydata 科学计算全栈（NumPy→pandas→matplotlib/plotly→Dash→PyTables）
          → 🧠 ml/     ONNX 机器学习模型生态（模型交换格式·转换器·编译器·推理后端）
            → 🤖 ai/   人工智能与大模型应用（agnes-ai 大模型API → ai-agent Agent框架 → langchain-ai LLM应用框架 → datawhale 学习社区）
              → 🌐 web/ Web 开发生态（fastapi · graphql）
                → 📡 comm/ 通信与网络生态（ZeroMQ 消息 · SSH 远程控制）
                  → 💭 think/ 思想与理论（psi · laozi 选读）
```

---

## 十域分组导航

### 📐 [规范与格式](meta/index.md) · 1 束 · 1 组

| 分组 | 束数 | 说明 |
|------|-----|------|
| [📐 规范与格式（okf-spec 锚点）](meta/index.md) | 1 | OKF v0.2 规范本体——目录结构、文档类型、交叉引用、术语、版本、信任与验证；阅读知识束前必读 |

### 🐍 [Python 语言核心](python/index.md) · 1 束 · 1 组

| 分组 | 束数 | 说明 |
|------|-----|------|
| [🐍 Python 语言核心（cpython 锚点）](python/index.md) | 1 | CPython 解释器核心架构——对象模型、引用计数、GC、字节码、编译器管线、模块导入系统；所有 Python 知识的底座 |

### 🔨 [构建系统与包管理生态](build/index.md) · 14 束 · 4 组

| 分组 | 束数 | 说明 |
|------|-----|------|
| [📦 Conda 包管理生态](build/conda/index.md) | 6 | Conda 核心、conda-lock/pack/constructor 工具链、Rattler Rust 实现、conda-docs 文档门户 |
| [📦 scikit-build 构建后端](build/scikit-build/index.md) | 1 | scikit-build-core——基于 CMake 的 PEP 517 独立构建后端（锚点组） |
| [🏗️ CMake 构建系统生态](build/cmake/index.md) | 1 | CMake 跨平台构建生成器——门面模式、状态快照、多生成器工厂、CTest/CPack 集成 |
| [🔧 通用开发工具](build/tooling/index.md) | 6 | Ninja 极速构建、Copier 项目模板、PyInvoke 任务自动化、invocations 任务集、GitHub Problem Matcher、Nuitka 编译 |

### 📚 [文档工程与交互式计算生态](document/index.md) · 105 束 · 5 组

| 分组 | 束数 | 说明 |
|------|-----|------|
| [📄 Sphinx 文档工程生态](document/sphinx/index.md) | 10 | Sphinx 核心、默认主题、功能扩展、输出渲染扩展、Docker 部署 |
| [📖 MyST Markdown 与 Executable Books 生态](document/myst/index.md) | 19 | MyST 解析器、Sphinx 集成、UI 组件扩展等 Executable Books 组织项目 |
| [📖 Jupyter Book v2 / MySTmd 生态](document/jupyter-book/index.md) | 8 | TypeScript 新一代技术文档工具链——MyST 引擎、CLI、多格式导出、主题系统 |
| [🔣 KaTeX 数学排版](document/katex/index.md) | 1 | KaTeX 快速 Web 数学排版库——LaTeX 表达式渲染为 HTML+MathML（锚点组） |
| [📓 Jupyter 数据科学生态](document/jupyter/index.md) | 67 | Jupyter 交互式计算生态——内核协议、Notebook 格式、JupyterLab、扩展、部署 |

### 📊 [数据科学与科学计算生态](data/index.md) · 7 束 · 1 组

| 分组 | 束数 | 说明 |
|------|-----|------|
| [📊 PyData 科学计算生态](data/pydata/index.md) | 7 | NumPy/pandas/matplotlib/Plotly/Dash/PyTables/SymPy——数值计算、数据分析、可视化、Web 应用、HDF5 存储 |

### 🧠 [机器学习模型生态](ml/index.md) · 8 束 · 1 组

| 分组 | 束数 | 说明 |
|------|-----|------|
| [🧠 ONNX 机器学习生态](ml/onnx/index.md) | 8 | ONNX 标准/IR-Python/优化器/onnxmltools/sklearn-onnx/tf2onnx/onnx-mlir/onnx-tensorrt——跨框架模型交换、转换器、编译器、推理后端 |

### 🤖 [人工智能与大模型应用生态](ai/index.md) · 95 束 · 9 组

| 分组 | 束数 | 说明 |
|------|-----|------|
| [🤖 AgnesAI 大模型生态](ai/agnes-ai/index.md) | 2 | AgnesAI 全模态 AI 平台——OpenAI 兼容 API、对话/图像/视频生成、Agent 工具调用 |
| [🤖 AI Agent 框架](ai/ai-agent/index.md) | 20 | AI Agent 运行时框架与架构模式——工具调用循环、多代理编排、记忆系统、Coding Agent 源码解读 |
| [🦜🔗 LangChain-AI LLM 应用框架](ai/langchain-ai/index.md) | 19 | LangChain/LangGraph 核心框架（Python+JS）、深度研究 Agent、可观测性、评测与基础设施 |
| [🐳 Datawhale 开源 AI 学习社区](ai/datawhale/index.md) | 18 | 国内最大开源 AI 学习社区——LLM 全栈/RAG/Agent/向量数据库/推荐系统/ML 理论 |
| [🧩 Coze 扣子开发平台生态](ai/coze/index.md) | 3 | 字节跳动一站式 AI Agent 开发平台——Python SDK、开源平台、LLM 可观测性 |
| [🧠 DeepSeek-AI 基础设施](ai/deepseek/index.md) | 12 | DeepSeek 开源大模型基础设施——MoE 通信、GPU kernel 优化、注意力、流水线并行、负载均衡 |
| [🚀 TRAE Community 生态](ai/trae/index.md) | 12 | 字节跳动 AI 编程 IDE 社区——平台应用、技能/模板/MCP 扩展、学习资源、社区治理 |
| [🐧 腾讯开源生态](ai/tencent/index.md) | 4 | 腾讯系开源与商业项目——CodeBuddy 产品矩阵、AI 红队平台、ncnn 推理框架 |
| [⚡ PocketFlow 极简 LLM 应用框架](ai/pocketflow/index.md) | 5 | 极简 LLM Agent 框架——节点+流程抽象、设计模式、实战教程 |

### 📡 [通信与网络生态](comm/index.md) · 10 束 · 2 组

| 分组 | 束数 | 说明 |
|------|-----|------|
| [📨 消息通信生态](comm/messaging/index.md) | 4 | ZeroMQ 消息通信与分布式任务队列——libzmq 核心库、C++/Python 绑定、dramatiq 任务队列 |
| [🌐 SSH 与远程控制](comm/networking/index.md) | 6 | Python SSH/远程控制生态——paramiko/fabric/netmiko/asyncssh/pexpect/scrapli |

### 🌐 [Web 开发生态](web/index.md) · 2 束 · 2 组

| 分组 | 束数 | 说明 |
|------|-----|------|
| [⚡ FastAPI Web 框架生态](web/fastapi/index.md) | 1 | FastAPI 高性能 ASGI Web 框架——类型注解驱动、依赖注入树、OpenAPI 自动生成 |
| [📡 GraphQL 核心规范与生态](web/graphql/index.md) | 1 | GraphQL 查询语言系统化中文教程——语法、Schema 类型系统、验证执行管线、内省系统 |

### 💭 [思想与理论](think/index.md) · 5 束 · 2 组

| 分组 | 束数 | 说明 |
|------|-----|------|
| [Ψhē 理论体系](think/psi/index.md) | 4 | ψ=ψ(ψ) 自指递归理论体系——哲学、数学、宇宙学、意识研究与 AI 应用 |
| [📜 老子（Laozi）知识包](think/laozi/index.md) | 1 | 《老子》（《道德经》）相关知识包——帛书《老子》阅读教程 |
