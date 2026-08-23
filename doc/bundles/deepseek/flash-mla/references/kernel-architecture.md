---
type: reference
scope: flash-mla
name: FlashMLA SM90/SM100 内核架构
version: "1.0.0"
source: csrc/sm90/, csrc/sm100/, csrc/smxx/, csrc/api/common.h, csrc/params.h
description: FlashMLA SM90 (Hopper) 和 SM100 (Blackwell) 内核架构详解
---

# SM90/SM100 内核架构详解

FlashMLA 针对 NVIDIA Hopper（SM90）和 Blackwell（SM100）GPU 架构分别实现了高度优化的 CUDA 内核。两者共享架构无关的通用组件（调度元数据生成、SplitKV combine），但在内核主体部分充分利用各自的硬件特性。

---

## 一、整体架构分层

```
Python API 层 (flash_mla/__init__.py, flash_mla_interface.py)
    │
    ▼
C++ API 层 (csrc/api/*.h, api.cpp)
    │  ├── Arch 检测（is_sm90a / is_sm100f）
    │  ├── 参数校验与张量 reshape
    │  ├── 调度元数据生成（首次调用）
    │  └── 架构/特性分发（DISPATCH 宏 + ImplBase）
    │
    ├──────────────────────┬───────────────────────┐
    ▼                      ▼                       ▼
SM90 内核 (csrc/sm90/)  SM100 内核 (csrc/sm100/)  SMxx 通用 (csrc/smxx/)
    │                      │                       │
    ├─ decode/dense/       ├─ decode/head64/       ├─ decode/
    │  └─ splitkv_mla      │  └─ kernel.cuh        │  ├─ get_decoding_sched_meta/
    ├─ decode/sparse_fp8/  ├─ decode/head128/      │  └─ combine/
    │  └─ splitkv_mla      ├─ prefill/sparse/
    └─ prefill/sparse/     │  └─ fwd/
       └─ fwd              ├─ prefill/sparse/
                           │  └─ fwd_for_small_topk/
                           └─ prefill/dense/
                              └─ (CUTLASS-based)
```

---

## 二、SM90 (Hopper) 内核架构

### 2.1 关键硬件特性

SM90（Hopper H100/H200）引入的关键硬件特性：

| 特性 | 说明 | FlashMLA 用途 |
|---|---|---|
| **WGMMA** (Warp Group Matrix Multiply-Accumulate) | 128 线程（4 warps）协作的矩阵乘指令，形状 64×N×16 | QK 和 PV 两个 GEMM 阶段 |
| **TMA** (Tensor Memory Accelerator) | 异步张量拷贝引擎，支持多维张量传输 | Q/K/O 数据在全局内存和 shared memory 间的异步搬运 |
| **DSM** (Distributed Shared Memory) | Thread Block Cluster 内跨 CTA 的 shared memory 访问 | Remote P（attention scores）的 SS 模式 WGMMA |
| **Thread Block Cluster** | 多个 CTA 组成 cluster，可协同执行 | GQA/MQA 多头协作（CLUSTER_SIZE = NUM_M_BLOCKS） |
| **ClusterTransactionBarrier** | Cluster 级异步事务屏障 | TMA 拷贝和 DSM 访问的同步 |
| **cp.async + L2 prefetch** | 异步全局内存加载，带 L2 缓存提示 | FP8 KV cache 的反量化数据加载 |

### 2.2 Dense Decode 内核（BF16/FP16）

**配置常量：**

| 常量 | 值 | 说明 |
|---|---|---|
| BLOCK_SIZE_M | 64 | Q 方向 tile 大小（对应 64 个 query head 或 split） |
| PAGE_BLOCK_SIZE | 64 | KV cache 页块大小（token 数） |
| HEAD_DIM_K | 576 | K 头维度（V32 模式默认） |
| HEAD_DIM_V | 512 | V 头维度 |
| NUM_THREADS | 256 | 每个 CTA 的线程数 |

**WGMMA 配置：**

| MMA 阶段 | 指令形状 | 模式 | 说明 |
|---|---|---|---|
| QK (sQ) | 64×64×16 F32BF16BF16 | SS | Q 从 smem、K 从 smem 加载 |
| QK (rQ) | 64×64×16 F32BF16BF16 | RS | Q 从寄存器、K 从 smem 加载 |
| PV (LocalP) | 64×256×16 F32BF16BF16 | RS (MN-major) | P 从寄存器、V 从 smem 加载 |
| PV (RemoteP) | 64×256×16 F32BF16BF16 | SS (MN-major) | P 从 DSM、V 从 smem 加载 |

**Shared Memory 布局（Traits）：**
- `smem_sQ`：Q 的 shared memory 缓冲区
- `smem_sK0/smem_sK1`：K 的双缓冲（双缓冲隐藏加载延迟）
- `smem_sP0`：P（attention scores）缓冲区
- `smem_sM`：online softmax max 值
- `sL_reduction_wksp`：LSE reduction 工作空间
- `smem_sScale0/smem_sScale1`：缩放因子双缓冲
- NamedBarriers：`sScale0Ready/sScale1Ready`、`sP0Ready`、`rO1sP0sV0RIssued`、`sMInitialized`

**执行流程：**
1. TMA 异步加载 Q tile 到 smem
2. 循环遍历 KV blocks：
   a. TMA 加载 K tile 到 smem（双缓冲交替）
   b. WGMMA QK 计算 attention scores
   c. Online softmax 更新 max/sum
   d. WGMMA PV 计算 output 累加
   e. 对于 GQA/MQA，通过 DSM 访问其他 CTA 的 P 矩阵
3. 输出 O 到全局内存

### 2.3 Sparse FP8 Decode 内核

**编译期模板参数：**

| 参数 | V32 | MODEL1 | 说明 |
|---|---|---|---|
| HEAD_DIM_K | 576 | 512 | K 总维度 |
| HEAD_DIM_V | 512 | 512 | V 维度 |
| HEAD_DIM_ROPE | 64 | 64 | RoPE 维度 |
| HEAD_DIM_NOPE | 512 | 448 | NoPE 维度 |
| QUANT_TILE_SIZE | 128 | 64 | 反量化 tile 大小 |
| NUM_SCALES | 4 | 8 (含 padding) | 每 token 缩放因子数量 |
| NUM_BYTES_PER_TOKEN | 656 | 576 | 每 token KV cache 字节数 |
| NUM_THREADS | 384 | 384 | 128×3 = 3 个 warpgroup |
| BLOCK_M | 64 | 64 | Q 方向 tile |
| TOPK_BLOCK_SIZE | 64 | 64 | K 方向 tile（topk 分块） |
| NUM_K_BUFS | 2 | 2 | K 双缓冲 |
| CLUSTER_SIZE | NUM_HEADS/64 | NUM_HEADS/64 | Cluster 大小（h=128 时为 2） |

**WGMMA 指令（同 Dense）：**
- QK: `GMMA::MMA_64x64x16_F32BF16BF16_SS/RS`
- PV: `GMMA::MMA_64x256x16_F32BF16BF16_SS/RS` (MN-major)

**FP8 反量化流程：**
1. 使用 PTX `ld.global.nc` 指令带 L1/L2 缓存提示从全局内存加载 FP8 数据
2. `cvt_fp8x8_bf16x8` 将 8 个 `float8_e4m3` 转为 8 个 `bfloat16` 并乘以对应 scale
3. 反量化后的数据写入 smem 供 WGMMA 使用

**NamedBarriers：**
- `sScale_and_sS_ready/sScale_and_sS_free`：scale 和 S 缓冲区同步
- `oBuf_free_and_sL_ready`：输出缓冲区和 LSE 就绪
- `epilogue_r2s_ready`：epilogue 寄存器到 smem 就绪
- `batch_loop_sync/warpgroup0_sync`：循环和 warpgroup 同步

**实例化矩阵：**

| | NUM_HEADS=64 | NUM_HEADS=128 |
|---|---|---|
| ModelType::V32 | `v32_persistent_h64.cu` | `v32_persistent_h128.cu` |
| ModelType::MODEL1 | `model1_persistent_h64.cu` | `model1_persistent_h128.cu` |

### 2.4 Sparse Prefill 内核

**配置：**
- D_V=512, B_H=64, B_TOPK=64, NUM_THREADS=384
- MMA 配置与 decode 相同（64×64×16 QK, 64×256×16 PV）
- V32 模式（D_QK=576）时 S 缓冲区与 K 的 RoPE 部分重叠节省 smem
- MODEL1 模式（D_QK=512）时分配两个 S 缓冲区
- 支持 `HAVE_TOPK_LENGTH` 模板参数（可变 topk 长度）

**实例化：**
- `phase1_k512.cu`、`phase1_k576.cu`
- `phase1_k512_topklen.cu`、`phase1_k576_topklen.cu`

---

## 三、SM100 (Blackwell) 内核架构

### 3.1 关键硬件特性

SM100（Blackwell B100/B200）引入的关键新特性：

| 特性 | 说明 | FlashMLA 用途 |
|---|---|---|
| **Tensor Memory (tmem)** | 片上大容量张量存储，替代部分 shared memory | 存储 Q、P（attention scores）、O 矩阵 |
| **UTCMMA** | 支持 tmem 操作的矩阵乘指令 | P 和 O 的 MMA 计算，直接读写 tmem |
| **UTCCP** (Tensor Memory Copy) | tmem 异步拷贝引擎 | tmem 数据搬运 |
| **Dual GEMM** | 单次 MMA 产生两行 P 矩阵（行 0-63 和 64-127） | 加倍 P 计算吞吐量 |
| **WS (Warp-Specialized) 模式** | MMA 指令支持 warp-specialized 调度 | 生产-消费者流水线 |
| **NOELECT** | MMA 指令不选举 warpgroup leader | 减少调度开销 |

### 3.2 Sparse Decode Head64 内核

**Tensor Memory 列布局：**

| tmem 列范围 | 内容 | 维度 |
|---|---|---|
| 0 ~ 255 | 输出 O | 512 维 V（BF16，256列×2=512值） |
| 256 ~ 399 | 查询 Q | 288 列（576维 V32 或 512维 MODEL1） |
| 400 ~ 464 | P（attention scores） | 64 列（128 个 topk 块，dual GEMM） |

**编译期常量：**

| 参数 | V32 | MODEL1 | 说明 |
|---|---|---|---|
| D_Q / D_K | 576 | 512 | Q/K 总维度 |
| D_V | 512 | 512 | V 维度 |
| D_NOPE | 512 | 448 | NoPE 维度（FP8） |
| D_ROPE | 64 | 64 | RoPE 维度（BF16） |
| QUANT_TILE_SIZE | 128 | 64 | 反量化 tile 大小 |
| V_HAVE_ROPE | false | true | V 是否包含 RoPE 部分 |
| NUM_SCALES_EACH_TOKEN | 4 | 8 | 每 token 缩放因子数 |
| TMA_K_STRIDE | 656 | 576 | TMA 加载 KV 的 stride（字节） |
| B_H / B_TOPK | 64 / 64 | 64 / 64 | 头数 / topk 块大小 |
| NUM_BUFS | 2 | 2 | K 双缓冲 |
| NUM_INDEX_BUFS | 4 | 4 | 索引缓冲区数量 |
| NUM_THREADS | 384 | 384 | 128×3 warpgroup |
| D_Q_SW128 | 512 | 512 | SW128 加载的 Q 维度 |
| D_Q_SW64 | 64 | 0 | SW64 加载的 Q 维度（V32 的 RoPE 部分） |
| K_ROPE_SW | 64 | 128 | RoPE 加载的 SW 宽度（字节） |

**MMA 指令：**

| 阶段 | 指令 | 形状 | 说明 |
|---|---|---|---|
| P 计算 | `SM100_MMA_F16BF16_WS_TS_NOELECT` | 64×128×K (B_TOPK×2) | TS 模式，dual GEMM |
| O 计算 | `SM100_MMA_F16BF16_WS_SS_NOELECT` | 64×256×K (MN-major) | SS 模式 |

- Dual GEMM：P 计算时 B_TOPK×2=128，一次 MMA 产生两块 P（行 0-63 和行 64-127），经 warp reduce 合并

**Shared Memory 优化：**
- 使用 union 重叠 Q/O 和 KV dequant 缓冲区，最大化 smem 利用率
- 多个 transaction barriers 用于 TMA async copy 和 tmem 操作的同步

### 3.3 Sparse Decode Head128 支持

SM100 上 h_q=128 的 decode 有两种实现路径：

1. **d_qk=512（MODEL1）专用内核**：
   - 路径：`csrc/sm100/prefill/sparse/fwd_for_small_topk/head128/instantiations/phase1_decode_k512.cu`
   - `num_sm_parts = max(arch.num_sms / s_q / 2, 1)`
   - `fixed_overhead_num_blocks = 3`（比 head64 少）
   - 调用 `sm100::fwd_for_small_topk::head128::run_fwd_for_small_topk_phase1_kernel<DecodeWithSplitKV, 512>`

2. **d_qk=576（V32）双次 head64**：
   - 通过 `Decode_Sm100_Head64x2_Impl` 调用 head64 内核两次，每次处理 64 头
   - `num_sm_parts = max(arch.num_sms / s_q, 1)`（与 head64 相同）

### 3.4 Dense Prefill/Backward（CUTLASS 实现）

SM100 的 dense prefill/backward 基于 NVIDIA CUTLASS 库实现，采用 TMA warpspecialized 流水线：

**文件结构：**
- `fmha_cutlass_fwd_sm100.cu` / `fmha_cutlass_bwd_sm100.cu`：编译入口
- `sm100_fmha_mla_fwd_mainloop_tma_warpspecialized.hpp`：MLA 专用 mainloop
- `sm100_fmha_mla_load_tma_warpspecialized.hpp`：MLA 专用 TMA 加载
- `sm100_fmha_fwd_mainloop/epilogue/load_tma_warpspecialized.hpp`：通用 mainloop/epilogue/load
- `fmha.hpp` / `fmha_device_bwd.hpp`：device 层
- Tile scheduler：`fmha_tile_scheduler.hpp` / `fmha_causal_tile_scheduler.hpp`
- 辅助 kernel：`fmha_kernel_bwd_convert.hpp`、`fmha_kernel_bwd_sum_OdO.hpp`
- 公共组件：`fmha_common.hpp`、`pipeline_mla.hpp`、`mask.cuh`、`gather_tensor.hpp`

**注意：** BWD 目前不支持 GQA（`num_qo_heads != num_kv_heads` 时抛出 ValueError）。

### 3.5 Sparse Prefill 内核

**Head64 配置：**
- 支持 d_qk=512/576，通过模板参数分发
- 使用 Dual GEMM + Tensor Memory
- 实例化：`head64/instantiations/phase1_k512.cu`、`phase1_k576.cu`

**Head128 配置：**
- 标准路径：`head128/instantiations/phase1_k512.cu`、`phase1_k576.cu`
- Small topk 路径（topk ≤ 1280）：`fwd_for_small_topk/head128/instantiations/phase1_prefill_k512.cu`

**公共子程序（common_subroutine.h）：**
- `load_indices_and_generate_mask`：加载索引并生成有效性掩码
- `retrieve_mask_and_reduce_p`：从 tmem 获取 P，warp 间 reduce，执行 masking
- `rescale_O`：对 tmem 中 O 按 chunk 重新缩放
- `get_max/get_s_from_p`：online softmax 计算

---

## 四、SMxx 通用组件

### 4.1 调度元数据生成内核

```
smxx::decode::run_get_decoding_sched_meta_kernel(GetDecodeSchedMetaParams &params)
```

架构无关的调度元数据生成内核，在首次调用 decode 时运行。生成 `DecodingSchedMeta` 结构体数组，记录每个 SM part 需要处理的请求范围、block 范围和 split 索引。

**DecodingSchedMeta 结构体（对齐 32 字节）：**
```cpp
struct DecodingSchedMeta {
    int begin_req_idx, end_req_idx;     // inclusive
    int begin_block_idx, end_block_idx; // inclusive, exclusive
    int begin_split_idx;
    int is_first_req_splitted, is_last_req_splitted;
    int _pad[1];
};
```

**参数计算：**
- dense decode：`num_sm_parts = max(num_sms / h_k / ceil_div(s_q * h_q / h_k, 64), 1)`
- SM90 sparse：`num_sm_parts = max(num_sms / s_q / (h_q/64), 1)`
- SM100 sparse head64：`num_sm_parts = max(num_sms / s_q, 1)`
- SM100 sparse head128（MODEL1）：`num_sm_parts = max(num_sms / s_q / 2, 1)`
- `block_size_n = 64`，`fixed_overhead_num_blocks = 5`（head128 small_topk 为 3）

### 4.2 Combine 内核

```cpp
template<typename ElementT>
void run_flash_mla_combine_kernel(CombineParams &params);
```

架构无关的 SplitKV combine 内核，将各 split 的部分输出和 LSE 合并为最终结果。Combine 逻辑基于 online softmax 的数学性质：

```
对于多个 split i，已知各 split 的 (m_i, l_i, o_i)：
m_new = max(m_0, m_1, ..., m_{n-1})
l_new = Σ l_i * exp(m_i - m_new)
o_new = Σ o_i * l_i * exp(m_i - m_new) / l_new
```

支持 `attn_sink`：最终输出乘以 `exp(lse) / (exp(lse) + exp(attn_sink))`。

---

## 五、C++ API 分发机制

### 5.1 Arch 结构体

```cpp
struct Arch {
    int major, minor, num_sms;
    cudaDeviceProp device_prop;
    bool is_sm90a() const { return major == 9 && minor == 0; }
    bool is_sm100f() const { return major == 10; }
};
```

### 5.2 DISPATCH 宏

| 宏 | 支持的值 | 用途 |
|---|---|---|
| `DISPATCH_NUM_HEADS(N, NAME, ...)` | 64, 128 | 查询头数分发 |
| `DISPATCH_HEAD_DIM(D, NAME, ...)` | 512, 576 | K 头维度分发 |
| `DISPATCH_BOOLEAN_FLAG(F, NAME, ...)` | true, false | 布尔特性分发 |
| `DISPATCH_MODEL_TYPE(T, NAME, ...)` | V32, MODEL1 | 模型类型分发 |

### 5.3 ImplBase 特性分发

```cpp
template<typename RunArgT_, typename FeatureT_>
class ImplBase {
    virtual void run_(const RunArgT &params, const std::vector<FeatureT> &required_features) = 0;
    constexpr virtual std::span<const FeatureT> get_supported_features() const = 0;
    void run(...) { check_features(); run_(...); }
};
```

通过 `DECLARE_SUPPORTED_FEATURES(...)` 宏声明支持的特性集合，`run()` 方法先验证所有要求的特性是否被支持，再调用具体实现。

### 5.4 Sparse Decode 实现分发

| GPU | h_q | d_qk | 实现类 |
|---|---|---|---|
| SM100 | 64 | 576/512 | `Decode_Sm100_Head64_Impl` |
| SM100 | 128 | 576 | `Decode_Sm100_Head64x2_Impl`（2x head64） |
| SM100 | 128 | 512 | `Decode_Sm100_Head128_Impl`（small_topk 专用内核） |
| SM90 | 64/128 | 576/512 | `Decode_Sm90_Impl` |

### 5.5 Sparse Prefill 实现分发

| GPU | h_q | topk | 实现类 |
|---|---|---|---|
| SM90 | 64/128 | 任意 | `Fwd_Sm90_Impl` |
| SM100 | 64 | 任意 | `Fwd_Sm100_Head64_Impl` |
| SM100 | 128 | ≤1280 且支持所有特性 | `Fwd_Sm100_Head128_Small_TopK_Impl` |
| SM100 | 128 | 其他 | `Fwd_Sm100_Head128_Impl` |

---

## 六、编译配置

### 6.1 编译环境

- **C++ 标准**：C++20
- **优化 flags**：`-O3 -DNDEBUG --use_fast_math`
- **架构 flags**：`arch=compute_90a,code=sm_90a`（SM90）、`arch=compute_100f,code=sm_100f`（SM100）
- **NVCC 要求**：SM100 编译需要 NVCC ≥ 12.9

### 6.2 环境变量控制

| 环境变量 | 作用 |
|---|---|
| `FLASH_MLA_DISABLE_SM90=1` | 禁用 SM90 内核编译 |
| `FLASH_MLA_DISABLE_SM100=1` | 禁用 SM100 内核编译 |
| `FLASH_MLA_DISABLE_FP16` | 禁用 FP16 dense decode 内核 |

### 6.3 源文件清单

| 类别 | 源文件 |
|---|---|
| API 入口 | `csrc/api/api.cpp` |
| SMxx 通用 | `get_decoding_sched_meta.cu`、`combine.cu` |
| SM90 dense decode | `fp16.cu`、`bf16.cu` |
| SM90 sparse decode | `model1_persistent_h64.cu`、`model1_persistent_h128.cu`、`v32_persistent_h64.cu`、`v32_persistent_h128.cu` |
| SM90 sparse prefill | `fwd.cu`、`phase1_k512.cu`、`phase1_k512_topklen.cu`、`phase1_k576.cu`、`phase1_k576_topklen.cu` |
| SM100 dense prefill/bwd | `fmha_cutlass_fwd_sm100.cu`、`fmha_cutlass_bwd_sm100.cu` |
| SM100 sparse prefill | head64 (`k512.cu`, `k576.cu`)、head128 (`k512.cu`, `k576.cu`)、fwd_for_small_topk/head128 (`phase1_prefill_k512.cu`) |
| SM100 sparse decode | head64 (`v32.cu`, `model1.cu`)、fwd_for_small_topk/head128 (`phase1_decode_k512.cu`) |

### 6.4 外部依赖

- **CUTLASS**：git submodule at `csrc/cutlass/`，提供 SM100 dense prefill/bwd 和基础 MMA 指令封装
- **kerutils**：头文件库 at `csrc/kerutils/include/`，提供 SM80/SM90/SM100 的底层 PTX intrinsic 和 helper 函数

---

## 七、相关链接

- [/deepseek/flash-mla/references/api](/deepseek/flash-mla/references/api) — Python API 参考
- [/deepseek/flash-mla/references/kv-cache-layout](/deepseek/flash-mla/references/kv-cache-layout) — FP8 KV cache 布局详解
- [/deepseek/flash-mla/concepts/hopper-blackwell-kernels](/deepseek/flash-mla/concepts/hopper-blackwell-kernels) — Hopper/Blackwell 硬件特性与内核设计
- [/deepseek/flash-mla/concepts/splitkv](/deepseek/flash-mla/concepts/splitkv) — SplitKV 调度与执行流程
- [/deepseek/deep-gemm/](/deepseek/deep-gemm/) — DeepGEMM 高性能 GEMM 核函数库
