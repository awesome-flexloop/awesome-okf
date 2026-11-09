---
okf_version: "0.2"
type: group
title: "🧠 机器学习模型生态"
description: "机器学习模型互操作、部署生态与深度学习框架张量语义——跨框架模型格式 ONNX 及其标准/转换器/优化器/编译器/推理后端，Apache TVM、CAFFE、PyTorch 张量布局（view/reshape/contiguous），以及 TVM TIRx 两代编译基础层（layout/dispatch、54 配置基准）"
---

# 🧠 机器学习模型生态

本域存放机器学习模型互操作与部署相关的知识包，以 ONNX（开放神经网络交换格式）生态为核心，覆盖模型标准、Python IR、优化器、多框架转换器、编译器与推理后端；并包含深度学习框架层面的张量内存布局语义（shape/stride/连续性）、Apache TVM 编译栈，以及面向 Agent 时代的 TVM TIRx 编译基础层。

## 域内分组导航

| 分组 | 一句话简介 |
|------|-----------|
| [🧠 ONNX 机器学习生态](onnx/index.md) | ONNX 开放神经网络交换格式生态——标准、IR、优化器、转换器、编译器与推理后端 |
| [⚙️ Apache TVM 深度学习编译器](apache-tvm/index.md) | Apache TVM 四层架构源码中文教程——FFI 基础设施、TIR 张量 IR、Relax 图级 IR 与 Runtime 执行引擎 |
| [☕ CAFFE 架构分析](caffe/index.md) | CAFFE 深度学习框架架构分析——依赖结构、序列化、构建实践、现代化改造与反模式防御 |
| [🔧 PyTorch 张量布局（view/reshape）](pytorch-view-reshape/index.md) | PyTorch 张量语义教程——view()/reshape() 机制、stride 布局、transpose/permute 后的连续性与 contiguous() 内存成本 |
| [🧱 TVM TIRx 编译基础层](tvm-tirx/index.md) | 两代 TIRx 教程——2026-06 硬件原生 kernel DSL（layout/dispatch、54 配置基准）到 2026-11 Agent 时代极简基础层 |

```{toctree}
:hidden:
:maxdepth: 7

onnx/index
apache-tvm/index
caffe/index
pytorch-view-reshape/index
tvm-tirx/index
```
