---
type: concept
title: "VISTA 总览：让多模态模型在交互式世界里保留视觉经验"
description: "VISTA 是什么、解决什么被既有做法解决不了的问题，以及它与传统文本网格/代码世界模型路线的根本分野。"
tags: [vista, visual-harness, multimodal, arc-agi-3, agent-memory]
generated: { by: "opencode/minimax-m3.1-flash-free", at: "2026-10-20" }
verified:
  - { by: "process:seven-concepts-v", at: "2026-10-20" }
status: stable
stale_after: 2027-04-20
sources:
  - id: article-source
    resource: /references/article-source.md
  - id: verification
    resource: /references/verification.md
  - id: arxiv
    url: "https://arxiv.org/abs/2610.02200"
---

# 00 · VISTA 总览

## 一句话

**VISTA 是 MIT 团队（何恺明等）提出的一个"视觉原生 Harness"**：它不训练任何模型，而是把交互环境返回的每一帧原样保存到上下文之外，并给模型配一套"按需回看"的工具，让通用多模态模型获得**长时程视觉**（long-horizon vision）[F-001][F-002][F-060]。

论文坐标：arXiv:2610.02200《VISTA: A Visual Harness for Reasoning in an Interactive World》，2026-10-01 提交，MIT，CC BY 4.0，代码以 MIT License 开源于 `github.com/joshhhhhan/VISTA` [F-045][F-075]。

## 它要解决的问题是什么

### 问题 1：既有做法把世界压缩成了文字

在 ARC-AGI-3 这类交互式视觉基准上，已有的主流思路是**先把画面转换成由数字组成的文本网格**（以整数颜色索引逐行编码），再让模型编写程序来模拟环境规则、验证行动方案——即所谓基于代码的世界模型 [F-017][F-061]。

论文指出这条路线的根本困难：**环境越复杂，物体的外观、空间关系和动态变化就越难被完整地转化成文字和代码** [F-018]。文字网格能表达"哪个格子是红"，却很难表达"这个红色小方块的朝向标记是什么"——而后者恰恰可能是通关的关键细节。

### 问题 2：上下文会淘汰掉"还没被注意到"的细节

随着交互历史变长，早期的观察**可能被移出上下文，或被文字摘要替代** [F-018][F-062]。这带来一个不对称难题：

> **模型第一次看到一张图时，未必知道哪个细节会在后面变得重要** [F-015]。

如果记忆机制在写入时就要决定"什么值得记住"，它就必须提前知道后面会需要什么——而这是做不到的。视觉信息也很难提前用一份文字笔记完整记录下来，更难保证后续执行任务时记录的信息依然够用 [F-016]。

### VISTA 的研究问题表述

> 如何在不额外训练基础模型的情况下，让智能体在推理需要时，重新检查过去看到的视觉信息？[F-019]

论文摘要给出的答案是"给通用多模态模型长时程视觉" [F-060]，方法层面则是三组件的组合 [F-024]——详见 [01 三组件机制](01-visual-harness-components.md)。

## 与传统做法的根本分野

```mermaid
flowchart LR
    subgraph TRAD["传统做法：把环境抽象成文字/代码"]
        T1["画面 64x64 像素"] --> T2["整数颜色索引文本网格"]
        T2 --> T3["模型编写符号程序"]
        T3 --> T4["抽象环境规则并校验"]
    end
    subgraph VISTA["VISTA：保留原始视觉信息"]
        V1["环境返回每一帧原样"] --> V2["无损视觉记忆（上下文之外）"]
        V2 --> V3["inspect 按需回看/裁剪/放大/对比"]
        V3 --> V4["模型直接感知 + 推理"]
    end
    TRAD -.->|"环境复杂时压缩失真<br/>早期画面被摘要替代"| LOSS["信息不可逆损失"]
    VISTA -->|"需要时才取回原图"| V4
```

两条路线不是互斥的技术选型，而是**信息保真度与可编程性之间的权衡**：

| 维度 | 文本网格 + 代码世界模型 | VISTA 视觉原生 Harness |
|------|------------------------|---------------------|
| 环境表示 | 离散、可执行、可校验 | 原始像素、不可程序化 |
| 细节保真 | 受限于颜色索引与程序表达能力 | 无损保留每一帧 |
| 可验证性 | 强（程序可运行验证） | 弱（依赖模型自身推理） |
| 上下文成本 | 低（文本压缩比高） | 需外部存储，但上下文侧只放最后一帧 [F-032] |
| 额外训练 | 无 | 无 [F-054] |

> **解读（假设）**：两条路线并非取代关系。VISTA 论文 §4.3 自己也列出 program-synthesis 类对比系统（Schema 95.35、Retrodict 99.86、Tycho 100.00），说明在 ARC-AGI-3 上"写程序"路线同样能接近满分 [F-065]。VISTA 的主张是**另一条同样有效的路径**，尤其适用于视觉细节不可预先形式化的环境。

## 边界：它不是什么

- **它不是新模型**。§3.2 明确："The harness is purely mechanical and **does not involve any trained model**"——它只执行模型请求的工具调用、返回图像或像素值、对无效请求报错 [F-054]。环境理解、行动规划和推理仍由现成的多模态模型完成 [F-034][F-035]。
- **它不是"视觉经验自动变强"**。模型不会因为看过更多帧就获得新能力；变化的是模型**获取、保存和使用视觉信息的方式** [F-035]。
- **它不保证在未见题目上同样有效**。论文 §6 自己承认：所用模型在公开基准之后发布，**无法排除这些游戏已被纳入训练数据**；在 ARC-AGI-3 私有集上评估才是更强的泛化检验 [F-068]。这一条博文完全未提及，是解读"满分 100"时不可省略的前提，详见 [05 局限与实践](05-limitations-and-practice.md)。

## 头条结果（先看数字，再看限定）

| 模型 | ARC-AGI-3 公开 25 局 | RHAE 得分 | 官方实现基线 |
|------|-------------------|----------|--------------|
| Claude Opus 5.0 | 全部通关 | **100.00** | 40.68 [F-047][F-064] |
| GPT-5.6 Sol | 全部通关 | **99.00** | 13.33 [F-049][F-064] |
| GLM-5.3 Flash 320B（开源权重） | — | 66.93 | — [F-063] |

RHAE（Relative Human Action Efficiency）是 ARC-AGI-3 的官方指标，计分口径与"满分 100"的含义见 [03 ARC-AGI-3 结果](03-arc-agi3-results.md)。

## 下一步

- 想了解**具体怎么实现** → [01 三组件机制](01-visual-harness-components.md)
- 想了解**记忆如何组织与交接** → [02 记忆与上下文](02-memory-and-context.md)
- 想看**完整实验与消融** → [03 ARC-AGI-3 结果](03-arc-agi3-results.md)

## 相关

- [AI 工程方法论]](../../../practice/ai-engineering-methodology/index.md)：Harness 工程与 Agent 评测谱系——VISTA 是"上下文工程 + 视觉记忆"路线的实证样本
- [MiniT2I 极简像素空间文生图]](../../minit2i/index.md)：同为何恺明团队的视觉表征研究，可对照"极简化"与"保真化"两种取向
- [Agent Lightning]](../../agent-lightning/index.md)：同为 harness 范式工作，可对照"harness 参与训练"与"harness 只做编排"两条路线
- [事实登记](../references/article-source.md) · [核验与勘误](../references/verification.md) · [知识地图](../references/knowledge-map.md)
