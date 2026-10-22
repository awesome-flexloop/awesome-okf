---
type: bundle
okf_version: "0.2"
scope: deepinfer
name: DeepInfer Wiki
version: "0.1.0"
source: https://github.com/deepseek-ai/DeepInfer
description: DeepInfer - DeepSeek 大规模生产推理框架源码中文教程，支持 DeepSeek-V4.1-Flash、NVIDIA SM100 与华为昇腾 950 双平台
sources:
  - id: deepinfer-github
    resource: https://github.com/deepseek-ai/DeepInfer
    title: DeepInfer 官方仓库
  - id: deepseek-announce
    resource: https://mp.weixin.qq.com/s?__biz=Mzk0OTYwNzc3NQ%3D%3D&mid=2247485884&idx=1&sn=d457981abe7db1f1b5d600fc109dc836
    title: DeepSeek 开源推理框架：走向真正普惠的未来（DeepSeek 官方公众号，2026-10-20）
  - id: deepseek-zhihu-report
    resource: https://zhuanlan.zhihu.com/p/2095560295930508953
    title: DeepSeek V4.1 Flash 大规模推理部署实践（DeepSeek 官方技术报告）
---

# DeepInfer

**DeepInfer** 是 DeepSeek 驱动其大规模生产服务的**高性能推理框架**，于 2026-10-20 全面开源（Apache-2.0）。它基于 [vLLM](https://github.com/vllm-project/vllm) 改造（多数文件标注 "Derived from vLLM; modified by DeepSeek"），并吸收了 SGLang 与 TensorRT-LLM 的设计灵感。基于 DeepInfer，DeepSeek 已实现 **DeepSeek V4.1 Flash 高吞吐、低延迟的大规模推理服务**；未来新模型的推理代码与性能优化也将持续在该仓库更新。

- **引擎版本**：0.1.0（`deepinfer/__init__.py`）
- **支持模型**：DeepSeek-V4.1-Flash（默认 checkpoint `deepseek-ai/DeepSeek-V4.1-Flash-1017`）
- **支持硬件**：NVIDIA SM100 GPU（CUDA 13）· 华为昇腾 950 NPU（CANN 9.2）
- **前置环境**：Linux · GCC ≥ 13 · Python 3.12

---

## 核心能力

| 能力 | 说明 |
|---|---|
| **优化算子与运行时** | 集成 FlashMLA / DeepGEMM / DeepEP / TileKernels / DeepSelect 与自研 TileLang 核 |
| **并行策略** | Attention DP / balanced CP、MoE EP + EPLB 专家负载均衡 |
| **DSpark 推测解码** | draft token 加速 + confidence 调度变长验证（变长验证较固定验证吞吐 +6%） |
| **SWA Bounded Replay** | 只重算最近 128 token 的有界回放，decoder prefill 计算量近乎减半 |
| **异步调度** | Zero-Overhead Batch Scheduler，CPU 调度与 GPU 执行流水线重叠，默认开启 |
| **Batch 不变推理** | 不同 batch 组合下结果一致（`DEEPINFER_BATCH_INVARIANT=1`，NVIDIA only） |
| **确定性采样** | 相同输入 token 与采样参数产生相同输出（需固定 `seq_seed`） |
| **结构化输出** | 约束生成符合 regex / JSON Schema / EBNF 文法（xgrammar 编译 + bitmask 掩码） |

---

## 生产运营数据（官方公开）

| 指标 | 数值 | 来源 |
|---|---|---|
| 单一集群服务吞吐 | 155 万亿 Tokens/天 | 知乎技术报告 |
| 整体收入 | 每卡每小时 38 美金（按谷价） | 知乎技术报告 |
| Block KVCache 存储 | 约 100 PiB SSD（3FS 集群） | 知乎技术报告 |
| 峰值聚合读带宽 | 10 TiB/s（写 850 GiB/s） | 知乎技术报告 |
| SWA KVCache 命中率 | 98%+（TTL 约 180 秒） | 知乎技术报告 |
| MoE 负载不均衡度 | moe_lb = 1.0320（EP2/DP2 prefill） | 知乎技术报告 |

---

## 开源边界：开箱即用 vs 需自建

README 明确列出**完整推理服务所需、但不在本次开源内**的组件：

1. **KV cache 系统**（生产实现依赖 3FS 分布式文件系统）
2. **VE / Prefill / Decode 分离**（引擎内大部分功能已实现，但部署编排需自建）
3. **跨 data-parallel 副本的负载均衡**（prefill 与 decode 两侧）

> 官方说法："KVCache 管理与负载均衡组件因与内部基础设施耦合较深，相关代码目前尚未完整开源。"对应的生产架构设计（四层负载均衡 / KVCache 存储 / 自动扩缩容）以[部署实践](concepts/deployment-practice.md)专章讲解。

---

## 文档导航

### 📘 核心概念 [concepts/](concepts/index.md)

| 文档 | 内容 |
|---|---|
| [概述](concepts/overview.md) | 项目定位、支持矩阵、目录结构、构建与快速开始 |
| [引擎架构](concepts/architecture.md) | LLMEngine、C++ 调度器、ZOS 零开销调度流水线 |
| [并行策略](concepts/parallelism.md) | EP/DP/CP/EPLB、deep_cluster 硬件探测层、Wide-EP |
| [DSpark 推测解码](concepts/speculative-decoding.md) | DFlash 草稿模型、ConfidenceHead、变长验证 |
| [结构化输出](concepts/structured-output.md) | xgrammar 编译/匹配、token bitmask、编译与推理解耦 |
| [大规模部署实践](concepts/deployment-practice.md) | 生产架构：四层负载均衡、KVCache 存储、自动扩缩容 |

### 📙 代码示例 [examples/](examples/index.md)

| 示例 | 内容 |
|---|---|
| [离线推理](examples/offline-inference.md) | offline_inference.py 用法、并行参数、VL 回归、PPL 基线 |
| [性能基准](examples/benchmark.md) | benchmark.py 三大指标、sweep 与 Pareto 曲线 |

### 📗 API 参考 [references/](references/index.md)

| 文档 | 内容 |
|---|---|
| [环境变量](references/env-vars.md) | DEEPINFER_* 配置体系总表 |
| [外部资源](references/resources.md) | 官方报告、论文、关联仓库链接 |

---

## 快速开始

### 构建安装

```bash
# 创建并激活空的 Python 3.12 环境
# nvidia 或 ascend 二选一，保持导出
export DEEPINFER_ACCELERATOR=nvidia
./build.sh
```

`build.sh` 流程：校验平台变量 → 安装 `requirements-<平台>.txt` →（nvidia）强制 NCCL 2.32.3 → `scripts/build_vendor.sh` 编译 vendor 算子轮子 → 编译主扩展并符号链接入 `deepinfer/_so/<accelerator>-<arch>/`。构建后无需 `pip install -e .`，示例脚本自动注入仓库根到 `sys.path`。

### 离线推理

```bash
python examples/offline_inference.py          # 默认 --ep 8
python examples/offline_inference.py --ep 2 --dp 8
python examples/offline_inference.py --ep 2 --cp 8
```

首次运行自动从 Hugging Face 下载 `DeepSeek-V4.1-Flash-1017`；`DEEPINFER_HF_MODEL_DIR` 指向本地副本可离线运行。

---

## 相关项目

| 项目 | 关系 |
|---|---|
| [deepseek-recipe](../deepseek-recipe/index.md) | 同步开源的生产级 Token 编解码组件——API 协议与 token 序列双向转换，与 DeepInfer 组成完整推理中间层 |
| [FlashMLA](../flash-mla/index.md) | DeepInfer 集成的 MLA 注意力核函数库（vendor submodule） |
| [DeepGEMM](../deep-gemm/index.md) | DeepInfer 集成的高性能 GEMM 核函数库（vendor submodule） |
| [DeepEP](../deep-ep/index.md) | DeepInfer 集成的 MoE 专家并行通信库（vendor submodule） |
| [TileKernels](../tile-kernels/index.md) | DeepInfer 依赖的 TileLang DSL 核函数库（PyPI 依赖 `tile-kernels==2.1.0`） |
| [vLLM](https://github.com/vllm-project/vllm) | DeepInfer 的代码基座（Derived from vLLM） |

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
spec/facts
spec/insights
```
