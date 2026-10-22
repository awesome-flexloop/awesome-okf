---
type: Example
title: "实战 04：基准对拍"
description: "Humming 基准对拍实战——复用项目自带五套 harness、读懂归档结果的目录与命名规则、构造自己的对拍脚本、cold L2 cache 的正确测法与统计判据"
tags: [humming, example, benchmarking, harness, results, marlin, cutlass, triton]
generated: { by: seven-concepts-cmd+source-code-to-okf-wiki/E, at: "2026-10-22T23:40:00+08:00" }
status: stable
stale_after: 2027-04-22
sources:
  - id: local-source
    resource: /references/facts.md
    title: 本地源码检出事实清单
  - id: blog
    url: https://vllm.ai/blog/2026-10-21-humming
---

# 实战 04：基准对拍

> 场景页。官方性能数字全部带特定条件（F-079）。本文教你**复用项目自带设施**并**建立自己的对拍基线**。

## 一、项目自带的五套 harness

（F-095，`benchmarks/` 目录）

| 脚本 | 对标对象 | 说明 |
|------|---------|------|
| `bench_humming.py` | Humming 自身 | 基准主体 |
| `bench_marlin.py` | Marlin | vLLM 内置 W4A16 基线 |
| `bench_cutlass_w8a8.py` | CUTLASS W8A8 | Hopper W8A8 基线 |
| `bench_torch.py` | PyTorch 原生 | 参照下限 |
| `bench_triton_moe.py` | Triton MoE | MoE 对标 |

**这是最重要的一点**：官方博客里的所有倍数都是在**同一套 harness 内**跑出来的（F-079）。复用它的 harness，你的数字就和官方可比；自己另写一套，则只能内部横向比。

## 二、已归档结果的组织方式

### 目录结构（F-096）

```
benchmarks/results/
├── 4090/
├── a800/
├── h20/
└── h200/
    └── dense_n8192_k8192_g0/
        ├── humming_w4a16_int4_float16.json
        ├── humming_w4a8_float4e2m1_float8e4m3.json
        ├── humming_w8a16_int8_float16.json
        ├── marlin_w4a16_int4_float16.json
        ├── marlin_w4a8_int4_int8.json
        ├── marlin_w8a16_int8_float16.json
        └── cutlass_w8a8_float8e4m3_float16.json
```

> ⚠️ **注意实际文件名**：Humming 侧有 **1–8 位全谱**的归档（`humming_w1a16_…` 到 `humming_w8a16_…`），这正是它相对 Marlin（只有 w4/w8）的覆盖优势的直接体现（F-010、F-070）。激活类型后缀用完整格式名（`float8e4m3`、`float4e2m1`），不是简写 `float8`。

### 用例目录名编码（F-096）

```
dense_n8192_k8192_g0
  │    │     │    └── group size（0 = 无分组）
  │    │     └─────── K = 8192
  │    └───────────── N = 8192
  └────────────────── Dense

dense_n8192_k8192_g0_f16accum
  └─ 加 f16 累加变体

moe_e256_k8_n512_k7168_g128x128
     │   │  │   │     │    └── group 128x128
     │   │  │   │     └────── K = 7168
     │   │  │   └──────────── N = 512
     │   │  └──────────────── top-8
     │   └─────────────────── 256 专家
     └─────────────────────── MoE
```

### 结果文件名规则（F-097）

```
{实现}_w{权重位宽}a{激活位宽}_{权重类型}_{激活类型}.json
```

例：`humming_w4a16_int4_float16.json` = Humming，4bit 权重 / 16bit 激活，int4 权重，float16 激活；`cutlass_w8a8_float8e4m3_float16.json` = CUTLASS，8bit 权重 / 8bit 激活，float8e4m3 权重，float16 激活。

**同一目录下并存多种实现**（humming / marlin / cutlass / torch），意味着**可以直接对拍**——不需要自己跑一遍 Marlin。

## 三、读懂官方数字的前提

### 基准方法六项（F-079）

| 条件 | 说明 |
|------|------|
| M 覆盖 | 1 到 8192 的**每一个 2 的幂** |
| Warmup | 充分预热 |
| 计时 | 逐 kernel |
| Cache | **cold L2 cache** |
| 样本间隔 | 短暂 pause |
| MoE speedup | 「Gateup GEMM 延迟 + Down GEMM 延迟」之和 |

### 各组官方数字速查

| 组 | 对标 | 关键数据 | 出处 |
|----|------|---------|------|
| 编译耗时 | CUTLASS+NVCC | 1.82s vs 23.35s | F-080 |
| Dense W4A16 | Marlin | 小 batch 3–4×；H200 大 batch ~2× | F-082 |
| MoE W4A16 | Marlin | H20/H200 MXFP4 ~2×；B300 grouped ~5× | F-083 |
| Hopper W8A8 | DeepGEMM Contiguous | 小 batch ~2.6×，中 batch ~2.5× | F-084 |
| Hopper W4A8 | DeepGEMM W8A8 | H20 ~4.2×，H200 ~4.5× | F-085 |
| B300 | DeepGEMM Contiguous | W8A8 ~1.25×、W4A8 ~1.6×、W4A4 ~1.4× | F-086 |
| SM120/121 | FlashInfer CUTLASS | SM121 小 batch W4A8 +19%、W4A4 +9% | F-087 |
| SM120 其他位宽 | BF16 cuBLAS | 最低位 >5× | F-088 |
| 端到端 | Marlin W4A16（BF16 激活） | 吞吐 +14%–43%，TTFT −25%–32% | F-089 |

## 四、构造自己的对拍脚本

### 复用项目 harness

```bash
cd <humming-repo>
python benchmarks/bench_humming.py --help
python benchmarks/bench_marlin.py --help
```

**先跑通官方 harness**，拿到与自己环境匹配的数字，再考虑自定义。

### 自写对拍（同时跑多实现）

```python
import time, json
import torch

def timeit(fn, warmup=10, iters=50):
    for _ in range(warmup):
        fn()
    torch.cuda.synchronize()
    ts = []
    for _ in range(iters):
        t0 = time.perf_counter()
        fn()
        torch.cuda.synchronize()
        ts.append((time.perf_counter() - t0) * 1e3)
    ts.sort()
    return ts[len(ts) // 2]      # 中位数，比均值抗干扰

def cold_l2_flush():
    """官方基准用 cold L2 cache，自写脚本要对齐"""
    # 用一个大 buffer 占满 L2
    cache = torch.empty(int(128 * 1024 * 1024 // 4), dtype=torch.float32, device="cuda")
    cache.zero_()
    del cache
```

### 统计判据

| 指标 | 为什么重要 |
|------|-----------|
| **中位数** | 比均值抗干扰（系统抖动、其他进程） |
| **P10 / P90** | 看尾部延迟——生产环境关心 P99 |
| 多次独立运行 | 确认结果稳定，不是偶然 |

**建议**：每个配置至少跑 3 次独立运行，报告跨运行的变异。差异小于 5% 的倍数不值得引用。

### 扫 M 全谱

```python
m_values = [1 << i for i in range(14)]   # 1..8192，每个 2 的幂
```

**为什么要扫全谱**：M 决定 kernel 选择（F-057），不同 M 档位用不同 tile 配置。**只在某一个 M 上测得出的结论没有代表性**——官方数据也坚持扫全谱（F-079）。

### 扫位宽组合

```python
for w_bits, a_bits in [(4, 16), (4, 8), (8, 8), (8, 16), (6, 16)]:
    ...
```

**6bit 值得单独测**——这是 Humming 相对 Marlin 的差异化位宽（F-070、F-091），也是官方 benchmark 目录里出现的位宽。

## 五、和官方数据对照

拿到自己的数字后，与 `benchmarks/results/` 里的归档结果对照：

```bash
# 看某个配置的历史数据
cat benchmarks/results/h200/dense_n8192_k8192_g0/humming_w4a16_int4_float16.json

# 找同类配置文件
ls benchmarks/results/h200/dense_n8192_k8192_g0/
```

**对照时注意**：

| 差异项 | 影响 |
|--------|------|
| 硬件型号 | 同架构不同型号（如 A800 vs H20）差异显著 |
| CUDA / 驱动版本 | 影响编译产物与库选择 |
| CPU 型号 | 影响编译耗时（F-094）与 launch 开销 |
| PyTorch 版本 | 影响周边算子性能 |
| 缓存状态 | cold vs warm L2 结果差很多 |

## 六、测试设施

除 benchmark 外，项目还有完整的 kernel 级测试（F-098）：

| 目录/文件 | 覆盖内容 |
|-----------|---------|
| `tests/kernels/humming/test_datatype.py` | dtype 组合正确性 |
| `tests/kernels/humming/test_scale.py` | scale 粒度正确性 |
| `tests/kernels/humming/test_zero_point.py` | 零点处理 |
| `tests/kernels/humming/test_mxfp4.py` | MXFP4 特殊路径 |
| `tests/kernels/humming/test_block_scaled.py` | 块级缩放 |
| `tests/kernels/humming/test_accumulation.py` | 累加行为 |
| `tests/kernels/humming/test_shape.py` | shape 覆盖 |
| `tests/kernels/humming/test_moe.py` | MoE 路径 |
| `tests/kernels/humming/test_special_paths.py` | 特殊路径 |
| `tests/kernels/process_input/test_layout.py` | 输入布局 |
| `tests/kernels/process_input/test_matrix.py` | 输入矩阵 |
| `tests/kernels/process_input/test_scale.py` | 输入 scale |
| `tests/test_jit_infrastructure.py` | JIT 基础设施 |
| `tests/test_sm8x_heuristics.py` | SM8x 启发式 |
| `tests/test_sm90_heuristics.py` | SM90 启发式 |
| `tests/test_sm90_h20_heuristics.py` | SM90 H20 启发式 |
| `tests/test_tuning_candidates.py` | M 候选生成与去重 |

**跑测试是验证环境健康的最佳方式**：

```bash
pytest tests/ -v
```

**`test_tuning_candidates.py` 尤其值得跑**——它验证的正是启发式的 M 候选生成逻辑（F-057），出问题时报错信息最直接。

## 七、判读与报告纪律

1. **带条件引用**：写「3× 于 Marlin」时必须附「小 batch、多设备、cold L2、逐 kernel 计时」。
2. **标注基线身份**：Marlin / DeepGEMM / FlashInfer / cuBLAS 都是强基线。
3. **区分内核收益与激活精度收益**：官方端到端数据同时改了两件事（F-089）。
4. **本包未做真机实测**：以上全部是官方在其特定条件下的结果。
5. **报告变异**：多次独立运行的变异大于 5% 的结论不要引用。

## 八、下一步

- [08 性能与基准](../concepts/08-performance.md)：完整数据与条件说明
- [01 稠密量化 GEMM](01-dense-gemm.md)：功能对拍脚本
- [02 MoE GEMM](02-moe-gemm.md)：MoE 侧的基准构造
