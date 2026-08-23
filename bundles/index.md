---
okf_version: "0.2"
type: bundles-index
title: "知识束总索引"
description: "awesome-okf-xs 知识束（bundles）分组导航——按技术生态组织的开源项目源码中文教程"
total_bundles: 240
groups: 24
---

# 知识束总索引（Bundles Index）

> **OKF (Open Knowledge Format)** 知识束是面向开源项目源码与AI平台的系统化中文教程，遵循 [OKF v0.2 规范](meta/okf-spec/index.md)，每个知识束包含概念文档（concepts/）、实战示例（examples/）、信源参考（references/）三层结构。
>
> 当前共 **240 个知识束**，按技术生态分为 **24 个分组**。

---

## 生态关系概览

```
┌──────────────────────────────────────────────────────┐
│            📐 meta/okf-spec (OKF 格式规范)            │
│            所有知识束遵循的格式约定                     │
└─────────────────────┬────────────────────────────────┘
                      │ 规范约束
┌─────────────────────▼────────────────────────────────┐
│           🐍 python/cpython (Python 语言底座)         │
│           对象模型 · GC · 字节码 · 导入系统            │
└──────────┬──────────────────────────┬────────────────┘
           │                          │
┌─────────────────────┬──────────────────────────┬────────────────┐
│ 📦 conda/ 环境管理   │  │ 🔧 tooling/ 通用开发工具      │
│ 包管理 · 锁定 · 打包 │  │ 任务自动化 · CI 集成          │
│ 安装器 · Rust 引擎   │  │                              │
└──────────┬──────────┘  └────────────┬─────────────────┘
           │                          │
┌──────────▼──────────────────────────▼─────────────────┐
│ 🏗️ cmake/ 构建系统                                    │
│ CMake构建生成器 · 多后端 · CTest测试 · CPack打包       │
└──────────┬──────────────────────────┬─────────────────┘
           │                          │
           ├──────────────────────────┤
           │                          │
┌──────────▼──────────┐  ┌────────────▼─────────────────┐
│ 📓 jupyter/ 交互式   │  │ 📄 sphinx/ 文档工程           │
│ 计算 · Notebook     │  │ 文档生成 · 扩展 · 国际化      │
│ 内核协议 · Docker   │  │ 社交卡片 · 重定向 · 数学渲染  │
└─────────────────────┘  └──────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│           📊 pydata/ 科学计算生态                     │
│  NumPy · pandas · matplotlib · Plotly · Dash        │
│  PyTables · 数值计算 · 数据分析 · 可视化 · Web应用    │
└──────────────────────────┬───────────────────────────┘
                           │ 模型训练/数据处理
┌──────────────────────────▼───────────────────────────┐
│           🧠 onnx/ 机器学习模型生态                    │
│  ONNX标准 · IR · 优化器 · 模型转换器                  │
│  onnx-mlir编译器 · TensorRT后端                      │
│  （跨框架模型交换格式，AI模型互操作性基石）            │
└──────────────────────────┬───────────────────────────┘
                           │ 模型部署/推理
┌──────────────────────────▼───────────────────────────┐
│           🤖 agnes-ai/ AI大模型生态                    │
│  多模态API网关 · 对话/图像/视频 · Agent工具调用        │
│   （独立AI服务层，通过OpenAI兼容SDK调用）              │
└──────────────────────────┬───────────────────────────┘
                           │ 模型调用
┌──────────────────────────▼───────────────────────────┐
│           🤖 ai-agent/ AI Agent框架                   │
│  Agent循环 · 工具系统 · 记忆架构 · 多代理编排          │
│  插件系统 · 通信协议 · 技能/Persona                   │
│   （构建在大模型API之上的Agent运行时架构）             │
└──────────────────────────┬───────────────────────────┘
                           │ LLM应用编排
┌──────────────────────────▼───────────────────────────┐
│           🦜🔗 langchain-ai/ LLM应用框架生态           │
│  LangChain/LangGraph(Python+JS) · 深度研究Agent      │
│  SWE Agent · 可观测性SDK · 评测库 · 基础设施部署      │
│  （LLM应用开发的事实标准框架，Runnable组合协议）       │
└──────────────────────────────────────────────────────┘
```

---

## 推荐入门路径

从零开始系统学习开源项目源码，推荐按以下顺序：

```
📐 okf-spec       了解 OKF 知识束格式规范（30分钟）
  → 🐍 cpython   理解 Python 解释器底层（选读核心章节）
    → 🔧 copier  掌握项目模板脚手架（创建标准化项目）
      → 🔧 pyinvoke 掌握 Python 任务自动化（实用工具）
        → 📦 conda 深入环境与包管理（日常开发必备）
          → 🏗️ cmake 掌握跨平台构建系统（C/C++项目必备）
            → 📄 sphinx  掌握文档工程能力（项目文档写作）
              → 📓 jupyter 交互式计算与数据分析
                → 📊 pydata 科学计算全栈（NumPy→pandas→matplotlib/plotly→Dash→PyTables）
                  → 🧠 onnx 机器学习模型生态（模型交换格式·转换器·编译器·推理后端）
                    → 🤖 agnes-ai 大模型API（AI服务调用）
                      → 🤖 ai-agent Agent框架（智能体构建）
                        → 🦜🔗 langchain-ai LLM应用框架（Runnable/LangGraph/Agent编排）
                          → 🐳 datawhale AI学习社区（LLM全栈/RAG/Agent/推荐系统/ML理论）
```

---

## 分组导航

| 分组 | 知识束数 | 说明 |
|------|---------|------|
| [📐 规范与格式](meta/index.md) | 1 | OKF 格式规范本体——阅读知识束前必读 |
| [🐍 Python 语言核心](python/index.md) | 1 | CPython 解释器核心架构——所有 Python 知识的底座 |
| [📦 Conda 包管理生态](conda/index.md) | 6 | Conda 核心、lock/pack/constructor 工具链、Rattler Rust 实现、文档门户 |
| [📓 Jupyter 数据科学生态](jupyter/index.md) | 4 | 内核协议、Notebook 格式、Notebook 应用、Docker 部署 |
| [📄 Sphinx 文档工程生态](sphinx/index.md) | 10 | Sphinx 核心、默认主题、功能扩展、输出渲染扩展、Docker 部署 |
| [🔧 通用开发工具](tooling/index.md) | 5 | PyInvoke 任务引擎、Copier 项目模板、invocations 任务集合、GitHub Problem Matcher、Ninja 极速构建 |
| [🏗️ CMake 构建系统生态](cmake/index.md) | 1 | CMake 跨平台构建生成器——门面模式、状态快照、多生成器工厂、目标传播、CTest/CPack 集成 |
| [🤖 AgnesAI 大模型生态](agnes-ai/index.md) | 1 | AgnesAI多模态AI平台——OpenAI兼容API、对话/图像/视频生成、Agent工具调用 |
| [🤖 AI Agent 框架](ai-agent/index.md) | 21 | AI Agent运行时框架——Agent循环、工具系统、记忆架构、多代理编排、插件架构、通信协议、Coding Agent源码解读 |
| [📊 PyData 科学计算生态](pydata/index.md) | 6 | NumPy/pandas/matplotlib/Plotly/Dash/PyTables——数值计算、数据分析、可视化、Web应用、HDF5存储 |
| [🧠 ONNX 机器学习生态](onnx/index.md) | 8 | ONNX标准/IR-Python/优化器/ONNXMLTools/sklearn-onnx/tf2onnx/onnx-mlir/onnx-tensorrt——跨框架模型交换、转换器、编译器、推理后端 |
| [📖 Jupyter Book v2 / MySTmd 生态](jupyter-book/index.md) | 8 | MyST引擎/CLI/语法扩展/多格式导出/Jupyter Book CLI/Notebook执行/Thebe交互/JupyterLab扩展/主题系统——TypeScript新一代技术文档工具链 |
| [🐳 Datawhale 开源 AI 学习社区](datawhale/index.md) | 18 | LLM教程/RAG/Agent/向量数据库/推荐系统/ML理论——torch-rechub/deepagents/base-llm/happy-llm/hello-agents/all-in-rag等18个项目的源码级中文教程 |
| [🦜🔗 LangChain-AI LLM应用框架](langchain-ai/index.md) | 19 | LangChain/LangGraph核心框架(Python+JS)、Google/MongoDB集成、LangSmith可观测性、deepagents深度研究Agent、open-swe SWE Agent、openevals评测、openwiki、基础设施部署 |
| [ψ Ψhē 理论体系](psi/index.md) | 4 | ψ=ψ(ψ)自指递归理论——核心哲学(塌缩/回声/观察者)、数学形式化(CST/RH证明/坍缩数学)、XOR-SHIFT宇宙本论、GodGPT应用 |
| [📨 消息通信生态](messaging/index.md) | 4 | ZeroMQ核心(libzmq)、C++绑定(cppzmq)、Python绑定(pyzmq)、Python分布式任务队列(dramatiq)——套接字抽象、ZMTP协议、I/O线程、Actor模型、Broker抽象 |

---

## 分组详情

### 📐 [规范与格式](meta/index.md)

| 知识束 | 简介 |
|--------|------|
| [okf-spec](meta/okf-spec/index.md) | OKF v0.2 规范——目录结构、文档类型、交叉引用、术语、版本、信任与验证 |

### 🐍 [Python 语言核心](python/index.md)

| 知识束 | 简介 |
|--------|------|
| [cpython](python/cpython/index.md) | CPython 解释器——对象模型、引用计数、GC、字节码、编译器管线、C 扩展 |

### 📦 [Conda 包管理生态](conda/index.md)

| 知识束 | 简介 |
|--------|------|
| [conda](conda/conda/index.md) | Conda 核心——七层架构、MatchSpec、SAT 求解器、事务、插件系统 |
| [conda-lock](conda/conda-lock/index.md) | 环境锁定——多平台 lockfile、conda/pypi 双求解器、内容哈希 |
| [conda-pack](conda/conda-pack/index.md) | 环境打包——可重定位归档、prefix 替换、跨环境部署 |
| [constructor](conda/constructor/index.md) | 安装器构造——跨平台安装包、construct.yaml、FCP、签名安全 |
| [rattler](conda/rattler/index.md) | Rust 实现——Crate 架构、高性能求解、repodata 网关、包流式安装 |
| [conda-docs](conda/conda-docs/index.md) | 文档门户——Sphinx 多项目架构、插件生态、社区贡献 |

### 📓 [Jupyter 数据科学生态](jupyter/index.md)

| 知识束 | 简介 |
|--------|------|
| [jupyter-client](jupyter/jupyter-client/README.md) | 协议客户端——ZMQ 五通道、内核管理、消息签名、多内核并行 |
| [nbformat](jupyter/nbformat/index.md) | Notebook 格式——NotebookNode 模型、v4 JSON、验证器、信任签名 |
| [jupyter-notebook](jupyter/jupyter-notebook/index.md) | Notebook v7——后端 App、前端 Shell、Handler、扩展系统 |
| [jupyter-docker-stacks](jupyter/jupyter-docker-stacks/index.md) | Docker 镜像——层级体系、启动生命周期、Hook 自定义、GPU 支持 |

### 📄 [Sphinx 文档工程生态](sphinx/index.md)

| 知识束 | 简介 |
|--------|------|
| [sphinx](sphinx/sphinx/index.md) | 文档生成器核心——Builder、Doctree、Domain、扩展接口、主题 |
| [alabaster](sphinx/alabaster/index.md) | Sphinx 默认主题——极简架构（130行Python）、50+配置选项、组件化侧边栏、主题开发范本 |
| [sphinx-argparse](sphinx/sphinx-argparse/index.md) | CLI 文档——argparse 自动文档、man page、嵌套子命令 |
| [sphinx-autobuild](sphinx/sphinx-autobuild/index.md) | 热重载预览——文件监听、自动重建、WebSocket 刷新 |
| [sphinx-intl](sphinx/sphinx-intl/index.md) | 国际化——gettext 目录、Transifex、翻译统计 |
| [sphinx-websupport](sphinx/sphinx-websupport/index.md) | Web 集成——嵌入式文档、评论、搜索 API |
| [sphinxcontrib-jsmath](sphinx/sphinxcontrib-jsmath/index.md) | 数学渲染——JS 客户端渲染、公式编号、按需加载 |
| [sphinxext-opengraph](sphinx/sphinxext-opengraph/index.md) | 社交卡片——OGP 标签、智能描述、Matplotlib 自动生成图 |
| [sphinxext-rediraffe](sphinx/sphinxext-rediraffe/index.md) | 页面重定向——HTML 跳转、跨平台路径、diff 检查 |
| [sphinx-docker-images](sphinx/sphinx-docker-images/index.md) | Docker 构建——base/latexpdf/ci 镜像、LaTeX 编译 |

### 🔧 [通用开发工具](tooling/index.md)

| 知识束 | 简介 |
|--------|------|
| [ninja](tooling/ninja/index.md) | Ninja 极速构建系统——Node-Edge二分图依赖模型、关键路径并行调度、mtime增量构建、depfile头依赖追踪、dyndep动态依赖、CMake/Meson/gn后端引擎（11概念+5示例+8信源，共27文档） |
| [copier](tooling/copier/index.md) | 项目模板渲染与更新——Jinja2 沙箱、问卷系统、Git 版本管理、三向合并更新、任务/迁移、Python API |
| [pyinvoke](tooling/pyinvoke/index.md) | 任务自动化——Pythonic CLI 任务、Context、Runner、Watcher |
| [invocations](tooling/invocations/index.md) | 官方任务集——打包、测试、文档、CI、检查格式化 |
| [github-problem-matcher](tooling/github-problem-matcher/index.md) | Actions 注解——Problem Matcher 模式、正则捕获、PR 错误高亮 |

### 🏗️ [CMake 构建系统生态](cmake/index.md)

| 知识束 | 简介 |
|--------|------|
| [cmake](cmake/cmake/index.md) | CMake 核心构建系统——两阶段执行模型、不可变状态快照、多生成器工厂（Makefile/Ninja/VS/Xcode）、目标属性 PUBLIC/PRIVATE/INTERFACE 传播、find_package Module/Config 双模式、策略系统、CTest 测试、CPack 打包（13概念+3示例+6信源，共22文档） |

### 🤖 [AgnesAI 大模型生态](agnes-ai/index.md)

| 知识束 | 简介 |
|--------|------|
| [agnes-ai-models](agnes-ai/agnes-ai-models/index.md) | AgnesAI统一API网关——OpenAI兼容接口、对话补全、文生图、文生视频、Function Calling/Agent工具调用、速率限制、错误处理、生产最佳实践（8概念+5示例+2信源，共17文档） |

### 🤖 [AI Agent 框架](ai-agent/index.md)

| 知识束 | 简介 |
|--------|------|
| [ai-agent-fundamentals](ai-agent/ai-agent-fundamentals/index.md) | Agent跨项目基础——6大核心架构模式对比、4框架代码级对比、框架选型指南 |
| [hermes-agent](ai-agent/hermes-agent/index.md) | 渐进式披露多Agent框架——Think-Act-Observe循环、ToolRegistry(100+工具)、MCP/ACP双协议 |
| [veadk-python](ai-agent/veadk-python/index.md) | 火山引擎Agent SDK——A2A/A2UI协议、RAG知识库、Sequential/Parallel/Loop/Supervisor组合模式 |
| [zleap-agent](ai-agent/zleap-agent/index.md) | Workspace-first Agent——Run→Work→WorkStep三级Fiber状态机、PostgreSQL+pgvector双线记忆 |
| [deepseek-harness](ai-agent/deepseek-harness/index.md) | Cordis插件架构(50+包)、Phase状态机+Inbox双队列、MCP/ACP双协议 |
| [intelligent-terminal](ai-agent/intelligent-terminal/index.md) | Windows Terminal原生Agent——双进程架构、ACP JSON-RPC 2.0、命名管道传输 |
| [cordis](ai-agent/cordis/index.md) | 可组合插件元框架——Context DI容器、Fiber六状态生命周期、5种事件派发模式 |
| [second-me](ai-agent/second-me/index.md) | 个人AI数字分身——L0→L1→L2三层记忆HMM、LoRA微调+DPO对齐 |
| [codewhale](ai-agent/codewhale/index.md) | Rust Coding Agent——21 crate workspace、Fleet多Agent、Workflow双轨引擎、ExecPolicy沙箱 |
| [deepseek-reasonix](ai-agent/deepseek-reasonix/index.md) | Go Agent运行时——ACP v1协议、arbiter/governor运行循环、QQ/飞书Bot网关、Checkpoint恢复 |
| [openai-codex](ai-agent/openai-codex/index.md) | OpenAI Codex CLI——三语言架构(JS/Rust/Python)、三层沙箱防御、AGENTS.md/Skills系统 |
| [nanobot](ai-agent/nanobot/index.md) | Python多端Agent——MessageBus+WebSocket、CLI/TUI/WebUI三端、SDK类型系统 |
| [deepcode-cli](ai-agent/deepcode-cli/index.md) | TypeScript编码助手——三包monorepo、10种权限作用域、MCP工具命名空间 |
| [opencode](ai-agent/opencode/index.md) | Terminal Coding Agent——Bun+Turbo+SST、SessionV2/Context Epoch、混合云部署 |
| [pi-cli](ai-agent/pi-cli/index.md) | Pi AI CLI——9包monorepo、AI/TUI双层、5个内置prompt工作流 |

### 📊 [PyData 科学计算生态](pydata/index.md)

| 知识束 | 简介 |
|--------|------|
| [numpy](pydata/numpy/index.md) | 科学计算基础库——ndarray多维数组、ufunc通用函数、dtype类型系统、广播规则、索引切片、线性代数、随机数（8概念+2示例+4信源，共18文档） |
| [pandas](pydata/pandas/index.md) | 数据分析核心库——DataFrame/Series数据模型、BlockManager列式存储、Index体系、GroupBy split-apply-combine、IO读写（4概念+1示例+1信源，共10文档） |
| [matplotlib](pydata/matplotlib/index.md) | 绑图基础库——Artist层级体系、多后端渲染、pyplot状态机、OO接口、属性系统（4概念+1示例+1信源，共10文档） |
| [plotly](pydata/plotly/index.md) | 交互式可视化——Figure数据模型、BasePlotlyType对象层级、Plotly Express高级API、renderers渲染框架（4概念+1示例+1信源，共10文档） |
| [dash](pydata/dash/index.md) | Web应用框架——Dash主类、WSGI/ASGI多后端、回调系统(Input/Output/State)、组件系统、MCP集成（4概念+1示例+1信源，共10文档） |
| [pytables](pydata/pytables/index.md) | HDF5数据管理——Node/Group/Leaf/Table层次、Atom类型系统、Blosc2压缩、CSI分块索引、NumPy/pandas集成（4概念+1示例+1信源，共10文档） |

### 🧠 [ONNX 机器学习生态](onnx/index.md)

| 知识束 | 简介 |
|--------|------|
| [onnx](onnx/onnx/index.md) | ONNX 标准核心——Protobuf IR（ModelProto/GraphProto/NodeProto/TensorProto）、OpSchema链式算子注册、Shape Inference形状推断、Checker模型验证、Python Helper API、C++ 核心IR双向链表、序列化/外部数据、版本转换（15概念+5示例+9信源，共29文档） |
| [ir-py](onnx/ir-py/index.md) | ONNX 纯Python IR参考实现——Model/Graph/Node/Value/Tensor核心实体、双向链表图结构、TensorProtocol张量协议、Tape录制回放、serde序列化/反序列化、名称管理与元数据（9概念+4示例+5信源，共18文档） |
| [optimizer](onnx/optimizer/index.md) | ONNX模型优化器——Pass基类体系（ImmutablePass/PredicateBasedPass/FullGraphBasedPass）、PassManager定点迭代、40+内置优化Pass、nanobind Python绑定、C API、自定义Pass开发（8概念+3示例+4信源，共15文档） |
| [onnxmltools](onnx/onnxmltools/index.md) | 多框架转换器——CoreML/LightGBM/XGBoost/CatBoost/H2O/LibSVM转ONNX、Topology IR、转换器注册、类型系统、树模型转换、Pipeline元数据（8概念+4示例+4信源，共16文档） |
| [sklearn-onnx](onnx/sklearn-onnx/index.md) | Scikit-learn转换器——Pipeline/FeatureUnion拓扑转换、ONNX算子代数、转换器注册机制、自定义转换器开发、分类器/回归器/预处理算子映射（7概念+4示例+4信源，共15文档） |
| [tensorflow-onnx](onnx/tensorflow-onnx/index.md) | TensorFlow转换器（tf2onnx）——Keras/SavedModel转ONNX、版本化算子集注册、GraphMatcher图重写、图内部API、优化器Pass、数据布局与类型转换（8概念+4示例+4信源，共16文档） |
| [onnx-mlir](onnx/onnx-mlir/index.md) | ONNX-MLIR编译器——基于LLVM/MLIR的端到端编译栈、ONNX Dialect/Krnl Dialect、Lowering Pipeline、ExecutionSession运行时、OMCompile编译器驱动、PyRuntime Python绑定（7概念+2示例+3信源，共12文档） |
| [onnx-tensorrt](onnx/onnx-tensorrt/index.md) | TensorRT后端解析器（onnx2trt）——ModelImporter ONNX解析管线、算子注册与Plugin机制、ShapedWeights权重内存模型、错误诊断与支持度查询、自定义Plugin开发（6概念+3示例+3信源，共12文档） |

### 📖 [Jupyter Book v2 / MySTmd 生态](jupyter-book/index.md)

| 知识束 | 简介 |
|--------|------|
| [mystmd](jupyter-book/mystmd/index.md) | MyST引擎核心——myst-parser（markdown-it+tokensToMyst MDAST生成）、myst-transforms（30+转换插件）、myst-common类型系统、myst-config配置、myst-frontmatter元数据、myst-spec节点规范（13概念+5示例+8信源，共26文档） |
| [myst-cli](jupyter-book/myst-cli/index.md) | 命令行工具——build多格式构建管线、start开发服务器、init项目初始化、clean清理、项目加载与TOC、模板系统、版本迁移、Session缓存（10概念+4示例+5信源，共19文档） |
| [myst-syntax](jupyter-book/myst-syntax/index.md) | 语法扩展——指令系统（admonition/code/figure/table/math/include）、角色系统（cite/ref/abbr/term）、Mermaid/SI单位等高级语法（9概念+3示例+4信源，共16文档） |
| [myst-exporters](jupyter-book/myst-exporters/index.md) | 多格式导出——HTML/LaTeX/PDF/DOCX/JATS XML/Markdown/Typst导出器、jtex模板引擎、JATS/LaTeX导入转换器（10概念+3示例+3信源，共16文档） |
| [jupyter-book](jupyter-book/jupyter-book/index.md) | Jupyter Book v2 CLI——Python+TypeScript双层架构、nodeenv环境管理、myst-cli白标发行版、模板系统（6概念+2示例+2信源，共10文档） |
| [myst-execute](jupyter-book/myst-execute/index.md) | Notebook执行与Thebe交互——myst-execute内核管理/缓存/执行管线、Thebe Core API/Binder连接、Thebe Lite Pyodide无服务器执行、Thebe React hooks（8概念+3示例+4信源，共15文档） |
| [jupyterlab-myst](jupyter-book/jupyterlab-myst/index.md) | JupyterLab扩展——三插件架构（content-factory/executor/mime-renderer）、MySTMarkdownCell、内联表达式、Widget React集成（6概念+3示例+4信源，共13文档） |
| [myst-theme](jupyter-book/myst-theme/index.md) | 主题系统——三层分离架构（styles/packages/themes）、CSS变量主题切换、命名网格线布局、myst-to-react MDAST→React渲染、Provider分层、Book/Article Remix SSR主题（8概念+2示例+3信源，共13文档） |

### 🐳 [Datawhale 开源 AI 学习社区](datawhale/index.md)

| 知识束 | 简介 |
|--------|------|
| [torch-rechub](datawhale/torch-rechub/index.md) | 推荐系统框架——30+模型（DSSM/DeepFM/DIN/MMoE等）、CTR/Match/MTL/Seq四类Trainer、ONNX导出与部署 |
| [deepagents](datawhale/deepagents/index.md) | 多语言Agent平台monorepo——libs/（acp/cli/code/evals/talon）+ openwiki，三层栈架构 |
| [base-llm](datawhale/base-llm/index.md) | 从NLP到LLM全栈教程——分词/Word2Vec/RNN/Transformer/BERT/GPT/LoRA/RLHF/量化/部署 |
| [happy-llm](datawhale/happy-llm/index.md) | 从零构建大模型——Transformer/PLM/LLaMA2手写实现/GRPO强化学习/RAG/Agent |
| [hello-agents](datawhale/hello-agents/index.md) | 从零构建智能体——16章：ReAct范式/框架开发/记忆/上下文工程/MCP-A2A通信协议/Agentic-RL/评估 |
| [all-in-rag](datawhale/all-in-rag/index.md) | RAG技术全栈指南——数据准备/索引构建/检索进阶/生成重排/评估体系/Graph RAG项目实战 |
| [easy-vecdb](datawhale/easy-vecdb/index.md) | 向量数据库原理与实践——向量检索/ANN算法（IVF/PQ/HNSW/LSH）/Annoy/Faiss/Milvus |
| [key-book](datawhale/key-book/index.md) | 机器学习理论钥匙书——可学性/计算复杂度/泛化界/稳定性/一致性/收敛率/遗憾界七大支柱 |
| [pumpkin-book](datawhale/pumpkin-book/index.md) | 南瓜书——西瓜书公式推导伴读，16章公式逐一推导 |
| [tiny-universe](datawhale/tiny-universe/index.md) | 大模型白盒子构建指南——TinyDiffusion/TinyRAG/TinyAgent/TinyLLM手搓实现 |
| [handy-ollama](datawhale/handy-ollama/index.md) | Ollama本地大模型部署教程——安装/模型管理/API/OpenAI兼容接口/WebUI/生产部署 |
| [handy-n8n](datawhale/handy-n8n/index.md) | n8n工作流自动化教程——6章从入门到高级，AI工作流与自定义节点 |
| [easy-vibe](datawhale/easy-vibe/index.md) | Vibe Coding多语言教程——10语言文档站、200+交互组件、AI Agent友好设计 |
| [vibe-vibe](datawhale/vibe-vibe/index.md) | Vibe开发教程——Basic入门/中英双语/100+交互组件/Docker部署 |
| [code-your-own-llm](datawhale/code-your-own-llm/index.md) | 手写LLM精简便签——全栈式LLM学习路径与文档写作规范 |
| [Agent-Learning-Hub](datawhale/Agent-Learning-Hub/index.md) | Agent学习路线图——9阶段Todo List、11级Project Ladder、9大资源分类 |
| [deepagents-in-action](datawhale/deepagents-in-action/index.md) | deepagents实战教程——Agent Harness定位、虚拟文件系统与Context Engineering、7种模板 |
| [members-visualization](datawhale/members-visualization/index.md) | Datawhale成员可视化（占位收录，仓库仅含.npmrc） |

### 🦜🔗 [LangChain-AI LLM应用框架](langchain-ai/index.md)

| 知识束 | 简介 |
|--------|------|
| [langchain](langchain-ai/langchain/index.md) | LangChain核心框架(Python)——Runnable组合协议、Message/Tool抽象、Prompt分层、输出解析、回调、检索（73事实/5洞察/10概念/4参考/3示例） |
| [langgraph](langchain-ai/langgraph/index.md) | LangGraph Agent编排框架(Python)——StateGraph/节点/边、Channel通道、Pregel BSP引擎、checkpoint持久化、Stream流式（128事实/6洞察/8概念/3参考/2示例） |
| [langchainjs](langchain-ai/langchainjs/index.md) | LangChain核心框架(JS/TS)——Runnable/Message/Tool、ReactAgent、Middleware、pnpm+turbo工作区（109事实/5洞察/8概念/3参考/2示例） |
| [langgraphjs](langchain-ai/langgraphjs/index.md) | LangGraph编排框架(JS/TS)——StateGraph/Annotation、通道、checkpoint、Pregel执行（7洞察/6概念/2参考/2示例） |
| [langchain-google](langchain-ai/langchain-google/index.md) | Google GenAI/VertexAI集成——双后端ChatModel、Embeddings、provider抽象与鉴权（85事实/3洞察/3概念） |
| [langchain-mongodb](langchain-ai/langchain-mongodb/index.md) | MongoDB集成——向量存储、Atlas Vector Search、聚合管道、聊天历史与缓存（79事实/4洞察/3概念） |
| [langsmith-sdk](langchain-ai/langsmith-sdk/index.md) | LangSmith可观测性SDK(JS)——traceable装饰器、RunTree追踪、评测器、匿名化（100事实/4洞察/4概念） |
| [langsmith-cli](langchain-ai/langsmith-cli/index.md) | LangSmith命令行工具(Go)——Cobra命令树、v1/v2透明切换、OAuth多Profile（57事实/3洞察/3概念/2参考） |
| [deepagents](langchain-ai/deepagents/index.md) | 深度研究Agent框架(Python)——planning/sub-agent/todo/context、ACP协议、Profile机制（64事实/5洞察/4概念/6参考，含lca变体） |
| [deepagentsjs](langchain-ai/deepagentsjs/index.md) | 深度研究Agent框架(TS)——中间件三层组装、子代理隔离、可插拔后端（83事实/3洞察/3概念） |
| [open-swe](langchain-ai/open-swe/index.md) | 开源SWE Agent——五图工厂、durable dispatch、reviewer findings、scheduler-reconcile闭环（70事实/4洞察/4概念） |
| [openevals](langchain-ai/openevals/index.md) | LLM评测库(JS+Python)——exact匹配、LLM-as-Judge、统一评测器协议（50事实/3洞察/3概念） |
| [openwiki](langchain-ai/openwiki/index.md) | Wiki/文档Agent(TS)——Agent-CLI分层、OAuth+Token管理、ngrok内网穿透（76事实/3洞察/3概念/2参考） |
| [openwork](langchain-ai/openwork/index.md) | 工作流CLI(TS)——桌面壳+deepagents内核、HITL审批、sql.js检查点（26事实/2洞察/1概念） |
| [chat-langchain](langchain-ai/chat-langchain/index.md) | 对话Demo应用——双文件合约(agent.py+identity.py)、六层中间件管道（26事实/2洞察/1概念/2参考） |
| [social-media-agent](langchain-ai/social-media-agent/index.md) | 社交媒体Agent(TS+Python)——14图微服务、HITL状态机、scatter-gather并行（34事实/10洞察/1概念） |
| [docs](langchain-ai/docs/index.md) | LangChain官方文档站——单源MDX双语构建、docs.json导航中心化、pipeline构建管道（100事实/2洞察，参考型） |
| [helm](langchain-ai/helm/index.md) | Helm Chart部署——五Chart分层矩阵、内置依赖vs外部服务双模式、三种入口互斥（85事实/4洞察，参考型） |
| [terraform](langchain-ai/terraform/index.md) | Terraform基础设施——四云模块矩阵、count条件编排、20+precondition守卫（56事实/1洞察，参考型） |

### ψ [Ψhē 理论体系](psi/index.md)

| 知识束 | 简介 |
|--------|------|
| [psi-core](psi/psi-core/index.md) | Ψhē核心哲学——ψ=ψ(ψ)自指递归方程、塌缩动力学、回声递归、观察者形成、语言涌现、现实结晶、元递归、统一回归（8概念+2示例+2信源） |
| [psi-math](psi/psi-math/index.md) | Ψhē数学形式化——theory_psi最小核心、坍缩集合论(CST)、黎曼猜想多路径证明、坍缩数学十大系统、物理常数坍缩起源、ZFC元数学批判（6概念+1示例+2信源） |
| [psi-universe](psi/psi-universe/index.md) | XOR-SHIFT宇宙本论——三大公理、FLIP/XOR/SHIFT操作层级、REC递归与元操作符、D0-D∞维度谱系、宇宙本体论(D10)、信息场与意识理论（6概念+1示例+2信源） |
| [godgpt](psi/godgpt/index.md) | GodGPT应用——AI灵性引导产品定位、深度共情/模式识别/扎根灵性智慧三大功能、订阅制+推广联盟商业模式、开曼群岛法律框架（4概念+1示例+2信源） |

### 📨 [消息通信生态](messaging/index.md)

| 知识束 | 简介 |
|--------|------|
| [libzmq](messaging/libzmq/index.md) | ZeroMQ C++ 核心库——四层管线(socket→pipe→session→engine)、socket_base_t模板方法、msg_t引用计数与零拷贝、ZMTP 3.x握手与帧编码、mailbox命令传递、io_thread/poller多路复用、fq/lb/dist路由算法、trie/mtrie订阅过滤 |
| [cppzmq](messaging/cppzmq/index.md) | C++ header-only绑定——RAII三巨头(context_t/socket_t/message_t)、sockopt类型安全选项、const_buffer/mutable_buffer内存抽象、poller_t多态事件多路复用、multipart_t高层多部分消息 |
| [pyzmq](messaging/pyzmq/index.md) | Python绑定——Cython/CFFI双后端可插拔、sugar纯Python语法层(Socket.send_string/json/pyobj/multipart)、asyncio子类覆写协程集成、attrsettr描述符选项系统、_future事件状态机、auth ZAP认证、eventloop/green/devices生态 |
| [dramatiq](messaging/dramatiq/index.md) | Python分布式任务队列——Actor装饰器双重身份、Broker防腐层(Redis/RabbitMQ/Stub)、Worker SEDA线程模型(ConsumerThread+WorkerThread+PriorityQueue)、Middleware洋葱模型、Message frozen dataclass信封、Encoder序列化、Results结果后端、CLI多进程+Watcher热重载 |
