---
type: ConceptIndex
title: "concepts/ 概念文档"
description: "Humming 知识包概念层——按「入门 → 核心模块 → 场景 → 进阶」四段组织，覆盖项目身份、快速开始、量化模型、架构、内核设计、调优、MoE、vLLM 集成、性能与进阶主题十篇"
tags: [humming, concepts, index, 导航]
generated: { by: seven-concepts-cmd+source-code-to-okf-wiki/E, at: "2026-10-22T23:40:00+08:00" }
status: stable
stale_after: 2027-04-22
---

# concepts/ 概念文档

本知识包的概念层按「入门 → 核心模块 → 场景 → 进阶」四段组织（源自 Humming v0.1.18 源码 + vllm.ai 官方博客 + vLLM 集成侧源码 + 作者知乎自述，R→I→E→V 转化；操作可复现性两问均中，故设 examples/）。

| 层次 | 文档 | 说明 |
|------|------|------|
| 入门 | [00 Humming 是什么](00-overview.md) | 身份卡片、与 Marlin/DeepGEMM 的关系、vLLM 生态位、适用边界 |
| 入门 | [01 快速开始](01-quickstart.md) | 安装 → 三步生命周期 → 对拍 → 缓存管理 → 常见报错 |
| 核心 | [02 量化模型](02-quantization-model.md) | 权重×激活支持矩阵、scale 粒度四态、schema 注册表、类型约束判定 |
| 核心 | [03 架构总览](03-architecture.md) | 三层配置分工、GEMM/MMA 四型、JIT 编译栈、13 项算子出口 |
| 核心 | [04 内核设计](04-kernel-design.md) | 三条流水线、CUDA 七层组件、权重 repack 与 packing 层级、反量化三路径 |
| 核心 | [05 调优与启发式](05-tuning.md) | 设备启发式分派、算力/带宽瓶颈判定、M 维候选与对齐、栅格化调度 |
| 核心 | [06 MoE 路径](06-moe.md) | 四种 GEMM 形态、MoE 专属参数、激活表达式翻译、端到端实测 |
| 场景 | [07 vLLM 集成](07-vllm-integration.md) | 三条接入路径、12 个权重 schema、版本依赖钉、kernel 选择优先级 |
| 进阶 | [08 性能与基准](08-performance.md) | 基准方法六项条件、全组加速倍数、自建 benchmark 体系 |
| 进阶 | [09 进阶主题](09-advanced.md) | 未文档化浮点格式、CUBIN 补丁与架构白名单、路线图三方向 |

## 推荐阅读顺序

| 读者 | 顺序 |
|------|------|
| 第一次接触 | 00 → 01 → [01 稠密量化 GEMM](../examples/01-dense-gemm.md) |
| 要接进 vLLM | 00 → 07 → [03 vLLM 服务化](../examples/03-vllm-serving.md) → 08 |
| 要读源码 | 03 → 04 → 05 → 02 |
| 要评性能 | 08 → [04 基准对拍](../examples/04-benchmarking.md) |

```{toctree}
:hidden:
:maxdepth: 2

00-overview
01-quickstart
02-quantization-model
03-architecture
04-kernel-design
05-tuning
06-moe
07-vllm-integration
08-performance
09-advanced
```
