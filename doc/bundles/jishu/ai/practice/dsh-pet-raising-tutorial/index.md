---
okf_version: "0.2"
type: bundle
title: "DeepSeek Harness 养鱼教程：跨聊天通道的电子宠物与社媒运营"
description: "从一篇公众号教程提炼 DSH 养成教程：四层运行时、五段人设、四通道证据等级、三层安全边界与社媒运营闸门；单源未实测，保持 draft。"
source: references/source-manifest.md
total_bundles: 1
total_content_docs: 13
total_md_files: 18
generated: { by: "process:seven-concepts-cmd", at: "2026-11-04T11:05:00+08:00" }
status: draft
tags: [DeepSeek, Harness, DSH, Agent, Persona, QQ-Bot, WeChat, Feishu, Live-Streaming, Safety]
stale_after: 2026-12-04
sources:
  - id: wx-kazike
    resource: https://mp.weixin.qq.com/s/-LcRUPe5OYBRjiTEzYXKog
    title: DeepSeek Harness养鱼教程来了，一文送你的肥鱼当上主播。
    author: 数字生命卡兹克
    last_modified: 2026-11-03
  - id: qq-official
    resource: https://ima.qq.com/wiki/
    title: QQ Bot,支持接入 DeepSeek Harness（腾讯 QQ 公众号 2026-08-15）
  - id: dsh-plugin-index
    resource: https://dshpluginhub.ai/zh/plugins/tencent-connect-dsh-qqbot
  - id: napcat
    resource: https://github.com/NapNeko/NapCatQQ
  - id: astrbot
    resource: https://github.com/AstrBotDevs/AstrBot
---

# DeepSeek Harness 养鱼教程：跨聊天通道的电子宠物与社媒运营

原文是一篇操作向的公众号教程：把 DeepSeek Harness 装好，接进 QQ、微信、飞书，给它一段人设，再放它去 B 站和抖音发内容、开直播。[F-005](references/facts.md) 本包把它拆成四层运行时、五段人设、四条通道、三层边界，并逐条核对哪些是官方口径、哪些只是作者一个人说的。

**状态为 draft。** 主信源单篇，全包零独立运行。QQ 官方插件路线有同源官方口径兜底（三步接入、单聊群聊独立记忆、@才响应、聊天内切模型），[F-010、F-013 至 F-015](references/facts.md) 微信与飞书的接入、跨通道共享记忆、直播自动化都停在作者陈述这一层。[F-027 至 F-029](references/facts.md) 原文配图未逐图核读，界面级细节可能随版本变化。详见[核验与勘误](references/verification.md)。

## 一句话结论

门槛不在安装，在边界。装通道已经简化到三步扫码，真正需要判断的是「一个以我的身份在外面说话的实体被允许说什么、做什么」。[F-010、F-041](references/facts.md) 因此本包的阅读重心放在人设约束、指令来源与彩排闸门，而不是插件安装。

## 推荐学习路径

| 步 | 读什么 | 读完后能判断什么 |
|---|---|---|
| 1 | [把 DSH 当作宠物运行时](concepts/pet-runtime-model.md) | 模型、Harness、通道插件、平台账号各管什么，故障该找谁 |
| 2 | [人设设计](concepts/persona-design.md) | 为什么禁令比形容词有效，五段结构缺一段会怎样 |
| 3 | [最小可行路径](examples/qq-bot-minimal-path.md) | 只走官方通道时最短几步、怎么验收、先查哪一级 |
| 4 | [四通道拓扑与共享记忆](concepts/channel-topology.md) | 四个通道的证据等级，以及跨通道一致为什么难 |
| 5 | [放出去之前](concepts/safety-boundaries.md) | 三条禁令对应哪三种攻击面，测试怎么做才算数 |
| 6 | [社媒运营闭环](concepts/social-ops-loop.md) | 消费型与生产型的差别，彩排闸门怎么套用 |
| 7 | [知识地图](concepts/knowledge-map.md) | 三条洞察与「锚束演迭」四步养成模式 |

想直接动手的读者可从第 3 步开始，但第 5 步必须补上。

## 包内导航

- 概念六篇：[概念索引](concepts/index.md)
- 练习三篇：[示例索引](examples/index.md)
- 信源与核验：[参考索引](references/index.md)，含 54 条事实登记与八处口径勘误

## 关联阅读

- [DeepSeek Harness 与创造模式](../../ecosystems/deepseek-harness/index.md)：同一宿主的另一条主线——创造模式与插件开发，与本包的「通道 + 人设」分工不同。
- [Agent 工程方法论](../ai-engineering-methodology/index.md)：Harness 工程与提示词工程的通用框架。
- [思维方法论](../../../../zhexue/methodology/index.md)：Agent 协作与会话版本化的可迁移方法。

## 明确不覆盖

- 不评估任何平台的自动化互动规则是否允许，不提供频率、话术或规避思路。
- 不复述人设提示词原文，只提炼结构并重写示例。
- 不宣称「能跑通」，因为本包没有一次独立运行。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
