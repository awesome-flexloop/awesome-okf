---
type: Concept
title: "结果与消融：数字怎么读，以及证据等级"
description: "277 任务实验设置、表 1 逐组合结果、表 2(a) 消融、表 2(b) 泛化、成本口径与四组易混数字"
tags: [实验结果, 消融, Pass@1, Web-Bench, CredData, ReposVul, 证据等级]
status: stable
stale_after: 2027-02-28
generated: { by: "reference_agent/seven-concepts-rie", at: "2026-11-17T12:35:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-17T12:35:00+08:00" }
sources:
  - id: facts
    resource: ../references/article-source.md
  - id: paper
    resource: https://arxiv.org/html/2610.22732v1
  - id: verification
    resource: ../references/verification.md
---

# 结果与消融：数字怎么读，以及证据等级

## 实验设置

| 项 | 内容 | 事实编号 |
|---|---|---|
| 任务集 | 277 个 SWE-Bench 任务，6 仓库：scikit-learn 60、SymPy 60、Django 40、Sphinx 44、Matplotlib 34、xarray 39 | F-073 |
| 来源 | 199 个 Verified + 78 个 full test split | F-074 |
| 顺序 | 仓库内按时间顺序；控制器只从更早任务学习 | F-075 |
| 组合 | Claude Code + Sonnet 5 / Opus 4.8、Copilot CLI + Sonnet 5、Codex + GPT-5.6 Terra / GPT-5.6 Sol | F-076 |
| 重复 | 每个设置跑完整六仓库、3 个 seed | F-077 |
| 质量指标 | SWE-Bench Pass@1、Web-Bench cumulative Pass@2、安全基准 detection F1 | F-077 |
| 比较对象 | 默认 high / medium / low effort、RTK、RepoMap、TE、TE+RTK、TE+RepoMap | F-078 |
| 成本口径 | mean cache-aware cost，含控制器自身全部调用 | F-049、F-048 |

每个仓库的控制器**从零历史开始**，这是一条重要的公平性设定（F-086）：结果不是靠预先灌入经验取得的。

## 表 1：逐组合结果

| Agent–Model | 默认 Pass@1 | TE ΔCost | TE Pass@1 | 默认 medium effort ΔCost / Pass@1 |
|---|---|---|---|---|
| Claude Code + Sonnet 5 | 74.7±1.3 | **−23.6±1.8** | 76.0±1.2 | −26.6±1.4 / 70.0±1.8 |
| Claude Code + Opus 4.8 | 74.0±0.6 | **−30.9±2.1** | 73.0±0.6 | −16.8±2.1 / 72.2±0.4 |
| Codex + GPT-5.6 Terra | 73.8±1.0 | **−24.7±1.2** | 74.7±1.0 | −25.7±2.0 / 69.6±1.2 |
| Codex + GPT-5.6 Sol | 80.1±0.8 | **−26.1±2.1** | 81.7±0.7 | −28.9±1.9 / 76.7±0.7 |
| Copilot CLI + Sonnet 5 | 75.0±1.5 | **−18.4±1.5** | 77.6±1.3 | −25.4±2.4 / 72.6±1.2 |

事实编号 F-079 ~ F-081。三点读法：

1. **Pass@1 在 4/5 组合上升**，唯一下降的是 Opus 4.8 的 −1.0 个百分点（F-082）。
2. **降推理强度省得更多但质量塌了**：medium effort 在五个组合的 Pass@1 均低于默认，low effort 更甚；论文 §4.2 汇总为 Pass@1 下降 1.8–10.3 个百分点（F-082）。这正是 [成本口径](02-black-box-controller.md) 里「质量写成约束」的意义。
3. **可以叠加固定策略**：TE+RTK 在 Opus 4.8 上达到 −33.2±1.7%、Pass@1 74.8±1.2，高于默认（F-083）。

## 一致性与回本点

- 6 仓库 × 5 组合 = **30 个 cell 全部降本**，幅度 5.2–40.1%（F-084）；对照下 RTK 单独在 12 个 cell 上**增加**成本，RepoMap 单独在 15 个 cell 上增加（F-085）。
- TE+RepoMap 在 29/30 个 cell 降本（F-084 相关段落）。
- 累积成本曲线：除 xarray 外各仓初期更贵，**第 6 个任务起全部低于默认**，终点累积节省 16.9–32.0%（F-086）。

「前几个任务更贵」不是缺陷，而是学习成本；但对只有三五个任务的项目，这套方法可能根本不回本。判据见 [局限与落地](09-limits-and-adoption.md)。

## 表 2(a)：消融

Claude Code 上每个元策略单独运行，参数与全栈完全相同（未在消融上单独调参）：

| 模型 | Micro-skills | Tool pruning | Failure-loop guard | Combined |
|---|---|---|---|---|
| Sonnet 5 ΔCost | −11.8±2.1 | −13.2±1.3 | −7.1±2.2 | **−23.6±1.8** |
| Opus 4.8 ΔCost | −14.3±2.3 | −17.7±1.5 | −5.4±1.8 | **−30.9±2.1** |

事实编号 F-087、F-088。结论：**工具剪枝单份最大**（作用于每轮），微技能紧随，循环守卫是个位数；所有变体 Pass@1 与默认相差 ≤3 个百分点；**没有任何单一变体达到全栈的节省幅度**。附录 H 补充了解释：组合变体各列的动作计数与单策略变体接近，三条元策略很少互相干扰。

## 表 2(b)：泛化到不同任务结构

| 基准 | 任务结构 | Claude Code | Codex | Copilot CLI |
|---|---|---|---|---|
| Web-Bench（102 任务 / 5 项目，Pass@2） | 同一项目内连续构建 | −21.2±1.3 | −16.0±1.5 | −18.7±1.9 |
| CredData（100 任务，F1） | 每任务一个新仓库，固定审计 brief | −19.6±0.7 | −16.5±1.0 | −18.3±1.4 |
| ReposVul（100 任务，F1） | 每任务一个新仓库，轨迹更短 | −7.5±1.6 | −6.4±1.2 | −9.3±1.6 |

事实编号 F-090、F-091、F-071。安全基准关闭 micro-skills，只留工具剪枝与循环守卫；ReposVul 降幅明显更小，论文解释为**轨迹更短、可回收成本本来就少**。

⚠️ **别用合并区间替代逐基准数字**：论文摘要写「6.4–21.2%」，博客写安全审计「6.4–19.6%」，仓库 README 写「6–20%」。三者覆盖范围不同（核验报告 D-1）。Copilot CLI 在 Web-Bench 上 Pass@2 从 60.8 降到 59.3，也说明「成本降」不等于「每个质量指标都升」。

## 证据等级（V 阶段采纳 V-1）

| 项 | 状态 |
|---|---|
| 数字来源 | 论文表 1 / 表 2，作者团队自测，3 seed |
| 信源关系 | 博客、论文、项目页、仓库 README 四者均由作者团队发布（F-014、F-109） |
| 独立第三方复现 | 本次采集未取得 |
| 成本口径依赖 | cache-aware 加权，随厂商缓存定价变化；换计价表不可直接比较 |
| 可复现材料 | `experiments/` 提供 harness 与任务集（F-104），但本束未运行 |
| 本束实测 | 无。未安装插件、未跑实验 |

因此本束把所有结果表述为「论文报告」，不表述为「已验证效果」。

## 四组易混数字

| 容易混 | 正确读法 |
|---|---|
| 18.4–30.9% vs 5.2–40.1% | 五组合平均降本 vs 30 个 cell 的降本区间 |
| 16.9–32.0% vs 18.4–30.9% | 累积曲线终点节省 vs 平均单任务降本 |
| 6.4–21.2% vs 6.4–19.6% | 摘要的三基准合并区间 vs 博客的两安全基准合并区间 |
| 30% vs 7% | 同仓历史重复率 vs 跨仓历史匹配率（[成本剖析](01-cost-profiling.md)） |
