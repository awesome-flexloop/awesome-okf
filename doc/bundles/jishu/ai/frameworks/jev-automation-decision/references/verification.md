---
type: Reference
title: "Jev 文章核验报告"
description: "对速度、成本、机制、应用和候补名单的四类核验与勘误记录"
tags: [Jev, TypeSafe, P0, 核验]
generated: { by: "process:seven-concepts-v", at: "2026-09-20" }
status: flagged
stale_after: 2026-10-20
sources:
  - { id: article, resource: "https://mp.weixin.qq.com/s/40nRaVYdYljYCbwkPCZo7g" }
  - { id: intro, resource: "https://docs.typesafe.ai/introduction" }
  - { id: quickstart, resource: "https://docs.typesafe.ai/introduction/quickstart" }
  - { id: system-one, resource: "https://docs.typesafe.ai/concepts/system-one" }
  - { id: state, resource: "https://docs.typesafe.ai/concepts/state" }
---

# 核验报告

> **结论：flagged。** 当前文章的核心宣传结论没有独立同条件证据；本报告只确认官方机制和页面契约，不把文章案例或厂商数字升级为实测事实。

## 日期/版本

| 对象 | 结论 |
| --- | --- |
| 微信文章 | 页面显示 2026-09-18 18:00，已记录为页面元信息 |
| Jev 可用性 | 文章称 Early Access；本次未注册或确认候补数量 |
| API/模型版本 | Quick Start 使用 `jev-latest`；未锁定具体版本 |

## 成效数字溯源

| 声明 | 结论 | 处理 |
| --- | --- | --- |
| 20～200 倍速度、40～400 倍成本 | 文章单源，未见同条件独立基准 | 正文标为宣传口径，不作 SLA |
| 0.042 美元/百万输入 token、输出免费 | 官方介绍可核对价格口径 | 仍注明官方价格会变 |
| 客服100毫秒、Doom每秒10次、单小时数美元 | 文章演示口径，无日志/账单 | 仅作应用想象，不作普遍结论 |
| 候补十几万人 | 无统计平台、时间窗和去重口径 | 标为未核验 |

## 口径对照

- “几乎不产生幻觉”被改写为“输出受类型约束，不能直接推出业务语义正确”。[F-005](article-source.md)
- “输出直接免费”只保留为文章与官方价格页的计费口径，不推导零总成本。[F-004](article-source.md)
- “实时操控游戏/浏览器”拆为状态提供、Jev 判断和外围执行三层，不暗示原生视觉或自主点击。[F-010～F-013](article-source.md)

## 引文与归属

- System One、Noul、Choice、Score、state 和 Quick Start 均标注官方来源。
- 文章中的“血洗”“集体高潮”等修辞不进入教程事实层。
- “官方流水线准确率无限逼近顶尖大模型”未找到可复现评测表，未写入知识结论。

## V 四视角审查

| 视角 | 攻击点 | 修正 |
| --- | --- | --- |
| 魔鬼代言人 | 倍数可能来自有利工作流 | 标成厂商/文章口径，不写普遍收益 |
| 新人 | 读者可能把结构化输出理解成自动执行 | 明确外围代码、人工回退和权限检查 |
| 业务方 | API 单价不等于完整任务成本 | 增加状态采集、重试、辅助模型和人工成本 |
| 未来视角 | `jev-latest`、价格和 Early Access 会变化 | 设置 `stale_after`，要求复核版本与价格 |

## 门禁状态

- 双份 F 编号：与 spec `facts.md` 和本文件 `article-source.md` 均为 F-001～F-024。
- 外部性能：未做独立复现，禁止声称通过。
- 本地结构、UTF-8、toctree、相对链接和总索引检查在 `log.md` 补记实际结果。
