---
type: Concept
title: ncnn 整体架构
description: ncnn 为移动端优化的高性能神经网络推理框架，纯 C++ 零第三方依赖，CPU/GPU 双后端，覆盖 x86/ARM/MIPS/RISC-V/LoongArch 全架构。
tags: [ncnn, architecture, overview]
generated: { by: "reference_agent/trae-solo", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: facts
    resource: /spec/facts.md
    title: ncnn 源码事实采集
---

# ncnn 整体架构

ncnn 是腾讯优图实验室开源的高性能神经网络推理框架，专为移动端、嵌入式和边缘设备设计。版本 1.0.20260526，BSD-3-Clause 许可证，已在 QQ、Qzone、微信、天天 P 图等产品中部署。

## 核心设计原则

### 纯 C++ 零第三方依赖

ncnn 不依赖 BLAS、NNPACK、Protobuf 或任何其他第三方库。为在极端环境下可编译，它在 `src/` 下内嵌了五套最小替代实现：

| 内嵌实现 | 替代对象 | CMake 选项 |
|---|---|---|
| `simplestl.h/.cpp` | C++ STL（vector/string） | `NCNN_SIMPLESTL` |
| `simpleomp.h` | OpenMP 运行时 | `NCNN_SIMPLEOMP` |
| `simpleocv.h` | OpenCV 基础结构 | `NCNN_SIMPLEOCV` |
| `simplemath.h` | libm | `NCNN_SIMPLEMATH` |
| `simplevk.h` | Vulkan loader | `NCNN_SIMPLEVK`（默认 ON） |

这意味着即使在无 STL、无异常、无 RTTI 的裸机环境下，ncnn 仍可编译（F-100、F-104）。

### CPU/GPU 双后端统一抽象

ncnn 通过同一个 [`Layer`](03-layer-abstraction.md) 基类同时支持 CPU（`Mat`）和 GPU（`VkMat`）推理。每个算子可选择性实现 CPU `forward` 和/或 Vulkan `forward`，运行时由 [`Option::use_vulkan_compute`](05-option-config.md) 开关选择后端。

### 全架构覆盖

`src/layer/` 下为每个 CPU 架构维护独立的 SIMD 优化目录（F-103）：

```
src/layer/
├── arm/       265 文件  (NEON/VFPv4/ASIMDHP/ASIMDDP/SVE/SVE2/I8MM)
├── x86/       282 文件  (SSE2/AVX/AVX2/AVX512/FMA/F16C/VNNI)
├── mips/      163 文件  (MSA/Loongson MMI)
├── riscv/     180 文件  (RVV/Zfh/Zvfh)
├── loongarch/ 170 文件  (LSX/LASX)
└── vulkan/    128 文件  (SPIR-V compute shader)
```

编译期所有 kernel 全部保留，运行时由 [`ruapu.h`](07-simd-packing.md) 检测 CPU 能力后选择最优路径（胖二进制策略）。

## 模块分层

```
┌─────────────────────────────────────────────┐
│  应用层  examples/  python/  benchmark/      │
├─────────────────────────────────────────────┤
│  Net / Extractor   (模型加载 + 推理调度)      │
├─────────────────────────────────────────────┤
│  Layer 基类 + 110+ 算子实现                  │
│  (CPU forward / Vulkan forward / inplace)    │
├──────────────┬──────────────────────────────┤
│  Mat 张量    │  VkMat / VkImageMat          │
│  (引用计数)   │  (Vulkan 设备缓冲)           │
├──────────────┴──────────────────────────────┤
│  Allocator / PoolAllocator / VkAllocator    │
│  Option / ParamDict / ModelBin / DataReader │
├─────────────────────────────────────────────┤
│  ruapu CPU 检测  ·  simplevk Vulkan loader  │
│  simpleomp/stl/ocv/math 内嵌替代            │
└─────────────────────────────────────────────┘
```

## PIMPL 模式

所有公共管理类（[`Net`](01-net-extractor.md)、`Extractor`、`PoolAllocator`、`Pipeline`、`VulkanDevice` 等）均采用 `XxxPrivate* const d` 指针隐藏实现。这保证了：

1. 公共头文件不暴露 STL 容器和平台相关类型；
2. 动态库 ABI 稳定，跨编译器版本兼容；
3. 编译防火墙——修改实现不需要重编译包含头文件的用户代码。

而热路径上的 [`Mat`](02-mat-tensor-system.md) 和 `Layer` 不用 PIMPL，直接内联字段以避免间接访问开销。

## 模型格式

ncnn 使用自有的 `.param`（网络结构）和 `.bin`（权重）二进制格式，无需 Protobuf。结构由 [`ParamDict`](08-paramdict-modelbin.md) 解析文本参数，[`ModelBin`](08-paramdict-modelbin.md) 加载权重数据，[`DataReader`](08-paramdict-modelbin.md) 抽象文件/内存/Android Asset 三种来源。

## 相关概念

- [01 Net 与 Extractor 推理流程](01-net-extractor.md)
- [02 Mat 张量系统](02-mat-tensor-system.md)
- [03 Layer 抽象层](03-layer-abstraction.md)
- [06 Vulkan GPU 后端](06-vulkan-gpu.md)
- [07 SIMD 打包存储](07-simd-packing.md)
