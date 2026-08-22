---
type: concept
title: "ONNX Optimizer 整体架构"
description: "ONNX Optimizer 的三层架构：C++ 核心优化引擎、Python 薄绑定、C API 嵌入式入口，以及项目设计哲学与 IR 版本兼容处理"
sources:
  references: [../references/pass-base.md, ../references/pass-manager.md, ../references/python-c-api.md]
  facts: [F-001, F-002, F-003, F-004, F-005, F-011, F-012, F-040, F-042, F-043, F-054, F-056, F-060]
---

# ONNX Optimizer 整体架构

## 核心理解

ONNX Optimizer（v0.4.2，Apache-2.0 许可证）的核心动机是"在众多 ONNX 后端实现之间共享优化工作"——提供一套 C++ 优化库和预打包优化 passes，使任何 ONNX 后端都能通过单次函数调用复用所有可在 ONNX 图上直接实现的图重写优化，而不必各自重新实现。

整个系统采用**三层架构**：

```
┌─────────────────────────────────────────────────────────────┐
│                     用户接口层                               │
├──────────────┬──────────────────┬───────────────────────────┤
│  Python API  │   命令行 (CLI)   │       C API               │
│ optimize()   │ python -m        │ C_API_Optimize()          │
│ get_avail... │   onnxoptimizer  │ C_API_OtimizeFromFile()   │
├──────────────┴──────────────────┴───────────────────────────┤
│                   nanobind 薄绑定层                          │
│         onnx_opt_cpp2py_export （6个函数）                   │
├─────────────────────────────────────────────────────────────┤
│                     C++ 核心引擎                             │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────┐ │
│  │  Optimizer   │→│ PassManager  │→│ 50 个内置 Passes    │ │
│  │ (入口门面)   │  │ (执行引擎)   │  │ (Fuse/Nop/Separate)│ │
│  └─────────────┘  └──────────────┘  └─────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ GlobalPassRegistry（全局单例注册表，pass 名称→实例）     │ │
│  └─────────────────────────────────────────────────────────┘ │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────┐ │
│  │ model_util  │  │ pass_util    │  │ data_type           │ │
│  │ (模型IO)    │  │ (工具函数库) │  │ (FP16/BF16/复数)    │ │
│  └─────────────┘  └──────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## C++ 核心层：所有逻辑的实现所在

C++ 层是 ONNX Optimizer 的**真正实现层**，所有核心逻辑——Pass 基类体系、PassManager 执行引擎、50 个内置优化 passes、模型加载/保存、外部数据处理——全部在 C++ 中实现。

核心组件：

| 组件 | 头文件 | 职责 |
|------|--------|------|
| Pass 基类体系 | `pass.h` | 定义优化 pass 的抽象接口和三类继承基类 |
| PassManager | `pass_manager.h` | pass 执行引擎（线性/定点） |
| GlobalPassRegistry | `pass_registry.h` | 全局 pass 注册表（单例） |
| Optimizer | `optimize.h` | C++ 层入口门面，封装 proto↔Graph 转换 |
| model_util | `model_util.h` | 模型加载/保存/外部数据处理 |
| pass_util | `passes/pass_util.h` | Pass 开发工具函数库 |
| 内置 passes | `passes/*.h` | 50 个具体优化 pass 实现 |

所有代码位于 `ONNX_NAMESPACE::optimization` 命名空间下。

## Python 绑定层：极薄的封装

Python 层不是独立的优化实现，而是通过 **nanobind**（注意不是 pybind11）绑定 C++ 函数的极薄封装。Python `optimize()` 函数的主要工作是：

1. **序列化/反序列化**：将 Python 端的 ModelProto 对象序列化为字节串传给 C++，再反序列化结果
2. **大模型回退**：当模型超过 2GB 触发 protobuf `ValueError` 时，自动回退到临时文件路径
3. **默认参数处理**：`passes=None` 时使用默认的 fuse+elimination 集合

核心优化逻辑全部在 C++ 中完成，Python 层不实现任何图变换算法。

## C API 层：嵌入式入口

C API（`c_api/onnxoptimizer_c_api.h`）为非 C++/Python 语言提供嵌入能力，同样是薄封装。提供两种调用模式：

- **内存缓冲模式**：`C_API_Optimize()` 接收/返回序列化字节缓冲
- **文件模式**：`C_API_OtimizeFromFile()`（注意拼写错误）通过文件路径输入输出

> ⚠️ **已知 API 缺陷**：`C_API_OtimizeFromFile` 函数名拼写缺少 'p'（`Otimize`），因 C ABI 兼容性无法修复，调用者需注意。

## IR 版本自动升级

`Optimizer::optimize()` 隐含了一个关键的兼容性处理：当输入模型的 IR 版本为 3 时，自动升级到 IR v4。IR v4 的核心变化是 **initializer 不必同时出现在 graph input 列表中**，这使得优化器可以将 Constant 节点提取为 initializer 而无需同时修改 input 列表。

这一升级是静默的——输出模型的 IR 版本将是 v4 而非原始的 v3，下游工具如果严格检查 IR 版本需要注意此行为。

若模型 IR 版本过旧导致 `ImportModelProto()` 返回 nullptr，optimizer 输出警告并直接返回原始模型（不做任何优化）。

## 实验性声明

所有核心源码文件均标注：

> *"The code in this file is highly EXPERIMENTAL. Adventurous users should note that the APIs will probably change."*

README 明确列出 Roadmap 第一项是"分离图重写与常量折叠"（或纯图重写模式），说明核心团队认识到当前架构在常量折叠等全局分析方面的局限。

## 设计哲学

ONNX Optimizer 遵循以下设计原则：

1. **保守默认**：`get_fuse_and_elimination_passes()` 默认只做等价的算子融合和无用操作消除，不做图结构拆分或算子替换
2. **C++ 为核心**：所有逻辑在 C++ 实现，保证性能和可嵌入性
3. **薄绑定原则**：Python/C API 层只做绑定和参数适配，不复制逻辑
4. **注册驱动**：所有 pass 通过 `GlobalPassRegistry` 注册，添加新 pass 只需注册即可被发现和执行
5. **定点收敛**：对非幂等 pass 提供 FixedPointPassManager 反复执行直到收敛

## 关联概念

- [Pass 系统：基类继承体系与注册机制](01-pass-system.md) — 深入 Pass 类层次和注册机制
- [PassManager 执行模型与定点收敛](03-pass-execution.md) — 了解 pass 的执行和收敛机制
- [内置优化 Passes 分类详解](02-builtin-passes.md) — 了解 50 个内置 pass 的功能
- [Python/CLI/C API 使用指南](05-python-cli-api.md) — 了解三层 API 的具体使用方式
