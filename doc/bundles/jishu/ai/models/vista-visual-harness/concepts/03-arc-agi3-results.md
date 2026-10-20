---
type: concept
title: "ARC-AGI-3 结果与计分口径：满分 100 意味着什么"
description: "VISTA 在 ARC-AGI-3 上的完整结果——RHAE 官方计分公式、基线与提升幅度、消融阶梯、动作数对照、多次运行方差、竞争系统对照与数据污染限定。"
tags: [vista, arc-agi-3, rhae, benchmark, ablation, evaluation]
generated: { by: "opencode/minimax-m3.1-flash-free", at: "2026-10-20" }
verified:
  - { by: "process:seven-concepts-v", at: "2026-10-20" }
status: stable
stale_after: 2027-01-20
sources:
  - id: article-source
    resource: /references/article-source.md
  - id: verification
    resource: /references/verification.md
  - id: arc-methodology
    url: "https://docs.arcprize.org/methodology"
  - id: arxiv
    url: "https://arxiv.org/abs/2610.02200"
---

# 03 · ARC-AGI-3 结果与计分口径

## 主结果

| 模型 / 方案 | 完成情况 | RHAE | 动作数 | F |
|------------|---------|------|--------|---|
| **Claude Opus 5.0 + VISTA**（xhigh） | 25/25 公开游戏全部通关 | **100.00** | 7,302 | [F-047][F-048][F-077] |
| 人类参考（首次游玩） | 25/25 | 100（参照系） | 17,135 | [F-048] |
| 官方实现 + Opus 5.0（high）† | — | 40.68 | — | [F-047][F-077] |
| **GPT-5.6 Sol + VISTA**（max） | 25/25 公开游戏全部通关 | **99.00** | — | [F-049][F-077] |
| 官方实现 + GPT-5.6 Sol（max） | — | 13.33 | 10,619 | [F-064][F-077] |
| GLM-5.3 Flash 320B（开源权重）+ VISTA | — | 66.93 | — | [F-063] |

论文摘要原文：

> "VISTA improves Claude Opus 5.0's Relative Human Action Efficiency score from **40.68** to a perfect **100.00**, with the model completing all **25** public games using **57.4% fewer actions** than first-time human participants." [F-047]

动作数对照：VISTA 共用 **7,302** 个动作，比人类参考的 **17,135** 个动作少 **57.4%** [F-007][F-048]。

> **限定（勘误 E-5 + E-9）**：博文只说"满分 100"，未给基线。补上基线才能看清提升幅度：Opus 5.0 从 40.68 → 100.00，GPT-5.6 Sol 从 13.33 → 99.00。
> **但这两个数字并非同条件对照**：40.68 是 Opus 5.0 在 **high** 推理强度、官方协议（每关 5× 人类基线动作预算 / 12 小时上限）下**由官方公布的逐局分数换算**得出；100.00 则是 Opus 5.0 在 **xhigh**、2,000 动作 / 48 小时协议下取得 [F-077][F-079]。差值里同时混入了 **harness、推理强度、评测协议**三项变化。严格同模型同 effort 的对照是 **GPT-5.6 Sol（max）：13.33 → 99.00** [F-077]。

## RHAE 是什么：官方计分口径

RHAE（Relative Human Action Efficiency，读作 "ray"）是 ARC-AGI-3 的**官方**指标 [F-073]：

| 规则 | 内容 |
|------|------|
| 单关得分 | （人类基线动作数 / AI 动作数）² |
| 单关**得分**上限 | **115%（1.15 分）**——注意这是**分数**上限，不是动作数比例；若按动作计，AI 需做到人类动作数的 1/√1.15 ≈ **93.3%** 才能拿满该关 |
| 未通关关卡 | 计 **0** 分 |
| 游戏得分 | 各关得分的**加权平均**（以关卡序号 1-indexed 为权重） |
| 总分 | 各游戏分的**平均**，最终落在 **0%–100%** |
| 人类基线 | 每关"动作数最少者"的**上中位数**（upper median human） |

**因此"满分 100"的确切含义**：AI 必须在**全部 25 个游戏的全部关卡**上完成通关，且每一关的动作效率都不低于人类基线（单关最多可超出 1.15 倍）。不是部分关卡的高分累加。

> 这解释了动作数口径的重要性：RHAE 是**平方**关系，动作效率翻倍直接导致分数翻四倍，因此 7,302 vs 17,135 的差距在分数上被放大。

## 消融阶梯：六次配置变更各值多少分

论文 §4.3 给出在**同一个 GPT-5.6 Sol 模型**上逐步变更 harness 配置后的 RHAE 序列 [F-079]。六步的真实标签是：

```
官方实现(文本网格) 13.33
  (i)   图像观测（渲染 PNG 替代文本网格）                 47.32
  (ii)  提高动作与时间上限（2,000 动作 / 48 小时）       51.66
  (iii) 连续对话（最小 agent harness + 原生 compaction）  65.82
  (iv)  双笔记 GUIDE.md + WORKING.md + 可复用游戏模型     70.05
  (v)   无损视觉记忆 + 模型引导的视觉检查                 94.10
  (vi)  精确像素读出（数值 RGB）——VISTA 完整形态          99.00
```

```mermaid
flowchart LR
    A["官方实现<br/>文本网格<br/>13.33"] --> B["(i) 图像观测<br/>47.32"]
    B --> C["(ii) 动作/时间上限<br/>51.66"]
    C --> D["(iii) 连续对话<br/>65.82"]
    D --> E["(iv) 双笔记<br/>70.05"]
    E --> F["(v) 视觉记忆+检查<br/>94.10"]
    F --> G["(vi) 精确像素读出<br/>99.00"]
    style A fill:#f0f0f0,stroke:#999,color:#333
    style F fill:#e1f5fe,stroke:#0288d1,color:#01579b
    style G fill:#e1f5fe,stroke:#0288d1,color:#01579b
```

**三点必须读准**：

1. **VISTA 自身的视觉组件在 (v)(vi) 才登场**。附录 A.2 的标题就是 "(iv)→(vi): Add VISTA's visual harness" [F-079]。前四步（表示方式 → 评测协议 → 连续会话 → 双笔记）不是 VISTA 的视觉组件。最大的一次跃升 **70.05 → 94.10（+24.05）** 才是"无损视觉记忆 + 视觉检查"带来的。
2. **(i) 那一跳（13.33 → 47.32）不是免费午餐**。论文明确注明：*"The low action count is partly due to runs reaching the action or time limit before completing the games"*——该配置下许多 run 在通关前就触及动作/时间上限，完成率偏低 [F-079]。
3. **(i)–(iv) 仍按官方协议每次动作自动获得至多 7 帧**；只有 (v)(vi) 改成"只给最后一帧 + 可主动检视" [F-079]。也就是说，"减少上下文里的图片数量"与"引入无损视觉记忆"是同时发生的两件事，不能拆开归因。

> **解读（假设 M2）**：这条阶梯是"VISTA 不训练模型"这一说法的最有力证据——**同一批模型**，仅通过编排配置的逐步叠加，RHAE 从 13.33 走到 99.00 [F-079][F-054]。因此这一跃升发生在**语境编排层**，而非模型能力层。这也意味着：评估这类工作的增益时，基线必须固定模型、只换 harness，否则无法归因。
>
> **注意**：该受控对比只在阶梯内部成立。下一节的"40.68 → 100.00"**不是**同条件对照（见下）。

## 多次运行方差（勘误 E-4）

博文只给单点数字，论文附录 B.1 给出三次运行的波动 [F-067]：

| 指标 | 三次运行 | 均值 ± 标准差 |
|------|---------|--------------|
| ARC-AGI-3（RHAE，Sol） | 99.00 / 98.90 / 99.23 | 99.04 ± 0.17 |
| GameWorld 成功率 | 64.7% / 64.7% / 60.6% | 63.33 ± 2.37% |
| GameWorld 进度 | 81.0% / 80.0% / 76.9% | 79.30 ± 2.14% |
| BabyVision 准确率 | 61.5% / 61.5% / 66.7% | 63.23 ± 3.00% |

**读法**：ARC-AGI-3 的波动极小（±0.17），"99 / 100"是稳定的；GameWorld 与 BabyVision 的波动在 2–3 个百分点量级，因此"63.3%""63.2%"这类单点数字**必须**带上方差才有意义。

## 竞争系统对照

ARC-AGI-3 上还有走 **program-synthesis（程序合成）** 路线的其他系统，论文 §4.2 表 1 列出 [F-077]：

| 系统 | 模型 | 推理强度 | RHAE | 路线 |
|------|------|---------|------|------|
| Tycho | GPT-5.6 Sol | max | **100.00** | 程序合成 |
| Retrodict | GPT-5.6 Sol | max | 99.86 | 程序合成 |
| ewma_sv_v1.6 | GPT-5.6 Sol | xhigh | 98.97 | 程序合成 |
| Schema（回退行） | Opus 4.8 → Fable 5 | max | 98.98 | 程序合成 |
| Schema | GPT-5.6 Sol | xhigh→max | 95.35 | 程序合成 |
| **VISTA** | **Opus 5.0** | **xhigh** | **100.00** | 视觉原生 Harness |
| **VISTA** | **GPT-5.6 Sol** | **max** | **99.00** | 视觉原生 Harness |
| 官方实现 | Opus 5.0 | high | 40.68 † | 无程序合成 |
| 官方实现 | GPT-5.6 Sol | max | 13.33 | 无程序合成 |

† 论文表注：40.68 是"由官方公布的 25 局逐局分数计算得出"，**不是重跑所得** [F-077]。

> **解读（假设 M5 的一半）**：VISTA 的满分**不是** ARC-AGI-3 上的唯一满分——Tycho 同样拿到 100.00。论文自己的措辞也是 "matching other state-of-the-art systems" [F-078]。所以这个结果证明的是"视觉原生路线能达到与程序合成路线同等的水平"，而不是"视觉路线超越了程序路线"。这一点博文完全没有呈现，而它恰恰是判断这条技术路线价值时的正确参照系。
>
> 论文同时给出自己的定位声明：*"VISTA is, to our knowledge, the first system to achieve perfect or near-perfect performance **without program synthesis**"* [F-078]。这是论文的主张（带 "to our knowledge" 限定），本束如实登记、不作强化。

## 另一变体：3D 重渲染

论文另给出一个 3D 重渲染变体：ARC-AGI-3 上 RHAE **84.12**，用 **20,640** 个动作 [F-066]。

**读法**：换成 3D 渲染后性能明显下降（100 → 84.12），且动作数激增（7,302 → 20,640）。这说明 VISTA 的效果**依赖 2D 网格环境的渲染特性**——网格化、离散、颜色索引明确的画面最适合"无损保存 + 放大检视"这套机制。这是该方法最重要的适用边界之一。

## 数据污染限定（勘误 E-3 · 论文最重要的局限）

论文 §6 原文：

> "because the models we use were released after the public benchmarks, we cannot rule out the possibility that these games were included in their training data. Evaluation on novel games, such as those in the **private set** of ARC-AGI-3, would provide a stronger test of our system's generalization." [F-068]

**这句话的含义**：Claude Opus 5.0 与 GPT-5.6 Sol 都是在公开基准**之后**发布的，论文作者无法排除这 25 个公开游戏已经出现在它们的训练数据中。因此"满分 100"**不等于**"在未见过的游戏上也能满分"。

ARC-AGI-3 的数据集构成 [F-074]：

| 子集 | 数量 | 性质 |
|------|------|------|
| 公开演示集（Public Demo） | **25** | VISTA 评测所用 |
| 半私有集（Semi-Private） | 55 | 用于外部 API 前沿模型测试（存在小概率数据泄漏风险） |
| 完全私有集（Fully Private） | 55 | 用于 ARC Prize 官方竞赛，严密看管 |

与 ARC-AGI-2 约 10:1 的公私比不同，**ARC-AGI-3 反转了这个比例**；私有集被刻意设计为与公开集**分布外**（out-of-distribution），且对人类和 AI 都更难。

> **这四条限定缺一不可**（见 [核验报告 · 核心声明与"不可省略的限定"四件套](../references/verification.md)）：
> ① **基线及其可比性**：官方实现 Opus 5.0 **high** 40.68（†由官方公布分数换算）、GPT-5.6 Sol **max** 13.33 [F-077]；
> ② **数据污染不可排除** [F-068]；
> ③ **未见题目上的表现未知** [F-074]；
> ④ **基准方的官方立场**：公开集分数永不登官方榜、不是 AGI 进展的有效度量、社区榜成绩自报不核验 [F-084]。
>
> **博文完全未提及 ②③④**——这是本束认为最重要的勘误项。

### ④ 基准方自己怎么说（勘误 E-3 的补充）

比论文自陈更强的限定来自**基准所有者 ARC Prize**，而非 VISTA 论文。ARC-AGI-3 技术报告原文 [F-084]：

> "we will **never report public set scores** of any system on the official leaderboard… evaluating on it is emphatically **not a valid measure of progress towards AGI**."
>
> "scores will be **self-reported**… the ARC Prize foundation **will not verify anything** on the community leaderboard, and we specifically caution against interpreting any scores on the community leaderboard as evidence of AGI progress."

更值得注意的是：ARC Prize 自己开源了一个"harness"，**以人类回放**即可在全部公开环境上取得 100% [F-084]。

**这意味着**：在 ARC-AGI-3 公开集上拿满分，**本身就不构成一个有区分度的成就信号**——公开集满分可以由人类回放达成，且基准方明确拒绝把它当作进展度量。VISTA 结果的意义必须从"分数"转移到"**在不使用程序合成的前提下达到该分数**"这一点上 [F-078]。

## 成绩的可核对性（勘误 E-1 的配套更正）

ARC Prize 官方平台提供了记分卡：Opus 5.0 对应 RHAE 100、GPT-5.6 Sol 对应 RHAE 99 [F-076]，成绩**可在 ARC Prize 站点核对**。但按上一节的政策，ARC Prize **不核验社区榜成绩** [F-084]——因此准确表述是"成绩可在官方站点查到对应记分卡"，而非"成绩已被独立第三方复核验证"。

## 成本口径：这套方案要花多少钱（勘误 E-9 配套）

论文 §4.3 给出了完整的 token 与预算口径 [F-080]，这是判断"要不要照着做"时最该先看的一节：

| 维度 | 数值 |
|------|------|
| 单帧观测的 token 成本 | 图像观测约 **308** 图像 token；等效 64×64 文本网格约 **4K** 文本 token |
| 含 7 帧的单次请求 | 文本网格约 **28K** token vs 图像约 **2.2K** token |
| 单局平均 token 用量 | 文本网格 **71.9M** vs 图像观测 **30.7M** |
| 上下文长度的影响 | **780K** → 105.7M token/局；**200K** → 30.7M；**100K** → token 约减半而 RHAE 仅降 **0.4** |
| 输入图像放大倍率 | **4×** 比默认 **8×** 少用 **75%** 图像 token 且性能相当；**2×** 会降低性能 |
| 单局预算 | 论文配置为至多 **2,000** 动作 / **48 小时**（官方实现为每关 5× 人类基线动作预算 / 12 小时）[F-079] |

**读法**：VISTA 的官方配置**并不便宜**——单局约 3,070 万 token。但论文给出了第一个可调的降本旋钮：**把上下文从 200K 降到 100K，token 用量约减半而只损失 0.4 RHAE** [F-080]。对工程实践而言，这是比"要不要上 VISTA"更早该回答的问题。

## 下一步

- 这套方法在其他基准上是否同样有效 → [04 跨基准验证](04-cross-benchmark-validation.md)
- 完整局限清单与给读者的实践建议 → [05 局限与实践](05-limitations-and-practice.md)

## 相关

- [事实登记](../references/article-source.md) · [核验与勘误](../references/verification.md) · [知识地图](../references/knowledge-map.md)
