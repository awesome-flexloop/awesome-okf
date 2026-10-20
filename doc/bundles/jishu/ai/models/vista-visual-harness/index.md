---
okf_version: "0.2"
type: bundle
title: "VISTA 视觉原生 Harness：让多模态模型保留并复用视觉经验"
description: "微信博文经 OKF v0.2 七阶段转化（论文解读/技术综述，非操作教程）——MIT 何恺明团队 VISTA 视觉原生 Harness：视觉观测/无损视觉记忆/视觉检查三组件，ARC-AGI-3 公开集 RHAE 满分 100（基线 40.68），含 8 项勘误与数据污染限定。"
tags: [vista, visual-harness, multimodal, arc-agi-3, agent-memory, kaiming-he, mit]
generated: { by: "opencode/minimax-m3.1-flash-free", at: "2026-10-20" }
verified:
  - { by: "process:seven-concepts-v", at: "2026-10-20" }
status: stable
stale_after: 2027-04-20
sources:
  - id: blog
    url: "https://mp.weixin.qq.com/s/3S5OW6ytgz27zrq4UgCkgQ"
    title: "何恺明团队发布多模态Harness框架（量子位，2026-10-09）"
  - id: arxiv
    url: "https://arxiv.org/abs/2610.02200"
    title: "VISTA: A Visual Harness for Reasoning in an Interactive World"
  - id: project
    url: "https://vista-research.github.io/"
    title: "VISTA 项目页（2026-08-05 blogpost 版本）"
  - id: github
    url: "https://github.com/joshhhhhan/VISTA"
    title: "VISTA 代码仓库（MIT License）"
  - id: arc-methodology
    url: "https://docs.arcprize.org/methodology"
    title: "ARC Prize 官方评测方法学（RHAE 定义）"
---

# VISTA 视觉原生 Harness：让多模态模型保留并复用视觉经验

> **论文解读 / 技术综述，非操作教程** [F-002]。本束由[量子位公众号博文](https://mp.weixin.qq.com/s/3S5OW6ytgz27zrq4UgCkgQ)（作者 henry，2026-10-09）经 OKF v0.2 七阶段工作流转化，全部关键数字与机制经 arXiv 论文原文、项目页、GitHub 仓库与 ARC Prize 官方方法学核验。
> **骨架判定**：博文未给出读者可照做的安装/配置/实测流程（两问判据第一问为"否"），因此**不设 `examples/`**；开源仓库的运行要求作为事实登记在 [05 局限与实践](concepts/05-limitations-and-practice.md)。

MIT 团队（何恺明等）提出 **VISTA**——一个视觉原生的 Harness（模型外部脚手架）。它不训练任何模型，而是把交互环境返回的**每一帧原样保存到上下文之外**，并给模型配一套按需回看的工具，让通用多模态模型获得**长时程视觉** [F-001][F-002][F-060]。

## 核心要点速览

| 维度 | 内容 |
|------|------|
| **定位** | 视觉原生 Harness——为通用多模态模型提供长时程视觉 [F-001][F-060] |
| **三组件** | 视觉观测（visual observations）、无损视觉记忆（lossless visual memory）、视觉检查（visual inspection）[F-050] |
| **机制内核** | 对交互历史的**显式注意力**（explicit attention mechanism）——模型自主选择回看哪一帧、哪个区域 [F-059] |
| **记忆结构** | 原始帧档案 + `GUIDE.md`（跨关卡结论）+ `WORKING.md`（当前关卡状态）三层 [F-030][F-051][F-053] |
| **头条结果** | ARC-AGI-3 公开 25 局：Claude Opus 5.0 RHAE **100.00**（官方实现基线 40.68），动作数比人类少 **57.4%** [F-047][F-048][F-064] |
| **第二模型** | GPT-5.6 Sol 同样全部通关，RHAE **99.00**（基线 13.33）[F-049][F-064] |
| **跨基准** | GameWorld 成功率 40.0%→63.3%；AI GameStore 47.3→140.3；BabyVision 41.0%→63.2% [F-056][F-057][F-058] |
| **消融证据** | 同一模型下 RHAE 阶梯 13.33 → 47.32 → 51.66 → 65.82 → 70.05 → 94.10 → 99.00 [F-065] |
| **额外训练** | **无**——Harness "does not involve any trained model" [F-054] |
| **开源** | `github.com/joshhhhhan/VISTA`，MIT License [F-075] |
| **论文坐标** | arXiv:2610.02200，2026-10-01 提交，MIT，CC BY 4.0 [F-045] |

## 已知边界与可信度

- **论文自陈的最重要局限（博文完全未提，勘误 E-3）**：所用模型在公开基准之后发布，**无法排除这些游戏已被纳入训练数据**；在 ARC-AGI-3 私有集上评估才是更强的泛化检验 [F-068]。因此正确表述是"在**公开集**上取得满分"，而非"多模态模型已达人类水平"。
- **满分不是唯一**：程序合成路线中 Tycho 亦为 100.00、Retrodict 99.86 [F-065]。本结果证明的是视觉原生路线可与程序合成路线**同等**，非超越。
- **方法有适用边界**：3D 重渲染变体降至 RHAE 84.12、动作数增至 20,640 [F-066]；最适配网格化、离散、颜色边界清晰的 2D 环境。
- **跨基准证据强度是混合的**：GameWorld 与 AI GameStore 同为浏览器游戏，BabyVision 为静态图片（非交互式）[F-058]，故证明的是稳健性 + 部分可迁移性。
- **必须带方差引用**：GameWorld 63.33±2.37%、BabyVision 63.23±3.00%、ARC-AGI-3 99.04±0.17 [F-067]。
- **RHAE 口径**：单关得分 =(人类基线动作数/AI 动作数)²，单关上限 1.15 倍，未通关计 0，总分为各游戏分平均 [F-073]——满分要求 25 局全部关卡通关。
- **本束共 8 项勘误（E-1~E-8）**，完整清单见 [核验报告](references/verification.md)；项目页（2026-08）与论文（2026-10）存在系统性数字差异，本束一律以**论文口径**为准。
- **状态**：`stable`（18 项 P0 声明全部通过独立核验，核心声明无需降级；勘误已完整落实）。
- **本束无 examples**：博文为论文解读，无读者可复现的操作流程（两问判据）。

## 内容导航

- [概念文档](concepts/index.md) — 6 篇：总览 / 三组件机制 / 记忆与上下文 / ARC-AGI-3 结果口径 / 跨基准验证 / 局限与实践
- [信源参考](references/index.md) — 事实清单（F-001~F-076）、P0 核验报告与勘误、知识地图、信源登记

## 主题关联

本束与同组 [MiniT2I 极简像素空间文生图](../minit2i/index.md) 属同一"何恺明团队视觉研究"主题簇：MiniT2I 走**极简化**路线（三大减法：去 VAE / 去 AdaLN / 去私有数据），VISTA 走**保真化**路线（无损保留每一帧）——两者恰好构成"视觉表征该做减法还是做加法"的一对参照。

本束与 [Agent Lightning](../agent-lightning/index.md) 属同一"Harness 范式"主题簇，但路线相反：Agent Lightning 让 harness **参与模型训练**（Harnessed Agentic RL），VISTA 让 harness **只做编排**（不训练任何模型）[F-054]。两束合看，可以回答"harness 到底应该管到哪一层"。

本束与 [AI 工程方法论](../../practice/ai-engineering-methodology/index.md) 的 Harness 工程谱系、[planning-with-files](../../practice/planning-with-files/index.md) 的文件系统外存思路可互参——VISTA 是"上下文工程 + 视觉记忆"路线的一个实证样本。

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
references/index
log
```
