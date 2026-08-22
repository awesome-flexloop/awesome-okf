---
okf_version: "0.2"
type: bundles-index
title: "知识束总索引"
description: "awesome-okf-xs 知识束（bundles）分组导航——按技术生态组织的开源项目源码中文教程"
total_bundles: 44
groups: 11
---

# 知识束总索引（Bundles Index）

> **OKF (Open Knowledge Format)** 知识束是面向开源项目源码与AI平台的系统化中文教程，遵循 [OKF v0.2 规范](meta/okf-spec/index.md)，每个知识束包含概念文档（concepts/）、实战示例（examples/）、信源参考（references/）三层结构。
>
> 当前共 **44 个知识束**，按技术生态分为 **11 个分组**。

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
| [🤖 AI Agent 框架](ai-agent/index.md) | 1 | AI Agent运行时框架——Agent循环、工具系统、记忆架构、多代理编排、插件架构、通信协议 |
| [📊 PyData 科学计算生态](pydata/index.md) | 6 | NumPy/pandas/matplotlib/Plotly/Dash/PyTables——数值计算、数据分析、可视化、Web应用、HDF5存储 |
| [🧠 ONNX 机器学习生态](onnx/index.md) | 8 | ONNX标准/IR-Python/优化器/ONNXMLTools/sklearn-onnx/tf2onnx/onnx-mlir/onnx-tensorrt——跨框架模型交换、转换器、编译器、推理后端 |

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
| [ai-agent](ai-agent/ai-agent/index.md) | AI Agent框架核心架构——Agent循环、工具系统（注册表/Capability Seam）、记忆架构（ST/LT/HMM三层）、多代理编排（MoA/Workspace/Subagent）、Provider抽象、上下文管理（压缩/知识蒸馏）、技能Persona系统（SKILL.md/280+角色）、插件架构（Cordis Fiber/Context原型链）、通信协议（MCP/ACP/COM/OSC）（10概念+4示例+1信源，共15文档） |

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
