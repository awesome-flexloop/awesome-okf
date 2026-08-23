---
type: spec-insights
scope: flash-mla
source: flash-mla-spec-facts
---

# FlashMLA 核心洞察

## 一、架构定位

FlashMLA（v1.0.0）是 DeepSeek 开源的高性能 MLA（Multi-head Latent Attention）注意力核函数库，专为 NVIDIA Hopper（SM90）和 Blackwell（SM100）GPU 架构深度优化。其核心定位是为 DeepSeek-V3/V3.1/V3.2/R1 模型的推理阶段提供高效的 MLA 解码（decoding）和预填充（prefill）注意力计算，特别是长上下文场景下的 SplitKV 分页注意力与 FP8 量化 KV cache 计算。

## 二、核函数分类体系

### 2.1 按计算阶段分

| 阶段 | 核函数 | 架构支持 | KV Cache 格式 | MLA 模式 |
|---|---|---|---|---|
| Dense Decoding | `dense_decode_fwd` | SM90 | BF16/FP16 | MQA |
| Sparse Decoding | `sparse_decode_fwd` | SM90 & SM100 | FP8 | MQA |
| Dense Prefill | `dense_prefill_fwd/bwd` | SM100 | —（输入 K/V） | MHA |
| Sparse Prefill | `sparse_prefill_fwd` | SM90 & SM100 | —（输入 K/V） | MQA |

### 2.2 按注意力模式分

- **Dense Attention**：全注意力，所有历史 token 参与计算，使用 paged KV cache + block_table 索引
- **Sparse Attention（DSA）**：Token 级稀疏注意力，仅计算 indices 指定的 top-k token，KV cache 使用 FP8 压缩格式
- **Sparse Prefill**：预填充阶段的稀疏注意力，输入为 3D 张量（无 batch 维度，需手动模拟 batch）

### 2.3 按 GPU 架构分

| 架构 | 关键硬件特性 | FlashMLA 利用方式 |
|---|---|---|
| SM90 (Hopper) | WGMMA、TMA、DSM（Distributed Shared Memory）、Thread Block Cluster | WGMMA 64x64x16/64x256x16 MMA、TMA 异步拷贝 Q/K、Cluster 多头协作（CLUSTER_SIZE=NUM_M_BLOCKS）、DSM 跨 cluster P 矩阵传输 |
| SM100 (Blackwell) | Tensor Memory（tmem）、UTCMMA、UTCCP（Tensor Memory copy） | tmem 存储 Q/P/O（列 0~255=O、256~=Q、400~464=P）、UTCMMA 矩阵指令、UTCCP 异步拷贝、Dual GEMM |

## 三、MLA 低秩 KV 压缩关键设计

### 3.1 MLA 核心思想

MLA 通过低秩压缩将 KV cache 维度从标准 MHA 的 `num_heads × head_dim` 压缩为单个潜在向量（latent vector），大幅减少 KV cache 内存占用：
- K 和 V 共享一个 `d=576`（V32 模式）或 `d=512`（MODEL1 模式）的压缩表示
- 其中 NoPE 部分（不参与旋转位置编码的维度）分别为 512/448 维，RoPE 部分为 64 维
- 查询头数 h_q 可以是 64 或 128，KV 头数 h_kv=1（MQA 模式）

### 3.2 两种模型模式

| 模式 | head_dim (d_qk) | head_dim_v (d_v) | d_noPE | d_RoPE | FP8 bytes/token | 适用模型 |
|---|---|---|---|---|---|---|
| V32 | 576 | 512 | 512 (FP8) | 64 (BF16) | 656 | DeepSeek-V3/V3.1/V3.2 |
| MODEL1 | 512 | 512 | 448 (FP8) | 64 (BF16) | 576 | DeepSeek 新配置模型 |

V32 模式下每个 token 的 KV cache 布局：
- 前 512 字节：NoPE 部分，512 个 `float8_e4m3` 值
- 接下来 16 字节：4 个 `float32` 缩放因子（每 128 个 FP8 值一个 scale）
- 最后 128 字节：RoPE 部分，64 个 `bfloat16` 值（不量化，保持精度）

MODEL1 模式下量化 tile 大小为 64（V32 为 128），因此有 7 个 scale + 1 个 padding 共 8 个 float32（32 字节），加上 448 字节 FP8 NoPE + 128 字节 BF16 RoPE = 576 字节/token。

## 四、SplitKV 长序列注意力技术

### 4.1 SplitKV 核心思想

SplitKV 将长序列的 KV cache 沿序列维度切分为多个 split，每个 split 由不同的 SM（Streaming Multiprocessor）并行处理，最终通过 online softmax 的 log-sum-exp 进行合并（combine）。这是 FlashMLA 实现长上下文（32K+）高效解码的关键技术。

### 4.2 调度机制

- **Tile Scheduler**：首次调用时生成 `tile_scheduler_metadata`（形状 `(num_sm_parts, DecodingSchedMetaSize/4)`，int32），记录每个 SM 部分处理的请求范围、block 范围和 split 索引
- **num_splits**：形状 `(b+1)` 的 int32 张量，记录每个 batch 的 split 数量
- **num_sm_parts 计算**：根据 GPU SM 数量、序列长度、头数动态计算（SM90 dense: `max(arch.num_sms / h_k / ceil_div(s_q*h_q/h_k, 64), 1)`；SM90 sparse: `max(arch.num_sms / s_q / (h_q/64), 1)`）
- **固定开销块数**：`fixed_overhead_num_blocks = 5`（dense 和 SM90/SM100 head64 sparse）或 3（SM100 head128 sparse）
- **block_size_n = 64**：KV 维度的 tile 大小

### 4.3 两阶段执行

1. **分块计算阶段**：多个 CTA 并行处理 KV 序列的不同 split，每个 CTA 维护独立的 online softmax 状态（max、sum）和部分输出，结果写入全局内存的 accumulator 缓冲区
2. **Combine 阶段**：架构无关的 `run_flash_mla_combine_kernel` 将各 split 的部分结果合并为最终输出，通过 `tile_scheduler_metadata` 确定合并方式

## 五、Paged KV Cache 机制

- **页块大小**：`page_block_size = 64`（硬编码，当前不支持其他大小）
- **block_table**：形状 `(batch_size, max_num_blocks_per_seq)`，int32，映射逻辑 block → 物理 block
- **cache_seqlens**：形状 `(batch_size)`，int32，每个序列的实际 KV 长度
- **稀疏注意力**：不使用 block_table，indices 直接编码物理位置 `(block_idx * page_block_size + offset_in_block)`

## 六、SM90 Hopper 内核架构关键洞察

### 6.1 Dense Decode（BF16）

- **WGMMA 配置**：QK 使用 `MMA_64x64x16_F32BF16BF16_SS/RS`，PV 使用 `MMA_64x256x16_F32BF16BF16_RS/SS`（MN-major）
- **BLOCK_SIZE_M = 64**，NUM_THREADS = 256，PAGE_BLOCK_SIZE = 64
- **双缓冲 K**：使用 `smem_sK0/smem_sK1` 双缓冲隐藏 K 加载延迟
- **TMA 异步拷贝**：通过 `launch_tma_copy` 封装 TMA + ClusterTransactionBarrier 实现 Q/K/O 的异步传输
- **DSM 跨 Cluster 通信**：通过 `get_peer_addr` 计算跨 cluster 地址，实现 P 矩阵的 SS（shared memory to shared memory）模式 WGMMA

### 6.2 Sparse FP8 Decode

- **模板参数**：`ModelType`（V32/MODEL1）× `NUM_HEADS`（64/128）共 4 个实例化
- **Cluster Launch**：`CLUSTER_SIZE = NUM_M_BLOCKS = NUM_HEADS/64`，h_q=128 时 cluster_size=2，两个 CTA 协作处理 128 头
- **反量化**：`cvt_fp8x8_bf16x8` 将 8 个 FP8 E4M3 转为 BF16 并乘以 scale，使用 PTX `ld.global.nc` 带 L1/L2 缓存提示
- **双缓冲 + Ring Buffer**：K 缓冲区 NUM_K_BUFS=2，S 缓冲区双缓冲，通过 `RingBufferState` 管理多阶段流水线
- **Warp 协作**：384 线程 = 128×3，分为 3 个 warpgroup 分别负责 QK MMA、PV MMA、数据加载

## 七、SM100 Blackwell 内核架构关键洞察

### 7.1 Sparse Decode Head64

- **Tensor Memory 列布局**：列 0~255=O（512 维 V，BF16），列 256~=Q，列 400~464=P（attention scores）
- **Dual GEMM**：`TiledMMA_P` 形状 64×128（B_TOPK×2），一次 MMA 产生两块 P 矩阵（行 0-63 和 64-127），经 warp reduce 合并
- **MMA 指令**：`SM100_MMA_F16BF16_WS_TS_NOELECT`（P 计算）和 `SM100_MMA_F16BF16_WS_SS_NOELECT`（O 计算），使用 WS（warp-specialized）模式
- **Shared Memory Union 复用**：Q/O 与 KV dequant 缓冲区通过 union 重叠，最大化 smem 利用率
- **TMA_K_STRIDE**：V32=656 字节，MODEL1=576 字节，对应每个 token 的 KV cache 步长
- **V_HAVE_ROPE**：V32 模式 V 不含 RoPE（V 完全在 NoPE 部分），MODEL1 模式 V 含 RoPE（需要额外加载 RoPE 部分计算 V）

### 7.2 Sparse Decode Head128

- **两种路径**：
  1. d_qk=512（MODEL1）：使用 `fwd_for_small_topk/head128` 的专门 decode 内核（`phase1_decode_k512.cu`）
  2. d_qk=576（V32）：通过调用两次 head64 内核模拟（`Decode_Sm100_Head64x2_Impl`）
- **small_topk 优化**：当 topk ≤ 1280 时使用专门的小 topk 内核

### 7.3 Dense Prefill/Backward（CUTLASS）

- 基于 NVIDIA CUTLASS 库实现，为标准 MHA（非 MLA 压缩）模式
- 支持 varlen 变长序列输入（通过 cu_seqlens 累积序列长度）
- FWD 使用 TMA warpspecialized 流水线，BWD 不支持 GQA（num_qo_heads ≠ num_kv_heads 时报错）
- MLA 专用 mainloop：`sm100_fmha_mla_fwd_mainloop_tma_warpspecialized.hpp` 和 `sm100_fmha_mla_load_tma_warpspecialized.hpp`

## 八、Python API 设计关键洞察

1. **延迟初始化**：`get_mla_metadata()` 返回空的 `FlashMLASchedMeta`，实际调度元数据在首次调用 `flash_mla_with_kvcache` 时生成，后续调用检查参数一致性
2. **路由分发**：`flash_mla_with_kvcache` 内部根据 `indices` 是否存在自动路由到 sparse/dense decode
3. **autograd 集成**：`flash_attn_varlen_func` 通过自定义 `torch.autograd.Function`（`FlashAttnVarlenFunc`）实现前向/反向传播
4. **API 兼容性**：保留旧接口参数（如 `num_splits`、`get_mla_metadata` 的旧参数），实际使用新的延迟初始化机制
5. **Sparse Prefill 无 batch 维度**：`flash_mla_sparse_fwd` 输入为 3D 张量 `[s_q, h_q, d_qk]`，多 batch 需手动 reshape

## 九、编译与依赖

- **C++ 标准**：C++20，`-O3`/`-DNDEBUG`/`--use_fast_math`
- **架构 flags**：SM90a（`compute_90a,sm_90a`）和 SM100f（`compute_100f,sm_100f`）
- **环境变量**：`FLASH_MLA_DISABLE_SM90=1`/`FLASH_MLA_DISABLE_SM100=1` 禁用对应架构编译，`FLASH_MLA_DISABLE_FP16` 禁用 FP16 dense decode
- **NVCC 版本**：SM100 编译需要 NVCC ≥ 12.9
- **依赖**：CUTLASS（git submodule）、kerutils（头文件库）
- **扩展模块名**：`flash_mla.cuda`（pybind11 绑定）

## 十、性能指标

| 内核 | GPU | 性能 |
|---|---|---|
| Dense MLA Decoding | H800 SXM5 | 最高 3000 GB/s（内存受限）/ 660 TFLOPS（计算受限） |
| Sparse MLA Decoding（FP8） | H800 SXM5 | 410 TFLOPS（计算受限） |
| Sparse MLA Decoding（FP8） | B200 | 350 TFLOPS（未充分优化） |
| Sparse MLA Prefill | H800 SXM5 | 640 TFLOPS |
| Sparse MLA Prefill | B200 | 1450 TFLOPS |
| Dense MHA Prefill FWD | B200 | 1460 TFLOPS |
| Dense MHA Prefill BWD | B200 | 1000 TFLOPS |

## 十一、与 DeepGEMM/TileLang 的关系

- **DeepGEMM**（[/deepseek/deep-gemm/](/ai/deepseek/deep-gemm/)）：DeepSeek 的高性能 GEMM 核函数库，使用 JIT 编译，提供通用矩阵乘法能力；FlashMLA 专注于注意力核函数，两者在推理 pipeline 中各司其职——FlashMLA 负责注意力计算，DeepGEMM 负责 MLP/MoE 的线性层计算
- **TileLang**（[/deepseek/tile-kernels/](/ai/deepseek/tile-kernels/)）：TileLang 编写的核函数库，可作为 CUDA C++ 核函数的补充，提供更高抽象层级的核函数开发方式；FlashMLA 使用纯 CUDA C++ 手写核函数以达到极致性能
