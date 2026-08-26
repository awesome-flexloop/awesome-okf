---
type: category
title: "ONNX 机器学习生态"
okf_version: "0.2"
description: "ONNX（开放神经网络交换格式）生态系统源码级中文教程——8个核心知识包、109篇内容文档（含60概念+21示例+28信源），覆盖标准规范、IR、优化器、模型转换器、编译器与推理后端"
total_bundles: 8
total_content_docs: 109
total_md_files: 150
verified: grep-verified
generated: true
status: stable
---

# ONNX 机器学习生态知识库

本知识包分组收录 [ONNX（Open Neural Network Exchange）](https://onnx.ai) 生态系统各核心项目的系统化中文源码教程。ONNX 是机器学习模型的开放标准格式，定义了可扩展的计算图模型、内置算子和标准数据类型，实现不同深度学习框架之间的互操作性。

所有知识包遵循 [OKF v0.2 规范](../../meta/okf-spec/index.md)，通过源码深度阅读（R→I→E→V→C 五阶段链路）生成，所有API引用均经Grep级源码验证。

## 📊 知识包概览

| 层次 | 知识包 | 概念 | 示例 | 信源 | 内容文档 |
|------|--------|------|------|------|---------|
| 核心标准 | [onnx](onnx/index.md) | 14 | 4 | 8 | 26 |
| 核心标准 | [ir-py](ir-py/index.md) | 8 | 3 | 4 | 15 |
| 优化工具 | [optimizer](optimizer/index.md) | 7 | 2 | 3 | 12 |
| 模型转换 | [onnxmltools](onnxmltools/index.md) | 7 | 3 | 3 | 13 |
| 模型转换 | [sklearn-onnx](sklearn-onnx/index.md) | 6 | 3 | 3 | 12 |
| 模型转换 | [tensorflow-onnx](tensorflow-onnx/index.md) | 7 | 3 | 3 | 13 |
| 编译后端 | [onnx-mlir](onnx-mlir/index.md) | 6 | 1 | 2 | 9 |
| 编译后端 | [onnx-tensorrt](onnx-tensorrt/index.md) | 5 | 2 | 2 | 9 |
| **合计** | **8 知识包** | **60** | **21** | **28** | **109** |

> 注："内容文档"指 concepts/examples/references 目录下的实质性文档（不含各目录 index.md 导航页）。含导航索引、日志文件共 **150 个 .md 文件**。

## 核心标准层

| 知识包 | 简介 |
|--------|------|
| [onnx](onnx/index.md) | ONNX 标准本体——Protobuf IR 模型、计算图结构、算子注册机制（OpSchema）、形状推断、模型检查器、Python Helper API、C++ 核心 IR、序列化/反序列化、版本转换 |
| [ir-py](ir-py/index.md) | ONNX 纯 Python IR 参考实现——Model/Graph/Node/Value/Tensor 核心实体、双向链表图结构、TensorProtocol 张量协议、Tape 图变换、serde 序列化/反序列化、名称与元数据管理 |

## 优化工具层

| 知识包 | 简介 |
|--------|------|
| [optimizer](optimizer/index.md) | ONNX 模型优化器——Pass 基类体系（ImmutablePass/PredicateBasedPass/FullGraphBasedPass）、PassManager 定点迭代、40+内置优化Pass（常量折叠/死代码消除/算子融合）、Python/C++双API、自定义Pass开发 |

## 模型转换层

| 知识包 | 简介 |
|--------|------|
| [onnxmltools](onnxmltools/index.md) | 多框架转换器——CoreML/LightGBM/XGBoost/CatBoost/H2O/LibSVM 转 ONNX、Topology IR、转换器注册机制、类型系统、树模型转换、Pipeline与元数据 |
| [sklearn-onnx](sklearn-onnx/index.md) | scikit-learn 转换器——Pipeline/FeatureUnion 转换拓扑、ONNX算子代数、转换器注册机制、自定义转换器开发、分类器/回归器/预处理 |
| [tensorflow-onnx](tensorflow-onnx/index.md) | TensorFlow 转换器（tf2onnx）——Keras/SavedModel/tflite 转 ONNX、版本化算子集注册、GraphMatcher 图替换、图内部API、优化器Pass、数据布局与类型转换 |

## 编译器与后端层

| 知识包 | 简介 |
|--------|------|
| [onnx-mlir](onnx-mlir/index.md) | ONNX-MLIR 编译器——基于 LLVM/MLIR 的端到端编译栈、ONNX Dialect/Krnl Dialect、Lowering Pipeline、ExecutionSession 运行时、OMCompile 编译器驱动、PyRuntime Python绑定 |
| [onnx-tensorrt](onnx-tensorrt/index.md) | TensorRT 后端解析器（onnx2trt）——ModelImporter ONNX解析管线、算子注册与插件机制、ShapedWeights 权重内存模型、错误诊断与支持度查询、自定义Plugin开发 |

## 推荐学习路径

### 路径一：标准理解（核心规范）
```
📐 onnx（Protobuf IR + OpSchema + Checker）
  → 🔧 ir-py（Python IR 操作实践）
    → ⚡ optimizer（图优化原理）
```

### 路径二：模型部署（工程实践）
```
📐 onnx（理解模型结构）
  → 🔄 sklearn-onnx/tensorflow-onnx/onnxmltools（选择对应转换器）
    → ⚡ optimizer（优化模型）
      → 🚀 onnx-tensorrt（GPU推理部署）
         或 🏗️ onnx-mlir（原生编译部署）
```

## 生态关系概览

```
┌──────────────────────────────────────────────────────────────────┐
│                     模型转换器（Converters）                       │
│  tensorflow-onnx  sklearn-onnx  onnxmltools                      │
│  (TF/Keras)      (sklearn)     (CoreML/LGBM/XGB)                │
└───────────────────────┬──────────────────────────────────────────┘
                        │ 输出 ONNX 模型 (.onnx)
┌───────────────────────▼──────────────────────────────────────────┐
│                 onnx/（核心标准 · Protobuf IR）                   │
│  ModelProto · GraphProto · NodeProto · TensorProto               │
│  OpSchema 注册表 · Shape Inference · Checker · Helper API        │
│                 ir-py/（Python IR 操作层）                        │
│  双向链表图 · TensorProtocol · Tape变换 · serde序列化             │
└─────────┬──────────────────────────────────┬─────────────────────┘
          │ 加载/验证                         │ 优化变换
┌─────────▼──────────┐         ┌──────────────▼─────────────────────┐
│  optimizer/（优化器）│        │                                    │
│  40+ Pass 管线      │        │                                    │
│  常量折叠/融合/消除  │        │                                    │
└─────────┬──────────┘         │                                    │
          │ 优化后模型           │                                    │
┌─────────▼────────────────────▼────────────────────────────────────┐
│                 编译器与推理后端（Compilers & Backends）            │
│  onnx-mlir/（MLIR原生编译）       onnx-tensorrt/（TensorRT GPU）  │
│  ONNX Dialect → Krnl → LLVM      ModelImporter → Plugin → Engine │
│  ExecutionSession 运行时           ShapedWeights 权重管理         │
└──────────────────────────────────────────────────────────────────┘

   注：ONNX Runtime 等运行时后端不在本源码目录（external/libs/models/onnx/）内，未收录
```

## 信源与验证

- **源码根目录**：`external/libs/models/onnx/`
- **生成方法**：source-code-to-okf-wiki 技能（R→I→E→V→C 五阶段链路）
- **方法论指导**：seven-concepts-cmd（R→I→E 知识沉淀）
- **API验证**：43个关键API经Grep级源码验证（.py/.cc/.cpp/.h/.hpp/.proto）
- **链接验证**：613个内部链接0断链
- **frontmatter**：150个文件YAML元数据完整

```{toctree}
:maxdepth: 7

onnx/index
ir-py/index
optimizer/index
onnxmltools/index
sklearn-onnx/index
tensorflow-onnx/index
onnx-mlir/index
onnx-tensorrt/index
```
