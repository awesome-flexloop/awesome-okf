---
type: concept
scope: deep-gemm
name: MegaMoE 融合运算
version: "2.6.1"
source: csrc/apis/mega.hpp, deep_gemm/mega/__init__.py, csrc/jit_kernels/impls/sm100_fp8_fp4_mega_moe.hpp, csrc/jit_kernels/impls/sm100_bf16_mega_moe.hpp
description: DeepGEMM MegaMoE 对称缓冲区融合 MoE 核函数的设计原理
---

# MegaMoE 融合运算

MegaMoE 是 DeepGEMM 为大规模 MoE 模型设计的极致性能融合核函数，仅支持 SM100（Blackwell）架构。它利用 GPU 对称内存（Symmetric Memory）构建跨 rank 的零拷贝环形通信缓冲区，将 MoE 层的 token dispatch、专家 GEMM、SwiGLU 激活、token combine 完整融合到单个核函数中，消除了传统 MoE 实现中显式 all-to-all 通信和核函数间中间结果写回的开销。

---

## 一、传统 MoE 的性能瓶颈

传统 MoE 实现（如使用 DeepEP + 分组 GEMM）的执行流程：

```
1. Router → top-k 选择
2. Token Dispatch (all-to-all 发送 token 到目标 expert 所在 rank)
3. L1 GEMM (up_proj + gate_proj): 分组 GEMM
4. SwiGLU Activation
5. L2 GEMM (down_proj): 分组 GEMM
6. Token Combine (all-to-all 发送结果回源 rank)
7. 加权求和
```

**性能问题**：
- **通信开销**：两次 all-to-all（dispatch 和 combine）占据大量时间，特别是在跨节点 EP 场景下
- **核函数启动开销**：多个独立核函数（dispatch、GEMM1、activation、GEMM2、combine）分别启动，launch overhead 累积
- **内存带宽浪费**：中间结果（L1 输出、激活后结果、L2 输出）需要写入和读回 HBM，带宽成为瓶颈
- **同步开销**：核函数之间需要 GPU 同步，无法重叠计算和通信

## 二、MegaMoE 核心设计

### 2.1 对称内存环形缓冲区

MegaMoE 使用 PyTorch 的 `torch.distributed._symmetric_memory` 分配跨 rank 的对称内存：

```python
# 单 rank: torch.empty 分配
# 多 rank: symm_mem.empty 分配（所有 rank 相同虚拟地址映射）
buffer = symm_mem.empty(num_bytes, dtype=torch.int8, device=device)
handle = symm_mem.rendezvous(buffer, group)
buffer_ptrs = handle.buffer_ptrs  # 所有 rank 的 buffer 指针
```

对称内存的特性：
- 所有 rank 上相同虚拟地址指向各自的物理内存
- 通过 `buffer_ptrs[rank_id]` 可以直接读写其他 rank 的内存（需通过 ibverbs/NVLink 远程访问）
- 支持零拷贝 RDMA/GPU Direct 访问，无需 CPU 参与

### 2.2 融合执行模型

MegaMoE 将整个 MoE 前向融合为单个核函数，内部通过环形（ring）通信模式流水线执行：

```
核函数内部流水线（每个 SM 独立调度）：

┌─────────────────────────────────────────────────────────┐
│  Stage 1: Pull tokens from remote rank via symm buffer  │
│  Stage 2: L1 GEMM (up+gate) + SwiGLU                   │
│  Stage 3: Push L1 acts to ring buffer                   │
│  Stage 4: Pull L1 acts from ring buffer                 │
│  Stage 5: L2 GEMM (down)                                │
│  Stage 6: Atomic add result to output y                 │
└─────────────────────────────────────────────────────────┘
```

核函数通过 software pipeline 和 double/triple buffering 重叠通信和计算：
- 一个 warp group 执行 TMA 异步加载（pull/push 数据）
- 另一个 warp group 执行 WGMMA 计算
- 通过信号量（semaphore）同步生产者和消费者

### 2.3 环形缓冲区布局

```
Symmetric Buffer 内存布局（每个 rank）：
┌────────────────────────────────────────────┐
│ Input Section                              │
│ ├── x (num_max_tokens_per_rank × hidden)   │ ← 本 rank 输入 token
│ ├── x_sf (num_max_tokens × hidden/128)     │ ← 输入 SF
│ ├── topk_idx (num_max_tokens × num_topk)   │ ← Top-K 专家索引
│ └── topk_weights (num_max_tokens × num_topk)│← Top-K 权重
├────────────────────────────────────────────┤
│ Shared Expert Section                      │
│ ├── shared_l1_acts (复用 x)                │
│ ├── shared_l1_acts_sf                      │
│ ├── shared_l2_acts                         │
│ └── shared_l2_acts_sf                      │
├────────────────────────────────────────────┤
│ Ring Buffer Section (跨 rank 循环)          │
│ ├── l1_acts (num_ring_tokens × hidden)     │ ← L1 GEMM 输出循环区
│ ├── l1_acts_sf                             │
│ ├── l2_acts (num_ring_tokens × inter)      │ ← L2 GEMM 输出循环区
│ └── l2_acts_sf                             │
└────────────────────────────────────────────┘
```

### 2.4 Ring 容量计算

环形缓冲区需要容纳最坏情况下的"在途"（live）数据块：

```cpp
// 遍历所有候选 block_m，取最大 ring 需求
for (const auto& block_m : kCandidateBlockM) {  // {8,16,32,64,96,128,192}
    num_pool_blocks = ceil(总路由tokens / block_m) + num_experts_per_rank;
    num_live_pool_blocks = sched::get_num_max_live_pool_blocks(
        num_pool_blocks, num_sms, hidden, intermediate_hidden);
    num_ring_tokens = max(num_ring_tokens, num_live_pool_blocks * block_m);
}
num_ring_tokens = align(num_ring_tokens, kLCMCandidateBlockM);  // 对齐到 384
```

`kLCMCandidateBlockM = 384` 是所有候选 block_m（8, 16, 32, 64, 96, 128, 192）的最小公倍数，确保 ring buffer 对齐到任何 block 大小。

---

## 三、双精度权重方案

MegaMoE 对路由专家和共享专家使用不同的精度策略：

| 组件 | 精度 | 原因 |
|---|---|---|
| 路由专家 L1/L2 权重 | FP4 (E2M1, packed Int8) | 极致压缩带宽，per-1×32 block SF |
| 路由专家权重 SF | UE8M0 (packed Int32) | 硬件原生支持，4× 压缩 |
| 共享专家 L1/L2 权重 | FP8 (E4M3) | 共享专家数量少，保持更高精度 |
| 共享专家权重 SF | UE8M0 (packed Int32) | 同路由专家 |
| 激活值 | FP8 (E4M3) | 激活分布更复杂，需要更高精度 |
| 输出 y | BF16 | 最终输出精度 |
| Top-K 权重 | FP32 | 路由权重精度 |

**BF16 模式**（`bf16_mega_moe`）：所有计算使用 BF16，无 SF，用于精度敏感场景或 ablation。

---

## 四、SwiGLU 融合与权重交错

### 4.1 SwiGLU 激活

SwiGLU 激活函数：`output = gate(x) * silu(up(x))`

传统实现需要两次 GEMM（gate_proj 和 up_proj）+ 一次 element-wise 乘法。MegaMoE 将 gate 和 up 权重交错排列，在 GEMM 输出时直接计算 SwiGLU：

### 4.2 权重交错

```python
def _interleave_weights(t: torch.Tensor, gran: int = 8) -> torch.Tensor:
    """将 gate/up 权重沿 N 维度交错排列"""
    # 原始排列: [gate_0, gate_1, ..., gate_n, up_0, up_1, ..., up_n]
    # 交错排列: [gate_0..7, up_0..7, gate_8..15, up_8..15, ...]
```

交错后 L1 权重形状为 `(num_experts, intermediate_hidden*2, hidden)`，gate 和 up 每 gran=8 列交替排列。核函数可以连续加载 gate 和 up 数据并直接计算 SwiGLU，减少寄存器压力和 shared memory 开销。

### 4.3 SF 转置（UTCCP 布局）

```python
def _transpose_sf_for_utccp(sf: torch.Tensor) -> torch.Tensor:
    """reshape(-1, 4, 32, packed_sf_k).transpose(2,3).reshape(...)"""
```

UE8M0 打包的 SF 需要特殊转置以匹配 Unified Tensor Core Compute Pipeline (UTCCP) 的数据加载模式，确保 WGMMA 指令可以直接使用 SF 而无需额外重排。

---

## 五、启发式配置

### 5.1 Block M 选择

基于 `num_expected_tokens_per_expert`（每个专家预期 token 数）分档选择 block_m：

| 每专家 token 数 | block_m |
|---|---|
| 很少 | 16 |
| 较少 | 32 |
| 中等 | 64 |
| 较多 | 96 |
| 多 | 128 |
| 很多 | 192 |

候选值：`{8, 16, 32, 64, 96, 128, 192}`，LCM 为 384。

### 5.2 关键配置参数

`MegaMoEConfig` 包含：
- `block_m/n/k`：GEMM tile 大小
- `load_block_m/n`, `store_block_m`：数据加载/存储 tile 大小
- `sf_block_m/n`：SF tile 大小
- `num_ring_tokens/sf_ring_tokens`：环形缓冲区容量
- `swizzle_acts_mode/weights_mode`：数据 swizzle 模式
- `num_stages`：pipeline 阶段数
- `smem_size`：shared memory 大小
- `num_dispatch/non_epilogue/epilogue_threads`：线程分配
- `cluster_size = 2`：thread block cluster 维度

---

## 六、使用流程

### 6.1 权重预处理

```python
import deep_gemm

# 1. 变换权重（interleave + SF transpose）
l1_weights, l2_weights = deep_gemm.transform_weights_for_mega_moe(
    l1_weights,  # (num_experts, inter*2, hidden) FP8/FP4 tuple or BF16 tensor
    l2_weights,  # (num_experts, hidden, inter) FP8/FP4 tuple or BF16 tensor
    activation='swiglu'
)
```

### 6.2 缓冲区分配

```python
# 2. 创建对称缓冲区
sym_buffer = deep_gemm.get_symm_buffer_for_mega_moe(
    group,                       # 分布式进程组
    num_experts=256,
    num_max_tokens_per_rank=4096,  # 会自动对齐到 384
    num_topk=8,
    hidden=4096,
    intermediate_hidden=256,     # 每个专家的中间维度
    num_shared_experts=1,        # 可选共享专家
    mma_type='fp8xfp4',          # 或 'bf16xbf16'
)
```

### 6.3 前向计算

```python
# 3. 准备输入（将 token 数据拷贝到 sym_buffer.x 等视图）
# sym_buffer.x.copy_(input_tokens)
# sym_buffer.topk_idx.copy_(topk_indices)
# sym_buffer.topk_weights.copy_(topk_weights)

# 4. 执行 MegaMoE
deep_gemm.fp8_fp4_mega_moe(
    y,                           # 输出 (num_tokens, hidden) BF16
    l1_weights, l2_weights,      # (weights, sf) 元组
    sym_buffer,                  # SymmBuffer 实例
    shared_l1_weights=None,      # 可选共享专家权重
    shared_l2_weights=None,
    cumulative_local_expert_recv_stats=None,  # 可选统计
    recipe=(1, 1, 32),
    activation='swiglu',
    activation_clamp=None,
    fast_math=True,
)
```

---

## 七、关键约束

1. **仅支持 SM100**：MegaMoE 核函数使用 Blackwell 专用指令（如 FP4 WGMMA、UTCCP），无法在 Hopper 上运行
2. **仅支持 SwiGLU**：激活函数硬编码为 SwiGLU
3. **Recipe 固定**：FP8/FP4 模式 recipe 必须为 `(1, 1, 32)`（per-1×32 block SF）
4. **权重布局**：
   - 路由专家权重：K-major、contiguous、packed FP4（Int8）
   - 路由专家 SF：MN-major（stride(-2)==1）、TMA 对齐、dtype=Int32（UE8M0）
   - 共享专家权重：2D、K-major、contiguous、FP8（E4M3）
5. **L1 权重形状**：intermediate_hidden × 2（gate+up 交错）
6. **维度对齐**：hidden 和 intermediate_hidden 须为 128 的倍数
7. **Token 对齐**：num_max_tokens_per_rank 对齐到 384（`kLCMCandidateBlockM`）
8. **Rank 整除**：num_experts 必须能被 num_ranks（group size）整除
9. **Cluster size**：固定为 2（thread block cluster 维度）
10. **对称内存依赖**：需要 PyTorch `symmetric_memory` 支持（多 rank 场景）

---

## 八、调试

设置 `DG_COMM_KERNEL_DEBUG=1` 环境变量时，核函数执行后会清零整个 sym_buffer。这用于检测是否正确地在每次调用前重新填充输入数据。

---

## 九、相关链接

- [/deepseek/deep-gemm/references/mega-moe](/ai/deepseek/deep-gemm/references/mega-moe) — MegaMoE API 参考
- [/deepseek/deep-gemm/examples/moe-forward](/ai/deepseek/deep-gemm/examples/moe-forward) — MegaMoE 使用示例
- [/deepseek/deep-gemm/concepts/fp8-gemm](/ai/deepseek/deep-gemm/concepts/fp8-gemm) — FP8/FP4 量化方案
- [/deepseek/deep-gemm/concepts/grouped-gemm](/ai/deepseek/deep-gemm/concepts/grouped-gemm) — 分组 GEMM（非融合 MoE 方案）
- [/deepseek/deep-ep/](/ai/deepseek/deep-ep/) — DeepEP 通信库（非融合方案）
