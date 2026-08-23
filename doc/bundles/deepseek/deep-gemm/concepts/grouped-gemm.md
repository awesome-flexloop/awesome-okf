---
type: concept
scope: deep-gemm
name: 分组 GEMM 与 MoE 并行
version: "2.6.1"
source: csrc/apis/gemm.hpp, deep_gemm/include/deep_gemm/common/types.cuh
description: DeepGEMM 的 M-grouped/K-grouped 分组 GEMM 设计，服务于 MoE 专家并行计算
---

# 分组 GEMM 与 MoE 并行

分组 GEMM（Grouped GEMM）是 DeepGEMM 为 MoE（Mixture of Experts）模型设计的核心计算模式。在 MoE 层中，不同 token 被路由到不同的专家，每个专家仅处理分配给它的 token 子集，这导致矩阵乘法不再是一个规则的大矩阵乘，而是多个小矩阵乘的集合。分组 GEMM 将这些小矩阵乘高效地批量执行，避免逐个启动核函数的开销。

---

## 一、GEMM 类型枚举

```cpp
// deep_gemm/include/deep_gemm/common/types.cuh
enum class GemmType {
    Normal = 0,                              // 标准矩阵乘
    MGroupedContiguous = 1,                  // M 分组，连续布局
    MGroupedMasked = 2,                      // M 分组，掩码布局
    KGroupedContiguous = 3,                  // K 分组，连续布局
    Batched = 4,                             // 批量 GEMM
    MGroupedContiguousWithPsumLayout = 5,    // M 分组 + PSUM 布局
    KGroupedContiguousWithPsumLayout = 6     // K 分组 + PSUM 布局
};
```

---

## 二、M-Grouped GEMM

### 2.1 计算模式

M-Grouped GEMM 用于 MoE 的**前向传播**（FFN 第一层和第二层）。其核心思想是：

- 所有 token 在 M 维度上拼接在一起，每个 token 被分配到一个 expert
- 权重矩阵按 expert 分组为 `[G, N, K]`（G 个专家）
- 通过 `grouped_layout` 张量指示每个 token 属于哪个 expert
- 核函数内部根据 expert ID 选择对应的权重矩阵进行计算

**形状**：
- 连续布局：`[M, K] @ [G, N, K].mT -> [M, N]`
  - A（激活）：M 个 token，每个 token 有 K 维特征
  - B（权重）：G 个专家，每个专家有 N×K 权重矩阵
  - D（输出）：M 个 token，每个 token 有 N 维输出
  - grouped_layout：长度为 M 的 Int32 张量，`grouped_layout[i]` 表示第 i 个 token 对应的 expert ID

- 掩码布局：`[G, M, K] @ [G, N, K].mT -> [G, M, N]`
  - A（激活）：G 个专家，每个专家最多 M 个 token（含 padding）
  - B（权重）：G 个专家
  - D（输出）：G 个专家的输出
  - masked_m：长度为 G 的 Int32 张量，`masked_m[g]` 表示第 g 个专家的实际 token 数
  - expected_m：padding 后的 M 大小

### 2.2 连续布局 vs 掩码布局

| 特性 | 连续布局（contiguous） | 掩码布局（masked） |
|---|---|---|
| 激活形状 | `[M, K]` 2D，token 按 expert 顺序排列 | `[G, M, K]` 3D，每个 expert 有独立的 M 维 |
| grouped_layout | 长度 M，标记每个 token 的 expert ID | 长度 G，标记每个 expert 的实际 token 数 |
| 内存效率 | 高，无 padding | 低，有 padding（expected_m - masked_m[g]） |
| 适用场景 | token dispatch 后连续排列 | expert 内 token 独立 padding（如 EP 通信后） |
| PSUM 布局 | 支持 | 不支持 |

### 2.3 PSUM 布局（Partial Sum）

在张量并行（TP）或专家并行（EP）场景下，分布式 rank 之间需要累加 partial sum。PSUM 布局是 DeepGEMM 为分布式计算设计的特殊数据排列：

- `use_psum_layout=True` 时，grouped_layout 的语义变为长度为 G 的张量，标识每个 expert 对应的 rank
- SFA（A 的缩放因子）打包时跳过 gap 行（不属于当前 rank 的 token）
- `expected_m_for_psum_layout` 指定预期的 M 值（含 padding）
- 支持 K-grouped 场景（`KGroupedContiguousWithPsumLayout`）

### 2.4 零填充保证

- SM100 连续布局 M-grouped GEMM 有 `ensure_zero_padding` 参数（默认 True）
- 确保 padding 区域为零，避免 TMA 越界读取产生垃圾值
- SM90 无此参数（硬件行为不同）

---

## 三、K-Grouped GEMM

### 3.1 计算模式

K-Grouped GEMM 用于 MoE 的**反向传播**（权重梯度计算）。反向传播时，每个 expert 的输入和输出梯度沿 K 维度拼接：

**形状（TN 布局）**：
- A（输出梯度）：连续拼接的 `[sum_k, M]`，每个 expert 的 K 不同
- B（激活）：连续拼接的 `[sum_k, N]`
- D（权重梯度）：3D `[G, M, N]`，每个 expert 的权重梯度
- ks_cpu：CPU 上的整数列表，`ks_cpu[g]` 表示第 g 个 expert 的 K 值
- grouped_layout：长度为 G 的 Int32 张量

```
A: [k0 + k1 + ... + k(G-1), M]  (连续拼接，各 expert 的 dy)
B: [k0 + k1 + ... + k(G-1), N]  (连续拼接，各 expert 的 x)
D: [G, M, N]                    (每个 expert 的 dW)
```

### 3.2 NT vs TN 布局

| 布局 | SM90 FP8 | SM90 BF16 | SM100 FP8 | SM100 BF16 | C 张量 |
|---|---|---|---|---|---|
| NT（A=K-major） | ✅ | ❌ | ❌ | ❌ | 必须提供 |
| TN（A=N-major） | ❌ | ✅ | ✅ | ✅ | 必须提供 |

- NT 布局要求 recipe=(1,1,128)，仅 SM90 FP8，不支持 PSUM
- TN 布局支持 gran_k=32 或 128，SM100 支持 PSUM
- NT 布局需要额外分配 tensormap buffer（`num_sms * 4 * sizeof(CUtensorMap)` 字节），用于 TMA 描述符双缓冲

### 3.3 K 对齐

- K-alignment 通过 `heuristics_runtime->get_mk_alignment_for_contiguous_layout()` 获取
- 默认值 128，SM100 可根据 expected_m 动态调整（32-224，步长 32）
- 必须满足 `k_alignment % 32 == 0`
- 每个 expert 的 K 值必须是 k_alignment 的倍数

---

## 四、MoE 前向中的分组 GEMM 流程

典型的 MoE FFN 层前向计算涉及两次分组 GEMM：

```
                    ┌─────────────────────────────┐
                    │     Router (top-k 选择)      │
                    └──────────┬──────────────────┘
                               │
                               ▼
                    ┌─────────────────────────────┐
                    │  Token Dispatch（按expert排序）│
                    │  → 形成 grouped_layout       │
                    └──────────┬──────────────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
    ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
    │ Expert 0    │   │ Expert 1    │   │ Expert G-1  │
    │ m_grouped_  │   │ m_grouped_  │   │ m_grouped_  │
    │ gemm_nt_    │   │ gemm_nt_    │   │ gemm_nt_    │
    │ contiguous  │   │ contiguous  │   │ contiguous  │
    │ (Gate+Up)   │   │ (Gate+Up)   │   │ (Gate+Up)   │
    └──────┬──────┘   └──────┬──────┘   └──────┬──────┘
           │                 │                 │
           ▼                 ▼                 ▼
    ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
    │  SwiGLU     │   │  SwiGLU     │   │  SwiGLU     │
    │  Activation │   │  Activation │   │  Activation │
    └──────┬──────┘   └──────┬──────┘   └──────┬──────┘
           │                 │                 │
           ▼                 ▼                 ▼
    ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
    │ m_grouped_  │   │ m_grouped_  │   │ m_grouped_  │
    │ gemm_nt_    │   │ gemm_nt_    │   │ gemm_nt_    │
    │ contiguous  │   │ contiguous  │   │ contiguous  │
    │ (Down)      │   │ (Down)      │   │ (Down)      │
    └──────┬──────┘   └──────┬──────┘   └──────┬──────┘
           │                 │                 │
           └────────────────┼────────────────┘
                            ▼
                   ┌──────────────────┐
                   │  Token Combine   │
                   │  (按top-k权重求和) │
                   └──────────────────┘
```

DeepGEMM 的 **MegaMoE** 模式将上述流程（dispatch + GEMM1 + SwiGLU + GEMM2 + combine）完全融合为单个核函数，通过对称环形缓冲区实现零拷贝通信。参见 [/deepseek/deep-gemm/concepts/moe-operations](/deepseek/deep-gemm/concepts/moe-operations)。

---

## 五、M/K 对齐与启发式

### 5.1 MK 对齐配置

```python
deep_gemm.set_mk_alignment_for_contiguous_layout(128)
deep_gemm.get_mk_alignment_for_contiguous_layout()  # → 128
deep_gemm.get_theoretical_mk_alignment_for_contiguous_layout(expected_m=None)
```

- **SM90**：固定 128
- **SM100**：动态计算，从 224 递减（步长 32），确保 `block_m - 32 >= expected_m`，最小 32
- 影响连续布局下 TMA 加载效率和 padding 量

### 5.2 Block 大小倍数

```python
deep_gemm.set_block_size_multiple_of((128, 64))  # M=128倍数, N=64倍数
```

强制 JIT 核函数的 block 维度为指定倍数，用于对齐外部 tile 大小约束。

### 5.3 编译维度

```python
fp8_gemm_nt(..., compiled_dims="nk")  # 或 "mn"
```

- `"nk"`：JIT 按 N、K 维度特化（NT/NN 转置默认）
- `"mn"`：JIT 按 M、N 维度特化（TN/TT 转置默认）
- 可通过 `set_ignore_compile_dims(True)` 禁用维度特化以减少编译次数

---

## 六、关键约束

1. **grouped_layout**：必须为 Int32、contiguous，长度与 M（非 psum）或 G（psum）匹配
2. **masked_m**：必须为 Int32、contiguous，长度为 G
3. **B 张量（权重）**：3D `[G, N, K]`，必须为 K-major（SM90）或支持 K/MN-major（SM100）
4. **D 张量**：必须为 N-major（行优先），BF16 类型
5. **K-grouped**：ks_cpu 中每个 K 值必须是 k_alignment 的倍数；C 张量（用于累加）必须提供且 contiguous
6. **M-grouped contiguous 的零填充**：SM100 默认 ensure_zero_padding=True，要求 padding 区域为零
7. **架构分发**：
   - M-grouped：SM90→1D2D kernel，SM100→1D1D kernel
   - K-grouped NT：仅 SM90 FP8
   - K-grouped TN：SM90 BF16，SM100 FP8/BF16

---

## 七、相关链接

- [/deepseek/deep-gemm/concepts/fp8-gemm](/deepseek/deep-gemm/concepts/fp8-gemm) — FP8/FP4 量化与缩放因子
- [/deepseek/deep-gemm/concepts/moe-operations](/deepseek/deep-gemm/concepts/moe-operations) — MegaMoE 融合核
- [/deepseek/deep-gemm/concepts/performance-optimization](/deepseek/deep-gemm/concepts/performance-optimization) — TMA/WGMMA 性能优化
- [/deepseek/deep-gemm/references/api](/deepseek/deep-gemm/references/api) — 分组 GEMM API 参考
- [/deepseek/deep-ep/](/deepseek/deep-ep/) — DeepEP 专家并行通信库
