---
type: example
scope: flash-mla
name: FlashMLA 性能基准测试指南
version: "1.0.0"
source: benchmark/bench_flash_mla.py
description: 使用 FlashMLA 内置 benchmark 脚本进行性能测试与对比
---

# 性能基准测试指南

FlashMLA 提供了内置的 benchmark 脚本（[benchmark/bench_flash_mla.py](file:///d:/spaces/SpecWeave/external/libs/ai/deepseek-ai/FlashMLA/benchmark/bench_flash_mla.py)），支持与 PyTorch SDPA、FlashInfer、Triton 实现进行性能对比。本文档介绍如何运行和自定义 benchmark。

---

## 一、运行内置 Benchmark

### 1.1 快速开始

```bash
cd /path/to/FlashMLA

# 对比 FlashMLA vs PyTorch 基线（默认）
python benchmark/bench_flash_mla.py --compare

# 运行所有实现（torch + flash_mla + flash_infer + flash_mla_triton）
python benchmark/bench_flash_mla.py --all

# 只运行 FlashMLA
python benchmark/bench_flash_mla.py --one --target flash_mla

# 自定义基线对比
python benchmark/bench_flash_mla.py --compare --baseline flash_infer --target flash_mla
```

### 1.2 命令行参数

| 参数 | 默认值 | 说明 |
|---|---|---|
| `--baseline` | `torch` | 基线实现（`torch`/`flash_mla`/`flash_infer`/`flash_mla_triton`） |
| `--target` | `flash_mla` | 目标实现 |
| `--all` | False | 运行所有实现 |
| `--one` | False | 只运行目标实现（不对比） |
| `--compare` | False | 对比 baseline 和 target |

### 1.3 默认测试配置

```python
# 默认 shape_configs
batch_size = 128
s_q = 1                  # decode 场景（单 token 生成）
h_q = 128                # 128 个 query 头
h_kv = 1                 # MQA（1 个 KV 头）
d = 576                  # V32 模式 head_dim=576
dv = 512                 # V 维度=512
causal = True
dtype = bfloat16
page_block_size = 64

# 测试序列长度
seq_lens = [1024, 2048, 4096, 8192, 16384, 32768]
```

---

## 二、自定义 Benchmark

### 2.1 基本性能测试框架

```python
import torch
import time
from flash_mla import get_mla_metadata, flash_mla_with_kvcache

def benchmark_flash_mla(
    batch_size=128,
    seq_len=4096,
    h_q=128,
    h_kv=1,
    d=576,
    dv=512,
    dtype=torch.bfloat16,
    causal=True,
    is_fp8=False,
    num_warmups=5,
    num_iters=20,
    device="cuda",
):
    """自定义 FlashMLA MLA 解码性能测试"""
    page_block_size = 64
    max_num_blocks = (seq_len + page_block_size - 1) // page_block_size
    total_blocks = batch_size * max_num_blocks
    s_q = 1  # decode

    # 创建 KV cache
    if is_fp8:
        # FP8 KV cache: 656 bytes/token for V32
        bytes_per_token = 656
        k_cache = torch.randint(
            0, 255, (total_blocks, page_block_size, h_kv, bytes_per_token),
            dtype=torch.uint8, device=device
        )
        # 注意：实际使用需要正确填充 FP8 数据和 scales
        indices = torch.randint(
            0, seq_len, (batch_size, s_q, 64),  # topk=64
            dtype=torch.int32, device=device
        )
        block_table = None
        cache_seqlens = None
    else:
        k_cache = torch.randn(
            total_blocks, page_block_size, h_kv, d,
            dtype=dtype, device=device
        )
        block_table = torch.arange(
            total_blocks, dtype=torch.int32, device=device
        ).view(batch_size, max_num_blocks)
        cache_seqlens = torch.full(
            (batch_size,), seq_len, dtype=torch.int32, device=device
        )
        indices = None

    # 创建 Q
    q = torch.randn(batch_size, s_q, h_q, d, dtype=dtype, device=device)

    # 获取调度元数据
    sched_meta, _ = get_mla_metadata()

    # 预热
    for _ in range(num_warmups):
        out, lse = flash_mla_with_kvcache(
            q, k_cache, block_table, cache_seqlens, dv,
            sched_meta, causal=causal, is_fp8_kvcache=is_fp8,
            indices=indices,
        )
    torch.cuda.synchronize()

    # 计时
    start_event = torch.cuda.Event(enable_timing=True)
    end_event = torch.cuda.Event(enable_timing=True)

    start_event.record()
    for _ in range(num_iters):
        out, lse = flash_mla_with_kvcache(
            q, k_cache, block_table, cache_seqlens, dv,
            sched_meta, causal=causal, is_fp8_kvcache=is_fp8,
            indices=indices,
        )
    end_event.record()
    torch.cuda.synchronize()

    avg_time_ms = start_event.elapsed_time(end_event) / num_iters

    # 计算性能指标
    total_seqlens = batch_size * seq_len
    flops = s_q * total_seqlens * h_q * (d + dv) * 2  # QK + PV
    bytes_accessed = (
        total_seqlens * h_kv * d  # KV 读取
        + batch_size * s_q * h_q * d  # Q 读取
        + batch_size * s_q * h_q * dv  # O 写入
    ) * (torch.finfo(dtype).bits // 8)

    tflops = flops / (avg_time_ms * 1e-3) / 1e12
    bandwidth_gbs = bytes_accessed / (avg_time_ms * 1e-3) / 1e9

    print(f"==== FlashMLA Benchmark ====")
    print(f"Config: batch={batch_size}, seq_len={seq_len}, h_q={h_q}, h_kv={h_kv}, d={d}, dv={dv}")
    print(f"Mode: {'FP8 Sparse' if is_fp8 else 'BF16 Dense'}, causal={causal}")
    print(f"Avg time: {avg_time_ms:.3f} ms")
    print(f"Performance: {tflops:.1f} TFLOPS")
    print(f"Bandwidth: {bandwidth_gbs:.0f} GB/s")
    print()

    return avg_time_ms, tflops, bandwidth_gbs


# 测试不同配置
print("=== BF16 Dense Decode ===")
for seq_len in [1024, 4096, 16384, 32768]:
    benchmark_flash_mla(seq_len=seq_len, is_fp8=False)

print("=== FP8 Sparse Decode (H100/B200 only) ===")
major, _ = torch.cuda.get_device_capability()
if major >= 9:
    for seq_len in [4096, 8192, 16384]:
        benchmark_flash_mla(seq_len=seq_len, is_fp8=True)
```

### 2.2 FLOPS 和带宽计算公式

```python
def calc_metrics(batch_size, seq_len, h_q, h_kv, d, dv, dtype, time_ms):
    """计算 TFLOPS 和带宽"""
    s_q = 1  # decode
    total_seqlens = batch_size * seq_len

    # FLOPS: 每个 Q-K 对有 d 次乘加（QK 点积），每个 V 列有 s_kv 次乘加（PV）
    flops = s_q * total_seqlens * h_q * (d + dv) * 2  # multiply-add = 2 ops

    # 内存访问量（近似）
    dtype_bytes = torch.finfo(dtype).bits // 8
    bytes_accessed = (
        total_seqlens * h_kv * d * dtype_bytes  # KV 读取
        + batch_size * s_q * h_q * d * dtype_bytes  # Q 读取（较小）
        + batch_size * s_q * h_q * dv * dtype_bytes  # O 写入（较小）
    )

    tflops = flops / (time_ms * 1e-3) / 1e12
    bandwidth_gbs = bytes_accessed / (time_ms * 1e-3) / 1e9

    return tflops, bandwidth_gbs
```

---

## 三、不同场景的性能测试

### 3.1 内存受限 vs 计算受限

解码阶段存在两种性能模式：

```python
def profile_memory_compute_bound():
    """测试内存受限和计算受限场景"""
    import torch

    print("=== 内存受限场景（小 batch，短序列）===")
    # 小 batch 时，KV 数据量小，计算量不足以隐藏延迟，性能受内存带宽限制
    benchmark_flash_mla(batch_size=1, seq_len=1024, is_fp8=False)
    # 预期：~3000 GB/s（接近 H800 HBM3 带宽上限）

    print("=== 计算受限场景（大 batch，FP8 sparse）===")
    # 大 batch + FP8 sparse 时，计算成为瓶颈
    if torch.cuda.get_device_capability()[0] >= 9:
        benchmark_flash_mla(batch_size=128, seq_len=8192, is_fp8=True)
        # 预期：~410 TFLOPS (H800) 或更高
```

### 3.2 不同序列长度扫描

```python
def sweep_seq_lengths():
    """扫描不同序列长度"""
    seq_lens = [512, 1024, 2048, 4096, 8192, 16384, 32768, 65536]
    results = []

    for seq_len in seq_lens:
        try:
            t, tflops, bw = benchmark_flash_mla(
                batch_size=128, seq_len=seq_len, num_iters=10
            )
            results.append((seq_len, t, tflops, bw))
        except RuntimeError as e:
            print(f"seq_len={seq_len} OOM or error: {e}")
            break

    # 打印表格
    print(f"{'seq_len':>8} {'time(ms)':>10} {'TFLOPS':>10} {'GB/s':>10}")
    for seq_len, t, tflops, bw in results:
        print(f"{seq_len:>8} {t:>10.3f} {tflops:>10.1f} {bw:>10.0f}")
```

### 3.3 Triton 参考 Kernel

FlashMLA benchmark 包含 Triton 实现的 MLA decode kernel 作为参考，核心参数：

```python
# Triton kernel 配置
BLOCK_H = 16          # 头维度 tile 大小
BLOCK_N = 64          # KV 序列维度 tile 大小
NUM_KV_SPLITS = 32    # SplitKV 分片数
```

Triton kernel 分为两个阶段：
1. `_mla_attn_kernel`：分块 QK 点积 + PV 乘加（SplitKV 分块计算）
2. `_mla_softmax_reducev_kernel`：split-KV reduce（合并各 split 的结果）

---

## 四、性能验证

### 4.1 正确性验证

运行 FlashMLA 的单元测试确保结果正确：

```bash
# Dense decode 正确性测试
python tests/test_flash_mla_dense_decoding.py

# Sparse decode 正确性测试
python tests/test_flash_mla_sparse_decoding.py

# Sparse prefill 正确性测试
python tests/test_flash_mla_sparse_prefill.py

# SM100 MHA dense 测试（需要 B200）
python tests/test_fmha_sm100.py
```

### 4.2 PyTorch 参考实现对比

```python
import torch
import torch.nn.functional as F
from flash_mla import get_mla_metadata, flash_mla_with_kvcache

def verify_correctness(batch_size=2, seq_len=128, h_q=64, h_kv=1, d=576, dv=512):
    """验证 FlashMLA 结果与 PyTorch 参考实现一致"""
    dtype = torch.bfloat16
    device = "cuda"
    page_block_size = 64

    # 创建输入
    q = torch.randn(batch_size, 1, h_q, d, dtype=dtype, device=device)
    max_num_blocks = (seq_len + page_block_size - 1) // page_block_size
    total_blocks = batch_size * max_num_blocks

    k_cache = torch.randn(total_blocks, page_block_size, h_kv, d, dtype=dtype, device=device)
    block_table = torch.arange(total_blocks, dtype=torch.int32, device=device).view(batch_size, max_num_blocks)
    cache_seqlens = torch.full((batch_size,), seq_len, dtype=torch.int32, device=device)

    # FlashMLA
    sched_meta, _ = get_mla_metadata()
    out_flash, lse_flash = flash_mla_with_kvcache(
        q, k_cache, block_table, cache_seqlens, dv,
        sched_meta, causal=True, is_fp8_kvcache=False,
    )

    # PyTorch 参考实现
    # 构造完整 KV（处理分页）
    k_full = torch.zeros(batch_size, seq_len, h_kv, d, dtype=dtype, device=device)
    for b in range(batch_size):
        for i in range(seq_len):
            block_idx = i // page_block_size
            offset = i % page_block_size
            phys_block = block_table[b, block_idx]
            k_full[b, i] = k_cache[phys_block, offset, 0]

    # GQA: repeat KV heads
    q_full = q.squeeze(1)  # (b, h_q, d)
    k_full = k_full.repeat_interleave(h_q // h_kv, dim=2) if h_kv < h_q else k_full
    k_full = k_full.permute(0, 2, 1, 3)  # (b, h_q, seq, d)
    q_full = q_full.unsqueeze(2)  # (b, h_q, 1, d)

    # 手动 causal mask（decode 时 causal 无影响，因为 q 只有 1 个位置）
    attn_weights = torch.matmul(q_full, k_full.transpose(-1, -2)) / (d ** 0.5)
    attn_weights = F.softmax(attn_weights, dim=-1)
    out_ref = torch.matmul(attn_weights, k_full[..., :dv])  # 近似 V=K 的前 dv 维
    out_ref = out_ref.squeeze(2)  # (b, h_q, dv)

    # 比较
    diff = (out_flash.squeeze(1).float() - out_ref.float()).abs()
    print(f"Max error: {diff.max().item():.6f}")
    print(f"Mean error: {diff.mean().item():.6f}")

    cos_sim = torch.nn.functional.cosine_similarity(
        out_flash.squeeze(1).float().flatten().unsqueeze(0),
        out_ref.float().flatten().unsqueeze(0)
    ).item()
    print(f"Cosine similarity: {cos_sim:.6f}")
```

---

## 五、性能调优建议

1. **预热（Warmup）**：首次调用 FlashMLA 会触发调度元数据初始化和 CUDA kernel 加载，benchmark 需要足够的 warmup 次数
2. **L2 缓存刷新**：严格 benchmark 时应在每次迭代前刷新 L2 缓存（可通过 `torch.cuda.empty_cache()` 或访问大数组实现）
3. **Batch Size 调优**：大 batch 提高计算密度，小 batch 受内存带宽限制；根据部署场景选择合适的 batch size
4. **Sparse FP8 模式**：DeepSeek-V3.2 的 DSA 模式配合 FP8 KV cache 可大幅提升计算吞吐量（最高 410 TFLOPS on H800）
5. **SplitKV 自动调优**：`num_sm_parts` 由内核根据 SM 数量和头数自动计算，无需手动设置
6. **CUDA Graphs**：对于固定形状的解码场景，可使用 CUDA Graphs 捕获 kernel 执行，减少 launch overhead
7. **SM100 优化**：Blackwell GPU 上使用 MODEL1 模式（d=512）和 small_topk 内核可获得更好性能

---

## 六、相关链接

- [/deepseek/flash-mla/examples/basic-decoding](/ai/deepseek/flash-mla/examples/basic-decoding) — MLA 解码基础使用示例
- [/deepseek/flash-mla/references/api](/ai/deepseek/flash-mla/references/api) — Python API 参考
- [/deepseek/flash-mla/concepts/splitkv](/ai/deepseek/flash-mla/concepts/splitkv) — SplitKV 性能优化原理
- [/deepseek/flash-mla/concepts/hopper-blackwell-kernels](/ai/deepseek/flash-mla/concepts/hopper-blackwell-kernels) — 架构特性与性能
- [/deepseek/deep-gemm/examples/tuning](/ai/deepseek/deep-gemm/examples/tuning) — DeepGEMM 性能调优参考
