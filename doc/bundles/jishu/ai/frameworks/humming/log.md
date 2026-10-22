---
type: Log
title: "更新日志"
description: "Humming 知识包更新日志"
tags: [humming, changelog, log]
status: stable
---

# 更新日志

## 2026-10-23

**Created**: Humming v0.1.18 OKF 知识包（七概念方法论 R→I→E→V→C，本地源码 + 官方博客 + vLLM 集成侧源码 + 作者自述四信源）

- 基于本地源码检出 `v0.1.18-1-g5b500b4`（commit `5b500b4`，2026-10-21）、vllm.ai 官方博客（2026-10-21 发布公告）、vLLM 本地检出 `v0.32.1rc0-283` 的集成侧源码、作者知乎自述文章整理
- 结构：index + concepts/（00–09，入门 2 篇 / 核心 5 篇 / 场景 1 篇 / 进阶 2 篇）+ examples/（4 类典型场景）+ references/（facts 106 条 / source-map / verification）+ log
- 编号事实 F-001~F-106 全部标注源码路径与行号或 commit/URL
- 五处口径差异已在 verification.md 逐一核验并解释：
  - 差异 #1：vLLM 引入 Humming 依赖的版本——博客称 0.29.0，源码 git 历史显示自 v0.22.0 起即含（引入 #42540 → revert #43492 → 恢复 #43530），已逐 tag 验证
  - 差异 #2：打包体积——README/作者自述 100+KB vs 博客 ~500KB，未实测裁决，两者并列
  - 差异 #3：FP4 架构门槛——README SM120+ vs 源码 SM100（UMMA）或 SM120，两者并列并注明「以真机执行为准」
  - 差异 #4：INT4 架构门槛——README SM80+ vs 源码 `dtype_map` int4: 75，两者并列
  - 差异 #5：运行期依赖清单——README「仅 torch 与 NVCC」vs `pyproject.toml` 实为 8 项，以 pyproject 为准
- 落点说明：置于 `jishu/ai/frameworks/humming/`，与既有 `frameworks/vllm` 束同级——Humming 属 vllm-project 组织、frameworks 分类已覆盖「推理」与「代码库源码教程」，且为单仓独立束，不入 ecosystems 组织目录
- 关联包：vllm（宿主框架）、deep-gemm（性能对标基线）

### V 门对抗审查（2026-10-23）

**四视角审查**（魔鬼代言人 / 新人 / 老板 / 未来），产出 **30+ 条具体意见**，**采纳并修正 24 条**，新增 8 条编号事实（F-099~F-106）。

**修正的实质性错误**（全部回源码复核后确认属实）：

| # | 问题 | 修正 |
|---|------|------|
| 1 | F-038 权重 scale 缺省推断规则写成「按权重类型分派」 | 改为源码真实逻辑：仅按 `weight_scale_group_size_n` / `weight_scale_group_size` 推断（`>1`→BLOCK、`==0`→CHANNEL、其余→GROUP） |
| 2 | 架构→流水线表把 SM120/121 标为 UMMA | 更正为 **MXMMA**；UMMA 仅限 `sm_version // 10 ∈ {10,11}`（F-099~F-100） |
| 3 | `locks` 被误读为「专家级写冲突锁」 | 更正为 **stream-k 累加锁**，含容量公式与 batch-invariant 下禁用 stream-k 的说明（F-101） |
| 4 | 启发式类名表虚构 `Sm8xHeuristics` | 更正为 86/87/89 各一个独立类，并说明「每 SM 版本一类」的维护性质（F-056） |
| 5 | offset-binary 的出处标为 README Acknowledgement | 更正为 `humming/schema/humming.py:298` 注释原文（F-030） |
| 6 | `tests/native/` 被描述为「三组 kernel 级测试」 | 更正为仅含 `device_info_mock.cpp` 一个 C++ mock（F-098） |
| 7 | MoE 激活数量记为 11 | 更正为 **12**（源码字典实测，F-078） |
| 8 | overview 断言「全部以 Marlin 为基线」 | 更正为「不同图表用不同基线」（cuBLAS / Marlin / DeepGEMM / FlashInfer） |
| 9 | 未收录 vLLM 侧真实启用条件 | 补 `_HUMMING_PREFERRED_CAPABILITIES = {90}`——**自动优先仅限 Hopper**，其余架构需显式指定（F-078） |
| 10 | 未收录缓存可移植性风险 | 补「签名含 `.cuh` 绝对路径→mtime，镜像换路径即全量失效」与「文件锁在缓存命中检查之前」两个坑（F-043、F-045） |
| 11 | 缺「不该用 Humming」判断 | index.md 新增 7 条反向清单 + 版本对齐提醒（0.1.18 vs vLLM 钉 0.1.17） |
| 12 | 缺黑话速查表 | 03-architecture.md 新增 11 词速查（MMA/UMMA/TMEM/TMA/stream-k/rasterization/PDL/offset-binary/e0mX 等） |
| 13 | 未收录博客的三条架构边界 | 补 SM103 UMMA 不支持 INT8、Rubin 不支持隐藏格式、T-Head 玄武 810E 已支持（F-102~F-104） |
| 14 | 未收录激活类型选择与回退机制 | 补 `--quantization-config.moe.activation mxfp8` 与自动回退链（F-105、F-106） |
| 15 | 「Humming 取代竞品」的误读风险 | 09-advanced.md 新增「与相邻方案的关系」定位表 |
| 16 | 缺少启发式稳定性提醒 | 05-tuning.md 新增「启发式的稳定性」小节 |

**同时新增 2 处口径差异登记**：差异 #4（INT4 架构门槛）、差异 #5（运行期依赖清单）。

### V 门回归审查（2026-10-23）

**审查对象**：首轮修正后的全束文本（22 篇）。**产出 20 条意见**（10 条「必须再改」+ 10 条「建议」），**全部处理完毕**。回归审查的价值在于捕捉首轮修正自身引入的**结论反转**——即「改对了一半」。

**10 条必须再改（均为结论级反转）**：

| # | 问题 | 修正 |
|---|------|------|
| 1 | `patch_cubin` 编译签名判据写反 4 处（写成「补丁开关打开时才入签名」） | 回源码复核 `compiler.py:68` 判据为 `postprocess_cubin is not None`（**恒真**）→ 改为「补丁内容哈希**总是**入签名，补丁变更自动使缓存失效」（F-043） |
| 2 | MXMMA 支持写成无条件成立（3 处绝对化） | 补前提 `use_block_scaled_mma`，并区分「架构支持」与「配置开启」两层（F-100） |
| 3 | F-106 把「告警」与「回退」混同，且把范围窄化为 FP8 | 更正为「任意 <16bit 激活」，并拆成**两个互斥分支**：告警（继续用现有 kernel）/ 回退（切回 FlashInfer）（F-106） |
| 4 | 「三处口径差异」旧表述残留 2 处 | 全文统一为**五处** |
| 5 | 「只依赖 PyTorch」旧表述残留 5 处 | 统一为**运行期 8 项**（F-005） |
| 6 | 事实计数「98 条」残留 2 处 | 统一为 **106 条** |
| 7 | 旧表述残留 4 处（专家级锁 / 11 种激活 / 三组测试 / F-101 路径） | 分别更正为 stream-k 累加锁 / **12** 种 / `device_info_mock.cpp` 单文件 / `humming/include/humming/kernel/humming.cuh` |
| 8 | F-012 指向「差异 #3」，实际应为差异 #2 | 更正引用指向 |
| 9 | `locks` 容量写成「必须为」 | 更正为「**至少为**」（`numel() >= required_locks`） |
| 10 | 02-quantization-model 举例把 `group_size_n == 1` 误写为 128 | 更正为 `group_size_n == 1` |

**10 条建议（均已采纳）**：

- 补 `use_int_weight_scale` / `use_fused_e8m0_scale` 强制 GROUP 粒度的例外（`config.py:394-395`）
- F-076 补 vLLM 侧 `model_executor/kernels/linear/*/humming.py` 6 个落点
- 06-moe 口径统一（补 `linear.py`、量化工具与 schema 分列两处）
- 04-kernel-design 的 warp specialization 目标架构更正为 SM90 及以后
- source-map 文件归属更正（`.h`/`.cpp` 归 `csrc/`）
- index.md 反向清单补 `HUMMING_TMP_DIR`（无可写缓存目录场景）
- 行号校正：F-030 / F-034 / F-078 / 05-tuning / 07-vllm
- source-map 的运行期依赖表述同步为 8 项（本次收尾时补）
- examples/index.md 的运行环境同步为 8 项依赖（本次收尾时补）
- F-008（`__version__` 三级回退）在 source-map 落表，消除「已定义未引用」

**收尾自检结果**（C 阶段提交前）：

| 检查项 | 结果 |
|--------|------|
| `check-bundles-index.py` | 通过——9 域 / 63 组 / **671 束**，frontmatter、计数行、节标题、分组表、toctree 五面一致 |
| `check-toctrees.py` | 本束 0 问题；剩余 2 处为他方 WIP（`ponzi-scheme`），非本束责任范围 |
| `check-utf8.py` | 通过——12254 个文件均为有效 UTF-8 |
| 束内链接自检 | 22 篇、**123 条**内部 md 链接，**断链 0** |
| 事实编号自检 | 定义 **106** 条、范围 F-001~F-106、**编号断档 0**、正文引用未定义 **0**、已定义未引用 **0**（收尾修正后） |

**已知边界**：本包全部内容基于源码阅读与官方文档，**未在真实 GPU 上运行任何 kernel**；性能数字均为官方在其特定测试条件下的结果，不作为通用结论。
