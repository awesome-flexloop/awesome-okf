---
type: spec-insights
scope: deep-gemm
source: deep-gemm-spec-facts
---

# DeepGEMM 核心洞察

## 一、架构定位

DeepGEMM（v2.6.1）是 DeepSeek 开源的高性能 GEMM 核函数库，专为 Hopper（SM90）和 Blackwell（SM100）GPU 架构设计，采用 JIT（Just-In-Time）编译技术在运行时生成最优 CUDA 核函数。其核心定位是为大语言模型（LLM）训练与推理中的矩阵乘法提供极致性能，特别是 MoE（Mixture of Experts）场景下的分组 GEMM 运算。

## 二、核函数分类体系

### 2.1 按数据类型分

- **FP8/FP4 GEMM**：SM90 支持 FP8（E4M3），SM100 额外支持 FP4（E2M1，packed 为 Int8）
- **BF16 GEMM**：全架构支持的半精度 GEMM
- **TF32 GEMM**：仅用于 Hyperconnection prenorm 场景
- **cuBLASLt 回退**：所有架构均可用的兜底路径

### 2.2 按 GEMM 模式分（GemmType 枚举）

| GemmType | 说明 | 典型场景 |
|---|---|---|
| Normal | 标准矩阵乘 | 普通前向/反向传播 |
| MGroupedContiguous | M 维度分组，连续布局 | MoE 前向（连续 expert 布局） |
| MGroupedMasked | M 维度分组，带掩码 | MoE 前向（expert 间 padding） |
| KGroupedContiguous | K 维度分组，连续布局 | MoE 反向传播 |
| Batched | 批量 GEMM | 多头注意力 |
| MGroupedContiguousWithPsumLayout | M 分组 + PSUM 布局 | 分布式并行 partial sum |
| KGroupedContiguousWithPsumLayout | K 分组 + PSUM 布局 | 分布式反向 partial sum |

### 2.3 按缩放因子（SF）布局分（KernelType）

- **Kernel1D1D**：A/B 缩放因子均为 per-1xK 粒度（gran_mn=1），SM100 新格式（SF 为 Int 类型，UE8M0 packed）
- **Kernel1D2D**：A 为 per-1xK，B 为 per-128x128 粒度（SM90 格式，SF 为 Float 类型）
- **KernelNoSF**：无缩放因子（BF16 核函数）

## 三、JIT 编译系统关键洞察

1. **双编译器支持**：NVCC（离线编译 cubin）和 NVRTC（运行时编译），通过 `DG_JIT_USE_NVRTC` 环境变量切换，默认 NVCC
2. **分层缓存**：内存中的 `KernelRuntimeCache` + 磁盘缓存（`~/.deep_gemm/cache/`），基于 include hash + compiler signature + flags + code 的签名机制
3. **Include 解析**：递归解析 `<deep_gemm/*>` 头文件依赖，计算 include hash 以实现精确缓存失效
4. **原子写入**：编译到临时目录后 fsync + rename，保证多进程安全
5. **NVRTC PCH 支持**：NVRTC ≥ 12.8 时启用预编译头加速
6. **架构自适应编译**：编译目标架构通过 `device_runtime->get_arch()` 获取，SM100 区分 "100a"（Blackwell 标准版）和 "100f"（未来版本）

## 四、FP8/FP4 量化方案

1. **Per-block 缩放因子**：FP8 使用 per-block（M×K 网格）缩放因子，SM90 下 A 侧为 1×128 粒度，B 侧为 128×128 粒度；SM100 下统一为 1×K 粒度
2. **UE8M0 编码**：SM100 使用 UE8M0（无符号 8-bit 指数-only）格式表示缩放因子，4 个 scale 打包为 1 个 int32，减少内存带宽
3. **缩放因子布局转换**：`layout::transform_sf_into_required_layout()` 根据架构和 recipe 自动转换 SF 布局（TMA 对齐、MN-major、UE8M0 打包等）
4. **FP4 支持**：SM100 独有，使用 E2M1 码点（{0, 0.5, 1, 1.5, 2, 3, 4, 6}），每 2 个 E2M1 码打包为 1 byte（nibble packing）

## 五、MegaMoE 关键设计

1. **对称缓冲区（Symmetric Buffer）**：利用 PyTorch `symmetric_memory` 实现跨 rank 的零拷贝环形通信缓冲区，消除 MoE 层 all-to-all 的显式通信
2. **融合前向/反向**：将 dispatch → GEMM1 → activation → GEMM2 → combine 融合为单个核函数，减少中间结果写回
3. **双权重精度**：路由专家权重使用 FP4（极致压缩），共享专家权重使用 FP8（保持精度）
4. **SwiGLU 激活融合**：L1 权重将 gate/up 沿 N 维度交错排列（gran=8），匹配 SwiGLU 的计算模式
5. **Ring buffer 容量**：基于候选 block_m（8/16/32/64/96/128/192）的最坏情况 live pool 大小计算，对齐到 LCM(384)
6. **仅支持 SM100**：MegaMoE 核函数目前仅 Blackwell 架构可用

## 六、性能优化关键技术

1. **TMA（Tensor Memory Accelerator）**：Hopper/Blackwell 专用异步拷贝引擎，要求数据 TMA 对齐（128 字节）
2. **WGMMA（Warp Group Matrix Multiply-Accumulate）**：Hopper 引入的 warp-group 级矩阵乘指令，SM100 支持 FP8/FP4 MMA
3. **PDL（Programmatic Dependent Launch）**：SM90/SM100 的核函数间依赖控制机制，减少 launch overhead
4. **SM 数量动态配置**：`set_num_sms()` 可限制使用的 SM 数量，配合 MPS 实现多实例公平共享
5. **Tensor Core 利用率控制**：`set_tc_util()` 控制 TC 利用率（默认 100%）
6. **Cluster Launch**：SM90+ 支持 thread block cluster 启动，MegaMoE 使用 cluster_size=2
7. **Swizzle 模式**：权重和激活数据采用 swizzle 布局以优化 TMA 加载效率和 bank conflict

## 七、Python 工具链

1. **量化工具**（`deep_gemm/utils/math.py`）：提供 per_token/per_channel/per_block FP8/FP4 量化/反量化
2. **测试工具**（`deep_gemm/testing/`）：bench 计时（CUDA Event + L2 flush）、numeric 精度验证（余弦距离 + 逐 bit 比较）
3. **分布式工具**（`deep_gemm/utils/dist.py`）：init_dist 初始化、uneven_all_gather 不等长 all-gather
4. **Mega 工具**（`deep_gemm/mega/`）：SymmBuffer 管理、权重变换（interleave + SF transpose）
5. **Layout 工具**（`deep_gemm/utils/layout.py`）：TMA 对齐尺寸计算、MK 对齐配置
6. **Legacy 支持**（`deep_gemm/legacy/`）：A100 的 Triton 核函数，9 个 autotune 配置

## 八、与 DeepEP/TileLang 的关系

- **DeepEP**（[/deepseek/deep-ep/](../../deep-ep/index.md)）：DeepSeek 的专家并行通信库，提供 EP（Expert Parallelism）的 all-to-all 通信原语，与 DeepGEMM 的 MegaMoE 协同使用——DeepEP 负责通信，DeepGEMM 负责计算
- **TileLang**（[/deepseek/tile-kernels/](../../tile-kernels/index.md)）：TileLang 编写的核函数库，`third-party/tilelang_ops/` 包含 SwiGLU+weight 到 FP8 的融合算子，作为 DeepGEMM 核函数的补充
