---
okf_version: "0.2"
type: group
title: "🧠 机器学习模型生态"
description: "机器学习模型互操作、部署生态与深度学习框架张量语义——跨框架模型格式 ONNX 及其标准/转换器/优化器/编译器/推理后端，Apache TVM、CAFFE，以及 PyTorch 张量布局（view/reshape/contiguous）"
---

# 🧠 机器学习模型生态

本域存放机器学习模型互操作与部署相关的知识包，以 ONNX（开放神经网络交换格式）生态为核心，覆盖模型标准、Python IR、优化器、多框架转换器、编译器与推理后端；并包含深度学习框架层面的张量内存布局语义（shape/stride/连续性），服务模型训练与部署中的维度转换与内存优化。

## 域内分组导航

| 分组 | 一句话简介 |
|------|-----------|
| [🧠 ONNX 机器学习生态](onnx/index.md) | ONNX 开放神经网络交换格式生态——标准、IR、优化器、转换器、编译器与推理后端 |
| [⚙️ Apache TVM 深度学习编译器](apache-tvm/index.md) | Apache TVM 四层架构源码中文教程——FFI 基础设施、TIR 张量 IR、Relax 图级 IR 与 Runtime 执行引擎 |
| [☕ CAFFE 架构分析](caffe/index.md) | CAFFE 深度学习框架架构分析——依赖结构、序列化、构建实践、现代化改造与反模式防御 |
| [🔧 PyTorch 张量布局（view/reshape）](pytorch-view-reshape/index.md) | PyTorch 张量语义教程——view()/reshape() 机制、stride 布局、transpose/permute 后的连续性与 contiguous() 内存成本 |

```{toctree}
:hidden:
:maxdepth: 7

onnx/index
apache-tvm/index
caffe/index
pytorch-view-reshape/index
```
