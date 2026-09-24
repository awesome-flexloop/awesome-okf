---
type: Reference
title: "Jev 自动化决策文章事实登记"
description: "当前公众号文章的二十四条声明、来源距离与核验边界"
tags: [Jev, TypeSafe, 事实核验]
generated: { by: "process:seven-concepts-e", at: "2026-09-20" }
status: flagged
stale_after: 2026-10-20
sources:
  - { id: article, resource: "https://mp.weixin.qq.com/s/40nRaVYdYljYCbwkPCZo7g" }
  - { id: intro, resource: "https://docs.typesafe.ai/introduction" }
  - { id: quickstart, resource: "https://docs.typesafe.ai/introduction/quickstart" }
  - { id: system-one, resource: "https://docs.typesafe.ai/concepts/system-one" }
  - { id: state, resource: "https://docs.typesafe.ai/concepts/state" }
---

# 文章事实登记

## 来源代号

| 代号 | 来源 | 信源距离 |
| --- | --- | --- |
| W | [微信文章](https://mp.weixin.qq.com/s/40nRaVYdYljYCbwkPCZo7g) | 第三方综述 |
| O1 | [官方介绍](https://docs.typesafe.ai/introduction) | 官方定位与机制 |
| O2 | [Quick Start](https://docs.typesafe.ai/introduction/quickstart) | 官方请求/响应示例 |
| O3 | [System One](https://docs.typesafe.ai/concepts/system-one) | 官方概念说明 |
| O4 | [State](https://docs.typesafe.ai/concepts/state) | 官方输入限制 |

## 事实登记

| 编号 | 声明 | 来源 | 状态与限制 |
| --- | --- | --- | --- |
| F-001 | 文章标题为《快200倍、输出直接免费！全新AI模型Jev爆火，正在血洗大模型自动化》，作者张江咖啡，页面显示2026-09-18 18:00。 | W | 元信息已读 |
| F-002 | 文章将 Jev 描述为不生成自由文本、输出结构化决策和置信度的模型。 | W | 文章口径；官方文档补充 |
| F-003 | 文章称 Jev 比主流前沿模型快20～200倍。 | W | 未独立复现 |
| F-004 | 文章称成本降低40～400倍，输入每百万 token 为0.042美元，输出免费。 | W | 价格可由官方介绍核对；倍数未独立复现 |
| F-005 | 文章称类型错误被架构消除，几乎不可能产生幻觉。 | W | 类型合法不等于业务判断正确 |
| F-006 | 文章将 Jev 解释为 System One 决策原语，使用 Choice、Score、Noul 三类输出。 | W | 与 O1/O3 一致 |
| F-007 | Choice 用于有限选项，Score 用于评级，Noul 用于真假判定并返回概率。 | W/O1 | 官方文档可核对 |
| F-008 | 文章给出客服工单按紧急性、退款和派单进行分流的示例。 | W | 概念示例，无运行日志 |
| F-009 | 文章称 Jev 可约100毫秒完成客服分流。 | W | 单源案例数字 |
| F-010 | 文章称 Jev 可约每秒10次为《毁灭战士》作动作选择。 | W | 演示口径 |
| F-011 | 文章称《毁灭战士》演示运行一小时成本仅数美元。 | W | 成本边界不明 |
| F-012 | 文章称社区使用 Jev 控制超级马里奥和其他 Agent 身体反射。 | W | 未核验原始演示 |
| F-013 | 文章将浏览器 RPA 描述为由 Jev 选择点击、填表和确认动作。 | W | 外围程序执行未实测 |
| F-014 | 文章将安全熔断和流水线调度列为 Jev 的应用方向。 | W | 应用推导，无独立评测 |
| F-015 | 文章列出官网、技术文档和发布长文三个官方入口。 | W | URL 可访问性需随时间复核 |
| F-016 | 官方将 Jev 定位为首个 System One 模型，接收 state 和 typed questions，返回结构化结果。 | O1/O3 | 官方定位 |
| F-017 | 官方提供 Noul、Choice、Score 三种问题类型，三者可以一次请求混用并独立评估。 | O1/O3 | 官方机制 |
| F-018 | 官方 state 可以是字符串、JSON 对象或文本数组；当前不接受图像、音频和视频。 | O4 | 官方当前限制 |
| F-019 | Quick Start 展示 POST `/v1/systemone`、Bearer 鉴权、`state`、`model` 和 `questions`。 | O2 | 契约已读，未调用 |
| F-020 | Quick Start 展示 `jev-latest`、answers 和 usage 字段。 | O2 | 示例契约，不代表实测 |
| F-021 | Choice 和 Score 返回 confidence，Noul 返回0～1的 yes 概率而非独立 confidence。 | O1/O3 | 官方机制 |
| F-022 | 官方建议把复杂判断拆成原子问题，在代码中组合，并为不完整选项保留 other/none。 | O1 | 设计建议 |
| F-023 | 官方性能数据属于厂商评测口径，不等于跨地区 SLA 或独立基准。 | O1 | 来源性质判断 |
| F-024 | 文章称 Early Access 候补名单已有十几万人。 | W | 无统计来源，未核验 |

## R/G1 记录

F-001～F-024 连续；事实表只登记来源声明和证据边界，工程解释见概念文档。
