---
type: api-reference
scope: deep-gemm
name: MegaMoE Operations
version: "2.6.1"
source: csrc/apis/mega.hpp, deep_gemm/mega/__init__.py, csrc/jit_kernels/heuristics/mega_moe.hpp, deep_gemm/include/deep_gemm/layout/mega_moe.cuh
description: DeepGEMM MegaMoE 对称缓冲区 MoE 核函数 API
---

# MegaMoE 运算

MegaMoE 是 DeepGEMM 提供的高性能 MoE（Mixture of Experts）融合核函数，利用对称内存（Symmetric Memory）实现跨 rank 的零拷贝环形通信缓冲区，将 dispatch、GEMM、activation、combine 完整融合为单内核，仅支持 SM100（Blackwell）架构。

---

## 一、Python API

### 1.1 SymmBuffer 类

```python
class SymmBuffer:
    def __init__(self, group: dist.ProcessGroup, num_experts: int,
                 num_max_tokens_per_rank: int, num_topk: int,
                 hidden: int, intermediate_hidden: int,
                 num_shared_experts: int = 0,
                 mma_type: str = 'fp8xfp4',
                 activation: str = 'swiglu')
```

**参数说明**：
- `group`：PyTorch 分布式进程组
- `num_experts`：总专家数
- `num_max_tokens_per_rank`：每 rank 最大 token 数（会自动对齐到 384）
- `num_topk`：Top-K 路由数
- `hidden`：隐藏层维度
- `intermediate_hidden`：FFN 中间层维度
- `num_shared_experts`：共享专家数（默认 0）
- `mma_type`：MMA 类型，`"fp8xfp4"`（路由专家 FP4、共享专家 FP8）或 `"bf16xbf16"`
- `activation`：激活函数类型，仅支持 `"swiglu"`

**缓冲区视图**（通过 `slice_input_buffers` 创建）：
| 视图名 | 形状 | dtype | 说明 |
|---|---|---|---|
| `x` | `(num_max_tokens_per_rank, hidden)` | FP8/BF16 | 输入 token |
| `x_sf` | `(num_max_tokens_per_rank, hidden/128)` | Int32 | 输入缩放因子（仅 FP8） |
| `topk_idx` | `(num_max_tokens_per_rank, num_topk)` | Int64 | Top-K 专家索引 |
| `topk_weights` | `(num_max_tokens_per_rank, num_topk)` | Float32 | Top-K 权重 |
| `shared_l1_acts` | 同 x | FP8/BF16 | 共享专家 L1 激活（复用 x） |
| `shared_l1_acts_sf` | `(num_max_shared_sf, hidden/128)` | Int32 | 共享 L1 SF（M-major stride=1） |
| `shared_l2_acts` | `(num_max_tokens_per_rank, shared_intermediate)` | FP8/BF16 | 共享专家 L2 激活 |
| `shared_l2_acts_sf` | `(num_max_shared_sf, shared_intermediate/128)` | Int32 | 共享 L2 SF |
| `l1_acts` | `(num_ring_tokens, hidden)` | FP8/BF16 | 环形缓冲区 L1 激活 |
| `l1_acts_sf` | `(num_sf_ring_tokens, hidden/128)` | Int32 | 环形 L1 SF（M-major） |
| `l2_acts` | `(num_ring_tokens, intermediate_hidden)` | FP8/BF16 | 环形缓冲区 L2 激活 |
| `l2_acts_sf` | `(num_sf_ring_tokens, intermediate_hidden/128)` | Int32 | 环形 L2 SF |

**方法**：
- `destroy()`：释放缓冲区和句柄资源

**分配方式**：
- 单 rank：`torch.empty` 分配 int8 缓冲区
- 多 rank：`symm_mem.empty` 分配对称内存，通过 `symm_mem.rendezvous` 获取跨 rank 指针

### 1.2 工厂函数

```python
def get_symm_buffer_for_mega_moe(group, num_experts, num_max_tokens_per_rank,
                                 num_topk, hidden, intermediate_hidden,
                                 num_shared_experts=0,
                                 use_fp8_dispatch=None,
                                 mma_type='fp8xfp4',
                                 activation='swiglu') -> SymmBuffer
```

- 自动将 `num_max_tokens_per_rank` 对齐到 `get_token_alignment_for_mega_moe()` 返回值（384）
- `use_fp8_dispatch` 参数已弃用，向后兼容时发出 DeprecationWarning

### 1.3 权重变换

```python
def transform_weights_for_mega_moe(l1_weights, l2_weights,
                                    activation='swiglu') -> Tuple
```

**FP8 模式**（输入为 `(weights, sf)` 元组）：
- L1 权重：沿 N 维度交错排列 gate/up 部分（gran=8），SF 先交错再转置
- L2 权重：不变，SF 执行 `_transpose_sf_for_utccp` 转置

**BF16 模式**（输入为 tensor）：
- L1 权重：沿 N 维度交错排列 gate/up
- L2 权重：不变

**交错规则**（`_interleave_weights`）：
```python
# 原始排列: [gate_0..n, up_0..n]
# 交错排列: [gate_0..7, up_0..7, gate_8..15, up_8..15, ...]
```

**SF 转置**（`_transpose_sf_for_utccp`）：
- reshape `(-1, 4, 32, packed_sf_k)` → transpose(2,3) → reshape `(num_groups, mn, packed_sf_k)`
- 用于 UTCCP（Unified Tensor Core Compute Pipeline）的 SF 布局

### 1.4 MegaMoE 前向核函数

```python
def fp8_fp4_mega_moe(y, l1_weights, l2_weights, sym_buffer,
                     shared_l1_weights=None, shared_l2_weights=None,
                     cumulative_local_expert_recv_stats=None,
                     recipe=(1, 1, 32), activation='swiglu',
                     activation_clamp=None, fast_math=True) -> None
```

**参数**：
- `y`：输出张量，形状 `(num_tokens, hidden)`，BF16
- `l1_weights`/`l2_weights`：路由专家权重，`(weights_tensor, sf_tensor)` 元组
  - L1 权重形状：`(num_experts_per_rank, intermediate_hidden*2, hidden)`，dtype=Int8（packed FP4），K-major
  - L2 权重形状：`(num_experts_per_rank, hidden, intermediate_hidden)`，dtype=Int8（packed FP4），K-major
  - SF：dtype=Int32，gran_mn=1, gran_k=32，MN-major，TMA-aligned
- `sym_buffer`：`SymmBuffer` 实例
- `shared_l1_weights`/`shared_l2_weights`：可选共享专家权重，`(weights, sf)` 元组
  - 权重 dtype=Float8_e4m3fn，2D，K-major
  - L1 形状：`(shared_intermediate*2, hidden)`，L2 形状：`(hidden, shared_intermediate)`
- `cumulative_local_expert_recv_stats`：可选 Int32 张量，长度 `num_experts_per_rank`，统计每专家接收 token 数
- `recipe`：必须为 `(1, 1, 32)`
- `activation`：必须为 `"swiglu"`
- `activation_clamp`：激活 clamp 值（≥0），默认 infinity
- `fast_math`：是否启用快速数学模式（默认 True）

```python
def bf16_mega_moe(y, l1_weights, l2_weights, sym_buffer,
                  shared_l1_weights=None, shared_l2_weights=None,
                  cumulative_local_expert_recv_stats=None,
                  activation='swiglu', activation_clamp=None,
                  fast_math=True) -> None
```

- BF16 版本，参数结构类似，但权重无 SF，dtype=BF16
- MMA 类型固定为 `"bf16xbf16"`

---

## 二、C++ API

### 2.1 查询函数

```cpp
// 返回 token 对齐值（kLCMCandidateBlockM = 384）
int get_token_alignment_for_mega_moe();

// 返回给定配置下的 block_m
int get_block_m_for_mega_moe(
    int num_ranks, int num_experts,
    int num_max_tokens_per_rank, int num_tokens, int num_topk,
    const std::string& mma_type);

// 返回缓冲区大小和切片函数
tuple<int64_t, function> get_symm_buffer_size_for_mega_moe(
    int num_ranks, int num_experts,
    int num_max_tokens_per_rank, int num_topk,
    int hidden, int intermediate_hidden,
    const std::string& mma_type, const std::string& activation,
    int num_shared_experts = 0);
```

### 2.2 核函数入口

```cpp
void fp8_fp4_mega_moe(y, l1_weights_tuple, l2_weights_tuple,
    shared_l1_weights_tuple_opt, shared_l2_weights_tuple_opt,
    cumulative_local_expert_recv_stats,
    sym_buffer, sym_buffer_ptrs, rank_idx,
    num_max_tokens_per_rank, num_experts, num_topk,
    recipe, activation, activation_clamp_opt, fast_math);

void bf16_mega_moe(y, l1_weights, l2_weights,
    shared_l1_weights_opt, shared_l2_weights_opt,
    cumulative_local_expert_recv_stats,
    sym_buffer, sym_buffer_ptrs, rank_idx,
    num_max_tokens_per_rank, num_experts, num_topk,
    activation, activation_clamp_opt, fast_math);
```

---

## 三、启发式配置

文件：`csrc/jit_kernels/heuristics/mega_moe.hpp`

### 3.1 候选 Block M 值

```cpp
static constexpr int kNumCandidateBlockMs = 7;
static constexpr int kCandidateBlockM[7] = {8, 16, 32, 64, 96, 128, 192};
static constexpr int kLCMCandidateBlockM = 384;  // LCM of all candidates
```

### 3.2 MMA 类型

```cpp
enum class MmaKind { BF16 = 0, MXFP8FP4 = 1 };
// BF16: element_size=2, no SF
// MXFP8FP4: element_size=1, with SF
```

### 3.3 Block 配置选择

`get_block_config_for_mega_moe(...)` 返回 `(cluster_size, block_m, store_block_m, block_k, num_epilogue_warpgroups)`：
- 基于 `num_expected_tokens_per_expert` 分档选择 block_m（16/32/64/96/128/192）
- block_k 为 128 或 256
- cluster_size 固定为 2（thread block cluster）
- Ring 容量遍历所有候选 block_m，取最坏情况 live pool blocks × block_m 的最大值，对齐到 384

### 3.4 环形缓冲区容量计算

```
num_pool_blocks = ceil(总路由tokens / block_m) + num_experts_per_rank
num_live_pool_blocks = sched::get_num_max_live_pool_blocks(num_pool_blocks, num_sms, ...)
num_ring_tokens = max(所有候选block_m的 num_live_pool_blocks × block_m)
num_ring_tokens = align(num_ring_tokens, 384)
```

SF 环形 token 数通过 `get_num_sf_ring_tokens(num_ring_tokens, block_m)` 计算，确保所有候选 block_m 下的 SF 需求。

---

## 四、使用约束

1. **架构限制**：仅 SM100（Blackwell）支持
2. **激活函数**：仅 SwiGLU
3. **Recipe**：FP8/FP4 版本 recipe 必须为 `(1, 1, 32)`
4. **权重布局**：K-major（stride(-1)==1），contiguous
5. **SF 布局**：MN-major（stride(-2)==1），TMA 对齐，dtype=Int32（UE8M0 packed）
6. **L1 权重形状**：intermediate_hidden×2（gate+up 交错）
7. **隐藏层对齐**：hidden 和 intermediate_hidden 均须为 128 的倍数（FP8 模式）
8. **Token 对齐**：num_max_tokens_per_rank 须对齐到 384
9. **rank 数量**：num_experts 必须能被 num_ranks 整除
10. **调试模式**：`DG_COMM_KERNEL_DEBUG` 环境变量非零时，kernel 执行后清零 sym_buffer（调用者需重新填充）

---

## 五、相关链接

- [/deepseek/deep-gemm/concepts/moe-operations](/deepseek/deep-gemm/concepts/moe-operations) — MegaMoE 概念详解
- [/deepseek/deep-gemm/examples/moe-forward](/deepseek/deep-gemm/examples/moe-forward) — MegaMoE 使用示例
- [/deepseek/deep-ep/](/deepseek/deep-ep/) — DeepEP 专家并行通信库
