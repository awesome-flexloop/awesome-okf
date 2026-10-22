---
okf_version: "0.2"
type: bundle
title: "Humming：JIT 编译的量化 GEMM 内核库"
description: "Humming v0.1.18 源码与官方博客教程——面向量化推理的 JIT 编译 GEMM 内核库，统一量化表示与支持矩阵、三层配置架构、三条 CUDA 流水线（标准/warp specialization/UMMA）、设备启发式调优、MoE grouped 路径、vLLM 三条接入路径与完整性能基准"
tags: [humming, gemm, quantized-inference, jit-compilation, cuda, moe, tensor-core, vllm, 源码教程]
generated:
  by: seven-concepts-cmd+source-code-to-okf-wiki
  at: "2026-10-22T23:40:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-10-23T00:30:00+08:00"
status: stable
stale_after: 2027-04-22
sources:
  - id: local-source
    resource: vllm-project/humming @ 5b500b407a716e9dfcede04a5eba97a6eece0508
    title: 本地源码检出（git describe: v0.1.18-1-g5b500b4，2026-10-21）
  - id: github-repo
    url: https://github.com/vllm-project/humming
    title: Humming 官方仓库
  - id: blog
    url: https://vllm.ai/blog/2026-10-21-humming
    title: Announcing Humming: Fast, Flexible Kernels for Quantized Inference（2026-10-21）
  - id: vllm-local
    resource: vllm-project/vllm @ 7d5335936c40306063a29fc4e2ccbe71b280e40c
    title: vLLM 本地源码检出（v0.32.1rc0-283，2026-10-22）
  - id: zhihu-author
    url: https://zhuanlan.zhihu.com/p/2021951434141222000
    title: 通用高性能量化推理算子库 Humming（作者 Jinzhen 自述，知乎专栏）

---

# Humming：JIT 编译的量化 GEMM 内核库

Humming 官方自我定位是 **"a high-performance, lightweight, and highly flexible JIT (Just-In-Time) compiled GEMM kernel library specifically designed for quantized inference"**——面向量化推理的高性能、轻量、高灵活 JIT 编译 GEMM 内核库（F-001）。它由 **Ant Group 与 vLLM community 联合开源**（F-009），是 vLLM 量化推理的内核后端之一。

本知识包基于**本地源码检出**（`v0.1.18-1-g5b500b4`，commit `5b500b4`，2026-10-21；F-003）、**vllm.ai 官方博客**（2026-10-21 发布公告）、**vLLM 集成侧源码**（v0.32.1rc0-283）与**作者知乎自述**四信源交叉整理。

> **类型**：源码学习教程（可操作）。所有命令与代码示例可在 Humming v0.1.18 环境复现；版本相关数字均带时点。
> **信源距离**：本地源码（一手）+ 官方博客（一手）+ vLLM 集成侧源码（一手）+ 作者自述（一手但时点较早）。
> **核验结论**：四源在**核心 API 与项目定位**上完全一致；在架构门槛、体积口径、版本引入时点、依赖清单等边界表述上存在 **5 处口径差异**，均已逐一核验并解释（见 [references/verification.md](references/verification.md)）。

## 本文概要

Humming 解决的核心问题是**量化 GEMM 的覆盖度与性能二选一**：通用 Marlin 类内核只支持 4/8 位固定位宽、架构专用，大 batch 下表现不佳（F-091）。Humming 的做法是**用 JIT 换自由度**——内核在运行时针对「权重类型 × 激活类型 × scale 粒度 × GEMM 形态 × 目标架构」现场编译，于是任意 ≤8 bit 的组合都能被覆盖，且由**设备启发式**自动为每个 M 档位挑选最优 tile 配置（F-056~F-060）。

代价是首次编译耗时（单 kernel 1.82–1.88 秒，相对 CUTLASS+NVCC 的 23.35 秒约快 13 倍，F-080），收益是官方测得的多组加速优势——Dense W4A16 小 batch 约 3–4× Marlin，MoE W4A16 在 B300 上 grouped 路径约 5×（F-082、F-083），端到端 DeepSeek-V4.1-Flash 吞吐提升 14%–43%（F-089）。

## 阅读路径

1. [00 Humming 是什么](concepts/00-overview.md)——身份卡片、与 Marlin/DeepGEMM 的关系、vLLM 生态位与适用边界
2. [01 快速开始](concepts/01-quickstart.md)——安装 → 三步生命周期 → 对拍 → 缓存管理 → 常见报错
3. [02 量化模型](concepts/02-quantization-model.md)——权重×激活支持矩阵、scale 粒度四态、schema 注册表与类型约束
4. [03 架构总览](concepts/03-architecture.md)——三层配置、GEMM/MMA 四型、JIT 编译栈、13 项算子出口
5. [04 内核设计](concepts/04-kernel-design.md)——三条流水线、CUDA 七层组件、权重 repack 与 packing 层级
6. [05 调优与启发式](concepts/05-tuning.md)——设备启发式分派、算力/带宽瓶颈判定、M 维候选与栅格化
7. [06 MoE 路径](concepts/06-moe.md)——四种 GEMM 形态、激活表达式翻译、端到端实测数据
8. [07 vLLM 集成](concepts/07-vllm-integration.md)——三条接入路径、12 个权重 schema、版本依赖钉
9. [08 性能与基准](concepts/08-performance.md)——基准方法六项条件、全组加速倍数、自建 benchmark 体系
10. [09 进阶主题](concepts/09-advanced.md)——未文档化浮点格式、CUBIN 补丁与架构白名单、路线图三方向

实战示例见 [examples/](examples/index.md)（稠密量化 GEMM、MoE GEMM、vLLM 服务化、基准对拍四类场景）；编号事实清单见 [references/facts.md](references/facts.md)。

## 核心事实速查

| 项 | 值 | 出处 |
|----|-----|------|
| 官方定位 | 面向量化推理的高性能、轻量、高灵活 JIT 编译 GEMM 内核库 | F-001 |
| 版本 | 本地检出 `v0.1.18-1-g5b500b4`（2026-10-21） | F-003 |
| 许可证 | Apache-2.0 | F-004 |
| 出身 | Ant Group 与 vLLM community 联合开源 | F-009 |
| PyPI 包 | `humming-kernels`（extras: cu12 / cu13） | F-005 |
| 依赖 | Python ≥3.10；运行期 8 项，以 `torch>=2.7` 为主 | F-005 |
| 兼容架构 | NVIDIA SM75+（Turing）起 | F-018 |
| 支持范围 | 权重任意 ≤8 bit（F-015）；激活 FP16/BF16/FP8/FP4/INT8/INT4 | F-015、F-018 |
| 量化粒度 | group / block / channel / tensor 四态 | F-019 |
| 输入量化 | 六种模式（none/static_tensor/dynamic_token/dynamic_group/…） | F-021 |
| GEMM 形态 | DENSE / INDEXED / GROUPED_CONTIGUOUS / GROUPED_MASKED | F-036 |
| MMA 指令 | MMA / WGMMA / UMMA / MXMMA | F-037 |
| 权重 schema | 12 项（awq / gptq / mxfp4 / modelopt / quark / compressed-tensors …） | F-023 |
| 三层配置 | LayerConfig / ComputeConfig / TuningConfig | F-031 |
| CUDA 流水线 | 标准 / warp specialization / UMMA（tcgen05）三条 | F-051 |
| 编译耗时 | 1.82s (NVCC) / 1.88s (NVRTC) vs CUTLASS 23.35s | F-080 |
| 缓存 | `~/.humming/cache/<hash>/`，签名含头文件 mtime | F-042、F-043 |
| 启发式覆盖 | SM75/80/86/87/89/90/100/103/110/120/121 + PPU | F-056 |
| M 维候选 | 基础 1/2/4/8；Dense 上限 8192，MoE 上限 65536 | F-057 |
| vLLM 依赖钉 | `humming-kernels[cu13]==0.1.17`（vLLM v0.32.0） | F-071 |
| vLLM 引入版本 | 源码口径自 v0.22.0 起（博客称 0.29.0，见差异 #1） | F-072、F-073 |

## 阅读前必知的四条口径

1. **本包未做真机实测**：全部内容基于源码阅读、官方博客与作者自述。性能数字（F-080~F-089）为官方在其特定测试条件下的结果，**不代表通用结论**；落地前请以自有负载实测。
2. **性能倍数必须带条件引用**：官方基准用 cold L2 cache、逐 kernel 计时、M 覆盖 1–8192 每个 2 的幂（F-079）。脱离这些条件引用倍数会失真。
3. **Humming 不无条件胜出**：vLLM 侧实现了 `prefers_humming()` / `prioritize_humming()` 的优先级判定（F-078）——**自动优先仅在 compute capability == 90（H100/H800/H20）时生效**（F-078）。显式指定后端参数 ≠ 必然生效——须按 [实战 03](examples/03-vllm-serving.md) 的方法验证。
4. **未文档化浮点格式有硬边界**：`float8e3m4` / `float4e0m3` 需 CUBIN 补丁 + 架构白名单双条件，且源码明确警告 SM107 执行会抛 **illegal instruction**（F-028、F-029）——不可 try/except 兜底。

## 什么情况下不该用 Humming

这是一份**反向判断清单**——先确认自己的场景不在下列条目里，再考虑接入：

| 场景 | 为什么不该用 | 替代路径 |
|------|-------------|---------|
| **需要 batch-invariant 输出且必须保留 stream-k** | batch-invariant 模式强制 `use_stream_k=False`（F-101），与 stream-k 性能收益互斥 | 接受 stream-k 关闭的损失，或换其他后端 |
| **SM120/121 上追求 UMMA 路径** | `is_umma_supported` 要求 `sm_version // 10 in (10, 11)`——SM120/121 **不支持 UMMA**（F-099）；且博客明确 **Rubin 也不支持 e3m4/e0m3 隐藏格式**（F-103） | SM120/121 在 MX 系浮点激活下走 MXMMA，否则回落 MMA（F-100）；Rubin 用常规路径 |
| **B300（SM103）上需要 UMMA 路径跑 INT8** | 博客明确 SM103 的 **UMMA 指令不再支持 INT8 计算**，退回早期 MMA 路径性能显著降低（F-102） | 换激活精度（如 FP8）或换架构 |
| **无法接受首次调用编译延迟且无预热手段** | 单 kernel 编译 1.82–1.88 秒（F-080）；缓存签名含 `.cuh` **绝对路径→mtime**（F-043），镜像换路径即全量失效 | 固定安装路径做镜像预热，或用持久卷 + 首次启动预热 |
| **只读容器 / 无可写缓存目录** | 缓存目录 `~/.humming/cache/` 与临时目录 `~/.humming/tmp/`（含 `module/`、`lock/`）不可写会导致编译失败或每次重新编译（F-042） | 同时设 `HUMMING_CACHE_DIR` 与 `HUMMING_TMP_DIR` 到可写卷 |
| **权重格式 vLLM 原生已高性能支持且不需长尾位宽** | Humming 的差异化在**编译效率 + 量化覆盖度**，不是所有场景都更快 | 用 vLLM 原生路径（如 Marlin） |
| **多副本冷启动且启动时间敏感** | **文件锁在缓存命中检查之前获取**（F-045）——即使缓存已命中，副本也需串行取锁；冷启动成本上界 ≈ 副本数 × 单次编译耗时 | 共享持久卷 + 串行预热 |

> **版本对齐提醒**：本包基于 **humming-kernels 0.1.18**；vLLM v0.32.0 的依赖钉为 **0.1.17**（`vllm/requirements/cuda.txt:33`，F-071）。两者差一个版本，升级时请确认版本（`patch_cubin.cpp` 的内容哈希**总是**进入编译签名，补丁变更会自动使缓存失效，F-043）。


## 五处口径差异速览

| # | 差异项 | 官方博客 / README | 源码口径 | 处理 |
|---|--------|------------------|---------|------|
| 1 | vLLM 引入版本 | 博客称 0.29.0 起 | 自 v0.22.0 起即含（F-072） | 以源码为准；引用须写具体版本 |
| 2 | 打包体积 | README/自述 100+KB；博客 ~500KB | 未实测 | 两者并列，不裁决；需精确时自行实测 |
| 3 | FP4 架构门槛 | README SM120+ | 源码 SM100（UMMA）或 SM120（F-013） | 并列呈现；**以真机执行为准** |
| 4 | INT4 架构门槛 | README SM80+ | 源码 `dtype_map` int4: 75（F-013） | 并列呈现；类型合法性以源码为准 |
| 5 | 运行期依赖清单 | README「仅 torch 与 NVCC」 | `pyproject.toml` 实为 8 项（F-005） | 以 `pyproject.toml` 为准 |

详见 [references/verification.md](references/verification.md)。

## 已知边界与时效

- 本束基于 2026-10-21 源码快照，`stale_after: 2027-04-22`。Humming 处于 0.1.x 快速迭代期（版本号三位数滚动），引用行号须带版本口径。
- **autotune 尚未落地**：当前依赖针对性启发式，官方将其列为未来计划（F-090）。同理「EP 下量化 All-to-All 通信可用」是**规划目标而非现状**。
- **PPU 路径只登记机制存在**（`PPUSm80Heuristics`、强制 NVCC 分支，F-041、F-056），官方博客未展开硬件细节，本包不做性能或兼容性承诺。

## 信源与可信度

- 编号事实清单（F-001~F-106）：[references/facts.md](references/facts.md)
- 源码树结构与关键文件登记：[references/source-map.md](references/source-map.md)
- 四源交叉核验记录：[references/verification.md](references/verification.md)

## 主题关联

- [DeepGEMM 源码精读](../../ecosystems/deepseek/deep-gemm/index.md)：同为量化 GEMM 内核，AOT 预编译路线，是官方性能对标的主要基线
- [AI Agent 框架](../ai-agent/index.md)：上层编排视角（跨域关联，弱耦合）

> **宿主框架**：Humming 是 vLLM 的推理内核层依赖（`--linear-backend humming` / `--moe-backend humming` / `--quantization humming`），本束讲内核实现，宿主引擎与服务化全谱见 vLLM 官方文档与源码仓库。

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
examples/index
references/index
log
```
