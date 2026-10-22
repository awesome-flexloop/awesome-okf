---
type: Reference
title: "核验记录：源码 × 官方博客 × 作者自述交叉验证"
description: "Humming 知识包交叉核验记录——五处口径差异（vLLM 引入版本、打包体积、FP4/INT4 架构门槛、运行期依赖清单）的逐一核验与解释，关键事实多源确认清单，未采纳与待核项"
tags: [humming, verification, cross-check, source-reconciliation, evidence]
generated: { by: seven-concepts-cmd+source-code-to-okf-wiki/V, at: "2026-10-22T23:40:00+08:00" }
status: stable
stale_after: 2027-04-22
sources:
  - id: local-source
    resource: /source-map.md
    title: 本地源码检出（v0.1.18-1-g5b500b4，2026-10-21）
  - id: blog
    url: https://vllm.ai/blog/2026-10-21-humming
    title: Announcing Humming（2026-10-21）
  - id: vllm-local
    resource: vllm-project/vllm @ 7d5335936c40306063a29fc4e2ccbe71b280e40c
    title: vLLM 本地源码检出（v0.32.1rc0-283，2026-10-22）
---

# 核验记录：源码 × 官方博客 × 作者自述交叉验证

本知识包采用**四信源**：本地源码检出（一手代码）、官方博客（一手口径）、vLLM 集成侧源码（一手代码）、作者知乎自述（一手但时点较早）。四源在**核心 API 与项目定位**上完全一致，但在架构门槛、体积口径、版本引入时点、依赖清单等**边界表述**上存在 5 处口径差异，逐一核验如下。

## 一、口径差异及解释

### 差异 #1：vLLM 引入 Humming 依赖的版本

| 侧 | 说法 | 出处 |
|----|------|------|
| 官方博客 | 「从 vLLM 0.29.0 起，CUDA 安装默认包含 Humming 依赖」 | 博客「Using Humming in vLLM」节 |
| vLLM 源码 | 依赖自 **v0.22.0** 即已存在于 `requirements/cuda.txt` | F-072 |

**核验过程**：

```bash
# 1) 追溯该行进入 requirements/cuda.txt 的全部提交
git log -S "humming-kernels" -- requirements/cuda.txt
# → 2026-05-19 引入（PR #42540）
# → 2026-05-23 revert（PR #43492）
# → 2026-05-26 恢复（PR #43530）

# 2) 逐 tag 比对是否含该行
for t in v0.21.0 v0.22.0 v0.24.0 v0.26.0 v0.29.0 v0.32.0; do
  echo -n "$t: "; git show $t:requirements/cuda.txt | grep -c humming-kernels
done
# → v0.21.0: 0 / v0.22.0 起恒为 1
```

**结论**：博客口径的 0.29.0 是**当时的版本钉**（v0.29.0 钉 `humming-kernels[cu13]==0.1.12`），而非依赖首次出现的版本。依赖首次出现于 v0.22.0（2026-05-29 发布），中间经历一次引入-回滚-恢复的短暂波折。

**处理**：本包以源码口径为准（F-072），博客说法作为「当时对外表述」记录（F-073）。引用「vLLM 默认带 Humming」时须写明**具体 vLLM 版本**，不可只写「0.29.0 起」。

### 差异 #2：打包体积

| 侧 | 说法 | 出处 |
|----|------|------|
| README | 「The package size is only **100+KB**」 | README.md:19 |
| 官方博客 | 「wheel package 约为 **500 KB**」 | 博客「Usage / Installation」节 |
| 作者知乎自述 | 「打包后 wheel 仅 100+KB」 | F-094 |

**核验过程**：本包未在本地环境执行 `pip wheel` 实测体积（需完整构建 CUDA 扩展，超出纯阅读核验范围），因此**不裁决谁对**，只登记口径。

**结论**：README 与作者自述口径一致（100+KB），博客口径不同（500KB）。可能解释：README 指纯 Python 门面部分、博客指含编译产物/元数据的完整 wheel；亦可能为不同时点测量。本包引用时按来源分列，不做统一化改写。

**处理**：F-012 同时记录两处说法并指向本节。**未实测项**，选型若在意安装体积请自行 `pip download humming-kernels --no-deps` 实测。

### 差异 #3：FP4 的架构门槛

| 侧 | 说法 | 出处 |
|----|------|------|
| README 支持矩阵 | FP4 (e2m1) 需 **SM120+** | README.md:30（F-018） |
| 源码 `check_dtype()` | float4e0m3 / float4e2m1 / float8e3m4 门槛为 **SM100（UMMA 路径）或 SM120** | `humming/kernel/humming.py:427-440`（F-013） |

**核验过程**：逐行读 `check_dtype()` 的 `dtype_map` 与 `operand_dtype_map`，确认 FP4 条目的门槛写成「SM100 或 SM120」双路径，而非 README 的单一 SM120。

**结论**：源码比 README 多一条 SM100 路径。**本包不直接采信源码口径为唯一答案**——原因是源码对 SM100 的 FP4 支持依赖 `UMMA`（tcgen05 指令）路径，其可用性还受 `mma.py` 的架构白名单约束（F-027：SM100/103/120/121），且 README 的支持矩阵是面向用户的保守对外表述。

**处理**：F-013 记录源码双路径，F-018 记录 README 保守口径，两者在概念页并列呈现并注明差异来源。**遇到 FP4 落地问题时的正确做法**：以真机执行结果为准，而非任一侧文档——源码注释亦警告 SM107 执行未文档化编码会抛 illegal instruction（F-029）。

### 差异 #4：INT4 的架构门槛

| 侧 | 说法 | 出处 |
|----|------|------|
| README 支持矩阵 | INT4 需 **SM80+** | README.md:32（F-018） |
| 源码 `check_dtype()` | `dtype_map` 中 `int4: 75`——**SM75 即合法** | `humming/kernel/humming.py:429`（F-013） |

**核验过程**：直接读 `dtype_map` 字典，确认 `dtypes.int4: 75` 与 `dtypes.int8: 75` 同档。

**结论**：源码门槛比 README 低一个架构代次。README 面向用户的保守表述（INT4 激活需要比 FP16 更新的架构做硬件支持）可能出于实测性能考虑，但**类型合法性检查本身以源码为准**。

**处理**：F-013 与 F-018 分别记录两侧口径。**架构门槛在概念页与实战页并列呈现**——落地前以真机执行为准。

### 差异 #5：运行期依赖清单

| 侧 | 说法 | 出处 |
|----|------|------|
| README | 「Minimal dependencies: Requires only **PyTorch** and **NVCC**」 | README.md:18 |
| 作者知乎自述 | 「无复杂依赖，仅需 torch 和 nvcc」 | F-094 |
| `pyproject.toml` | 运行期依赖共 **8 项**：`torch>=2.7`、`triton`（非 win32）/ `triton-windows>=3.8.0.post29`（win32）、`numpy`、`safetensors`、`jinja2`、`cuda-bindings`、`tqdm`、`tabulate` | `pyproject.toml:23-33`（F-005） |

**核验过程**：读 `pyproject.toml` 的 `[project].dependencies` 数组，逐项计数。

**结论**：README 与作者自述的「仅需 torch 和 nvcc」是**面向核心路径的简化表述**（NVCC 属 extras，不在运行期依赖里）；实际运行期依赖有 8 项，其中 `cuda-bindings` 是 NVRTC 后端的可选探测对象，`triton`/`jinja2` 供代码生成路径使用。

**处理**：F-005 已修正为完整 8 项清单。**不影响使用**——这些都是纯 Python / 已随 torch 生态普及的包，安装体积差异可忽略；`triton` 在 Windows 上需 `triton-windows` 变体，装不上时可考虑只用依赖 torch 的路径。

## 二、关键事实多源确认

| 事实 | 源码侧 | 博客/自述侧 | 结论 |
|------|--------|------------|------|
| 项目定位（F-001） | README.md:4 原文 | 博客首段同义表述 | ✅ 一致 |
| 许可证 Apache-2.0（F-004） | 仓库根 `LICENSE` | 博客开源声明 | ✅ 一致 |
| SM75+ 兼容性（F-018） | `dtype_map` 最低门槛 SM75 | README「SM75+」 | ✅ 一致 |
| 依赖 torch>=2.7（F-005） | `pyproject.toml:23-33` 实为 8 项 | 作者自述「仅需 torch 和 nvcc」 | ⚠️ 见差异 #5 |
| 依赖体量（F-005/F-094） | `pyproject.toml` 运行期 8 项依赖 | 作者自述「仅需 torch 和 nvcc」 | ⚠️ 见差异 #5 |
| 编译耗时量级（F-080/F-094） | — | 博客 1.82s/1.88s；自述「1–2 秒」 | ✅ 一致（互为印证） |
| 支持 Dense 与 MoE 两种 GEMM（F-001/F-018） | `GemmType` 四态（F-036） | README「both Dense GEMM and MoE GEMM」 | ✅ 一致 |
| 量化策略多样（F-019~F-021） | `WeightScaleType` 四态 + `InputQuantizationMode` 六态 | README「various quantization strategies」 | ✅ 一致 |
| vLLM 集成 PR #34556（F-092） | vLLM 侧 humming 代码已合入 | 作者自述给出 PR 号 | ✅ 一致（PR 号采信作者侧） |
| 仓库迁移（F-092） | 当前 `vllm-project/humming` | 自述早期地址 `inclusionAI/humming` | ✅ 一致（迁移已发生） |
| 量级定位「轻量」（F-012/F-094） | README 100+KB | 博客 500KB | ⚠️ 差异 #2，已解释 |
| vLLM 引入版本（F-073） | 自 v0.22.0 起（git 历史） | 博客称 0.29.0 | ⚠️ 差异 #1，已解释 |
| INT4 架构门槛（F-013/F-018） | `dtype_map` int4: 75 | README SM80+ | ⚠️ 差异 #4，已解释 |
| 运行期依赖（F-005） | `pyproject.toml` 8 项 | README「仅 torch 与 NVCC」 | ⚠️ 差异 #5，已解释 |
| FP4 架构门槛（F-013/F-018） | SM100 或 SM120 | README SM120+ | ⚠️ 差异 #3，已解释 |

## 三、未采纳 / 待核项

- **未实测项**：本包全部内容基于源码阅读、官方博客与作者自述，**未在真实 GPU 上运行任何 kernel**。性能数字（F-080~F-089）一律为官方博客在其特定测试条件下的结果，不代表通用结论。落地前请以自有负载实测为准。
- **性能数字的测试条件**：基准由 vLLM community 运行，M 覆盖 1 到 8192 的每一个 2 的幂，充分 warmup，逐 kernel 计时，**cold L2 cache**，样本间短暂 pause；MoE speedup 定义为「Gateup GEMM 延迟 + Down GEMM 延迟」之和（F-079）。脱离这些条件引用倍数会失真。
- **端到端数据仅一组**：F-089 的 DeepSeek-V4.1-Flash / 8×H20 / TP=8 是官方给出的唯一端到端样本，样本量不足以支撑普适结论。
- **作者自述的支持范围（F-093）**：写作时点早于本包源码快照，自述称「已支持 SM75–SM90 高级特性，SM100/SM120 特性未来支持」，而本包源码快照（2026-10-21）已含 SM100/SM120/SM121 启发式文件与 UMMA 流水线。**以源码快照为准**，作者自述仅作演进脉络参考。
- **未文档化浮点格式（F-027~F-029）**：源码明确警告白名单外的架构（如 SM107）执行会抛 illegal instruction。本包只登记机制与白名单，**不给出可直接照抄的启用配置**——需 CUBIN 补丁 + 架构白名单双重条件，且须真机验证。
- **路线图内容（F-090）**：autotune 尚未落地，当前依赖针对性启发式；EP 下量化 All-to-All 通信为规划目标而非现状。引用时勿表述为已有能力。
- **`docs/config.md`**：官方逐字段配置参考（442 行），本包只摘取三层配置的关键字段，未逐字段搬运，避免与上游文档产生双份维护。
- **PPU 设备路径**：源码含 `ppu_sm80.py` 专用启发式与 PPU 强制 NVCC 分支（F-041、F-056），但官方博客未展开 PPU 硬件细节。本包仅登记机制存在，不做性能或兼容性承诺。

## 四、核验方法

1. **源码侧**：文件路径 + 行号级读取与 grep（每条事实的来源列均标注路径与行号，见 [facts.md](facts.md)）。
2. **git 历史侧**：`git log -S` 追溯依赖引入/回滚/恢复三个提交节点，逐 tag 比对确认「自 v0.22.0 起恒含」。
3. **博客侧**：WebFetch 抓取 `https://vllm.ai/blog/2026-10-21-humming` 全文，提取定位、量化支持、配置三层、性能数字与测试条件、路线图五节。
4. **社区侧**：知乎 CLI `search zhihu` 检索作者自述文章，交叉核对项目缘起、PR 号、仓库迁移与早期支持范围。
5. **差异处理**：源码与文档冲突且无法由源码单方裁定时（如差异 #3），**并列呈现双方口径并标注来源**，不以推测补齐；涉及真机行为的项明确标注「以实机为准」。

## 五、结论

四源在**项目定位、编译耗时量级、Dense/MoE 双路径、量化策略多样性、核心 API 形态**五项上完全一致，无实质冲突。5 处差异均属**口径层面**（版本引入时点、体积统计范围、架构门槛表述宽严、依赖清单详略），已在第一节逐条给出核验过程与处理方式。

本包的事实基线可信度高；未覆盖部分集中在**真机性能与未文档化格式**，二者均已在第三节明确标注为未实测/待核，读者不应据此作生产决策。
