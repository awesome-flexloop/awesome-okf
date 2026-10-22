---
type: Concept
title: "性能与基准：数字背后的测试条件"
description: "Humming 官方性能数据的完整登记——基准方法六项条件、编译耗时对照、Dense/MoE/Hopper/Blackwell/SM120 各组加速倍数、端到端实测数据与阅读纪律"
tags: [humming, benchmark, performance, methodology, comparison, 进阶]
generated: { by: seven-concepts-cmd+source-code-to-okf-wiki/E, at: "2026-10-22T23:40:00+08:00" }
status: stable
stale_after: 2027-04-22
sources:
  - id: blog
    url: https://vllm.ai/blog/2026-10-21-humming
    title: Announcing Humming（2026-10-21）— Results 章节
  - id: local-source
    resource: /references/facts.md
    title: 本地源码检出事实清单
---

# 性能与基准：数字背后的测试条件

> 进阶层。**本页的所有倍数都必须连同测试条件一起引用**——脱离条件的加速比没有意义。

## 一、基准方法（六项条件，F-079）

官方基准由 **vLLM community** 运行，方法如下：

| 条件 | 说明 |
|------|------|
| M 覆盖 | 1 到 8192 的**每一个 2 的幂** |
| Warmup | 充分预热 |
| 计时粒度 | **逐 kernel** 计时 |
| Cache 状态 | **cold L2 cache**（每次测量前清空 L2） |
| 样本间隔 | 短暂 pause |
| MoE speedup 定义 | 「Gateup GEMM 延迟 + Down GEMM 延迟」之和 |

**两点尤其重要**：

- **cold L2 cache** 是保守设定——生产环境中权重常驻 L2，真实延迟可能更低。这让官方数字偏保守，是好事。
- **MoE speedup 的定义方式**：它把 MoE 的两个 GEMM（Gateup + Down）合并计时，而不是分开报告。解读时要知道这是一个复合指标。

## 二、编译耗时（轻量定位的证据）

环境：H200 server + CUDA 13.4 + **关闭编译缓存**（F-080）：

| 方案 | 耗时 | 相对 CUTLASS |
|------|------|-------------|
| CUTLASS + NVCC | 23.35 秒 | 1× |
| **Humming + NVCC** | **1.82 秒** | **≈ 12.8× 更快** |
| Humming + NVRTC | 1.88 秒 | ≈ 12.4× 更快 |

> ⚠️ **这组数字的三个限定条件**（缺一不可）：**H200 server** + **CUDA 13.4** + **关闭编译缓存**。脱离条件引用倍数会失真。

**为什么差这么多**：CUTLASS 需要展开整套模板实例化；Humming 只为当前这一个具体配置编译一个 kernel。

**覆盖成本**：编译并加载单层 GEMM 全部受支持 M 档位的内核约 **2–4 秒**（F-081）。且 Humming 可在模型 warmup 期间**并行编译**内核。

> 作者知乎自述「单个算子编译时间约 1–2 秒，与算子复杂度相关、与 CPU 性能强相关」（F-094）——与官方数据互为印证。

## 三、Dense W4A16

对标 vLLM Marlin（F-082）：

| 场景 | 数据 |
|------|------|
| 多数配置 | 与 Marlin **持平或更快** |
| 小 batch 多设备 | 约 **3–4×** |
| 大 batch，H200 | 约 **2× Marlin** |
| 大 batch，部分 B300 场景 | 超 **3× Marlin** |

**注意「多数配置持平」**：不是所有情况都赢。Dense 路径上 Humming 的优势主要集中在小 batch（低延迟场景）。

## 四、MoE W4A16

对标 vLLM Marlin（F-083）：

| 硬件 | 场景 | 数据 |
|------|------|------|
| H20 / H200 | MXFP4，多个中大 batch | 约 **2× Marlin** |
| B300 | MXINT4 / NVFP4 的 grouped 路径 | 约 **5×** |
| SM120 / SM121 | 一系列 workload | 优于 Marlin 与对应 FlashInfer 实现 |

**MoE 的加速比显著高于 Dense**——原因见 [06 MoE 路径](06-moe.md)：grouped 形态正是固定 shape 内核最不擅长的区间。

## 五、Hopper 对标 DeepGEMM

| 场景 | 对标 | 数据 |
|------|------|------|
| W8A8 | DeepGEMM Contiguous | 小 batch 约 **2.6×**、中 batch 约 **2.5×** |
| W4A8 | DeepGEMM W8A8 | H20 约 **4.2×**、H200 约 **4.5×** |

（F-084、F-085。）

## 六、Blackwell B300 对标 DeepGEMM

同精度对标 DeepGEMM Contiguous（F-086）：

| 精度组合 | 数据 |
|---------|------|
| W8A8 | 约 **1.25×** |
| W4A8 | 约 **1.6×** |
| W4A4 | 约 **1.4×** |

**注意倍数量级明显低于 Hopper 组**（1.25–1.6× vs 2.5–4.5×）。（编者注，非博客原文：强基线下增益收窄是合理的现象。）

## 七、SM120 / SM121 对标 FlashInfer CUTLASS

（F-087）：

| 项 | 数据 |
|----|------|
| 多数测试点 | 更优 |
| SM121 小 batch W4A8 | 约 **+19%** |
| SM121 小 batch W4A4 | 约 **+9%** |

## 八、其他 WnA16 格式（SM120）

（F-088）：

| 项 | 数据 |
|----|------|
| 最低位配置 | 超过 BF16 cuBLAS 的 **5×** |
| 大 batch，H20 | 多个位宽维持接近 BF16 cuBLAS 的计算效率 |

## 九、端到端实测

唯一一组端到端数据（F-089）：

| 项 | 值 |
|----|----|
| 模型 | DeepSeek-V4.1-Flash |
| 硬件 | 8×H20，TP=8 |
| 变更 | MoE 执行：vLLM Marlin W4A16（BF16 激活）→ Humming W4A8（tokenwise FP8 激活） |
| 吞吐提升 | **14%–43%** |
| TTFT 降低 | **25%–32%** |
| 并发 64 输出吞吐 | 442.37 → **633.94 tokens/s** |
| TPOT | 约降 **31%** |

⚠️ **该实验同时改了两件事**（内核 + 激活精度），所以 14%–43% 是综合效果，不可归因给单一因素。

## 十、阅读纪律

1. **必须带条件引用**。「3× 于 Marlin」这种说法单独出现是误导——要写明「小 batch 多设备、cold L2 cache、逐 kernel 计时」。
2. **注意基线是谁**。Marlin 与 DeepGEMM 都是强基线，不是弱参照物。
3. **本包未做真机实测**。以上全部是官方博客在其特定条件下的结果，**不代表通用结论**。上生产前必须以自有负载实测。
4. **端到端样本只有一个**。不足以支撑普适结论。
5. **编译时间依赖 CPU 性能**（F-094）。在弱 CPU 机器上首次编译可能明显更慢。

## 十一、自建基准

Humming 自带五套可横向对比的 harness（F-095）：

| 脚本 | 对标 |
|------|------|
| `benchmarks/bench_humming.py` | Humming 自身 |
| `benchmarks/bench_marlin.py` | Marlin |
| `benchmarks/bench_cutlass_w8a8.py` | CUTLASS W8A8 |
| `benchmarks/bench_torch.py` | PyTorch 原生 |
| `benchmarks/bench_triton_moe.py` | Triton MoE |

### 已归档结果的组织方式

按设备分目录（F-096）：`4090/`、`a800/`、`h20/`、`h200/`。

用例目录名编码 shape 与分组参数：

```
dense_n8192_k8192_g0                    # Dense，N=K=8192，group size 0
dense_n8192_k8192_g0_f16accum           # 同上 + f16 累加
moe_e256_k8_n512_k7168_g128x128         # MoE：256 专家，top-8，N=512，K=7168，group 128x128
```

**结果文件名规则**（F-097）：

```
{实现}_w{权重位宽}a{激活位宽}_{权重类型}_{激活类型}.json
```

同一目录下并存 `humming_*`、`marlin_*`、`cutlass_*`、`torch_*` 四类实现——**便于直接对拍**。

### 测试布局

（F-098）kernel 级测试 9 + 3 个，另 1 个 C++ mock，Python 级测试 5 个：

| 目录/文件 | 内容 |
|-----------|------|
| `tests/kernels/humming/` | 9 个：accumulation / block_scaled / datatype / moe / mxfp4 / scale / shape / special_paths / zero_point |
| `tests/kernels/process_input/` | 3 个：layout / matrix / scale |
| `tests/native/` | 仅 `device_info_mock.cpp` 一个 C++ mock（设备信息桩） |
| `tests/test_jit_infrastructure.py` | JIT 基础设施 |
| `tests/test_sm8x_heuristics.py` | SM8x 启发式 |
| `tests/test_sm90_heuristics.py` | SM90 启发式 |
| `tests/test_sm90_h20_heuristics.py` | SM90 H20 启发式 |
| `tests/test_tuning_candidates.py` | 调优候选生成 |

**`test_tuning_candidates.py` 值得注意**——它验证的正是 M 维候选生成与去重逻辑（F-057）。

## 十二、延伸阅读

- [09 进阶主题](09-advanced.md)：路线图与未文档化格式
- [06 MoE 路径](06-moe.md)：MoE 加速比更高的原因
- 实战：[04 基准对拍](../examples/04-benchmarking.md)
