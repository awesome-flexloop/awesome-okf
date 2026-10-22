---
type: ExampleIndex
title: "Examples 索引：Humming 四类典型场景"
description: "Humming 实战示例集——稠密量化 GEMM、MoE GEMM、vLLM 服务化与基准对拍，覆盖 HummingLayer 三步生命周期、grouped 布局构造、后端切换与性能对拍四类高频用法"
tags: [humming, examples, dense-gemm, moe, vllm-serving, benchmarking]
generated: { by: seven-concepts-cmd+source-code-to-okf-wiki/E, at: "2026-10-22T23:40:00+08:00" }
status: stable
stale_after: 2027-04-22
sources:
  - id: local-source
    resource: /references/source-map.md
    title: 本地源码检出登记
---

# Examples 索引：Humming 四类典型场景

本目录包含 Humming v0.1.18 的实践示例，按「跑通 → 进阶形态 → 服务化 → 度量」组织，覆盖四个最高频使用场景。所有命令与代码基于源码快照，可在 NVIDIA SM75+ 环境复现。

## 示例列表

| 示例 | 场景 | 涵盖主题 |
|------|------|---------|
| [01 稠密量化 GEMM](01-dense-gemm.md) | 库内直接调用 | `HummingLayer` 三步生命周期、位宽与精度扫描、误差判读、性能基线 |
| [02 MoE GEMM](02-moe-gemm.md) | 库内直接调用 | 四种 GEMM 形态选择、grouped 布局构造、专家负载不均模拟、栅格化调优 |
| [03 vLLM 服务化](03-vllm-serving.md) | 框架集成 | 三条接入路径、命令行参数、生效验证、常见错误排查、生产部署建议 |
| [04 基准对拍](04-benchmarking.md) | 性能度量 | 复用五套 harness、读懂归档结果命名、自写对拍脚本、cold L2 cache 测法 |

## 按场景分类

### 入门闭环

- [01 稠密量化 GEMM](01-dense-gemm.md)：从 `HummingLayer` 出发，跑通 install → load → transform → call 的最小闭环，建立「相对误差 + 归一化 MSE + 方向性偏差」三指标判读标准。

### 进阶形态

- [02 MoE GEMM](02-moe-gemm.md)：构造 grouped 布局，理解 `sorted_ids` / `expert_ids` / `num_tokens_padded` 三参数的配合，用负载波动系数（cv）诊断专家不均衡。

### 服务化

- [03 vLLM 服务化](03-vllm-serving.md)：一条命令启用 Humming 后端，四种方法验证是否真的生效，覆盖 gpt-oss + mxfp4 报错等已知坑。

### 性能验证

- [04 基准对拍](04-benchmarking.md)：复用项目自带 harness 与归档结果，建立带统计判据的自有基线。

## 前置知识

建议先阅读：

- [01 快速开始](../concepts/01-quickstart.md)：安装与最小闭环
- [02 量化模型](../concepts/02-quantization-model.md)：类型与位宽约束
- [07 vLLM 集成](../concepts/07-vllm-integration.md)：三条接入路径的机制

## 运行环境

- Humming v0.1.18（本地检出 `v0.1.18-1-g5b500b4`，2026-10-21）
- Python ≥ 3.10；运行期依赖共 8 项，以 `torch>=2.7` 为主（F-005）
- NVIDIA SM75+（Turing）起；BF16 需 SM80+，FP8 需 SM89+，FP4 需 SM100/SM120
- 示例 03 需 vLLM 且其 `requirements/cuda.txt` 含 `humming-kernels`（自 vLLM v0.22.0 起）
- 示例 04 建议独占 GPU（cold L2 cache 测法对并发敏感）

```{toctree}
:maxdepth: 2

01-dense-gemm
02-moe-gemm
03-vllm-serving
04-benchmarking
```
