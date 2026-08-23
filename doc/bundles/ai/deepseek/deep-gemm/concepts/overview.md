---
type: concept
scope: deep-gemm
name: DeepGEMM 概述
version: "2.6.1"
source: deep-gemm-spec-facts
description: DeepGEMM 高性能 GEMM 核函数库整体架构与核心概念
---

# DeepGEMM 概述

DeepGEMM 是 DeepSeek 开源的高性能通用矩阵乘法（GEMM）核函数库，专为 NVIDIA Hopper（SM90）和 Blackwell（SM100）GPU 架构深度优化，采用运行时 JIT 编译技术在调用时动态生成最优 CUDA 核函数，为大语言模型训练和推理提供极致的矩阵计算性能。

---

## 一、核心定位

DeepGEMM 的设计目标是服务于大规模 MoE（Mixture of Experts）语言模型的训练与推理，其核心特性包括：

1. **低精度矩阵乘**：原生支持 FP8（E4M3）和 FP4（E2M1）精度，配合 per-block 缩放因子实现高精度量化计算
2. **分组 GEMM**：针对 MoE 场景的 M-grouped 和 K-grouped GEMM，支持连续布局和掩码布局
3. **MegaMoE 融合核**：利用对称内存（Symmetric Memory）实现零拷贝环形通信，将 dispatch→GEMM1→SwiGLU→GEMM2→combine 融合为单内核
4. **JIT 自适应编译**：根据 GPU 架构、输入维度、数据布局动态生成最优核函数，无需预编译
5. **Hopper/Blackwell 专用优化**：充分利用 TMA 异步拷贝、WGMMA 矩阵指令、Thread Block Cluster、PDL 等新硬件特性

## 二、支持的架构

| GPU 架构 | SM 版本 | FP8 GEMM | FP4 GEMM | BF16 GEMM | MegaMoE | MQA Logits |
|---|---|---|---|---|---|---|
| Hopper (H100/H200) | SM90 | ✅ 1D1D/1D2D | ❌ | ✅ | ❌ | ✅ |
| Blackwell (B100/B200) | SM100 | ✅ 1D1D | ✅ 1D1D | ✅ | ✅ FP8/FP4/BF16 | ✅ |
| Ampere (A100) | SM80 | ❌ (legacy Triton) | ❌ | ✅ (Triton) | ❌ | ❌ |

> **注意**：SM80（A100）支持通过 `deep_gemm.legacy` 子模块提供 Triton 实现的 BF16 grouped GEMM，但性能不及 Hopper/Blackwell 的 CUDA C++ JIT 核函数。

## 三、功能模块

DeepGEMM 的功能按以下模块组织：

### 3.1 GEMM 核函数（核心）

| 类别 | SM90 实现 | SM100 实现 | 说明 |
|---|---|---|---|
| 标准 FP8 GEMM | `sm90_fp8_gemm_1d1d` / `sm90_fp8_gemm_1d2d` | `sm100_fp8_fp4_gemm_1d1d` | `[M,K]@[N,K]^T`，支持四种转置组合 |
| M-Grouped FP8 GEMM（连续） | `sm90_m_grouped_fp8_gemm_contiguous_1d2d` | `sm100_m_grouped_fp8_fp4_gemm_contiguous_1d1d` | MoE 前向，token 到 expert 的连续布局 |
| M-Grouped FP8 GEMM（掩码） | `sm90_m_grouped_fp8_gemm_masked_1d2d` | `sm100_m_grouped_fp8_fp4_gemm_masked_1d1d` | MoE 前向，expert 间 padding 掩码 |
| K-Grouped FP8 GEMM | `sm90_k_grouped_fp8_gemm_1d1d` | `sm100_k_grouped_fp8_gemm_1d1d` | MoE 反向，连续 K 分组 |
| 标准 BF16 GEMM | `sm90_bf16_gemm` | `sm100_bf16_gemm` | BF16 精度，支持 cuBLASLt 回退 |
| M-Grouped BF16 GEMM | `sm90_m_grouped_bf16_gemm_contiguous` / `sm90_bf16_m_grouped_gemm_masked` | `sm100_m_grouped_bf16_gemm_contiguous` / `sm100_m_grouped_bf16_gemm_masked` | BF16 分组 GEMM |
| K-Grouped BF16 GEMM | `sm90_bf16_k_grouped_gemm` | `sm100_bf16_k_grouped_gemm` | BF16 K 分组 GEMM |

### 3.2 Attention 核函数

- **FP8 GEMM + Head Split**（`fp8_gemm_nt_skip_head_mid`）：QKV 投影融合，跳过中间 head 维度
- **MQA Logits**（`fp8_fp4_mqa_logits`）：多查询注意力 logits 计算，支持 FP8/FP4
- **Paged MQA Logits**（`fp8_fp4_paged_mqa_logits`）：分页 KV cache 的注意力 logits

### 3.3 Einsum 核函数

- `"bmk,bnk->mn"`：批量归约 GEMM
- `"bhr,hdr->bhd"` / `"bhd,hdr->bhr"`：注意力投影/反向投影
- `"bhd,bhr->hdr"`：权重梯度（仅 SM100 FP8）

### 3.4 Hyperconnection 核函数

- `tf32_hc_prenorm_gemm`：TF32 精度的超连接前置归一化 GEMM

### 3.5 MegaMoE 核函数

- `fp8_fp4_mega_moe`：FP8/FP4 精度的融合 MoE 前向（仅 SM100）
- `bf16_mega_moe`：BF16 精度的融合 MoE 前向（仅 SM100）

### 3.6 Layout 工具

- 缩放因子布局转换（TMA 对齐、MN-major、UE8M0 打包）
- TMA 对齐尺寸计算

## 四、Python 包结构

```
deep_gemm/
├── __init__.py          # 包入口，导出所有公共 API，初始化 C++ 模块
├── _C.so                # C++ 扩展模块（pybind11 绑定）
├── mega/
│   └── __init__.py      # MegaMoE Python 层（SymmBuffer、权重变换）
├── testing/
│   ├── __init__.py      # 测试工具导出
│   ├── bench.py         # 性能基准测试（CUDA Event、L2 flush、Kineto）
│   ├── numeric.py       # 数值验证（余弦距离、逐 bit 比较）
│   └── utils.py         # 测试工具函数
├── utils/
│   ├── __init__.py      # 工具导出
│   ├── dist.py          # 分布式工具（init_dist、uneven_all_gather）
│   ├── layout.py        # Layout 工具（TMA 对齐、MK 对齐配置）
│   └── math.py          # 数学工具（FP8/FP4 量化/反量化、对齐函数）
├── legacy/              # A100 Triton 核函数（向后兼容）
│   ├── __init__.py
│   ├── m_grouped_gemm.py
│   ├── a_fused_m_grouped_gemm.py
│   ├── a_fused_k_grouped_gemm.py
│   ├── b_fused_k_grouped_gemm.py
│   └── tune_options.py
└── include/
    └── deep_gemm/       # JIT 编译用 CUDA C++ 头文件
        ├── common/      # 类型定义、编译配置、TMA copy、数学工具
        ├── comm/        # 通信屏障
        ├── epilogue/    # 输出 epilogue（存储 CD、transform）
        ├── impls/       # 各架构核函数实现
        ├── layout/      # MegaMoE/MQA 布局定义
        ├── mma/         # WGMMA MMA 指令封装（SM90/SM100）
        ├── ptx/         # PTX 内联汇编（LD/ST、TCGen05、TMA、WGMMA）
        └── scheduler/   # 核函数调度器（GEMM/MegaMoE/MQA/Paged MQA）
```

## 五、C++ 源码结构

```
csrc/
├── python_api.cpp       # pybind11 模块入口，注册所有 API
├── apis/                # Python 绑定 API 层
│   ├── gemm.hpp         # GEMM 核函数入口（架构分发、参数校验）
│   ├── attention.hpp    # Attention 核函数入口
│   ├── einsum.hpp       # Einsum 核函数入口
│   ├── hyperconnection.hpp  # Hyperconnection 入口
│   ├── layout.hpp       # Layout 工具入口
│   ├── mega.hpp         # MegaMoE 核函数入口
│   └── runtime.hpp      # 运行时配置入口
├── jit/                 # JIT 编译系统
│   ├── compiler.hpp     # 编译器（NVCC/NVRTC）
│   ├── device_runtime.hpp   # 设备运行时（SM/TC/PDL 配置、cuBLASLt）
│   ├── kernel_runtime.hpp   # 内核运行时（加载、启动、CRTP 模式）
│   ├── include_parser.hpp  # Include 依赖解析（hash 计算）
│   ├── cache.hpp        # 内核运行时缓存
│   └── handle.hpp       # CUDA Driver/Runtime API 句柄管理
├── jit_kernels/
│   ├── impls/           # JIT 核函数实现（各架构具体实现）
│   └── heuristics/      # 启发式配置（block 大小、MegaMoE 配置）
├── utils/               # 工具函数（布局检查、兼容性宏、哈希、异常）
└── indexing/            # 索引工具
```

## 六、版本信息

- **当前版本**：2.6.1
- **CUDA 要求**：CUDA ≥ 12.1（TMA 支持），推荐 ≥ 12.3
- **PyTorch 要求**：PyTorch ≥ 2.1（FP8 支持）
- **Python**：通过 pip 安装，`setup.py` 构建 C++ 扩展

## 七、相关链接

- [/deepseek/deep-gemm/concepts/fp8-gemm](/ai/deepseek/deep-gemm/concepts/fp8-gemm) — FP8/FP4 GEMM 精度方案
- [/deepseek/deep-gemm/concepts/grouped-gemm](/ai/deepseek/deep-gemm/concepts/grouped-gemm) — 分组 GEMM 与 MoE 并行
- [/deepseek/deep-gemm/concepts/jit-kernel-compilation](/ai/deepseek/deep-gemm/concepts/jit-kernel-compilation) — JIT 内核编译系统
- [/deepseek/deep-gemm/concepts/moe-operations](/ai/deepseek/deep-gemm/concepts/moe-operations) — MegaMoE 融合运算
- [/deepseek/deep-gemm/concepts/performance-optimization](/ai/deepseek/deep-gemm/concepts/performance-optimization) — 性能优化技术
- [/deepseek/deep-ep/](/ai/deepseek/deep-ep/) — DeepEP 专家并行通信库
- [/deepseek/tile-kernels/](/ai/deepseek/tile-kernels/) — TileLang 核函数库
