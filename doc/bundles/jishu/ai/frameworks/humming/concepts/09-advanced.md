---
type: Concept
title: "进阶主题：未文档化格式、路线图与社区视角"
description: "Humming 的进阶议题——未文档化浮点格式（float8e3m4/float4e0m3）的 CUBIN 补丁与架构白名单机制、官方路线图三方向、社区与作者视角的演进脉络"
tags: [humming, advanced, undocumented-dtypes, cubin-patch, roadmap, community, 进阶]
generated: { by: seven-concepts-cmd+source-code-to-okf-wiki/E, at: "2026-10-22T23:40:00+08:00" }
status: stable
stale_after: 2027-04-22
sources:
  - id: local-source
    resource: /references/facts.md
    title: 本地源码检出事实清单
  - id: blog
    url: https://vllm.ai/blog/2026-10-21-humming
    title: Announcing Humming（2026-10-21）— Future Plans 节
  - id: zhihu-author
    url: https://zhuanlan.zhihu.com/p/2021951434141222000
---

# 进阶主题：未文档化格式、路线图与社区视角

> 进阶层。本文覆盖三块内容：**官方 README 未写但源码存在的格式**、**已公布的路线图**、**社区与作者视角**。

## 一、未文档化浮点格式

### 是什么

源码中存在两组官方 README **未列出**的浮点格式（F-027，`humming/config/mma.py:43-47`）：

```python
UNDOCUMENTED_FP_DTYPES = [...]        # float8e3m4, float4e0m3
UNDOCUMENTED_FP_SM_VERSIONS = [...]    # SM100, SM103, SM120, SM121
```

| 格式 | 位宽 | 指数位 | 尾数位 |
|------|------|--------|--------|
| `float8e3m4` | 8 | 3 | 4 |
| `float4e0m3` | 4 | 0 | 3 |

**`float4e0m3` 的指数位为 0**——这正是「指数位为 0 的浮点」家族的一员（见 [02 量化模型](02-quantization-model.md) 中整数自动转换的讨论，F-025、F-026）。它的数值范围与同位宽对称整数相同。

### 为什么叫「未文档化」

这些格式在源码中可用，但**官方 README 的支持矩阵里没有列**。两个原因叠加：

1. 它们依赖 **CUBIN 补丁**（`patch_cubin.cpp`）——需要修改生成的二进制，常规编译流程不产生。
2. 它们只在**特定架构**上被验证过。

### 启用条件（双条件，F-028）

```python
def supports_undocumented_fp_dtypes(...):
    return is_cubin_patch_enabled() and sm_version in UNDOCUMENTED_FP_SM_VERSIONS
```

**必须同时满足**：

| 条件 | 说明 |
|------|------|
| ① CUBIN 补丁已启用 | `is_cubin_patch_enabled()` |
| ② 架构在白名单内 | SM100 / SM103 / SM120 / SM121 |

### ⚠️ 硬警告

源码注释明确写道（F-029）：

> 新增架构必须在**真机测试后**才可加入白名单——**SM107 执行这两种编码会抛 illegal instruction**。

「illegal instruction」是 CUDA 层面的硬错误，不是 Python 异常，**无法被 try/except 捕获**。在不支持的架构上启用会导致进程直接崩溃。

**实践建议**：

- 生产环境**不要**依赖未文档化格式——它随时可能变更或移除。
- 若必须使用：先确认 `torch.cuda.get_device_capability()` 落在白名单内，且 CUBIN 补丁链路完整可用。
- **以真机执行为准**，不要只依据 README 或本文档。

### 已知边界（官方博客明确的三条）

| 边界 | 说明 | 出处 |
|------|------|------|
| **SM103（B300）的 UMMA 不支持 INT8** | 博客原文：「UMMA instructions on the B300 (SM103) no longer support INT8 computation, but earlier MMA instructions can still execute INT8 GEMM, with substantially lower performance.」——即**能力面在同代架构内也会分化** | F-102 |
| **Rubin 不支持这两种隐藏格式** | 博客原文：「Rubin does not support these two hidden Tensor Core formats, so support for these native compute paths does not extend to Rubin.」——**未来架构的支持面是收缩的** | F-103 |
| **T-Head 玄武 810E 已完整支持** | 博客原文：「Humming already fully supports T-Head's Zhenwu 810E」——CUDA 兼容设备的支持面是**扩展的** | F-104 |

**这三条合起来说明**：未文档化格式的支持面**随架构演进而变动**，不是「Blackwell 之后一直有」。规划换卡周期时必须考虑这一点。

### CUBIN 补丁的开关

源码默认启用 CUBIN 补丁（`postprocess_cubin` 非空时生效，F-043）。该补丁是未文档化浮点格式可用的前提（F-028）。可用环境变量 `HUMMING_DISABLE_PATCH_CUBIN=1` 关闭。

**关于缓存**：`patch_cubin.cpp` 的内容哈希**总是**进入编译签名（判据是 `postprocess_cubin` 参数非 None，与补丁开关无关，F-043）——因此补丁内容变更会**自动**使缓存失效，升级后无需手动清理 `~/.humming/cache/`。

## 二、路线图

官方博客「Future Plans」节列出三个方向（F-090）：

### ① 扩大设备支持

- **Rubin 架构特性**：包含 Locality Domains
- **更多 T-Head PPU 设备**：如 Zhenwu M890
- **更多 CUDA 兼容设备**

> 源码侧已有 PPU 基础设施：`PPUSm80Heuristics` 与 PPU 强制 NVCC 分支（F-041、F-056）。但官方博客未展开 PPU 硬件细节，本包只登记机制存在，不做性能或兼容性承诺。

### ② 引入 autotune

**当前状态**：靠针对性调优，**尚未有自动搜索**（F-090）。

官方预期是**与现有启发式互补**，而非替代——启发式提供架构级先验知识，autotune 在其基础上做局部搜索。

（本包对此的观察，见 [05 调优与启发式](05-tuning.md) 开头：JIT 编译时间与搜索空间存在天然张力，这是启发式路线的合理性来源。）

### ③ 深化与推理框架的集成

范围（F-090）：

- 量化模型加载
- 后端选择
- 并行推理
- 运行时调度
- 设备适配

**具体目标之一**：让 **EP 下的量化 All-to-All 通信可用**。

> EP（Expert Parallel）下，MoE 专家分布在不同设备间，token 需要 All-to-All 交换。当前这条路径的量化支持是**规划目标而非现状**——引用时勿表述为已有能力。

## 三、社区与作者视角

### 项目缘起

作者自述（F-091）：2025 年主要在做 vLLM 仓库 **Marlin 算子**的开发与优化，为 Marlin 增加 MoE 支持与更多量化类型（FP8、MXFP4、NVFP4）及更多激活类型（FP8、INT8）。

**判断的问题**（作者原文观点）：

1. **位宽覆盖不足**——通用 Marlin 只支持 4 位或 8 位，其他位数难加。
2. **性能不足**——不少算子性能不佳；Marlin 在大 batch 下表现差，从 Hopper 起必须用架构专属指令才能发挥硬件性能。

这两个判断直接对应 Humming 的两项设计：**任意 ≤8 bit**（F-010、F-070）与 **JIT + 架构专属流水线**（F-051）。

### 集成路径

作者自述 vLLM 集成 PR 为 **#34556**（已合并），并给出早期仓库地址 `github.com/inclusionAI/humming`——后迁至 `vllm-project/humming`（F-092）。**仓库迁移已发生**，当前地址为准（F-002）。

### 早期支持范围（时点早于本包快照）

作者自述（F-093）：

| 维度 | 当时范围 |
|------|---------|
| 激活类型 | FP16 / BF16 / FP8 / INT8 / INT4 |
| 权重类型 | 1–8 位全部整数与浮点类型 |
| 量化方法 | groupwise / blockwise / channelwise / tensorwise |
| scale 类型 | FP16 / BF16 / E4M3 / E5M2 / E8M0 |
| 架构 | 「已支持 SM75–SM90 高级特性，SM100/SM120 特性未来支持」 |

**⚠️ 时点差异**：作者写作时称 SM100/SM120 支持是「未来」，而本包源码快照（2026-10-21）**已含** SM100/SM120/SM121 启发式文件与 UMMA 流水线（F-051、F-056）。

**以源码快照为准**，作者自述仅作演进脉络参考。这正是自述材料与一手代码需要交叉核验的典型场景。

### 编译与体积自述

作者自述（F-094）：

| 项 | 说法 | 与官方对照 |
|----|------|-----------|
| 单算子编译时间 | 约 1–2 秒（与算子复杂度相关，与 CPU 性能强相关） | ✅ 与官方 1.82/1.88s 互证（F-080） |
| 依赖 | 仅需 torch 和 nvcc | ⚠️ README 为简化表述，`pyproject.toml` 实为 8 项（差异 #5） |
| wheel 体积 | 100+KB | ⚠️ 与博客的 500KB 有差异（差异 #2，未实测裁决） |

## 四、与相邻方案的关系（并行竞合，不是取代）

初学者常把 Humming 读成「要取代 CUTLASS / DeepGEMM / Marlin」，这是误读。官方博客的立场是**并行竞合**，且各方案的差异化维度不同：

| 方案 | 定位 | 编译方式 | 覆盖范围 |
|------|------|---------|---------|
| **Humming** | JIT 化的量化 GEMM 引擎 | **JIT 运行时编译**（1.82s/kernel） | 量化形态最全（任意 ≤8 bit + 六种 scale 粒度），SM75–SM121 |
| **CUTLASS** | 模板化高性能后端 | AOT 模板实例化（23.35s） | 通用 GEMM 形态全，算力上界参考 |
| **DeepGEMM** | Blackwell 上的专用 GEMM 库 | AOT 预编译 | 聚焦 Hopper/Blackwell 的 FP8/MX 路径 |
| **Marlin / FlashInfer** | vLLM 侧的低比特推理路径 | AOT 预编译 | 4/8bit 为主，与 vLLM 深度耦合 |
| **cuBLAS** | NVIDIA 官方数学库 | AOT | 浮点 GEMM 上界，博客的共同基线之一 |

**Humming 的差异化维度是「编译效率 + 量化覆盖度」，而非「所有场景下算力超越 CUTLASS/DeepGEMM」**（F-080 的编译耗时对比正是这个维度的直接体现）。

同时注意：官方博客明确 **FlashInfer CUTLASS W4A8 本身也是基于 Humming 思路的实现**，而 Humming 当前实现在其基准中表现更好（F-085 段）。这说明生态是**互相借鉴**而非单向替代。

## 五、开发者视角小结

从本包梳理出的三条「非显而易见」认知：

1. **JIT 是取舍不是免费午餐**。换来位宽与架构的覆盖广度，代价是首次编译 1.82–1.88 秒/ kernel 与磁盘缓存依赖。缓存不可写（只读容器、临时卷）的环境需要预热策略。
2. **Humming 不取代 vLLM 的后端选择逻辑**。`prefers_humming()` / `prioritize_humming()` 存在（F-078）说明 vLLM 会判定何时不该用 Humming。显式指定参数≠必然生效。
3. **官方文档的保守性是有意的**。README 支持矩阵（FP4 → SM120+）比源码（SM100 或 SM120）更严（F-013 vs F-018）。这通常意味着「保守表述面向大众，激进表述面向已知架构的专家」。**遇到冲突，以真机为准**（差异 #3）。

## 六、延伸阅读

- [02 量化模型](02-quantization-model.md)：指数位为 0 的浮点家族
- [05 调优与启发式](05-tuning.md)：autotune 的现状与张力
- [08 性能与基准](08-performance.md)：编译耗时的完整数据
- [核验记录](../references/verification.md)：三处口径差异的逐一核验
