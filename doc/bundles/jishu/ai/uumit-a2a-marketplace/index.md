---
okf_version: "0.2"
type: bundle
title: UUMit A2A 能力交易平台 OKF 知识包
description: 微信博文一手体验经七阶段核验转化——UUMit（小龙人）AI 原生能力网络的平台事实、双边市场机制、A2A 交易层叙事与冷启动现实（产品实测/资讯，非操作教程）
tags: [uumit, 小龙人, a2a, agent-marketplace, skill, 能力交易, ut, agent经济]
generated:
  by: trae-agent
  at: "2026-09-16T20:30:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-09-16T20:30:00+08:00"
status: stable
stale_after: "2026-12-31"
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/uhp0Fn0YaFVmbC0eYzi-oA
  - id: official-site
    url: https://uumit.com/
  - id: official-juejin-launch
    url: https://juejin.cn/post/7646262111694864435
  - id: official-juejin-a2a
    url: https://juejin.cn/post/7646984259749003291
  - id: official-juejin-onekey
    url: https://juejin.cn/post/7655623395044065314
  - id: csdn-5day-test
    url: https://blog.csdn.net/Mumaren6/article/details/163753966
  - id: tencent-cloud-analysis
    url: https://cloud.tencent.com/developer/article/2673020
---

# UUMit A2A 能力交易平台

> **类型**：第三方一手实测/产品资讯（**非操作教程，无 examples/**——操作可复现性两问中"版本/输入输出可复现"为否）
> **数据时点**：博文体验 2026-08；官网与营销数字核验时点 2026-09-16
> **P0 核验**：10 项 P0 中 ✅ 6 项 / ⚠️ 4 项（瞬时值、汇率、第三方实测单源）/ ❌ 0 项；另完成 1 项仿冒站甄别
> **状态**：stable（核心声明——平台存在、模块、时间线、开放状态——全部核验通过）

## ⚠️ 厂商自述数据提示

本主题涉及大量平台方自述数字：官网营销页的 14,265+ 在线 Agent、18K 日任务、98.68% 成功率、案例"效率 +60%"等（F-035）**均无独立出处与统计口径**，正文只作为"官网自述（2026-09-16 时点）"引用，不构成事实背书；UT 充提汇率（1 元=100 UT / 1 UT≈0.007 元）来自第三方实测而非官方牌价。另发现与官方无关的可疑站点 **uumit.org**（USDT 计价、数字自相矛盾），官方域名为 uumit.com / m.uumit.com。

## 本文概要

微信公众号「阿超数字抽屉」文章《第一批"赛博卖家"，已经用 Agent 自动接单了》记录了作者对 **UUMit（小龙人）**——一个把任务、技能、知识、数据、算力、时间统一为可交易能力的 AI 原生网络——的内测体验与公测初观：注册天赋解析、在 Agent 中一句话上架写作 Skill、逛任务/时间/技能/知识市场。博文提出核心判断"**Skill 是易复制的经验文件，背后可按次调用的数据/API/知识库才是核心资产**"（📝 作者观点，核验发现与官方 per-call 叙事同构）。

本 bundle 经七阶段转化（R→I→E→V），补齐了官方信源与两个独立第三方视角：平台 2026-05 内测→8 月开放的时间线、UT 货币体系、UUMit Skill 指令式接入，以及最关键的冷启动现实——第三方 5 天自动接单实测收入约 10.2 元、成本约 28 元（ROI 为负）。

## 文档结构

### concepts/ — 概念解析（三层）

| 文档 | 主题 |
|------|------|
| [00-platform-and-timeline.md](concepts/00-platform-and-timeline.md) | 事实层：平台定位、时间线、六大市场模块地图、UT 体系、Skill 接入 |
| [01-marketplace-mechanism.md](concepts/01-marketplace-mechanism.md) | 机制层：三件事与双边市场、MCP 调用层 vs A2A 交易层、Skill 资产论点与溯源 |
| [02-agent-economy-landscape.md](concepts/02-agent-economy-landscape.md) | 格局层：营销数字甄别、负 ROI 实测、四点质疑、仿冒风险、行动启示 |

### references/ — 信源登记

| 文档 | 说明 |
|------|------|
| [article-source.md](references/article-source.md) | 博文事实清单（F-001 至 F-040：博文 26 条 + 核验补充 14 条） |
| [verification.md](references/verification.md) | P0 核验报告（勘误四清单、厂商自述隔离、uumit.org 甄别） |

## 主题关联

- [Matt Pocock Skills 生态解读](../mattpocock-skills/index.md)：同为微信博文转化束，讲 Agent Skills 标准化生态——本束回答"Skill 之后如何被定价调用"，两者构成"Skill 是什么 → Skill 怎么交易"的衔接
- [AI Agent 行业研究](../agent-industry-research/index.md)：Agent 行业三篇研究，提供本束所在赛道的宏观坐标
- [Token 经济大爆发](../token-economy-explosion/index.md)：按 token 计费的宏观经济背景，与本束 per-call/per-token 微观结算机制呼应

## 已知边界

- **非操作教程**：博文为平台 UI 走查，无版本、无输入输出、无可复现步骤，不设 examples/
- **时效快速衰减**：平台公测期模块/入口/数字迭代频繁（如"时间市场"入口已弱化），stale_after 设为 2026-12-31，到期前建议复核
- **单源条目**：注册天赋档案细节（F-013~F-015）仅博文一处；UT 汇率（F-032）、5 天账本（F-033）各为单一第三方实测
- **观点分层**：F-002~F-006、F-022~F-026 为作者观点/预测，"全球首个 A2A 平台"为厂商自述，均未当作事实背书
- **盈利预测未证实**：博文"睡觉自动赚米"的乐观预测与第三方负 ROI 实测并存，真实收益以订单和自有账本为准

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
references/index
log
```
