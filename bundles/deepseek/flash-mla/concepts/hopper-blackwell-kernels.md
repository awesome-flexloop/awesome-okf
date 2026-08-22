---
type: concept
scope: flash-mla
name: Hopper 与 Blackwell 内核设计
version: "1.0.0"
source: csrc/sm90/, csrc/sm100/, csrc/sm90/helpers.h, csrc/sm100/helpers.h, docs/
description: FlashMLA 在 Hopper (SM90) 和 Blackwell (SM100) GPU 上的硬件特性利用与内核设计差异
---

# Hopper 与 Blackwell 内核设计

FlashMLA 针对 NVIDIA Hopper（SM90）和 Blackwell（SM100）两代 GPU 架构分别实现了高度定制的 CUDA 内核。两代架构在矩阵计算单元、内存层次结构和通信机制上有重大差异，FlashMLA 的内核设计充分利用了各自的硬件特性。

---

## 一、Hopper (SM90) 架构特性

### 1.1 WGMMA（Warp Group Matrix Multiply-Accumulate）

WGMMA 是 Hopper 引入的 warp-group 级矩阵乘指令，由 128 个线程（4 个 warp，即一个 warpgroup）协作执行：

| 属性 | 值 |
|---|---|
| 参与线程数 | 128（4 warps） |
| 基本形状 | 64×N×16（M=64 固定，N 可选 8/16/24/.../256，K=16） |
| 输入类型 | BF16/FP16/TF32/FP8 |
| 累加器类型 | F32 |
| 执行模式 | 异步（warpgroup 内其他线程可并行执行） |

FlashMLA 使用的 WGMMA 指令：

| 用途 | 指令 | 形状 | 模式 |
|---|---|---|---|
| QK 点积 | `GMMA::MMA_64x64x16_F32BF16BF16_SS` | 64×64×16 | SS（Q 和 K 都在 smem） |
| QK 点积（Q 在寄存器） | `GMMA::MMA_64x64x16_F32BF16BF16_RS` | 64×64×16 | RS（Q 在寄存器，K 在 smem） |
| PV 乘加（P 在寄存器） | `GMMA::MMA_64x256x16_F32BF16BF16_RS` | 64×256×16 | RS（P 在寄存器，V 在 smem），MN-major |
| PV 乘加（P 在 DSM） | `GMMA::MMA_64x256x16_F32BF16BF16_SS` | 64×256×16 | SS（P 在远程 smem，V 在本地 smem），MN-major |

**SS vs RS 模式：**
- **SS**：A 和 B 矩阵都从 shared memory 加载，支持跨 CTA 的 DSM 访问
- **RS**：A 矩阵从寄存器fragment 加载，B 从 shared memory 加载，延迟更低

### 1.2 TMA（Tensor Memory Accelerator）

TMA 是 Hopper 的多维异步拷贝引擎，替代了 Ampere 时代的 `cp.async`：

| 特性 | 说明 |
|---|---|
| 拷贝粒度 | 支持 1D~5D 张量拷贝 |
| 异步性 | 完全异步，不占用寄存器，通过 transaction barrier 同步 |
| 目标地址 | Shared memory（支持 swizzle 布局） |
| 数据类型 | 自动处理多种数据类型转换 |

FlashMLA 中 TMA 的使用：
- Q 张量：从全局内存 TMA 加载到 smem
- KV 张量：通过 TMA 异步加载 K block 到 smem（双缓冲）
- O 张量：结果通过 TMA 写回全局内存

TMA 拷贝通过 `launch_tma_copy()` helper 封装，结合 `ClusterTransactionBarrier` 实现 cluster 级同步。

### 1.3 DSM（Distributed Shared Memory）

DSM 是 Hopper Thread Block Cluster 的核心特性：

- **Cluster Launch**：多个 CTA（thread block）作为一个 cluster 一起启动在同一 GPC（Graphics Processing Cluster）上
- **跨 CTA smem 访问**：CTA 可以直接读写同一 cluster 内其他 CTA 的 shared memory
- **地址映射**：通过 `get_peer_addr(p)` 计算对端 CTA 的 smem 地址，PEER_ADDR_MASK = 16MB

FlashMLA 利用 DSM 实现 GQA/MQA 的多头协作：
- 当 h_q > 64（如 h_q=128）时，CLUSTER_SIZE = h_q/64 = 2
- 两个 CTA 组成 cluster，每个处理 64 个 query 头
- PV 阶段使用 SS 模式 WGMMA，P 矩阵通过 DSM 从对端 CTA 的 smem 读取，避免重复计算

### 1.4 SM90 内核执行模型

SM90 sparse FP8 decode 内核使用 **Persistent Thread Block** 模式：

1. **线程配置**：384 线程 = 3 warpgroup × 128 线程
   - Warpgroup 0：WGMMA 计算（QK 和 PV 矩阵乘）
   - Warpgroup 1：WGMMA 计算 + 数据加载协调
   - Warpgroup 2：TMA 加载、FP8 反量化、epilogue 存储

2. **双缓冲流水线**：
   - NUM_K_BUFS=2（K 双缓冲），KV 加载和计算重叠
   - RingBufferState 管理多阶段流水线
   - S 缓冲区（attention scores）双缓冲

3. **Shared Memory 布局**：
   - Q smem 缓冲区
   - K 双缓冲（smem_sK0/smem_sK1，union 包含 K/O 和 S 共享区域）
   - S smem（attention scores）
   - Online softmax 状态（sM, sL, sScale）
   - Transaction barriers（TMA 和 DSM 同步）
   - is_kv_valid 有效性掩码

---

## 二、Blackwell (SM100) 架构特性

### 2.1 Tensor Memory (tmem)

Blackwell 引入了片上 Tensor Memory，是一种介于 register file 和 shared memory 之间的新存储层次：

| 属性 | 值 |
|---|---|
| 位置 | 每个 SM 独立 |
| 容量 | 比 shared memory 更大（具体容量未公开） |
| 用途 | 专门存储张量数据（Q、P、O 矩阵） |
| 访问方式 | UTCMMA 直接读写，UTCCP 异步拷贝 |

FlashMLA SM100 内核的 tmem 列布局：

| tmem 列范围 | 内容 | 维度 |
|---|---|---|
| 列 0 ~ 255 | 输出 O | 256 列 × 2 = 512 个 BF16 值（d_v=512） |
| 列 256 ~ 399（V32）/ 256~383（MODEL1） | 查询 Q | 144 列 / 128 列存储压缩后的 Q |
| 列 400 ~ 464 | 注意力分数 P | 64 列（支持 128 个 topk 块 = dual GEMM） |

### 2.2 UTCMMA（Tensor Memory MMA）

UTCMMA 是 Blackwell 的新一代矩阵乘指令，直接操作 tmem 中的数据：

| 指令 | 形状 | 模式 | 用途 |
|---|---|---|---|
| `SM100_MMA_F16BF16_WS_TS_NOELECT` | 64×128×K | WS-TS（warp-specialized, tmem-to-shared） | P 计算（attention scores），Dual GEMM |
| `SM100_MMA_F16BF16_WS_SS_NOELECT` | 64×256×K (MN-major) | WS-SS（shared-to-shared） | O 计算（value 乘加） |

**Dual GEMM**：UTCMMA 的 P 计算形状为 64×128（B_TOPK×2=128），一次 MMA 产生两块 P 矩阵（行 0-63 和行 64-127），经 warp 间 reduce 合并为一块，有效加倍了 P 阶段的吞吐量。

**NOELECT**：不选举 warpgroup leader，减少调度开销。

**WS（Warp-Specialized）模式**：生产-消费者 warpgroup 分工，加载 warpgroup 和计算 warpgroup 通过 barrier 同步，形成深度流水线。

### 2.3 UTCCP（Tensor Memory Copy）

UTCCP 是 tmem 的异步拷贝引擎，类似 Hopper 的 TMA 但面向 tmem：
- 在全局内存、shared memory 和 tmem 之间异步传输张量数据
- 通过 transaction barriers 同步拷贝完成
- 支持 dual GEMM 的 P 矩阵布局

### 2.4 SM100 内核优化特性

1. **Shared Memory Union 复用**：Q/O 缓冲区与 KV dequant 缓冲区通过 union 重叠，最大化 smem 利用率
2. **Dual GEMM**：单次 MMA 产生两行 P 矩阵，加倍 P 计算吞吐量
3. **V_HAVE_ROPE 区分**：V32 模式 V 完全在 NoPE 部分（V_HAVE_ROPE=false），MODEL1 模式 V 含 RoPE（V_HAVE_ROPE=true），影响数据加载和 MMA 配置
4. **Small TopK 优化**：topk ≤ 1280 时使用专门的 `fwd_for_small_topk` 内核，减少固定开销块数（3 vs 5）
5. **Head128 专用路径**：d_qk=512（MODEL1）使用专用 head128 内核；d_qk=576（V32）使用双次 head64 调用

---

## 三、SM90 vs SM100 内核对比

| 特性 | SM90 (Hopper) | SM100 (Blackwell) |
|---|---|---|
| **矩阵指令** | WGMMA (64×N×16, 128 threads) | UTCMMA (64×N×K, 支持 dual GEMM) |
| **张量存储** | Shared memory + registers | Tensor Memory (tmem) + smem + regs |
| **异步拷贝** | TMA (gm→sm) | TMA + UTCCP (gm→sm/tmem) |
| **跨 CTA 通信** | DSM (Cluster 内 smem 访问) | 不依赖 DSM，使用 tmem |
| **Cluster 大小** | NUM_M_BLOCKS (h_q/64) | 无 Cluster（tmem 替代） |
| **Q 存储** | Shared memory | Tensor Memory 列 256~ |
| **P 存储** | Shared memory (smem_sP) | Tensor Memory 列 400~464 |
| **O 存储** | Shared memory → global | Tensor Memory 列 0~255 → global |
| **线程数/CTA** | 256 (dense) / 384 (sparse) | 384 (sparse) |
| **FP8 反量化** | `cvt_fp8x8_bf16x8` (PTX) | `fp8x2_to_bf16x2_with_scale` (helper) |
| **Dense Prefill** | 不支持（仅 decode） | CUTLASS SM100 内核 |
| **Dual GEMM** | 不支持 | P 阶段 64×128 = 2×(64×64) |
| **Sparse Decode h_q=128** | Cluster (size=2) | MODEL1: 专用内核; V32: 2× head64 |
| **Warp 协作** | NamedBarriers | Slot barriers + exchange buffers |

---

## 四、SMxx 架构无关组件

SM90 和 SM100 共享两个架构无关的通用组件：

### 4.1 调度元数据生成内核

```cpp
// smxx/decode/get_decoding_sched_meta/
void run_get_decoding_sched_meta_kernel(GetDecodeSchedMetaParams &params);
```

在首次调用 decode 时运行，根据 batch 大小、序列长度、KV 长度和 SM 数量，为每个 SM part 计算需要处理的请求范围和 block 范围。

### 4.2 Combine 内核

```cpp
// smxx/decode/combine/
template<typename ElementT>
void run_flash_mla_combine_kernel(CombineParams &params);
```

SplitKV 的合并阶段，将各 split 的部分结果（m_i, l_i, o_i）合并为最终输出。两个架构使用相同的 combine 逻辑，因为 combine 阶段计算量小，不需要架构特殊优化。

---

## 五、性能优化技术总结

### 5.1 SM90 优化技术

1. **WGMMA 异步执行**：WGMMA 指令异步执行，warpgroup 内其他线程可在 MMA 等待时执行数据加载和反量化
2. **TMA 异步拷贝 + 双缓冲**：KV 数据通过 TMA 预取下一个 block，计算和加载完全重叠
3. **DSM 跨 CTA P 共享**：GQA/MQA 模式下通过 DSM 避免重复计算 P 矩阵
4. **Cluster Launch**：多头协作，减少每个 CTA 的工作量
5. **L2 预取提示**：`cp.async.cg.shared.global.L2::256B` 主动预取下一 block 到 L2
6. **L1 缓存策略**：`evict_last`/`evict_first` 控制 L1 缓存替换策略
7. **WGMMA SS/RS 模式选择**：Q 第一次计算后保存在寄存器中，后续使用 RS 模式减少 smem 读取

### 5.2 SM100 优化技术

1. **Tensor Memory 存储 Q/P/O**：tmem 提供更高带宽的张量数据访问，减少对 smem 的压力
2. **Dual GEMM**：一次 MMA 产生两行 P 矩阵，加倍 P 计算吞吐量
3. **WS（Warp-Specialized）调度**：加载和计算 warpgroup 分工，形成更深的流水线
4. **Shared Memory Union 复用**：Q/O 和 KV dequant 共享 smem 空间
5. **Small TopK 优化**：减少固定开销块数（5→3），降低小 topk 场景的 launch overhead
6. **TMA_K_STRIDE 精确配置**：V32=656, MODEL1=576 字节，TMA 步长精确匹配 KV cache 布局

---

## 六、编译配置

### 6.1 编译架构 Flags

| 架构 | NVCC Flag | 环境变量禁用 |
|---|---|---|
| SM90a (Hopper) | `-gencode arch=compute_90a,code=sm_90a` | `FLASH_MLA_DISABLE_SM90=1` |
| SM100f (Blackwell) | `-gencode arch=compute_100f,code=sm_100f` | `FLASH_MLA_DISABLE_SM100=1` |

### 6.2 编译优化 Flags

```
-O3 -DNDEBUG --use_fast_math -std=c++20
```

### 6.3 实例化矩阵

**SM90 Sparse Decode（4 个实例化）：**
- ModelType::V32 × NUM_HEADS=64 → `v32_persistent_h64.cu`
- ModelType::V32 × NUM_HEADS=128 → `v32_persistent_h128.cu`
- ModelType::MODEL1 × NUM_HEADS=64 → `model1_persistent_h64.cu`
- ModelType::MODEL1 × NUM_HEADS=128 → `model1_persistent_h128.cu`

**SM100 Sparse Decode（3 个实例化）：**
- head64 × V32 → `head64/instantiations/v32.cu`
- head64 × MODEL1 → `head64/instantiations/model1.cu`
- head128 small_topk × MODEL1（decode k512）→ `fwd_for_small_topk/head128/instantiations/phase1_decode_k512.cu`

---

## 七、相关链接

- [/deepseek/flash-mla/concepts/overview](/deepseek/flash-mla/concepts/overview) — FlashMLA 整体概述
- [/deepseek/flash-mla/concepts/splitkv](/deepseek/flash-mla/concepts/splitkv) — SplitKV 调度与执行流程
- [/deepseek/flash-mla/references/kernel-architecture](/deepseek/flash-mla/references/kernel-architecture) — 内核架构完整技术参考
- [/deepseek/deep-gemm/concepts/performance-optimization](/deepseek/deep-gemm/concepts/performance-optimization) — DeepGEMM 性能优化技术（WGMMA/TMA/PDL 等）
