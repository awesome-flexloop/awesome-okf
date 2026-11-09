---
type: Concept
title: 性能证据——54 配置 B200 基准怎么读
description: 解读第一代 TIRx 在 B200 上的 GEMM/低精度 GEMM/FlashAttention-4 共 54 个配置的基准结果、实验设置、可比边界与不可外推的结论
tags: [tvm-tirx, benchmark, gemm, flashattention, b200, 性能, 证据]
generated: { by: seven-concepts-cmd/1.1.0, at: 2026-11-09T00:00:00+08:00 }
verified: { by: process:seven-concepts-v, at: 2026-11-09T00:00:00+08:00 }
status: stable
stale_after: 2027-02-09
sources:
  - id: june-blog
    resource: https://tvm.apache.org/2026/06/22/tirx
  - id: june-zhihu
    resource: https://zhuanlan.zhihu.com/p/2052656701392920995
---

# 性能证据：54 配置 B200 基准

> 文中 `[F-xxx]` 为编号事实，来源见 [facts.md](../references/facts.md)。
> ⚠️ **适用范围**：这些数字测于 **第一代 TIRx（`apache-tvm` 0.25.0）**，不是第二届独立包 `apache-tvm-tirx` 0.1.0b1 [F-099]。本次未独立复现。

## 1. 实验设置

| 项 | 配置 |
|----|------|
| 硬件 | 4× NVIDIA B200（SM100）[F-081] |
| 软件 | driver 595.58.03，CUDA 13.2，PyTorch 2.12.0+cu132 [F-081] |
| 配置数 | 54 个 [F-081] |
| 计时 | Proton，warmup 100，repeat 30，5 轮独立测量取平均 [F-081] |
| 指标 | sustained TFLOPS；GEMM 用 `2MNK`，FA4 用 `4·B·H·S²·D`（B=1，D=128；causal 乘 0.5）[F-081] |
| 对比 | 每个配置取适用的 SOTA baseline 中最快者 [F-081] |

工作负载构成 [F-081]：

- FP16 / BF16 GEMM：各 5 个方阵尺寸，1024³ → 16384³；
- FP8 blockwise GEMM：7 个 DeepGEMM-style 形状；
- NVFP4 GEMM：5 个方阵尺寸；
- FlashAttention-4：32 个配置（序列 1024–8192，heads 4/8/16/32，causal 与非 causal）。

## 2. 结果

### 2.1 Dense GEMM（FP16 / BF16）

| 形状 | TIRx | 最佳 baseline | 相对 |
|------|------|---------------|------|
| BF16 8192³ | 1517 TFLOPS | DeepGEMM-BF16 | 0.96× [F-082] |
| FP16 8192³ | 1404 TFLOPS | DeepGEMM cuBLASLt | 0.95× [F-082] |

在 1024³–16384³ 的方阵尺寸上，官方表述为「基本跟随」最佳 cuBLAS/DeepGEMM baseline [F-082]。

### 2.2 低精度 GEMM

| 形状 | TIRx | 对比 |
|------|------|------|
| FP8 blockwise 4096×4096×7168 | 2895 TFLOPS | DeepGEMM 的 0.99× [F-083] |
| NVFP4 8192³ | 5930 TFLOPS | 距最佳 baseline 不到 2% [F-084] |

### 2.3 FlashAttention-4

| 配置 | TIRx | CuTeDSL baseline | 相对 |
|------|------|------------------|------|
| s4096, 32 heads, non-causal | 1340 TFLOPS | 1330 | 0.99× [F-085] |
| s8192, 32 heads, non-causal | 1328 TFLOPS | 1327 | 1.00× [F-085] |
| s4096, causal | 1236 TFLOPS | — | 0.97× [F-085] |

32 个 FA4 配置的整体分布 [F-086]：

| 类别 | 范围 | 中位 |
|------|------|------|
| non-causal | 580 – 1358 TFLOPS | 1277 |
| causal | 277 – 1326 TFLOPS | 1075 |

短序列绝对数值较低（如 s1024 causal 433 TFLOPS），官方归因于 `S²` 的 FLOP 缩放，而不是长上下文性能退化 [F-086]。

## 3. 这组数据证明了什么

1. **低边界 DSL 可以达到 SOTA 邻域**：在 GEMM、低精度 GEMM、FA4 三类工作负载上，TIRx 与 cuBLAS/DeepGEMM/CuTeDSL 的差距在 0–5% 量级 [F-082]~[F-085]。
2. **显式控制不等于性能损失**：把 pipeline、同步、角色、内存放置留在源码里，仍能接近高度调优的库实现。
3. **指令级 dispatch 有效**：TMA、`ldmatrix`、`tcgen05.ld`、WGMMA/tcgen05 的选择能在真实 kernel 上跑出接近基线的吞吐 [F-076][F-082]。

## 4. 这组数据没有证明什么

| 不能推出 | 原因 |
|----------|------|
| 「`tvm-tirx` 0.1.0b1 也这么快」 | 测量对象是第一代 `apache-tvm` 0.25.0 [F-099] |
| 「TIRx 全面超过 cuBLAS/DeepGEMM」 | 多数结果是 0.95×–1.00×，属于接近而非超越 [F-082]~[F-085] |
| 「在所有 GPU 上都如此」 | 只在 B200（SM100）上测 [F-081] |
| 「Agent 生成 kernel 也能达到该水平」 | 基准测的是专家 kernel library，不是 Agent 生成结果 [F-069] |
| 「端到端训练/推理更快」 | 只测 kernel 级吞吐，没有模型级端到端数据 |

## 5. 可比性边界

阅读任何 TIRx 性能声明时，先核对五个口径：

```text
① 哪一代？        apache-tvm 0.25.0（第一代） vs apache-tvm-tirx 0.1.0b1（第二代）
② 哪块硬件？      B200/SM100；其他卡未测
③ 对比谁？        cuBLAS / DeepGEMM / FlashInfer / CuTeDSL，且固定 commit
④ 怎么计时？      Proton，warmup 100 / repeat 30 / 5 轮
⑤ 什么指标？      sustained TFLOPS，GEMM 2MNK，FA4 4·B·H·S²·D
```

baseline 的 commit 也被固定 [F-081]：

| baseline | 版本 |
|----------|------|
| torch-cublas | PyTorch 2.12.0+cu132 |
| deepgemm / bf16 / cublaslt | commit 714dd1a4（2026-05-11），v2.1.1.post3 后 17 个 commit |
| flashinfer | commit bff85f34（2026-05-22），nightly-v0.6.12-20260523 |
| flashattn_sm100（CuTeDSL） | commit 3da76cdb（2026-05-22），fa4-v4.0.0.beta14 |
| cublaslt_nvfp4 | tirx-kernels 中的 cuBLASLt reference |

## 6. 为什么短序列数字看起来低

FA4 的计算量按 `4·B·H·S²·D` 缩放。序列长度减半，FLOPs 降为约 1/4，但固定开销（launch、同步、流水线填充）不会同比例下降，因此短序列的 sustained TFLOPS 天然更低 [F-086]。读到 s1024 的 433 TFLOPS 时，不应直接与 s8192 的 1328 TFLOPS 比较「实现好坏」。

## 7. 复现建议

若要独立验证，最小路径是：

1. 安装 `apache-tvm==0.25.0`（第一代），不要装 `apache-tvm-tirx` [F-071][F-095]；
2. 准备 B200（SM100）与 CUDA 13.2 环境；
3. 使用官方 kernel library `mlc-ai/tirx-kernels` 的对应 kernel；
4. 按 Proton 的 warmup/repeat 设置计时；
5. 固定 baseline commit，避免「拿今天的库比昨天的数字」。

> 本次知识包未执行上述复现，性能结论均来自官方博客 [F-099]。

## 8. 与第二代的关系

第二代目前**没有公开的同类基准** [F-040]。这不等于第二代更慢，而是说明：

- 第一代已证明「低边界 DSL 能达到 SOTA 邻域」这一设计判断；
- 第二代的卖点是架构（动态扩展、三语言、Agent 友好），其性能需要等官方或第三方基准；
- 在第二代基准出现前，不应把第一代数字当作第二代的能力证明 [F-099]。
