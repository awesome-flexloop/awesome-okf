---
okf_version: "0.2"
---

# ONNX 机器学习生态知识库

本知识包分组收录 [ONNX（Open Neural Network Exchange）](https://onnx.ai) 生态系统各核心项目的系统化中文源码教程。ONNX 是机器学习模型的开放标准格式，定义了可扩展的计算图模型、内置算子和标准数据类型，实现不同深度学习框架之间的互操作性。

所有知识束遵循 [OKF v0.2 规范](../meta/okf-spec/index.md)，通过源码深度阅读（R→I→E→V→C 五阶段链路）生成。

## 核心标准层

| 知识束 | 简介 |
|--------|------|
| [onnx](onnx/index.md) | ONNX 标准本体——Protobuf IR 模型、计算图结构、算子注册机制（OpSchema）、形状推断、模型检查器、Python Helper API、C++ 核心 IR、序列化/反序列化、参考后端 |
| [ir-py](ir-py/index.md) | ONNX 纯 Python IR——Model/Graph/Node/Value 核心实体、零拷贝张量、Tape 图变换、序列化/反序列化、mmap 支持 |

## 优化工具层

| 知识束 | 简介 |
|--------|------|
| [optimizer](optimizer/index.md) | ONNX 模型优化器——Pass 系统、常量折叠、死代码消除、算子融合、命令行 API |

## 模型转换层

| 知识束 | 简介 |
|--------|------|
| [onnxmltools](onnxmltools/index.md) | 多工具包转换器——CoreML/LightGBM/XGBoost/CatBoost/H2O 等转 ONNX |
| [sklearn-onnx](sklearn-onnx/index.md) | scikit-learn 转换器——Pipeline 转换、算子映射、自定义转换器注册 |
| [tensorflow-onnx](tensorflow-onnx/index.md) | TensorFlow 转换器（tf2onnx）——Keras/SavedModel/tflite 转 ONNX、图替换机制 |

## 编译器与后端层

| 知识束 | 简介 |
|--------|------|
| [onnx-mlir](onnx-mlir/index.md) | ONNX-MLIR 编译器——基于 LLVM/MLIR 的 ONNX 编译栈、ONNX Dialect、编译流程、运行时接口 |
| [onnx-tensorrt](onnx-tensorrt/index.md) | TensorRT 后端解析器——ONNX 模型解析、算子支持、插件机制 |

## 推荐学习路径

```
📐 onnx（核心标准）→ 🔧 ir-py（Python IR）→ ⚡ optimizer（优化器）
  → 🔄 onnxmltools/sklearn-onnx/tensorflow-onnx（转换器）
    → 🏗️ onnx-mlir（编译器）→ 🚀 onnx-tensorrt（推理后端）
```

## 生态关系概览

```
┌─────────────────────────────────────────────────────────────┐
│                   模型转换器（Converters）                    │
│  tensorflow-onnx  sklearn-onnx  onnxmltools                 │
└──────────────────────┬──────────────────────────────────────┘
                       │ 生成 ONNX 模型
┌──────────────────────▼──────────────────────────────────────┐
│              onnx/（核心标准与 Protobuf IR）                 │
│  计算图 · 算子定义 · 类型系统 · 检查器 · Helper API          │
│              ir-py/（Python IR 操作层）                      │
│  零拷贝张量 · Tape 变换 · 序列化                             │
└──────────┬───────────────────────────────┬──────────────────┘
           │ 加载模型                       │ 优化
┌──────────▼──────────┐     ┌──────────────▼───────────────┐
│  optimizer/（优化器）│     │                              │
│  常量折叠/算子融合   │     │                              │
└──────────┬──────────┘     │                              │
           │ 优化后模型      │                              │
┌──────────▼────────────────▼──────────────────────────────┐│
│              编译器与后端（Compilers & Backends）          ││
│  onnx-mlir/（MLIR 编译器）  onnx-tensorrt/（TRT 后端）    ││
└──────────────────────────────────────────────────────────┘│
                                                            │
   （ONNX Runtime、其他后端不在本源码目录内，未收录）         │
└─────────────────────────────────────────────────────────────┘
```
